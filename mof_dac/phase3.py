"""Run development and frozen held-out synthetic solver benchmarks."""

import argparse
import hashlib
import json
import os
import platform
from importlib.metadata import version
from pathlib import Path

import numpy as np

from .gurobi import solve_gurobi
from .instances import decode_slot_state, slot_problem
from .optimizers import exact, slot_simulated_annealing
from .snn import solve_nonconvex_experiment


def _initial_state(slots, functionalized, seed):
    return decode_slot_state(np.random.default_rng(seed).normal(size=2 * slots), functionalized)


def _stats(rows, field="absolute_gap"):
    values = np.asarray([row[field] for row in rows if row.get(field) is not None], dtype=float)
    return {"count": int(len(rows)), "scored_count": int(len(values)),
            "mean": float(np.mean(values)) if len(values) else None,
            "median": float(np.median(values)) if len(values) else None,
            "p90": float(np.percentile(values, 90)) if len(values) else None,
            "maximum": float(np.max(values)) if len(values) else None,
            "optimum_hits": int(np.sum(np.isclose(values, 0, atol=1e-8))) if len(values) else 0}


def _reference(problem, time_limit):
    gurobi = solve_gurobi(problem, time_limit=time_limit, seed=0, threads=1)
    energy = float(problem.energy(gurobi.x)) if gurobi.x is not None else None
    record = {"status": gurobi.status, "seconds": gurobi.seconds, "energy": energy,
              "feasible": bool(gurobi.x is not None and problem.feasible(gurobi.x, binary=True)),
              "diagnostics": gurobi.diagnostics}
    if problem.n <= 20:
        oracle = exact(problem)
        oracle_energy = float(problem.energy(oracle.x)) if oracle.x is not None else None
        record["enumeration"] = {"status": oracle.status, "seconds": oracle.seconds,
                                 "energy": oracle_energy,
                                 "feasible_states": oracle.diagnostics.get("feasible_states")}
        if gurobi.status == "optimal" and not np.isclose(energy, oracle_energy, atol=1e-8):
            raise RuntimeError("Gurobi and exact enumeration disagree")
    return record


def _sa_rows(problem, functionalized, reference_energy, instance_seed, budgets, solver_seeds):
    rows = []
    for steps in budgets:
        for solver_seed in solver_seeds:
            result = slot_simulated_annealing(problem, functionalized, seed=solver_seed, steps=steps)
            energy = float(problem.energy(result.x)) if result.x is not None else None
            rows.append({"instance_seed": instance_seed, "solver_seed": solver_seed,
                         "steps": steps, "status": result.status, "seconds": result.seconds,
                         "energy": energy,
                         "feasible": bool(result.x is not None and problem.feasible(result.x, binary=True)),
                         "absolute_gap": (energy - reference_energy
                                          if energy is not None and reference_energy is not None else None),
                         "diagnostics": result.diagnostics})
    return rows


def _snn_row(problem, functionalized, reference_energy, instance_seed, max_iterations):
    x0 = _initial_state(problem.n // 2, functionalized, instance_seed)
    result = solve_nonconvex_experiment(problem, x0, max_iterations=max_iterations,
                                        equality_band=0.0)
    decoded = decode_slot_state(result.x, functionalized) if result.x is not None else None
    decoded_energy = float(problem.energy(decoded)) if decoded is not None else None
    return {"instance_seed": instance_seed, "initial_energy": float(problem.energy(x0)),
            "max_iterations": max_iterations, "status": result.status, "seconds": result.seconds,
            "raw_feasible": bool(result.x is not None and problem.feasible(result.x)),
            "raw_violations": ({k: float(v) for k, v in problem.violations(result.x).items()}
                               if result.x is not None else None),
            "decoded_feasible": bool(decoded is not None and problem.feasible(decoded, binary=True)),
            "decoded_energy": decoded_energy,
            "absolute_gap": (decoded_energy - reference_energy
                             if decoded_energy is not None and reference_energy is not None else None),
            "diagnostics": result.diagnostics}


def run_heldout(*, instance_seeds=range(100, 120), bit_sizes=(12, 20, 50),
                sa_budgets=(250, 1000, 4000), solver_seeds=range(3),
                snn_iterations=2000, time_limit=30.0):
    instances = []
    for bits in bit_sizes:
        if bits % 2:
            raise ValueError("bit sizes must be even")
        slots, functionalized = bits // 2, bits // 4
        for instance_seed in instance_seeds:
            problem = slot_problem(slots, seed=instance_seed, functionalized=functionalized,
                                   interaction_density=0.35, interaction_scale=1.0)
            reference = _reference(problem, time_limit)
            reference_energy = reference["energy"] if reference["status"] == "optimal" else None
            sa = _sa_rows(problem, functionalized, reference_energy, instance_seed,
                          sa_budgets, solver_seeds)
            snn = _snn_row(problem, functionalized, reference_energy, instance_seed, snn_iterations)
            instances.append({"bits": bits, "slots": slots, "functionalized": functionalized,
                              "instance_seed": instance_seed,
                              "parameter_regime": "synthetic_dense_frustrated",
                              "interaction_density": 0.35, "interaction_scale": 1.0,
                              "reference": reference, "sa_runs": sa, "snn_run": snn})
    by_size = {}
    for bits in bit_sizes:
        selected = [row for row in instances if row["bits"] == bits]
        sa_rows = [run for row in selected for run in row["sa_runs"]]
        snn_rows = [row["snn_run"] for row in selected]
        by_size[str(bits)] = {
            "instances": len(selected),
            "certified_references": sum(row["reference"]["status"] == "optimal" for row in selected),
            "sa_feasible_fraction": float(np.mean([row["feasible"] for row in sa_rows])),
            "sa_gap": _stats(sa_rows),
            "sa_gap_by_steps": {str(steps): _stats(
                [row for row in sa_rows if row["steps"] == steps])
                for steps in sa_budgets},
            "snn_raw_feasible_fraction": float(np.mean([row["raw_feasible"] for row in snn_rows])),
            "snn_decoded_feasible_fraction": float(np.mean([row["decoded_feasible"] for row in snn_rows])),
            "snn_decoded_gap": _stats(snn_rows),
        }
    return {"protocol": {"instance_seeds": list(instance_seeds), "bit_sizes": list(bit_sizes),
                         "sa_budgets": list(sa_budgets), "sa_solver_seeds": list(solver_seeds),
                         "snn_iterations": snn_iterations,
                         "gurobi_time_limit_seconds": time_limit, "gurobi_threads": 1},
            "summary_by_bits": by_size, "instances": instances}


def run_benchmark(phase2_path, *, quick=False):
    phase2_path = Path(phase2_path)
    phase2 = json.loads(phase2_path.read_text(encoding="utf-8"))
    seeds = range(100, 103) if quick else range(100, 120)
    heldout = run_heldout(instance_seeds=seeds,
                          sa_budgets=(100, 400) if quick else (250, 1000, 4000),
                          solver_seeds=range(2) if quick else range(3),
                          snn_iterations=200 if quick else 2000,
                          time_limit=10 if quick else 30)
    return {"schema_version": 2, "parameter_regime": "synthetic",
            "environment": {"python": platform.python_version(), "platform": platform.platform(),
                            "logical_cpus": os.cpu_count(), "numpy": version("numpy"),
                            "scipy": version("scipy"), "snn_opt": version("snn-opt"),
                            "gurobipy": version("gurobipy")},
            "phase2_source": str(phase2_path),
            "phase2_source_sha256": hashlib.sha256(phase2_path.read_bytes()).hexdigest(),
            "phase2_schema_version": phase2.get("schema_version"), "heldout": heldout,
            "surrogate_screening": {"status": "blocked_pending_target_and_data_access",
                                    "preferred_dataset": "ODAC25",
                                    "reason": "Requires target definition, storage, and gated model/data access"},
            "claims": ["Synthetic held-out solver-quality comparison only",
                       "No CPU-speed, hardware-energy, chemistry or DAC-performance claim"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase2", type=Path, default=Path("docs/phase2_results.json"))
    parser.add_argument("--output", type=Path, default=Path("docs/phase3_results.json"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    result = run_benchmark(args.phase2, quick=args.quick)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    total = len(result["heldout"]["instances"])
    certified = sum(row["reference"]["status"] == "optimal"
                    for row in result["heldout"]["instances"])
    print(f"Saved {args.output}: {certified}/{total} certified held-out instances")


if __name__ == "__main__":
    main()
