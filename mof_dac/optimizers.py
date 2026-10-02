"""Development solvers. Exact enumeration/repair limited to n<=20."""

from dataclasses import dataclass, field
from time import perf_counter

import numpy as np
from scipy.linalg import qr
from scipy.optimize import LinearConstraint, linprog, minimize

from .formulation import Problem


@dataclass
class Result:
    method: str
    x: np.ndarray | None
    seconds: float
    status: str
    diagnostics: dict = field(default_factory=dict)


def feasible_batches(problem: Problem):
    # ponytail: exponential tiny-instance oracle; use a certified MIP solver beyond 20 bits.
    if problem.n > 20:
        raise ValueError("Enumeration and exact-distance repair limited to n<=20")
    shifts = np.arange(problem.n, dtype=np.uint64)
    for start in range(0, 1 << problem.n, 4096):
        integers = np.arange(start, min(start + 4096, 1 << problem.n), dtype=np.uint64)
        x = ((integers[:, None] >> shifts) & 1).astype(np.float64)
        yield x[problem.feasible(x, binary=True)]


def exact(problem):
    start = perf_counter()
    best, energy, count = None, np.inf, 0
    for batch in feasible_batches(problem):
        count += len(batch)
        if len(batch):
            values = problem.energy(batch)
            i = int(np.argmin(values))
            if values[i] < energy:
                best, energy = batch[i].copy(), float(values[i])
    return Result("enumeration", best, perf_counter() - start,
                  "optimal" if best is not None else "infeasible",
                  {"feasible_states": count, "enumerated_states": 1 << problem.n})


def repair_nearest(problem, relaxed):
    """Minimize squared distance to relaxed[n], never Hamiltonian energy.

    Ties retain the first state in integer enumeration order (bit 0 is LSB).
    """
    relaxed = problem.state(relaxed)
    if relaxed.shape != (problem.n,):
        raise ValueError("Repair requires one state")
    start = perf_counter()
    best, distance = None, np.inf
    for batch in feasible_batches(problem):
        if len(batch):
            values = np.sum((batch - relaxed) ** 2, axis=1)
            i = int(np.argmin(values))
            if values[i] < distance:
                best, distance = batch[i].copy(), float(values[i])
    return Result("nearest_feasible_repair", best, perf_counter() - start,
                  "repaired" if best is not None else "infeasible",
                  {"squared_distance": distance if best is not None else None})


def _independent_equalities(problem, tol=1e-10):
    """Return a scaled independent equality basis and an audit record."""
    E, e = problem.E, problem.e
    if not len(e):
        return E, e, {"original_rows": 0, "rank": 0, "selected_rows": []}
    norms = np.linalg.norm(E, axis=1)
    zero = norms <= tol
    if np.any(np.abs(e[zero]) > tol):
        return None, None, {"original_rows": len(e), "rank": 0,
                            "selected_rows": [], "consistent": False}
    candidates = np.flatnonzero(~zero)
    scaled_E = E[candidates] / norms[candidates, None]
    scaled_e = e[candidates] / norms[candidates]
    rank = int(np.linalg.matrix_rank(scaled_E, tol=tol))
    augmented_rank = int(np.linalg.matrix_rank(
        np.column_stack((scaled_E, scaled_e)), tol=tol))
    if augmented_rank != rank:
        return None, None, {"original_rows": len(e), "rank": rank,
                            "selected_rows": [], "consistent": False}
    if rank:
        _, _, pivots = qr(scaled_E.T, pivoting=True, mode="economic")
        chosen = np.sort(pivots[:rank])
        selected = candidates[chosen]
        basis_E, basis_e = scaled_E[chosen], scaled_e[chosen]
    else:
        selected = np.array([], dtype=int)
        basis_E, basis_e = np.empty((0, problem.n)), np.empty(0)
    return basis_E, basis_e, {"original_rows": len(e), "rank": rank,
                              "selected_rows": selected.tolist(), "consistent": True}


def slsqp_relaxation(problem, *, seed=0, restarts=8, maxiter=500):
    """Local SciPy control, not SNN. LP starts do not access binary oracle."""
    if restarts < 1 or maxiter < 1:
        raise ValueError("Positive restarts and maxiter required")
    start = perf_counter()
    rng = np.random.default_rng(seed)
    basis_E, basis_e, equality_audit = _independent_equalities(problem)
    if basis_E is None:
        return Result("slsqp_relaxation", None, perf_counter() - start,
                      "inconsistent_equalities", {"equality_audit": equality_audit})
    constraints = []
    if len(basis_e):
        constraints.append(LinearConstraint(basis_E, basis_e, basis_e))
    if len(problem.u):
        constraints.append(LinearConstraint(problem.U, -np.inf, problem.u))
    best, energy, attempts = None, np.inf, []
    for _ in range(restarts):
        initial = linprog(rng.normal(size=problem.n),
                          A_ub=problem.U if len(problem.u) else None,
                          b_ub=problem.u if len(problem.u) else None,
                          A_eq=basis_E if len(basis_e) else None,
                          b_eq=basis_e if len(basis_e) else None,
                          bounds=(0, 1), method="highs")
        if not initial.success:
            attempts.append({"stage": "initialization", "status": int(initial.status),
                             "message": initial.message})
            break
        result = minimize(problem.energy, initial.x, jac=problem.gradient,
                          method="SLSQP", bounds=[(0, 1)] * problem.n,
                          constraints=constraints, options={"maxiter": maxiter, "ftol": 1e-10})
        feasible = bool(np.isfinite(result.x).all() and problem.feasible(result.x))
        attempts.append({"stage": "solve", "success": bool(result.success),
                         "feasible": feasible, "message": result.message,
                         "iterations": int(result.nit)})
        if feasible and problem.energy(result.x) < energy:
            best, energy = result.x.copy(), float(problem.energy(result.x))
    return Result("slsqp_relaxation", best, perf_counter() - start,
                  "feasible_candidate" if best is not None else "no_feasible_candidate",
                  {"seed": seed, "restarts": restarts, "maxiter": maxiter, "attempts": attempts,
                   "equality_audit": equality_audit, "global_certificate": False})


def simulated_annealing(problem, *, seed=0, steps=2000, temperature=2.0,
                        final_temperature=0.01, initialization_attempts=10000,
                        max_flips=4):
    """Feasible-state SA with symmetric random proposals of up to four flips.

    No penalty objective or hidden oracle. Rejected infeasible moves are counted.
    This neighborhood need not connect an arbitrary feasible set.
    """
    if steps < 1 or initialization_attempts < 1 or max_flips < 1:
        raise ValueError("Positive step and initialization budgets required")
    if not np.isfinite([temperature, final_temperature]).all() or not (
            0 < final_temperature <= temperature):
        raise ValueError("Require finite 0 < final_temperature <= temperature")
    start = perf_counter()
    rng = np.random.default_rng(seed)
    effective_max_flips = min(max_flips, problem.n)
    x = None
    for attempt in range(initialization_attempts):
        candidate = rng.integers(0, 2, size=problem.n).astype(float)
        if problem.feasible(candidate, binary=True):
            x = candidate
            break
    if x is None:
        return Result("sa_feasible_moves", None, perf_counter() - start,
                      "initialization_failed", {"seed": seed, "attempts": initialization_attempts})
    energy = float(problem.energy(x))
    best, best_energy, rejected, accepted = x.copy(), energy, 0, 0
    for t in np.geomspace(temperature, final_temperature, steps):
        proposal = x.copy()
        bits = rng.choice(problem.n, size=rng.integers(1, effective_max_flips + 1), replace=False)
        proposal[bits] = 1 - proposal[bits]
        if not problem.feasible(proposal, binary=True):
            rejected += 1
            continue
        proposed_energy = float(problem.energy(proposal))
        delta = proposed_energy - energy
        if delta <= 0 or rng.random() < np.exp(-delta / t):
            x, energy = proposal, proposed_energy
            accepted += 1
            if energy < best_energy:
                best, best_energy = x.copy(), energy
    return Result("sa_feasible_moves", best, perf_counter() - start, "feasible_candidate",
                  {"seed": seed, "steps": steps, "temperature": temperature,
                   "final_temperature": final_temperature, "initialization_attempts": attempt + 1,
                   "max_flips": effective_max_flips, "infeasible_proposals": rejected,
                   "accepted_proposals": accepted})


def slot_simulated_annealing(problem, functionalized, *, seed=0, steps=10000,
                             temperature=2.0, final_temperature=0.01):
    """SA for ordered A/B slot pairs with exact B count; swap neighborhood."""
    if problem.n % 2 or not 0 <= functionalized <= problem.n // 2 or steps < 1:
        raise ValueError("Require paired slots, valid functionalized count and positive steps")
    if not (0 < final_temperature <= temperature):
        raise ValueError("Require 0 < final_temperature <= temperature")
    start = perf_counter()
    rng = np.random.default_rng(seed)
    slots = problem.n // 2
    b_slots = rng.choice(slots, functionalized, replace=False)
    x = np.zeros(problem.n)
    x[0::2] = 1
    x[2 * b_slots] = 0
    x[2 * b_slots + 1] = 1
    if not problem.feasible(x, binary=True):
        return Result("sa_slot_swaps", None, perf_counter() - start,
                      "initialization_failed", {"seed": seed})
    energy = float(problem.energy(x))
    best, best_energy, accepted, rejected = x.copy(), energy, 0, 0
    for t in np.geomspace(temperature, final_temperature, steps):
        chosen = np.flatnonzero(x[1::2] == 1)
        unchosen = np.flatnonzero(x[1::2] == 0)
        if not len(chosen) or not len(unchosen):
            break
        out_slot, in_slot = rng.choice(chosen), rng.choice(unchosen)
        proposal = x.copy()
        proposal[2 * out_slot:2 * out_slot + 2] = (1, 0)
        proposal[2 * in_slot:2 * in_slot + 2] = (0, 1)
        if not problem.feasible(proposal, binary=True):
            rejected += 1
            continue
        proposed_energy = float(problem.energy(proposal))
        delta = proposed_energy - energy
        if delta <= 0 or rng.random() < np.exp(-delta / t):
            x, energy, accepted = proposal, proposed_energy, accepted + 1
            if energy < best_energy:
                best, best_energy = x.copy(), energy
    return Result("sa_slot_swaps", best, perf_counter() - start, "feasible_candidate",
                  {"seed": seed, "steps": steps, "temperature": temperature,
                   "final_temperature": final_temperature,
                   "accepted_proposals": accepted, "infeasible_proposals": rejected,
                   "neighborhood": "exchange one B slot with one A slot"})
