# Fedora 80/625-Ry diagnostic — terminal result, 2026-10-08

**ONE authorized diagnostic executed. Four SCF iterations completed; SCF did not
converge. Authorization consumed. No accepted scientific energy or final forces.**

## Comparison with archived 80/600 Ry

The negative-charge diagnostic is integrated negative valence pseudocharge, in
electrons; the SCF error is a separate quantity in Ry. Neither 0.1 nor 0.522
electrons is used as an acceptance threshold.

| Stage | Negative charge, 600 Ry | Negative charge, 625 Ry | SCF error, 600 Ry | SCF error, 625 Ry |
|---|---:|---:|---:|---:|
| Initial | 0.3659 | 0.3659 | — | — |
| 1 | 0.3741 | 0.3741 | 20.00902028 | 20.00912607 |
| 2 | 0.3836 | 0.3836 | 2.51087335 | 2.51084927 |
| 3 | 0.3887 | 0.3887 | 0.66475787 | 0.66475088 |
| 4 | 0.3940 | 0.3940 | 0.26218816 | 0.26218300 |

All second negative-charge components are zero. The five observations agree at
QE's printed precision; this is not proof of exact equality of the densities.
The modest cutoff increase produced no observed reduction of this diagnostic.
SCF-error trajectories are very similar and decreasing, but the final error
remains far above `conv_thr=1d-8 Ry`. No failed-diagonalization or fatal warning
was reported. Persistent negative-charge diagnostics remain unresolved.

| Representation | Archived 600 Ry | Actual 625 Ry |
|---|---:|---:|
| Dense FFT | 225 × 225 × 225 | 225 × 225 × 225 |
| Dense Gamma G-vectors | 1,902,004 | 2,022,032 |
| Smooth FFT | 160 × 160 × 160 | 160 × 160 × 160 |
| Smooth Gamma G-vectors | 741,079 | 741,079 |

This matches the offline prediction: 6.31% more density G-vectors but unchanged
real-space FFT dimensions. A null result here cannot exclude sensitivity to a
larger cutoff or a finer FFT grid. It does not establish accurate energies,
forces, pseudopotential suitability, cutoff/k-point convergence or UMA accuracy.

## Controlled inputs and initialization

- The full executed input matches archived v3 byte-for-byte after only
  `ecutrho=600` → `625` and execution-control `max_seconds=12948` → `1350`.
- Same exact 127-atom first water complex, atom order/cell, five pinned SSSP UPFs,
  QE 7.5 build, 80-Ry wavefunction cutoff, Gamma, PBE-D3(BJ), dispersion version 4
  with threebody false, charge 0, nspin 1, fixed occupations and convergence target.
- Same CG, mixing_beta 0.3, mixing_ndim 4, disk_io high, verbosity high and
  electron_maxstep 200. Four MPI ranks bound to distinct physical cores 0–3,
  one compute thread each. No previous scratch/checkpoint reused.
- Both runs use the same default atomic starting density and atomic+random
  starting wavefunctions. Both print starting charge 521.9847 renormalized to
  522.0000 and 457 randomized atomic wavefunctions. The new output/XML confirms
  522 electrons and 261 bands. Source review is in the diagnostic plan and the
  retained QE 7.5 `read_namelists.f90`, `wfcinit.f90`, `random_numbers.f90`.
- The CPU random generator has a fixed default initialization; the thermal-MD
  reseeding branch is not this SCF calculation. Identical controls and startup
  messages make the comparison useful, but byte identity of distributed initial
  wavefunctions was not measured. Changed density G counts and floating-point
  ordering can still affect subsequent iterations. No seed or initialization
  setting was changed to make the comparison appear closer.

Recorded full-package verification and scientific review were reused. Runtime
executable hashes, manifest identity, exact input differences and copied UPFs were
checked. No sealed package, prior output, coordinates or source/build was edited.

## Resources, timing and termination

| Quantity | Measured result |
|---|---:|
| Prelaunch available physical RAM | 12.6067 GiB |
| Peak job cgroup memory | 10,344,960,000 bytes = **9.634495 GiB** |
| Job swap peak | **0** |
| Sampled high/max/OOM/OOM-kill events | **0** |
| Minimum sampled host available RAM | 3.558907 GiB |
| Retained scratch | 544,069,813 bytes, approximately 0.507 GiB |
| QE reported wall time | **17 min 15.19 s** |
| MPI launch through worker cleanup | **17 min 18.019 s** |
| Preparation through automatic cleanup/inhibitor release | **25 min 11.895 s** |
| Final independent host cleanup confirmation | **29 min 49.699 s** after allocation start |

The archived v3 peak was 9.132080 GiB; the earlier v2 peak was 9.313965 GiB.
The 625-Ry measured peak fits below the retained 10-GiB high guard and 11-GiB hard
cap. This measures only this short path, not memory for a fully converged SCF or
force evaluation. The original 96-task limit and zero-job-swap policy were enforced.

QE's printed cumulative timing values at iterations 1–4 were 288.9, 526.4, 791.1,
1034.8 s, versus archived 280.1, 513.6, 771.3, 1008.0 s. These observations are not
a reliable full-convergence runtime prediction. No other application was closed
or restarted to obtain this result; normal power and system swap settings remain.

Allocation was fixed at **10:09:41.465532–10:39:41.465532 UTC**, including controller
preparation and its dummy check. This was a newly explicitly authorized window;
the earlier preparation-only hold and its original receipt remain preserved.
The current deadline was never reset or extended.

The scheduled EXIT timer fired at allocation +1500 s. The controller also recorded
the graceful request at +1501.216 s. QE completed iteration 4, printed
`Program stopped by user request` and `Calculation stopped in scf loop at iteration # 4`,
then wrote restart data and `JOB DONE`. No fifth iteration started. The external
stop at +1665 s and 15-second kill escalation were not needed for the real job.
Worker service exit status was **0**, with `Result=success` for process execution.

**Process success and JOB DONE do not mean scientific SCF success.** XML records
`convergence_achieved=false`, `n_scf_steps=4`, and `exit_status=255`. Its energy
quantities use Hartree: cutoffs 40/312.5 Ha correspond to 80/625 Ry; its SCF error
0.1310914978 Ha agrees with approximately 0.262183 Ry. No final forces are present.
Partial energies are retained solely as raw diagnostic evidence.

## Controller test and cleanup

The interrupted controller check was completed with the reviewed Fedora
unit-specific `TimeoutStopFailureMode=kill` / `FinalKillSignal=SIGKILL` override.
Dummy02 passed in 31.075 s: its independent deadline killed three processes in
separate process groups while guardian monitoring was paused; partial logs and
the original receipt remained intact. The 10-GiB high-event stop rule was checked
directly. Prior successful component tests were reused; no extra scientific runs.

The real controller ran as a separate user guardian service under a verified
task-owned `sleep:idle` block inhibitor. Periodic logs retain inhibitor ownership,
AC, clocks, memory/events, tasks, scratch and SCF status. The inhibitor stayed
active through worker cleanup and was released afterward. Final host inspection
confirmed no QE/MPI workers, no task inhibitor, inactive worker/guardian/timers,
and removal of the task's temporary runtime override. No suspend/hibernate entries
were found during the allocation. The earlier charger interruption was user-caused
and explained; it was not treated as evidence of a persistent hardware fault.

## Evidence and next decision

- Main assessment, accounting, control review, allocation, postflight and hashes:
  `evidence/qe75-rho625-run02/`.
- Full input, stdout/stderr, periodic status/resources, five UPFs and retained
  scratch: `local/qe75-rho625-v1/run02/`; **29 raw files hashed**.
- Scratch includes XML, charge density, PAW data, distributed wavefunctions,
  mixing files and restart_scf files. They are preserved, not certified here as a
  portable restart or authorization to resume.
- Successful adapted dummy: `evidence/qe75-rho625-controller-dummy02/` and
  `local/qe75-rho625-v1/dummy02/`.
- Controller/launcher/assessment: `scripts/qe75_rho625_v1.py`,
  `scripts/launch_qe75_rho625_v1.py`, `scripts/assess_qe75_rho625_v1.py`.
- Consumed configuration: `configs/qe75-rho625-v2.json`. Exact executed commands
  are retained in `guardian-launch.json`, `worker-launch.json`, and
  `execution-started.json`. Do not rerun them.

**Recommendation: obtain focused QE/pseudopotential expert review of this paired
600/625-Ry evidence before authorizing a longer SCF or a larger-grid calculation.**
The concrete question is whether the unchanged integrated negative pseudocharge
at fixed FFT dimensions is consistent with this mixed USPP/PAW set, and what
larger-grid comparison would be needed to establish numerical adequacy. The
current local test establishes bounded early-SCF resource feasibility and no
observed negative-charge reduction for this modest cutoff change; it does not
settle that question. No further calculation, second geometry, UMA or refit was
launched. Phase 3 remains incomplete.
