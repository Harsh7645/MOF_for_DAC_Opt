# Fedora QE 7.5 completion v5 — first frozen water complex

Assessed 2026-10-09; calculation completed 2026-10-08. **Converged SCF, ready for independent assessment. Authorization consumed; no further calculation authorized.** This establishes electronic self-consistency for this input, not cutoff convergence, physical accuracy, UMA accuracy or Phase 3 completion.

## Decision and verified result

- One clean 80/600-Ry attempt on `uio66_110111_H2O_s28_f0.010_complex`. Earlier 600-Ry checkpoints lacked XML/density; 625-Ry checkpoint was excluded. No earlier scratch reused.
- Exact archived 600-Ry input reused byte-for-byte: SHA256 `b60f5a1bf910b7883bcbbb1e8e185791ef57103e82af60801f46f25361915838`. Frozen 127 atoms/cell, 522 electrons, 261 bands, Gamma, PBE-D3(BJ) two-body, neutral nspin=1, fixed occupations, 80/600 Ry, conv_thr=1e-8 Ry, mixing_beta=0.3, CG/mixing_ndim=4/disk_io=high preserved. All five potential hashes and the QE executable hash verified.
- Text and XML agree: **16 SCF iterations**, XML final estimated error **7.774700847537152e-9 Ry**, XML convergence=true and exit_status=0; MPI/service exit=0, JOB DONE. No diagonalization warning or fatal error found.
- Final total energy **−3003.62393554 Ry**; XML **−1501.811967768731 Ha**, difference **2.538e-9 Ry**. Includes D3(BJ); do not add dispersion again. Accepted as a converged SCF datum for review, with numerical/physical uncertainty unestablished.
- XML input/output atom identities and order match; coordinate/cell differences from frozen source are at most 3.553e-15 / 2.665e-15 Å (serialization precision).
- **127 finite total-force vectors**, text Ry/bohr versus XML Ha/bohr (factor 2); maximum component difference 4.990e-9 Ry/bohr. Maximum force norm **0.164180 eV/Å**, atom 95 (O); RMS norm **0.083462 eV/Å**. Printed total force 0.036582 Ry/bohr and SCF force correction 0.000105 Ry/bohr. Frozen structures were not relaxed; these forces are findings, not automatic failure.
- Dense FFT **225³, 1,902,004 G vectors**; smooth FFT **160³, 741,079 G vectors**. Starting charge 521.9847 renormalized to 522 and 457 randomized atomic wavefunctions match archived baseline; first four errors reproduce it exactly at printed precision.

## Negative valence pseudocharge trajectory

This diagnostic is distinct from SCF error and net electron count. It initially increases, peaks at 0.3947 electrons in iteration 6, then settles at 0.3938 while SCF error falls. It remains nonzero after convergence/at force evaluation. Neither 0.1 nor 0.522 electrons is treated as an acceptance threshold. Persistence does not establish accurate energies or resolve density-grid/pseudopotential sensitivity. The earlier narrow 625-Ry probe used the same FFT dimensions and cannot exclude wider grid sensitivity.

| Iteration (0 = initial) | Negative pseudocharge, e | Estimated SCF error, Ry |
|---:|---:|---:|
| 0 | 0.3659 | — |
| 1 | 0.3741 | 20.00902028 |
| 2 | 0.3836 | 2.51087335 |
| 3 | 0.3887 | 0.66475787 |
| 4 | 0.3940 | 0.26218816 |
| 5 | 0.3938 | 0.0858073 |
| 6 | 0.3947 | 0.00935478 |
| 7 | 0.3945 | 0.00486566 |
| 8 | 0.3944 | 0.00080212 |
| 9 | 0.3943 | 0.00038587 |
| 10 | 0.3941 | 8.374e-05 |
| 11 | 0.3940 | 7.22e-06 |
| 12 | 0.3939 | 3.06e-06 |
| 13 | 0.3938 | 7e-07 |
| 14 | 0.3938 | 1.2e-07 |
| 15 | 0.3938 | 4e-08 |
| 16 | 0.3938 | 7.8e-09 |

## Resources, deadline and cleanup

- Actual fresh gate: AC online, 12.662 GiB available RAM, sufficient persistent disk, no preexisting QE/MPI workers. Four physical cores, one compute thread per rank, no oversubscription.
- Enforced 11-GiB hard / 10-GiB high guard / zero cgroup swap / 96-task limit unchanged. Peak **9.253384 GiB (9,935,745,024 bytes)**, sampled tasks at most 15. Zero high/max/OOM/task-limit events and zero job swap. Minimum sampled host available RAM **1.353779 GiB**; host headroom fell during execution, so later allocations must recheck resources. No applications/services were closed.
- MPI start 2026-10-08 15:42:33 UTC (21:12:33 IST); service exit 16:52:54 UTC (22:22:54 IST). Launch through cleanup **4221.400 s (70 min 21 s)**. Scratch **830,566,191 bytes (~0.774 GiB)** retained.
- Immutable allocation began **14:54:38.654980 UTC**, ceiling **18:54:38.654980 UTC**. Preparation and charger wait counted. Worker cleanup at **7096.701 s**, original automatic package finished at **7117.526 s (1 h 58 min 38 s)**, within four hours. No clock reset or extension. Subsequent offline reassessment/package correction is not additional compute allocation.
- Normal termination on SCF convergence, before deadline stops. All 2021 resource samples show AC online and task sleep:idle block inhibition. No suspend/hibernate events in the allocation journal. Inhibitor released after cleanup; worker/guardian/timers inactive, no cgroup or workers remaining, runtime override removed. Follow-up host inspection on 2026-10-09 confirms this; system power settings unchanged.

## Assessment correction and provenance

The automatic v1 assessment failed an empty assertion after verifying convergence/settings/geometry. It counted **1016** `atom ... force =` lines across one total-force table and seven component tables, expecting 127. QE 7.5 `PW/src/forces.f90` lines 348–409 explicitly prints total forces followed by verbose components. This was a parser error, not a missing-force or SCF failure.

`scripts/assess_qe75_completion_v5_v2.py` selects the uniquely headed total-force block and checks all 127 vectors against XML with the original tolerances. All checks pass. Original `assessment.json`, original script, raw outputs and original review ZIP remain unchanged. No scientific setting/criterion was weakened and no QE was rerun.

- Raw: `local/qe75-fedora-completion-v5/run01/` (input, stdout/stderr, five UPFs, XML, density/PAW/wavefunction/checkpoint files, resource log). All **27** raw-file hashes reverified. File retention alone is not a future restart-compatibility certification.
- Final assessment: `evidence/qe75-fedora-completion-v5/launch02/assessment-v2.json`.
- Converted total energy/forces: sibling `completed-SCF-pending-independent-assessment-v2.json`.
- Integrity/cleanup: sibling `reassessment-integrity.json`, `postflight.json`, `postflight-followup.json`, `result.json`, `inhibitor-release.json`, `raw-file-hashes.json`.
- Original review ZIP: `artifacts/phase3/uio66_qe600_completion_v5_review.zip`, SHA256 `3dc362b2e6fb594e562402e569ea3c47f4f8b6c800c998339773a96c6228100c` (preserves original failed assessment).
- Corrected portable review: `artifacts/phase3/uio66_qe600_completion_v5_review_v2.zip`; checksum and verification in `evidence/qe75-fedora-completion-v5/launch02/portable-review-v2-receipt.json`. Contains original raw/evidence plus corrected assessment, parser/source excerpts and this report; original assessment explicitly retained.
- Paired diagnostic review remains `artifacts/phase3/uio66_qe_review_600_625_v1.zip` (included). Reviewer recommendation came through the user and remains provisional; verified local evidence is distinguished from interpretation.

## Next decision

**Send the corrected portable package for independent QE/pseudopotential review of this first converged frozen result**, especially persistent negative pseudocharge and force interpretation, before deciding on any second geometry or convergence study. No additional calculation is authorized or launched. Cutoff/k-point convergence, physical accuracy, publication proton correspondence, UMA accuracy and Phase 3 remain unresolved.

Offline reassessment command (never launches QE):

```bash
python3 scripts/assess_qe75_completion_v5_v2.py
```
