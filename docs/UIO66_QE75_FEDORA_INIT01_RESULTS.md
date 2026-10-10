# Fedora initialization 01 — 2026-10-06

**The ONE authorized initialization-only test completed. Zero SCF steps; no DFT
energy or force result. Authorization is consumed and both execution flags are false.**

The transferred originals are `artifacts/UIO66_Frozen_DFT_QE75_v2.zip` and
`artifacts/uio66_frozen_dft_v2_qe75_receipt.json` (not inside `phase3/`). Neither was
modified. The ZIP matches the receipt and expected SHA256
`4ea11e147c529d8b893d2131c06812ec5978b24f0c7d8905c116c22e4e6d0554`.
Receipt SHA256: `ccbc9014bc6ce151b464fedb5e78a31abfd6bb095369488c944614d6ba197338`.
Manifest SHA256: `716b281245bee302cc6cb574c0e724aaf2dcec66a5480d34ae52893c47b21032`.
All **140 files** matched in the archive and fresh extraction:
`artifacts/phase3/uio66_frozen_dft_v2_qe75_fedora_verified01/`.
No scientific package rebuild or QE reinstall occurred. Historical Windows paths
inside the receipt remain unchanged; the separate Fedora config records local paths.

## Execution and initialization guarantee

The selected first water complex was
`uio66_110111_H2O_s28_f0.010_complex__baseline.in`. A separate execution copy adds
only `nstep=0`; coordinates, cell, atom order and all scientific settings are preserved.
The original source archive and executable hash were rechecked before launch.
Relevant compiled-release source files were byte-compared with the archive:

- `PW/src/input.f90:463`: the SCF branch sets `nstep=min(1,nstep)`, preserving zero;
  line 659 transfers it into the internal control flags.
- `PW/src/run_pwscf.f90:149`: zero triggers `pre_init`, grid setup, summary,
  memory estimate and `config-init` XML, then **RETURN** before `init_run` and SCF.
- The actual XML records `nstep=0`, `n_scf_steps=0`, `convergence_achieved=false`,
  and internal `exit_status=255`. The process returned 0 because this build uses
  default Fortran STOP without returning the internal status. There is no total
  energy/force result. Empty timing headings such as “Called by electrons” do not
  indicate execution. The printed “8 plain mixing” is a mixing-history setting,
  not eight SCF iterations.

The timeout was a resource guard, not the initialization mechanism. Four MPI ranks
were bound to four different physical cores, one thread per rank. The service had
8 GiB MemoryMax, 7 GiB MemoryHigh, MemorySwapMax=0, RuntimeMaxSec=585 and 15-second
termination grace, within the authorized 600 seconds. No retry or limit increase.

Before staging: **10.62 GiB MemAvailable**, about **213.52 GiB persistent Btrfs free**;
the runner checked the RAM/disk gates again before its sole launch. Zen browser/web
processes were the largest optional memory consumers (largest individual content
process about 1.21 GiB RSS). No application was terminated or cache forcibly dropped.

## Observed sizes and resource evidence

|Quantity|Observation|
|---|---|
|Atoms / electrons / occupied bands|127 / 522 / 261|
|Cutoffs / sampling|80 / 600 Ry; Gamma|
|Dense FFT grid|225 × 225 × 225; 1,902,004 G-vectors|
|Smooth FFT grid|160 × 160 × 160; 741,079 G-vectors|
|PW distribution summary|185,045 tally; 46,256–46,267 per rank|
|Final wavefunction dimension|Not initialized: XML `npwx=0`; do not interpret as zero physical basis size|
|QE predicted maximum dynamical RAM per rank|**>3.17 GiB**|
|QE predicted total dynamical RAM|**>12.67 GiB**|
|Measured service cgroup peak|848,805,888 bytes = **0.7905 GiB** (809.4 MiB)|
|Swap / memory-limit/OOM events|0 bytes swap; all high/max/OOM/kill counters zero|
|Elapsed|0.24 s QE-reported wall; 3.003 s MPI monitor; **3.836 s whole service**|
|CPU time|3.480 s for whole service|
|Retained scratch|44,512 bytes (initialization XML); not a full-SCF disk estimate|

The PW distribution tally is the initialization grid report, not a finalized
wavefunction basis dimension. QE labels memory as “GB” but defines GB=1024³ in
`PW/src/memory_report.f90:65`. Its comments explicitly call this a rough estimate
before large arrays are allocated. The measured peak covers package/software
preflight, the launcher and initialization; it does not measure SCF allocation.

XML confirms PBE, D3 version 4, threebody=false, Gamma, four ranks/one thread and
80/600 Ry (XML stores 40/300 Hartree). Atom identities/order and input/output
coordinates match archived geometry, maximum error 3.56e-15 Å; cell error 2.67e-15 Å.
The scientific parser correctly rejects this output as incomplete/unconverged.
The XML dispersion-energy zero is an initialization placeholder, not an evaluated
DFT correction. All DFT results remain absent.

Retained notices: C/O pseudo atomic wavefunctions renormalized internally;
IEEE_UNDERFLOW_FLAG/IEEE_DENORMAL on four ranks; no QE fatal error. UPF files are
unchanged. systemd ignored deprecated CPUAccounting assignment but still reported
CPU time. After completion the transient service was inactive/unloaded and no
`pw.x`, `mpirun` or `prterun` process remained. Its live properties were no longer
available; the saved service summary, journal and cgroup snapshot supply accounting.

## Decision and retained evidence

**No full SCF under the current 8-GiB allocation.** The predicted >12.67-GiB demand
exceeds the cap and the preflight's available RAM. Initialization success does not
establish laptop feasibility. A larger verified RAM allocation and separately
reviewed launcher/resources are needed before any full-SCF decision. Do not reduce
scientific cutoffs, shrink structures, raise limits, or rerun automatically.

Still unknown: actual SCF/diagonalization peak memory, sustained runtime/thermals,
scratch growth, SCF convergence, complete converged XML/parser compatibility,
forces/energy differences, numerical convergence and UMA accuracy. Phase 3 and the
proton correspondence issue remain incomplete; four UMA host SPs stay separate.

Evidence: `evidence/qe75-fedora-init01/` contains package verification, mechanism
trace, resource snapshot, authorization and consumption receipts, config copies,
assessment, service console/journal and checksums. All execution copies, stdout,
stderr, cgroup samples and partial/init scratch are in
`local/qe75-fedora-v1/smoke01/`; hash manifests cover these files without deletion.
Both directories are ignored by Git and must be retained/copied separately.

Offline assessment implementation: `scripts/assess_qe75_fedora_init_v1.py`.
It was reproduced from logs/XML/accounting without running QE again. The original
sealed 32-rank launcher remains unchanged. No model refit, design expansion, UMA,
ionic relaxation or material-performance claim.
