Design Overview: Linear Time Memory Tradeoff Solver (Prototype)

Hashing:
- Uses hashlib.blake2b keyed by header as a pluggable endpoint hash returning nodes in [0,2^n).
- Interface is CuckooHash.endpoint(edge_index, side, n). Can be swapped with SipHash2-4 later.

Memory Tradeoff:
- Partition edges into k bins by edge index range so per-bin processing stays within N/k working set.
- For each bin, recompute endpoints on demand (no global bitmaps), keeping only small per-bin degree maps.
- Local trimming: multiple rounds remove leaf edges (degree 1 on either side) to approximate lean trimming.

Traversal:
- Build small adjacency maps from trimmed edges and run bounded DFS to attempt finding a 42-edge cycle.
- Use verify_cycle() to validate a candidate cycle.

Determinism:
- All results are deterministic with given header, n, threads, seed. No randomness used in this prototype.

Metrics:
- Track hashes_computed (estimated), edges_touched, attempts, elapsed time, and peak memory via tracemalloc.

Parallelism:
- Not implemented in the prototype; threads parameter is accepted but unused.

Limitations:
- Not performance-optimized; intended for correctness scaffolding and unit tests on small n.
- DFS approach will not scale to large n for cycle finding.
