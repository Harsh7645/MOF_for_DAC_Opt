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

Latest runtime blocker: user enabled file-URL access. Browser automation then failed
before interaction: Codex sandbox setup helper not found; resets/readiness checks
failed. Kaggle CLI lacks local credentials. No GPU allocated/no new energies.
Suggested recovery: restart desktop app, reopen chat, @Chrome continue pilot.
Approval persists. Before allocation run tmp/prepare_fresh_launch_receipt.py;
retain original immutable release, never extend an active allocation deadline.
See docs/UIO66_SAMPLING_EXECUTION.md.

## Authorized eight-design pilot launch (latest)

User approved512 guest plus16 force continuations,2T4 and4.2h deadline; no refit/DFT/full expansion.
Read ../docs/UIO66_SAMPLING_EXECUTION.md. Frozen71-file read-only release and watchdog exist;
51tests passed22.05s. Separate Kaggle notebook11bab0e3c7 created. Import blocked by
Chrome extension Allow access to file URLs disabled; user recovery requested.
No actual GPU allocation or scientific run started. Approval persists.

# Current state

LATEST2026-10-04IST: pilotexecution evidenceLOST,GPUsoff/0activeevents. Nonpersistent
interactive session expired/restarted;19:09:44UTC workingdirectorylackedpilotfiles.
Last192accepted/0failedobserved,actualcompletion/forcechecks/time unknown. No frozen
stabilityassessmentpossible. Read ../docs/UIO66_PILOT_RECOVERY.md. Saved-batch
replacement prepared,55testspass;explicitreplacementapproval required,NOTlaunched.
All ACTIVE notesbelow historical. No64/DFT/refit;phase3/ODAC25gatesremainopen.

LATEST17:16UTC2026-10-03: approved512+16pilot ACTIVE in notebook11bab0e3c7,
controller196/fourworkers; actual2T4,512frozen poses andcheckpointSHAverified.
Zero guest attempts at launch, no ranking. Monitoronly, neverrestart/reruncontroller.
Shareddeadline21:01:13.871329UTCincludingbothsetupattempts NEVERrefresh. Read
../docs/UIO66_SAMPLING_EXECUTION.md. Download/auditraw thenstopGPU andshowfrozen
assessmenttouserbeforeanyexpansion/DFT/refit. Phase3/ODAC25workstreamstillopen.

Superseding execution state (2026-10-03 17:12 UTC): Chrome/HF_TOKEN ready; initial
2T4preflight failed on Windows paths before inference. Failure archive/notebook
downloaded and session stopped. Portable shared resolver+boundary tests52pass;
512local frozen poses pass. Successor71-file release_20261003T170532Z uploaded;
repeatedGPUpreflight active. No guest energies yet. Originalshared deadline
21:01:13.871329UTC from16:49:13.871329UTC, NEVER reset. See latest section of
../docs/UIO66_SAMPLING_EXECUTION.md; older launch blockers below are historical.

Latest execution status (2026-10-03 16:53 UTC): Chrome recovered. Authorized private
notebook11bab0e3c7 imported, frozen input attached, two T4s selected and Internet ON,
session OFF. HF_TOKEN not listed in new notebook Secrets; user asked to add/attach
existing token directly there. No GPU/new energies. Receipt-only escaping fix
frozen successor release_20261003T164913Z preserves original and all scientific
inputs/code.71hashes and six-cell compilation/receipt roundtrip pass. Read
../docs/UIO66_SAMPLING_EXECUTION.md; older blockers below are historical.

Updated 2026-10-03. Phases 1 and 2 computational scopes are complete. Phase 3
numerical track is complete; its material-ranking track has authenticated ODAC25
and UMA evidence plus a frozen table of 138 paired validation targets.

Phase 2 evidence: `../docs/PHASE2_SUMMARY.md` and
`../docs/phase2_results.json`. Exact-equality convex control now converges in 251
iterations; five raw nonconvex 50-variable runs remain infeasible at strict
tolerance, while 5/5 decoded states are feasible.

Phase 3 evidence: `../docs/PHASE3_STATUS.md` and
`../docs/phase3_results.json`. Frozen seeds 100–119 were run at 12, 20 and 50 bits.
Gurobi certified 60/60 optima, exact enumeration agreed for all 40 <=20-bit
instances, 540/540 SA runs were feasible, and 60/60 decoded SNN runs were feasible.

External data decision: `../docs/dataset_decision.md`. The user has ODAC25/UMA
Hugging Face access and approved paired CO2/H2O adsorption-energy targets on
Kaggle GPU. The target contract and guarded Kaggle smoke pipeline are implemented;
the bundle includes an importable cell-by-cell Kaggle notebook. Authenticated
inventory and schema inspection succeeded on one 847,228,928-byte validation GCMC
shard (41,926 structures). Its sampled adsorption-energy fields are null. UMA on
P100 failed because Kaggle's PyTorch build lacks `sm_60`. The rerun succeeded on
one T4 for 16 structures: total-energy MAE 0.0236525 eV, RMSE 0.0248619 eV and
maximum absolute error 0.0355138 eV. Downloaded raw evidence is under
`../artifacts/kaggle/odac25_uma_t4_smoke_2026-09-12/`.

Historical verification: 26 tests passed after the September evidence update.
Current verification is in the active continuation below. Graphify's authoritative
coverage, source digests and graph integrity are recorded in
`../graphify-out/BUILD_AUDIT.json`; older graph counts are superseded.
The
T4 result validates authenticated loading and UMA execution, not paired target
quality or material ranking. All chemistry claims remain open; all reported
optimization benchmark coefficients are synthetic.

Target gate executed 2026-09-13: bounded streaming extraction selected
`val/mof_plus_adsorbate/part_00000.aselmdb` (8,418,258,944 bytes; SHA-256
`2927f1ebb3af5fd4ea6e5d1072f9bdef549afa9e53ce3f0605955885da4b6c8c`). The
authenticated full profile found 560,208 rows, 151 MOFs, 3,590 trajectories, 138
MOFs with both pure CO2/H2O records and 285 repeated MOF-gas groups. Missing/null
targets and count inconsistencies were zero.

The deterministic reduction executed on all 560,208 target-shard rows: exact
one-molecule rows, largest `fid` per trajectory, then lowest corrected adsorption
energy among final frames for each MOF/gas. It retained source index, trajectory
and fid and produced 285 single-gas targets forming 138 paired MOFs. Evidence is
under `../artifacts/kaggle/odac25_paired_targets_2026-09-14/`. The next gate is
frozen, training-only composition and UMA adsorption-energy baselines, followed
by the graph-model comparison. No predicted material ranking is claimed yet.

The detailed remaining execution plan, dependencies, artifacts and exit criteria
are maintained in `../docs/REMAINING_WORK.md`.

## Active continuation 2026-10-03

LATEST STEP — methods-focused eight-design sampling pilot prepared, not launched.
Read `../docs/UIO66_SAMPLING_PILOT_V2.md` and chemistry/DFT review draft.
Full64 structure/image-aware connectivity/source/reference and512-placement audit
passed. Parent six BDC linkers bridge twelve distinct node images; all64 host
nets have winding rank3, Zr/O degree8, four node OH; no periodic edge changes.
Chemical identity/protonation/rotamers remain unverified. Fixed initial planar
NH2 can become pyramidal; do not infer chemical validity from force convergence.
Frozen v2 patterns:000000,111111,110111,001001,000110,001100,000111,010101.
Plan has512 poses,32/gas/state:two independent16-start batches, each8targeted/
8random; data/design/uio66_sampling_pilot_v2.json SHA256
f5b4cd746c471838b141c91d88442026ab4f1bcc0bf7548d5665a8924724f68e.
Dry preparation9.19s;512-pose validation2.73s. Full suite50passed18.82s.
Archived main measured73.103min on2T4/4workers. Newmain estimate1.1–3.3h;
representative0.02-force allowance makes1.4–4.2h. Reserve2GiB outputs, excludes
weights/runtime. No new GPU job/DFT. Await allocation/protocol review; CLI defaults
to dry geometry. No64-design expansion supported. Registered representative
force continuation adds16guests and component refs at0.02/600steps; primary
pilot0.05/400steps. Initial0.01eV energy target assessed, not promised.
Historical51/13 split/results unchanged; four historical test designs enter
pilot, and all13 previously scored labels cannot serve untouched final tests.
ODAC25 mismatch stays separate; Phase3 overall incomplete. No external contact.

LATEST VERIFIED: Full provisional paired run, local audit, train-only fit and
CPU solver comparison completed. This supersedes running/no-fit statements below.
64 complete pairs; 512 accepted starts. Main archive downloaded (133,472,188
bytes), SHA-256 aee36cc47cda2b2088fc30c44f7fd240bad7e5731f71932a63018c4fc6bb1837.
Archived executed sources, bare input/report hashes and all local trajectories,
forces, contacts, inferred connectivity and CIF coordinates verified.
Max system force .049972475 eV/Angstrom; max observed steps200. Site-range
medians CO2 .135686 / H2O .326160 eV; maxima .196987 / .467891 eV.
Fit: 51 train/13 test; rank22, condition17.8487, bootstrap193/200 identifiable.
Pairwise held-out MAE/RMSE .0301754/.0413030 eV; additive .0238031/.0275139.
Pairwise generalizes worse. Nested2-vs4 starts: mean absolute delta change
.0130766, max .135151 eV, Spearman .7260, top10 overlap .4; max J shift .0506196.
Graph: `../data/design/uio66_uma_train_fit_v1.json`, heuristic/UMA-derived only.
CPU exact/Gurobi optimum110111: predicted delta -.0474215 eV, actual sampled
delta -.0436706. SA/raw SNN/thresholded SNN each10/10 fitted optimum hits.
Sampled best is111111 (-.0879886 eV), not the model optimum. Full-family top5
overlap .8 includes training and is not a held-out material score.
Curvature: min/max Hessian eigenvalues -.086836/.135148; no PSD shift.
Artifacts: `../artifacts/phase3/uio66_uma_fit/`, main archive and
`../docs/uio66_design_results.json`. No GPU job is active; draft save still failed.
Phase3 remains incomplete. Expand sampling under a separately named uniform
protocol before trusting rankings; chemistry/independent validation, frozen
ODAC25 reference/training compatibility and learned structure baseline remain open.

Paired adsorption protocol v1 is frozen and implemented. Actual pilot: states
000000/111111, two starts/gas, same pinned UMA. All 8 starts accepted; both
paired targets complete. Delta CO2-minus-H2O: +0.0296889057 and +0.0126993900 eV.
Model gas references: CO2 -22.9974396449; H2O -14.3828426083 eV. These are UMA
values, not ODAC25 DFT constants. Site ranges reach 0.36944 eV; no strong
material ordering, global-minimum or selectivity claim follows.
Raw pilot archive/CIFs/trajectories/logs/executed sources were downloaded to
`../artifacts/kaggle/uio66_adsorption_2026-10-03/`; local audit passed, source
report SHA-256 021bd197b54af8e5ce886415959aa44c805c56808caa5fad84c72f0f2c6fb86e.
The full run is active: all 64 states, four starts/gas, fmax 0.05, 200 steps,
four single-thread processes on two T4 GPUs. Latest observed checkpoint had
21 complete pairs, no failed pairs; counts are provisional while running.
Do not reset the live Kaggle kernel. Save conflict backup is retained locally.
Freeze before fitting: 53 merged duplicate groups, 51 train/13 test, rank 22;
pilot groups restricted to training. Implemented audited all-target fitting,
additive comparison, training-group bootstrap, provisional graph export and
CPU solver comparison scaffolding. None has fit or benchmarked real h/J yet.
Reproducible adsorption notebook and 118-file bundle (407,156 bytes at creation)
exist. Full verification: 44 tests passed in 15.57 seconds; synthetic demo -4.6,
no SNN in demo. ASE/NumPy/spglib upstream deprecation warnings remain.
Next: preserve full output, audit every trajectory/label, fit only if all 64
targets pass, inspect held-out/sampling errors, then compare actual solvers.
Independent chemistry review and ODAC25/learned-baseline gates remain open.

64/64 provisional UiO-66 bare structures converged on two T4 GPUs using pinned
UMA-s-1p2p1, task odac, batch inference and fixed-cell LBFGS. Tolerance 0.05
eV/Angstrom, 150-step budget; observed 0–42 steps, maximum force 0.0499344.
All were contact-free below 0.7 Angstrom with unchanged distance-inferred bonds.
Trajectories/logs/CIFs and executed sources were downloaded to
`../artifacts/kaggle/uio66_bare_2026-10-03/`. Independent local trajectory-energy,
force, source/input/output hash and CIF diagnostics passed. Bare energies alone
are not adsorption h/J or chemical validation. See
`../docs/UIO66_PROVISIONAL_LIBRARY.md` for provenance and limitations.

Initial duplicate audit: 53 parent-operation groups at 0.01 and 0.05 Angstrom,
64 at 1e-5; not a full crystallographic equivalence certificate. Retain initial
duplicate groups together for future fitting. Reproducible notebook and small
structure-bearing bundle are implemented. Relaxed grouping found 54 groups at
0.01 Angstrom and 53 at 0.05. Retain initial duplicate groups conservatively.
Full suite: 39 passed in 10.81s;
synthetic demo remains -4.6. Upstream ASE/NumPy/spglib deprecation warnings remain.

Phase 3 is incomplete. Frozen ODAC25 reference convention and training-field
mismatch remain unresolved; local `../docs/ODAC25_REFERENCE_QUESTION.md` draft
records reproducible questions and has not been sent. Next independent work:
chemistry review and paired adsorption placement/relaxation/reference protocol
for the provisional family, followed by labels, uncertainty-aware h/J fitting,
and grounded solver comparisons. Preserve the 138-pair ODAC25 benchmark.

## Historical continuation 2026-10-02

Read `../docs/PHASE3_REFERENCE_AUDIT.md` and
`../docs/UIO66_PROVISIONAL_LIBRARY.md` first. September eSEN had 68 OOM failures;
no full-pool score is valid. Fresh Kaggle T4 execution restored bounded data
and audited 2,048 spaced rows. Adsorption fields use `energy_old`: gas constants
are -22.990396 eV CO2 and -14.236396 eV H2O; sample identity spreads are below
3.3e-14 eV. Corrected total `energy` cannot replace it. Scoring now reverses
recorded system/bare k-point shifts for frozen labels: reference-assisted
evaluation on DFT-selected geometries, not prospective screening. Matched bare
references and full inference are still being verified.

Safeguards: cached-input SHA-256 binding, frozen source-index verification,
retained training provenance, progress checkpoints and average-tie Spearman
(constant ranks produce null). Notebook syntax fixed; 21 cells compiled.
Final full suite: 36 passed in 14.17 seconds. All 64 CIF roundtrip checks pass.
ASE 3.26.0 emits an upstream NumPy 2.5 shape-deprecation warning. Synthetic
demo remains energy -4.6; no SNN run in that demo.

User approved a provisional UiO-66 library: 64 nominal six-slot BDC/NH2-BDC
patterns with ideal formal charge/stoichiometry. An authenticated ODAC25 parent
was exported (index 184693, `jz4002345_si_002`, fid 7); periodic mapping found
six complete BDC linkers, and all 64 unrelaxed CIF proposals passed composition
and severe-contact checks. Symmetry deduplication, adsorption labels and real
h/J remain absent. Training-mirror
corrected-field/fid incompatibility remains a P3.1 blocker. Do not mark Phase 3
complete or move its real-grounding gate to Phase 4.

Bare-reference audit: all-frame minima gave 145 mismatches; final-frame minima
gave 94 of 285. Direct lookup over all 189,504 bare rows completed: 67 distinct
unresolved energies, 5 with exact stored matches and 62 without. The convention
or reference version needs clarification. Do not
score an altered subset or bypass the energy-identity guard. Audit archives are
downloaded under `artifacts/kaggle/odac25_reference_audit_2026-10-02/`.
