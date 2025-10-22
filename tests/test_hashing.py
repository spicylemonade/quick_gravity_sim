from cuckatoo_solver.hashing import CuckooHash


def test_determinism():
    header = bytes.fromhex("00" * 32)
    h1 = CuckooHash(header)
    h2 = CuckooHash(header)
    for e in [0, 1, 2, 12345, 99999]:
        for side in [0, 1]:
            assert h1.endpoint(e, side, 16) == h2.endpoint(e, side, 16)


def test_range():
    header = bytes.fromhex("ab" * 32)
    h = CuckooHash(header)
    for n in range(4, 16):
        N = 1 << n
        for e in [0, 7, 123, 9999]:
            for side in [0, 1]:
                v = h.endpoint(e, side, n)
                assert 0 <= v < N
