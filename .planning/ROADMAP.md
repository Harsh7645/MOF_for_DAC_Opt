# Four-phase research roadmap

Status: Phases 1–2 computational scopes complete; Phase 3 active. Retain four phases. Relative 12-week schedule from report,
not a calendar commitment. Full source-derived mapping lives in `context.md`.

## Phase 1 - Formulation & Literature (weeks 1-3)

- [x] Read supplied report and professor feedback; archive sources with hashes.
- [x] Write project memory, agent instructions, beginner guide and chat state.
- [x] Initialize graph input, explicit constraints, QUBO/relaxation conventions.
- [x] Run synthetic loop and independent numerical checks.
- [x] Freeze controlled v1 slot semantics, multiplicities, topology and charge audit; real chemistry identities remain a later evidence gate.
- [x] Draft slot-based formulation alternatives, equations and worked example.
- [x] Complete scoped Lucas study and quantum/QUBO-MOF literature comparison.
- [x] Build an instance family beyond one fixture; include difficult/infeasible cases.
- [x] Validate Stage A parameter recovery and freeze Stage B/C sourcing contract.

Exit: PASS for the controlled synthetic scope. `docs/PHASE1_SUMMARY.md` records
evidence and the open real-chemistry gate; no material validity is claimed.

## Phase 2 - Algorithm & Integration (weeks 4-6)

- [x] Run pinned lab solver on a certified convex control.
- [x] Define an explicitly experimental nonconvex route preserving raw objective and constraints.
- [x] Add convergence/failure diagnostics, start sweeps and scalable slot decoding.
- [x] Pilot 50 variables on development-only synthetic instances.

Exit: PASS for integration. `docs/PHASE2_SUMMARY.md` records failed convergence,
strict-feasibility results and limits; no solver-performance claim is made.

## Phase 3 - Scaling & Benchmarking (weeks 7-9)

- [x] Execute frozen held-out synthetic instance sets; protocol is frozen.
- [x] Materialize paired CO2/H2O candidates. Authenticated execution produced
  285 exact single-gas targets and 138 paired validation MOFs with provenance.
- [x] Implement constraint-aware SA and Gurobi references with budgets/status/bounds.
- [ ] Execute UMA ODAC baseline, then integrate a CGCNN/MOFTransformer-family comparison on the same split.
- [x] Execute development and frozen held-out quality comparisons with seed distributions and honest timing limits.

Exit: reproducible comparisons across all three report baseline categories.

Continuation 2026-10-02: material scoring requires the reference audit in
`../docs/PHASE3_REFERENCE_AUDIT.md`. Provisional library:
`../docs/UIO66_PROVISIONAL_LIBRARY.md`. Actual structures, real h/J and grounded
solver results remain Phase 3 gates. Preserve the four-phase structure.

Milestone 2026-10-03: all 64 provisional UiO-66 bare structures were model-relaxed
on two T4 GPUs and audited locally (64 converged/contact-free/unchanged inferred
bonds). Initial declared-tolerance grouping and post-relaxation grouping were
executed. Bare preparation does not close the paired adsorption, real h/J,
chemistry review or material-baseline gates. See the provisional library document.

## Phase 4 - Analysis & Drafting (weeks 10-12)

- [ ] Validate reconstructed top candidates, structure identity and DAC conditions.
- [ ] Perform affordable independent top-K validation; document unsupported claims.
- [ ] Analyze parameter sensitivity, failures, constraint/repair and solver ablations.
- [ ] Produce figures, reproducibility bundle and manuscript.

Exit: defensible material claims and scientific narrative. Hardware energy benefit
is a deployment hypothesis unless directly measured.
