from __future__ import annotations
import hashlib
import struct
from dataclasses import dataclass
from typing import Protocol

class HashPlugin(Protocol):
    def digest64(self, key: bytes, msg: bytes) -> int: ...

class Blake2b64Plugin:
    def digest64(self, key: bytes, msg: bytes) -> int:
        h = hashlib.blake2b(key=key, digest_size=8)
        h.update(msg)
        return int.from_bytes(h.digest(), "little")

blake2b64 = Blake2b64Plugin()

@dataclass(frozen=True)
class CuckooHash:
    header: bytes
    plugin: HashPlugin = blake2b64

    def endpoint(self, edge_index: int, side: int, n: int) -> int:
        # side: 0 for U, 1 for V
        # Deterministic keyed hash: H(header, edge_index, side) mod 2^n
        msg = self.header + struct.pack("<QB", edge_index, side & 1)
        return self.plugin.digest64(self.header, msg) & ((1 << n) - 1)

    def edge(self, edge_index: int, n: int) -> tuple[int, int]:
        u = self.endpoint(edge_index, 0, n)
        v = self.endpoint(edge_index, 1, n)
        return (u, v)
