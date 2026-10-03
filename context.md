# Project memory and research state

Updated: 2026-09-12. Status: Phases 1–2 and Phase 3 numerical track complete;
paired ODAC25/UMA material track ready for authenticated Kaggle execution.

## Evidence and precedence

Latest continuation: `.planning/STATE.md`, `docs/PHASE3_REFERENCE_AUDIT.md` and
`docs/UIO66_PROVISIONAL_LIBRARY.md` (2026-10-02) supersede historical execution
counts below. Phase 3 remains incomplete. Provisional library development is
authorized; 64 unrelaxed coordinate proposals now exist. Chemistry approval,
relaxation, symmetry deduplication, adsorption labels and real h/J are pending.

- [Scoping report](sources/scoping_report.pdf), four pages: original proposal, equations, baselines, 12-week timetable.
- Professor feedback: supplied Discord screenshots, message dated June 1, 2026, 10:32 PM in screenshot 2. Screenshot capture date September 10 is not the message date. [Feedback record](sources/professor_feedback.md).
- Later professor corrections supersede conflicting proposal claims. Implementation decisions below are explicitly additions, not quotations from the report.
- Lab repository: https://github.com/ahkhan03/SNN_opt . API review anchored to `f6623472204b2b5b7955c98e91024a391cf96fff`; PyPI `snn-opt==0.6.0` executed in Phase 2. See `docs/PHASE2_SUMMARY.md`.
- [Research sources and open literature work](docs/references.md).

## Research objective

Target: amine-functionalized zirconium MOFs, initially UiO-66 derivatives (report p.1). DAC means capturing CO2 from dilute ambient air; report uses 400 ppm as its design condition, not a current atmospheric measurement. Study whether SNN-QP dynamics recover good feasible building-block selections under an explicitly stated surrogate objective.

Two distinct questions: (1) Does the optimizer solve the specified numerical problem well? (2) Does that numerical objective predict useful, buildable, DAC-relevant structures? Synthetic success answers only the first, and does not establish material discovery or DAC performance.

## Mathematical contract

Report p.2:

\[
H(x)=\sum_i h_i x_i+\sum_{i<j}J_{ij}x_ix_j.
\]

Binary selection: `x in {0,1}^n`. Relaxation: `x in [0,1]^n`. Fractional solver states are numerical variables, not certified fractional compositions. Negative `h_i` rewards intrinsic affinity; positive `J_ij` penalizes co-selection; negative `J_ij` rewards compatibility. These are pseudo-energy terms until their units, normalization and calibration are established. The report's adsorption-enthalpy interpretation is a modeling proposal, not measured per-block ground truth.

Store an undirected interaction graph: building-block records are vertices; each unordered pair is stored once as an edge with `J`, method, source and units. This selection graph is distinct from the periodic atom/bond graph of an assembled MOF. An absent edge means an explicit modeled zero, not unknown chemistry; inputs must declare this policy.

Let `W[n,n]` be symmetric with zero diagonal and `W[i,j]=J_ij`. Let `h[n]` contain linear costs. Preserve the report's continuous polynomial:

\[
f(x)=h^T x+\tfrac12x^T W x,\quad \nabla f=h+Wx,\quad \nabla^2f=W.
\]

Binary symmetric QUBO export: `Q = diag(h) + W/2`, so `x.T @ Q @ x = H(x)` **only on binary x**. On fractional x, replacing `h_i*x_i` with `h_i*x_i^2` changes the relaxation. Never pass `2*Q` as the Hessian while claiming the original relaxation. Upper-triangular export would instead use full `J_ij` above the diagonal; never mix conventions.

### Explicit selection constraints (professor correction)

For a chosen metal-type set `M`, linker choices `L`, predefined multiplicities `s_i`, formal charge `q_i`, budget `B`, and target charge `q_target`:

\[
\sum_{i\in M}x_i=1,\qquad
L_{min}\leq\sum_{i\in L}s_i x_i\leq B,\qquad
\sum_i s_i q_i x_i=q_{target}.
\]

General representation: `A_eq x = b_eq`, `A_ub x <= b_ub`, plus box bounds. Hard incompatibility can use `x_i+x_j<=1`; soft positive costs alone do not forbid selection. Additional slot occupancy, topology, coordination and connectivity rules require an explicit assembly model. These constraints are necessary selection checks, not sufficient proof of a realizable periodic crystal.

Variable semantics must be frozen before real parameterization: presence of a type is different from choosing an occupant of a crystallographic slot. Binary presence cannot encode arbitrary counts. Real charge balance requires consistent cell multiplicities, protonation, node capping and defects. Demo uses abstract unit multiplicities and toy formal charges; it is not a UiO-66 unit cell.

Once constraints are retained explicitly this is a constrained binary quadratic problem, with a constrained continuous QP relaxation. Calling the complete constrained model a QUBO is shorthand only. Equality penalties `rho*||Ax-b||^2` can produce a binary QUBO export, with constant offset retained. Inequalities require a justified slack encoding to produce a true unconstrained QUBO; this foundation does not silently square their residuals.

### Convexity and solver claims

SNN-QP equivalence guarantees apply to the convex setting and relevant assumptions. For our nonconvex relaxation, SNN-QP is an experimental heuristic; global optimality, convergence, and even local-minimum attainment are not automatically guaranteed.

Mixed signs alone do not establish indefiniteness. Check eigenvalues of the symmetric Hessian. For this nonzero zero-diagonal `W`, zero trace plus a nonzero eigenvalue implies both positive and negative eigenvalues. Restrictions to an equality-feasible affine subspace may change relevant curvature; full-space indefiniteness is not itself a proof of nonconvexity on every constrained feasible set. Foundation reports full-space curvature conservatively.

Do not add a diagonal shift merely to make a PSD solver accept the instance: it changes the relaxation. Even a shift with binary linear compensation changes fractional behavior and must be a separately named experiment.

### Decoding

Report proposes thresholding. Required correction: evaluate raw thresholded feasibility, then repair separately if needed. Record relaxed state, rounded state, repaired state, each objective, residuals and repair time. Tiny-instance repair minimizes distance to the relaxed state over feasible binary states, with deterministic tie breaking; it does not optimize energy or use the exact energy oracle. It is exponential and restricted to `n<=20`.

## Four phases: original timetable with corrected gates

Weeks are relative effort estimates. No calendar start or final deadlines agreed.

| Phase | Report schedule and deliverables | Corrected work and exit gate |
|---|---|---|
| 1: Formulation & Literature | Weeks 1-3; library, h/J sourcing, explicit QUBO | Stage A: synthetic graph, constraints, exact tiny oracle, reproducible end-to-end loop. Stage B: independently validate chemistry parameter sources; no CoRE-as-pairwise-table assumption. Study Lucas, audit lab API, scout quantum/QUBO MOF work. Exit: agreed variable semantics, tested mapping, tractable instances, provenance, literature comparison. |
| 2: Algorithm & Integration | Weeks 4-6; QUBO-to-SNN mapping, roughly 50-variable pilot, hyperparameter calibration | Validate convex controls against lab solver first; decide and document a nonconvex experiment with professor. Preserve equalities, bounds, rounding/repair diagnostics; tune seeds/step sizes/budgets on development instances. Exit: pinned upstream integration, independent correctness checks and transparent nonconvex behavior. |
| 3: Scaling & Benchmarking | Weeks 7-9; full design space, low-energy candidates, SA/Gurobi comparisons | Freeze held-out instance families and candidate pool. Benchmark quality/feasibility first; SA, Gurobi, and report's primary competitive surrogate screening (MOFTransformer or CGCNN). Track exact bounds and gaps, seed distributions, cost of candidate generation and repair. Exit: reproducible tables with uncertainty and no test leakage. |
| 4: Analysis & Drafting | Weeks 10-12; chemistry validation, manuscript, efficiency/material insights | Validate reconstructed structures and DAC-relevant labels under explicit conditions; top-K expensive validation where feasible. Separate optimizer quality from chemistry validity; manuscript states limitations. Hardware energy advantage remains a hypothesis unless measured on target deployment. Exit: auditable results, sources, figures, manuscript and reproducibility bundle. |

## Baselines and evaluation

Report p.3 explicitly names **Simulated Annealing**, **Gurobi Optimizer**, and **surrogate-model-driven screening using MOFTransformer or CGCNN**, with top-K DFT validation. Preserve all three categories. Exhaustive enumeration and SciPy SLSQP are added development controls, not substitutions for the named baselines. MOFTransformer is a multimodal Transformer; the report groups it loosely with GNN potentials. Neither model is automatically a validated DAC predictor or interatomic potential.

Primary: feasible binary energy, feasibility rate, gap to certified small-instance optimum, optimum hit rate over seeds, known-good structure recovery on a fixed independent dataset. Secondary: end-to-end runtime and SA time-to-solution. Material screening: top-K recall/overlap and independently validated property quality using the same candidate pool, conditions and validation budget.

Define before publication: absolute energy gap `H-H*`, relative gap `(H-H*)/max(abs(H*), eps)` with declared epsilon/units; infeasible candidates receive no finite valid gap. Gurobi reference must include status, incumbent, bound, MIP gap and limits; only certified termination supports an exact label. Equal-energy degeneracy counts as success even if bit strings differ.

For target success probability 0.99 and empirical per-run success p, independent fixed-budget restart TTS estimate is `t_run*ceil(log(0.01)/log(1-p))`; p=1 gives one run, p=0 is not observed / unbounded estimate. Include confidence intervals and setup/repair costs. Current demo records runtime; it is not a TTS study.

## State and unresolved decisions

- Phase evidence and exact commands are recorded in [chat_context.md](chat_context.md) and `docs/verification.md`.
- The nonconvex SNN route remains an explicitly experimental heuristic. Gurobi,
  SA and decoded SNN held-out results exist for 60 synthetic instances.
- ODAC25 paired CO2/H2O atomistic adsorption energy is selected. The user has
  dataset/model access and Kaggle GPU; authenticated target reduction produced
  138 frozen validation pairs. Reference conventions and training-field mapping
  remain unresolved; see `docs/PHASE3_REFERENCE_AUDIT.md`.
- Real h/J data, chemically validated slot/stoichiometry encoding, surrogate
  training, DFT validation and hardware measurements remain future work.
- Select the actual block library, property labels/conditions, data licenses and compute allocation before the material-ranking track.
- User approved a provisional six-slot UiO-66 BDC/NH2-BDC library. All 64 bare
  structures completed pinned UMA fixed-cell relaxation and passed numerical
  diagnostics on 2026-10-03; chemical approval and paired adsorption h/J remain
  pending. See `docs/UIO66_PROVISIONAL_LIBRARY.md` and `.planning/STATE.md`.
- The scoped literature matrix found a provisional gap, not proof of novelty. Do not claim first-of-kind.
