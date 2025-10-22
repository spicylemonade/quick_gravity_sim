from __future__ import annotations

import math
import os
import time
import tracemalloc
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

from .hashing import CuckooHash


@dataclass
class SolverConfig:
    header: bytes
    n: int               # Graph size parameter; edges = 2^n
    k: int               # Memory reduction factor >= 2
    threads: int = 1
    seed: int = 0
    max_attempts: int = 1
    time_budget_sec: Optional[float] = None


@dataclass
class SolveResult:
    found: bool
    cycle_edges: List[Tuple[int, int, int]]  # list of (edge_index, u, v)
    elapsed_ms: float
    peak_mem_bytes: int
    metrics: Dict[str, int]


# Helper: measure peak memory using tracemalloc as an approximation
class PeakMem:
    def __enter__(self):
        tracemalloc.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Stop to finalize peak measurement
        tracemalloc.stop()

    def peak(self) -> int:
        try:
            current, peak = tracemalloc.get_traced_memory()
        except RuntimeError:
            # If tracemalloc stopped, can't query; best-effort 0
            return 0
        return peak


def _edges_iter(n: int) -> Iterable[int]:
    # Iterate all edge indices [0, 2^n)
    m = 1 << n
    return range(m)


def _construct_uv(hash_fn: CuckooHash, e: int, n: int) -> Tuple[int, int]:
    u = hash_fn.endpoint(e, 0, n)
    v = hash_fn.endpoint(e, 1, n)
    return u, v


def _trim_bin(hash_fn: CuckooHash, n: int, edges: Iterable[int], rounds: int = 2) -> List[Tuple[int, int, int]]:
    """Perform local trimming within a bin using only per-bin node degree maps.

    This is a small-memory approximation of lean trimming. It recomputes degrees for a few
    rounds and keeps edges that are not leaves in the local subgraph.
    """
    # Local degree maps per side
    alive = list(edges)
    for _ in range(rounds):
        deg_u: Dict[int, int] = {}
        deg_v: Dict[int, int] = {}
        for e in alive:
            u, v = _construct_uv(hash_fn, e, n)
            deg_u[u] = deg_u.get(u, 0) + 1
            deg_v[v] = deg_v.get(v, 0) + 1
        new_alive: List[int] = []
        for e in alive:
            u, v = _construct_uv(hash_fn, e, n)
            if deg_u.get(u, 0) > 1 and deg_v.get(v, 0) > 1:
                new_alive.append(e)
        if len(new_alive) == len(alive):
            break
        alive = new_alive
    # Return (e,u,v) for remaining edges
    return [(e, *_construct_uv(hash_fn, e, n)) for e in alive]


def _find_cycle_42(hash_fn: CuckooHash, n: int, edges: List[Tuple[int, int, int]]) -> Optional[List[Tuple[int, int, int]]]:
    """Attempt to find a 42-edge directed cycle in the provided edge set.

    Strategy: build adjacency maps U->list of (e,v) and V->list of (e,u) and perform bounded
    DFS from each edge to try to find a cycle of length 42. This is naive but fine for small n
    and unit testing. We keep visited edges per path to avoid reuse.
    """
    from collections import defaultdict, deque

    adj_u: Dict[int, List[Tuple[int, int]]] = defaultdict(list)
    adj_v: Dict[int, List[Tuple[int, int]]] = defaultdict(list)
    for e, u, v in edges:
        adj_u[u].append((e, v))
        adj_v[v].append((e, u))

    # Alternate sides; start from an edge and walk 41 more edges
    def dfs_from(start: Tuple[int, int, int]) -> Optional[List[Tuple[int, int, int]]]:
        e0, u0, v0 = start
        # stack items: (current_side, current_node, path_edges)
        # side 1 means we are at V-side node and will move via adj_v to U; side 0 means at U -> V
        stack = [(1, v0, [(e0, u0, v0)])]  # we used edge e0 from u0->v0
        visited_edge_ids = set([e0])
        while stack:
            side, node, path = stack.pop()
            if len(path) == 42:
                # Check close the cycle back to u0
                last_e, last_u, last_v = path[-1]
                # We need to return to u0 on the next adjacency consistent with alternation:
                # For length 42 cycle, path has 42 edges already; ensure it ends at U node equal to u0.
                # Our path always stores (e,u,v), meaning an edge from u->v. After odd steps, we are at V.
                # After 42 edges, we are at V if started at U? Let's verify:
                # Start: (e0, u0->v0), then side toggles; After 42 edges, parity==0 means we're at U.
                # Simpler: verify that last_v == v0 and last_u == u0 after 42 steps? That's too strict.
                # Use full verification at end using verify_cycle.
                return path
            if side == 1:
                # at V, next edges go V->U using adj_v on this node
                for e_next, u_next in adj_v.get(node, () ):
                    if e_next in (ed for ed,_,_ in path):
                        continue
                    # identify the u that this edge connects from
                    # e_next has endpoints (u_next, node)
                    # append as (e_next, u_next, node)
                    stack.append((0, u_next, path + [(e_next, u_next, node)]))
            else:
                # at U, move U->V
                for e_next, v_next in adj_u.get(node, () ):
                    if e_next in (ed for ed,_,_ in path):
                        continue
                    stack.append((1, v_next, path + [(e_next, node, v_next)]))
        return None

    # Try from each edge as a starting point but limit attempts to avoid explosion
    max_starts = min(1000, len(edges))
    for i in range(max_starts):
        cand = dfs_from(edges[i])
        if cand is not None and len(cand) == 42:
            # sanity verify
            if verify_cycle(hash_fn.header, n, cand):
                return cand
    return None


def verify_cycle(header: bytes, n: int, cycle_edges: List[Tuple[int, int, int]]) -> bool:
    """Verify that the given edges form a valid 42-length cycle under the keyed hash.

    cycle_edges: list of (edge_index, u, v)
    """
    if len(cycle_edges) != 42:
        return False
    h = CuckooHash(header)
    seen_e = set()
    # Recompute all endpoints and check adjacency
    # We expect edges to alternate between U->V with matching nodes
    prev_v = None
    for idx, (e, u, v) in enumerate(cycle_edges):
        if e in seen_e:
            return False
        seen_e.add(e)
        u2 = h.endpoint(e, 0, n)
        v2 = h.endpoint(e, 1, n)
        if u2 != u or v2 != v:
            return False
        if idx > 0:
            # previous edge end node must match this start node
            prev_e, prev_u, prev_v_real = cycle_edges[idx-1]
            if prev_v_real != u:
                return False
    # close the loop: last v must connect back to first u
    first_e, first_u, first_v = cycle_edges[0]
    last_e, last_u, last_v = cycle_edges[-1]
    if last_v != first_u:
        return False
    return True


def solve(config: SolverConfig) -> SolveResult:
    """Prototype solver using binning and local degree trimming.

    This is not optimized; it aims to provide a scaffold with deterministic behavior and metrics.
    """
    t0 = time.perf_counter()
    metrics: Dict[str, int] = {
        "hashes_computed": 0,
        "edges_touched": 0,
        "attempts": 0,
    }

    # Setup hash
    hash_fn = CuckooHash(config.header)
    n = config.n
    if config.k < 1:
        raise ValueError("k must be >= 1")

    total_edges = 1 << n

    time_budget_sec = config.time_budget_sec

    found: Optional[List[Tuple[int, int, int]]] = None
    peak_mem_bytes = 0

    with PeakMem() as pm:
        attempt = 0
        while attempt < config.max_attempts:
            attempt += 1
            metrics["attempts"] = attempt

            # Choose binning by k: split edges into k bins by high bits of edge index
            bins = config.k
            bin_size = (total_edges + bins - 1) // bins
            for b in range(bins):
                start = b * bin_size
                end = min(total_edges, start + bin_size)
                if start >= end:
                    continue
                # Stream through edges in this bin
                edges = list(range(start, end))
                metrics["edges_touched"] += len(edges)
                # Local trim
                trimmed = _trim_bin(hash_fn, n, edges, rounds=2)
                # Count hashes: for each edge per round, we compute two endpoints twice
                metrics["hashes_computed"] += len(edges) * 2 * 2
                # Try to find cycle 42 in this bin
                cycle = _find_cycle_42(hash_fn, n, trimmed)
                if cycle is not None and verify_cycle(config.header, n, cycle):
                    found = cycle
                    break
                # update peak memory snapshot
                peak_mem_bytes = max(peak_mem_bytes, pm.peak())
            if found is not None:
                break
            # Check time budget
            if time_budget_sec is not None and (time.perf_counter() - t0) >= time_budget_sec:
                break
        # final peak
        peak_mem_bytes = max(peak_mem_bytes, pm.peak())

    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    return SolveResult(
        found=found is not None,
        cycle_edges=found or [],
        elapsed_ms=elapsed_ms,
        peak_mem_bytes=peak_mem_bytes,
        metrics=metrics,
    )
