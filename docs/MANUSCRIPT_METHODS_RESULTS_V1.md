# Separating Optimization Performance from Target Reliability in a Discrete MOF Design Workflow

Methods/results foundation, 27 October 2026. **Unreviewed draft, not a submission.**
Central results use synthetic objectives and sampled UMA targets. Cutoff-unconverged
DFT is confined to exploratory supplementary context. Independent final and
chemistry reviews are outstanding. Claim IDs refer to the [evidence ledger](../plans/phase3-methods-scope-v1/CLAIMS.md).

## Methods

### Separating the questions

We ask how discrete optimization, surrogate adequacy and adsorption-target
reliability should be assessed separately before an optimized design is
interpreted physically. The workflow distinguishes (i) optimization error on a
fixed numerical objective, (ii) approximation of saved target labels by that
objective, and (iii) sensitivity of the labels to sampling and relaxation.
These are separate diagnostics; we do not construct a common error budget or
infer quantitative dominance of one source over another.

Binary design variables are represented as a graph of linear coefficients and
candidate pair terms, with `H(x)=h^T x + (1/2)x^T W x`, symmetric W, explicit
linear constraints and separate binary/continuous feasibility checks. Synthetic
slot models include occupancy and exact functionalization constraints. The
UiO-66 case instead compiles the fixed node and six occupied linkers into its
template, leaving six substitution bits. A box-relaxed solution, its decoded
binary state and a certified discrete reference are distinct objects. Convex
SNN–QP guarantees are not extended to the indefinite experiments. [C1–C3]

### Fixed-objective solver comparisons

The frozen synthetic experiment uses 20 generator seeds (100–119) at each of
12, 20 and 50 binary variables. Gurobi 13.0.3 uses one thread and a 30-second cap;
enumeration independently checks the 12-/20-bit cases. SA uses exact-cardinality
slot swaps, seeds 0–2 and 250/1000/4000-step budgets. The SNN experiment uses
`snn-opt==0.6.0`, exact equality export, one deterministic start per instance and
a 2000-iteration cap. Raw constraint/integrality diagnostics are retained; a
deterministic exact-count decoder is evaluated separately. Runs are CPU software
experiments, with unequal budgets and numbers of starts, not a controlled
neuromorphic hardware, energy-consumption or speed comparison. [C1–C2; T1/F1]

The six-bit fitted-objective case is separate: enumerate all 64 states, compare
Gurobi (one run, 60-second cap, one thread), SA (10 seeds, 2000 steps), and SNN
(10 starts, 2000-iteration cap) with raw and 0.5-thresholded outputs retained.
Its objective is the training-derived pairwise approximation, not the observed
sampled target or a physical-energy oracle. [C3; T2]

### Ordered structural models and target construction

The parent and six-linker image map define 64 ordered substitution patterns.
For k substitutions the framework formula is C48H(28+k)NkO32Zr6. Four node
hydroxyls are retained; each chosen aromatic H is replaced by NH2 under the
recorded atom-index and initial-orientation rule. Neutral/closed-shell and
defect-free assumptions are explicit. Publication-CIF comparison supports
composition/cell consistency but not unique proton correspondence. These are
ideal computational models, not experimentally established materials or an
exhaustive isomer/rotamer library. See [structural record](STRUCTURAL_MODEL_RECORD_V1.md).
Its qualified chemistry assessment is pending. [C9]

For each pattern, the archived UMA-s-1p2p1/`odac` run provides four starts per
gas, flexible atomic relaxation at fixed cell, a 200-step cap and 0.05-eV/Angstrom
force tolerance. Same-model gas energies and the lowest accepted sampled empty
framework supply the common adsorption reference. The modeled score is
`y=min_s Eads(CO2,s)-min_s Eads(H2O,s)`, lower preferred. The shared bare
reference cancels in y, but each gas component is also inspected separately.
This is a sampled energetic difference, not capacity, humidity selectivity,
regeneration energy or equilibrium DAC performance. Exact model/checkpoint and
source hashes remain in the original reports. [C4,C7]

### Surrogate adequacy and development stability

The label-independent seed 41 split merges initial/relaxed duplicate groups and
retains 51 development patterns (42 groups) and 13 historical evaluation patterns
(11 groups). The 13 have already been inspected; they are not an untouched test.
The original OLS models use seven additive parameters or22 pairwise parameters
(intercept,six linear terms,15 pair products). Historical fits are preserved.

Exploratory analyses use only the 51 development designs: leave-one-group-out,
20 grouped five-fold repetitions and 1000 whole-group bootstrap draws under a
fixed protocol/seed. Duplicate groups stay intact; multiplicity is retained in
bootstrap fits. Rank-deficient fits are recorded, not repaired or retried.
Predicted rank stability is conditional on these labels and these51 designs.
No hyperparameter selection or additional model class was introduced. MAE,
RMSE, pattern/count residuals and identifiability are reported together. [C4–C6]

### Reliability diagnostics

The nested first-two versus all-four starts use a common four-start bare
reference and assess each gas and the paired difference. Nested changes and
site ranges are sensitivity diagnostics, not independent-replicate error bars.
The subsequent preregistered eight-design pilot uses 32 starts per gas in two
independent16-start batches, comparable targeted/random effort and retained
failures. Its frozen energy/ranking criteria are not revised after observing
the results. A separate matched diagnostic continues selected endpoints through
0.02/0.01/0.005 eV/Angstrom, includes original-pose replays and four rigid controls
on one tightly relaxed empty host. Controls and relaxation paths assess numerical
behavior, not a causal thermodynamic decomposition or diffusion kinetics. [C7–C8]

## Results

### Solver quality is a property of the specified objective and budget

Gurobi certified all 60 synthetic references; enumeration agreed on all 40 smaller
instances. At4000 SA steps, optimum hits were 60/60,59/60 and 55/60 at 12/20/50 bits.
Decoded SNN hits were 15/20,10/20 and 7/20. Raw SNN continuous feasibility was 3/20,
0/20 and 0/20; the same counts also satisfy integrality in these saved outputs.
Decoding yielded20/20 binary-feasible outputs at each size. No raw infeasible
energy is promoted to a valid binary gap. Unequal starts/budgets preclude a
general solver-dominance interpretation. [C1–C2; T1/F1]

All methods recovered the six-bit fitted objective's optimum at the declared
budgets: Gurobi 1/1, SA 10/10, raw SNN 10/10 and thresholded SNN 10/10. This verifies
agreement on that small numerical objective; it demonstrates neither SNN
superiority nor physical validity of its preferred design. [C3; T2]

### Pairwise flexibility does not give robust adequacy improvement

Historical development MAE decreases from 24.037 to17.125 meV with pair terms,
but historical evaluation MAE increases from 23.803 to30.175 meV. In development
grouped five-fold analysis, pairwise MAE is worse in 19/20 repetitions; median
MAE is 29.408 meV additive and 33.690 meV pairwise. The exception is retained:
leave-group-out RMSE is 41.042 meV additive versus 38.551 meV pairwise, even though
its MAE is 28.049 versus 29.508 meV. Repeated partitions are correlated;19/20 is
not an independent-trials p-value. [C4; T3/F2]

Residuals depend on substitution arrangement and amino count. Pairwise can help
some high-count patterns while worsening typical errors at counts 1–3. Counts 0/6
each contain a single pattern, making population extrapolation inappropriate.
Pattern 001011 accounts for a large historical error increase, but no outlier
was removed. This is descriptive attribution, not an identified chemical cause.
[C5; S1 and the original pattern CSV]

The full pairwise training matrix is identifiable (rank 22), but23/1000 group
bootstrap fits lose rank; the additive fits remain identifiable. Fourteen of 15
interaction ranges cross zero. Median bootstrap top 10 overlap with the fixed
development fit is 0.70 additive and 0.60 pairwise. These conditional ranges do not
establish chemical interactions or physical confidence. Additive is therefore
the descriptive reference; neither model is a physically validated predictor.
[C6; T4/F3/S2]

### Label reliability remains unresolved independently of optimization

Within the 51 development designs, two-to-four-start paired targets change by
15.123 meV mean absolute and 135.151 meV maximum absolute difference. Separate
CO2/H2O mean absolute changes are 7.072/8.559 meV. Cancellation can hide component
changes. No numerical ratio of these shifts to solver gaps is interpreted as
uncertainty dominance: the objectives, conditioning and units are distinct.
[C7; S3]

The larger pilot completed512 guest starts but only 1/8 patterns passed the full
frozen energy criterion. Batch rank correlation was 0.523810 versus required0.90;
top-two overlap was 50% versus 100%, with three decisive reversals. The no-go
decision remains. The 509 geometric clusters are not 509 proven physical minima.
[C7; T5/F4]

All48 matched component paths completed;44 met the initial5-meV last-checkpoint
criterion and four guest paths did not. The original start31 tighter endpoint
was reproduced closely, while selected water/CO2 continuations involved substantial
host and guest motion. Four original-pose replays ultimately agreed closely with
matched continuations, but those are matched numerical inputs, not independent
site discoveries. Shared-host rigid controls constrain host variation while
changing the coupled optimization problem; their differences cannot uniquely
separate host deformation from guest interactions. [C8; T6]

## Limitations, transferable procedure and supplementary boundary

The demonstrated contribution is an inspectable sequence: freeze the objective
and constraints; establish discrete references where feasible; separate raw
feasibility/decoding; test surrogate adequacy without group leakage; perturb
target construction and relaxation independently; retain failures; and gate
physical interpretation on structural/chemical and numerical evidence. This
procedure is transferable as an evaluation design. Transfer of the observed
performance numbers to other MOFs, solvers or chemical systems is not demonstrated.

The additional 15 fit parameters exhibit greater sensitivity, consistent with
estimation variability on limited targets. Sampling fluctuations, omitted
higher-order effects and motif/host changes are hypotheses for residuals, not
causally isolated mechanisms. No material ranking, general UMA accuracy or SNN
advantage is established. Independent final review and chemistry assessment
are prerequisites to Phase 3 closure under the revised scope.

Fourteen frozen baseline DFT single points may appear in a clearly labeled
supplement linked to [the existing baseline report](UIO66_QE75_BASELINE14_RESULTS_V1.md).
Their quantities are excluded from central quantitative conclusions because
cutoff/grid/k-point convergence is unresolved. Future confirmed criteria are in
[v3](FUTURE_CONVERGENCE_RULES_V3.md); higher-memory access is not a dependency of
this limited study. ODAC25 identity/reference/training work is a deferred
extension, with frozen selections and the unsent request preserved; no benchmark
scores are claimed.

## Citations and novelty work outstanding

Before submission, verify primary citations for the SNN solver/theorem scope,
QUBO conventions, UMA, the structural source and prior adsorption/surrogate
validation methods. Existing project literature is a starting point, not a
completed novelty audit. Do not call this the first framework or claim a new
physical mechanism, optimizer or generally superior surrogate. What has been
demonstrated here is the documented evaluation procedure and this case's outcomes.

Tables/figures and exact captions: [central evidence index](../plans/phase3-methods-scope-v1/EVIDENCE_INDEX.md).
Rebuild formatting only: `python -m scripts.build_phase3_methods_package --output local/phase3-methods-package-NEW`.
That command reads saved results and does not run any solver, fit or inference.
