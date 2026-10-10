# Frozen-water DFT pair — second completion v7, 2026-10-09

**Both frozen water-complex SCFs converged at 80/600 Ry. Local independent raw-evidence checks pass.** These are electronic-convergence results; cutoff/grid/k-point convergence, physical accuracy, UMA accuracy and Phase 3 completion remain unestablished. No convergence study or additional geometry has been launched.

## Paired result (second minus first)

| Quantity | First, f0.010 | Second, f0.005 |
|---|---:|---:|
| Text total energy, Ry | −3003.62393554 | −3003.62675764 |
| XML total energy, Ha | −1501.811967768731 | −1501.813378821678 |
| SCF iterations | 16 | 16 |
| Final XML SCF error, Ry | 7.774700847537152e-9 | 4.636287245504316e-9 |
| Final negative pseudocharge, electrons | 0.3938 | 0.3946 |
| Maximum total-force norm, eV/Å | 0.1641800457 | 0.1553166929 |
| RMS total-force norm, eV/Å | 0.0834623069 | 0.0831281193 |
| Maximum-force atom | 95 (O) | 95 (O) |
| Peak job memory, GiB | 9.253384 | 9.245415 |

Using high-precision XML energies and QE's conversion 1 Ry = 13.605693122994017 eV:

- **DFT ΔE = −0.038396706757 eV = −38.396707 meV**.
- Archived **UMA ΔE = −0.041461080671 eV = −41.461081 meV** (−934.0439250522884 minus −934.002463971617 eV).
- **DFT ΔE − UMA ΔE = +0.003064373914 eV = +3.064374 meV**. DFT predicts a smaller energy decrease by this amount.

Both methods favor the second frozen checkpoint at their present settings. This comparison is **provisional pending cutoff/grid checks**; the 3.064-meV discrepancy is comparable to the project's existing 2–3-meV numerical assessment target, which has not yet been demonstrated. It is not evidence that UMA is physically accurate. These are total complex-energy differences at two fixed geometries, not adsorption energies or relaxed DFT minima. Absolute UMA and DFT energy zeros are not compared. D3(BJ) is already included once in each QE total energy.

## Exact protocol and verification

The new v7 attempt was explicitly authorized after v6 stopped on AC loss. v6's incomplete checkpoint and all failure evidence remain intact; **v7 started clean**. No failed restart or automatic retry occurred.

Second target: `uio66_110111_H2O_s28_f0.005_complex`. The selected input is byte-identical to the reviewed v6 second input, SHA256 `6e5208b721ce790b932a67ba103f135c28cfe2889b02fc2a2958614532be62b3`. Exact sealed frozen 127 atoms/cell, all five SSSP potentials and same QE 7.5 build preserved. Scientific/numerical protocol unchanged: 80/600 Ry, Gamma, PBE-D3(BJ), version 4/threebody=false, neutral nspin=1, fixed occupations, conv_thr=1e-8 Ry, mixing_beta=0.3, CG/mixing_ndim=4/disk_io=high/verbosity=high. Prefix/coordinates identify the second geometry; other science matches the first.

Verified from actual input, full stdout/stderr and final XML:

- 522 electrons, 261 bands; input/output atom symbols/order match all 127 frozen atoms. Maximum coordinate/cell differences are 3.553e-15 / 2.665e-15 Å (serialization precision).
- XML convergence=true, exit_status=0; service/MPI exit=0, JOB DONE. No final or earlier diagonalization warning or fatal QE error found.
- Second text/XML energy difference **3.356e-9 Ry**, consistent with printed precision.
- **All 127 total-force vectors** independently read from the uniquely headed raw total-force table, not the seven verbose component tables. Text Ry/bohr versus XML Ha/bohr uses factor two; species type and consecutive 1-based atom mapping checked. Maximum component difference **4.969e-9 Ry/bohr**, all finite. CSV retains every native-unit vector and mapping.
- These deliberately frozen geometries have nonzero forces. Their magnitude does not automatically invalidate SCF, and the f0.010/f0.005 labels are UMA checkpoint tolerances, not DFT force convergence thresholds.
- Dense FFT **225³ / 1,902,004 G vectors**; smooth FFT **160³ / 741,079 G vectors**; identical to the first baseline. Starting atomic/randomized-wavefunction choices agree with the previous second attempt, and all ten previously completed iterations reproduce its printed errors/negative-charge values.
- Manifest, both selected frozen geometries and potentials hash checked; all **27 v7 raw files** match the terminal hash manifest. First-result XML/input/stdout hashes rechecked before differencing.

## Negative-pseudocharge and SCF trajectory

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
|11|0.3948|6.16e-06|
|12|0.3947|3.52e-06|
|13|0.3947|6e-07|
|14|0.3946|1.2e-07|
|15|0.3946|2e-08|
|16|0.3946|4.6e-09|

A final force-stage diagnostic repeats 0.3946 electrons. Negative pseudocharge peaks at iteration 6 then settles as SCF error decreases. It is integrated negative valence pseudocharge, not the SCF error or net charge. Neither persistent nonzero values nor the 0.1/0.522-electron heuristics independently accept or reject physical accuracy. Earlier 600→625 Ry tests retained the same FFT grid and do not exclude larger-grid sensitivity.

## Resources, elapsed time and cleanup

- Final fresh gate: AC online, **12.457294 GiB available RAM**, adequate persistent disk, no prior workers. No applications closed by the agent.
- Actual four physical cores / one compute thread per MPI rank; 11-GiB hard cap, 10-GiB high guard, zero job swap, 96-task ceiling. Same byte-identical reviewed controller; only new paths/unit/allocation. No weakened safeguards.
- Full service peak **9,927,188,480 bytes = 9.245414734 GiB**; lifetime swap peak zero. **2029 samples** show zero memory/task-limit events, AC online and sleep:idle block inhibition. Maximum sampled tasks 15; minimum sampled host available RAM **1.018932 GiB**. Host headroom became narrow; do not assume more local memory is available for higher cutoffs.
- MPI started **07:30:54 UTC / 13:00:54 IST**, service exited **08:41:33 UTC / 14:11:33 IST**. Launch through cleanup **4240.105 s (70m40.105s)**; scratch **830,566,191 bytes (~0.774 GiB)** retained, including XML/density/PAW/wavefunction files. Future restart compatibility would still require a separate check.
- Immutable allocation **07:30:05.863522–11:30:05.863522 UTC**, preparation/cleanup included. Workers cleaned up at **4289.228 s (71m29.228s)**; original automatic archive completed at **4324.701 s (72m04.701s)**, before four hours. No deadline reset or extension. Normal convergence ended the run; no stop guard fired.
- No suspend/hibernate event in the allocation journal. Workers/guardian/timers stopped, cgroups gone, temporary inhibitor released and override removed; follow-up host inspection confirms cleanup. Power settings unchanged.

### Accounting caveat and independent audit correction

The separate audit's first version assumed `result.json` always contained final cgroup counters. After this successful exit, the kernel had already removed that cgroup, so it raised `KeyError('final_cgroup')` after its energy/geometry/force checks. That failure and script are preserved.

The separately versioned audit uses the retained full-lifetime service memory/swap peaks, successful exit status, monitoring samples and journal when final counters are unavailable. Peak memory stayed below the 10-GiB guard, swap peak was zero, all sampled counters were zero, and no OOM/service failure was recorded. **Final cgroup counters are unavailable**, not invented as zero. Last sample preceded worker cleanup by 2.115 seconds. All scientific acceptance checks are unchanged; `independent-audit-v2.json` passes. This is an offline accounting correction, not a rerun or a relaxed convergence criterion.

## Smallest next convergence study — proposal only

**Two paired density-cutoff checks**, one per existing frozen water complex:

1. Keep ecutwfc=80 Ry; change only **ecutrho 600→750 Ry**. Preserve exact coordinates/cell/potentials, functional/dispersion, Gamma, charge/spin/occupations, conv_thr=1e-8 Ry and other settings.
2. Confirm actual dense FFT changes; existing offline source-derived prediction is **243³, 2,658,579 G vectors**, versus baseline 225³. Record realized dimensions/counts and negative-pseudocharge trajectories.
3. Converge both SCFs and recheck text/XML/forces. Evaluate the change in **paired ΔE**, not either absolute energy alone, against the existing **2–3 meV** assessment target; examine force changes against **0.005–0.01 eV/Å**. These are numerical assessment targets, not physical guarantees.
4. Review a larger-RAM allocation first. Existing 750-Ry estimates are **12.005–13.017 GiB**, not measured bounds, exceeding this laptop's 11-GiB cap. No local limit increase is authorized. Retain bounded controls and independently verified resources on any future machine.

This isolates charge-density resolution. It is the smallest useful next check for the present concern, not a complete convergence proof: ecutwfc and k-point checks remain separate, and smaller negative pseudocharge alone would not validate energies. **Nothing in this proposed study has been launched or newly authorized.** Next decision: independently review this paired result and authorize/resource the two density-cutoff checks if appropriate. No further geometry, UMA inference, refit or design expansion; Phase 3 remains incomplete.

## Evidence and Windows transfer

- Raw second result: `local/qe75-second-v7/run01/`.
- Actual assessment/comparison: `evidence/qe75-second-v7/assessment.json`, `comparison.json`.
- Separate audit: `independent-audit-v2.json`, `independent-force-crosscheck.csv`, `independent-resource-summary.json`, `comparison-source-hashes.json`, `postflight-followup.json` in that evidence directory. Original audit failure retained as `independent-audit-v1-failure.json`.
- Prior first independent review: `docs/UIO66_QE75_FIRST_INDEPENDENT_REVIEW_V6.md`; prior AC failure: `docs/UIO66_QE75_SECOND_V6_RESULTS.md`.
- Original automatic Windows ZIP: `artifacts/phase3/uio66_qe_water_pair_v7_windows.zip`, SHA256 `202bf5339a7d14cef5dc292c103704e759aba488731ec457a1b1957dfd5f51f6` (60 verified payloads). Original archive unchanged.
- Final reviewed Windows ZIP: `artifacts/phase3/uio66_qe_water_pair_v7_windows_v2.zip`, adjacent `.zip.sha256`, receipt `evidence/qe75-second-v7/portable-review-v2-receipt.json`. Includes first complete review archive, second full inputs/outputs/XML/checkpoints/UPFs/accounting, independent force audit, this report and checksums. No external message or upload was sent.
