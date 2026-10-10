# Windows baseline verification and Git integration - 2026-10-10

**14 baseline SCFs complete; numerical convergence and physical/UMA accuracy
remain unresolved. Phase 3 is incomplete.** This review ran only offline Python;
no SSH, QE, MPI, UMA, job submission, relaxation or new scientific calculation.

## Git recovery and preservation

Initial inspection found **no active merge/rebase and no unmerged index entries**.
HEAD was `12cc065`, two commits behind already-fetched `origin/main` (`2b83668`).
Seven modified tracked files and 25 untracked source/doc/test files were present.
No new pull/fetch was started. Windows work was checkpointed as `9cbcc61`, then
the existing `origin/main` was merged locally with explicit conflict resolution.

Recoverable backup outside the repository:
`../MOF_for_DAC_Opt_recovery/20261010_103218/`.

- `windows_work_before_integration.zip`: all 32 affected files, original index,
  working/staged patches, status and commit IDs; every file hash verified.
  SHA256 `2f5f6e789c7f4ddbdc8e9dc4266bd73be36f3b1a0e17bb797abe8c7008aa6012`.
- `merge_conflicts_before_resolution.zip`: conflicted working files plus all
  three index stages, saved before changing any conflict.
  SHA256 `28ad126f9f46a6669fb5ebdf9d413fc86ca956851f862c40a18c7f69518befba`.
- `receipt.json` and `resolutions.json`: file checksums and per-file resolution.

Conflicts were `.planning/STATE.md`, `AGENTS.md` and `MODEL_HANDOFF.md`.
For each, both branches had only added status prefixes to an identical common
body after newline normalization. Each resolution retains the 349-line Fedora
prefix, 47-line Windows prefix and common body once, with a current-status header
and historical labels. No global ours/theirs selection was used.

Windows CSE/PARAM helpers, Slurm guards, Python3.10 hashing and tests are preserved.
Both overlay manifests still validate against their original payload bytes.
Scoped `.gitattributes` prevent checkout newline conversion of these hash-pinned
overlays and the incoming frozen QE plans; current status text uses LF.

The seven operational Fedora configs are absent here and now explicitly ignored.
The already-tracked historical `configs/qe75-fedora-v1.json` remains unchanged with
execution flags false. No old approval is current authority. Ignored local
artifacts were left in place; no reset, discard, deletion, push or force-push.

## Portable evidence verification

Archive: `artifacts/phase3/uio66_qe_baseline14_review_v1.zip`, **3,930,640 bytes**.
SHA256 **`8f7fbf7abc4839117595f18e14b42db05d8392547cede539232ae937e99bf0d7`**.
Archive, receipt and scientific plans imported unchanged from Fedora commit `2b83668`.

```powershell
python scripts/review_qe75_baseline14_portable.py --archive artifacts/phase3/uio66_qe_baseline14_review_v1.zip --extract-to local/windows-baseline14-review-20261010 --output local/windows-baseline14-analysis-20261010
python -m pytest tests/test_qe75_baseline14_portable.py tests/test_qe75_fedora_v1.py tests/test_qe_water_pilot.py tests/test_cse_cluster.py tests/test_param_shakti.py -q -p no:cacheprovider --basetemp=tmp/pytest_windows_merge_20261010 --tb=short
```

Results: **471 payload hashes, 14 SCFs, 1,717 force vectors and four energy
comparisons verified. 42 targeted tests passed in 15.53 seconds.** Text/XML
convergence, energies, exact geometry/cell/atom identities, electron counts,
approved potentials/settings and available archived force comparisons passed.
SCF iteration counts span 16-18; maximum final SCF error is
`9.480468785539937e-9 Ry`. These are SCF/parser checks, not cutoff convergence.

Outputs: `local/windows-baseline14-analysis-20261010/review.json` and `forces.csv`.
Exact review payloads: `local/windows-baseline14-review-20261010/`.
Use new directory names for another review; verifier intentionally refuses overwrite.
Full density/PAW/wavefunction restart checkpoints remain Fedora-only, as described
in the [portable handoff](UIO66_QE75_WINDOWS_BASELINE14_GUIDE.md).

## Reconstructed provisional differences

Later checkpoint minus earlier, **meV**, same composition within each row.
Guest-associated = complex minus stripped-host difference. It includes guest
deformation and interaction changes; it is not an adsorption energy.

|Frozen transition|DFT complex|UMA complex|DFT host|DFT guest-associated|
|---|---:|---:|---:|---:|
|110111 H2O s28, 0.010 to 0.005|-38.396707|-41.461081|-21.725487|-16.671220|
|110111 CO2 s7, 0.020 to 0.010|-79.440623|-75.053958|+1.189612|-80.630235|
|110111 CO2 s7, 0.010 to 0.005|-10.155191|-13.873650|-9.860710|-0.294481|
|000000 CO2 s16, 0.010 to 0.005|-15.607560|-17.749933|-0.203710|-15.403850|

At the current settings, DFT and UMA both favor the later **complex** geometry in
all four cases. Their complex changes differ by 2.142-4.387 meV. This does not
establish physical agreement within a known numerical uncertainty.

The decomposition attributes portions of the water change to both the frozen
host and guest-associated term. The final CO2 s7 complex change is almost entirely
the matching host change: its -0.294481-meV remainder has **unresolved sign** at
the current numerical accuracy. Earlier CO2 s7 and parent CO2 changes are mainly
guest-associated at these settings. These statements describe the computed
decomposition, not proven causal mechanisms or material rankings.

The largest force across all 14 geometries is **0.565884531 eV/Angstrom**, H at
QE atom115/source atom114 in `uio66_110111_H2O_s28_f0.010_host`. The archive's
0.435954 wording refers to the largest new **complex** force; raw forces already
contain the correct host value. Archive untouched. Large residual forces remain
diagnostic because the snapshots were intentionally frozen, not DFT-relaxed.

## Next decision, without execution

Review these baseline results and define exact acceptance metrics for separately
authorized density/grid and wavefunction-cutoff checks. The prepared paired
80/750-Ry water calculation requires a larger verified memory allocation than
the retained Fedora laptop cap. Electronic tolerance, k-points, negative
pseudocharge behavior and transfer to host/CO2 differences also remain unresolved.

Preserve the original failed sampling pilot, four missing UMA host single points,
ODAC25 reference mismatch and chemistry/proton-placement questions as distinct
open workstreams. No refit, expansion, ranking claim or new calculation follows
from this successful offline review.
