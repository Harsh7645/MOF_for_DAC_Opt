# Windows handoff: completed frozen 80/600-Ry baseline

All 14 mandatory SCFs (seven MOF+guest complexes and seven matching stripped hosts) converged. **Phase 3 and numerical/physical validation remain incomplete. No additional calculation is authorized.** Start with [the baseline report](UIO66_QE75_BASELINE14_RESULTS_V1.md) and [Fedora handoff](UIO66_QE75_FEDORA_HANDOFF.md).

## Pull, verify, extract and reproduce the offline review

From the repository root in PowerShell, with Python 3.10 or newer installed:

```powershell
git switch main
git pull --ff-only origin main
$zip = 'artifacts/phase3/uio66_qe_baseline14_review_v1.zip'
$expected = '8f7fbf7abc4839117595f18e14b42db05d8392547cede539232ae937e99bf0d7'
if ((Get-FileHash $zip -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected) { throw 'Review ZIP checksum mismatch' }
py -3 scripts/review_qe75_baseline14_portable.py --archive $zip --extract-to local/baseline14-review-v1 --output local/baseline14-offline-analysis-v1
if ($LASTEXITCODE -ne 0) { throw 'Offline review failed; inspect the error' }
py -3 -m unittest discover -s tests -p test_qe75_baseline14_portable.py -v
```

Use new directory names on subsequent reviews; the tool refuses to overwrite existing output/extraction directories. `local/` is ignored by Git. The script needs **only the Python standard library**; no QE, MPI, UMA, NumPy, GPU, systemd or network access. Its checks do not depend on Python assertions and remain active under `python -O`.

Expected result: **471 payload hashes, 14 SCFs and 1,717 force vectors verified** (1,463 from the twelve-job recovery batch plus 254 from the two earlier water complexes). Generated `review.json` reconstructs electron counts, convergence, energies, all four energy comparisons, negative-pseudocharge trajectories and sampled memory. `forces.csv` contains every atom's stdout Ry/bohr, XML converted to Ry/bohr, eV/Å components, one-based QE atom index and zero-based frozen source index. The tool also checks archived UMA and paired DFT force-component differences. Rounding tolerances used for text/XML matching are parser consistency checks, not numerical-convergence acceptance thresholds.

## What travels with Git

The ZIP is **3,930,640 bytes (3.75 MiB)**, stored as an ordinary Git blob. Its sibling `.zip.sha256` and `.receipt.json` record the checksum and original packaging receipt. No LFS or separate transfer is required for this offline baseline review.

Inside the archive:

|Path|Contents|
|---|---|
|`raw/job01/` … `raw/job12/`|Exact executed input, **complete stdout/stderr**, final `scratch/<manifest-id>.save/data-file-schema.xml`, resource samples and worker receipts|
|`raw/prior-water-first/`, `raw/prior-water-second/`|The same review evidence for the two earlier converged complexes|
|`frozen-package/`|Frozen manifest, 14 mandatory geometry JSON files, original file hashes and pseudopotential provenance|
|`pseudo/`|All five exact approved UPFs, checked against frozen SHA256 pins|
|`evidence/comparisons.json`, `force-comparisons.json`|Energies, complex/host/guest-associated differences, mapped force comparisons and available archived UMA comparisons|
|`evidence/jobNN/`|Assessments, force vectors, terminal status, service accounting, journals and verification receipts|
|`evidence/terminal-review-v1/`|Independent raw/XML audit, 1,463-vector crosscheck and comparison audit|
|`prior-audits/`, `plan/`, `code/`|Earlier water audits, job mapping and historical Fedora controller/audit sources|
|`SHA256SUMS.json`|SHA256 for every other archive member|

The tracked repository adds current reports/status, historical Fedora execution/control/parser sources, tests, frozen-input plans, the proposed (disabled) 750-Ry plans and the portable verifier. The archive's exact inputs avoid Windows newline conversion affecting scientific input pins. Retain archive files unchanged. Absolute `/home/harshsahu/...` paths in historical receipts identify the original Fedora sources; they are not Windows prerequisites.

The frozen manifest is a historical pre-execution document: its `dft: null` / preparation status has deliberately not been rewritten. Use `evidence/comparisons.json` and the final audits for completed results. Historical source trajectories, publication documents and the original 140-file sealed preparation ZIP are referenced for upstream provenance; they are **not needed** to reproduce this offline baseline comparison. This archive supplies the exact 14 geometries, inputs, potentials and archived UMA values/forces used here. It does not supply the four missing UMA host results.

## Report correction (archive preserved)

The immutable archive's `REVIEW_REPORT.md` calls **0.435954 eV/Å** the largest new force. That is the largest new **complex** force. The overall largest new force is **0.565884531 eV/Å**, water `f0.010_host`, QE atom 115. The archive's per-job table, raw forces and machine-readable statistics already contain the correct host value. Current tracked reports correct this wording; no raw result, energy, geometry or archive hash changed.

## Fedora-only execution and preserved checkpoints

All `launch_*`, `run_qe75_*`, worker, guardian, finalizer, control-check and historical terminal-audit commands assume Fedora/systemd/cgroup v2, local execution receipts and the original software build. **Do not execute them as part of Windows analysis.** Successful controller tests are historical evidence, not permission for another run. The portable verifier is the supported offline entry point.

Full checkpoints and scratch remain under `/home/harshsahu/MOF_for_DAC_Opt/`:

- New 12 jobs: `local/qe75-baseline12-recovery-v2/job01/run01/scratch/` through `job12/run01/scratch/` — 9.093915 GiB total.
- First water complex: `local/qe75-fedora-completion-v5/run01/scratch/`.
- Second water complex: `local/qe75-second-v7/run01/scratch/`.
- Interrupted original host and all earlier failures: `local/qe75-baseline12-v1/job01/run01/` and the historical paths in the Fedora handoff.
- Full accounting/receipts: `evidence/qe75-baseline12-recovery-v2/`, `evidence/qe75-fedora-completion-v5/`, `evidence/qe75-second-v7/`.

The review ZIP omits binary charge-density, PAW and wavefunction checkpoints. Future restart/archival backup requires separate transfer plus exact compatibility review; Git pull is **not** a full restart backup. No evidence was deleted.

Execution dependencies were QE 7.5 (`local/qe75-fedora-v1/build/bin/pw.x`, SHA256 `0d1f6d9ac37a99f4f3fb72359bd3b6ffe54594cea92ed46a596238fa9283d8f1`), GCC/gfortran 16.2.1, OpenMPI 5.0.10, FFTW 3.3.10 and OpenBLAS 0.3.34; build details are in `docs/UIO66_QE75_FEDORA_V1.md`. They are not required or bundled for Windows offline analysis. General project development needs the packages in `pyproject.toml`; broader pytest tests require the optional dev dependencies.

## Pending decisions

- Review the completed baseline; retain 80/600-Ry results as provisional. SCF convergence does not establish accurate energy differences or UMA accuracy.
- The next prepared numerical check is **two paired water-complex 80/750-Ry SCFs**, with only `ecutrho` changed. This is **not authorized**. Estimated 12–13-GiB demand exceeds the unchanged laptop 10-GiB high / 11-GiB hard limits; verify a larger-memory allocation first.
- Fix the assessment metric/threshold explicitly: historical **2–3 meV** and **0.005–0.01 eV/Å** are ranges, not binding pass thresholds. Compare the change in second-minus-first energy and mapped force components, actual FFT/G counts and negative pseudocharge.
- Density checks alone leave wavefunction cutoff, k-points and transfer to hosts/CO₂ unresolved. Settings changes may require recalculating affected comparison groups.
- Persistent negative pseudocharge is neither automatic acceptance nor rejection. Large forces are allowed for deliberately frozen snapshots. The −0.294481-meV CO₂ guest-associated remainder has unresolved sign; these differences are not adsorption energies.
- Physical validity, publication proton correspondence, the failed sampling-stability pilot and four missing UMA host single points remain unresolved. No relaxation, UMA, refitting or design expansion is authorized.

## Commit scope and verification

All outstanding source/report/plan changes from the Fedora continuation are retained in this commit. Seven untracked machine-specific operational configs stay on Fedora unchanged: `configs/qe75-fedora-{feasibility-v2,completion-v3,completion-v5}.json`, `configs/qe75-rho625-{v1,v2}.json`, `configs/qe75-second-{v6,v7}.json`. They contain local paths and historical authorization/deadline state; the superseded rho625-v1 flag is not current authorization. Necessary completed-job config receipts are already in the review ZIP. None is required by the portable verifier.

Ignored `local/`, `evidence/`, caches, old large archives and scratch were not broadly staged. Only the requested ZIP and its checksum/receipt were force-added. No ignore rules were weakened. Scoped `.gitattributes` preserve QE plan bytes and LF source files across Windows checkouts; the historical CRLF atom-map CSV is retained byte-for-byte. Existing source dependencies are tracked; all scientific inputs needed by the portable review are inside the ZIP.

Verification on Fedora: 140 portable raw members byte-identical to retained local evidence; all 471 ZIP payload checksums pass; portable reconstruction passes 14 SCFs / 1,717 forces / four energy comparisons. Seven new portable tests and six existing Fedora preparation tests pass (13 total), without QE/UMA. The generic pytest runner is not installed in the system interpreter; these targeted tests use standard-library unittest. A second portable test run using only staged files in an isolated temporary directory also passed; no Fedora evidence directories were available there. Staged whitespace checks and credential-signature screening passed. Remote commit verification is reported after the push.
