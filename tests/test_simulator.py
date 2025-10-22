import numpy as np
import math
import pytest
from quick_gravity_sim import NBodySimulator, Body, G


def make_two_body():
    M = 10.0
    m = 1.0
    r = 1.0
    v = math.sqrt(G * M / r)
    bodies = [
        Body(mass=M, pos=np.array([0.0, 0.0]), vel=np.array([0.0, 0.0])),
        Body(mass=m, pos=np.array([r, 0.0]), vel=np.array([0.0, v])),
    ]
    return bodies


def test_momentum_conservation():
    bodies = make_two_body()
    sim = NBodySimulator(bodies)
    p0 = sim.total_momentum().copy()
    for _ in range(1000):
        sim.step(0.001)
    p1 = sim.total_momentum()
    assert np.allclose(p0, p1, atol=1e-9)


def test_energy_approx_conservation_small_dt():
    bodies = make_two_body()
    sim = NBodySimulator(bodies)
    e0 = sim.total_energy()
    for _ in range(5000):
        sim.step(0.0005)
    e1 = sim.total_energy()
    rel_err = abs(e1 - e0) / (abs(e0) + 1e-12)
    assert rel_err < 1e-3


def test_circular_orbit_radius_stability():
    bodies = make_two_body()
    sim = NBodySimulator(bodies)
    # Track radius of smaller mass from the large mass (assumed index 0 is central)
    r_values = []
    for _ in range(5000):
        sim.step(0.0005)
        r_vec = sim.state.positions[1] - sim.state.positions[0]
        r_values.append(np.linalg.norm(r_vec))
    r_values = np.array(r_values)
    r_mean = float(np.mean(r_values))
    r_std = float(np.std(r_values))
    assert abs(r_mean - 1.0) < 5e-3
    assert r_std < 1e-2


def test_center_of_mass_stationary_if_initial_momentum_zero():
    # Symmetric velocities to get zero net momentum
    bodies = [
        Body(1.0, np.array([-1.0, 0.0]), np.array([0.5, 0.0])),
        Body(1.0, np.array([1.0, 0.0]), np.array([-0.5, 0.0])),
    ]
    sim = NBodySimulator(bodies)
    com0 = sim.center_of_mass().copy()
    for _ in range(2000):
        sim.step(0.001)
    com1 = sim.center_of_mass()
    assert np.allclose(com0, com1, atol=1e-8)
