# Windows to PARAM Shakti: preparation v1

Updated 2026-10-07. **No remote job, build or DFT calculation submitted.**
Phase 3 remains incomplete; no scientific DFT result exists.
Use repository-relative paths below from the project root.

## Verified locally

- Windows OpenSSH SSH/SCP clients available. User supplied actual login
  `23BT10034@10.5.18.100`. Port 22 is reachable over Wi-Fi.
- No existing OpenSSH known-host entry found for that IP. Strict checking rejected
  the connection before password authentication.
- Offered ED25519 fingerprint:
  `SHA256:9XibnJwLyJezyWcu/PJCFLjIU6PN685P253L1oXCvCo`.
  This is **observed, not institutionally verified**. No key was accepted/installed.
  Windows ssh-keyscan hit an unsupported-KEX error; existing Git OpenSSH keyscan
  retrieved the public key. No SSH algorithm/checking downgrade was made.
- `artifacts/phase3/UIO66_Frozen_DFT_QE75_v2.zip` SHA256 verified:
  `4ea11e147c529d8b893d2131c06812ec5978b24f0c7d8905c116c22e4e6d0554`.
  Receipt and **all 140 package-file hashes** verified. Sealed archive unchanged.
- No Fedora handoff/initialization artifact found in expected root/docs/phase3
  locations. User reports successful zero-SCF initialization with full estimated
  memory exceeding laptop RAM. This is user-reported, not an inspected raw result.

Local evidence: `artifacts/phase3/param_shakti_preparation_20261007/` contains
`local_access_receipt.json`, public-key observations and
`remote_directory_ledger.json`. No password, OTP or authentication secret is saved.
The remote directory ledger is **empty**: no remote directory has been created.

## Endpoint correction and host trust (2026-10-07)

The supplied **10.5.18.100 is documented as the CSE cluster**, not the PARAM
Shakti login endpoint. Official source: https://cse.iitkgp.ac.in/Cluster-100.pdf
(section How to Login). Its published CPU partition is `cpupart`; do not apply
PARAM's `medium`/40-rank policy or charging/storage assumptions to this endpoint.
Live entitlement, installed QE and node resources remain unverified.

PARAM's official hostname `paramshakti.iitkgp.ac.in` resolves locally to
`10.171.17.201`. The user's account on that distinct system is not established.
Do not move credentials to that hostname merely because the username is known.

Correction to the earlier report: the PARAM usage page DOES contain an ECDSA
fingerprint in its SCP examples. Exact comparison against public keys scanned
without authentication on 2026-10-07:

| Source / endpoint | ECDSA SHA256 |
|---|---|
| Official PARAM webpage | `xN9lbdCx4+ywHnsuK1McWGguquHAWCxBdSbI1mNqtlY` |
| Offered by PARAM hostname | `xN9lbdCx4+ywHnsuK1McWGguquHAWCxBdSbI1mNqt1Y` |
| Offered by supplied CSE IP | `G5xVnRtECJql9+xmLmMmJeWoEmcTE5CbzHCV6rXutsg` |

The webpage uses lowercase `l` near the end; the offered PARAM hash uses digit
`1`. This is not an exact match. A possible documentation typo remains unverified;
never silently correct or trust it. The published PARAM fingerprint cannot
validate the different CSE endpoint either. No previously trusted OpenSSH/PuTTY
key was found. No public matching CSE fingerprint was found in the targeted
institutional search. DNS hostname resolution and campus Wi-Fi establish no key
trust by themselves. No key accepted, credential submitted or remote file created.

Required next: confirm which cluster the account belongs to and obtain its host
fingerprint from institute-issued instructions or a previously verified client.
This can wait for the user; all independent local preparation is retained.

## Interactive login after trusted verification

Compare the offered fingerprint against an institution-issued fingerprint or a
previously institution-verified client record. Do not establish trust using the
same network scan alone. The available PARAM webpage fingerprint fails the exact comparison above.
Do not disable host checking or accept a changed key without verification.

The agent's tool terminal cannot securely solicit your password/2FA interaction.
Use your own Windows PowerShell terminal (no transcript):

```powershell
ssh -p 22 -o StrictHostKeyChecking=ask -o ConnectTimeout=15 23BT10034@10.5.18.100
```

Accept a new key **only after trusted comparison**. Enter CAPTCHA, password and
2FA only at the SSH client's prompts; never in chat, command arguments, scripts or
logs. Complete any first-login enrollment in this unrecorded interactive session.
Do not run scientific work on the login node. After login is established, exit
that session and run the bounded discovery helper in your terminal:

```powershell
powershell -NoProfile -File hpc/param_shakti_v1/discover.ps1 -UserName 23BT10034 -Endpoint 10.5.18.100 -Port 22 -OutputFile artifacts/phase3/param_shakti_preparation_20261007/discovery.txt
```

It keeps strict checking, requests authentication directly through SSH, captures
only output after the authenticated discovery marker and does not record stderr
authentication prompts. It performs read-only account/module/quota queries.
No compute entitlement follows merely from a successful SSH login.

## Official guidance and facts still requiring live verification

[PARAM Shakti official guidance](https://hpc.iitkgp.ac.in/using-the-system)
was consulted on 2026-10-07. It describes Slurm, `medium` MPI jobs with 40 tasks/node,
`myquota`/`sbalance`, site examples under `/home/iitkgp/slurm-scripts`, and temporary
scratch subject to a 60-day policy. Its examples/listings are not proof of this
account's current entitlement. Home quotas have student exceptions. Actual
partitions, QoS, balances, charging and storage must be checked after authentication.

Discovery must establish:

1. Actual identity/home, Slurm association/account, allowed partitions/QoS, per-user
   and account limits, balance and billing weights/rates. Restricted queries remain
   unknown; they do not mean unlimited or zero cost. Inspect accessible relevant QoS
   details after the association identifies their names; do not query/change others.
2. Actual home/scratch quotas, ownership, persistence and backup policy. The proposed
   100 GiB restart allowance may exceed home quota; never copy it there blindly.
3. Installed QE versions and module dependency chain. Inspect the selected module,
   `command -v pw.x`, `readlink -f`, executable SHA256, `file`, `ldd`, compiler/MPI
   information and supported site example. A bounded `pw.x -h` check is lightweight;
   do not invoke SCF/initialization on login nodes. Python 3.11+ is required by the
   current runner (`hashlib.file_digest`). Verify its module/path as well.
4. A supported QE 7.5 is preferred. If absent: stop to review available versions
   versus a private-prefix QE 7.5 build using the site's supported toolchain and a
   separately approved Slurm build allocation. Do not copy the Fedora executable,
   silently change QE version or perform a large login-node build.

## Transfer and preservation procedure (pending authenticated paths)

After discovery, choose a dedicated project root on confirmed persistent storage
and a separate dedicated scratch root. Record each absolute directory, parent,
creation time, purpose, owner and persistence class in the remote-directory ledger
**when created**. Do not overwrite a previous project/extraction/run directory.
No remote paths in the following command patterns have been created or verified.

```powershell
# Replace VERIFIED_REMOTE_ROOT only after discovery and directory creation recorded.
scp -P 22 -o StrictHostKeyChecking=yes artifacts/phase3/UIO66_Frozen_DFT_QE75_v2.zip artifacts/phase3/uio66_frozen_dft_v2_qe75_receipt.json 23BT10034@10.5.18.100:VERIFIED_REMOTE_ROOT/
scp -P 22 -o StrictHostKeyChecking=yes -r hpc/param_shakti_v1 23BT10034@10.5.18.100:VERIFIED_REMOTE_ROOT/
```

On the login node, in that confirmed project directory (lightweight verification):

```bash
sha256sum UIO66_Frozen_DFT_QE75_v2.zip
python3 param_shakti_v1/verify_extract.py --zip UIO66_Frozen_DFT_QE75_v2.zip --receipt uio66_frozen_dft_v2_qe75_receipt.json --destination package
```

The extractor pins ZIP/manifest, rejects unexpected/duplicate/traversal/symlink
members, verifies all 140 members before and after extraction, and refuses an
existing destination. Its JSON lists every extraction-created directory; retain
and merge this into the directory ledger. Capture the verified remote hashes locally.
Inputs/coordinates, UPFs, pairwise PBE-D3(BJ), 80/600 Ry, Gamma, neutral `nspin=1`,
fixed occupations and 1e-8 Ry electronic tolerance remain unchanged.

## Separately versioned cluster launcher and submission proposal

`hpc/param_shakti_v1/` holds a source snapshot of the adapted runner, environment
template, extraction/discovery helpers, overlay hashes and `pilot.sbatch.in`.
`scripts/run_qe_water_pilot.py` is the maintained source. The frozen v2 runner is
preserved in its sealed package; new cluster execution uses the reviewed overlay.

The environment example is unapproved and contains null account, ranks, module
and path facts. No installation or allocation is fabricated. Resolve every
`__PLACEHOLDER__` in a **new** submission file only after live discovery; use a
verified QoS directive only if needed. Pin overlay hashes before remote use.

Current **PARAM-only conditional** proposal, based on published MPI guidance.
**Not applicable to the supplied CSE endpoint; retain as an unapproved draft.**

|Item|Proposed, not verified|
|---|---|
|Partition/layout|One `medium` node, 40 MPI ranks, one thread each|
|Memory|64 GiB per node|
|Time|Two separate four-hour jobs, sequential|
|Exposure|At most 8 node-hours / 320 allocated CPU-core-hours if 40 cores are billed|
|Billing|Actual SUs/currency/weights/account balance unknown; must be reviewed|
|Scratch|100 GiB shared project ceiling, temporary; retain partial/restart files|
|Scope|Only two baseline 110111 H2O28 frozen complex SCFs|

A different live site layout requires a recorded configuration/script revision;
do not use the old 32 ranks by default. The adapted runner checks running Slurm
job ID, account/partition, one node, rank/thread allocation, four-hour time limit,
64 GiB request, executable/PP/input hashes, and actual XML MPI layout. It refuses
login-node execution in cluster mode. No validation is bypassed to change ranks.

Before any submission, review actual script, allocation exposure and storage paths.
Static validation now uses Bash syntax and synthetic Slurm/format tests; this is
**not compute-node integration**. After configuration, allowed no-submit checks are:

```bash
bash -n pilot.sbatch
grep -n '__' pilot.sbatch  # must have no unresolved placeholders
sbatch --test-only pilot.sbatch 0  # optional site scheduling validation; does not submit
```

No `sbatch --test-only` has yet been run remotely. The real submission commands
below are **for review, not authorized now**:

```bash
sbatch --parsable pilot.sbatch 0
# After first job completes, download/verify/independently inspect its real output.
# Only if approved and first job is complete, update the external reviewed config:
sbatch --parsable --dependency=afterok:FIRST_JOB_ID pilot.sbatch 1
```

There is no automatic second submission. Job 1 requires the successful first-job
evidence hashes/state and an independent-review flag. Failures return nonzero,
preventing afterok continuation. No retry, requeue or deadline extension.
Slurm sends a signal before its hard stop; the runner terminates workers and keeps
partial data. An uncatchable kill can leave incomplete manifests; never call such
outputs a valid completed energy comparison.

## Capture, download and assessment

Retain module list, executable/build/MPI provenance, exact argv and input/UPF hashes,
live Slurm job description, SCF stdout/stderr/XML, forces/energies, sampled memory
and scratch, GNU time and exit status. End-of-script sacct is provisional; fetch
final accounting after Slurm finalizes the job:

```bash
sacct -j VERIFIED_JOB_IDS --units=M --parsable2 --format=JobID,State,ExitCode,Elapsed,AllocCPUS,ReqMem,MaxRSS,TotalCPU,NodeList,AllocTRES
```

MaxRSS can describe the largest task rather than total-node memory. Inspect site
cgroup/accounting evidence; do not label sampled RSS sums as authoritative peak.
Keep small evidence in confirmed persistent storage and all scratch until locally
downloaded/hash-verified. Check local free space before transferring large restarts.
Independently inspect the first actual QE output/XML against the parser before
allowing job two. Successful SCF is not cutoff/k-point convergence or material
validation. Existing fixed-geometry energy/force assessment remains applicable.

After both evidence and scratch are downloaded:

```powershell
python scripts/run_qe_water_pilot.py --verify-evidence LOCAL_EVIDENCE --scratch LOCAL_SCRATCH
```

Prepare a path-by-path cleanup proposal only after verification. Include bytes,
persistence class, local backup/hash receipt and reason for each candidate. **Wait
for explicit deletion instruction; no deletion now.** This includes failed runs.

## Handoff status

Blocked at cluster identity/account clarification and institutional host-key verification,
then interactive authentication. The supplied IP identifies CSE; PARAM-specific
resource settings are not transferable.
Account/QoS/limits/balance, installed QE/MPI, remote transfer and compute-node tests
are unverified. Remote directories created: **none**. Jobs submitted: **none**.
Do not contact administrators or buy allocation on the user's behalf.
Graphify was used for exact-symbol retrieval; no graph rebuild was performed as
requested. New/changed files in this handoff must be read directly until a future
authorized targeted index refresh. Preserve all previous pilot failures and results.

Local validation: **100 tests passed in 31.39 s** (ASE/NumPy/spglib deprecation
warnings); Bash and PowerShell syntax checks passed. These are local preparation
checks, not live-cluster integration or scientific DFT results.
