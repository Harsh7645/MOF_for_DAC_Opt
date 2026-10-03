# Phase 3 status — numerical track and paired targets complete, baselines open

## Frozen held-out benchmark

Executed 2026-09-11 using generator seeds 100–119 at 12, 20 and 50 bits: 60
dense frustrated synthetic instances. Gurobi 13.0.3 used one thread and a 30 s
limit and certified all 60 optima. Exact enumeration independently agreed on all
40 instances at 12 and 20 bits. The machine exposed 12 logical CPUs; timings are
local descriptive measurements, not hardware comparisons.

SA used exact-cardinality slot swaps, solver seeds 0–2 and budgets of 250, 1,000
and 4,000 steps. All 540 runs were feasible. Optimum hits by budget were:

| Bits | 250 | 1,000 | 4,000 |
|---:|---:|---:|---:|
| 12 | 60/60 | 60/60 | 60/60 |
| 20 | 53/60 | 56/60 | 59/60 |
| 50 | 18/60 | 48/60 | 55/60 |

SNN used one deterministic start per instance, 2,000 iterations and exact
equalities. Raw feasible fractions were 15%, 0% and 0% at 12, 20 and 50 bits.
Exact-count decoding was feasible for 60/60 outputs. Decoded optimum hits were
15/20, 10/20 and 7/20; mean decoded gaps were 0.0840, 0.5256 and 2.8450 synthetic
energy units. These results show declining solution quality with size under the
fixed CPU-simulation budget; they do not establish a hardware advantage.

Full per-instance and per-run evidence is in `phase3_results.json`.

## Material-ranking gate

Authenticated inventory and schema inspection have executed. The user has ODAC25
and UMA Hugging Face access and approved paired CO2/H2O atomistic adsorption
targets using Kaggle GPU. `ODAC25_TARGET_CONTRACT.md` freezes the energy definition, paired
metrics and boundary from process-level working capacity. The guarded inventory,
streamed member extraction, schema inspection and UMA smoke pipeline have
executed.

On 2026-09-12, `uma-s-1p2p1` with task `odac` processed 16 validation GCMC
structures on one Kaggle T4. Stored total-energy comparison gave MAE 0.0236525 eV,
RMSE 0.0248619 eV and maximum absolute error 0.0355138 eV. Kaggle reported the
inference cell completed in 216.508 s, including first-use model compilation and
cell overhead. The model emitted a heterogeneous-batch fallback warning but
returned all 16 records. Raw JSON, schema, inventory and archive metadata are in
`../artifacts/kaggle/odac25_uma_t4_smoke_2026-09-12/`.

The external manifest loader is implemented and tested. It requires stable IDs,
CIF paths, target values/units, split labels, source, license and explicit
conditions. It does not infer missing chemistry.

On 2026-09-14 the frozen exact-single-molecule reducer ran over all 560,208 rows
of the authenticated target shard. It produced 285 single-gas targets and 138
MOFs with paired CO2/H2O targets. The downloaded archive and full provenance are
in `../artifacts/kaggle/odac25_paired_targets_2026-09-14/`. Descriptively, median
corrected adsorption energies are -0.227023 eV for CO2 and -0.405304 eV for H2O;
the median CO2-minus-H2O delta is 0.198297 eV. These validation-label summaries
are not fitted baselines or material-performance claims.

## Exit audit

- Frozen held-out numerical family: PASS.
- Exact/Gurobi references and bounds: PASS.
- Constraint-aware SA with budget distributions: PASS.
- SNN raw/decoded held-out comparison: PASS.
- Real candidate selection: PASS for 138 authenticated validation pairs with
  trajectory/frame/source-index provenance.
- UMA ODAC execution smoke: PASS on 16 GCMC structures using one T4.
- CGCNN/MOFTransformer-family comparison: PENDING verified ODAC25 field mapping.
- UMA smoke result: PASS on T4. P100 is incompatible with Kaggle's current
  PyTorch build; the inspected GCMC shard has null adsorption-energy targets.
- Target-bearing extraction/profile tooling: IMPLEMENTED AND LOCALLY TESTED;
  authenticated Kaggle execution PASS. The 8,418,258,944-byte shard contained
  560,208 rows, 151 MOFs and 3,590 trajectories; 138 MOFs had both pure CO2/H2O
  records and 285 MOF-gas groups repeated across frames/configurations.
- Deterministic target reduction: PASS AUTHENTICATED EXECUTION. It keeps exact
  one-molecule rows, final trajectory frames and the strongest sampled final
  configuration, retaining provenance; 285 targets formed 138 pairs.
- Reproducible comparison across numerical baselines: PASS.
- Material-ranking comparison: NOT RUN.

Phase 3 cannot be marked scientifically complete until frozen non-leaking
composition and UMA adsorption-energy baselines, a compatible graph-model
comparison and the material-ranking evaluation execute. Synthetic optimization
work is complete and must remain labeled synthetic.

## Structural preparation milestone, 2026-10-03

All 64 provisional UiO-66 structures completed fixed-cell UMA bare relaxation
on two T4 GPUs. Saved trajectories, final CIFs and provenance passed independent
local checks: 64 converged, no severe contacts, no changed distance-inferred
bonds. Initial grouping: 53 groups at 0.01/0.05 Angstrom; relaxed grouping:
54/53. These diagnostics do not prove crystallographic or chemical validity.
Full suite: 39 passed; synthetic demo -4.6. Read
[UIO66_PROVISIONAL_LIBRARY.md](UIO66_PROVISIONAL_LIBRARY.md) for exact artifacts,
protocol and limitations. Phase 3 remains incomplete: no paired design labels,
real adsorption h/J, valid full-pool material prediction or learned baseline score.

## Paired design pilot, 2026-10-03

The separate UMA design experiment now has two audited paired pilot targets,
from 8/8 accepted starts. The full 64-state/four-start run is active; h/J fitting
and solver comparison are implemented but have not executed on full real outputs.
The frozen duplicate-group split has 51 training and 13 test states, rank 22.
See [UIO66_ADSORPTION_PROTOCOL.md](UIO66_ADSORPTION_PROTOCOL.md). These pilot
predictions are not independent chemistry validation or a frozen ODAC25 score.

## Full provisional design result, 2026-10-03

Supersedes the running/no-fit statements above. All 64 paired targets and 512
starts passed remote/local audits. Train-only 22-parameter fit and actual CPU
Gurobi/SA/SNN comparison executed. Held-out MAE: pairwise .0301754 eV versus
additive .0238031 eV. Two-to-four-start top10 overlap .4; sampling and rankings
are unstable. All solvers found the tiny fitted objective optimum; that is not
the best sampled configuration or independent chemical validation.
Read [protocol/results](UIO66_ADSORPTION_PROTOCOL.md) and
[recomputable numerical evidence](uio66_design_results.json). The exported
graph is explicitly heuristic/UMA-derived. This completes the provisional
computational path, not Phase3's unseen-MOF/chemical validation gates.
