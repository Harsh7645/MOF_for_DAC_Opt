# QE density-cutoff diagnostic proposal and control checks — 2026-10-08

**Offline investigation complete; no QE/UMA launched. Scientific execution is
disabled. The pending conditional unchanged-first-geometry authorization remains
unused. This proposed cutoff change needs separate approval.**

## Observations and interpretation

Reference: `local/qe75-fedora-completion-v3/run01/input.in` and `stdout.log`.
Line-numbered excerpts and aligned records are retained in
`evidence/qe75-rho-diagnostic-plan-v1/`. Graphify is unavailable; targeted source
retrieval was used without rebuilding the graph.

| Stage | Integrated negative charge (electrons) | Estimated SCF error (Ry) |
|---|---:|---:|
| Initial potential | 0.3659 | Not applicable |
| Iteration 1 | 0.3741 | 20.00902028 |
| Iteration 2 | 0.3836 | 2.51087335 |
| Iteration 3 | 0.3887 | 0.66475787 |
| Iteration 4 | 0.3940 | 0.26218816 |

All second printed components are zero. Iteration 5 started but did not finish.
Negative charge rose 0.0281 electrons (7.68%) while the estimated SCF error fell
about 76-fold. These observations establish persistence beyond the initial guess,
not SCF divergence, a converged density, or accurate energies/forces. No failed
diagonalization warning appears in the retained output. Termination followed
suspend/deadline enforcement, not an observed numerical crash.

QE 7.5 `PW/src/v_of_rho.f90:508–522,584–592` integrates the magnitude of negative
**valence pseudodensity**, after subtracting the core density added for XC. It
sums across MPI ranks and multiplies by cell volume/grid size. The generic
up/down label does not imply spin polarization here (`nspin=1`). This is neither
net-charge error nor the estimated SCF error. Its printing threshold is not an
acceptance threshold. `PW/src/electrons.f90:856,911–937` shows that the
unconverged SCF potential uses the mixed density; these observations therefore
concern that mixed density. The converged branch uses the output density.

The separate initial `starting charge 521.9847, renormalised to 522.0000` message
and atomic wavefunction renormalization messages should not be conflated with
negative charge. The [QE guide](https://www.quantum-espresso.org/Doc/pw_user_guide/node21.html)
discusses finite Fourier truncation and augmentation-related negative regions;
the [self-consistency FAQ](https://www.quantum-espresso.org/faq/self-consistency/)
offers a separate starting-charge heuristic. **Neither 0.1 nor 0.001×522=0.522
electrons is used as an automatic acceptance threshold.** The initial-charge
heuristic does not resolve persistent mixed-density diagnostics during SCF.

## Actual pseudopotentials and density representation

All five actual v3 UPFs match the sealed SSSP 1.3.0 PBE Precision files and hashes.
Exact filenames, SHA256 values and metadata are in
`plans/qe75-rho-diagnostic-v1/pseudopotential-pins.json`.

| Species / exact file | Type; nonlinear core correction | SSSP recommended wavefunction/density Ry |
|---|---|---:|
| Zr / `Zr_pbe_v1.uspp.F.UPF` | USPP; yes | 30 / 240 |
| N / `N.oncvpsp.upf` | NC; yes | 80 / 320 |
| H / `H_ONCV_PBE-1.0.oncvpsp.upf` | NC; no | 80 / 320 |
| C / `C.pbe-n-kjpaw_psl.1.0.0.UPF` | PAW; yes | 45 / 360 |
| O / `O.pbe-n-kjpaw_psl.0.1.UPF` | PAW; yes | 75 / 600 |

The actual 80/600 Ry input meets the largest recommendations. Recommendations
do not prove convergence for this structure. There are no explicit `nr1/2/3` or
smooth-grid overrides. Mixed USPP/PAW augmentation and finite density Fourier
resolution make cutoff sensitivity plausible, but current evidence does not
identify a responsible atom/species or distinguish truncation from pseudization.
No final density exists for spatial localization.

Source files were hash-compared with the pinned official QE 7.5 archive.
`setup.f90:487`, `FFTXlib/src/fft_types.f90:1086–1197`, and
`fft_support.f90:126–165` define the cutoff/grid rules. Offline reciprocal-lattice
enumeration reproduced both recorded baseline grids and G counts, without QE:

| Density cutoff (Ry) | Dense FFT dimensions | Gamma density G-vectors |
|---:|---:|---:|
| 600, recorded baseline | 225³ | 1,902,004 |
| 625, predicted | 225³ | 2,022,032 |
| 650, predicted | 240³ | 2,144,033 |
| 750, predicted | 243³ | 2,658,579 |

The smooth 320-Ry representation remains 160³ / 741,079 G-vectors. Increasing
600→625 Ry adds 6.31% more density G-vectors but leaves the real-space FFT grid
unchanged. It tests reciprocal truncation sensitivity, not independently refined
FFT quadrature. See also [QE input documentation](https://www.quantum-espresso.org/Doc/INPUT_PW.html).

## Smallest proposed comparison — one new calculation, not authorized

Compare **one clean 80/625-Ry first-complex probe** against the archived 80/600-Ry
initial state and first four completed iterations. A second baseline run is not
needed for this exploratory comparison; the first two baseline iterations also
have the prior v2 evidence. This is not a full cutoff-convergence study.

- Exact proposal: `plans/qe75-rho-diagnostic-v1/rho625.in`.
- Matched reference: `plans/qe75-rho-diagnostic-v1/rho600.in`.
- These files differ **only in `ecutrho`**. Relative to the archived v3 input,
  both share the time-control change `max_seconds=12948` → `1350`.
- Preserve all 127 atoms, cell, atom order, UPFs, 80-Ry wavefunctions, Gamma,
  PBE-D3(BJ), version 4/two-body dispersion, neutral singlet/fixed occupations,
  CG, mixing_beta 0.3, mixing_ndim 4, disk_io high and verbosity high.
- Preserve `conv_thr=1d-8`, `electron_maxstep=200`, `scf_must_converge=.true.`
  and force output. Stop by EXIT/time control, not a relaxed convergence target.
- Compare initial negative charge and matched iterations 1–4, SCF error,
  diagonalization warnings, realized grids/G counts, resource usage and exit reason.
  Request EXIT after the fourth completed error report; a fifth may start before
  QE notices it. If fewer finish within the bounds, retain and compare only those.

Interpretation: a consistent reduction beyond the printed rounding scale (about
0.00005 electrons per value) supports cutoff sensitivity. Report absolute and
relative changes and the SCF-error trajectory; do not invent a pass threshold.
A null result at 625 Ry does not rule out a larger-grid effect. Mixed/nonmonotonic
changes or materially different SCF trajectories are inconclusive. Even a strong
reduction cannot establish converged energies/forces, physical validity or UMA
accuracy. No partial energy is accepted as a scientific result.

## Memory and enforced limits proposed

Use the larger observed early-SCF peak, **9.313965 GiB**, as the baseline anchor.
The species-specific source allocation model plus an empirical baseline offset,
and a separate uniform G-count scaling estimate, give:

| Density Ry | Calibrated allocation estimate (GiB) | Uniform G scaling (GiB) | Assessment |
|---:|---:|---:|---|
| 625 | 9.710 | 9.902 | Plausibly fits; narrow margin below 10-GiB high guard |
| 650 | 10.266 | 10.502 | Crosses existing high guard; not proposed locally |
| 750 | 12.005 | 13.017 | Exceeds 11-GiB hard cap; not proposed locally |

These are sensitivity estimates, **not measured peaks or confidence bounds**.
FFT workspace, process imbalance, allocators, file cache, and unvisited force
stages may differ. The earlier conservative >12.67-GiB estimate and the 0.79-GiB
initialization measurement are not substitutes for SCF memory evidence. Source,
grid counts and calculations are saved in `source-grid-memory-audit.json`.

Proposed limits: four MPI ranks on four physical cores, one compute thread;
11-GiB hard / 10-GiB high memory, zero cgroup swap, 96 tasks. Require 12-GiB
MemAvailable, at least 3.5-GiB total physical reserve, 40-GiB persistent free disk,
AC and no competing QE jobs. Retain normal system-wide swap and power settings.

Proposed **1800-second total allocation**, starting before staging: QE soft
max_seconds 1350; EXIT by allocation+1500; external stop at +1665 with 15-second
kill escalation; workers gone by +1680 and 120 seconds reserved for finalization.
Earlier EXIT after four iterations. No new allocation receipt has been created.
Stop on fatal error, loss of AC/inhibitor, any swap/OOM/memory.high/memory.max/pids
event, current job RAM ≥10.75 GiB, host available <0.75 GiB, scratch ≥20 GiB or
disk free <20 GiB. Preserve all partials. No retry or automatic limit increase.

**Exact worker command, staging, timer offsets, environment and systemd policy:**
`plans/qe75-rho-diagnostic-v1/COMMANDS.md`; machine-readable proposal in
`proposal.json` has approval false. The worker command must not run standalone.
A future scientific supervisor must incorporate the tested control correction
below and be reviewed before launch; the old v3 launcher is insufficient unchanged.

Final host snapshot: 14.936-GiB physical RAM, **10.594-GiB available**, 6.060-GiB
free, 4.924-GiB cached, 0.075-GiB reclaimable slab; zram 8 GiB, unused;
213.539-GiB persistent disk free. Cached memory is partly reclaimable and already
accounted for in MemAvailable; do not add it again. **AC offline**, and available
RAM below the proposed gate. No applications closed or cache dropped. A future
launch needs fresh resources, AC connected and the lid kept open.

## Independent non-QE execution-control checks — completed

Final script: `scripts/qe75_control_checks_v3.py`; evidence:
`evidence/qe75-control-checks-v3/`. Three inert Python processes per case, in
different process groups, deliberately ignored SIGTERM and flushed partial logs.
No MPI/QE/UMA was invoked; no deliberate system suspend or system-clock change.

| Final test | Elapsed seconds | Result |
|---|---:|---|
| Absolute deadline + termination escalation | 10.801 | All workers gone; three partial logs retained |
| Controller SIGSTOP interruption | 11.532 | Independent timer killed entire cgroup; receipt unchanged |
| Injected late-resume clock condition | 2.851 | Existing workers stopped; expired receipt refused new work |

Original allocation receipts were hash-checked unchanged. Effective limits were
checked at runtime (11/10 GiB, zero swap, 96 tasks, OOM group). The task-owned
`sleep:idle` **block** inhibitor and owner PID were verified repeatedly through
worker cleanup. An injected post-workload exception exercised the release path.
Final checks confirmed no dummy or QE/MPI workers, no task inhibitor, and no
task-specific runtime overrides. All evidence and partial output are retained.
This verifies components and simulated interruption behavior, not real suspend
recovery, a production QE integration, or protection against power loss/forced
privileged suspend. [systemd inhibitor semantics](https://www.freedesktop.org/software/systemd/man/250/systemd-inhibit.html).

Earlier non-QE v1/v2 checks exposed a Fedora-specific issue:
`/usr/lib/systemd/user/service.d/10-timeout-abort.conf` overrides a transient
`TimeoutStopFailureMode=kill` setting. Effective abort mode caused SIGABRT/core
handling; those logs and failures remain in their versioned evidence directories.
The final v3 check used a temporary **unit-specific runtime drop-in**, verified
effective `TimeoutStopFailureMode=kill` / `FinalKillSignal=SIGKILL` before workers
started. Final units ended with expected timeout/SIGKILL (status 9), empty cgroups.
Only these task-owned overrides were removed after cleanup. Fedora's global
drop-in, power settings and unrelated inhibitors/services were not changed.

## Exact next decision

Review the 625-Ry diagnostic's limited sensitivity and memory margin, then approve
or decline that **specific one-run proposal**. A focused question for a QE/PP
expert, with actual input/output excerpts, is saved in
`plans/qe75-rho-diagnostic-v1/EXPERT_QUESTION.md` and has not been sent. Expert input
is needed before declaring persistent negative charge harmless; the current
source review alone cannot do that. If a larger-grid probe is needed, use a
separately verified larger-memory allocation rather than relaxing local limits.

The pending unchanged first-geometry four-hour authorization remains unused.
No scientific run, restart, second geometry, convergence study, UMA or refit has
occurred in this work. Phase 3 remains incomplete.
