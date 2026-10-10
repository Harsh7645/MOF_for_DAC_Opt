> Subsequent update: numerical diagnostic proposal and independent non-QE control
> checks are recorded in `UIO66_QE75_RHO_DIAGNOSTIC_PLAN_V1.md`. Scientific execution
> remains on hold and the conditional authorization unused. The dated preflight
> record below is preserved; its pending control checks have since been completed.

# Fedora v4 preflight — negative-density review, 2026-10-08

**HOLD BEFORE LAUNCH. No QE, dummy workload, new inhibitor or new allocation started.
The newly granted conditional one-attempt authorization is NOT consumed.**
The numerical review is the first prerequisite; it has not cleared. This hold follows
the user's explicit instruction to report substantive unresolved numerical concerns
before launching. It is not a claim that the frozen model is definitively invalid.

## Retained output and source verification

All25 retained v3 raw files still match their SHA256 manifest. The scientific package,
inputs, coordinates, potentials and build are unchanged. Source files below were
byte-compared with the pinned official QE7.5 archive. Graphify is unavailable;
bounded source searches were used, with no graph rebuild.

| Stage | First printed negative-charge component (electrons) | Second component |
|---|---:|---:|
| Initial potential | 0.3659 | 0 |
| SCF iteration1 | 0.3741 | 0 |
| SCF iteration2 | 0.3836 | 0 |
| SCF iteration3 | 0.3887 | 0 |
| SCF iteration4 | 0.3940 | 0 |

Increase0.0281electrons (~7.68%); no declining trend is observed in these four
iterations. In parallel, SCF errors decreased20.00902028→2.51087335→0.66475787→
0.26218816Ry. A decreasing SCF residual does not establish numerical accuracy.
No failed-diagonalization warning was reported; iteration5 was interrupted.

`local/qe75-fedora-v1/q-e-qe-7.5/PW/src/v_of_rho.f90:508` shows the nspin1
path accumulating the magnitude of negative valence pseudocharge after subtracting
the added core density. Lines584–592 sum across MPI ranks and multiply by cell
volume divided by FFT-grid size. These are integrated electron-count units, not
pointwise density, net-charge errors, percentages or SCF energy residuals. The
up/down wording is generic; this run has nspin1. The print threshold eps8 is a
reporting threshold, not a validated acceptance threshold.

## Interpretation and launch gate

The [QE troubleshooting guide](https://www.quantum-espresso.org/Doc/pw_user_guide/node21.html)
flags sizable negative charge, around0.1, as concerning. It explains Fourier
truncation and USPP-related negative regions and discusses charge-density cutoff
sensitivity. The matching pinned source is `PW/Doc/user_guide.tex:1538`;
lines1499–1504 also identify USPP augmentation pseudization/truncation as potential
causes of convergence trouble. This does not prove that raising ecutrho will solve
this particular case.

The [QE self-consistency FAQ,6.12](https://www.quantum-espresso.org/faq/self-consistency/)
gives a separate rough starting-charge caution of0.001 times the electron count:
0.522electrons for522electrons. Our final0.3940 is0.07548% of522 and below that
relative heuristic. This is relevant counterevidence to declaring the output
invalid solely from an absolute0.1 rule.

These are differing heuristics, not a single formal pass/fail specification.
The retained diagnostics persist and increase beyond the initial guess; no
converged density, spatial localization or numerical convergence assessment exists.
**The current evidence does not establish that the warnings are harmless, nor
prove a specific failure mechanism.** Under the requested preflight gate, hold the
new launch for numerical review. Do not automatically change cutoffs, potentials,
mixing, charge/spin or coordinates, or launch extra diagnostic calculations.

## Preparation status and resources

The host snapshot confirms AC power online, zero system zram usage, no pw.x/mpirun/
prterun workers, and229,366,198,272B persistent free space. Physical RAM:14.936GiB;
MemAvailable:12.561GiB. No applications or services were stopped. Existing
system delay inhibitors are not a verified task-owned sleep/idle block inhibitor.
No new task inhibitor was acquired, so none remains to release.

Sleep/idle inhibitor acquisition, lifetime/release checks, dummy deadline/process
cleanup/retention tests and interruption/resume checks remain **unperformed** after
this first scientific gate failed to clear. They must pass before any later launch.
Do not treat v3's controls as sufficient: that attempt lacked temporary sleep
inhibition and exceeded its real wall envelope during automatic suspend.

No four-hour allocation was created because run preparation has not begun. The
new authorization remains conditional and unused; all older attempt authorizations
remain consumed. A future launch also requires fresh RAM/disk/AC/job checks and a
recorded immutable allocation before staging, with the lid open and AC connected.

## Exact next decision and evidence

Review the persistent negative pseudocharge using this report and the pinned input/
UPFs with a QE numerical reviewer. Resolve whether an unchanged-settings attempt
is justified, or propose a separately reviewed diagnostic plan. No additional
convergence calculation is authorized by this hold. The existing one-attempt
permission must not be silently broadened or consumed on an unsuitable run.

- Source/data review: `evidence/qe75-fedora-v4-preflight/negative-density-review.json`.
- AC/RAM/disk/jobs/inhibitors: `evidence/qe75-fedora-v4-preflight/host-status.json`.
- Evidence hashes: `evidence/qe75-fedora-v4-preflight/evidence-file-hashes.json`.
- Previous raw output: `local/qe75-fedora-completion-v3/run01/stdout.log`.
- Previous failed-attempt details: `docs/UIO66_QE75_FEDORA_COMPLETION_V3.md`.

No new scientific result. Phase3,fullSCF/finalforces,numerical accuracy and UMA
accuracy remain unresolved. Evidence directories remain Git-ignored.
