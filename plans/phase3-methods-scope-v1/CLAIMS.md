# Central claim-to-evidence review v1

This is a local source check, **not independent scientific review**. Current
wording is limited to the following claims; provenance hashes and checks are in
the scope package receipt. No novelty, material-ranking, SNN-superiority or
uncertainty-dominance claim is admitted.

|ID|Claim / source selector|Evidence|Scope and limitation|
|---|---|---|---|
|C1|Synthetic reference/SA results: `heldout.summary_by_bits`, `heldout.protocol`, `heldout.instances`|`evidence/inputs/synthetic.json`; T1/F1|60 synthetic instances; actual unequal budgets. Synthetic units, no chemical or hardware conclusion.|
|C2|Raw/decoded SNN feasibility and recovery: per-instance `snn_run`, `raw_violations`, aggregate decoded gaps|Same input; T1/F1; `mof_dac/phase3.py` and `formulation.py`|Raw continuous versus binary checks separated; decoder output is another candidate, not evidence raw dynamics satisfied constraints.|
|C3|All methods recover the six-bit fitted optimum: `solver_comparison.summary`, `.oracle`, `.runs`|`evidence/inputs/case.json`; T2; `scripts/benchmark_uio66_fit.py`|Only the fitted objective. Threshold uses same raw runs. No physical optimum or SNN advantage.|
|C4|Pairwise MAE generally worse; RMSE exception: historical train/test metrics, `cv`|`evidence/inputs/historical.json`, `development.json`, `split.json`; T3/F2|Historical 13 exposed; all new fits development-only. Correlated CV repetitions, no p-value. Additive descriptive only.|
|C5|Count/pattern residuals vary: `residuals_by_amino_count`, `historical_error_contributions`|`development.json`; S1; original `residuals_by_pattern.csv`|Descriptive, composition coverage unequal; no removed outliers or causal chemistry.|
|C6|Conditional coefficient/rank instability: `stability`, original bootstrap records|`development.json`; T4/F3/S2; prior `bootstrap_fits.json`|977/1000 pairwise identifiable;14/15 J ranges cross zero. Neither rank failures nor range signs establish interactions.|
|C7|Target sampling sensitivity and failed pilot: `sampling_sensitivity`, pilot `stability`|`development.json`, `pilot.json`; T5/F4/S3|Nested sensitivity is not an uncertainty estimate. Independent-batch pilot failure retained;509 clusters not proven minima. No cross-regime error-dominance ratio.|
|C8|Relaxation/replay behavior: `components`, `historical_start31_reproduction`, `matched_controls`|`evidence/inputs/matched.json`; T6; existing matched-v2 report/trajectories|48 paths,4 guest sensitivity failures. Reproducibility is numerical, not validation of model physics; rigid controls retain causal confounds.|
|C9|Ideal ordered structure assumptions and provenance|`docs/STRUCTURAL_MODEL_RECORD_V1.md`; source/mapping/publication comparison and saved 64 audit|Four node H and coherent formula are computational observations/bookkeeping. Proton correspondence and chemical adequacy still require qualified review.|

Supplementary-only:14 electronically converged frozen DFT baselines, with cutoff
convergence unresolved. Their numerical differences are **not evidence for a
central quantitative conclusion** in this revised manuscript. The existing
professor packet remains historical and must not override the new scope.

Deferred:ODAC25 identity/reference/training/benchmark, additional UMA host points,
DFT refinements, physical ranking/top-K validation and hardware performance.
Their omission from the central claims is a documented deferral, not completion.
