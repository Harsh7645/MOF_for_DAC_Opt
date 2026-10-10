# Fedora first-complex completion v3 — 2026-10-08 IST

## TERMINAL — interrupted by system suspend; no further execution

ONE attempt was explicitly authorized, including a clean start if the old checkpoint
was invalid. Launch approval is consumed; no retry, second geometry or limit increase.
Final assessment: `evidence/qe75-fedora-completion-v3/assessment.json`.
The last periodic status is retained and is not an active-job indicator.

## Pre-run review

Prior estimated SCF errors:20.00902028→2.51087335Ry vs1e-8Ry threshold.
Prior per-iteration diagonalization ethr:1e-2→3.83e-3Ry; average inner iterations2.9→3.5.
Cumulative QE-reported CPU times31.2,289.3,533.2s. No failed-diagonalization warning;
negative-density diagnostics0.3659,0.3741,0.3836 were present and remain a review item.
Two iterations do not support a reliable full-completion time estimate.
Prior stop was externalTERM at570s, MPIexit1; no JOB DONE or clean checkpoint.
All21previous raw files match their retained SHA256 manifest.

Only four distributed wavefunction and four mixing files existed; no saved XML,
charge density or clean-stop state. QE7.5 documentation requires a clean stop and
compatible processor/parallel layout for `restart_mode='restart'`.
[Official input documentation](https://www.quantum-espresso.org/Doc/INPUT_PW.html)
and the pinned source `PW/Doc/INPUT_PW.def:193` support this decision.
Thus **one clean start** uses the same sealed first input; zero previous scratch
files are copied. No speculative restart invocation was performed.

## Fixed allocation and settings

Receipt: `evidence/qe75-fedora-completion-v3/allocation.json`, recorded before preparation.
Start2026-10-07T20:08:36.034359Z; deadline2026-10-08T00:08:36.034359Z (05:38:36IST).
Total14400s includes preparation and finalization. No deadline reset.

- Exact frozen first water-complex input, all140packagefiles and pinned QE/MPI hashes verified.
- Same four ranks on physical cores0–3, one compute thread (MPI helpers remain), CG,
  mixing_ndim4,mixing_beta0.3,disk_iohigh,verbosityhigh,conv_thr1e-8,electron_maxstep200.
- Geometry/cell/UPFs/80and600Ry/PBE-D3BJpairwise/Gamma/neutral/nspin1/fixed occupations
  and requestedforces unchanged. Only max_seconds changes relative to prior v2 input.
- Actual cgroup11GiBhard/10GiBhigh,MemorySwapMax0,OOMPolicykill,TasksMax96 verified.
- At least12GiBavailable RAM,3.5GiBtotal reserve,40GiBdisk required at launch.
  No applications stopped this turn; system-wide swap settings unchanged.
- At23:48:36UTC(05:18:36IST), independent timer creates `scratch/prefix.EXIT`;
  controller also requests it, and QE max_seconds provides an additional soft stop.
  `Modules/check_stop.f90` confirms wall-time/EXIT checking; `c_bands.f90`,
  `electrons.f90` and `run_pwscf.f90` support clean-stop state/XML saving at checkpoints.
- Independent external timer stops the whole service at00:03:21UTC(05:33:21IST);
  KillModecontrol-group,TimeoutStop15s,SendSIGKILLyes enforce termination by00:03:36UTC.
  RuntimeMaxSec also bounds the unit. Final five minutes reserved for accounting/handoff.
- Controller stops slightly earlier on the external deadline and on fatal errors,
  swap/OOM/memory/process-limit events, memory>=10.75GiB,hostavailable<0.75GiB,
  scratch>=20GiB orpersistentfree<20GiB. Storage thresholds sampled every2s, not a quota.
  Two-second samples retain convergence/error, task count, cache/anon memory breakdown,
  cgrouppeak/swap/events, disk and elapsed allocation time. Atomic status.json updated.

Config `configs/qe75-fedora-completion-v3.json`; controller `scripts/qe75_completion_v3.py`.
Historical commands (do not rerun):

```bash
python3 scripts/qe75_completion_v3.py
python3 scripts/qe75_completion_v3.py --launch
```

Graphify unavailable; bounded source retrieval used. No graph or QE rebuild.
Prior and sealed packages/evidence preserved. Source hashes checked against the official
QE7.5 archive. Offline guard/input-equivalence checks passed; no extra QE invocation.

## Outcome

**Unconverged. Four iterations completed; iteration5 started. Not ready for independent
scientific assessment. No final energy/forces accepted; no retry or second geometry.**

| Evidence | Observed result |
|---|---|
| SCF error estimates (Ry) | 20.00902028,2.51087335,0.66475787,0.26218816 |
| Required threshold | 1e-8 Ry, unchanged and unmet |
| Diagonalization | No failed-eigenvalue/diagonalization warning reported |
| Other diagnostics | Negative-density reports persisted (last0.3940); C/O atomic-wavefunction renormalization diagnostics retained |
| Peak cgroup RAM | 9,805,496,320 B =9.132080GiB |
| Cgroup swap / memory / PID limit events | 0 /0 /0 |
| Minimum sampled host MemAvailable | 4,221,624,320 B =3.931694GiB |
| Maximum sampled tasks | 16 (four compute ranks plus MPI/controller helpers) |
| Scratch growth | 0→486,793,968B =0.453362GiB |
| Controller awake monotonic runtime | 1096.345859s (18min16.346s) |
| Systemd reported awake service runtime | 1096.548s |
| Service total CPU | 4314.101s across ranks/helpers |
| Preparation before MPI | 227.839745s |
| Real elapsed allocation to worker termination | 27,776.580179s (7h42min56.580s), including suspend |
| Real deadline overrun | 13,376.580179s (3h42min56.580s) |
| Process / controller exit | MPI1 /controller0; controller success is NOT SCF success |

### Suspend and deadline failure

Fedora's `gsd-power` requested automatic suspend at02:00:34IST; the kernel entered
s2idle at02:00:35. The system resumed at09:21:32IST. This spans the scheduled graceful
stop05:18:36, external stop05:33:21 and total deadline05:38:36. Journals confirm both
absolute timer services ran together at09:21:32 when the machine resumed. The
controller independently observed the expired absolute deadline and terminated MPI.
The last two samples show a26,452.394s real-versus-monotonic gap; final stop followed
the resumed sample by about0.199s. Systemd's18-minute runtime excludes the long sleep.

**The requested four-hour real wall envelope was not achieved.** No deadline was
reset or extended, and QE was not executing during system suspend; nevertheless,
processes remained suspended across the deadline and finalization occurred after
resume. The external timers did not wake the machine. No temporary sleep inhibitor
had been installed. Do not present this as four hours of SCF work or as a compliant
four-hour completion. A future attempt requires explicit new authorization and a
verified per-attempt sleep inhibitor or other verified awake allocation; no permanent
power/boot configuration has been changed.

### Output and worker verification

No SCF-converged marker, JOB DONE, saved XML, charge-density file, or final forces.
Eight partial scratch data files and the EXIT marker remain. Restart is still invalid;
do not reuse the fragments as a complete checkpoint. No partial energy was accepted.
Input/UPF/executable/package checks still pass. The offline assessor rejects the
result; its complete-output energy/force/XML checks could not be exercised because
those outputs do not exist. Scientific numerical/physical accuracy remains untested.

Postflight confirms no pw.x/mpirun/prterun, all five recorded MPI/rank PIDs absent,
unitinactive/dead,cgroupgone; both timers inactive and explicitly stopped. System
zram usage0; persistentdiskfree229,386,891,264B. No applications stopped this turn.

Retained paths:

- `local/qe75-fedora-completion-v3/run01/`: input,prior-sealed input copy,pseudo,
  stdout/stderr,resources.jsonl,status,execution marker,result,scratch,graceful-stop request.
- `evidence/qe75-fedora-completion-v3/`: immutableallocation,prior-output/source audit,
  launch plan/timer receipt,hostpreflight,live recovery check,postflightjournal,
  suspend-analysis,assessment,console,timer cleanup and SHA256 manifests.
- `scripts/assess_qe75_completion_v3.py`: offline assessor only, no QE launch.

The original launcher-result receipt is absent after the session interruption;
controller result, systemd console and retained journal provide terminal evidence.
Raw/evidence paths are Git-ignored and must be preserved separately. Previous21v2raw
files and all140sealedpackagefiles remain hash-identical.

### Exact next decision

Execution approval remains false and consumed. Do not rerun v3, reset its allocation,
resume scratch, increase limits or launch another geometry. The next user decision is
whether to authorize a separately prepared, awake first-geometry allocation. It must
address automatic suspend before starting; the memory result alone does not establish
full-SCF/force-stage feasibility. Phase3 and all scientific-accuracy questions remain open.
