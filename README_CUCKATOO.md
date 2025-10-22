# Cuckatoo Cycle Solver (Prototype)

This is a prototype linear-time memory tradeoff solver for Cuckoo/Cuckatoo cycle (target cycle length 42) implemented in Python for research and testing. It includes:

- Pluggable keyed hashing (default: hashlib.blake2b keyed)
- Simple binning-based local trimming to reduce memory pressure
- Cycle verification routine
- CLI entry point and tests for basic functionality

Note: This is not an optimized or production-grade solver. It is intended to scaffold further work per the spec.

Usage:

- CLI: `python3 -m cuckatoo_solver.cli <header_hex> <n> <k> [--threads N] [--max-attempts M] [--time-budget-sec S]`
- As a library: see tests for examples.

Run tests:

- `python3 -m pytest -q tests`

Benchmark example:

- `python3 benchmarks/benchmark.py --n 8 --k 2 --attempts 1`
