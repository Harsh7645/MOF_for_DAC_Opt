"""Run a tiny synthetic research loop: load, solve, decode, audit, save."""

import argparse
import hashlib
import json
import os
import platform
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import numpy as np
import scipy

from .data import load_instance
from .optimizers import Result, exact, repair_nearest, simulated_annealing, slsqp_relaxation


def summarize(problem, result, reference=None):
    record = {"method": result.method, "status": result.status,
              "seconds": result.seconds, "diagnostics": result.diagnostics}
    if result.x is None:
        record.update(x=None, energy=None, binary_feasible=False, absolute_gap=None)
        return record
    feasible = bool(problem.feasible(result.x, binary=True))
    energy = float(problem.energy(result.x))
    record.update(x=result.x.tolist(), energy=energy,
                  selected=[key for key, x in zip(problem.ids, result.x) if x >= 0.5],
                  selection_note="Threshold interpretation; check binary_feasible before use",
                  binary_feasible=feasible,
                  continuous_feasible=bool(problem.feasible(result.x)),
                  violations={k: float(v) for k, v in problem.violations(result.x).items()},
                  absolute_gap=energy - reference if feasible and reference is not None else None)
    return record


def run(instance, *, seed=0):
    start = perf_counter()
    problem, metadata = load_instance(instance)
    if problem.n > 20:
        raise ValueError("Demo includes exhaustive oracle/repair: n must be <=20")
    setup_seconds = perf_counter() - start
    # Run heuristics before oracle; neither solver sees the reference solution.
    sa = simulated_annealing(problem, seed=seed)
    relaxed = slsqp_relaxation(problem, seed=seed)
    candidates = [sa, relaxed]
    if relaxed.x is not None:
        before_rounding = perf_counter()
        rounded = (relaxed.x >= 0.5).astype(float)
        candidates.append(Result("threshold_0.5", rounded, perf_counter() - before_rounding, "rounded"))
        candidates.append(repair_nearest(problem, relaxed.x))
    oracle = exact(problem)
    reference = float(problem.energy(oracle.x)) if oracle.x is not None else None
    A, b, C, d = problem.snn_arrays()
    report = {
        "schema_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
        "instance": str(Path(instance).resolve()),
        "instance_sha256": hashlib.sha256(Path(instance).read_bytes()).hexdigest(),
        "parameter_regime": metadata["parameter_regime"], "energy_units": metadata["energy_units"],
        "seed": seed, "variables": list(problem.ids), "curvature": problem.spectrum(),
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "scipy": scipy.__version__, "platform": platform.platform(),
                        "processor": platform.processor(),
                        "thread_environment": {k: os.environ.get(k) for k in
                                               ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS")}},
        "snn": {"status": "not_run", "reason": "Convex adapter only; nonconvex experiment pending",
                "A_shape": list(A.shape), "b_shape": list(b.shape),
                "C_shape": list(C.shape), "d_shape": list(d.shape), "equality_band": 0.0},
        "oracle": summarize(problem, oracle, reference),
        "results": [summarize(problem, candidate, reference) for candidate in candidates],
        "setup_seconds": setup_seconds,
        "total_seconds": perf_counter() - start,
        "limitations": ["Toy selection constraints do not validate a physical MOF",
                        "Single-seed smoke run is not a benchmark or TTS estimate",
                        "Exact-distance decoding is exponential and separately timed",
                        "SA moves up to four bits; arbitrary feasible sets can still be disconnected",
                        "Gurobi, material surrogates and DFT validation are not run"],
    }
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path, default=Path("data/synthetic/toy.json"))
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output", type=Path, default=Path("results/demo.json"))
    args = parser.parse_args()
    report = run(args.instance, seed=args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Saved {args.output}; oracle energy={report['oracle']['energy']}; "
          f"synthetic={report['parameter_regime'] == 'synthetic'}; SNN not run")


if __name__ == "__main__":
    main()
