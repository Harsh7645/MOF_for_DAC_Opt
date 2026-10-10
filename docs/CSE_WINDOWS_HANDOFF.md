> Historical cluster preparation preserved. As of 2026-10-10, all 14 baseline
> SCFs are complete on Fedora. Use `docs/UIO66_QE75_WINDOWS_BASELINE14_GUIDE.md`
> for current offline work. Old pending terminals/launch steps below are not
> current instructions or authorization; no cluster action is required for analysis.

# Windows to IIT Kharagpur CSE: preparation v1

Updated 2026-10-07. Current endpoint: `23BT10034@10.5.18.100`, port 22.
User confirms CSE, CPU-only scope and successful manual SSH login. This supersedes
the PARAM endpoint ambiguity. Preserve the earlier PARAM draft as historical.
**User authenticated; read-only discovery captured. No compute allocation or DFT result.**

## Verified live discovery (first pass)

User accepted first-use SSH trust and authenticated in the private terminal.
Strict subsequent discovery completed; saved ED25519
`SHA256:9XibnJwLyJezyWcu/PJCFLjIU6PN685P253L1oXCvCo` matches the earlier observation.
This is user-accepted first-use trust, not independent institutional verification.
Evidence: `artifacts/phase3/cse_preparation_20261007/discovery_20261007_143350.txt`.

- Host `master`; uid39101, group `other`; home `/home/others/23BT10034`.
- No `cpupart` in live partition listing. `maspart` is DOWN and refers to master;
  remaining advertised partitions are GPU partitions. None selected for CPU study.
- Account/association queries returned no rows; normal QoS exists. Entitlement and
  billing unresolved; AllowAccounts=ALL and AccountingStorageEnforce=none are not proof.
- Python3.10.12 and Open MPI4.1.2 on PATH. No pw.x on PATH/matching QE module shown.
  Follow-up software inventory still required before declaring QE unavailable.
- Home is NFS with 3.2T filesystem free, not per-user quota. `quota` unavailable.
  No /scratch candidate shown. /data is master-local ext4, not verified shared scratch.
  Backup/quota/retention unknown.
- CR_CORE, task/affinity, proctrack/linuxproc, jobacct_gather/linux: hard memory
  enforcement not established. Memory request/RSS monitor alone do not satisfy guard.

CSE runner now hashes in chunks for Python3.10 compatibility; sealed v2 unchanged.
29 focused tests pass5.93s. Transfer helper opened in user terminal; completion
requires remote verification evidence. No SCF/build/submission authorized.

## First-use access transition (historical)

User reports the friend also has no known-host file and asks to proceed without
independent fingerprint verification. Normal first-use SSH acceptance is now the
chosen route: `connect_and_discover.ps1` opens an interactive prompt with
`StrictHostKeyChecking=ask`; user decides in their terminal. Changed keys remain
blocked. The follow-up discovery uses `StrictHostKeyChecking=yes`. No automatic
key acceptance, checking bypass or institutional-verification claim.

Visible PowerShell helper launched; credential input and any host acceptance
remain in that terminal. At this update, successful authentication/discovery is
not yet confirmed. No compute job or remote directory creation is in the helper.

## Previous access state

Windows OpenSSH `ssh -G` resolves its host records to
`C:\Users\hp\.ssh\known_hosts` and `known_hosts2`; neither is available.
No matching PuTTY cached key was found. User clarified the successful connection
was Windows PowerShell/CMD on a friend's computer; its public known-host record
is not available on this laptop. No key was accepted or replaced. User-reported manual login
is not independent institutional host-key verification.

Obtain only the saved **public host key** from that friend's Windows account:

```powershell
ssh-keygen -F 10.5.18.100 -f "$env:USERPROFILE\.ssh\known_hosts"
```

Compare this previously used key with the currently offered key before pinning it.
If it matches that connection, reuse with `StrictHostKeyChecking=yes`. Record the
trust basis as the user's previous connection; do not label it independently
institutionally verified. A missing/changed key must be surfaced, never bypassed.
Never copy private keys, passwords, OTPs or session secrets into this repository.

After key reuse is established, run from the project root in the user's own
PowerShell terminal (password enters directly into SSH, no transcript):

```powershell
powershell -NoProfile -File hpc/cse_v1/discover.ps1 -OutputFile artifacts/phase3/cse_preparation_20261007/discovery.txt
# If the verified prior OpenSSH-format public-key file is elsewhere:
# append -KnownHostsFile 'C:\actual\verified\known_hosts'
```

Do not use the commented placeholder path literally. The helper fails on an
unknown/changed key. It captures only authenticated discovery output; authentication
stderr remains in the terminal. It never submits jobs or executes QE.

## Discovery and current unknowns

`hpc/cse_v1/discover.sh` queries identity, partitions, CPU-node scheduler metadata,
account/QoS limits, scheduler enforcement, quotas, mount points, module names,
QE/MPI paths and library links. Missing commands/permission errors remain unknown.
Paths merely existing does not prove write permission, shared compute visibility,
quota entitlement, persistence or retention. No remote directories are created.

The [official CSE guide](https://cse.iitkgp.ac.in/Cluster-100.pdf) lists `cpupart`
and two CPU nodes with dual six-core CPUs and 128 GB RAM. These published values
are **not live account/resource verification**. Do not use PARAM's `medium`,
40-rank rule, charging model or scratch-retention policy. GPU partitions excluded.

Before any execution review, verify:

- Actual login hostname, account associations, allowed CPU partition/QoS, maximum
  wall time, memory/CPU limits, charging/balance or the site's applicable entitlement.
- Node physical-core topology, Slurm CPU allocation/binding and hard memory/time
  enforcement. Select ranks from these facts; SMT threads are not physical cores.
- Supported QE 7.5 executable/version/hash and compatible compiler/MPI libraries,
  launch/binding argv, and Python 3.10+ for the CSE overlay. No QE version is currently confirmed.
- Persistent project path and shared compute-visible scratch; actual quotas and
  retention, including failures and partial files. Keep total scratch within 100 GiB.

If QE 7.5 is absent, report installed alternatives first. A concrete fallback is
a private-prefix QE 7.5 build with a compatible installed compiler/MPI stack,
using a separately reviewed Slurm build allocation. No installation/build/version
change is authorized or performed here. Never copy the Fedora binary.

## Frozen package and transfer

Local ZIP, receipt and all **140 hashed files reverified**; no coordinate/input/UPF
changes. ZIP SHA256:
`4ea11e147c529d8b893d2131c06812ec5978b24f0c7d8905c116c22e4e6d0554`.

Files ready:

- `artifacts/phase3/UIO66_Frozen_DFT_QE75_v2.zip`
- `artifacts/phase3/uio66_frozen_dft_v2_qe75_receipt.json`
- `hpc/cse_v1/` separate execution overlay; previous PARAM overlay unchanged.

After authentication and storage verification, create a new dedicated persistent
project root and separate scratch root. Record **every created absolute directory**,
purpose, persistence, owner and timestamp in
`artifacts/phase3/cse_preparation_20261007/remote_directory_ledger.json`.
Current ledger is empty. Do not overwrite or delete remote paths.

Transfer pattern, pending actual paths and trusted-key reuse:

```powershell
scp -P 22 -o StrictHostKeyChecking=yes artifacts/phase3/UIO66_Frozen_DFT_QE75_v2.zip artifacts/phase3/uio66_frozen_dft_v2_qe75_receipt.json 23BT10034@10.5.18.100:VERIFIED_PERSISTENT_ROOT/
scp -P 22 -o StrictHostKeyChecking=yes -r hpc/cse_v1 23BT10034@10.5.18.100:VERIFIED_PERSISTENT_ROOT/
```

On the login node, in that new directory, only lightweight integrity checks:

```bash
sha256sum UIO66_Frozen_DFT_QE75_v2.zip
python3 cse_v1/verify_extract.py --zip UIO66_Frozen_DFT_QE75_v2.zip --receipt uio66_frozen_dft_v2_qe75_receipt.json --destination package
```

The extractor pins ZIP/manifest hashes, rejects unsafe/unexpected members, refuses
existing destinations and verifies 140 files before/after extraction. Its returned
directory list must join the ledger. Retain the remote verification output locally.

## CSE execution overlay: draft, not submission-ready

`hpc/cse_v1/environment.example.json` leaves actual account/partition/ranks/paths,
executable/build/MPI and all approvals unset. `pilot.sbatch.in` has explicit
placeholders. No executable final script can be claimed before discovery.

Scope: two exact water complexes, one four-hour CPU job per complex; one node,
one thread per verified MPI rank, proposed 64 GiB RAM, zero requested GPUs.
Maximum exposure is **8 node-hours and 8 Ãƒâ€” verified rank-count CPU-hours**, subject
to actual site billing (whole-node billing may differ). No monetary/SU estimate.
The original 32-rank and PARAM 40-rank proposals are not inherited.

The adapted runner validates real Slurm account/resources and refuses login-node
execution or GPU allocations in CSE mode. One frozen calculation per job. First
failed/incomplete run blocks the second; successful first output still requires
independent inspection and retained evidence verification. No automatic submission,
retry, requeue or extension. Preserve partial files at hard termination.

Scientific settings remain frozen: PBE-D3(BJ) pairwise, original exact geometry,
verified SSSP potentials, 80/600 Ry, Gamma, neutral `nspin=1`, fixed occupations,
`conv_thr=1e-8 Ry`; no ionic relaxation. See `docs/UIO66_QE75_WATER_PILOT_V2.md`.

After filling and reviewing actual environment, script and limits, syntax-only
checks are `bash -n pilot.sbatch` and unresolved-placeholder inspection.
Optional `sbatch --test-only pilot.sbatch 0` is not yet run remotely.
Real commands, **for later review only; not authorized**:

```bash
sbatch --parsable pilot.sbatch 0
# Only after the first successful output is independently reviewed and approved:
sbatch --parsable --dependency=afterok:FIRST_JOB_ID pilot.sbatch 1
```

Retain executable/module/build/MPI evidence, allocation, exact input/PP hashes,
SCF stdout/stderr/XML, energies/forces, elapsed time, peak-memory accounting,
scratch usage and exit status. End-of-script accounting is provisional; collect
final `sacct` after termination. Incomplete/unconverged output is not an energy result.
No successful SCF alone establishes numerical convergence or material validation.

## Verification and next action

27 focused tests passed in 12.00 s. Bash discovery/submission-template syntax and
PowerShell parser checks passed. These are local checks, not cluster integration.
Synthetic 12-rank allocation test is not evidence of available CSE resources.

Current blocker: complete user first-use host-key acceptance and interactive
authentication in the open terminal. All live environment facts, transfer and final script
remain pending. No remote directory or job exists from this preparation task.
After future evidence downloads and hash verification, prepare a cleanup list;
wait for explicit deletion authorization. No cleanup now.
