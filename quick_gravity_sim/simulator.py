from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Iterable, Optional
from .body import Body
from .constants import G as G_DEFAULT


@dataclass
class NBodyState:
    positions: np.ndarray  # shape (N, 2)
    velocities: np.ndarray  # shape (N, 2)
    masses: np.ndarray  # shape (N,)


class NBodySimulator:
    """2D N-body gravitational simulator using a symplectic (kick-drift-kick) leapfrog integrator.

    Notes:
    - Units are arbitrary; choose G and initial conditions consistently.
    - Bodies are point masses; no collisions or softening by default.
    - Complexity: O(N^2) for direct summation.
    """

    def __init__(self, bodies: Iterable[Body], G: float = G_DEFAULT):
        bodies = list(bodies)
        if len(bodies) == 0:
            raise ValueError("At least one body is required")
        self.n = len(bodies)
        self.G = float(G)
        self.state = NBodyState(
            positions=np.stack([np.asarray(b.pos, dtype=float).reshape(2) for b in bodies], axis=0),
            velocities=np.stack([np.asarray(b.vel, dtype=float).reshape(2) for b in bodies], axis=0),
            masses=np.array([float(b.mass) for b in bodies], dtype=float),
        )

    # ---------------- Physics helpers ----------------
    def accelerations(self, positions: Optional[np.ndarray] = None, softening: float = 0.0) -> np.ndarray:
        """Compute accelerations on each body due to gravity from all others.

        Args:
            positions: Optional positions array shape (N,2). If None, uses current state's positions.
            softening: Plummer softening length epsilon; if >0, uses r2 += epsilon^2 to avoid singularity.
        Returns:
            accel: (N,2) accelerations array.
        """
        if positions is None:
            positions = self.state.positions
        N = self.n
        accel = np.zeros_like(positions)
        m = self.state.masses
        G = self.G
        eps2 = float(softening) ** 2
        # Direct pairwise summation
        for i in range(N):
            # Vector from i to all j
            diff = positions - positions[i]  # (N,2)
            # Mask out self
            diff[i] = 0.0
            r2 = np.sum(diff * diff, axis=1)  # (N,)
            if eps2 > 0.0:
                r2 = r2 + eps2
            inv_r3 = np.zeros_like(r2)
            nz = r2 > 0.0
            inv_r3[nz] = 1.0 / (r2[nz] * np.sqrt(r2[nz]))
            # Sum G * m_j * r_ij / |r_ij|^3
            a_i = (G * (m * inv_r3)[:, None] * diff).sum(axis=0)
            accel[i] = a_i
        return accel

    def potential_energy(self, positions: Optional[np.ndarray] = None, softening: float = 0.0) -> float:
        if positions is None:
            positions = self.state.positions
        N = self.n
        G = self.G
        m = self.state.masses
        eps2 = float(softening) ** 2
        U = 0.0
        for i in range(N):
            diff = positions[i + 1 :] - positions[i]
            r2 = np.sum(diff * diff, axis=1)
            if eps2 > 0.0:
                r2 = r2 + eps2
            r = np.sqrt(r2)
            # Avoid divide by zero for coincident points; contribute zero potential if r=0
            mask = r > 0.0
            if np.any(mask):
                U -= G * m[i] * np.sum(m[i + 1 :][mask] / r[mask])
        return float(U)

    def kinetic_energy(self, velocities: Optional[np.ndarray] = None) -> float:
        if velocities is None:
            velocities = self.state.velocities
        m = self.state.masses
        return float(0.5 * np.sum(m[:, None] * velocities * velocities))

    def total_energy(self, softening: float = 0.0) -> float:
        return self.kinetic_energy() + self.potential_energy(softening=softening)

    def total_momentum(self) -> np.ndarray:
        m = self.state.masses
        v = self.state.velocities
        return (m[:, None] * v).sum(axis=0)

    def center_of_mass(self) -> np.ndarray:
        m = self.state.masses
        r = self.state.positions
        M = float(np.sum(m))
        if M == 0.0:
            return np.array([0.0, 0.0], dtype=float)
        return (m[:, None] * r).sum(axis=0) / M

    # ---------------- Integration ----------------
    def step(self, dt: float, softening: float = 0.0):
        """Advance the system by one time step using leapfrog (kick-drift-kick).

        Args:
            dt: Time step
            softening: Optional softening length
        """
        dt = float(dt)
        s = self.state
        # First half-kick
        a0 = self.accelerations(s.positions, softening=softening)
        s.velocities = s.velocities + 0.5 * dt * a0
        # Drift
        s.positions = s.positions + dt * s.velocities
        # Second half-kick using new positions
        a1 = self.accelerations(s.positions, softening=softening)
        s.velocities = s.velocities + 0.5 * dt * a1

    def run(self, steps: int, dt: float, softening: float = 0.0, record_positions: bool = False):
        """Run multiple steps. Optionally record position trajectory.

        Returns:
            If record_positions True: np.ndarray shape (steps+1, N, 2) including initial positions.
            Else: None
        """
        if record_positions:
            traj = np.zeros((steps + 1, self.n, 2), dtype=float)
            traj[0] = self.state.positions
            for t in range(1, steps + 1):
                self.step(dt, softening=softening)
                traj[t] = self.state.positions
            return traj
        else:
            for _ in range(steps):
                self.step(dt, softening=softening)
            return None
