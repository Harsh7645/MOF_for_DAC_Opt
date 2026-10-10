# Second frozen-water 80/600-Ry attempt v6 — terminal AC stop

**UNCONVERGED. Authorization consumed. No automatic retry or further calculation authorized.**

The first frozen result remains independently verified and converged. The single second-geometry attempt was stopped by the reviewed AC guard; it did not produce a scientifically accepted energy or final forces. User messages saying “continue” were handled as continuation of monitoring/offline finalization, not authorization to restart a consumed attempt.

## Preparation and exact protocol

The independent first-result review passed (`docs/UIO66_QE75_FIRST_INDEPENDENT_REVIEW_V6.md`). The user closed Zen; available RAM at the final second-run gate was 12.724937 GiB, AC online, no existing workers and sufficient persistent disk (~210.3 GiB). The agent closed no applications/services.

Second target: `uio66_110111_H2O_s28_f0.005_complex`. Clean scratch, exact sealed second coordinates/cell and potentials. Input SHA256 `6e5208b721ce790b932a67ba103f135c28cfe2889b02fc2a2958614532be62b3`; sealed baseline SHA256 `d1bb4cb427fb9acde18bfe1139e0b7b9b71b8990af5ad460e9126acf1c8a0e56`. Same first-result scientific/numerical settings: 80/600 Ry, Gamma, PBE-D3(BJ) two-body, neutral nspin=1, fixed occupations, conv_thr=1e-8 Ry, beta=0.3, CG/mixing_ndim=4/disk_io=high/verbosity=high/max_seconds=12948. No checkpoint was reused. Input differs from the first only by the second frozen coordinates and target prefix; common cell and all other protocol fields match.

Successful controller checks were reused after AST comparison: only input path/hash, target prefix and provenance text changed. Four physical cores were verified and bound; hard memory 11 GiB, high guard 10 GiB, job swap 0 and tasks 96 enforced. Sleep:idle block inhibition was verified through cleanup. No boot/system power settings changed.

## Actual termination and accounting

- Fixed allocation: **2026-10-09 02:41:31.640757–06:41:31.640757 UTC** (08:11:31–12:11:31 IST), preparation/cleanup included; never reset or extended.
- MPI started 02:42:09 UTC (08:12:09 IST). Fedora reported **AC offline at 03:28:27.673264 UTC (08:58:27 IST)**. The guard invoked whole-unit stop; workers were gone by 03:28:28.510772 UTC. Subsequent read-only inspection also reported AC offline. This records observed power state, not a diagnosis of hardware failure.
- **10 completed SCF iterations; iteration 11 started.** Last estimated error **9.281e-5 Ry**, above 1e-8. No convergence message, JOB DONE, final total-force table, XML or charge density.
- Final service status **exit-code, exit 1** after the AC stop. No preceding fatal QE or diagonalization warning was found. Stopping was caused by AC loss, not negative pseudocharge, OOM or numerical acceptance criteria.
- Peak memory **9.237697601 GiB (9,918,902,272 bytes)**; zero job swap; zero high/max/OOM/task events. Maximum tasks 15; minimum host available RAM **3.834984 GiB**.
- MPI launch through worker cleanup **2778.525 s (46m18.525s)**. Allocation through cleanup **2816.870 s (46m56.870s)**; automatic Windows package completed at **2850.346 s (47m30.346s)**, within four hours. Later offline review/corrections did not extend the scientific allocation.
- Scratch retained: **511,898,448 bytes (~0.477 GiB)**, four distributed wavefunction and four mixing files. **Incomplete restart checkpoint**: no `data-file-schema.xml` or `charge-density.dat`. Do not restart from these files without a valid complete compatible checkpoint; none was found here.
- All **1331 samples** retained sleep/idle inhibition; only the final sample reported AC false. No suspend/hibernate journal entry during the allocation. Workers, guardian and timers stopped; empty worker cgroup, inhibitor released, override removed. The worker unit retains its systemd **failed** status as evidence; that does not mean workers remain.

## SCF/negative-pseudocharge trajectory

|Iteration (0 initial)|Negative pseudocharge, electrons|Estimated SCF error, Ry|
|---:|---:|---:|
|0|0.3664|—|
|1|0.3747|20.01274737|
|2|0.3843|2.51620285|
|3|0.3895|0.66025771|
|4|0.3950|0.25233622|
|5|0.3947|0.08673524|
|6|0.3955|0.00914888|
|7|0.3954|0.0052682|
|8|0.3953|0.00111169|
|9|0.3951|0.0005048|
|10|0.3949|9.281e-05|

The SCF errors decreased throughout the ten completed iterations, and negative pseudocharge peaked at 0.3955 then fell to 0.3949 electrons. This partial trend establishes neither eventual convergence nor accurate energies. Persistent pseudocharge is not automatically accepted or rejected. No force interpretation is possible for this attempt because final forces were not produced.

## Independent evidence audit and assessment corrections

All **21 raw-file hashes** match the preserved automatic manifest; the Windows archive checksum was independently reverified. Actual stdout reports 127 atoms, 522 electrons, 80/600 Ry and dense 225³ / 1,902,004 G vectors, smooth 160³ / 741,079 G vectors. The archived input coordinates/cell and five UPF hashes pass. With no final XML, final text/XML energy/geometry/force validation cannot be completed; no accepted result is inferred from input checks.

The automatic assessor correctly rejected the unconverged output, but two metadata flags needed correction:

1. Its `process_and_resource_success` flag used `ExecMainStatus=0` from the service **while still running** before cleanup. Actual terminal exit status is **1**, not successful completion.
2. Its `cleanup_verified=false` required the exact state `inactive`; the stopped unit was `failed` with empty cgroup. Host process inspection confirms no workers, task inhibitor or override. Cleanup is verified while the failed service state is retained.

Original `assessment.json` and original automatic archive remain unchanged. Corrected interpretation is in `assessment-terminal-v2.json`, with independent raw/trajectory/accounting checks in `partial-independent-audit.json`. These corrections change no scientific acceptance rule or result.

## Comparison and next decision

First DFT geometry remains converged: −3003.62393554 Ry, 16 iterations. **Second DFT energy is unavailable; no valid second-minus-first DFT difference exists.** Archived UMA difference remains **−0.041461080671410855 eV**. Unconverged second energies are not used for a provisional comparison.

**Next: restore stable AC and obtain a new explicit bounded completion authorization for the second frozen geometry.** This consumed attempt cannot be automatically retried. Its checkpoint is incomplete, so a future authorized attempt would need a clean start unless another complete compatible checkpoint is separately verified. Preserve all current evidence and unchanged protocol.

After two converged baseline geometries exist, the smallest useful proposed density-resolution check remains **two paired 80/750-Ry single points**, with actual FFT-grid change verified and all other settings fixed. Review on adequate hardware first: prior memory estimates exceed this laptop's 11-GiB cap. Compare changes in the paired energy difference to the existing 2–3 meV assessment target and forces to 0.005–0.01 eV/Å. This is not authorized and is not a full wavefunction-cutoff/k-point/physical-accuracy validation. No convergence study, UMA, refit or additional geometry was launched. Phase 3 remains incomplete.

## Portable evidence

- Raw: `local/qe75-second-v6/run01/`.
- Evidence: `evidence/qe75-second-v6/`, including `result.json`, `postflight.json`, `postflight-followup.json`, `assessment-terminal-v2.json`, `partial-independent-audit.json`, original allocation, controller review/diff and all logs/accounting.
- Original automatic archive: `artifacts/phase3/uio66_qe_water_pair_v6_windows.zip`, SHA256 `dfad6357c3750de08dae0e020985bc590881be69dfbd30f623f11e2a20cffbd3` (1,260,859,633 bytes; 53 verified payloads). Contains the first complete result/review plus the second partial evidence; its filename does not imply two valid results.
- Corrected Windows archive: `artifacts/phase3/uio66_qe_water_pair_v6_windows_v2.zip`, adjacent `.zip.sha256`; receipt `evidence/qe75-second-v6/portable-review-v2-receipt.json`. Includes this report and corrections while retaining original assessment/evidence. Use this corrected archive for review.
