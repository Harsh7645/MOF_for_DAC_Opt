# Chat context and handoff

## Detailed remaining-work ledger (2026-09-14)

Created `docs/REMAINING_WORK.md` as the authoritative operational checklist for
unfinished Phase 3/4 work. It covers leakage-safe training data, composition and
UMA adsorption baselines, graph-model comparison, material ranking, the missing
assembled-structure-to-h/J bridge, independent validation, ablations, figures,
reproducibility and manuscript gates.

## Target-bearing extraction implementation (2026-09-13)

Added a bounded stdlib streaming extractor for the first validation
`mof_plus_adsorbate` database and a pure metadata profiler for corrected CO2/H2O
target availability, count consistency, repeated trajectories and pairable MOFs.
Added a separate Kaggle CPU notebook so this large archive scan does not consume
GPU quota. The code is locally tested; the target shard has not yet been observed,
and no pose/frame selection or paired ranking is claimed.

## Live ODAC25 Kaggle discovery (2026-09-12)

Authenticated `facebook/ODAC25` inventory succeeded at revision
`43f37d9592a35377380fd20832ddc2164ddb2492`; the gated repo had eight metadata
files and zero `.aselmdb` files. `DATASET.md` links external archives. Streamed
`val/gcmc/part_00000.aselmdb` (847,228,928 bytes) from the filtered validation
archive without retaining the 12 GB tarball. Schema inspection succeeded: 41,926
structures, periodic atoms, energy/force calculator results, but sampled
`energy_ads`, `energy_ads_corrected`, and bare-MOF energy fields were null. This is
an UMA execution smoke source, not paired target evidence. P100 failed because the
installed PyTorch 2.13 CUDA 13 build excludes `sm_60`. Notebook was switched to
T4x2 and Run All completed. UMA `uma-s-1p2p1`, task `odac`, processed 16
structures on one T4/CUDA. Against stored total energies, MAE was 0.0236525 eV,
RMSE 0.0248619 eV and maximum absolute error 0.0355138 eV. The Kaggle output
archive was downloaded and unpacked at
`artifacts/kaggle/odac25_uma_t4_smoke_2026-09-12/`. These are total-energy smoke
metrics, not paired CO2/H2O adsorption or material-ranking evidence.

## Kaggle execution handoff (2026-09-12)

Upload the project bundle to Kaggle as a private Dataset, not a Model.
`kaggle/ODAC25_UMA_Smoke.ipynb` provides secret retrieval, bundle discovery,
revision-pinned inventory, one-shard download, schema inspection, single-GPU UMA
smoke evaluation and non-secret artifact packaging. The corrected notebook
streams the first validation GCMC member from the official external archive. An
authenticated T4 smoke result now exists; target-bearing `mof_plus_adsorbate`
extraction remains the next data step.

## ODAC25/UMA access and target decision (2026-09-12)

User confirmed gated access to `facebook/ODAC25` and `facebook/UMA`, an HF read
token, paired CO2/H2O targets, and Kaggle P100 or T4x2 compute. Added paired
adsorption-energy construction/metrics, strict split-leakage checks, guarded HF
inventory/download/schema tools, a Kaggle pipeline and target/runbook documents.
Token remained in Kaggle Secrets and no credential was stored locally. The
authenticated execution evidence is recorded in the live-discovery section above.
Tests: 24 passed.

## Phase 2 closure and Phase 3 held-out benchmark (2026-09-11)

Corrected Phase 2 equality export from a `1e-3` band to exact equality. The live
convex SNN control now converges in 251 iterations with `1.11e-16` equality
residual; a sensitivity sweep explains the earlier nonconvergence. Five nonconvex
50-variable raw outputs remain infeasible at strict tolerance, while all decoded
states are feasible.

Executed frozen Phase 3 seeds 100–119 at 12, 20 and 50 bits. Gurobi certified
60/60 optima; exact enumeration agreed on all 40 <=20-bit instances. All 540 SA
runs and all 60 decoded SNN runs were feasible. Added dense synthetic generator,
per-budget statistics and strict external material-manifest validation. Tests:
23 passed. See `docs/PHASE2_SUMMARY.md`, `docs/PHASE3_STATUS.md` and result JSON.

No external dataset or surrogate has run. `docs/dataset_decision.md` recommends
ODAC25, but target definition and gated data/model access remain required.

## Phase 3 development benchmark (2026-09-10)

Installed Gurobi 13.0.3; local runtime reported restricted non-production license
expiring 2027-11-29. Added original constrained binary adapter and slot-swap SA.
On the 50-variable Phase 2 development instance, Gurobi certified -17.6968954,
SA hit it 20/20, and decoded SNN hit it 3/5; raw SNN remained infeasible/unconverged.
Phase 3 stays open: held-out execution and real surrogate screening are pending.

## Phase 2 integration completion (2026-09-10)

Installed and ran `snn-opt==0.6.0`. Added explicit convex and nonconvex APIs,
upstream/KKT/residual diagnostics, an O(n log n) fixed-slot decoder, a tiny exact
comparison and five-start 50-variable pilot. Tests: 18 passed. The convex control
returned the exact feasible state but upstream did not converge by its criterion.
All raw 50-variable states were infeasible at project tolerance and unconverged;
all separately decoded states were feasible. See `docs/PHASE2_SUMMARY.md`.

## Phase 1 completion (2026-09-10)

Controlled synthetic scope complete; see `docs/PHASE1_SUMMARY.md`. Added deterministic
slot families, exact parameter recovery/rank guard, equality-basis preprocessing,
four-bit SA proposals and scoped literature/parameter contracts. Verification:
16 tests passed; six-case sweep completed; 42/50 feasible SA runs hit exact energy
optima and all 50 returned feasible states. These are synthetic numerical results.
Active phase is 2; SNN has not yet executed. Graphify needs refresh after these edits.

## Model-switch checkpoint (2026-09-10)

User requests Sol continuation with efficient persistent context. Read
`MODEL_HANDOFF.md` for concrete pending work and research leads from the latest
session. Phase 1 is still incomplete; no new numerical implementation or tests
were completed during this handoff. Existing Graphify output predates these
handoff edits; read current memory files directly until the next semantic refresh.

## Phase 1 start and Graphify request (2026-09-10)

User authorized starting Phase 1 and explicitly requested the actual Graphify
knowledge graph for future token-efficient retrieval. Prior graph input was only
the optimization fixture; no Graphify artifact existed then.

New deliverable: `docs/phase1_formulation.md` proposes fixed-template slot choices,
compares alternatives, specifies occupancy/budget/charge constraints and provides
a worked numerical example. Assumptions remain proposed. Real chemistry, broader
synthetic instances and live SNN execution are still pending.

Knowledge-graph scope and usage: `docs/knowledge_graph.md`. Inspect generated
`graphify-out/BUILD_AUDIT.json` for actual successful build and coverage evidence;
do not infer success from this handoff alone. Current source code is unchanged.

## User request (2026-09-10)

Initialize research in `C:/Users/hp/Documents/GitHub/MOF_for_DAC_Opt`, already
open in Antigravity. Read supplied report and professor screenshots. Produce
`context.md`, `agent.md`, detailed CS-oriented `beginner_guide.md`, core Python
data/formulation/optimizer foundation and this persistent chat context. Keep
four provisional phases. Preferences: dense communication, graph-based data,
runnable core first, clean array-native code, minimal modules and RTK where useful.

## Completed

- Inspected empty Git repo; no existing project code to preserve.
- Extracted all four PDF pages and visually checked all page renderings; read
  both supplied screenshots. Local sources archived with SHA256 manifest.
- Created requested documents sequentially, then implementation. Added uppercase
  `AGENTS.md` entry point because `agent.md` alone is not universally discovered.
- Applied professor corrections: nonconvex caveat, explicit linear selection
  constraints, two-stage parameter sourcing, quality-first benchmark framing.
- Added mathematical refinements: eigenvalue check; binary-Q versus fractional
  objective distinction; rounding/repair separation; no sufficiency claim for
  chemical validity from linear rows alone.
- NumPy/SciPy graph loader and formulation, seeded feasible-move SA, multistart
  SLSQP local control, tiny exact reference and independent nearest-feasible
  decoding. JSON reports include residuals, timings, seed, environment and hash.
- Added convex-only optional SNN adapter and SNN array export. Reviewed upstream
  conventions at commit `f6623472204b2b5b7955c98e91024a391cf96fff`.
- GSD principle applied as four-phase roadmap/state plus a completed vertical
  numerical slice. No unrelated planner workflow or separate graph database added.

## Verification

- `python -m pytest -q`: 12 passed (initial run 8.77 s).
- `python -m mof_dac --output results/demo.json`: completed.
- Seed-0 demo SA, SLSQP, thresholding and distance repair all returned -4.6 with
  zero constraint violations. This is a synthetic smoke result only.
- Detailed environment and observed outputs: `docs/verification.md`. All local
  Markdown links checked and resolved.
- Toy exact reference: 64 states, 10 feasible, unique optimum -4.6 at
  `[1,0,1,1,0,0]` (M0, L0, L1). These are abstract synthetic choices.
- Tests verify graph-vs-matrix energy on every bit string, QUBO equality-penalty
  offset, finite-difference gradient, exact toy solution, malformed input,
  rounding failure, distance repair independence from energy, seed reproducibility,
  infeasibility reporting, SNN nonconvex rejection and enumeration ceiling.
- No SNN solve, Gurobi solve, surrogate inference, real parameter derivation,
  DFT validation or hardware measurement performed. Optional upstream integration
  has not been live-tested. Do not relabel the SciPy result as SNN.

## Constraints and deliberate limits

- Current problem: graph subset selection, not periodic crystal assembly.
- Demo and exact-distance repair limited to 20 variables; future 50-variable
  pilot requires another decoder and appropriate reference method.
- SA one/two-bit feasible moves can have disconnected neighborhoods; random
  feasible initialization can fail. This is a development baseline.
- All toy coefficients and charges are invented. Real type-versus-slot,
  stoichiometry, coordination, geometry and parameter calibration need decisions.
- No CPU superiority, physical validity, material recovery, global nonconvex
  guarantee or novel contribution asserted.
- Private PDF/screenshots are local and Git-ignored; their extracted text and
  summaries are tracked candidates. Results and raw data are ignored.
- No Git commit/push, IDE configuration change or professor message made.

## Next session

Read `agent.md`, `context.md` and `.planning/ROADMAP.md`. Start Phase 1 decisions:
actual slot/type representation, fixed multiplicities, linker budget and target
properties. Expand synthetic tests into instance families; finish Lucas and
QUBO-MOF comparison matrix. In parallel with those research tasks when authorized,
verify an upstream convex control before designing any nonconvex SNN experiment.

Progress state is in files, not guaranteed hidden cross-session memory. Update
this handoff after each meaningful session and retain the four-phase structure.

## Milestone 2026-09-14 — authenticated target profile and reduction gate

- Kaggle streamed `val/mof_plus_adsorbate/part_00000.aselmdb`: 8,418,258,944
  bytes, SHA-256 `2927f1ebb3af5fd4ea6e5d1072f9bdef549afa9e53ce3f0605955885da4b6c8c`.
- Full profile: 560,208 rows; 151 MOFs; 3,590 trajectories; 138 MOFs with both
  pure CO2/H2O records; 285 repeated MOF-gas groups; zero missing/null target
  fields or inconsistent adsorbate counts. Pure-gas categories may contain more
  than one molecule and are not yet the paired target table.
- Implemented deterministic materialization: exact one-molecule CO2/H2O only,
  maximum `fid` per trajectory, minimum final-frame `energy_ads_corrected` per
  MOF/gas, same split, with trajectory/fid/source-index provenance.
- Added `materialize-targets` CLI and updated the Kaggle target notebook to emit
  `paired_targets.json`. Local verification: 26 tests pass.
- Authenticated Kaggle materialization completed on all 560,208 rows: 285 exact
  single-gas targets formed 138 paired validation MOFs. The archive and
  trajectory/fid/source-index provenance are stored in
  `artifacts/kaggle/odac25_paired_targets_2026-09-14/`.
- Next: materialize training targets/features, then run frozen composition and UMA
  adsorption-energy baselines. No predicted material ranking or chemistry
  validation is claimed yet.

## Continuation 2026-10-02

- Reopened saved Kaggle draft. Prior eSEN had 68 CUDA OOM failures; full UMA
  material inference was not saved. Historical baseline outputs are preliminary
  because ColabFit lacks corrected labels/fid; no successful benchmark was invented.
- Fresh T4 session installed fairchem-core 2.23.0, torch 2.13.0 and
  fairchem-data-odac 0.1.0; restored bounded train/validation files.
- Audited 2,048 spaced validation rows. Gas reference identity uses `energy_old`,
  not corrected `energy`; observed constants -22.990396/-14.236396 eV and
  floating-point identity spreads below 3.3e-14 eV. Corrected/original total-energy
  conventions must be explicitly mapped. Bare minimum verification is active;
  an initial minimum-`energy_old` match failed and no model score was produced.
- Fixed notebook syntax, Spearman average ties/null for constant ranks, cached
  input hashes, frozen source-index checks and per-10-record progress evidence.
  Training pair provenance is retained. Full tests passed 34 before the latest
  bare-cache diagnostic; focused tests passed after it. Synthetic demo remains -4.6.
- User authorized a provisional UiO-66 library: six occupied BDC/NH2-BDC slots,
  64 nominal patterns, charge/stoichiometry audit and a 22-parameter identifiable
  quadratic basis. No symmetry-unique count, adsorption labels,
  reviewed chemistry or real h/J coefficients exist.
- Read docs/PHASE3_REFERENCE_AUDIT.md and docs/UIO66_PROVISIONAL_LIBRARY.md.
  Preserve ongoing Kaggle state and download evidence. Phase 3 remains incomplete.

### Provisional structural milestone

- Exported ODAC25 `jz4002345_si_002` bare index 184693, fid 7,
  C48H28O32Zr6. Literature ID resolves to UiO-66 study DOI 10.1021/jz4002345;
  exact original-CIF equality and full metal topology remain unverified.
- Periodic distance-inferred mapping identifies six C8H4O4 linkers and a
  Zr6O8H4 remainder. Generated 64 initial CIFs with deterministic planar NH2
  substitutions; no relaxation, adsorption calculation, symmetry deduplication
  or h/J was performed. Composition, severe-contact and CIF roundtrip checks pass.
- Original/corrected bare minima across all frames failed 145 references;
  final-frame minima failed 94. Direct all-frame energy lookup completed on
  189,504 rows: 67 distinct unresolved references, 5 matched, 62 unmatched.
  Downloaded both audit archives; no full-pool MLIP score accepted.
- Final tests: 36 passed in 14.17 seconds; synthetic demo -4.6. A third archive
  with direct frame-lookup evidence was downloaded and verified locally.
  Graphify AST/semantic/HTML refreshed; coverage, source hashes, graph integrity,
  directed imports and local links verified. Latest counts live in BUILD_AUDIT.
  The secret-free Kaggle bundle was rebuilt with the new code and frozen targets.

## Continuation 2026-10-03: provisional bare structures

- Implemented parent-operation typed periodic matching and initial tolerance
  audit: 64 groups at 1e-5 Angstrom; 53 at 0.01/0.05. After relaxation: 54 at
  0.01 and 53 at 0.05. These are approximate split-safety groups, not definitive
  symmetry-unique chemistry counts. Keep initial duplicates together.
- Installed local spglib 2.7.0. Implemented fixed-cell LBFGS relaxation, immediate
  per-candidate checkpoints, pinned checkpoint checksum, and connectivity-change
  diagnostics. Authentic UMA file was `checkpoints/uma-s-1p2p1.pt`; initial
  root-level path failed 404. Secret stayed in Kaggle Secrets/environment.
- Four-candidate pilot converged. Ran all 64 on two T4 GPUs: 64 converged in
  0–42 steps at fmax 0.05 eV/Angstrom; all contact-free below 0.7 Angstrom,
  all unchanged inferred typed bonds. Downloaded 7,790,932-byte raw archive
  with trajectories/logs/CIFs/executed sources. Local independent audit passed.
- Runtime pinned HF revision f611b917d9c68566bbbeccbb0aa0f7cad1696cb2,
  SHA-256 b2673b85037b075674c25f55c34ffe1ff1e15db924be977b10a184765df0d5ce;
  fairchem 2.23.0, torch 2.13.0, ASE 3.26.0, NumPy 2.0.2. Per-structure compute
  summed to 378.33 seconds, excluding startup/download and parallel wall-time.
- Full suite: 39 passed in 10.81s; demo -4.6, synthetic, no SNN in demo.
  Added reproducible Kaggle notebook, hash-verified structure bundle and local
  ODAC reference-question draft (not sent). Memory and Graphify refreshed.
- Phase 3 incomplete: bare energies are not adsorption h/J. Remaining gates:
  chemistry review, paired placement/reference/relaxation labels, coefficient
  validation and grounded solvers; ODAC reference identity/training-field mismatch,
  learned structure baseline and frozen material ranking. No Phase 4 promotion.
- Existing foundation is now tracked at commit 55d1e6d; this session made no
  commit or push. Preserve existing edits and the live Kaggle notebook.

## Continuation 2026-10-03: paired adsorption

- Froze `docs/UIO66_ADSORPTION_PROTOCOL.md` before the pilot: fixed-cell flexible
  host + one CO2/H2O, seeded SO(3) placements, fmax .05, 200 LBFGS steps,
  isolated same-model gas references, lowest accepted gas-removed empty-host
  reference across both gases. Incomplete pairs remain null.
- Actual two-state/two-start pilot passed: 8/8 accepted. Model delta for
  000000 = +.0296889057 eV; 111111 = +.0126993900 eV. UMA gas references
  CO2 -22.9974396449 / H2O -14.3828426083 eV, not ODAC25 DFT constants.
  Site ranges reach .36944 eV; no robust material-ranking claim.
- Downloaded 2,535,365-byte raw pilot archive with logs/trajs/CIFs/executed
  sources. Local audit recomputes energies/forces, contacts, connectivity and
  CIF/trajectory agreement. SHA binds the report; audited two complete pairs.
- Full 64-state/four-start run is ACTIVE on two T4 GPUs, four processes,
  one CPU thread each. Paths `/kaggle/working/uio66_ads_full/worker*/`.
  Do not reload/Run All/stop the live notebook. Save conflict backup downloaded;
  no draft-save success claimed. Main output must be downloaded and audited.
- Frozen `data/design/uio66_fit_split.json`: 53 merged duplicate groups,
  51 train/13 test, rank 22; inspected pilot groups train-only. Implemented
  full-pool hash/protocol gates, additive/pairwise OLS comparison, training-group
  bootstrap, nested 2-vs-4-start sensitivity, provisional coefficient graph and
  CPU SNN/SA/Gurobi comparison. No real full fit/solver results yet.
- Added reproducible `kaggle/uio66_adsorption.ipynb` (11 cells; code compiled)
  and small verified bare-CIF bundle. Tests: 44 passed in 15.57s, demo -4.6
  synthetic, no SNN in demo. No commit/push or external messages.
- Phase 3 remains incomplete: provisional UMA design is separate from frozen
  ODAC25 material validation, unresolved reference/training fields, required
  learned structure baseline, and independent chemistry/DFT validation.

### Full v1 design execution completed

- All64 paired targets and512 starts accepted; four worker exit codes0.
  Downloaded 133,472,188-byte main archive SHA256
  aee36cc47cda2b2088fc30c44f7fd240bad7e5731f71932a63018c4fc6bb1837.
  Remote/local trajectory-energy/force/contact/connectivity/CIF/source/input
  audits passed. No GPU job remains active. Draft-save conflict remains;
  no successful SaveVersion claimed. Browser proof saved main_results.png.
- Train-only actual fit: rank22, condition17.8487, bootstrap193/200 identifiable;
  pairwise testMAE/RMSE .0301754/.0413030 eV versus additive .0238031/.0275139.
  Pairwise is worse; no test-driven retuning/all-data refit.
- Nested2-vs4 site budget: mean/max delta change .0130766/.1351513 eV,
  Spearman .7260, top10 overlap .4, maxJ shift .0506196. Rankings not stable.
- Actual CPU enumeration/Gurobi optimum110111 (-.0474215 predicted,
  -.0436706 sampled). SA/raw SNN/thresholded SNN each10/10 fitted optimum hits.
  Sampled best111111 -.0879886 eV differs. Full-family top5 overlap .8 includes
  training, not a held-out score. Nonconvex spectrum -.086836/.135148, no PSD shift.
- Saved docs/uio66_design_results.json and provisional UMA-derived heuristic
  data/design/uio66_uma_train_fit_v1.json with per-coefficient conditional
  bootstrap and complete provenance. Phase3 overall incomplete; independent
  chemical/physics validation, stable sampling, ODAC25 reference/training,
  learned structure baseline and frozen material ranking remain open.
