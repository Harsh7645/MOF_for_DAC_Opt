# Proposed commands — NOT authorized for execution

No QE launcher was invoked or enabled. These are the exact worker command and
required launch controls for a future reviewed adapter. Do not run the worker
standalone. `proposal.json` has scientific_execution_approved=false. The pending
permission for an unchanged first-geometry run is not permission for this625Ry probe.

## Inputs and staging

Use `rho625.in` for the only proposed new calculation. `rho600.in` is the matched
reference specification; reuse the archived v3 first four iterations instead of
launching another600Ry run. The two proposed inputs differ only in ecutrho.
Relative to v3, their only shared change is max_seconds12948→1350 (time control).
Both retain electron_maxstep200,scf_must_converge=true,conv_thr1e-8.

After separate approval, record an exclusive immutable allocation receipt BEFORE
copying input/potentials or preparing scratch. Proposed total1800s. Stage into a
new directory `local/qe75-rho-diagnostic-v1/rho625/`; refuse any existing run marker.
Copy `rho625.in` as input.in, and copy the exact five files from
`artifacts/phase3/uio66_frozen_dft_v2_qe75_fedora_verified01/pseudo/` into `pseudo/`.
Create empty persistent `scratch/`; verify all file hashes. No restart files reused.

## Exact worker command inside the guarded service

Working directory: `/home/harshsahu/MOF_for_DAC_Opt/local/qe75-rho-diagnostic-v1/rho625`.

```bash
env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1   OMPI_PRTERUN=/usr/lib64/openmpi/bin/prterun   PATH=/usr/lib64/openmpi/bin:/usr/bin:/bin   /usr/lib64/openmpi/bin/mpirun --host localhost:4 -np 4   --map-by core --bind-to core --nooversubscribe --report-bindings   /home/harshsahu/MOF_for_DAC_Opt/local/qe75-fedora-v1/build/bin/pw.x -in input.in
```

Retain stdout.log,stderr.log,exit status,XML/checkpoints,all scratch and hashes.
This command is not a safe standalone launcher and must not be executed now.

## Required guard commands/policy

The outer owner must invoke its supervisor with these exact inhibitor options:

```text
systemd-inhibit --no-ask-password --what=sleep:idle --mode=block
  --who=MOF-QE-rho625 --why="Bounded density-cutoff diagnostic and cleanup"
```

The supervisor is the command argument: it must verify that owner's PID and block
mode through `systemd-inhibit --list --json=short`, then keep the owner alive until
all job workers are confirmed gone and final accounting is saved. If the owner
vanishes or AC disconnects, stop the job. Release on both normal and failure paths.
Keep AC connected and the lid open. Do not alter permanent power settings.

Worker unit: `qe75-rho625-diagnostic-v1.service`. Required systemd-run properties:

```text
-p MemoryMax=11G -p MemoryHigh=10G -p MemorySwapMax=0
-p OOMPolicy=kill -p TasksMax=96 -p CPUAffinity=0-7
-p MemoryAccounting=yes -p IOAccounting=yes
-p RuntimeMaxSec=R -p TimeoutStopSec=15s
-p KillMode=control-group -p SendSIGKILL=yes -p FinalKillSignal=SIGKILL
```

R is floor(start+1665-current_time), computed from the original saved start,
never a new allocation start. Refuse nonpositive R. Independent absolute timers
must use UTC calendar times derived from that SAME receipt (AccuracySec1s):

```text
at start+1500: /usr/bin/touch <work>/scratch/uio66_110111_H2O_s28_f0.010_complex.EXIT
at start+1665: /usr/bin/systemctl --user stop qe75-rho625-diagnostic-v1.service
```

Controller also requests EXIT after four completed estimated-scf-accuracy reports;
a fifth iteration may already start before QE observes it. Compare only matched
initial/first-four observations. max_seconds1350 supplies another graceful stop.
All workers must be gone bystart+1680, leaving120s for finalization inside1800s.
Before continuing after any interruption, compare original wall deadline and
CLOCK_BOOTTIME elapsed time; if expired, terminate the entire cgroup and do not
continue/restart/reset. No automatic retries. A lost guardian must still leave the
external stop active; the inhibitor owner must cover worker cleanup.

Fedora's `/usr/lib/systemd/user/service.d/10-timeout-abort.conf` overrides a mere
transient-unit TimeoutStopFailureMode property. Create a temporary UNIT-SPECIFIC
runtime drop-in under `$XDG_RUNTIME_DIR/systemd/user/<unit>.d/90-qe-stop.conf`:

```ini
[Service]
TimeoutStopFailureMode=kill
FinalKillSignal=SIGKILL
```

Reload user units, then verify the EFFECTIVE mode,kill signal,cgroup limits and CPU
binding before allowing the worker to start. Preserve a copy of that drop-in as
evidence; remove only this run's runtime override after worker cleanup. Do not mask
or change Fedora's global drop-in. This exact override approach passed dummy tests.

Fresh gates:12GiB MemAvailable,>=3.5GiB total RAM reserve,40GiB persistent disk,
AC online,no competing QE jobs,verified package/executable/PP/input hashes.
Monitor every2s: SCF/negative-charge history, cgroup RAM/swap/events/tasks, scratch,
hostRAM/free disk, inhibitor ownership, wall/boot clocks. Stop on any memory.high,
memory.max,OOM,pids or swap event;>=10.75GiB current memory;<0.75GiB host available;
>=20GiB scratch or<20GiB free disk; fatal QE/MPI error. No threshold weakening.

## Verified non-QE command (historical; already completed)

```bash
python3 scripts/qe75_control_checks_v3.py
```

It refuses the existing evidence directory; do not rerun it over retained evidence.
Tests establish control-component behavior, not a completed QE integration test.
An adapted scientific supervisor implementing the above specification must be
reviewed before a future launch; existing v3 QE launcher is not sufficient unchanged.
