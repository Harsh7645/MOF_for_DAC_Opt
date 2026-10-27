# Central evidence v1: captions and reproduction

All artifacts in `evidence/` are generated from existing saved results. CSVs
retain numeric precision; Markdown tables are display summaries. SVGs are vector
masters; PNGs are previews (new F1/F4 at 300 dpi). Prior figures are copied
byte-for-byte, preserving their original plots. All inputs/outputs have hashes in
`evidence/receipt.json`; input JSON snapshots are included. No new fits or calculations.

|Item|Caption / required interpretation|
|---|---|
|[T1 synthetic](evidence/T1_synthetic.md)|Synthetic energy units only. Three SA budgets and 3 seeds/instance versus one2000-iteration SNN start/instance; Gurobi 30-second/one-thread reference. Raw continuous and binary feasibility are explicit. Blank raw optimum/gap entries mean not scored, never zero.|
|[F1 solver outputs](evidence/F1_solver_outputs.svg)|Fixed-objective optimum recovery and raw-versus-decoded binary feasibility. Unequal budgets/starts, no hardware or general superiority claim. Continuous feasibility happens to match binary counts for these raw saved outputs; do not assume this generally.|
|[T2 six-bit objective](evidence/T2_six_bit_objective.md)|One fitted numerical objective,64 enumerated states. Gurobi 1 run/60-second cap; SA 10 seeds/2000 steps; SNN 10 starts/2000-iteration cap. Threshold outputs reuse raw runs, not 10 extra independent solves.|
|[T3 surrogate](evidence/T3_surrogate.md), [F2 adequacy](evidence/F2_surrogate_adequacy.svg)|All errors against sampled UMA labels, meV. Historical exposed13 and development 51 kept distinct. Pairwise MAE generally worse; leave-group-out RMSE exception visible. Repeated-CV medians are descriptive, not confidence bounds.|
|[T4 stability](evidence/T4_stability.md), [F3 coefficients](evidence/F3_coefficients.svg)|Whole-group development bootstrap, fixed labels.23 pairwise rank failures retained in original evidence; ranges condition on identifiable draws. No chemical-interaction or physical-uncertainty claim.|
|[T5 sampling](evidence/T5_sampling.md), [F4 batch sensitivity](evidence/F4_sampling_batches.svg)|Eight patterns,32 starts per gas in two16-start batches. Bars show absolute batch gaps in meV, not calibrated uncertainty.10-meV line is only part of the full frozen energy gate; green/low paired gaps cannot override unstable gas components.|
|[T6 relaxation](evidence/T6_relaxation.md)|All48 component paths retained; last energy changes in meV.44 pass initial5-meV target,4 guest paths fail. Coincident checkpoints can give zero change without independent convergence evidence.|
|[S1 residual patterns](evidence/S1_pattern_residuals.svg)|Signed prediction-minus-target errors; development out-of-fold versus historical exposed evaluation marked H. Exact bit order L0…L5; no new structural descriptors or chemical interpretation.|
|[S2 rank stability](evidence/S2_conditional_ranks.svg)|Bootstrap ranking over the 51 development patterns only, relative to each model's full-development fit. Not out-of-sample material-ranking accuracy.|
|[S3 nested sampling](evidence/S3_nested_sampling.svg)|First-two versus all-four starts; same four-start bare reference. Components and paired score separate; relationship to residuals is descriptive, not a variance decomposition.|

```powershell
python -m scripts.build_phase3_methods_package --output local/phase3-methods-package-NEW
python -m scripts.build_phase3_methods_package --source-package plans/phase3-methods-scope-v1/evidence --output local/phase3-methods-snapshots-NEW
python -m pytest tests/test_phase3_methods_package.py -q -p no:cacheprovider --basetemp local/phase3-methods-tests-NEW
```

Use new directories. The first command reads original local source artifacts;
the second verifies and uses the included snapshots and figures, so it does not
require the original trajectory archives. Both require NumPy and Matplotlib.
Existing raw trajectories/receipts remain in their original paths;
this compact package is not a replacement for raw archives or a claim that every
scientific result can be recomputed from summary JSON alone. The prior
development-analysis code/protocol remains the provenance for exploratory fits;
re-running fits is unnecessary for this publication-formatting step.

Exploratory baseline DFT stays in the existing baseline supplementary records. ODAC25
remains a deferred extension. Neither supplies a central quantitative result here.
