"""Run the deterministic Phase 1 synthetic verification sweep."""

import argparse
import json
from pathlib import Path

import numpy as np

from .instances import phase1_instances
from .optimizers import exact, simulated_annealing, slsqp_relaxation


def run_sweep(seeds=range(10)):
    records = []
    for name, problem in phase1_instances().items():
        oracle = exact(problem)
        optimum = float(problem.energy(oracle.x)) if oracle.x is not None else None
        runs = [simulated_annealing(problem, seed=seed, steps=3000) for seed in seeds]
        feasible = [run for run in runs if run.x is not None and problem.feasible(run.x, binary=True)]
        hits = int(sum(np.isclose(problem.energy(run.x), optimum, atol=1e-8)
                       for run in feasible)) if optimum is not None else 0
        relaxed = slsqp_relaxation(problem, seed=0, restarts=4)
        records.append({
            "name": name, "variables": problem.n,
            "expected_infeasible": name.endswith("infeasible"),
            "oracle_status": oracle.status, "oracle_energy": optimum,
            "feasible_states": oracle.diagnostics["feasible_states"],
            "sa_runs": len(runs), "sa_feasible_runs": len(feasible),
            "sa_optimum_hits": hits,
            "slsqp_status": relaxed.status,
            "equality_audit": relaxed.diagnostics.get("equality_audit"),
        })
    return {"schema_version": 1, "parameter_regime": "synthetic",
            "seeds": list(seeds), "instances": records,
            "claims": ["Numerical formulation and solvers only",
                       "No chemistry, SNN, Gurobi, DFT, surrogate, or hardware validation"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("docs/phase1_results.json"))
    args = parser.parse_args()
    report = run_sweep()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Saved {args.output}: {len(report['instances'])} synthetic instances")


if __name__ == "__main__":
    main()
