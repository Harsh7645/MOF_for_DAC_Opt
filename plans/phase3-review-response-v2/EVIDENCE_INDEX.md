# Evidence index v2 — clarified captions and inspection

Read [manuscript v2](../../docs/MANUSCRIPT_METHODS_RESULTS_V2.md),
[response table](../../docs/PHASE3_REVIEW_RESPONSE_V2.md) and
[clarifications](../../docs/PHASE3_SCIENTIFIC_CLARIFICATIONS_V2.md) together.
All central numerical tables and seven figure pairs are unchanged from v1.
These captions clarify interpretation; they do not retroactively change outcomes.

|Item|Current caption/interpretation|
|---|---|
|[T1](../phase3-methods-scope-v1/evidence/T1_synthetic.csv), [F1](../phase3-methods-scope-v1/evidence/F1_solver_outputs.svg)|Unequal budgets; fixed synthetic objectives. Raw continuous/binary feasibility distinct. x_B−x_A stable exact-count decoding does not optimize H. Feasibility 1e-7; gap-hit 1e-8 synthetic units.|
|[T2](../phase3-methods-scope-v1/evidence/T2_six_bit_objective.csv)|Six-bit fitted objective, not a reliable material ranking. No prescribed amino count; threshold ≥0.5; binary gap-hit 1e-8 eV.|
|[T3](../phase3-methods-scope-v1/evidence/T3_surrogate.csv), [F2](../phase3-methods-scope-v1/evidence/F2_surrogate_adequacy.svg)|51 development and 13 historically exposed designs. Pairwise MAE generally worse; leave-group-out RMSE exception visible. Additive descriptive reference only.|
|[T4](../phase3-methods-scope-v1/evidence/T4_stability.csv), [F3](../phase3-methods-scope-v1/evidence/F3_coefficients.svg)|Coefficient ranges 2.5–97.5%; pairwise conditional on 977/1000, excluding 23 deficient fits; additive 1000/1000. Rank failure is retained evidence, not evidence of physical interactions.|
|[S1 residuals](../phase3-methods-scope-v1/evidence/S1_pattern_residuals.svg)|Development grouped out-of-fold residuals and exposed historical evaluation remain separate; no chemical mechanism inferred.|
|[S2 ranking](../phase3-methods-scope-v1/evidence/S2_conditional_ranks.svg)|5–95% rank/overlap/correlation ranges, pairwise 977/1000 versus additive 1000/1000; preferred-pattern frequencies have the same denominators. Conditional on fixed labels and 51 patterns, not physical rankings.|
|[S3 sampling](../phase3-methods-scope-v1/evidence/S3_nested_sampling.svg)|Nested two-to-four-start sensitivity, not calibrated uncertainty or a variance decomposition.|
|[T5](../phase3-methods-scope-v1/evidence/T5_sampling.csv), [F4](../phase3-methods-scope-v1/evidence/F4_sampling_batches.svg)|Distinct seed-stream batches conditional on shared model/placement rules; not unconditional IID accepted poses. Gas-specific failures cannot be hidden by paired cancellation. Original energy/ranking gate failed.|
|[T6](../phase3-methods-scope-v1/evidence/T6_relaxation.csv)|All 48 matched paths; four guest failures at the initial 5-meV criterion retained. Coincident checkpoints and replay agreement are not physical validation.|

Inspection entry point: [exact structures and chemistry questions](../../docs/CHEMISTRY_INSPECTION_REVIEW_V2.md).
New outputs: [749 coordinate rows](inspection/coordinates.csv),
[cell vectors](inspection/cells.csv), [image-labeled view coordinates](inspection/view_images.csv),
[20 OH vectors](inspection/OH_vectors.csv), [all bootstrap statuses](inspection/bootstrap_draw_status.csv),
[coefficient endpoints](inspection/coefficient_endpoints.csv),
[conditional summary inventory](inspection/conditional_summary_definitions.json),
[all saved numerical stability summaries](inspection/saved_stability_summaries.json),
[eight-pattern selection](inspection/pilot_selection.csv), [512 seed records](inspection/pilot_seed_streams.csv).

Node/guest panels and archived before/after views are in [views](inspection/views).
Leader lines connect labels to atoms; they are not chemical bonds. Two projections
and full coordinate/image tables accompany each view. Checkpoints and exact
parent/CIF copies are in [exact](inspection/exact).

Reproduction and archive boundary: [README](README.md).
Both geometry questions and independent final review remain open in
[review_status.json](review_status.json). No approval is inferred from local checks.
