quick_gravity_sim

A simple Python 2D N-body gravity simulator. Focuses on correctness and testability (no GUI required). Includes:
- Newtonian gravity in 2D with configurable gravitational constant G.
- Leapfrog (velocity Verlet) integrator for improved energy stability.
- Convenience classes for bodies and simulator.
- CLI to run sample simulations.
- Unit tests for conservation of momentum, approximate energy conservation, and circular orbit stability.

Getting Started
1) Install dependencies:
   pip install -r requirements.txt

2) Run tests:
   pytest -q

3) Run an example simulation (two-body circular orbit):
   python -m quick_gravity_sim.cli --example two_body --steps 2000 --dt 0.01 --output out.csv

4) Plot results (optional):
   python -m quick_gravity_sim.cli --example three_body --steps 5000 --dt 0.002 --output three.csv

Package Structure
- quick_gravity_sim/
  - __init__.py
  - body.py          : Body dataclass representing a massive particle
  - simulator.py     : NBodySimulator implementing gravity and leapfrog integration
  - constants.py     : Physical constants (G)
  - cli.py           : Command-line interface for running simulations

Physics Notes
- Uses Newtonian gravity F = G m1 m2 / r^2 in 2D; acceleration a_i = sum_j G m_j r_ij / |r_ij|^3.
- Integration uses velocity Verlet (aka leapfrog), which is symplectic and generally conserves energy better than naive Euler.

License
MIT