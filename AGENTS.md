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

# Agent entry point

LATEST2026-10-04IST: priorpilotrawfiles LOST after nonpersistent interactive session;
GPUsoff,0activeevents,noverifiedcompletion/assessment. All ACTIVE notesbelow historical.
Read docs/UIO66_PILOT_RECOVERY.md and latest docs/UIO66_SAMPLING_EXECUTION.md.
Saved-batch replacement prepared/55tests;NOT approved orlaunched. Do NOT rerun
oldsetup/controller orcreatefreshallocationtimestamp until explicit replacement
approval. Historicalresults/frozen512poses/split/checkpoint unchanged;no64/DFT/refit.

## Authorized pilot execution

Main pilot ACTIVE in notebook11bab0e3c7 (controllerPID196): monitor only; do NOT
reload/RunAll/rerun controller. GPU512-pose preflight and checkpoint hash PASSED.
Read docs/UIO66_SAMPLING_EXECUTION.md; deadline21:01:13.871329UTC2026-10-03 unchanged.

Read the latest section of docs/UIO66_SAMPLING_EXECUTION.md and mutable pointer
artifacts/phase3/uio66_sampling_active_release.json before browser work.
User approved only512 guest starts and16 registered force continuations on2T4,
4.2h shared deadline; no refit,64 expansion orDFT. Approval persists; do not ask again.
Browser/HF_TOKEN recovered. Initial Linux preflight failed on Windows separators
before inference; failure evidence local. Portable successor release_20261003T170532Z
verified;52tests pass. GPU preflight restarting. Original start16:49:13.871329UTC,
deadline21:01:13.871329UTC on2026-10-03; NEVER refresh this active timestamp.
Preserve frozen releases/results, raw failures and partial outputs; assess frozen
criteria before further science.

For model/session continuation, read [MODEL_HANDOFF.md](MODEL_HANDOFF.md).

Read [agent.md](agent.md) for repository instructions, then [context.md](context.md)
and [chat_context.md](chat_context.md) for research context and current state.

RTK: read `C:/Users/hp/.codex/RTK.md` before use. Use
`C:/Users/hp/.local/bin/rtk.exe` for supported commands when helpful. Keep native
PowerShell commands and structured tool calls native; preserve raw verification evidence.
