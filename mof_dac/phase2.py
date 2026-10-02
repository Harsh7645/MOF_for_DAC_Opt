"""Run convex control and an explicitly nonconvex 50-variable SNN pilot."""

import argparse
import json
from pathlib import Path

import numpy as np

from .formulation import Problem
from .data import load_instance
from .instances import decode_slot_state, slot_problem
from .optimizers import exact, feasible_batches, repair_nearest
from .snn import solve_convex_control, solve_nonconvex_experiment


def _record(problem, result, decoded=None):
    raw = result.x
    return {"status": result.status, "seconds": result.seconds,
            "energy": float(problem.energy(raw)) if raw is not None else None,
            "violations": ({k: float(v) for k, v in problem.violations(raw).items()}
                           if raw is not None else None),
            "diagnostics": result.diagnostics,
            "decoded_energy": float(problem.energy(decoded)) if decoded is not None else None,
            "decoded_feasible": (bool(problem.feasible(decoded, binary=True))
                                 if decoded is not None else None)}


def run_pilot(seeds=range(5), max_iterations=5000, equality_band=0.0):
    convex = Problem(("a", "b"), np.array([-1., -2.]), np.zeros((2, 2)),
                     np.ones((1, 2)), np.array([1.]), np.empty((0, 2)), np.empty(0))
    convex_result = solve_convex_control(convex, np.array([0.5, 0.5]),
                                         max_iterations=max_iterations,
                                         equality_band=equality_band)
    convex_sensitivity = []
    for band in (0.0, 1e-6, 1e-3):
        result = solve_convex_control(convex, np.array([0.5, 0.5]),
                                      max_iterations=max_iterations, equality_band=band)
        convex_sensitivity.append({"equality_band": band, **_record(convex, result)})
    slots, count = 25, 12
    problem = slot_problem(slots, seed=11, functionalized=count)
    runs = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        b_slots = rng.choice(slots, count, replace=False)
        x0 = decode_slot_state(np.column_stack((np.ones(slots), np.zeros(slots))).ravel(), 0)
        x0[2 * b_slots] = 0
        x0[2 * b_slots + 1] = 1
        result = solve_nonconvex_experiment(problem, x0, max_iterations=max_iterations,
                                            equality_band=equality_band)
        decoded = decode_slot_state(result.x, count) if result.x is not None else None
        record = _record(problem, result, decoded)
        record.update(seed=int(seed), initial_energy=float(problem.energy(x0)))
        runs.append(record)
    tiny, _ = load_instance(Path(__file__).resolve().parents[1] / "data/synthetic/toy.json")
    oracle = exact(tiny)
    optimum = float(tiny.energy(oracle.x))
    tiny_runs = []
    starts = np.vstack([batch for batch in feasible_batches(tiny) if len(batch)])[:3]
    for seed, x0 in enumerate(starts):
        result = solve_nonconvex_experiment(tiny, x0, max_iterations=max_iterations,
                                            equality_band=equality_band)
        repaired = repair_nearest(tiny, result.x) if result.x is not None else None
        record = _record(tiny, result, repaired.x if repaired is not None else None)
        record.update(seed=seed, initial_energy=float(tiny.energy(x0)),
                      decoded_optimum_hit=bool(repaired is not None and repaired.x is not None
                                               and np.isclose(tiny.energy(repaired.x), optimum)))
        tiny_runs.append(record)
    return {"schema_version": 2, "upstream": "snn-opt==0.6.0",
            "convex_control": _record(convex, convex_result),
            "convex_equality_band_sensitivity": convex_sensitivity,
            "tiny_nonconvex_reference": {"variables": tiny.n, "oracle_energy": optimum,
                                         "runs": tiny_runs},
            "nonconvex_pilot": {"variables": problem.n, "slots": slots,
                                "functionalized": count, "runs": runs,
                                "certificate": None,
                                "interpretation": "experimental raw-W heuristic"}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("docs/phase2_results.json"))
    parser.add_argument("--iterations", type=int, default=5000)
    parser.add_argument("--equality-band", type=float, default=0.0)
    args = parser.parse_args()
    report = run_pilot(max_iterations=args.iterations, equality_band=args.equality_band)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Saved {args.output}: 1 convex control + 5 nonconvex 50-variable runs")


if __name__ == "__main__":
    main()
