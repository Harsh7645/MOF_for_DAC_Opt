# Baseline recovery v2 — 2026-10-09

User confirms the interruption was caused by switching Fedora to Windows and explicitly authorizes one recovery attempt plus continuation of the 11 unattempted original jobs. The v1 batch has not resumed automatically. It remains unchanged and stopped.

## Inspection and decision

- No completed jobs among the original 12. Interrupted ID: `uio66_110111_H2O_s28_f0.010_host`; two SCF iterations completed, third started, last error 2.47751606 Ry, not converged.
- Prior water complexes were independently rechecked against stdout/XML: SCF/energy, 522 electrons, all frozen atom identities/coordinates/cell, and all 127 total force vectors with text/XML units and type mapping. Both remain valid converged SCFs and are excluded from this batch. Numerical/physical accuracy remains unverified.
- Interrupted raw hashes still match. Only four wavefunction and four mixing files exist: no data-file-schema.xml or charge density. This is not a complete compatible checkpoint. QE 7.5 INPUT_PW.def restart_mode requires a cleanly stopped run with compatible parallelization. One clean recovery in a new directory is selected; no old scratch is reused.
- All 12 input/geometry pins unchanged; composition-specific electron expectations and 80/600 scientific settings remain as independently reviewed in v1.

## Accounting and controls

The original 48-hour receipt is copied byte-identically, never reset. Elapsed time includes the interrupted attempt, Windows/offline interval, preparation, computation and cleanup. A current-boot monotonic anchor preserves all previously elapsed time and rejects an unexpected boot. The explicitly authorized recovery has its own four-hour ceiling beginning before recovery preparation; this is a new recovery allocation, not alteration of the old attempt. The old attempt and deadline remain archived. Remaining jobs each have at most one attempt and four hours, additionally clamped to the original batch deadline.

Four physical cores, 11-GiB hard/10-GiB high, zero job swap, 96 tasks unchanged. Every launch repeats AC, >=12-GiB available RAM, disk, worker and temporary sleep-inhibitor checks. Stop at any subsequent failure; no automatic retry. Original resource-stop and deadline algorithms retained. New control dummy passed; heartbeat wrapper checked without QE. Coordinator now saves a stopped ledger before potentially failing user-bus cleanup, and guardian saves cleanup-entry evidence before cleanup. No permanent system/power changes.

## Progress and user session

`docs/UIO66_QE75_BASELINE12_V2_PROGRESS.md` and `evidence/qe75-baseline12-recovery-v2/progress.json` update every **600 seconds**, plus starts, finishes and stops. They report manifest ID, completed SCF iterations, elapsed time, RAM/current peak, swap/events, disk/scratch, AC and inhibitor state. Raw per-job status remains sampled about every two seconds. `progress-history.jsonl` preserves the periodic records. Worker configuration/execution markers record attempt consumption; ledger includes the interrupted prior attempt separately.

Per the latest user preference, routine chat updates are suppressed. On-disk updates do not need this assistant chat to remain active; they do require Fedora and its user service manager to keep running. Rebooting/switching OS or logging out can terminate the jobs. The temporary inhibitor prevents ordinary sleep/idle, not an OS switch. Keep AC connected and the lid open.

Exact viewing command:

```bash
watch -n 30 cat /home/harshsahu/MOF_for_DAC_Opt/docs/UIO66_QE75_BASELINE12_V2_PROGRESS.md
```

Raw new evidence: `local/qe75-baseline12-recovery-v2/jobNN/run01/`. Audit/ledger: `evidence/qe75-baseline12-recovery-v2/`. Original v1 evidence and both water-complex results unchanged. Provisional energy/force comparisons update after accepted results. Phase 3 and numerical validation remain incomplete.

Recovery-job deadline UTC: 2026-10-09T18:03:21.887498+00:00

Original batch deadline UTC: 2026-10-11T09:17:37.439327+00:00
