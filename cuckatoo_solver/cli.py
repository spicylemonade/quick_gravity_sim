from __future__ import annotations
import argparse
import binascii
import json
from .solver import SolverConfig, solve


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Cuckoo/Cuckatoo 42-cycle solver (prototype)")
    p.add_argument("header", help="32-byte header in hex")
    p.add_argument("n", type=int, help="graph size exponent (N=2^n)")
    p.add_argument("k", type=int, help="memory reduction factor (>=2)")
    p.add_argument("threads", type=int, help="threads (1,2,4,8)")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--max_attempts", type=int, default=1)
    p.add_argument("--time_budget_sec", type=float, default=2.0)
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    header = binascii.unhexlify(args.header)
    cfg = SolverConfig(
        header=header,
        n=args.n,
        k=args.k,
        threads=args.threads,
        seed=args.seed,
        max_attempts=args.max_attempts,
        time_budget_sec=args.time_budget_sec,
    )
    res = solve(cfg)
    out = {
        "status": "FOUND" if res.found else "NOT_FOUND",
        "solution": res.cycle_edges,
        "metrics": {
            "elapsed_ms": res.elapsed_ms,
            "peak_memory_bytes": res.peak_mem_bytes,
            **res.metrics,
        },
        "build_info": res.build_info,
    }
    print(json.dumps(out))


if __name__ == "__main__":
    main()
