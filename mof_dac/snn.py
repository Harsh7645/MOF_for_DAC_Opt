"""Verified upstream convention; convex-only execution scaffold.

API reference commit: f6623472204b2b5b7955c98e91024a391cf96fff.
Indefinite MOF dynamics require a separately validated Phase 2 extension.
"""

from importlib.metadata import version
from time import perf_counter

import numpy as np

from .optimizers import Result


def _solve(problem, x0, *, max_iterations, equality_band, method, theory_scope):
    x0 = problem.state(x0)
    if x0.shape != (problem.n,) or max_iterations < 1:
        raise ValueError("Expected x0[n] and positive iteration budget")
    A, b, C, d = problem.snn_arrays(equality_band=equality_band)
    try:
        from snn_opt import solve_qp
    except ImportError as error:
        raise ImportError('Install optional integration with pip install -e ".[snn]"') from error
    start = perf_counter()
    result = solve_qp(A, b, C, d, x0, max_iterations=max_iterations,
                      backend="python", record_trajectory=False)
    state = np.asarray(result.final_x, dtype=float)
    valid = state.shape == (problem.n,) and np.isfinite(state).all()
    diagnostics = {"upstream_version": version("snn-opt"),
                   "upstream_converged": bool(result.converged),
                   "reason": str(result.convergence_reason),
                   "iterations_used": int(result.iterations_used),
                   "equality_band": equality_band,
                   "max_iterations": max_iterations,
                   "original_constraints_feasible": bool(valid and problem.feasible(state)),
                   "theory_scope": theory_scope,
                   "curvature": problem.spectrum()}
    for name in ("joint_feasible", "projection_budget_exhausted", "kkt_residual", "kkt_scale",
                 "kkt_tolerance", "stationarity_residual", "final_proj_grad_norm",
                 "max_violation_rows_raw", "max_violation_box"):
        value = getattr(result, name, None)
        if isinstance(value, (bool, np.bool_)):
            diagnostics[name] = bool(value)
        elif value is not None:
            diagnostics[name] = float(value) if np.isfinite(value) else None
    diagnostics["optimality_test"] = str(getattr(result, "optimality_test", "unknown"))
    if not valid:
        status = "invalid_output"
    elif diagnostics["upstream_converged"] and diagnostics["original_constraints_feasible"]:
        status = "converged_feasible"
    elif diagnostics["original_constraints_feasible"]:
        status = "feasible_unconverged"
    else:
        status = "returned_infeasible"
    return Result(method, state if valid else None, perf_counter() - start, status, diagnostics)


def solve_convex_control(problem, x0, *, max_iterations=2000, equality_band=0.0):
    """Call optional snn_opt on a PSD control; never shift its objective."""
    if not problem.spectrum()["full_space_psd"]:
        raise ValueError("Indefinite Hessian: use the explicitly experimental entry point")
    return _solve(problem, x0, max_iterations=max_iterations, equality_band=equality_band,
                  method="snn_convex_control", theory_scope="convex_control")


def solve_nonconvex_experiment(problem, x0, *, max_iterations=2000, equality_band=0.0):
    """Run raw indefinite coefficients with no convergence/optimality guarantee."""
    if problem.spectrum()["full_space_psd"]:
        raise ValueError("Use solve_convex_control for a PSD problem")
    return _solve(problem, x0, max_iterations=max_iterations, equality_band=equality_band,
                  method="snn_nonconvex_experiment",
                  theory_scope="experimental_outside_convex_guarantee")
