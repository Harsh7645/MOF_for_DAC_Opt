# Fixed review snapshot v2

27 October 2026. Entry point: [review response](../../docs/PHASE3_REVIEW_RESPONSE_V2.md),
[manuscript v2](../../docs/MANUSCRIPT_METHODS_RESULTS_V2.md),
[scientific clarifications](../../docs/PHASE3_SCIENTIFIC_CLARIFICATIONS_V2.md),
[chemistry inspection](../../docs/CHEMISTRY_INSPECTION_REVIEW_V2.md),
[closure checklist](../../docs/PHASE3_CLOSURE_CHECKLIST_V2.md).

The review snapshot is `snapshot.zip` beside this guide. Its external
`snapshot_receipt.json` and `snapshot.zip.sha256` record the ZIP checksum. The
archive includes `SNAPSHOT_MANIFEST.json`, listing every payload hash, source HEAD,
and the actual working-file hashes. HEAD alone does not identify this preparation:
pre-existing staged work was present and preserved. No commit is claimed.

The snapshot is created once with exclusive-create semantics. **Do not edit or
replace it.** Revisions need a new version/path and receipt. Responses belong in
`later_responses/` outside the snapshot, with the reviewed ZIP SHA256. The current
working repository may evolve; that does not change the frozen review record.
No signed scientific/chemistry approval has been received or inferred.

## Offline figure reproduction — no scientific runs

Extract into a new directory; use it as the repository root. Python, NumPy,
Matplotlib, ASE and pytest are the required local analysis dependencies. Versions
used in this preparation are recorded in the snapshot manifest. No install or
network access is performed by these commands.

```powershell
python -m scripts.build_phase3_methods_package --source-package plans/phase3-methods-scope-v1/evidence --output local/figure-replay-NEW
python -m scripts.prepare_phase3_review_response --output local/inspection-replay-NEW
python -m pytest tests/test_phase3_review_response.py -q -p no:cacheprovider --basetemp local/review-tests-NEW
```

The first command formats saved numerical results and copies five existing
figure pairs. The second copies exact checkpoints, filters existing inspection
tables, formats saved bootstrap/seed data and renders periodic images. It calls
no calculator, solver or fit. Matplotlib/font/version changes can change image
bytes; exact input and coordinate checks remain required. Do not overwrite
the included evidence with replay output.

## How the underlying scientific evidence was obtained — history, not launch instructions

- Synthetic experiment: 60 fixed slot objectives; Gurobi references and small
  enumeration; SA at three budgets; experimental nonconvex SNN and separate
  decoder. Source: `mof_dac/phase3.py`, `instances.py`, `formulation.py`; saved
  environment/protocol/run records in `evidence/inputs/synthetic.json` under the
  original methods package. The iteration/seed budgets are not matched.
- Ordered-pattern labels: historical UMA-s-1p2p1, task `odac`, fixed cell, four
  starts/gas, flexible atoms and same-model energy references. The pinned
  scientific checkpoint SHA256 is
  `b2673b85037b075674c25f55c34ffe1ff1e15db924be977b10a184765df0d5ce`.
  This is a label-generation convention, not validated adsorption physics.
- Historical OLS fits and 51/13 split are preserved. The later development-only
  grouped CV/bootstrap used the saved 51 labels, fixed protocol and all failure
  records. `scripts/analyze_uio66_development.py` documents that prior procedure;
  **do not rerun it to reproduce review figures**.
- The eight-pattern pilot and matched relaxation diagnostic ran previously on
  Kaggle with saved exact poses, model identity, trajectories and assessments.
  The review archive includes focused exact checkpoints and the frozen sampling
  manifest, not the full raw trajectory archives or model weights. Full scientific
  replication requires those historical archives, compatible environment, license/
  access, compute authorization and unchanged original protocols.
- Fourteen DFT baseline SCFs are exploratory supplementary history. No DFT
  executable, pseudopotentials, restart state or launch configuration is included
  as an executable continuation package. ODAC25 is a deferred extension.

This is a review/reformatting archive, not a promise of full scientific execution
from the small snapshot alone. Historical source documents can refer to material
in the full repository; new review entry-point links and all packaged payloads
are checked. The source allowlist excludes credentials, machine launch state,
model weights, private keys, environment files and recovery backups.

No QE/UMA calculation, solver experiment, refit, external message or expansion
is authorized by this snapshot. Historical approval flags are not current authorization.
