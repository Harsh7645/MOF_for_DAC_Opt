# Independent first-water review v6 — 2026-10-09

## Scope and outcome

**PASS: no substantive blocker or report/raw-evidence discrepancy identified.** Offline review only; no QE/UMA launched. The user conditionally authorizes one second frozen water-complex attempt after this review and fresh resource gates. Authorization remains unused because available RAM is below 12 GiB.

The independent script `scripts/review_qe75_first_v6.py` imports no earlier result parser. It reads the full stdout/stderr and XML, reconstructs the uniquely headed total-force table by line/token parsing, checks every force and atom identity, and independently recomputes accounting. It verifies the review ZIP's SHA256 and every payload, and checks local raw files against the archive and original raw-hash manifest. Existing sealed-package validation is reused; changed or selected inputs/potentials remain hash checked.

## Verified evidence

| Check | Actual finding |
|---|---|
| Review archive | 85 payloads pass; SHA256 c8951afe5281dd5bedd3f47d85c26b53c10bfe8df316b51e38e373e9616ae53e |
| Local raw files | All 27 agree with the archived evidence |
| Electronic convergence | 16 iterations; XML true, error 7.774700847537152e-9 Ry < 1e-8 Ry |
| Completion | XML exit 0, service/MPI exit 0, JOB DONE; no fatal/final diagonalization warning |
| Energy | Text −3003.62393554 Ry; XML −1501.811967768731 Ha; difference 2.538e-9 Ry |
| Electrons/structure | 522 electrons; all 127 symbols/order match frozen input and XML; cell/position discrepancies below 4e-15 Å |
| Forces | All 127 vectors finite; text Ry/bohr = 2 × XML Ha/bohr; maximum discrepancy 4.990e-9 Ry/bohr |
| Atom mapping | Consecutive 1-based atom indices; each QE species type agrees with input/geometry/XML symbol |
| Force norms | Maximum 0.1641800457 eV/Å at atom 95 (O); RMS 0.0834623069 eV/Å |
| Negative pseudocharge | Initial 0.3659; maximum 0.3947 at iteration 6; final/force-stage 0.3938 electrons |
| Resource peak | 9,935,745,024 bytes = 9.253384 GiB; no job swap/high/max/OOM/task events |
| Runtime | Launch through cleanup 4221.400 s; original allocation through package 7117.526 s < four hours |
| Scratch/headroom | 830,566,191 bytes; minimum sampled host available 1.353779 GiB |
| Cleanup | No workers, task inhibitor or runtime override retained; no suspend during allocation |

The force crosscheck is saved in `evidence/qe75-first-independent-review-v6/force-crosscheck.csv`, with both native unit sets, atom IDs/types/symbols and all differences. Unit conversion was checked against local QE 7.5 `Modules/qexsd_init.f90:1341` (forces divided by e2), `Modules/constants.f90`, and `PW/src/forces.f90` (total forces followed by verbosity-high component tables). The corrected earlier parser agrees with this separate reconstruction. Its original 1016-row failure remains preserved in the original archive; no acceptance tolerance was loosened.

The complete negative-pseudocharge/SCF-error trajectory is independently reconstructed in `review.json` and agrees with the completion report. SCF error decreases to the specified threshold while negative pseudocharge settles; neither persistent pseudocharge nor a heuristic electron threshold independently validates or invalidates this result. Finite forces on the deliberately frozen structure do not imply a relaxed DFT minimum and are not an automatic failure.

## Second geometry: authorization and current resource hold

Second target: `uio66_110111_H2O_s28_f0.005_complex`, using exactly the same protocol as the first result: frozen archived geometry/cell, five approved potentials, 80/600 Ry, Gamma, PBE-D3(BJ) two-body, neutral nspin=1, fixed occupations, conv_thr=1e-8 Ry, mixing_beta=0.3, CG, mixing_ndim=4 and disk_io=high. One clean attempt only, with four physical cores, 11-GiB hard/10-GiB high guard/zero job swap/96 tasks and four hours including preparation/cleanup. New allocation must start before second-run preparation; no allocation or worker has started during this offline review.

Fresh resource screen: AC online; **10.861282 GiB available RAM**, short of the required 12 GiB by **1.138718 GiB**; persistent disk free **210.289 GiB**; no QE/MPI workers. Zen/web content are the largest optional application consumers. Permission to close Zen gracefully is pending; no applications or services have been stopped. The temporary inhibitor and actual launch checks will be performed only when proceeding to the authorized attempt. Unchanged controller tests will be reused, with focused review of target/input/configuration changes.

The archived UMA energies are −934.002463971617 eV (first) and −934.0439250522884 eV (second): **second minus first = −0.041461080671410855 eV**. The values come from the sealed manifest's exact checkpoint records, not new inference. No second DFT energy exists yet, so no DFT difference or DFT–UMA comparison is claimed.

## Remaining uncertainty and smallest proposed follow-up

Successful SCF convergence does not establish cutoff/grid convergence, physical accuracy, UMA accuracy, proton correspondence with the publication or Phase 3 completion. Once the second baseline is available, the smallest useful density-resolution check is a **paired** recalculation of both frozen complexes at one higher charge-density cutoff that changes the actual dense FFT grid, keeping ecutwfc=80 and all other science fixed. The existing 80/750-Ry proposal is a candidate, subject to explicit memory/grid review on adequate hardware; previous estimates exceed this laptop's 11-GiB cap. Compare the change in second-minus-first energy against the existing 2–3 meV assessment target and force changes against 0.005–0.01 eV/Å. This is only a proposal: two jobs, no launch authorization, and it would not by itself establish wavefunction-cutoff or k-point convergence. A single higher-cutoff geometry would not adequately test the paired energy difference.

## Evidence and next action

- Prior complete raw result: `local/qe75-fedora-completion-v5/run01/`.
- Independent findings/accounting/trajectory: `evidence/qe75-first-independent-review-v6/review.json`.
- Fresh resource screen: sibling `resource-screen.json`.
- Complete Windows review ZIP remains `artifacts/phase3/uio66_qe600_completion_v5_review_v2.zip`.
- Small supplemental audit ZIP: `artifacts/phase3/uio66_qe_first_independent_review_v6.zip` (report, script, force crosscheck and JSON receipts); use alongside the complete original review ZIP.
- Next action: resolve the RAM prerequisite with user-approved application closure, then prepare and run the single authorized second geometry under unchanged limits. No renewed scientific confirmation is needed if its conditions pass.
