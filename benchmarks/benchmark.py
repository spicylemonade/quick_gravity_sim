from __future__ import annotations

import argparse
import json
import os
import time

from cuckatoo_solver.solver import SolverConfig, solve


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--header', default='00'*32)
    ap.add_argument('--n', type=int, default=8)
    ap.add_argument('--k', type=int, default=2)
    ap.add_argument('--threads', type=int, default=1)
    ap.add_argument('--attempts', type=int, default=1)
    ap.add_argument('--time-budget-sec', type=float, default=None)
    args = ap.parse_args()

    cfg = SolverConfig(
        header=bytes.fromhex(args.header),
        n=args.n,
        k=args.k,
        threads=args.threads,
        max_attempts=args.attempts,
        time_budget_sec=args.time_budget_sec,
    )
    res = solve(cfg)
    print(json.dumps({
        'status': 'FOUND' if res.found else 'NOT_FOUND',
        'elapsed_ms': res.elapsed_ms,
        'peak_memory_bytes': res.peak_mem_bytes,
        'metrics': res.metrics,
    }, indent=2))


if __name__ == '__main__':
    main()
