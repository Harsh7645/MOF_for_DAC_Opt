# Phase 2 completion — algorithm and SNN integration

Completed 2026-09-11 for the defined computational scope. Evidence is in
`phase2_results.json`; `tests/test_foundation.py` independently exercises the live
upstream package.

## Convex control and equality-band investigation

`snn-opt==0.6.0` solves the two-variable certified convex control at the exact
solution `[0, 1]`, energy `-2`. With exact equalities it reports
`converged_feasible` after 251 iterations; the original equality residual is
`1.11e-16`. A `1e-6` band also converges. The previous `1e-3` band returns the same
feasible solution but cannot pass the upstream KKT threshold because the band
itself contributes a residual of about `1e-3`. The production experiment now uses
an exact equality export (`equality_band=0`).

## Nonconvex experiment

The raw 50-variable Hessian is indefinite, so the Mancoo convex guarantee does
not apply. Five seeded raw runs reached the iteration limit and missed exact
equality by approximately `3.96e-6` to `5.20e-6`; all are recorded as
`returned_infeasible` under the project's `1e-7` tolerance. No raw-state energy gap
is reported as valid. The deterministic exact-count decoder returned feasible
binary states in 5/5 runs. On the enumerable toy, decoded states hit the optimum in
2/3 starts.

## Exit audit

- Pinned upstream solver and API metadata: PASS.
- Certified convex smoke test: PASS, now requiring upstream convergence.
- Raw nonconvex route with explicit theory boundary: PASS.
- Failure, KKT, residual and iteration diagnostics: PASS.
- Multiple starts and scalable constraint-aware decoding: PASS.
- 50-variable synthetic pilot: PASS.

Phase 2 is complete. Scaling and held-out quality belong to Phase 3. Neuromorphic
hardware speed or energy remains unmeasured and is not a Phase 2 software claim.
