from dataclasses import dataclass
import numpy as np
from typing import Optional

@dataclass
class Body:
    """A massive body in 2D space.

    Attributes:
        mass: Scalar mass (must be > 0)
        pos: 2D numpy array (x, y)
        vel: 2D numpy array (vx, vy)
        radius: Optional radius for visualization/collision checks (not used by core engine)
        name: Optional label
    """
    mass: float
    pos: np.ndarray
    vel: np.ndarray
    radius: Optional[float] = None
    name: Optional[str] = None

    def __post_init__(self):
        self.pos = np.asarray(self.pos, dtype=float).reshape(2)
        self.vel = np.asarray(self.vel, dtype=float).reshape(2)
        if self.mass <= 0:
            raise ValueError("Body mass must be positive")
