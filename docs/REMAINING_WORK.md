# Project work tracker

Updated: **2026-10-05**. This section is the current status. Historical notes and
original detailed checklists are preserved in the collapsed section below.

**Phase 3 is not complete. DFT preparation is complete; DFT execution has not started.**
No additional DFT/UMA run, refit or design expansion is authorized by this tracker.

## What's left ? next steps in order

### 1. Enable the two-water-complex DFT pilot

- [ ] Obtain access to a Linux system with **Quantum ESPRESSO 7.5 / pw.x**.
- [ ] Verify executable path, version/build, executable SHA256 and MPI installation.
- [ ] Confirm the exact single-node MPI launch/binding command.
- [ ] Obtain an approved allocation and hard resource limits. Current request:
  **32 physical CPU cores, 64 GiB RAM, 100 GiB scratch; two sequential jobs,
  maximum four hours each**. This is not confirmed availability or a runtime estimate.
- [ ] Confirm persistent output/scratch locations and retention of failed/partial jobs.
- [ ] Complete the external environment configuration and run preflight checks.
- [ ] Review the verified environment and obtain execution approval before launching.

**No need to obtain new pseudopotentials or remake the frozen geometries:** both
are already prepared and verified. See [the exact environment handoff and commands](UIO66_QE75_WATER_PILOT_V2.md).

### 2. Run and assess only the approved pilot

- [ ] After approval, run the two frozen **110111 / H2O / start 28** complexes
  at the saved 0.010 and 0.005 eV/A checkpoints; no ionic relaxation.
- [ ] Retain and download inputs, outputs, errors, accounting and partial/restart files;
  verify hashes. Exclude incomplete or unconverged jobs from valid comparisons.
- [ ] Independently validate the parser against real QE output and inspect actual
  allocation, SCF behavior, elapsed time, memory and scratch use.
- [ ] Compare the DFT complex energy change with UMA's **-0.04146108 eV**.
- [ ] Inspect water, amino/linker and node-proton forces; report residual forces and
  numerical uncertainty separately from any physical interpretation.
- [ ] Return pilot results for review and price later DFT work from measured DFT cost.

### 3. Resolve the scientific questions before larger calculations

- [ ] Obtain professor/MOF-expert review of parent/proton correspondence, source-to-ODAC
  preprocessing, amino placement/rotamers and the neutral closed-shell assumption.
  Original publication CIF has been retrieved; unique atom/proton correspondence
  remains unresolved. Preserve all questionable geometries.
- [ ] If separately approved, run the remaining **12 baseline single points** to
  complete seven complexes plus seven exact stripped hosts, and the **10 planned
  cutoff/k-point/electronic checks**. The two pilot jobs count toward 14 baseline jobs.
- [ ] Assess numerical stability: initial targets **2-3 meV** for energy differences
  and **0.005-0.01 eV/A** for relevant force changes; these do not guarantee accuracy.
- [ ] Compare complex, stripped-host and guest-associated energy changes to distinguish
  framework deformation from guest-associated stabilization.
- [ ] Separately obtain approval for the **four missing UMA stripped-host single points**:
  H2O28/0.010; CO2 7/0.020 and 0.010; CO2 16/0.010. These do not block the initial DFT
  complex comparison. Seven optional extracted-guest calculations are not mandatory
  and remain outside the initial DFT scope.
- [ ] Decide with the professor whether the evidence supports the provisional case
  study or requires a revised diagnostic. No automatic expansion or refit.

### 4. Close remaining Phase 3 evidence gates

- [ ] Resolve the **ODAC25 energy-reference mismatch** as a separate workstream.
- [ ] Finish or explicitly revise the original material-prediction benchmark scope:
  leakage-safe training extraction, constant/composition baselines, a valid UMA
  adsorption baseline, and the report-required CGCNN/MOFTransformer comparison.
  Existing code/scaffolding and target tables do not establish completed benchmarks.
- [ ] Establish adequate physical/model validity and sampling stability before
  treating provisional h/J coefficients or material rankings as reliable.
- [ ] Assess pairwise versus additive predictive value; current historical holdout
  favors additive. Any new fit or larger sampling study needs a separate reviewed plan.
- [ ] If generalization claims remain in scope, preregister genuinely unseen data.
  Preserve the historical **51/13 split**; its 13 viewed designs are not untouched tests.
- [ ] Confirm the methods-focused paper's final scope and Phase 3 exit criteria with
  the professor. A narrower paper does not silently mark omitted science complete.

### 5. Phase 4 ? after the relevant Phase 3 decisions

- [ ] Complete justified sensitivity, solver/score ablation and statistical analyses.
- [ ] Perform independently reviewed validation for any retained material claims;
  top-K material validation is conditional on the final paper scope and budget.
- [ ] Regenerate figures/tables from retained raw evidence, including negative results,
  failures, feasibility, repair costs, uncertainty and measured compute.
- [ ] Verify a clean-environment reproduction bundle, licenses and secret-free files.
- [ ] Complete literature/citation checks, manuscript and claim audit; obtain professor
  review. Do not claim a material ranking, CPU/SNN advantage or hardware energy savings
  without supporting evidence.

## Completed ? do not repeat

- [x] Phase 1 formulation, explicit constraints and controlled numerical foundation.
- [x] Phase 2 solver integration and synthetic benchmark work within documented scope.
- [x] ODAC25 access/schema/target preparation and UMA execution groundwork; not a
  completed real-material predictive benchmark.
- [x] Provisional 64-design UiO-66 structures, four-start study, historical split,
  additive/pairwise fits and solver comparisons. Their limitations remain recorded.
- [x] Eight-design sampling pilot and force checks executed and independently audited.
  **Stability failed; the failure and original thresholds remain preserved.**
- [x] Matched diagnostic v2 executed: **48/48 paths** completed; evidence downloaded
  and independently assessed. This did not establish UMA's physical accuracy.
- [x] Seven exact complex checkpoints, seven stripped hosts and seven optional guest
  structures frozen; chemistry-inspection packet and provenance retained.
- [x] QE 7.5 input revision with PBE-D3(BJ), **three-body term disabled**.
- [x] Five proposed **SSSP 1.3.0 PBE Precision** potentials downloaded and checksum-verified;
  headers, valence electrons, semicore treatment and cutoff recommendations recorded.
- [x] Two water-complex inputs prepared: **522 electrons / 261 occupied bands** each.
  Starting **80/600 Ry**, refinement **100/750 Ry**; convergence is not yet demonstrated.
- [x] Guarded launcher, output/retention checks and convergence/analysis plan prepared.
- [x] Original publication CIF retrieved and checksum-verified; composition/cell
  comparison completed without modifying canonical coordinates.
- [x] **91 tests passed; 31 exact input round trips; 140 package hashes verified.**
  Actual Linux/QE/MPI integration remains untested.
- [x] Versioned package sealed; previous package/results preserved; project memory and
  Graphify updated.

Current deliverables:

- [QE75 v2 protocol and handoff](UIO66_QE75_WATER_PILOT_V2.md)
- [Sealed v2 package](../artifacts/phase3/UIO66_Frozen_DFT_QE75_v2.zip)
- [Package checksums](../artifacts/phase3/uio66_frozen_dft_v2_qe75_receipt.json)
- [Matched diagnostic results](UIO66_MATCHED_DIAGNOSTIC_V2_RESULTS.md)
- [Failed sampling pilot results](UIO66_SAMPLING_PILOT_RESULTS.md)

<details>
<summary>Historical updates and original detailed backlog ? may contain superseded pending/active states</summary>

The current checklist above takes precedence. Material-benchmark and Phase 4
items below retain their original detail, subject to the professor's final scope.
Older ?missing pseudopotentials?, ?CIF unavailable?, and ?pilot active? statements
are historical, not current blockers. No historical result or threshold is changed.

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

LATEST 2026-10-04: revised matched diagnostic V2 prepared for REVIEW; NOT launched.
Read docs/UIO66_MATCHED_DIAGNOSTIC_V2.md. V1 preparation/release/notebook preserved.
All4 rigid110111 controls now depend on ONE guest-free bare110111 seed relaxed
through0.02->0.01->0.005. Exact H* host and one shared host-energy single point;
Zr-indexed mean-MIC translation maps guests; no rotations/repairs/resampling.
Four seed mapping previews pass; FINAL tight host/mappings/energy remain pending
runtime prerequisite. Flexible paths unchanged. Host failure blocks4rigid paths;
independent work continues, scientific holds stop.48relaxations+1hostSP (was4).
ScheduleGPU0=25paths/GPU1=23; estimated step-cap queue~101.86min beforeoverhead.
2T4/2h cap unchanged: workers/setup stop115min, retain partial results.71tests
passed23.19s including deadline/archive test.74v2filehashes verified;64v1files,
v1ZIP/notebook,28source poses and historical51/13split/fit unchanged.
Bundle artifacts/phase3/UIO66_Matched_Diagnostic_v2.zip SHA256
027f634ce1545c5810f9e19535ef5dd190df6714999a5e28d5502d171b50c83a.
Manifest SHA33c3d63d407f0fa82e80f270a4159e0daa90ddfd8f80f26eb9a7023f102cde0a.
No model-energy claim yet; no GPU/DFT/refit/full64/material ranking. Notebook
kaggle/uio66_matched_diagnostic_v2.ipynb APPROVED=False. Revised package requires
review before execution; generic continuation is not permission to launch it.

LATEST 2026-10-04: matched-geometry diagnostic PREPARED; NOT GPU-authorized/launched.
Read docs/UIO66_MATCHED_DIAGNOSTIC.md (findings,156endpoint table,plots,protocol,commands).
Saved110111/CO2/start31: gradual0.073618eV decrease; O125 moves0.925020A,
N22 moves0.568565A; CO2 approaches O109-H15 (H...O126 2.860240->2.199495A),
L1 ring rotates11.053deg. No image-edge change in83frames; reproducibility untested.
Frozen16matched+4original replays+4rigid guest controls;24reference paths+4hostSP.
Thresholds0.02->0.01->0.005 retain LBFGS history. Proposed2T4/2h cap, review required.
Manifest536b883cb364a956422143adbec4a852994b993fb624fd831ab56c7b7b173cac.
Bundle artifacts/phase3/UIO66_Matched_Diagnostic_v1.zip (64hashedfiles,571482bytes),
SHAd632b4eb6a01ede3ed58ec14ef58120490475e4c898fe8d24717cc294238a285.
64tests passed25.87s;CPU28pose validation;notebook APPROVED=False;all3278historical
raw hashes and original51/13split/fit unchanged. Originalpilot stillFAILED/NO-GO.
No refit/full64/DFT/material ranking. Expert chemistry review and ODAC25 mismatch
remain separate unresolved work. Prior compute approvals do NOT authorize this new diagnostic.

LATEST 2026-10-04: approved replacement pilot COMPLETE and raw evidence LOCAL.
Private saved Version1 id354989784 finished69min41s;0activeGPUevents verified.
512/512 main guest starts and16/16 force continuations accepted,zero failures.
Frozen scientific assessment independently reproduced exactly on localCPU.
NO-GO for expansion: only1/8 energy-stable; batchSpearman0.523810 vs0.90;
top2overlap50%;3decisive reversals; near-tie boundary;0/4 force cases met
initial0.01eVtarget. No refit/full64/DFT or material ranking authorized.
Read docs/UIO66_SAMPLING_PILOT_RESULTS.md and its raw evidence pointers.
Archive115956555bytes SHAfff5aabd928c41c10cd11d0fe4472cd0d322a196fbcdf7ee424ff1838abdb374.
56tests passed; explicit hash-checked Linux/Windows report relocation added.
Prior lost interactive attempt stays separate/unverifiable. Historical51/13
split/fit unchanged;13viewed designs are development evidence. Chemistry/site
review and ODAC25 mismatch remain open. Phase3 incomplete.
Older ACTIVE/pending-approval/setup-only notes below are historical.

LATEST 2026-10-03T19:45:16.348503+00:00: private saved replacement Version1 ACTIVE, id354989784.
Actual2T4/74frozenfilehashes/512posegeometry/pinnedUMAcheckpoint PASSED;
controllerPID123 launched at saved-job elapsed217.8s. Draft remains OFF.
No completion/energy/ranking/raw-secured claim yet. Monitor ONLY existing
version logs; NEVER rerun/import/SaveVersion2 or start draft GPU session.
https://www.kaggle.com/code/sahuharsh/uio66-sampling-replacement-saved-pilot/log?scriptVersionId=354989784
Hard deadline23:49:17.689632UTC2026-10-03 (05:19IST2026-10-04),never extend.
After terminal state download saved evidence ZIP and executed notebook,
hash-verify and independently audit frozen sampling/force criteria before
showing results. Absolute Linux report-path keys in force provenance may
require an explicit hash-checked relocation mapping for local re-audit;
never alter original reports/criteria or silently rewrite path identities.
Prior lost attempt separate/unverifiable. No full64/DFT/refit or ranking claim.
Earlier setup-only/pending-approval/oldACTIVE notes historical.

LATEST 2026-10-03T19:40:52.859774+00:00: approved saved replacement Version1 ACTIVE, scriptVersionId354989784.
Private Save & Run All verified; interactive draft remains OFF. Runtime bundle
74hashes and actual2T4/15360MiB each verified in saved logs; setup underway.
No guest completion or stability results claimed. Never rerun/createVersion2.
Monitor existing logs: https://www.kaggle.com/code/sahuharsh/uio66-sampling-replacement-saved-pilot/log?scriptVersionId=354989784
Frozen replacement deadline23:49:17.689632UTC2026-10-03 (05:19ISTnextday),
unchanged. Retain/download/hash outputs and assess frozen criteria afterward.
Prior lost interactive attempt stays separate/unverifiable. No64/DFT/refit.
Older pending-approval/NOT-launched/oldACTIVE notes historical.

LATEST 2026-10-04 IST: user explicitly approved ONE saved-batch replacement.
Prior interactive attempt remains unverifiable; no surviving raw pilot results.
New frozen release: uio66_sampling_saved_approved_20261003T193717Z;74 file hashes verified.
Bundle SHA256 a0afe73fccbccae5b59dfb53e8005f1f0381d973ca7da6789100c66679823ddc.
Conservative new budget start19:37:17.689632UTC2026-10-03; deadline
23:49:17.689632UTC (05:19:17IST2026-10-04). Never extend this receipt.
Private Save Version / Save & Run All preparation in notebookc35b611f07;
NOT launched yet. Runtime2T4/512poses/checkpoint must pass before inference.
Same512guest+16force scope; no refit/full64/DFT. Older pending-approval/ACTIVE
notes below historical. Read docs/UIO66_SAMPLING_EXECUTION.md for updates.

# Remaining work to complete the MOF-for-DAC optimization project

Updated: 2026-10-03

Newest methods-focused continuation:
[eight-design sampling pilot](UIO66_SAMPLING_PILOT_V2.md) and
[chemistry/DFT review draft](UIO66_CHEMISTRY_REVIEW.md). This does not close the
material-validation or ODAC25 gates below.

- [x] Audit all64 structures and512 archived starts, including periodic images,
  node H, six-linker/node bridges, amino geometry, placement/reference/source hashes.
- [x] Freeze eight patterns and512 initial poses,32/gas/state, independent batches
  and equal site-class quotas; implement dry/GPU/representative force runners.
- [x] Implement batch stability/minima/failure and tighter-force accounting audits.
- [x] CPU geometry checks and synthetic integration tests;50 full-suite tests pass.
- [x] Estimate archived-run cost; prepare small bundle/notebook and review commands.
- [x] Approved replacement512-guest pilot executed, downloaded and independently audited; stability failed.
- [x] Execute/audit16 representative0.02 force continuations; all accepted,0/4 initial convergence targets met.
- [x] Assess frozen0.01eV target, ties, basins and failures; NO-GO.
- [ ] Expert review of failed convergence and separately preregistered follow-up scope/budget.
- [ ] Expert approval of parent/node hydrogens, regioisomers, rotamers and site scope.
- [ ] Independent physical validation after resources/settings review; no DFT launched.
- [ ] New unseen-cohort preregistration for final generalization claims. Preserve
  historical51/13 records; their13 previously viewed labels are not untouched tests.

No full64x32x2 expansion, dataset-author contact or paper/performance claim made.

Current evidence: [PHASE3_REFERENCE_AUDIT.md](PHASE3_REFERENCE_AUDIT.md).
Composition baseline code, leakage checks, inference scaffolding and packaging
are implemented; strict training extraction and valid full-pool model results
remain incomplete. User authorized a
[provisional UiO-66 library](UIO66_PROVISIONAL_LIBRARY.md): 64 nominal patterns,
with 64 coordinate proposals from an authenticated ODAC25 parent. All 64 now
converged in fixed-cell UMA bare relaxation; saved trajectories and CIFs passed
the independent audit. Initial parent-operation grouping found 53 groups at
0.01/0.05 Angstrom; relaxed grouping found 54/53 respectively. These are
declared-tolerance diagnostics. Real adsorption coefficients, complete symmetry
review and chemical validation remain absent.
This does not close P3.6. Checkboxes
below represent complete evidence gates, not code existence.

Paired-design milestone: protocol and two-state pilot are complete; all eight
starts passed and two model-derived paired targets were audited locally. The
64-state/four-start experiment subsequently completed: 64 pairs and 512 accepted
starts audited locally. Actual training-only fit, conditional uncertainty and
CPU solvers executed. Frozen split: 51 train/13 test, 53 groups, rank22.
Pairwise test MAE .0301754 eV exceeds additive .0238031 eV; two-vs-four-start
top10 overlap .4. Sampling stability and independent validity remain open.
See [UIO66_ADSORPTION_PROTOCOL.md](UIO66_ADSORPTION_PROTOCOL.md).

This is the operational completion checklist for the research project. It starts
from the verified repository state: Phases 1 and 2 are complete for their
controlled computational scopes; the Phase 3 synthetic benchmark and the frozen
138-MOF ODAC25 validation target table are complete. Phase 3 model comparison,
the chemistry-grounded optimization loop, and Phase 4 remain.

## Completion definition

The project is complete only when all four statements are supported by saved,
reproducible evidence:

1. The constrained SNN method is compared fairly with SA and Gurobi on the same
   numerical objectives and constraints.
2. A model predicts the frozen paired CO2/H2O adsorption-energy target on unseen
   assembled MOFs without train/validation leakage.
3. Physical predictions are converted into auditable building-block `h_i` and
   `J_ij` coefficients, and the optimizer is run on that grounded objective.
4. Top configurations receive independent chemistry validation under declared
   DAC-relevant conditions, with limitations reported in the manuscript.

Passing only the numerical benchmark does not demonstrate useful MOF discovery.
Passing only the ODAC25 prediction benchmark does not demonstrate that the QUBO
representation can generate valid or synthesizable frameworks.

## Already complete — do not repeat

- [x] Source report and professor feedback extracted, archived and hashed.
- [x] Binary Hamiltonian, continuous relaxation and symmetric QUBO conventions.
- [x] Explicit occupancy, budget, charge and incompatibility constraints.
- [x] Synthetic parameter-recovery tests and controlled slot instance family.
- [x] Live `snn-opt==0.6.0` integration, convex control and nonconvex diagnostics.
- [x] Scalable exact-count decoder and 50-variable synthetic pilot.
- [x] Frozen 60-instance synthetic benchmark at 12, 20 and 50 bits.
- [x] Gurobi, constraint-aware SA and decoded-SNN numerical comparisons.
- [x] Authenticated ODAC25 inventory, schema inspection and T4 UMA smoke test.
- [x] Frozen ODAC25 exact-single-molecule reduction rule.
- [x] Authenticated validation materialization: 285 single-gas targets forming
  138 paired CO2/H2O MOFs with trajectory/frame/source-index provenance.

Authoritative completed evidence is in `PHASE1_SUMMARY.md`, `PHASE2_SUMMARY.md`,
`PHASE3_STATUS.md`, `phase3_results.json`, and
`../artifacts/kaggle/odac25_paired_targets_2026-09-14/`.

## Phase 3 — finish material prediction and ranking

### P3.1 Build a leakage-safe training set

Current state: the validation table is frozen. A matching training table does not
yet exist. Validation labels must not be used to select features, fit statistics,
tune hyperparameters or choose checkpoints.

- [ ] Inventory the filtered ODAC25 training archive without downloading the
  complete 555 GB archive.
- [ ] Define a bounded, shard-based extraction plan that fits Kaggle disk and
  session limits. Record archive URL/revision, member path, byte count and SHA-256.
- [ ] Apply the exact same v1 rule used for validation:
  - exact one-molecule CO2 or H2O records;
  - largest `fid` per relaxation trajectory;
  - lowest final-frame `energy_ads_corrected` per MOF/gas;
  - pair only identical `mof_name` and split.
- [ ] Save training single-gas and paired tables with source-index, trajectory and
  frame provenance.
- [ ] Verify finite targets, unique `(MOF, gas)` keys, consistent adsorbate counts,
  and zero MOF identity overlap between the chosen train and validation partitions.
- [ ] Record target distributions and coverage by MOF type. Do not alter the
  validation filter to increase sample count.
- [ ] Freeze all resulting manifests and hashes before model development.

Deliverables:

- `artifacts/kaggle/odac25_train_targets_<date>/paired_targets.json`
- `training_target_profile.json`, `evidence_manifest.json` and a run README
- a checked-in secret-free Kaggle notebook or script that recreates the artifacts

Exit criteria: the training table is reproducible, its provenance is complete,
and automated checks prove the official split boundary is preserved.

### P3.2 Establish simple training-only baselines

Purpose: complex models must outperform transparent low-cost predictors.

- [ ] Define structure-derived inputs available for train and validation records.
  Start with atom counts/composition and simple size features.
- [ ] Exclude adsorbate atoms from parent-MOF composition features, or represent
  them explicitly and consistently.
- [ ] Fit a constant predictor using training-set CO2/H2O means.
- [ ] Fit a small regularized linear or ridge composition model. Choose
  regularization using training-only cross-validation grouped by MOF identity.
- [ ] Freeze preprocessing, feature ordering, coefficients and training seeds.
- [ ] Evaluate once on the 138 frozen validation pairs.
- [ ] Report CO2 MAE/RMSE, H2O MAE/RMSE, delta MAE and delta top-10 overlap.
- [ ] Save per-MOF predictions so every aggregate can be recomputed.

Deliverables:

- `mof_dac/material_baselines.py` and focused tests
- `scripts/run_material_baselines.py`
- `artifacts/phase3/material_baselines.json`
- feature schema, split manifest and environment record

Exit criteria: deterministic reruns reproduce the same per-MOF predictions and no
validation statistic enters training or model selection.

### P3.3 Run a valid UMA adsorption-energy baseline

The existing UMA result is only a total-energy execution smoke test. It is not an
adsorption-energy baseline.

- [ ] Construct matched calculation triplets for every evaluated record:
  adsorbed MOF, corresponding bare MOF, and isolated CO2 or H2O reference.
- [ ] Verify atom identity, charge/spin assumptions, cell convention, correction
  convention and `task_name="odac"` compatibility for all three calculations.
- [ ] Define how ODAC25's re-relaxed bare-MOF correction maps to the UMA
  calculation. Reject subtraction that silently mixes incompatible DFT and UMA
  reference energies.
- [ ] Predict all component total energies with one pinned UMA checkpoint/version.
- [ ] Compute predicted adsorption energy using `ODAC25_TARGET_CONTRACT.md`.
- [ ] Run a small audit sample first, then the frozen candidate pool on a Kaggle
  T4. The current Kaggle/PyTorch build cannot run UMA on P100.
- [ ] Save per-component energies, failures, inference time, GPU, package versions,
  checkpoint identity and hashes.
- [ ] Evaluate the same paired metrics and top-10 definition used by the simple
  baselines. Failed structures remain in the reported denominator.

Deliverables:

- matched-triplet manifest and validation report
- secret-free Kaggle UMA adsorption notebook
- `uma_adsorption_predictions.json` and `uma_adsorption_metrics.json`

Exit criteria: each reported adsorption prediction can be reconstructed from
three compatible saved component calculations. No total-energy smoke metric is
presented as adsorption accuracy.

### P3.4 Add the report-required graph/Transformer comparison

The scoping report requires surrogate screening using MOFTransformer or CGCNN.
One compatible model is sufficient; both are optional.

- [ ] Audit current official implementations/checkpoints against the frozen target,
  structure format, license and Python/CUDA environment.
- [ ] Select MOFTransformer, CGCNN or a documented equivalent only after confirming
  it can consume the assembled structures and predict the paired energy target.
- [ ] Convert structures using a deterministic, versioned preprocessing pipeline.
- [ ] Train on training data only. Use grouped folds within the training partition
  for architecture and hyperparameter decisions.
- [ ] Freeze the checkpoint before evaluating the 138-MOF validation table.
- [ ] Record seeds, learning curves, checkpoint hash, parameter count, training
  time, inference time, GPU and failures.
- [ ] Report the same metrics and candidate pool used for other baselines.
- [ ] If neither named model is target-compatible, document the incompatibility
  and use a current DAC-specific graph model without calling it the named baseline.

Deliverables:

- model decision and license/provenance records
- training/evaluation configuration and checkpoint hash
- per-MOF predictions and comparison metrics

Exit criteria: at least one learned assembled-structure baseline has a reproducible,
leakage-safe score on the frozen validation set.

### P3.5 Produce the material-ranking benchmark

- [ ] Freeze the candidate pool at the 138 authenticated validation MOFs unless a
  documented data-quality failure requires exclusion.
- [ ] Use `delta = E_ads(CO2) - E_ads(H2O)` only as the declared competition
  diagnostic. Do not call it working capacity, selectivity or 400 ppm performance.
- [ ] Freeze `K=10` before viewing model ranking outcomes.
- [ ] Compare constant, composition, UMA and graph-model predictions using the
  identical target rows and metrics.
- [ ] Report per-gas errors, delta error, top-10 overlap, rank correlation,
  confidence intervals where supported, failure counts and measured cost.
- [ ] Produce a top-candidate table with structure IDs and provenance, labeled as
  model ranking pending independent validation.
- [ ] Document error cases, model disagreement and out-of-distribution structures.

Deliverables:

- `docs/phase3_material_results.json`
- `docs/PHASE3_MATERIAL_SUMMARY.md`
- comparison table and publication-quality error/ranking figures

Exit criteria: all model categories are compared on one frozen pool and Phase 3's
material claims are limited to held-out adsorption-energy ranking quality.

### P3.6 Ground the QUBO coefficients in real material evidence

This is the missing bridge between assembled-MOF prediction and the project's
building-block optimizer.

- [ ] Freeze a real design family: zirconium node, UiO-66 topology/template and a
  finite set of amine/linker substitutions.
- [x] Define provisional six-bit variables precisely: one BDC/NH2-BDC choice
  at each occupied mapped slot. Chemistry approval remains separate.
- [ ] Fix unit-cell multiplicities, protonation, node capping, defects, formal
  charges, linker budget and allowed substitutions with chemistry review.
- [x] Build provenance-bearing provisional assembled structures for all 64
  configurations; retain input hashes, atom mapping and final relaxed CIFs.
- [ ] Validate structure identity, coordination, periodic connectivity and charge
  before any energy calculation.
- [ ] Score assembled configurations with the selected physical model and a
  consistent target/condition.
- [x] Freeze provisional UMA sampling/reference protocol and audit the two-state pilot.
- [x] Freeze label-independent duplicate-group train/test split (51/13; rank 22).
- [x] Download/audit all 64 four-start paired targets; keep rejected/failed samples null.
- [x] Compare nested two/four-start budgets; measured instability, not a passed stability gate.
- [x] Fit provisional UMA-only h/J and report held-out additive comparison, rank/condition,
  per-coefficient conditional bootstrap uncertainty and input/source hashes.
- [x] Run actual CPU enumeration/Gurobi/SA/SNN on that provisional fitted objective.
- [ ] Stabilize sampled targets/rankings with a separately named uniform sampling study.
- [ ] Assess whether pairwise coefficients add predictive value; current holdout favors additive.
- [ ] Fit `H(x) = sum(h_i*x_i) + sum(J_ij*x_i*x_j)` using an identifiable design
  matrix.
- [ ] Record units, normalization, uncertainty, regularization and rank/condition
  diagnostics. Compare additive-only and pairwise models on held-out structures.
- [ ] Reject unsupported coefficients; never fill missing chemistry with silent
  zeros. Distinguish a modeled zero from an unknown interaction.
- [ ] Freeze a grounded interaction graph and rerun SNN, SA and Gurobi on the
  identical constrained objective.
- [ ] Test whether low-H configurations have improved held-out physical labels.

Deliverables:

- approved building-block/slot library and structure manifest
- real-coefficient graph with source, method, units and uncertainty per value
- parameter-fit diagnostics and held-out prediction report
- grounded SNN/SA/Gurobi artifacts and ranked configurations

Exit criteria: at least one auditable end-to-end path exists from real assembled
structures to `h/J`, constrained optimization, reconstructed candidates and
held-out physical scores.

## Phase 4 — validate, analyze and write

### P4.1 Reconstruct and validate top configurations

- [ ] Convert each selected bit vector into an explicit periodic structure.
- [ ] Confirm slot occupancy, atom counts, bonding/coordination, periodic images,
  charge/protonation, duplicate identity and parent-template consistency.
- [ ] Reject invalid structures before property evaluation and report the invalid
  fraction instead of silently removing it.
- [ ] Record deterministic reconstruction code and structure hashes.

Exit criteria: every top candidate maps to one reviewable structure, or is marked
invalid with a specific reason.

### P4.2 Perform affordable independent top-K validation

- [ ] Agree with the professor on the validation method and budget: DFT, a trusted
  higher-fidelity calculation, or an external independently labeled source.
- [ ] Freeze protocol, candidate count and selection rule before expensive runs.
- [ ] Declare temperature, pressure, gas composition, humidity and regeneration
  assumptions for any DAC/process claim.
- [ ] Validate the same top-K budget for competing methods where feasible.
- [ ] Save inputs, convergence status, outputs, failures, versions and compute cost.
- [ ] Compare predicted and independent ordering, uncertainty and failure modes.

Exit criteria: the strongest material claims have evidence independent of the
model used to select candidates.

### P4.3 Run sensitivity and ablation studies

- [ ] Vary `h/J` uncertainty, scaling and sparsification.
- [ ] Vary hard-constraint bounds, charge assumptions and block library.
- [ ] Compare raw SNN output, thresholding and distance repair separately.
- [ ] Ablate pairwise `J` terms against an additive-only model.
- [ ] Measure stability across SNN/SA seeds and budgets.
- [ ] Analyze results versus problem size, density, curvature and constraint
  tightness.
- [ ] Keep negative and nonconverged results in denominators.

Exit criteria: conclusions remain supported under reasonable modeling choices, or
their sensitivity is explicitly bounded.

### P4.4 Evaluate neuromorphic deployment claims honestly

- [ ] Keep CPU wall-clock results as descriptive software measurements.
- [ ] Define a target SNN hardware platform and measurement protocol if an energy
  or speed claim is retained.
- [ ] Measure preprocessing, encoding, execution, decoding and repair, including
  host overhead and failed runs.
- [ ] Otherwise state energy-efficient neuromorphic execution as a future
  deployment hypothesis.

Exit criteria: no CPU-simulation headline claims unsupported hardware speed or
energy superiority over optimized SA or Gurobi.

### P4.5 Statistical analysis and figures

- [ ] Freeze scripts and regenerate every table/figure from raw artifacts.
- [ ] Report seed distributions, feasible fractions, gaps and confidence intervals
  instead of only best runs.
- [ ] Separate numerical-optimizer figures from material-prediction figures.
- [ ] Include violations, failed cases, repair cost and data coverage.
- [ ] Create at minimum: workflow, benchmark-quality, feasibility, material-error,
  ranking/top-K and sensitivity figures.
- [ ] Put dataset split, units, sample count and limitations in captions.

Exit criteria: every plotted number traces to a saved machine-readable artifact.

### P4.6 Reproducibility bundle

- [ ] Pin Python, CUDA, solver and model versions.
- [ ] Save environment files, seeds, configurations and data manifests.
- [ ] Provide CPU instructions for synthetic tests and Kaggle GPU instructions for
  external model runs.
- [ ] Verify a clean-environment rerun of tests and a representative experiment
  from each track.
- [ ] Scan archives and Git history for secrets, private data and oversized files.
- [ ] Document licenses and access requirements for data, models and structures.

Exit criteria: another researcher can reproduce reported aggregates using the
documented inputs without receiving the Hugging Face token.

### P4.7 Manuscript and final audit

- [ ] Write methods: representation, constraints, parameter sourcing, SNN mapping,
  baselines, data splits, target and validation.
- [ ] Separate numerical, predictive and chemical-validity results.
- [ ] State the nonconvex SNN limitation and absence of a global guarantee.
- [ ] State that paired adsorption energy/delta is not DAC working capacity or
  experimental selectivity.
- [ ] Complete and verify the literature review before claiming novelty.
- [ ] Include unsuccessful runs, assumptions, data and hardware limitations.
- [ ] Run milestone, code, data-leakage, security and citation audits.
- [ ] Obtain professor review of chemistry assumptions and final claims.

Exit criteria: manuscript claims match the evidence and every result has a
traceable source artifact.

## Decisions requiring professor or user input

Prepare concrete options before requesting these decisions:

1. Exact real design family and finite linker/amine library.
2. Slot semantics, UiO-66 cell multiplicities, protonation/capping and defect
   policy.
3. Final physical objective beyond the adsorption-energy competition diagnostic,
   especially if working capacity or humid-air performance is claimed.
4. Independent validation method and affordable top-K budget.
5. Availability of direct neuromorphic hardware measurements.
6. Target venue, manuscript format and submission deadline.

Training extraction, baseline scaffolding, compatibility audits and analysis code
can continue before these decisions are finalized.

## Compute and storage plan

| Work | Minimum practical resource | Notes |
|---|---|---|
| Local tests, QUBO, SA and small Gurobi runs | CPU | Current suite runs locally; no GPU needed. |
| ODAC25 archive profiling/materialization | Kaggle CPU plus sufficient disk | Stream bounded shards; do not retain the full archive. |
| UMA adsorption calculations | Kaggle T4 GPU | Current environment succeeded on T4 and failed on P100 architecture support. |
| Composition baseline | CPU | Fit after training features are frozen. |
| CGCNN/MOFTransformer training | T4x2 or comparable GPU | Measure memory/runtime after model and batch size selection. |
| DFT/GCMC validation | External compute allocation | Method and budget require professor agreement. |
| Neuromorphic energy claim | Target neuromorphic hardware | CPU simulation cannot supply this evidence. |

## Immediate execution order

1. Add bounded ODAC25 training-shard discovery/materialization.
2. Freeze training targets and parent-MOF composition features.
3. Implement and run constant plus composition baselines.
4. Build and verify UMA adsorbed/bare/gas triplets; run UMA on T4.
5. Select and run one compatible graph/Transformer baseline.
6. Produce the frozen 138-MOF material-ranking comparison.
7. Review provisional chemistry and improve sampling/fit validation; auditable
   UMA-derived h/J now exists, but independent grounding and stable rankings do not.
8. Run grounded SNN/SA/Gurobi optimization and reconstruct top candidates.
9. Complete independent validation, ablations, figures and manuscript.

## Final completion checklist

- [ ] Phase 3 material baseline comparison passes its exit criteria.
- [ ] Real `h/J` sourcing and grounded optimization pass their exit criteria.
- [ ] Phase 4 structure and independent top-K validation pass.
- [ ] Sensitivity, failure and solver ablation analyses are complete.
- [ ] Reproducibility bundle reruns and contains no credentials.
- [ ] Manuscript, citations and claim audit are complete.
- [ ] Professor approves chemistry assumptions and final interpretation.
# Latest pilot gate — 2026-10-04 IST

Neweight-designpilot rawfiles lost after nonpersistentinteractive session restart;
finalcompletion/stabilityunverified. GPUsoff. Saved-batch replacement prepared and
55tests pass,awaiting explicitadditionalcomputeapproval. Read
[incident/replacement plan](UIO66_PILOT_RECOVERY.md). Historical64results/split remain
intact. No full64expansion,DFT,refit ormaterialranking claim. OlderACTIVE notes historical.


</details>
