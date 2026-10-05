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

LATEST 2026-10-04T14:13UTC: matched V2 private saved Version1 ACTIVE (355186088).
Monitor existing https://www.kaggle.com/code/sahuharsh/uio66-matched-diagnostic-v2?scriptVersionId=355186088
NEVER rerun/SaveVersion2/start draft. Draft OFF; UI GPU T4x2, runtime gates pending.
Submission14:12:45.336673UTC, external workerstop16:07:45UTC / end16:12:45UTC.
Frozen first-cell receipt controls original runtime setup/worker deadline; no extensions.
After terminal state download/hash evidence and locally rerun assessment; no further calculations.

LATEST 2026-10-04: USER APPROVED frozen matched diagnostic V2 execution only.
Two T4s, two-hour total including setup; worker stop115min, preserve partials.
No retries/repairs/substitute hosts/deadline extensions. No refit/64/DFT.
Preparing PRIVATE saved Kaggle batch; NOT LAUNCHED yet. Follow
artifacts/phase3/uio66_matched_v2_authorized/authorization.json for launch copy.
Frozen bundle unchanged SHA027f634ce1545c5810f9e19535ef5dd190df6714999a5e28d5502d171b50c83a.
Kaggle extracts nested ZIPs: upload byte-identical .bin, execution-copy notebook
APPROVED=True plus .bin lookup and explicit bundle SHA check. 74 file hashes
verified locally; GPU/checkpoint/shared-host/all4 mapping gates remain runtime.
Earlier preparation-only approval notes below superseded by explicit approval.

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

## Authorized pilot launch status (latest)

Read docs/UIO66_SAMPLING_EXECUTION.md. User approved only512 guest starts and16
force continuations on2T4,4.2h shared deadline; no refit,64 expansion orDFT.
71-file read-only release frozen under artifacts/phase3/uio66_sampling_release_20261003T161558Z;
controller watchdog tested;51tests passed. New private Kaggle notebook11bab0e3c7
created,old notebook preserved. Chrome local-file upload blocked: user must enable
ChatGPT extension Allow access to file URLs. No GPU session/calculation started.
Allocation approval persists; do not ask again. Verify immutable release and
checkpoint remotely, record actual allocation, run and assess after upload recovery.

# Model handoff — 2026-09-14

## Resume here

LATEST2026-10-04IST: STOPPED,0activeGPUevents. Priorinteractivepilotrawfiles lost
afterinactivity/nonpersistent restart. Lastobserved192accepted/0failed;actualfinal
completion/attempts/forcechecks/allocation unverified,noassessmentpossible. Do NOT
rerunoldsetup/controller. Read docs/UIO66_PILOT_RECOVERY.md/latestexecutionrecord.
Private saved-batch replacementnotebook prepared,waitsforcontroller/archiveserrors;
55testspass. Replacementcompute needs explicitapproval,newfrozenreceipt/verified
privateversion. No activeclock maybeextended. Historical64results/split/manifest
and originalreleases intact. No64expansion/DFT/refit ormaterialrankingclaims.

LATEST: authorized main pilot ACTIVE (2026-10-03 17:16UTC), controllerPID196,
all4worker reports started, zero attempts at launch. Portable GPU512-pose check
passed2.90s and exactcheckpointSHAverified. Do NOT reload/RunAll/rerun setup or
controller. Monitor cell only in notebook11bab0e3c7; deadline21:01:13.871329UTC
including bothsetup attempts, NEVER refresh. Read docs/UIO66_SAMPLING_EXECUTION.md.
After completion preserve/download/audit raw failures and combined frozencriteria,
stopKaggleGPUreservation, showuser results beforeanynextscience. No ranking yet.

Latest superseding execution status (2026-10-03 17:12 UTC): browser/HF_TOKEN ready.
GPU preflight failed before inference on Windows paths; raw5852-byte failure archive
and executed notebook downloaded. Two T4s stopped, portable path fix tested52passed,
then successor release_20261003T170532Z imported/private input attached and GPU
preflight restarting. BundleSHA989e26c4a3257bb893648985c86808404e88d69a67ad2a3192c2d4b6a46d0cb1;
all71hashes verified,512frozen local poses checked2.573s. Shared deadline remains
21:01:13.871329UTC from16:49:13.871329UTC; NEVER refresh active allocation timestamp.
No guest energies yet. Read docs/UIO66_SAMPLING_EXECUTION.md/current active pointer.

Latest execution (2026-10-03 16:53 UTC): Chrome restored; authorized six-cell
notebook imported and private frozen input attached at notebook11bab0e3c7.
Two T4s selected/Internet ON/session OFF. No GPU/new energies yet. New notebook
Secrets has no saved labels: user asked to add existing HF_TOKEN directly in
Kaggle and attach it. Await readiness, then verify remote environment/checkpoint
and launch approved512+16 with shared4.2h deadline. Receipt-only formatting fix
frozen as successor release_20261003T164913Z, bundleSHA
f3b141a641643c19273d87d0f33d6c6307d088edaaae92539004d9f74bf88736;
original preserved, all71hashes verified, scientific inputs/code unchanged.
Read docs/UIO66_SAMPLING_EXECUTION.md for authoritative current state.

Latest requested step: read `docs/UIO66_SAMPLING_PILOT_V2.md` and
`docs/UIO66_CHEMISTRY_REVIEW.md`. Methods-focused paper; 64 patterns provisional.
Fresh image-aware audit of all64 and512 archived starts passed. Eight patterns
frozen before new energies: 000000,111111,110111,001001,000110,001100,000111,010101.
`data/design/uio66_sampling_pilot_v2.json` contains512 initial poses,32/gas/config,
two independent batches with identical targeted/random quotas. SHA256
f5b4cd746c471838b141c91d88442026ab4f1bcc0bf7548d5665a8924724f68e.
CPU preparation9.19s and geometry validation2.73s passed; full suite50 tests passed.
No new UMA/DFT calculation launched. Review allocation before launch: main pilot
1.1–3.3h on twoT4/fourworkers, with representative force-study allowance1.4–4.2h
total; reserve2GiB outputs plus model/runtime caches. Exact commands/notebook in
protocol; `scripts/run_uio66_sampling_pilot.py` is dry-run by default, explicit
--execute only. `kaggle/uio66_sampling_pilot_v2.ipynb` allocation flags False.
Representative force study adds16 guest continuations at0.02 (not in512 count).
Initial0.01eV assessment target is not a universal guarantee. Chemistry review
pending; no full64x32x2 or periodicDFT authorized. Original51/13 split and scores
remain frozen; all13 historical test labels viewed, now development evidence.
ODAC25 reference mismatch separate/unresolved. No dataset-author/professor contact.

Latest verified milestone (2026-10-03): the full UiO-66 paired experiment and
provisional fitting/solver loop HAVE EXECUTED. This supersedes active-run/no-fit
notes below. Read `docs/UIO66_ADSORPTION_PROTOCOL.md`,
`docs/uio66_design_results.json` and `.planning/STATE.md`.
64/64 pairs, 512/512 starts accepted; downloaded 133,472,188-byte main archive,
SHA-256 aee36cc47cda2b2088fc30c44f7fd240bad7e5731f71932a63018c4fc6bb1837.
Remote and local trajectory/contact/connectivity/CIF/source/input audits passed.
Train-only fit: rank22, condition17.85, 51 train/13 test, 193/200 bootstrap draws
identifiable. Held-out pairwise MAE .0301754 eV vs additive .0238031 eV: pairwise
is worse. Two-vs-four-start top10 overlap .4, max delta change .135151 eV:
sampling/ranking is unstable. Do not claim validated h/J or reliable material ranking.
`data/design/uio66_uma_train_fit_v1.json` is a provisional UMA-derived heuristic
graph. CPU enumeration/Gurobi agree; SA and raw/thresholded SNN each hit the
fitted six-bit optimum 10/10. This does not establish larger-scale performance.
Main artifacts: `artifacts/kaggle/uio66_adsorption_2026-10-03/main/`;
fit/solver output: `artifacts/phase3/uio66_uma_fit/`. No GPU job remains active.
Kaggle still reports draft save failure; raw evidence and replay notebook are
local. Do not claim successful Save Version. Phase 3 overall remains incomplete.
Next independent step: separately named, uniformly expanded site-sampling study;
preserve v1 labels/split and inspect additive-vs-pairwise quality, never retune
on test labels. ODAC25 reference/training and learned-baseline gates still open.

Latest continuation (2026-10-03, paired adsorption) supersedes older counts below:
read `docs/UIO66_ADSORPTION_PROTOCOL.md` and `.planning/STATE.md`. The actual
two-state UMA pilot produced 8/8 accepted starts and two paired model targets;
downloaded evidence passed the local trajectory/contact/connectivity audit.
The full 64-state, four-start-per-gas run is ACTIVE in the existing Chrome Kaggle
notebook. Do not reload/Run All/stop it. Four workers, two per T4; outputs
`/kaggle/working/uio66_ads_full/worker*/adsorption.json`. Download and audit the
full archive before fitting. `data/design/uio66_fit_split.json` froze 53 duplicate
groups, 51 train/13 test, rank 22; both inspected pilot states are train-only.
No real h/J fit or solver comparison has executed yet. Reproducible notebook:
`kaggle/uio66_adsorption.ipynb`; bundle `artifacts/kaggle/UIO66_Adsorption_bundle.zip`.
Fit CLI: `python -m scripts.fit_uio66_adsorption --reports <four reports>
--output-dir artifacts/phase3/uio66_uma_fit`. It rejects incomplete targets and
changed protocols/splits. Then run `scripts.benchmark_uio66_fit` on fit/instance.
These are provisional UMA coefficients, never DFT-grounded validation. Phase 3
remains incomplete; frozen ODAC25 reference/training and learned-baseline gates
are unresolved. Notebook draft save conflict: backup downloaded locally; do not
reload a busy kernel. See `artifacts/kaggle/uio66_adsorption_2026-10-03/README.md`.

Current milestone (2026-10-03): read `docs/UIO66_PROVISIONAL_LIBRARY.md` and
`.planning/STATE.md`. All 64 provisional UiO-66 bare structures ran on two Kaggle
T4 GPUs with pinned UMA: 64 converged, 64 contact-free, 64 unchanged inferred
connectivity. Trajectories/CIFs/sources are downloaded to
`artifacts/kaggle/uio66_bare_2026-10-03/`; local independent audit passed.
Initial parent-operation grouping found 53 groups at 0.01/0.05 Angstrom,
64 at 1e-5. Retain initial duplicate groups for leakage safety.
39 tests pass; synthetic demo -4.6. Reproducible notebook:
`kaggle/uio66_relaxation.ipynb`. Phase 3 remains incomplete: these are bare
model energies, not paired adsorption labels or real h/J. ODAC25's 62 unmatched
reference energies and training-field mismatch still block full material scoring;
`docs/ODAC25_REFERENCE_QUESTION.md` is a local clarification draft, not sent.
Preserve frozen validation and the separate design experiment. Graphify's
`BUILD_AUDIT.json` records corpus/source freshness after refresh.

Current continuation (2026-10-02) supersedes stale counts below. Read
`.planning/STATE.md`, `docs/PHASE3_REFERENCE_AUDIT.md` and
`docs/UIO66_PROVISIONAL_LIBRARY.md` first. Phase 3 is incomplete. A fresh Kaggle
T4 run is auditing corrected total-energy versus `energy_old` adsorption
conventions and matched bare references. Preserve the notebook and download
results before ending the session. The user approved a provisional six-slot
BDC/NH2-BDC library; 64 unrelaxed CIF proposals now exist from an authenticated
ODAC25 parent with inferred periodic atom mapping. No real adsorption labels or
h/J exist. Bare-minimum matching still fails for 94 of 285 selected targets;
direct all-frame lookup completed on 189,504 rows: 62 of 67 distinct unresolved
energies have no exact stored match at 1e-5 eV. Preserve the frozen benchmark;
a separate target protocol needs explicit approval. Downloaded audit evidence is in
`artifacts/kaggle/odac25_reference_audit_2026-10-02/`.
Training mirror lacks corrected labels/fid.

Workspace: `C:/Users/hp/Documents/GitHub/MOF_for_DAC_Opt`.
Phases 1–2 and the Phase 3 frozen numerical track are complete. The paired
CO2/H2O ODAC25 validation target table has been materialized and downloaded.
Authenticated ODAC25 inventory, GCMC schema evidence and a successful 16-record
T4 UMA smoke output exist. The target-bearing shard was extracted and fully
profiled: 560,208 rows, 151 MOFs, 3,590 trajectories, 138 MOFs with pure CO2/H2O
records and 285 repeated MOF-gas groups. The deterministic exact-single-molecule,
final-frame, strongest-sampled-configuration reducer is implemented and tested.
The frozen reducer produced 285 single-gas targets and 138 paired validation
MOFs. Run non-leaking adsorption-energy baselines next; no predicted paired
ranking exists yet.
Read `.planning/STATE.md`, `docs/ODAC25_TARGET_CONTRACT.md` and
`docs/ODAC25_KAGGLE_RUNBOOK.md` for authoritative continuation state.
Use `docs/REMAINING_WORK.md` as the detailed checklist for every unfinished
Phase 3/4 deliverable and exit criterion.

Read `AGENTS.md` -> `agent.md`, this file, `.planning/STATE.md` and
`.planning/ROADMAP.md`; read `context.md` for the source-derived mathematical
contract. `chat_context.md` contains prior work/evidence. Original report text and
professor feedback are in `sources/`; do not request the originals again.

## Verified state before handoff

- NumPy/SciPy implementation exists: graph loader, Hamiltonian/QUBO construction,
  explicit linear constraints, SA, SLSQP, tiny enumeration and distance repair.
- Last recorded tests: 12 passed. Toy exact optimum -4.6; synthetic only.
  Tests were not rerun for this documentation-only handoff.
- SNN 0.6.0 and Gurobi 13.0.3 have now executed; read Phase 2/3 artifacts for the
  newer evidence. Surrogate inference, real chemistry coefficients, DFT and
  hardware measurement have not run.
- Phases 1–2 computational scopes are complete. Phase 3 is active and incomplete.
- The T4 UMA smoke run used `uma-s-1p2p1` with task `odac` and completed 16 GCMC
  structures on CUDA. Total-energy MAE was 0.0236525 eV, RMSE 0.0248619 eV and
  maximum absolute error 0.0355138 eV. Raw evidence is in
  `artifacts/kaggle/odac25_uma_t4_smoke_2026-09-12/`. This is an execution check;
  sampled paired adsorption fields were null.
- The authenticated target profile selected an 8,418,258,944-byte
  `mof_plus_adsorbate` database with SHA-256
  `2927f1ebb3af5fd4ea6e5d1072f9bdef549afa9e53ce3f0605955885da4b6c8c`.
  Persisted evidence is under
  `artifacts/kaggle/odac25_target_profile_2026-09-13/`.
- Current verification: 26 tests pass. Authenticated `paired_targets.json`
  evidence is in `artifacts/kaggle/odac25_paired_targets_2026-09-14/`.
- All project files remain untracked; no commit/push was made. Preserve files.

## Next implementation sequence

1. Preserve the frozen 138-pair validation table; do not use its labels to fit
   baselines or tune hyperparameters.
2. Materialize matching training targets/features with the same v1 rule.
3. Evaluate a mean/composition baseline and UMA adsorption-energy baseline on the
   same frozen validation records. Preserve official split boundaries.
4. Add a compatible CGCNN/MOFTransformer-family comparison or document a concrete
   target/interface incompatibility. Then produce the first material-ranking
   table with paired metrics and top-K overlap.
5. Move to Phase 4 validation, sensitivity analysis, figures and manuscript only
   after the material-ranking gate passes.

## Research leads already found (reopen before asserting details)

These are continuation leads, not a finished systematic review or proof that all
full texts were read. Prior browsing found:

- Lucas 2014, Ising formulations; equality/one-hot penalties and integer slack:
  https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2014.00005/full
- Mancoo et al. convex SNN/QP paper; inspect exact assumptions:
  https://proceedings.neurips.cc/paper_files/paper/2020/file/64714a86909d401f8feb83e8c2d94b23-Paper.pdf
- Greene-Diniz et al. 2022, MOF carbon capture via quantum electronic structure,
  not building-block QUBO: https://arxiv.org/abs/2203.15546
  https://link.springer.com/article/10.1140/epjqt/s40507-022-00155-w
- Kitai et al. 2020, factorization machines + quantum annealing for metamaterials;
  methodological analogy, not MOF study: https://www.tsudalab.org/publication/2020-kitai-designing/
- Periodic MOF quantum simulation: https://arxiv.org/abs/2510.02550 ; published
  version https://doi.org/10.1039/d6dd00023a . Distinguish VQE from annealing.
- MOFTransformer: https://www.nature.com/articles/s42256-023-00628-2
- Classical SA/NN potential orientational isomerism candidate:
  https://onlinelibrary.wiley.com/doi/10.1002/jcc.70349
- Unverified candidate for follow-up: https://arxiv.org/abs/2504.17453
- CoRE sources: https://doi.org/10.1021/acs.jced.9b00835 ;
  https://zenodo.org/records/14184621 . Structures are not ready-made block h/J.
- Possible fixed-template chemistry sources, not validated implementation:
  https://pubs.rsc.org/en/content/articlehtml/2017/cp/c6cp07801j ;
  https://www.nature.com/articles/ncomms5176 . Verify sharing/multiplicities,
  protonation and defects before assigning UiO-66 charges or building a library.

## Efficient retrieval and continuity

- Read `docs/knowledge_graph.md`; use Graphify exact-symbol `explain` first.
  Never dump the entire graph into context. Follow source pointers as needed.
- Current graph was refreshed after the October reference/structure milestone.
  `graphify-out/BUILD_AUDIT.json` contains the authoritative counts and source
  SHA-256 audit. Graph, coverage, directed imports, HTML and local links passed.
- Graphify budgets are advisory. Graph records are an index, not complete memory
  or scientific evidence. Refresh AST and semantic documents after work, audit
  freshness and preserve extracted/inferred distinctions.
- Graphify executable: `C:/Users/hp/.local/bin/graphify.exe`; Python environment:
  `C:/Users/hp/AppData/Roaming/uv/tools/graphifyy/Scripts/python.exe`.
- Prior build helper `tmp/build_graph.py` is ignored and requires regenerated
  extraction intermediates. `tmp/verify_graph.py` now checks dynamic counts and
  source SHA-256 freshness.
  Do not blindly rerun either or assume helper existence in a fresh checkout.
- Keep changes minimal, array-native and tested. No PyTorch dependency until an
  actual ML/GPU workload needs it. Apply available requested skills and RTK rules.
- Update chat_context, STATE and roadmap after each meaningful work block; record
  failures and exact next actions. Routine implementation choices can proceed;
  data access, licenses and physical measurements cannot be fabricated.
