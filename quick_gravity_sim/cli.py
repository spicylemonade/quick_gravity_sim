import argparse
import csv
import sys
import numpy as np
from .simulator import NBodySimulator
from .body import Body
from .constants import G as G_DEFAULT


def two_body_example():
    # Units chosen so that circular orbit is simple
    # Central mass M at origin, small mass m in circular orbit of radius r with speed v = sqrt(G*M/r)
    M = 10.0
    m = 1.0
    r = 1.0
    v = np.sqrt(G_DEFAULT * M / r)
    bodies = [
        Body(mass=M, pos=np.array([0.0, 0.0]), vel=np.array([0.0, 0.0]), name="M"),
        Body(mass=m, pos=np.array([r, 0.0]), vel=np.array([0.0, v]), name="m"),
    ]
    return bodies


def three_body_example():
    # Simple three-body setup (non-resonant random-ish)
    bodies = [
        Body(mass=10.0, pos=np.array([0.0, 0.0]), vel=np.array([0.0, 0.0]), name="A"),
        Body(mass=1.0, pos=np.array([1.0, 0.0]), vel=np.array([0.0, 3.5]), name="B"),
        Body(mass=1.0, pos=np.array([-1.0, 0.0]), vel=np.array([0.0, -3.5]), name="C"),
    ]
    return bodies


def write_csv(output_path, pos_traj):
    # pos_traj shape: (T, N, 2)
    T, N, _ = pos_traj.shape
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        header = ["t"] + [f"x{i}" for i in range(N)] + [f"y{i}" for i in range(N)]
        writer.writerow(header)
        for t in range(T):
            row = [t]
            row += [pos_traj[t, i, 0] for i in range(N)]
            row += [pos_traj[t, i, 1] for i in range(N)]
            writer.writerow(row)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run a simple 2D N-body gravity simulation")
    parser.add_argument("--example", choices=["two_body", "three_body"], default="two_body", help="Which preset to run")
    parser.add_argument("--steps", type=int, default=2000, help="Number of steps to simulate")
    parser.add_argument("--dt", type=float, default=0.01, help="Time step")
    parser.add_argument("--G", type=float, default=G_DEFAULT, help="Gravitational constant")
    parser.add_argument("--softening", type=float, default=0.0, help="Optional Plummer softening length")
    parser.add_argument("--out", type=str, default=None, help="Optional CSV output for positions trajectory")
    args = parser.parse_args(argv)

    if args.example == "two_body":
        bodies = two_body_example()
    else:
        bodies = three_body_example()

    sim = NBodySimulator(bodies, G=args.G)
    traj = sim.run(args.steps, args.dt, softening=args.softening, record_positions=(args.out is not None))

    if args.out is not None and traj is not None:
        write_csv(args.out, traj)
        print(f"Wrote trajectory to {args.out}")
    else:
        # Print final positions and velocities
        print("Final positions:")
        print(sim.state.positions)
        print("Final velocities:")
        print(sim.state.velocities)


if __name__ == "__main__":
    sys.exit(main())
