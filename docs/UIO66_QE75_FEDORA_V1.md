# Fedora continuation: QE 7.5 environment, revision 1

Current update: the [single initialization test completed](UIO66_QE75_FEDORA_INIT01_RESULTS.md).
The package transfer is verified and one-test authorization is consumed.
The preparation/blocked-state notes below are historical. No full SCF is authorized.

2026-10-06. **Environment preparation only; no scientific QE/UMA calculation.**
This continues the Windows project at Git commit
`12cc0654532209c92fa673ab31dba012df566447`. The latest scientific state is the
2026-10-05 sealed v2 preparation, not the older ACTIVE Kaggle entries.
Phase 3 remains incomplete: sampling failed stability criteria, matched diagnostics
support incomplete relaxation/configuration sensitivity, and UMA accuracy is unresolved.
All DFT values remain absent. Proton correspondence is unresolved; preserve the model.
Four missing UMA host single points remain a separate task.

## Local findings

|Item|Observed|
|---|---|
|OS|Fedora Linux 45 Workstation **Prerelease**, x86_64|
|CPU|AMD Ryzen 5 5500U; 1 socket, 6 physical cores, 12 logical threads|
|RAM|16,037,445,632 bytes = 14.94 GiB; about 7.8 GiB available at initial inspection|
|Swap|8 GiB zram; compressed RAM, not an extra 8 GiB of physical RAM|
|Persistent Linux storage|Btrfs `/dev/nvme0n1p5`, shared root/home; about 217 GiB free initially|
|Temporary storage|`/tmp` is RAM-backed tmpfs; unsuitable for the build/scratch allocation|
|Windows|243.2 GiB BitLocker partition, unmounted; not accessed or modified|
|Initial software|No `pw.x`, MPI, GCC/GFortran, make or CMake on PATH|

Raw initial inventory: `evidence/qe75-fedora-v1/initial_inventory.json`.
Availability changes with applications and filesystem use. Root and home share free
space; do not count them twice. No boot, partition, swap, or mount changes were made.

## Scientific package transfer is still required

The clone has no `artifacts/` or `data/external/` directory. These are ignored by Git.
Searches of accessible home/mount locations found no QE v2 ZIP or receipt.
The newest documents are present, but **the sealed scientific package has not been
verified on Fedora**. This is missing data, not evidence of a corrupt package.

Transfer the original Windows files to these repository-relative destinations:

- `artifacts/phase3/UIO66_Frozen_DFT_QE75_v2.zip`
- `artifacts/phase3/uio66_frozen_dft_v2_qe75_receipt.json`
- Unpacked package at `artifacts/phase3/uio66_frozen_dft_v2_qe75/`

Expected ZIP SHA256:
`4ea11e147c529d8b893d2131c06812ec5978b24f0c7d8905c116c22e4e6d0554`.
Verify it **before extraction**. Preserve the receipt and all historical path strings.
Do not regenerate the sealed package from incomplete source data. The Fedora checker
verifies the ZIP, receipt pins, and each of 140 files in both archive and unpacked tree:

```bash
python3 scripts/qe75_fedora_v1.py package --output evidence/qe75-fedora-v1/package-check02.json
```

The actual initial failure is saved in `evidence/qe75-fedora-v1/package-check01.json`.
No new source/UPF download substitutes for the missing sealed inputs.

## Reproducible software setup

Official QE source:
`https://gitlab.com/QEF/q-e/-/archive/qe-7.5/q-e-qe-7.5.tar.gz`.
Downloaded to `local/qe75-fedora-v1/q-e-qe-7.5.tar.gz`; local SHA256:
`7e1f7a9a21b63192f5135218bee20a5321b66582e4756536681b76e9c59b3cc8`.
This records downloaded bytes from the official HTTPS origin, not an independently
published signature. Official tag object: `17975e6f2ba19aec6f50d99c1fc677361d7c8b3a`;
peeled source commit: `770a0b2d12928a67048e2f3da8d10d057e52179e`.
Dependency commits come from the release's `external/submodule_commit_hash_records`.
The source-only Wannier90 checkout uses Git blob filtering and sparse `src/`
checkout at the same recorded commit. An interrupted large full fetch is retained
as `external/wannier90-interrupted-full-fetch/`; it is not used in the build.
See the [official CMake instructions](https://www.quantum-espresso.org/Doc/user_guide/node10.html)
and [QE 7.5 source README](https://gitlab.com/QEF/q-e/-/tree/qe-7.5).

Dependency installation command requested through normal escalation:

```bash
sudo dnf install -y gcc gcc-gfortran gcc-c++ make cmake openmpi openmpi-devel fftw-devel openblas-devel lapack-devel time
```

The agent's sudo attempt could not read a password. Dependencies subsequently became
visible from installation in the user's terminal. Verified RPMs include GCC/GFortran
16.2.1, Open MPI 5.0.10, CMake 4.3.0, GNU make 4.4.1, FFTW 3.3.10, OpenBLAS 0.3.34,
GNU time 1.9. Separate `lapack-devel` was absent; OpenBLAS supplies LAPACK.

Source retrieval and build commands (software only; preserve any failed partial
download for inspection instead of automatically retrying it):

```bash
bash scripts/fetch_qe75_fedora_v1.sh
bash scripts/build_qe75_fedora_v1.sh
```

The script selects explicit Fedora MPI compiler wrappers, MPI on, OpenMP off,
FFTW3 and OpenBLAS, Release build, two compilation jobs. No GPU, HDF5, LibXC or
ScaLAPACK is required for this PBE pilot. `CMAKE_POLICY_VERSION_MINIMUM=3.5`
allows older bundled dependency CMake files under CMake 4; source/scientific settings
are not rewritten. Build logs have unique UTC directories below
`evidence/qe75-fedora-v1/`. Local source/build/evidence are ignored by Git.

**Build complete** with the recorded toolchain, without a QE source patch.
Executable: `local/qe75-fedora-v1/build/bin/pw.x`.
SHA256: `0d1f6d9ac37a99f4f3fb72359bd3b6ffe54594cea92ed46a596238fa9283d8f1`.
The finalized build wrapper exited 0; `evidence/qe75-fedora-v1/build-final-wrapper.log`
retains the result. Earlier compiler warnings and an initial wrapper failure after
editing the running shell script are preserved in the versioned build logs.
Build uses QE's built-in XML support (`QE_ENABLE_FOX=OFF`), GFortran `-O3` and
QE's upstream `-fallow-argument-mismatch` flag. All linked libraries resolve.
MPI launcher: `/usr/lib64/openmpi/bin/mpirun`. Use explicit paths; Fedora does not
place these MPI wrappers on the default shell PATH.
The runtime also needs `/usr/lib64/openmpi/bin` prepended to PATH and
`OMPI_PRTERUN=/usr/lib64/openmpi/bin/prterun`; the Fedora adapter sets both.
An initial missing-PRRTE error and subsequent sandbox local-socket restriction were
resolved using those explicit paths and the normal escalation mechanism.
The software-only C probe passed with ranks 0–3 on physical cores 0–3
(logical sibling pairs 0/1, 2/3, 4/5, 6/7), one host and correct collective sum 6.
Source: `scripts/qe75_mpi_probe.c`; output: `evidence/qe75-fedora-v1/mpi-probe.log`.

```bash
python3 scripts/qe75_fedora_v1.py software --output evidence/qe75-fedora-v1/software-check06.json
```

**Startup passed**, recorded in `evidence/qe75-fedora-v1/software-check05.json`;
QE/MPI executable hashes are pinned in `configs/qe75-fedora-v1.json`.
The old `pw.x -h`/exit-0 preflight assumption is incorrect for this source release:
`Modules/command_line_options.f90` has no help handler. The revised check explicitly
uses `pw.x -in /dev/null`, requires the 7.5 banner and the sole expected
`read_namelists (2): could not find namelist &control` rejection (exit 1), and rejects
socket/other errors or SCF iterations. It supplies no structure/PP. Empty-input
`CRASH`/temporary files and output logs are retained in isolated evidence directories.
It also calls MPI `--version` and `ldd`. This is **startup verification only**, not
input validation or a successful DFT calculation. MPI local sockets require the
normal tool escalation when running from the agent sandbox.
Any system library/package update requires repeating software/link checks.

## Resource revision and proposed next resource test

The original `scripts/run_qe_water_pilot.py` and sealed package are untouched.
Its preflight, runtime memory/disk checks, and parser call hardcode the proposed
32-rank/64-GiB/100-GiB external allocation. Do not supply a fake allocation or
pass the Fedora config to it. A full local pilot launcher is **not yet approved or
validated**; revise those runtime/parser assumptions together after memory evidence.

`configs/qe75-fedora-v1.json` proposes **initialization only**: 4 MPI ranks bound to
physical cores, one thread each, 8 GiB cgroup RAM cap, 7 GiB memory pressure threshold,
zero swap, and a 600-second ceiling including termination grace. Four of six cores
leave CPU headroom. Require 10 GiB MemAvailable before launching so the OS retains
headroom; current availability does not meet this gate. Close large applications
and recheck rather than treating zram as usable pilot RAM.

Fedora user-service checks with tiny non-QE processes confirmed the exact proposed
8-GiB cap, 7-GiB high threshold, zero swap, 585-second runtime and 15-second kill
grace. Evidence: `evidence/qe75-fedora-v1/cgroup-profile-check.log`.
A separate 2-second RuntimeMaxSec terminated a 30-second sleep at 2.019 seconds
with SIGTERM. This tests the enforcement mechanism, not QE memory use.

Once package/build/binding checks pass, review and approve **only** this bounded test:

```bash
python3 scripts/qe75_fedora_v1.py stage-smoke --output evidence/qe75-fedora-v1/stage-smoke01.json
# Only after explicit initialization approval is recorded in the Fedora config:
systemd-run --user --wait --pipe --unit=qe75-init01 \
  --working-directory="$PWD" \
  -p MemoryHigh=7G -p MemoryMax=8G -p MemorySwapMax=0 \
  -p RuntimeMaxSec=585s -p TimeoutStopSec=15s -p KillMode=control-group \
  -p SendSIGKILL=yes -p OOMPolicy=kill \
  /usr/bin/python3 "$PWD/scripts/run_qe75_fedora_init_v1.py"
```

Not executed. The runner refuses while `initialization_execution_approved=false`.
Staging retains an exact baseline copy and adds **only** `nstep=0` to the first
water complex input; positions, atom order, cell, 80/600 Ry, Gamma, charge/spin,
occupations, pairwise D3(BJ), and electronic convergence are unchanged. No SCF loop
is authorized. The runner checks package/executable/input hashes and cgroup limits,
uses a new persistent `local/qe75-fedora-v1/smoke01/`, retains all partials, and
does not retry. Inspect cgroup/journal records after an external kill.

Storage: require 30 GiB free before launch; monitor the entire smoke directory every
second and stop at 10 GiB or below 20 GiB filesystem free. This is a sampled stop,
**not a filesystem quota**; transient overshoot is possible. RAM and wall time are
enforced by the user service. The monitor stops workers at 570 seconds, TERM then
KILL after 15 seconds; systemd independently stops the entire cgroup at 585 seconds,
with a final 15-second grace. No success or continuation on timeout/OOM/error.

QE's `PW/src/run_pwscf.f90:149` uses `nstep=0` to print setup/memory information,
write initialization XML, and set status 255 before `init_run`/SCF. Review this
expected initialization status separately from MPI failure; never classify it as
a converged energy. Confirm 522 electrons, 127 atoms, 4 MPI ranks, one thread,
correct PP/cutoffs/dispersion, no SCF iterations and no reported input errors.
If an error occurs, retain evidence and stop; do not alter scientific inputs.
This agrees with the [official nstep documentation](https://www.quantum-espresso.org/Doc/INPUT_PW.html).

Initialization estimates do not establish peak Davidson/PAW/SCF memory, sustained
laptop thermals, full runtime, convergence or energy/force accuracy. Whether the
unchanged pilot fits is unresolved. If it exceeds local resources, obtain an
external allocation; do not lower cutoffs or shrink the structure.

## Retrieval and checks

Read latest sections of `AGENTS.md`, `MODEL_HANDOFF.md`, `.planning/STATE.md`, and
`docs/UIO66_QE75_WATER_PILOT_V2.md`. Graphify CLI was absent. Used bounded exact
nodes from the existing graph for `preflight`, `execute`, `parse_result`, and
`verify_package`, then verified their source pointers. No graph rebuild, bulk graph
dump, notebook/history/trajectory loading, or Windows interpreter repair.
Graph is unchanged and does not yet index this Fedora revision.

Six new offline stdlib guard tests pass:
`python3 -m unittest tests.test_qe75_fedora_v1 -v`.
Python compilation, shell syntax and Git whitespace checks pass. The initialization
runner's false-approval guard rejects before launching a process. Full repository
tests were not rerun; initial Linux environment lacks project scientific dependencies.
Historical 91-test result belongs to the sealed Windows preparation.

Exact next decision: restore and hash-verify the sealed artifacts and recover at
least 10 GiB available physical RAM, then decide whether to authorize the initialization-only
test under the above limits. **No two-complex SCF execution approval exists.**
