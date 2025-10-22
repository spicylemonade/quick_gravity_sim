from cuckatoo_solver.solver import SolverConfig, solve


def test_solver_runs_small():
    header = bytes.fromhex("00" * 32)
    cfg = SolverConfig(header=header, n=8, k=2, threads=1, max_attempts=1, time_budget_sec=0.05)
    res = solve(cfg)
    assert res.found in (True, False)
    assert isinstance(res.elapsed_ms, float)
    assert isinstance(res.peak_mem_bytes, int)
    assert isinstance(res.metrics, dict)
