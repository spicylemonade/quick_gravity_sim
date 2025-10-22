from cuckatoo_solver.solver import verify_cycle


def test_verify_cycle_rejects_bad():
    header = bytes.fromhex("00" * 32)
    n = 8
    # not 42 edges
    assert verify_cycle(header, n, []) is False
    assert verify_cycle(header, n, [0, 1, 2]) is False


def test_verify_cycle_structure():
    # This test only checks API robustness; we don't construct a real cycle here.
    header = bytes.fromhex("11" * 32)
    n = 8
    fake = [(i, 0, 0) for i in range(42)]
    assert verify_cycle(header, n, fake) is False
