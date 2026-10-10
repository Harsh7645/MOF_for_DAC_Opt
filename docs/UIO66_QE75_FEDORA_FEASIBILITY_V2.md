# Fedora QE memory feasibility v2 — 2026-10-07

## Scope and provenance

The user authorized closing optional applications safely and ONE first-water-complex
SCF resource test, at most 600 seconds, only with a safe physical-memory reserve.
Zen closure was separately confirmed: no unsaved work or active task. Only its
verified user-owned main process received SIGTERM; it exited. No force kill,
service stop, cache dropping, system swap change, application restart, or QE rebuild.

The sealed ZIP, receipt and all 140 extracted files passed verification again.
Originals and `configs/qe75-fedora-v1.json` remain unchanged. The prior initialization
is separate and its authorization remains consumed. No graph rebuild; Graphify
was unavailable, so retrieval used bounded source reads and exact text searches.

## Machine and memory recovery

Ryzen 5 5500U: six physical cores, twelve logical CPUs. Physical RAM 14.936 GiB;
8 GiB zram is not counted as RAM. Zen was the largest optional application; other
large processes belonged to the user desktop/session/Codex or root system services
and were preserved. Before/after owner and RSS inventories are retained locally.
Immediately before closure MemAvailable was 10.001 GiB; after closure 12.137 GiB
(recovered 2.136 GiB). Anonymous memory fell from about 3.39 to 1.42 GiB, while
cache stayed about 6.2 GiB. MemAvailable already includes reclaimable cache.
Launch preflight: 12.345 GiB available and about 213.67 GiB persistent disk free.
No pre-existing QE/MPI jobs; system zram usage zero.

## Why a bounded SCF test was reasonable

The earlier 12.67-GiB QE estimate exceeds the old 8-GiB initialization cap. The
0.7905-GiB initialization peak did not measure SCF. Review of the unmodified QE7.5
source reproduced the old estimate as 12.669 GiB. `memory_report.f90` independently
maximizes projector-pair count and species atom count: Zr supplies 171 pairs,
carbon supplies 48 atoms. `addusforce.f90` instead allocates/frees these workspaces
inside the species loop: Zr has only six atoms. Thus the estimate combines maxima
that do not coexist for this structure. Actual per-species force workspace is
estimated at 5.74 GiB aggregate, versus 9.31 GiB for the combined-max formula.

With disk-resident mixing, base plus species-maximum workspace is approximately
8.64 GiB, before implementation/library/allocator overhead. Initialized G-shell
storage and the report's real-versus-complex `vg` discrepancy add further uncertainty.
This analytical inference supports a protected test; it is not a measured bound.
Relevant source files were byte-compared with the pinned official source archive;
formulas, hashes and assumptions are in `evidence/qe75-fedora-feasibility-v2/memory-source-audit.json`.

[Official QE input documentation](https://www.quantum-espresso.org/Doc/INPUT_PW.html)
describes lower-memory conjugate-gradient diagonalization and disk I/O options.
The [parallelization guide](https://www.quantum-espresso.org/Doc/user_guide/node20.html)
describes distributed FFT/G-vector work. Four MPI ranks on distinct physical cores
were retained; a single Gamma point provides no useful extra k-point pools.

## Separately versioned execution configuration

- `configs/qe75-fedora-feasibility-v2.json`
- `scripts/qe75_feasibility_v2.py`: prepare by default; explicit guarded execution.
- `scripts/launch_qe75_feasibility_v2.sh`: systemd cgroup launch, no retry.
- `local/qe75-fedora-feasibility-v2/run01/`: execution copies, logs, accounting, scratch.

Only the execution copy changes: `diagonalization='cg'`, `mixing_ndim=4`,
`disk_io='high'`, `verbosity='high'`, `max_seconds=540` (was 13800).
CG trades speed for memory; shorter mixing history can affect convergence behavior.
The convergence criterion, mixing beta, 200-step ceiling, exact cell/coordinates,
UPFs, 80/600 Ry, PBE-D3(BJ) pairwise convention, Gamma, charge/spin, occupations and
force request are preserved. No `nstep=0`; this test performs SCF work.

Actual launch-time cgroup checks enforce 11 GiB MemoryMax, 10 GiB MemoryHigh,
MemorySwapMax=0, OOM group kill and TasksMax=96. Total physical reserve is 3.936 GiB;
launch requires at least 12 GiB MemAvailable and 40 GiB persistent free disk.
The unit runtime limit is 585 seconds plus 15 seconds shutdown; monitor stops at
570 seconds, then TERM/wait10s/KILL/wait5s. QE's 540-second soft stop is additional.
Other stop conditions: cgroup use >=10.75 GiB, host MemAvailable <0.75 GiB,
scratch >=20 GiB, persistent free <20 GiB, or QE/MPI error. Storage thresholds are
sampled each second, not a filesystem quota; memory/process/time limits are enforced.

Ranks bind to cores 0–3 (logical sibling pairs 0–1, 2–3, 4–5, 6–7), leaving two
physical cores outside the computation. OMP/OpenBLAS/MKL threads are set to one.
MPI helper threads exist: live inspection showed three OS threads per QE rank and
16 total cgroup tasks, with each rank confined to its own physical core.

Offline safety checks verified unchanged scientific input blocks, malformed-input
rejection, RAM/reserve/storage gates, and rejection of consumed/unapproved execution.
No extra QE invocation or initialization was used for these checks.

Commands used (historical; do not rerun after authorization consumption):

```bash
python3 scripts/qe75_feasibility_v2.py
bash scripts/launch_qe75_feasibility_v2.sh
```

## Outcome

**ONE test completed; authorization consumed. No scientific result accepted.**

| Measurement | Result |
|---|---:|
| SCF iterations | 2 completed; iteration 3 started |
| Convergence / force stage | Not reached / not reached |
| Kernel cgroup peak | 10,000,793,600 bytes = 9.313965 GiB |
| Maximum sampled test swap | 0 bytes; service also reports 0B |
| Lowest sampled host MemAvailable | 3.791420 GiB |
| Controller elapsed | 570.999 s |
| Entire systemd service | 571.164 s (9 min 31.164 s) |
| CPU time (service) | 2254.282 s across ranks/helpers |
| Scratch growth | 0 to 436,585,008 bytes = 0.406601 GiB |
| Accounted block I/O | read 53,207,040 B; written 461,840,384 B |
| OOM / memory.max / memory.high events | 0 / 0 / 0 |
| Process-limit events | 0 |

The monitor reached its 570-second stop and sent TERM to its MPI process group.
MPI exited with code 1; the controller completed normally. Systemd's wrapper
`success`/exit0 means the monitor finished, **not SCF success**. No `JOB DONE`,
convergence, final forces or complete XML was produced. QE's soft 540-second limit
did not finish the running diagonalization before the monitor stop. Eight partial
scratch files (four wavefunction, four mixing files) remain; restartability is unverified.
All stdout/stderr and second-by-second resource samples are retained. No partial
energies are promoted into the scientific result pipeline.

Postflight: no `pw.x`, `mpirun`, `prterun` or Zen processes; every recorded worker
PID is absent, the unit is inactive/dead and its cgroup is removed. Host available
RAM was 12.635 GiB; persistent disk free 228,987,531,264 B
(~213.261 GiB). System zram contained 49,152 B afterward from outside this test;
the test cgroup had zero swap and system-wide swap settings were never changed.
The measured cgroup peak includes charged file cache and helpers, not just summed
rank RSS. A live snapshot showed 16 tasks and distinct core binding for all ranks.

Basis/grid evidence: 127 atoms, 522 electrons, 261 Kohn–Sham states, Gamma;
dense225³ / 1,902,004 G-vectors; smooth160³ / 741,079 G-vectors. The printed
full PW distribution sums to 185,045. No final XML `npwx` value is available.
The modified input still printed a conservative QE estimate of >12.22 GB;
that estimate uses the same independent species maxima described above.

## Conclusion and exact next decision

Closing Zen recovered enough physical memory to run this **bounded early-SCF test**.
Early SCF through two completed iterations fit under the 11-GiB cap with about
1.69 GiB peak headroom; time, not memory, ended this test. This is more informative
than repeating initialization. It does not establish full convergence time,
later-iteration peak, final force-stage peak, restartability, numerical convergence,
or feasibility of the second geometry. The source estimate is not a substitute for
measuring the unvisited stages. CG performance here was slow (two iterations in
about nine minutes); extrapolating a full SCF duration is unreliable.

**Execution is disabled.** Both the new config and old initialization config have
no active execution approval. Preserve the exclusive one-test marker. No retry,
limit increase, second geometry or full pilot was launched. The post-test shell
wrapper also refuses an existing marker and refuses overwriting its console log.
The exact next decision requires a separate user-reviewed completion allocation
(local with a new time budget and retained memory reserve, or an external machine
with more physical RAM). Do not schedule any continuation automatically. Phase3,
UMA accuracy, proton correspondence and scientific cutoff convergence remain unresolved.

## Retained handoff and evidence

- Concise current pointer: `docs/UIO66_QE75_FEDORA_HANDOFF.md`.
- Before/after app/process/memory inventory, source audit, authorization, live/final
  accounting, offline-check record and assessment: `evidence/qe75-fedora-feasibility-v2/`.
- Inputs, logs, resource samples, result and all partial scratch:
  `local/qe75-fedora-feasibility-v2/run01/`.
- `execution-file-hashes.json` pins code/input actually used; the shell refusal
  guard was added afterward. `raw-file-hashes.json` pins all retained run files.
  `evidence-file-hashes.json` pins supporting evidence. These directories are
  Git-ignored and must be preserved separately; documents/config/scripts are tracked.
