# Fedora handoff — 2026-10-06, after initialization 01

**ONE authorized initialization completed; authorization consumed. No SCF/UMA.**

- Original ZIP/receipt remain in `artifacts/`, byte-unchanged. ZIP SHA256 matches
  `4ea11e147c529d8b893d2131c06812ec5978b24f0c7d8905c116c22e4e6d0554`.
  All 140 files verified in fresh
  `artifacts/phase3/uio66_frozen_dft_v2_qe75_fedora_verified01/`.
- Existing QE 7.5 build reused: `local/qe75-fedora-v1/build/bin/pw.x`.
  No installation/package rebuild. Source and executable hashes rechecked.
- `nstep=0` source branch returns before SCF. Actual XML confirms nstep=0,
  zero SCF steps, internal status255 and no energy/forces. Process exit0 is expected
  for this build's default STOP. Scientific parser rejects the incomplete result.
- Four ranks, one thread each; unchanged 8-GiB cap, zero swap, 600-second ceiling.
  Preflight had 10.62 GiB available RAM and ~213.52 GiB persistent disk free.
  Zen web processes were optional memory consumers; no applications terminated.
- 127 atoms, 522 electrons, 261 bands; 80/600 Ry, Gamma, PBE-D3(BJ) two-body.
  Dense225³/1,902,004 G-vectors; smooth160³/741,079 G-vectors.
- **QE estimates >12.67 GiB total dynamical RAM**, exceeding the current 8-GiB cap.
  Measured initialization peak0.7905GiB, swap0, noOOM; service3.836s, QE0.24s.
  Initialization does not measure full-SCF RAM/runtime. Final wavefunction dimension
  remains uninitialized (`npwx=0`). Retained scratch44,512 bytes is only init XML.
- Both flags in `configs/qe75-fedora-v1.json` are false; authorization consumed.
  Keep `local/qe75-fedora-v1/smoke01/execution-started.json`. No retry/limit increase.
- Next decision: review a larger verified RAM allocation and full-SCF launcher.
  No full SCF authorized; do not lower cutoffs or alter the frozen model.
  Phase3, UMA accuracy, numerical convergence and proton correspondence unresolved.

Results and evidence detail: `docs/UIO66_QE75_FEDORA_INIT01_RESULTS.md`.
Evidence/accounting: `evidence/qe75-fedora-init01/`.
Raw input/output and all scratch: `local/qe75-fedora-v1/smoke01/`.
Both evidence directories are ignored by Git; retain/copy separately.
Offline assessor: `scripts/assess_qe75_fedora_init_v1.py` (no QE launch).
The existing graph was not rebuilt and does not yet index these results.
