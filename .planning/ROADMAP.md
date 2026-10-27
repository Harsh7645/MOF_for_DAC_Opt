# Current four-phase roadmap - revised methods scope, 27 October 2026

Research question: **How should discrete optimization, surrogate adequacy and
adsorption-target reliability be assessed separately before interpreting an
optimized MOF design physically?**

[Scope/disposition record](../docs/RESEARCH_SCOPE_REVISION_20261027.md) supersedes
older completion gates below. The [original roadmap snapshot](ROADMAP_pre_scope_20261027.md)
is byte-preserved; a changed scope does not complete its deferred objectives.

|Phase|Current deliverable and status|
|---|---|
|1|Formulation/constraints/synthetic recovery: completed computational scope; physical validity separate.|
|2|SNN integration and convex control: completed integration; indefinite route remains heuristic.|
|3|Methods evidence, structural record and manuscript foundation locally prepared. **INCOMPLETE** until qualified chemistry assessment and independent final review are documented and blocking findings resolved.|
|4|Review integration, literature/novelty verification, final manuscript/supplement and archival reproducibility; publication requires author approval.|

Central evidence: synthetic solver budgets/feasibility, six-bit fitted objective,
additive/pairwise adequacy and development-only stability, sampling/relaxation sensitivity.
ODAC25 is a **deferred extension** (investigation paused; request unsent; no benchmark).
DFT baseline is exploratory supplementary evidence only. Higher-memory/refinement
access is **not** a limited-scope closure dependency; numerical convergence remains
unresolved. Four missing UMA host points, physical rankings and hardware studies
are deferred, not completed. No new compute or messages authorized.

[Closure checklist](../docs/PHASE3_CLOSURE_CHECKLIST_V1.md) |
[Methods/results draft](../docs/MANUSCRIPT_METHODS_RESULTS_V1.md) |
[Confirmed future convergence rules](../docs/FUTURE_CONVERGENCE_RULES_V3.md).

## Historical roadmap below - not current completion criteria

# Four-phase research roadmap

Reviewed **26 October 2026** against scientific records through **10 October**.
Phases 1–2 computational scopes are complete; **Phase 3 remains incomplete**.
The original relative 12-week schedule is historical, not a calendar commitment.

## Phase 1 — formulation and literature

- [x] Source-backed formulation, explicit constraints and binary/relaxed conventions.
- [x] Controlled synthetic instance family, exact checks and parameter-recovery study.
- [x] Scoped literature work and documented real-chemistry evidence gates.

Exit: PASS for the controlled computational scope. See
[Phase 1 summary](../docs/PHASE1_SUMMARY.md); chemistry validity remains separate.

## Phase 2 — algorithm integration

- [x] Pinned upstream SNN execution on a convex control.
- [x] Experimental nonconvex route, diagnostics and separate binary decoding.
- [x] Development-only 50-variable pilot and recorded feasibility/failure limits.

Exit: PASS for integration. See [Phase 2 summary](../docs/PHASE2_SUMMARY.md).
No SNN superiority or hardware-energy benefit has been established.

## Phase 3 — benchmarking and materials evidence

### Completed evidence

- [x] Frozen 60-instance synthetic SNN/SA/Gurobi comparison at 12/20/50 bits.
  Gurobi certified all optima; the CV's 92% is SA 55/60 at 4,000 steps on
  20 synthetic 50-bit instances with three solver seeds.
- [x] Curate 560,208 ODAC25 source rows into 285 single-gas targets and 138
  paired validation MOFs with source/frame/trajectory provenance.
- [x] UMA total-energy execution smoke on 16 structures; MAE 0.0236525 eV.
  This is not the 138-MOF adsorption-energy benchmark.
- [x] Separate provisional six-bit UiO-66 study: 64 relaxed bare structures,
  64 paired targets/512 starts, frozen 51/13 group split, 22-parameter fit and
  enumeration/Gurobi/SA/SNN comparison. Pairwise MAE 0.0301754 eV is worse
  than additive 0.0238031 eV; the inspected holdout is now development evidence.
- [x] Eight-design sampling pilot and matched-geometry diagnostics completed.
  The registered sampling-stability gate failed; no expansion/refit pass is implied.
- [x] All 14 frozen 80/600-Ry QE 7.5 baseline SCFs completed: seven complex
  snapshots plus seven stripped hosts. Portable review verified 471 payload
  hashes, 14 SCFs and 1,717 force vectors. These are not top-ten candidate checks.
- [x] Convergence v2.1 preparation, portable inputs and offline metric verifier.
  This checkbox records preparation only; no refinement calculation has run.

### Remaining gates

- [ ] Resolve ODAC25 training/reference compatibility and freeze non-overlapping
  training targets; preserve the 138-MOF validation pool.
- [ ] Evaluate constant/ridge, UMA adsorption and CGCNN or the reviewed report
  alternative on identical targets; save per-MOF predictions, errors, top-ten
  overlap, rank correlation, failures and measured cost.
- [ ] Confirm reconstructed convergence algebra and a suitable machine/build/
  allocation. Registered targets are 2.0 meV per energy-difference comparison
  and all-atom maximum force-vector change <=0.005 eV/Angstrom. Both successive
  refinements and eventual common refined protocol versus original baseline
  are required; a sensitivity pass is not an absolute error bound.
- [ ] Execute separately reviewed density/wavefunction-cutoff checks, with
  baseline reproduction if machine/build changes; assess electronic tolerance,
  k-points and transfer to hosts/CO2. Water-complex checks alone do not close these.
- [ ] Resolve chemistry/proton correspondence, four missing UMA host results,
  sampling stability and predictive value before accepting/refitting coefficients.
- [ ] Establish independently supported rankings and define top-K candidate checks.

Resume from [remaining work](../docs/REMAINING_WORK.md),
[current Phase 3 summary](../docs/PHASE3_STATUS.md),
[baseline results](../docs/UIO66_QE75_BASELINE14_RESULTS_V1.md) and
[convergence v2.1](../docs/UIO66_QE75_WATER_CONVERGENCE_V2.md).
No calculation, remote job or automatic refit is authorized by this roadmap.

## Phase 4 — analysis and drafting

- [ ] Independently check selected candidate structures and the declared target.
- [ ] Analyze coefficient/sampling sensitivity, constraints, decoding and solver ablations.
- [ ] Prepare reproducible figures, evidence retention and a scoped manuscript.

Exit: defensible claims supported by the accepted physical and computational scope.
DAC working capacity/selectivity and hardware benefit require their own evidence.

<details>
<summary>Historical roadmap through 5 October — superseded execution states</summary>

The following record preserves earlier plans, dates and evidence. Statements such
as “all14DFTresults absent” and “run is active” describe that historical stage;
the current roadmap above controls. Relative paths in this retained text are historical.

LATEST 2026-10-05: QE7.5 frozen DFT preparation revision2 SEALED; no SCF/UMA launched.
Read docs/UIO66_QE75_WATER_PILOT_V2.md. New inputs PBE-D3(BJ),threebody=false;
verified official SSSP1.3.0PBEPrecision5UPFs,metadata/archive/individualMD5+SHA256.
80/600Ry matches maximum recommendations;100/750refinement not proven converged.
Water complex522electrons/261bands;host514/257.31exact input roundtrips;
21canonical geometries and previous109filepackage/ZIP unchanged.91tests pass18.49s.
Original publication CIF now retrieved/hashverified:456atoms,114primitive;
composition/cell agree closely;unique atom/proton correspondence still unresolved.
New package artifacts/phase3/uio66_frozen_dft_v2_qe75/;140filehashes.
ZIP UIO66_Frozen_DFT_QE75_v2.zip SHA4ea11e147c529d8b893d2131c06812ec5978b24f0c7d8905c116c22e4e6d0554.
Receipt uio66_frozen_dft_v2_qe75_receipt.json pins hash-manifest too.
Linux/QE/MPI executable/build/allocation absent;32CPU/64GiB/100GiB,2serial4hjobs
REQUEST ONLY. Guarded launcher/tests prepared;realQE/parser integration untested.
Next obtain verified environment+allocation+review,then two complexSCFs only.
Four UMAhostSP missing separately;all14DFTresults absent. Phase3 incomplete.
No ionicrelaxation/refit/64expansion/ranking. ODAC25reference mismatch separate.
Older v1 unknownPP/threebody=true/noCIF notes below historical, superseded above.

LATEST 2026-10-05: frozen-geometry DFT diagnostic REVIEW PACKAGE prepared; NO new inference.
Read docs/UIO66_FROZEN_DFT_DIAGNOSTIC.md. User confirms no DFT code/PP/compute
confirmed; no VASP access assumed. Exact7complex checkpoints+7stripped hosts+
7optional extracted guests;21roundtrips;551historicalrawhashes verified.
Inspection:336ZrOcontacts,28nodeprotons,84carboxylates,25amino records,
periodic-contact/crowding CSVs,3consistent XY/XZ+Zr-displacement figures.
UMA7complex+3exacthost energies reusable;4mandatoryhostSP and7optionalguest missing.
All DFT values absent. Proposed2watercomplexpilot,14baseline total+10checks=24SP;
no ionicrelaxation/refit/expansion. Runtime/cost unknown until actualDFTpilot.
Packet artifacts/phase3/uio66_frozen_dft_v1_review/; ZIP UIO66_Frozen_DFT_Review_v1.zip
SHA572b56a936408bc06036a29becc69b02ca2064690ed024eeefacb9ddcbd14bca;109filehashes;76tests passed30.64s.
QE inputs deliberately UNVALIDATED templates with unknownPP/cutoffs.
Next: professor/institution code/version/PP/license/charge-spin/scheduler/resources;
validate backend/parser and return exact commands/allocation for review before launch.
Phase3 incomplete; failedpilot/thresholds/51-13fit intact;ODAC25 mismatch separate.
Older matchedV2 completion and earlier proposals below retained as historical.

LATEST 2026-10-05: matched diagnostic V2 COMPLETE, saved355186088;48/48paths.
Read docs/UIO66_MATCHED_DIAGNOSTIC_V2_RESULTS.md before further Phase3 work.
Actual2T4;20min27s incl setup; workersexit0;0activeevents. No retries/repair/extension.
Raw archive local: artifacts/phase3/uio66_matched_v2_results_20261005/;
SHA b448c23d138163d46e43c6f11877f93e8465edf5996e1ef3a49f26ffe013f153.
469output+74releasehashes verified; independent frozen assessment reproduced;
4runtime common-host mappings independently reconstructed.15safetytests pass.
44/48 last-energy targets pass;4guest paths fail <=0.005eV initial target.
Start31 historical0.02 reproduction within0.000110A/0.000000717eV;
all4 final replays within0.000510eV; rigid/flexible differences remain confounded.
Incomplete relaxation and configuration sensitivity supported; UMA accuracy untested.
NO further compute/refit/full64/DFT authorized. Return results for chemistry review;
Phase3 incomplete; ODAC25 reference mismatch separate. Prior ACTIVE/prepared-only
notes below are historical. Original failedpilot/thresholds/51-13split preserved.

2026-10-04 revision: matched diagnostic V2 uses one tightly relaxed empty110111 host for4rigid controls; preparation/test/package complete, execution not authorized. See docs/UIO66_MATCHED_DIAGNOSTIC_V2.md. Phase3 incomplete.

2026-10-04 milestone: offline matched-geometry analysis and diagnostic preregistration complete; execution requires review. Phase3 remains incomplete. See docs/UIO66_MATCHED_DIAGNOSTIC.md.

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

Current methods-focused case-study step: eight-design32-start-per-gas replacement
pilot executed and independently audited (512+16 accepted). Frozen stability
failed: NO-GO for expansion/refitting; chemistry/site/force review next.
See `../docs/UIO66_SAMPLING_PILOT_RESULTS.md`; no new compute authorized.
Historical51/13 results preserved; no untouched-final-test claim from those13.
ODAC25 reference/training/model-comparison gates stay separate and unresolved.

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

Paired design continuation: actual two-state UMA pilot audited (8/8 starts
accepted). Full 64-state/four-start run is active. Label-independent duplicate
split is frozen (51 train/13 test, rank 22). Fit/uncertainty/CPU solver scripts
are implemented but have not executed on the full model outputs. This separate
study preserves the frozen ODAC25 benchmark and does not close chemical validation.

Completed subsequently: 64 paired targets/512 starts audited, 51/13 train/test
fit and CPU SNN/SA/Gurobi execution. Pairwise held-out error exceeds additive;
two-vs-four-start top10 overlap .4. Provisional computational path is complete;
stable/independent material validation and required learned baselines remain open.

## Phase 4 - Analysis & Drafting (weeks 10-12)

- [ ] Validate reconstructed top candidates, structure identity and DAC conditions.
- [ ] Perform affordable independent top-K validation; document unsupported claims.
- [ ] Analyze parameter sensitivity, failures, constraint/repair and solver ablations.
- [ ] Produce figures, reproducibility bundle and manuscript.

Exit: defensible material claims and scientific narrative. Hardware energy benefit
is a deployment hypothesis unless directly measured.

</details>
