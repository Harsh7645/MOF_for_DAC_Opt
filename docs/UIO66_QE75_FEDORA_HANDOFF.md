# Fedora handoff — 2026-10-10, all 14 baseline SCFs verified

**TERMINAL: 12/12 recovery-batch jobs complete; together with the prior two water complexes, 14/14 mandatory baseline single points have converged. All execution authorizations are consumed. No further calculation authorized.**

- Read `docs/UIO66_QE75_BASELINE14_RESULTS_V1.md` for the complete per-job table, energy decomposition, force findings and limitations.
- Independent offline audit passed all twelve outputs/XML/settings/composition-specific electron counts/frozen atom identities and cells, **1,463 total force vectors and 320 raw-file hashes**. Both prior water input/stdout/XML pins unchanged. All fourteen force statistics, available UMA force differences and paired energy differences reconstructed. No substantive report/raw discrepancy found.
- SCF: **16–18 iterations**, maximum final error **9.48046878554e-9 Ry** under unchanged 1e-8 Ry. Exit 0/JOB DONE/converged XML for every job; complete finite forces. No final diagonalization warnings. Final negative pseudocharge **0.3935–0.3946 e**, separately retained, not an automatic numerical verdict.
- Four physical cores; **11-GiB hard / 10-GiB high / zero job swap / 96 tasks** retained. Largest measured peak **9.537064 GiB**; minimum sampled host available **3.530083 GiB**; no observed resource-limit events. Final cgroups removed at normal exit; accounting relies on preserved full-service peaks, all samples and journals, not missing final counters.
- New runs through cleanup sum **13h39m53.571s**. Original batch through terminal finalization **18h29m53.924s**, including interrupted v1/Windows downtime and preparation, under the immutable 48-hour ceiling. Every attempt met its four-hour ceiling. Batch finished **2026-10-10 09:17:31 IST**. Job01 used one explicitly authorized clean recovery; remaining jobs each one attempt.
- Retained scratch **9.093915 GiB**, including final XML, charge density, PAW data and four-rank wavefunctions. No QE/MPI workers, task inhibitors or temporary overrides remain. All job/guardian/timer units are terminal. No new computation was launched during final review.
- DFT complex changes (later-minus-earlier, meV): water **−38.396707**, CO2/s7 0.020→0.010 **−79.440623**, CO2/s7 0.010→0.005 **−10.155191**, CO2/s16 0.010→0.005 **−15.607560**. Corresponding complex-minus-host changes: **−16.671220, −80.630235, −0.294481, −15.403850 meV**; these are not adsorption energies. The sub-meV remainder is not numerically resolved. DFT/UMA complex-difference discrepancies are **2.14–4.39 meV**, provisional.
- Evidence: `evidence/qe75-baseline12-recovery-v2/terminal-review-v1/independent-audit.json`, `comparison-audit.json`, `all-force-crosschecks.csv`; original comparisons and full per-job accounting in the parent directory. Raw `local/qe75-baseline12-recovery-v2/jobNN/run01/`; all historical failures/results unchanged.
- Portable review: `artifacts/phase3/uio66_qe_baseline14_review_v1.zip`, **471 verified payloads**, **3,930,640 bytes**, SHA256 `8f7fbf7abc4839117595f18e14b42db05d8392547cede539232ae937e99bf0d7`. Includes inputs, complete stdout/stderr, final XML, potentials, forces, accounting and checksums. **Large binary checkpoints remain on Fedora; this review ZIP is not a full restart backup.** Receipt: `evidence/qe75-baseline12-recovery-v2/terminal-review-v1/portable-review-receipt.json`.
- **Next decision:** review the completed baseline, then separately authorize the already prepared paired 80/750-Ry water density checks on a verified larger-memory allocation. Existing estimated 12–13-GiB demand exceeds this laptop's unchanged guards. Set explicit numerical acceptance rules; historical 2–3-meV and 0.005–0.01-eV/Å ranges remain ambiguous. Wavefunction cutoff, k points, host/CO2 transfer and physical/UMA accuracy remain unresolved.
- **Phase 3 remains incomplete.** Frozen forces do not establish relaxed minima; publication proton correspondence and four missing UMA host single points remain unresolved/separate. No relaxation, UMA, refitting or study expansion authorized.

---

## Windows analysis handoff — 2026-10-10

See `docs/UIO66_QE75_WINDOWS_BASELINE14_GUIDE.md`. The unchanged compact review ZIP is being committed with its checksum/receipt and a Python-standard-library offline verifier. It independently reconstructs all 14 results and 1,717 force vectors. Thirteen targeted offline tests pass; no calculation was launched.

**Summary correction:** 0.435954 eV/Å is the largest new complex force; the overall maximum is 0.565884531 eV/Å on the f0.010 water host (atom 115). Archived tables/raw evidence were correct; the immutable ZIP is preserved. Full checkpoints remain in the paths above and in the Windows guide. Phase 3 remains incomplete.

## Historical records

LATEST 2026-10-09: AUTHORIZED 12-job80/600 baseline batch recovery v2 COMPLETED.
Completed 12/12; active []. Two previous water complexes excluded.
Read docs/UIO66_QE75_BASELINE12_V2_PROGRESS.md and evidence/qe75-baseline12-recovery-v2/progress.json.
One newly authorized recovery for job01; otherwise ONE attempt/job,4h/attemptinclprepcleanup,48himmutablebatch;sequential4cores/11hard10high/zeroswap/96tasks.
Controller run_qe75_baseline12_v2.py is exclusively entered; do not relaunch or reset allocations.
If active,monitor existing qe75-baseline12-v2-batch.service only. If stopped,report blocker,no automatic retry.
Blocker: none. Pending IDs retain status; no extra calculations.
Raw local/qe75-baseline12-recovery-v2/;evidence evidence/qe75-baseline12-recovery-v2/;same80/600science.
750Ry checks NOT authorized;no limitsincrease/relaxation/UMA/refit. Phase3/cutoff/physicalaccuracy unresolved.
<!-- END BASELINE12 LIVE STATUS -->

# Fedora handoff — 2026-10-09, paired 80/750-Ry preparation only

**No calculation authorized or launched. Local execution is blocked by memory, even if the 12-GiB available-RAM gate is later met.**

- Read `docs/UIO66_QE75_RHO750_PAIR_PREPARATION_V1.md` for exact remaining manifest IDs, comparison rules, commands and budgets.
- Inventory: **14 baseline jobs = seven complexes + seven hosts; two water complexes converged; five complexes and all seven hosts remain.** Optional guests and the proposed two density checks are separate.
- `plans/qe75-rho750-pair-v1/` contains two pinned 80/750 inputs, `batch.json` (execution disabled), `inventory.json`, `assessment-spec.json`, `force-atom-map.csv` and source/input hashes. Only `ecutrho` changes from each actual converged input. Separate planned work roots `local/qe75-rho750-pair-v1/water01/run01/` and `water02/run01/`; no directories launched or checkpoint reused.
- Offline check `python scripts/check_qe75_rho750_preparation_v1.py` passed: 49 targeted hashes, exact cutoff-only byte changes and 14-job inventory. Existing full-package/portable-result/control audits reused. All sealed and historical results unchanged.
- Resource snapshot `evidence/qe75-rho750-preparation-v1/resources.json`: **14.936 GiB physical, 11.066 available, 203.833 GiB free persistent disk**, AC online, no QE/MPI workers, unused 8-GiB system swap. No applications closed.
- 750-Ry estimate **12.005–13.017 GiB** (not bounds) exceeds unchanged **10-GiB high/11-GiB hard**, zero job swap/96 tasks/four cores. Even analytical base+workspace 11.335 GiB exceeds the hard cap. Do not launch locally or silently raise limits. Predicted dense **243³ / 2,658,579 Gamma G**, smooth **160³ / 741,079 G**; verify actual output later.
- No initialization probe proposed: prior source-verified `nstep=0` path does not measure SCF memory and cannot clear this blocker.
- Assess δΔE = ΔE750−ΔE600, with baseline ΔE600=−0.03839670675722525 eV, and all corresponding force components with validated Ha/bohr→Ry/bohr→eV/Å units and atom mappings. Monitor negative pseudocharge/grid/resource evidence without automatic pseudocharge thresholds.
- Historical numerical targets **2–3 meV** and **0.005–0.01 eV/Å** are ranges with unspecified binding threshold/force aggregation. Flag ambiguity; no invented pass criterion. Density-only checks do not establish wavefunction-cutoff/k-point/host/CO2/physical accuracy.
- **Next decision:** obtain a verified larger-memory allocation and agree on the numerical assessment rule, then finalize the bounded adapter for exactly two serial checks. Candidate host ≥32 GiB physical/20 GiB available, proposed 16-GiB hard/15-GiB high, four cores/zero swap/96 tasks; this is a new proposal only, not a changed laptop configuration or permission. Four hours per job including setup/cleanup, eight hours total, no retries/extensions. Runtime readiness remains blocked until that allocation and changed controls are verified.
- Remaining baseline sequence: two water hosts, three 110111 CO2 complex/host pairs, two 000000 CO2 complex/host pairs. Use one accepted consistent protocol; reprice/recalculate affected comparison sets if settings change. Rough water-time reference ~14.1h for 12 jobs is not a forecast; proposed serial cap 48h, separately approved batches. Phase 3 remains incomplete.

---

## Historical records

# Fedora handoff — 2026-10-09, BOTH frozen-water baseline SCFs converged

**TERMINAL. Second-attempt v7 authorization consumed; no further calculations authorized.**

- Read `docs/UIO66_QE75_WATER_PAIR_V7_RESULTS.md`. Second geometry converged in **16 iterations**, error **4.636287245504316e-9 Ry**, exit 0/JOB DONE. Text/XML energy, 522 electrons, all 127 frozen atoms/cell/potentials and 127 finite force vectors pass independent checks.
- Second energy **−3003.62675764 Ry**. DFT second-minus-first **−0.038396706757 eV**, archived UMA **−0.041461080671 eV**; difference **+3.064374 meV**. Both favor the second checkpoint at these settings; cutoff/grid and physical accuracy remain unverified.
- Second maximum force **0.155316693 eV/Å** (atom 95, O), RMS **0.083128119 eV/Å**; frozen structures are not DFT-relaxed minima. Final negative pseudocharge **0.3946 electrons**, no diagonalization warnings; not an automatic accuracy verdict.
- Peak **9.245415 GiB**, zero job swap and no observed memory/task events; four physical cores/11-GiB hard/10-GiB high/96 tasks unchanged. Minimum host available RAM **1.018932 GiB**; retain reserve on any future run.
- Runtime plus cleanup **70m40.105s**; original allocation through automatic package **72m04.701s**, within four hours. All 2029 samples AC online and sleep:idle inhibited; no suspend. Workers/guardian/timers stopped, inhibitor released, runtime override removed. No apps closed by agent.
- Scratch **830,566,191 bytes**, XML/density/PAW/wavefunctions retained; 27 raw hashes verified. Normal exit removed cgroup before final counters could be captured; independent audit v2 uses retained full service peaks/samples/journal. Original v1 audit assumption failure preserved, all scientific checks unchanged.
- Raw `local/qe75-second-v7/run01/`; evidence `evidence/qe75-second-v7/`, especially `assessment.json`, `comparison.json`, `independent-audit-v2.json`, `independent-force-crosscheck.csv`, `independent-resource-summary.json`, `postflight-followup.json`.
- Final portable archive `artifacts/phase3/uio66_qe_water_pair_v7_windows_v2.zip`; receipt `evidence/qe75-second-v7/portable-review-v2-receipt.json`; includes first full result and second full result with checksums. Earlier v6 AC failure and all original archives remain preserved.
- Final archive: **73 payloads verified**, 1,560,120,984 bytes; SHA256 `2e4baff609d4d834885756062ed3d26ab611e171796de450cb59e4ab5d1c4af3`. Final reviewed packaging completed at allocation **4653.638s (77m33.638s)**, within the original four-hour ceiling.
- **Next decision:** review the paired result, then consider authorizing **two paired 80/750-Ry density-cutoff checks** with other science fixed, actual grid verification and larger verified RAM. Predicted dense grid 243³; 12.005–13.017-GiB estimates exceed this laptop's 11-GiB cap. Compare paired ΔE shift to 2–3 meV and forces to 0.005–0.01 eV/Å; this would not establish wavefunction-cutoff/k-point convergence.
- No proposed study/extra geometry/UMA/refit launched. Phase 3 and numerical/physical/UMA accuracy remain unresolved.

---

## Historical records

# Fedora handoff — 2026-10-09, NEW second-geometry attempt v7 active

**Monitor this existing attempt only. Newly granted authorization is consumed.**

- User explicitly authorized one new second-geometry completion attempt after restoring AC. v6 remains a separate preserved AC-stopped failure with incomplete checkpoint. New clean scratch; no checkpoint reused.
- Exact same approved second input SHA256 `6e5208b721ce790b932a67ba103f135c28cfe2889b02fc2a2958614532be62b3`, 80/600 Ry and all prior scientific/numerical settings. Controller is byte-identical to v6; successful checks reused.
- Fresh launch gate: **12.457294 GiB available**, AC online, no prior QE/MPI workers, adequate disk; four physical cores/11-GiB hard/10-GiB high/zero job swap/96 tasks and sleep:idle inhibition verified. No apps closed.
- **Fixed allocation 07:30:05.863522–11:30:05.863522 UTC (ends 17:00:05 IST)**. Preparation/cleanup included; no reset or extension. Grace 11:10:05; external stop 11:24:50 plus 15s; final five minutes reserved.
- Worker `qe75-second-v7.service`; guardian `qe75-second-v7-guardian.service`; inhibitor `MOF-QE-second-v7` must cover cleanup. Finalizer `qe75-second-v7-finalizer.service` performs offline assessment/packaging only.
- Raw/status `local/qe75-second-v7/run01/`; evidence `evidence/qe75-second-v7/`; config `configs/qe75-second-v7.json` consumed.
- Offline assessor now selects terminal service status; cleanup permits a failed terminal unit only when cgroup is empty, while still requiring no workers/task inhibitor/override. Scientific acceptance unchanged.
- No accepted second result yet. Monitor to terminal, independently verify XML/text convergence, energy, 522 electrons, frozen structure, 127 forces, warnings and accounting. Only if valid compare DFT second-minus-first with archived UMA −0.041461080671410855 eV.
- Preserve all raw/partial files and Windows package, confirm cleanup, update handoff. No automatic retry/extra geometry/convergence calculation/UMA/refit; Phase 3 incomplete.

---

## Historical records

# Fedora handoff — 2026-10-09, SECOND geometry stopped on AC loss

**TERMINAL, unconverged; authorization consumed. No new calculation authorized.**

- Read `docs/UIO66_QE75_SECOND_V6_RESULTS.md`. One second-geometry attempt completed 10 SCF iterations and began 11; final error **9.281e-5 Ry** versus target 1e-8. Negative pseudocharge **0.3949 e**. No final XML/density/forces or JOB DONE.
- Fedora AC went offline at **03:28:27 UTC / 08:58:27 IST**; reviewed guard stopped workers within one second. Actual terminal exit **1**. Subsequent AC check also offline; no hardware-fault diagnosis inferred.
- Peak **9.237698 GiB**, zero job swap/high/max/OOM/task events; minimum host available **3.834984 GiB**. Runtime plus cleanup **46m18.525s**; original allocation through automatic package **47m30.346s**, within four hours. No reset/extension/retry.
- Scratch **511,898,448 bytes**, four wavefunction and four mixing files; **incomplete, invalid restart checkpoint**. All 21 raw hashes verified. No files deleted.
- No workers or task inhibitor remain; override removed, timers/guardian inactive. Worker systemd failed state retained as evidence, cgroup empty. No suspend. User closed Zen before launch; agent closed no applications.
- Automatic assessment correctly rejected convergence but mislabelled pre-stop running status as process success and failed-state cleanup as unverified. Corrections preserved separately in `evidence/qe75-second-v6/assessment-terminal-v2.json` and `partial-independent-audit.json`; original assessment/archive unchanged.
- Raw `local/qe75-second-v6/run01/`; evidence `evidence/qe75-second-v6/`. Corrected portable archive `artifacts/phase3/uio66_qe_water_pair_v6_windows_v2.zip`; receipt `evidence/qe75-second-v6/portable-review-v2-receipt.json`. Contains first valid result and second partial evidence, not two accepted SCFs.
- Corrected archive: **63 payloads verified**, 1,260,878,285 bytes; SHA256 `c9063813f8cce7648b57a8e45355432b01c37cabc1516b746f5c66e1703f279b`. Original archive remains unchanged.
- **No DFT second-minus-first comparison is valid.** First remains converged; archived UMA delta −0.041461080671410855 eV remains a separate reference.
- **Next: stable AC and new explicit bounded authorization for second-geometry completion.** This consumed attempt cannot be restarted automatically; incomplete checkpoint implies clean start unless a complete compatible checkpoint is separately verified.
- Paired 80/750-Ry density check is proposed only, subject to memory/grid review and separate authorization. No convergence study/UMA/refit/extra geometry; Phase 3 incomplete.

---

## Historical records

# Fedora handoff — 2026-10-09, SECOND geometry active

**Monitor this single attempt only. Authorization consumed; no retries.**

- First independent review passed. User closed Zen; fresh launch available RAM **12.725 GiB**, AC online, no existing QE/MPI workers. No applications closed by agent.
- Second frozen target `uio66_110111_H2O_s28_f0.005_complex`; exact archived coordinates, same 80/600-Ry scientific/numerical protocol as first, no scratch reuse. Input SHA256 `6e5208b721ce790b932a67ba103f135c28cfe2889b02fc2a2958614532be62b3`.
- Actual four physical cores, 11-GiB hard/10-GiB high guard/zero job swap/96 tasks and temporary sleep:idle block inhibitor verified.
- Fixed allocation **02:41:31.640757–06:41:31.640757 UTC** (ends **12:11:31 IST**). Grace at 06:21:31; external stop 06:36:16 plus 15 seconds; final five minutes reserved. Never reset or extend. Includes preparation and cleanup.
- Worker `qe75-second-v6.service`, guardian `qe75-second-v6-guardian.service`, inhibitor `MOF-QE-second-v6`; keep inhibitor owner through cleanup.
- Raw/status `local/qe75-second-v6/run01/`; controls/evidence `evidence/qe75-second-v6/`; config `configs/qe75-second-v6.json` consumed. Controller changed only target/input pin/provenance; successful prior control checks reused.
- Monitor to terminal, preserve all evidence, independently assess second SCF/text/XML/geometry/127 forces/resources, calculate second-minus-first DFT versus archived UMA −0.041461080671410855 eV if valid. No second result or accepted partial energy claimed yet.
- Finalize Windows package, verify workers stopped and temporary controls removed. No extra geometries, cutoff study, UMA or refit authorized. Phase 3 remains incomplete.

---

## Historical records

# Fedora handoff — 2026-10-09, independent review passes; second geometry held for RAM

**ONE second frozen-water attempt conditionally authorized; UNUSED.**

- Independent review: `docs/UIO66_QE75_FIRST_INDEPENDENT_REVIEW_V6.md`. Full output/XML, all 127 total forces with atom mapping/units, convergence, energy, geometry and accounting agree with the first-result report. All 85 archive payloads and 27 local raw hashes verified. No substantive blocker found.
- Fresh host screen: AC connected, 210.289 GiB disk free, no QE/MPI workers. **Available RAM 10.861282 GiB < required 12 GiB** (shortfall 1.138718 GiB). Zen closure permission requested; no apps/services closed.
- No second-run allocation, inhibitor or scientific worker started. Start allocation before second-run preparation once resource hold is resolved. Existing first-run authorization remains consumed.
- Second target `uio66_110111_H2O_s28_f0.005_complex`: exact sealed geometry/potentials and same first-run 80/600-Ry protocol, conv_thr=1e-8, beta=0.3, CG/mixing4/diskhigh. One clean attempt; four physical cores, 11-GiB hard/10-GiB high guard/zero job swap/96 tasks; four hours including preparation and cleanup; no retry/extension.
- Reuse unchanged successful controller checks; inspect only target/input/config changes. Fresh AC/RAM/disk/workers and temporary sleep inhibition required before launch. No further scientific confirmation needed when conditions pass.
- After second result, independently verify and compare second-minus-first DFT with archived UMA −0.041461080671410855 eV. No DFT difference available yet.
- Offline evidence `evidence/qe75-first-independent-review-v6/`; supplemental Windows audit `artifacts/phase3/uio66_qe_first_independent_review_v6.zip`. Original full review ZIP remains intact.
- Proposed paired higher-density cutoff study requires separate authorization/resources; no convergence study/UMA/refit/Phase 3 completion.

---

## Historical records (superseded where noted)

# Fedora handoff — 2026-10-09, first 600-Ry SCF converged

**TERMINAL; authorization consumed. No more calculations authorized.**

- Read `docs/UIO66_QE75_FEDORA_COMPLETION_V5.md`. One clean first-geometry SCF converged in **16 iterations**, XML error **7.7747e-9 Ry** below 1e-8. Text/XML energy agrees; 522 electrons, frozen 127-atom geometry/cell and all five potentials verified. No 625-Ry checkpoint reuse.
- Energy −3003.62393554 Ry; 127 finite total forces, max norm 0.164180 eV/Å (O95), RMS 0.083462 eV/Å. Final negative pseudocharge **0.3938 e**, monitored and still subject to expert interpretation. No final diagonalization errors.
- Peak **9.253384 GiB**, job swap 0, no high/max/OOM/task events. Four physical cores / 11-GiB hard / 10-GiB high / 96 tasks retained. Runtime through cleanup **70m21s**, fixed allocation through original automatic package **1h58m38s**, within four hours. Scratch 830,566,191 bytes retained; minimum host available 1.354 GiB.
- Workers stopped, inhibitor released, runtime override removed, timers inactive; no suspend recorded. Follow-up host check confirms cleanup. No apps closed.
- Automatic force parser incorrectly counted verbose component tables (1016 rows). Separately versioned offline parser selects 127 total forces and matches XML. Original failed assessment and archive retained; no criteria/science changed and no new calculation.
- Final assessment: `evidence/qe75-fedora-completion-v5/launch02/assessment-v2.json`; raw `local/qe75-fedora-completion-v5/run01/` (27 hashes reverified).
- Corrected portable package: `artifacts/phase3/uio66_qe600_completion_v5_review_v2.zip`; receipt `evidence/qe75-fedora-completion-v5/launch02/portable-review-v2-receipt.json`. Original package and paired 600/625 review retained.
- All 85 packaged payloads verified. ZIP SHA256: `c8951afe5281dd5bedd3f47d85c26b53c10bfe8df316b51e38e373e9616ae53e` (779,992,174 bytes); adjacent `.zip.sha256` provided.
- **Next: independent assessment of this first converged result**, including negative pseudocharge/forces. SCF convergence is not cutoff/physical/UMA validation. Phase 3 incomplete; no second geometry, convergence study, UMA, refit or retry authorized.

---

## Historical records (superseded)

# Fedora handoff — 2026-10-08, ONE600-Ry completion attempt active

**Monitor existing v5 attempt ONLY. Authorization consumed. No retries.**

- User supplied provisional reviewer recommendation to continue first frozen
  geometry at80/600Ry; accuracy remains unproven. Input exactly matches archived600Ry
  (PBE-D3BJ,neutralnspin1,fixedoccupations,conv_thr1e-8,mixing_beta0.3,CG,mixing4,diskhigh).
- Cleanstart:600RySCFcheckpoints incomplete;625Rycheckpoint excluded. No geometry/PPchanges.
- Actual fresh checks passed:12.662GiBRAMavailable,AConline,noexistingQE/MPIjobs;
  fourphysicalcores,11GiBhard/10GiBhigh/zero job swap/96tasks andsleepinhibitor verified.
- **Immutable deadline18:54:38.654980UTC (00:24:38IST nextday)** from start14:54:38UTC.
  Preparation andACwaiting are included. GracefulEXIT18:34:38UTC;externalstop18:49:23UTC
  plus15s;workersgoneby18:49:38UTC;final5minreserved. Never reset or extend.
- Worker `qe75-completion-v5.service`;guardian `qe75-completion-v5-guardian.service`;
  inhibitor `MOF-QE-completion-v5` stays throughcleanup. No4iteration diagnosticstop.
  Nonzero negativecharge alone is not a stop rule; fatal/resource rules retained.
- Raw/status/resources: `local/qe75-fedora-completion-v5/run01/`.
  Active runtime evidence: `evidence/qe75-fedora-completion-v5/launch02/`.
  Root audit,controllerreview,pairedpackage receipt,allocation and earlierACfailure:
  `evidence/qe75-fedora-completion-v5/`. First invocation launched no scientific workers.
- Reviewer pairedZIP `artifacts/phase3/uio66_qe_review_600_625_v1.zip` contains12files
  withchecksums; verified evidence separated fromprovisionalinterpretation.
- No convergence/acceptedenergy/finalforces claimyet. Onterminal independentlyassess
  exactthreshold,text/XMLenergy,522electrons,geometry/cell,127finiteforces,finaldiag
  warnings andresourceevents. Preservealloutputs/checkpoints/accounting inportableZIP.
- Do not rerunlaunchers,startsecondgeometry,convergencestudy,UMA/refitorexpansion.
  Confirmworkerstop,inhibitorrelease/overrideremoval andupdatehandoffaftercompletion.

---

## Historical records

# Fedora handoff — 2026-10-08, 600-Ry completion held at AC gate

**New ONE80/600-Ry completion authorization is UNUSED. No QE launched.**

- Reviewer recommendation is the provisional interpretation supplied in the user's
  latest message. No separate reviewer document was found. Local verification and
  that interpretation are explicitly separated in the portable review package.
- Actual600/625inputs, complete stdout/stderr and available625XML agree with the
  prior diagnostic evidence.25+29rawhashes verified; no material discrepancy.
  XML coordinate/cell differences from frozen geometry are below4e-15angstrom.
- No compatible600RySCF checkpoint: v2/v3 lack completeXML/density; initialization
  output is not anSCFrestart. Clean start selected;625checkpoint excluded.
- Reviewer archive `artifacts/phase3/uio66_qe_review_600_625_v1.zip` contains the two
  inputs, fullstdout/stderr, availableXML, explicit600XMLabsence, pairedreport,
  verification,reviewstatus andchecksums. SHA256:
  `2bf64fd08900fb3b50ce7dc273b771ef56778a2c58872d813eaa7a0f3fdd96c8`.
- New reviewed controller `scripts/qe75_completion_v5.py`; config
  `configs/qe75-fedora-completion-v5.json`. Exact archived600Ry input selected:
  no scientific/input differences, max_seconds12948 retained. The4iteration
  diagnostic stop is removed; negativecharge trajectory is logged and does not
  trigger stopping by itself. Fatal/resource stop rules remain unchanged.
- Prior successful controls reused after AST comparison of deadline/resource/
  inhibitor/worker functions. Narrow changed behavior checked; no newdummy orQE.
- Fixed allocation started14:54:38.654980UTC and ends2026-10-08T18:54:38.654980+00:00.
  Grace+13200s,externalstop+14085s,killby+14100s,final300sreserve. Do not reset.
- **Final host gate failed: AC disconnected.** Guard stopped before work-directory
  staging or worker launch. Temporary inhibitor released; no override created.
  Earlier snapshot:12.541GiBavailable,212.821GiBdiskfree. No applications closed.
- Evidence `evidence/qe75-fedora-completion-v5/`: preflight-evidence-audit.json,
  review-package-receipt.json,controller-review.json,controller-changes.diff,
  result.json,inhibitor-release.json,hold-summary.json and allocation receipt.
- **Next:** connect charger and resume at fresh AC/RAM/disk/jobs/inhibitor gate.
  Do not repeat completed package/scientific/controller verification when unchanged.
  Existing wrapper's exclusive invocation marker must be preserved; continuation
  requires distinct invocation evidence within the remaining original allocation,
  not a reset/replay. No scientific launch authorization has been consumed.
- No600SCFresult yet; old625diagnostic remains unconverged. No retry,secondgeometry,
  highercutoff,UMA/refit/design expansion. Phase3 remains incomplete.

---

## Historical records

# Fedora handoff — 2026-10-08, 625-Ry diagnostic finished

**TERMINAL: four completed SCF iterations, unconverged. Authorization consumed.**

Read `docs/UIO66_QE75_RHO625_RESULTS_V1.md` for the comparison and accounting.

- Initial and iterations1–4 negative pseudocharge match the archived600Ry values
  at printed precision:0.3659,0.3741,0.3836,0.3887,0.3940 electrons.
  New SCF errors20.00912607,2.51084927,0.66475088,0.26218300Ry;target1e-8 unmet.
- Actual denseFFT225³ with2,022,032G; smooth160³ with741,079G. Same startingcharge
  and457randomizedatomicwfcs. Only scientific change ecutrho600→625; shared frozen
  geometry,UPFs,build and other settings preserved;max_seconds12948→1350 is control.
- Peak9.634495GiB,zero job swap,no high/max/OOM events,minhostavailable3.558907GiB.
  Four physical cores/11GiBhard/10GiBhigh/96tasks retained. Scratch544,069,813bytes.
- QEwall17m15.19s;MPIlaunchthroughworkercleanup17m18.019s. Fixed allocation
  10:09:41.465532–10:39:41.465532UTC; automatic cleanup/inhibitorrelease25m11.895s,
  final independent host verification29m49.699s. No deadline reset or extension.
- Scheduled EXIT requested at+1500s. Fourth iteration finished, then QE stopped
  by user request, exit0/JOBDONE. No fifth iteration, convergence or final forces.
  XMLconvergencefalse/4steps/exit_status255. No partial energy accepted scientifically.
- XML,charge density,PAW,wavefunction,mixing and restart files retained;29rawfiles
  hashed. Presence of files is not certification of restart compatibility.
- Adapted dummy02 passed31.075s (deadline/three process groups/partials/inhibitor
  cleanup). Real sleep:idle block inhibitor remained through worker cleanup and
  was released. No workers/taskinhibitors/runtimeoverrides remain;timersinactive;
  no suspend/hibernate journal entries. No apps closed or normal settings changed.
- Evidence `evidence/qe75-rho625-run02/`: assessment.json,postflight.json,
  result.json,controller-review.json,raw-file-hashes.json,XML summary and journals.
  Raw `local/qe75-rho625-v1/run02/`; successful dummy evidence
  `evidence/qe75-rho625-controller-dummy02/`. `configs/qe75-rho625-v2.json` consumed.
- **Next recommendation:** get focused QE/pseudopotential expert review of the
  paired600/625Ry evidence before authorizing longerSCF or a larger-grid test.
  Unchanged printed charge at the sameFFT does not exclude cutoff/grid sensitivity.
  This result establishes limited early-SCF resource feasibility, not accurate
  energies, fullDFT completion,UMA accuracy or completion ofPhase3.
- No retry,secondgeometry,additionalQE/UMA/refit/design expansion authorized.
  Prior preparation-only hold receipts and all historical evidence preserved.

---

## Historical records

# Fedora handoff — 2026-10-08, ONE625-Ry diagnostic active

**Monitor existing attempt ONLY. Authorization consumed; no retries.**

- Raw: `local/qe75-rho625-v1/run02/`; evidence: `evidence/qe75-rho625-run02/`.
- Fixed total allocation10:09:41.465532–10:39:41.465532UTC; do not reset/extend.
  Graceful EXIT by10:34:41UTC or fourth completed SCF error report, external stop
  10:37:26UTC plus15s, workers gone by10:37:41UTC, final2min reserved for cleanup.
- Adapted dummy02 passed31.075s: fixed deadline despite paused monitor, three
  separate process groups killed, logs retained, inhibitor released. Review receipt
  pins the exact controller. Latest fresh AC/RAM/disk/jobs/inhibitor checks passed.
- Four physical cores,11-GiB hard/10-GiB high,zero job swap,96 tasks enforced.
  Clean input80/625Ry; ecutrho is sole scientific change; max_seconds1350 execution control.
- Worker `qe75-rho625-v2.service`; guardian `qe75-rho625-v2-guardian.service`;
  task-owned sleep:idle block inhibitor `MOF-QE-rho625-v2` remains through cleanup.
- `configs/qe75-rho625-v2.json` approval consumed. Monitor status/resources/stdout;
  on terminal state compare initial and up to first4completed iterations to archived600Ry.
- No accepted partial energy or convergence/physical-accuracy claim. No second
  geometry, higher cutoffs, fullpilot, UMA/refit. Do not relaunch this controller.

---

## Historical records

# Fedora handoff — 2026-10-08, memory recovered; controller check held

**RAM gate passes. One 625-Ry authorization remains UNUSED; no QE launched.**

- Host process inspection confirms Zen is absent. Largest remaining applications
  include Codex/Astra, GNOME Shell, GNOME Software and Ptyxis terminal. No apps,
  services or cache were stopped/cleared; no permission to close anything was needed.
- Latest host snapshot: **12.640 GiB available**,14.936 GiB total;213.576 GiB disk
  free;8-GiB zram unused. RAM recovery occurred without assistant termination actions.
- Controller drafted in `scripts/qe75_rho625_v1.py` with dedicated configuration
  `configs/qe75-rho625-v1.json`. Execution is explicitly blocked by
  `controller_reviewed_and_dummy_passed=false`; review and integrated test unfinished.
- Adapted non-QE dummy invocation aborted at **AC disconnected** before launching
  workers. A subsequent snapshot read AC connected again. This transient must be
  resolved before a stable powered allocation; do not represent the dummy as passed.
- The task-owned sleep:idle inhibitor was acquired and released through the failure
  cleanup. Host verification: no task inhibitors, runtime override, QE/MPI workers.
- The preparation allocation began09:46:07.042827UTC with an unchanged30-minute
  ceiling; preparation terminated without any scientific launch. No deadline reset,
  retries or consumed scientific authorization. Retain the original allocation evidence.
- Evidence: `evidence/qe75-rho625-run01/` (host processes/resources/result/allocation),
  `evidence/qe75-rho625-controller-dummy01/` (AC failure and inhibitor cleanup).
- **Next:** keep AC reliably connected and lid open, complete controller review and
  its short integrated deadline/cleanup test, and recheck fresh resources before any
  scientific launch under the unused conditional authorization. Limits and scientific
  scope remain those in `docs/UIO66_QE75_RHO_DIAGNOSTIC_PLAN_V1.md`.
- No new SCF data, cutoff comparison, accepted energy or performance claim.

---

## Historical records

# Fedora handoff — 2026-10-08, authorized 625-Ry diagnostic held for RAM

**ONE 80/625-Ry diagnostic is conditionally authorized; authorization UNUSED.**

- Read `docs/UIO66_QE75_RHO_DIAGNOSTIC_PLAN_V1.md` for the unchanged scope and limits.
  Its earlier unapproved status is historical; the user has now approved one attempt.
- Early prerequisite check failed: **11.852 GiB available RAM < 12 GiB**
  (deficit 0.148 GiB). Physical total 14.936 GiB.
  Cache is already reflected in MemAvailable; no caches dropped. System zram unused.
- AC connected; 213.578 GiB persistent disk free; no QE/MPI workers.
- No applications/services stopped, new inhibitor/override created, scientific
  allocation started, or QE/dummy workload launched. Earlier evidence preserved.
- Input identity verified: only scientific difference `ecutrho=600` → `625`;
  execution-control difference `max_seconds=12948` → `1350`. Geometry/UPFs unchanged.
- Controller adaptation/review and its fresh dummy test remain unfinished prerequisites;
  work stopped at the explicit failing RAM gate. Previous component checks do not
  substitute for the requested adapted-controller test.
- Evidence: `evidence/qe75-rho625-resource-hold-20261008T094326Z/preflight.json`, process snapshot and hashes.
- **Next:** free at least the measured RAM deficit plus margin by closing chosen user
  applications, then recheck resources. Do not close apps without permission. Complete
  and review the controller, run its short dummy test, verify initialization choices,
  then acquire/verify the run inhibitor and perform final gates before ONE attempt.
  Keep AC connected and lid open. Existing authorization persists if prerequisites pass.
- Preserve four physical cores,11-GiB hard/10-GiB high,zero job swap,96 tasks and1800s
  total including preparation/cleanup. No automatic retry, extension or new calculations.

---

## Historical records

# Fedora handoff — 2026-10-08, numerical plan and control checks

**No QE/UMA launched. Pending conditional authorization remains unused.**

Read `docs/UIO66_QE75_RHO_DIAGNOSTIC_PLAN_V1.md` for aligned diagnostics,
source/UPF/FFT review, memory estimates and non-QE execution-control evidence.

- Initial negative pseudocharge 0.3659 electrons; SCF1–4:0.3741,0.3836,0.3887,0.3940.
  SCF error falls20.0090→2.51087→0.664758→0.262188Ry. Increase alone is not divergence;
  neither0.1 nor0.522 is an acceptance rule. Numerical accuracy remains unresolved.
- Smallest proposal: ONE clean80/625Ry probe against archived80/600 first4iterations.
  `plans/qe75-rho-diagnostic-v1/` contains exact inputs, commands, hashes and expert
  question. Only scientific variable is ecutrho; thresholds and frozen model retained.
  No new baseline run. Proposal approvalfalse; this cutoff change needs separate approval.
- Predicted625 densityGcount+6.31%, same225³FFT. It tests reciprocal cutoff sensitivity;
  a null result does not settle real-space-grid effects. No accepted partial energy.
- Peak estimate9.71–9.90GiB, not a guarantee;11GiBhard/10GiBhigh/zero swap/96tasks,
  four physical cores retained.650 crosses high guard;750 exceeds hard cap in estimates.
  Proposed1800s total incl setup/cleanup, no allocation receipt created.
- Independent non-QE controls completed: deadline, stopped-controller cleanup,
  simulated post-deadline resume/refusal; all partial logs and immutable receipts retained.
  Fedora's global timeout-abort drop-in required a temporary unit-specific kill override.
  Effective kill/SIGKILL and cgroup limits verified. Final v3 tests passed; prior failures
  preserved under `evidence/qe75-control-checks-v1/` and `-v2/`.
- Task-owned sleep:idle block inhibitor verified through cleanup and released. No dummy
  or QE/MPI workers, runtime overrides removed. No apps closed, cache dropped, or normal
  Fedora power/service settings changed. No deliberate suspend was tested.
- Evidence: `evidence/qe75-control-checks-v3/` and
  `evidence/qe75-rho-diagnostic-plan-v1/`; prior raw/package evidence remains unchanged.
- Final resource snapshot:14.936GiBphysical,10.594GiBavailable,213.539GiBdiskfree,
  systemzramunused, **AC disconnected**. Proposed12GiBavailable/AC gates currently fail.
- **Next decision:** review and explicitly approve or decline the625Ry diagnostic.
  Before any launch, adapt/review the scientific guardian with the verified control fix,
  connect AC, keep lid open and recheck resources/hashes. Existing v3 launcher must not
  be reused unchanged. Focused expert question prepared but not sent.
- No scientific authorization consumed; no four-hour attempt started. Phase3 incomplete;
  no second geometry, cutoff-convergence claim, UMA, refit or design expansion.

---

## Historical preflight record (superseded by the update above)

# Fedora handoff — 2026-10-08, v4 preflight hold

**No new QE attempt launched. New conditional authorization remains unused.**

Read `docs/UIO66_QE75_FEDORA_V4_PREFLIGHT.md` before execution work.

- First prerequisite has not cleared: integrated negative pseudocharge rises
  0.3659→0.3741→0.3836→0.3887→0.3940electrons through the initial state and four SCF
  iterations. QEguide flags values around0.1; starting-charge FAQ uses a relative
  heuristic0.001*522=0.522. The latter is not exceeded. These differing heuristics
  do not prove invalidity or establish harmlessness of persistent/increasing values.
- Hold launch for numerical review under the user's prerequisite. No changes to
  scientific settings, frozen geometries, UPFs or build; no added DFT diagnostic runs.
- All25v3rawfiles still hash-match. Evidence/source analysis and host snapshot:
  `evidence/qe75-fedora-v4-preflight/`; previous evidence remains intact.
- Host snapshot: AConline,noQE/MPIworkers,zero systemzram usage,~213.61GiBdiskfree.
  No apps/services stopped and no power settings changed.
- No temporary task inhibitor acquired; none needs release. Sleep/idle inhibitor
  lifetime/release and dummy deadline/cleanup/interruption tests remain unperformed.
  They are mandatory before a later run; don't claim corrected controls yet.
- No new allocation timestamp or run directory. Latest conditional one-attempt
  permission is UNUSED; older v3/v2 permissions remain consumed.
- Next decision: resolve the negative-density interpretation with numerical review,
  then finish sleep/dummy/resource prerequisites before considering the authorized
  unchanged first geometry. No second geometry, convergence study,UMA/refit/expansion.

---

## Previous terminal and historical records

# Fedora handoff — 2026-10-08, after interrupted completion attempt

**TERMINAL: unconverged; no accepted energy/forces. Authorization consumed. No workers remain.**

- Details: `docs/UIO66_QE75_FEDORA_COMPLETION_V3.md`.
- ONE clean attempt on first frozen complex; previous checkpoint had no XML/density.
  No prior scratch reused. Same QE7.5/UPFs/science/CG/mixing4/diskhigh/fourphysicalcores.
  11GiBhard/10GiBhigh,zero cgroupswap,96tasks; no applications stopped this turn.
- Four iterations completed; fifth started. Estimated SCF errors(Ry):20.00902028,
  2.51087335,0.66475787,0.26218816; threshold1e-8 unmet. No failed-diagonalization
  warnings; negative-density diagnostics persisted (last0.3940).
- Peak9,805,496,320B=9.132080GiB;swap0;noOOM/limit events. Scratch486,793,968B
  (0.453362GiB). Awake service1096.548s; MPIexit1/controllerexit0 is not SCF success.
- **Four-hour real wall budget was not met across automatic suspend.** Allocation
  began01:38:36IST; fixed deadline05:38:36IST. Fedora gsd-power suspended the host
  at02:00:35; it resumed09:21:32. Both stop timers fired on resume and the controller
  stopped MPI immediately. Actual allocation elapsed7h42m56.580s (mostly asleep).
  No deadline reset/extension or retry. No temporary sleep inhibitor had been installed.
- No JOB DONE/convergence/XML/charge-density/final forces. Eight partial data files
  plus EXIT retained; incomplete checkpoint, not suitable for a supported restart.
- `configs/qe75-fedora-completion-v3.json` approvalfalse/consumed. Unitinactive/dead,
  cgroupgone,recordedworkerPIDsabsent,bothstop timersinactive. Do not rerun v3.
- Raw/status/result/scratch: `local/qe75-fedora-completion-v3/run01/`.
  Evidence: `evidence/qe75-fedora-completion-v3/`, especially `allocation.json`,
  `prior-output-review.json`, `postflight.json` (system/job journals),
  `suspend-analysis.json`, `assessment.json` and hash manifests.
  All evidence/raw paths are Git-ignored; preserve separately. Previous21v2rawfiles
  and all140sealedpackagefiles remain unchanged. Existing source/build unchanged.
- **Next decision:** a separately authorized first-geometry attempt would need a
  verified temporary sleep inhibitor/awake allocation before launch. No new run,
  second geometry, convergence study,UMA/refit/expansion is authorized. This result
  is not ready for independent scientific assessment; fullSCF/finalforces/runtime,
  cutoff convergence and physical accuracy remain unverified. Phase3 incomplete.

---

## Historical handoffs (superseded)

# Active first-complex completion attempt — 2026-10-08 IST

**Monitor only. One authorized clean attempt is running; its launch authorization is consumed.**

- Current details: `docs/UIO66_QE75_FEDORA_COMPLETION_V3.md`.
- Unit `qe75-completion-v3.service`; four cores,11GiBhard,zero swaps,96tasks.
- Fixed allocation ends **2026-10-08 05:38:36 IST (00:08:36 UTC)**, including finalization.
  QE graceful stop scheduled05:18:36IST; external stop05:33:21IST plus15s shutdown.
  Never reset or extend this deadline; no retry/second geometry/UMA/expansion.
- Periodic state: `local/qe75-fedora-completion-v3/run01/status.json` and `resources.jsonl`.
  Preserve input/stdout/stderr/result/scratch and `execution-started.json` there.
- Allocation/source/restart review/timer receipts: `evidence/qe75-fedora-completion-v3/`.
- Prior v2 output lacked XML/density/clean restart; no prior scratch reused.
- Await terminal output, verify convergence/identity/hashes/energy/forces, confirm no workers,
  then update this handoff. No scientific completion claim yet.

---

## Historical handoff

# Fedora handoff — 2026-10-07, after ONE SCF feasibility test

**Authorization consumed; execution disabled. Two iterations completed, third started;
no converged energy or final forces accepted. Phase3 remains incomplete.**

- Read `docs/UIO66_QE75_FEDORA_FEASIBILITY_V2.md` for configuration, source audit,
  exact commands, accounting, limits and uncertainty. Older initialization details below
  are historical; this was a separately authorized SCF resource test.
- Zen closed gracefully with explicit permission; no other applications/services stopped
  or restarted. Available RAM rose 10.001→12.137 GiB (~2.136 GiB recovered).
  Total physical RAM14.936GiB; launchavailable12.345GiB; diskfree213.669GiB.
  Cache was not dropped. System zram is not extra physical RAM.
- QE7.5 existing build reused. Sealed ZIP/receipt and all140files reverified;
  archived science, source, build and previous config unchanged.
- New `configs/qe75-fedora-feasibility-v2.json` / `scripts/qe75_feasibility_v2.py` /
  `scripts/launch_qe75_feasibility_v2.sh`: four ranks on distinct physical cores,
  one compute thread, CG, mixing_ndim4, disk_iohigh, verbosityhigh, softmax540s.
  Exact geometry, UPFs,80/600Ry,PBE-D3BJ2body,Gamma,charge/spin and convergence preserved.
- Actual enforced limits:11GiBhard/10GiBhigh,zero cgroupswap,96tasks,
  service585s+15sshutdown; monitorstop570s. About3.936GiB totalphysicalreserve.
- Test reached two completedSCFiterations and startedthird; stoppedbytime at570.999s
  (service571.164s). Peak10,000,793,600bytes=9.313965GiB;swap0;noOOM/limit events.
  Minimum sampledhostavailable3.791GiB. Scratchgrew0→436,585,008bytes(0.406601GiB).
  MPIexit1; controller/serviceexit0 means monitor completion, NOT SCF success.
- Workersallgone,serviceinactive,cgroupremoved. Zenstaysclosed.
  Postflightavailable12.635GiB; systemzram49,152bytesoutsideQE; systemswapunchanged.
- All raw/partial outputs retained in `local/qe75-fedora-feasibility-v2/run01/`.
  Supporting records/assessment/hashes in `evidence/qe75-fedora-feasibility-v2/`.
  Both directories are Git-ignored; copy/preserve separately.
- Both old initialization approval and new feasibility approval are false. Keep
  `local/qe75-fedora-feasibility-v2/run01/execution-started.json`; never retry this run.
- **Conclusion:** closing Zen allowed early SCF to fit safely. Full convergence time,
  later peak memory, final forces and second geometry are unverified. No repeated
  initialization is needed. Next execution requires a separate reviewed completion
  allocation and authorization; no automatic continuation or increase in limits.
  UMA accuracy, proton correspondence and cutoff convergence remain unresolved.

---

## Historical handoff (unchanged)

# Fedora handoff — 2026-10-06, after initialization 01

**ONE authorized initialization completed; authorization consumed. No SCF/UMA.**

- Original ZIP/receipt remain in `artifacts/`, byte-unchanged. ZIP SHA256 matches
  `4ea11e147c529d8b893d2131c06812ec5978b24f0c7d8905c116c22e4e6d0554`.
  All 140 files verified in fresh
  `artifacts/phase3/uio66_frozen_dft_v2_qe75_fedora_verified01/`.
- Existing QE 7.5 build reused: `local/qe75-fedora-v1/build/bin/pw.x`.
  No installation/package rebuild. Source and executable hashes rechecked.
- `nstep=0` source branch returns before SCF. Actual XML confirms nstep=0,
  zero SCF steps, internal status255 and no energy/forces. Process exit0 is expected
  for this build's default STOP. Scientific parser rejects the incomplete result.
- Four ranks, one thread each; unchanged 8-GiB cap, zero swap, 600-second ceiling.
  Preflight had 10.62 GiB available RAM and ~213.52 GiB persistent disk free.
  Zen web processes were optional memory consumers; no applications terminated.
- 127 atoms, 522 electrons, 261 bands; 80/600 Ry, Gamma, PBE-D3(BJ) two-body.
  Dense225³/1,902,004 G-vectors; smooth160³/741,079 G-vectors.
- **QE estimates >12.67 GiB total dynamical RAM**, exceeding the current 8-GiB cap.
  Measured initialization peak0.7905GiB, swap0, noOOM; service3.836s, QE0.24s.
  Initialization does not measure full-SCF RAM/runtime. Final wavefunction dimension
  remains uninitialized (`npwx=0`). Retained scratch44,512 bytes is only init XML.
- Both flags in `configs/qe75-fedora-v1.json` are false; authorization consumed.
  Keep `local/qe75-fedora-v1/smoke01/execution-started.json`. No retry/limit increase.
- Next decision: review a larger verified RAM allocation and full-SCF launcher.
  No full SCF authorized; do not lower cutoffs or alter the frozen model.
  Phase3, UMA accuracy, numerical convergence and proton correspondence unresolved.

Results and evidence detail: `docs/UIO66_QE75_FEDORA_INIT01_RESULTS.md`.
Evidence/accounting: `evidence/qe75-fedora-init01/`.
Raw input/output and all scratch: `local/qe75-fedora-v1/smoke01/`.
Both evidence directories are ignored by Git; retain/copy separately.
Offline assessor: `scripts/assess_qe75_fedora_init_v1.py` (no QE launch).
The existing graph was not rebuilt and does not yet index these results.
