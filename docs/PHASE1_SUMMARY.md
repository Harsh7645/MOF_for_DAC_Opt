# Phase 1 completion record

Completed 2026-09-10 for the synthetic-first scope required by the professor's
feedback. This closes the numerical formulation and parameter plumbing. It does
not close the later chemistry-validation program.

## Frozen v1 decisions

- Fixed template; the metal/node is fixed and eliminated from x.
- Two abstract linker options per slot, one-hot occupancy, exact functionalization
  count, explicit incompatibility rows and a redundant occupancy/charge audit.
  Vacancies, mixed metals, defects and protonation changes are excluded.
- `H=h@x+0.5*x@W@x`; symmetric zero-diagonal W; constraints stay explicit.
- Missing interactions are zero only when declared. Stage A values are dimensionless.
- Thresholding and repair are evaluated separately. Enumeration is limited to 20 bits.

## Executed evidence

`python -m pytest -q`: 16 passed. Coverage includes Hamiltonian/QUBO equivalence
on bits, fractional distinction, gradients, penalties, malformed data,
infeasibility, rounding/repair, determinism, equality rank/consistency, slot edge
cases, exact coefficient recovery and the sweep contract.

`python -m mof_dac.phase1 --output docs/phase1_results.json`: six deterministic
instances, 4–16 variables. Five feasible families include frustration, degeneracy
and a rounding counterexample; one is intentionally infeasible. Exact enumeration
found 2, 5, 20, 55 and 6 feasible states. Across 50 feasible SA runs, every run
returned a feasible state and 42 reached the exact optimum: 10/10, 10/10, 9/10,
3/10 and 10/10. The decline at the largest size is visible; no scaling conclusion is
supported. SLSQP returned a continuous feasible candidate for all feasible cases.

SLSQP now normalizes equality rows, checks augmented consistency and passes only an
independent basis to SciPy; final feasibility uses all original rows. SA permits up
to four-bit symmetric proposals so exact-composition slot swaps are reachable in
these cases; arbitrary feasible spaces may remain disconnected.

## Exit audit

| Criterion | Status | Evidence |
|---|---|---|
| Mathematical contract and constraints | PASS | `context.md`, formulation contract, 16 tests |
| Initial variable/material encoding | PASS for controlled v1 | Fixed-template abstract slots; chemical identities absent |
| Tractable diverse instances | PASS | `mof_dac/instances.py`, `phase1_results.json` |
| Parameter pipeline | PASS for Stage A; B/C designed | Exact recovery, rank rejection, `parameter_sourcing.md` |
| Literature/novelty comparison | PASS as scoped review | `phase1_literature.md`; novelty remains provisional |
| Real chemistry validity | OPEN external evidence gate | Licensed CIF, identities, conditions and DFT labels absent |

Phase 1 is complete as a synthetic-first computational phase. Phase 2 may proceed
on convex controls. Real-material claims remain blocked until Stages B/C and Phase 4.
