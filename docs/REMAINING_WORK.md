# Remaining work to complete the MOF-for-DAC optimization project

Updated: 2026-10-03

Current evidence: [PHASE3_REFERENCE_AUDIT.md](PHASE3_REFERENCE_AUDIT.md).
Composition baseline code, leakage checks, inference scaffolding and packaging
are implemented; strict training extraction and valid full-pool model results
remain incomplete. User authorized a
[provisional UiO-66 library](UIO66_PROVISIONAL_LIBRARY.md): 64 nominal patterns,
with 64 coordinate proposals from an authenticated ODAC25 parent. All 64 now
converged in fixed-cell UMA bare relaxation; saved trajectories and CIFs passed
the independent audit. Initial parent-operation grouping found 53 groups at
0.01/0.05 Angstrom; relaxed grouping found 54/53 respectively. These are
declared-tolerance diagnostics. Real adsorption coefficients, complete symmetry
review and chemical validation remain absent.
This does not close P3.6. Checkboxes
below represent complete evidence gates, not code existence.

This is the operational completion checklist for the research project. It starts
from the verified repository state: Phases 1 and 2 are complete for their
controlled computational scopes; the Phase 3 synthetic benchmark and the frozen
138-MOF ODAC25 validation target table are complete. Phase 3 model comparison,
the chemistry-grounded optimization loop, and Phase 4 remain.

## Completion definition

The project is complete only when all four statements are supported by saved,
reproducible evidence:

1. The constrained SNN method is compared fairly with SA and Gurobi on the same
   numerical objectives and constraints.
2. A model predicts the frozen paired CO2/H2O adsorption-energy target on unseen
   assembled MOFs without train/validation leakage.
3. Physical predictions are converted into auditable building-block `h_i` and
   `J_ij` coefficients, and the optimizer is run on that grounded objective.
4. Top configurations receive independent chemistry validation under declared
   DAC-relevant conditions, with limitations reported in the manuscript.

Passing only the numerical benchmark does not demonstrate useful MOF discovery.
Passing only the ODAC25 prediction benchmark does not demonstrate that the QUBO
representation can generate valid or synthesizable frameworks.

## Already complete — do not repeat

- [x] Source report and professor feedback extracted, archived and hashed.
- [x] Binary Hamiltonian, continuous relaxation and symmetric QUBO conventions.
- [x] Explicit occupancy, budget, charge and incompatibility constraints.
- [x] Synthetic parameter-recovery tests and controlled slot instance family.
- [x] Live `snn-opt==0.6.0` integration, convex control and nonconvex diagnostics.
- [x] Scalable exact-count decoder and 50-variable synthetic pilot.
- [x] Frozen 60-instance synthetic benchmark at 12, 20 and 50 bits.
- [x] Gurobi, constraint-aware SA and decoded-SNN numerical comparisons.
- [x] Authenticated ODAC25 inventory, schema inspection and T4 UMA smoke test.
- [x] Frozen ODAC25 exact-single-molecule reduction rule.
- [x] Authenticated validation materialization: 285 single-gas targets forming
  138 paired CO2/H2O MOFs with trajectory/frame/source-index provenance.

Authoritative completed evidence is in `PHASE1_SUMMARY.md`, `PHASE2_SUMMARY.md`,
`PHASE3_STATUS.md`, `phase3_results.json`, and
`../artifacts/kaggle/odac25_paired_targets_2026-09-14/`.

## Phase 3 — finish material prediction and ranking

### P3.1 Build a leakage-safe training set

Current state: the validation table is frozen. A matching training table does not
yet exist. Validation labels must not be used to select features, fit statistics,
tune hyperparameters or choose checkpoints.

- [ ] Inventory the filtered ODAC25 training archive without downloading the
  complete 555 GB archive.
- [ ] Define a bounded, shard-based extraction plan that fits Kaggle disk and
  session limits. Record archive URL/revision, member path, byte count and SHA-256.
- [ ] Apply the exact same v1 rule used for validation:
  - exact one-molecule CO2 or H2O records;
  - largest `fid` per relaxation trajectory;
  - lowest final-frame `energy_ads_corrected` per MOF/gas;
  - pair only identical `mof_name` and split.
- [ ] Save training single-gas and paired tables with source-index, trajectory and
  frame provenance.
- [ ] Verify finite targets, unique `(MOF, gas)` keys, consistent adsorbate counts,
  and zero MOF identity overlap between the chosen train and validation partitions.
- [ ] Record target distributions and coverage by MOF type. Do not alter the
  validation filter to increase sample count.
- [ ] Freeze all resulting manifests and hashes before model development.

Deliverables:

- `artifacts/kaggle/odac25_train_targets_<date>/paired_targets.json`
- `training_target_profile.json`, `evidence_manifest.json` and a run README
- a checked-in secret-free Kaggle notebook or script that recreates the artifacts

Exit criteria: the training table is reproducible, its provenance is complete,
and automated checks prove the official split boundary is preserved.

### P3.2 Establish simple training-only baselines

Purpose: complex models must outperform transparent low-cost predictors.

- [ ] Define structure-derived inputs available for train and validation records.
  Start with atom counts/composition and simple size features.
- [ ] Exclude adsorbate atoms from parent-MOF composition features, or represent
  them explicitly and consistently.
- [ ] Fit a constant predictor using training-set CO2/H2O means.
- [ ] Fit a small regularized linear or ridge composition model. Choose
  regularization using training-only cross-validation grouped by MOF identity.
- [ ] Freeze preprocessing, feature ordering, coefficients and training seeds.
- [ ] Evaluate once on the 138 frozen validation pairs.
- [ ] Report CO2 MAE/RMSE, H2O MAE/RMSE, delta MAE and delta top-10 overlap.
- [ ] Save per-MOF predictions so every aggregate can be recomputed.

Deliverables:

- `mof_dac/material_baselines.py` and focused tests
- `scripts/run_material_baselines.py`
- `artifacts/phase3/material_baselines.json`
- feature schema, split manifest and environment record

Exit criteria: deterministic reruns reproduce the same per-MOF predictions and no
validation statistic enters training or model selection.

### P3.3 Run a valid UMA adsorption-energy baseline

The existing UMA result is only a total-energy execution smoke test. It is not an
adsorption-energy baseline.

- [ ] Construct matched calculation triplets for every evaluated record:
  adsorbed MOF, corresponding bare MOF, and isolated CO2 or H2O reference.
- [ ] Verify atom identity, charge/spin assumptions, cell convention, correction
  convention and `task_name="odac"` compatibility for all three calculations.
- [ ] Define how ODAC25's re-relaxed bare-MOF correction maps to the UMA
  calculation. Reject subtraction that silently mixes incompatible DFT and UMA
  reference energies.
- [ ] Predict all component total energies with one pinned UMA checkpoint/version.
- [ ] Compute predicted adsorption energy using `ODAC25_TARGET_CONTRACT.md`.
- [ ] Run a small audit sample first, then the frozen candidate pool on a Kaggle
  T4. The current Kaggle/PyTorch build cannot run UMA on P100.
- [ ] Save per-component energies, failures, inference time, GPU, package versions,
  checkpoint identity and hashes.
- [ ] Evaluate the same paired metrics and top-10 definition used by the simple
  baselines. Failed structures remain in the reported denominator.

Deliverables:

- matched-triplet manifest and validation report
- secret-free Kaggle UMA adsorption notebook
- `uma_adsorption_predictions.json` and `uma_adsorption_metrics.json`

Exit criteria: each reported adsorption prediction can be reconstructed from
three compatible saved component calculations. No total-energy smoke metric is
presented as adsorption accuracy.

### P3.4 Add the report-required graph/Transformer comparison

The scoping report requires surrogate screening using MOFTransformer or CGCNN.
One compatible model is sufficient; both are optional.

- [ ] Audit current official implementations/checkpoints against the frozen target,
  structure format, license and Python/CUDA environment.
- [ ] Select MOFTransformer, CGCNN or a documented equivalent only after confirming
  it can consume the assembled structures and predict the paired energy target.
- [ ] Convert structures using a deterministic, versioned preprocessing pipeline.
- [ ] Train on training data only. Use grouped folds within the training partition
  for architecture and hyperparameter decisions.
- [ ] Freeze the checkpoint before evaluating the 138-MOF validation table.
- [ ] Record seeds, learning curves, checkpoint hash, parameter count, training
  time, inference time, GPU and failures.
- [ ] Report the same metrics and candidate pool used for other baselines.
- [ ] If neither named model is target-compatible, document the incompatibility
  and use a current DAC-specific graph model without calling it the named baseline.

Deliverables:

- model decision and license/provenance records
- training/evaluation configuration and checkpoint hash
- per-MOF predictions and comparison metrics

Exit criteria: at least one learned assembled-structure baseline has a reproducible,
leakage-safe score on the frozen validation set.

### P3.5 Produce the material-ranking benchmark

- [ ] Freeze the candidate pool at the 138 authenticated validation MOFs unless a
  documented data-quality failure requires exclusion.
- [ ] Use `delta = E_ads(CO2) - E_ads(H2O)` only as the declared competition
  diagnostic. Do not call it working capacity, selectivity or 400 ppm performance.
- [ ] Freeze `K=10` before viewing model ranking outcomes.
- [ ] Compare constant, composition, UMA and graph-model predictions using the
  identical target rows and metrics.
- [ ] Report per-gas errors, delta error, top-10 overlap, rank correlation,
  confidence intervals where supported, failure counts and measured cost.
- [ ] Produce a top-candidate table with structure IDs and provenance, labeled as
  model ranking pending independent validation.
- [ ] Document error cases, model disagreement and out-of-distribution structures.

Deliverables:

- `docs/phase3_material_results.json`
- `docs/PHASE3_MATERIAL_SUMMARY.md`
- comparison table and publication-quality error/ranking figures

Exit criteria: all model categories are compared on one frozen pool and Phase 3's
material claims are limited to held-out adsorption-energy ranking quality.

### P3.6 Ground the QUBO coefficients in real material evidence

This is the missing bridge between assembled-MOF prediction and the project's
building-block optimizer.

- [ ] Freeze a real design family: zirconium node, UiO-66 topology/template and a
  finite set of amine/linker substitutions.
- [x] Define provisional six-bit variables precisely: one BDC/NH2-BDC choice
  at each occupied mapped slot. Chemistry approval remains separate.
- [ ] Fix unit-cell multiplicities, protonation, node capping, defects, formal
  charges, linker budget and allowed substitutions with chemistry review.
- [x] Build provenance-bearing provisional assembled structures for all 64
  configurations; retain input hashes, atom mapping and final relaxed CIFs.
- [ ] Validate structure identity, coordination, periodic connectivity and charge
  before any energy calculation.
- [ ] Score assembled configurations with the selected physical model and a
  consistent target/condition.
- [ ] Fit `H(x) = sum(h_i*x_i) + sum(J_ij*x_i*x_j)` using an identifiable design
  matrix.
- [ ] Record units, normalization, uncertainty, regularization and rank/condition
  diagnostics. Compare additive-only and pairwise models on held-out structures.
- [ ] Reject unsupported coefficients; never fill missing chemistry with silent
  zeros. Distinguish a modeled zero from an unknown interaction.
- [ ] Freeze a grounded interaction graph and rerun SNN, SA and Gurobi on the
  identical constrained objective.
- [ ] Test whether low-H configurations have improved held-out physical labels.

Deliverables:

- approved building-block/slot library and structure manifest
- real-coefficient graph with source, method, units and uncertainty per value
- parameter-fit diagnostics and held-out prediction report
- grounded SNN/SA/Gurobi artifacts and ranked configurations

Exit criteria: at least one auditable end-to-end path exists from real assembled
structures to `h/J`, constrained optimization, reconstructed candidates and
held-out physical scores.

## Phase 4 — validate, analyze and write

### P4.1 Reconstruct and validate top configurations

- [ ] Convert each selected bit vector into an explicit periodic structure.
- [ ] Confirm slot occupancy, atom counts, bonding/coordination, periodic images,
  charge/protonation, duplicate identity and parent-template consistency.
- [ ] Reject invalid structures before property evaluation and report the invalid
  fraction instead of silently removing it.
- [ ] Record deterministic reconstruction code and structure hashes.

Exit criteria: every top candidate maps to one reviewable structure, or is marked
invalid with a specific reason.

### P4.2 Perform affordable independent top-K validation

- [ ] Agree with the professor on the validation method and budget: DFT, a trusted
  higher-fidelity calculation, or an external independently labeled source.
- [ ] Freeze protocol, candidate count and selection rule before expensive runs.
- [ ] Declare temperature, pressure, gas composition, humidity and regeneration
  assumptions for any DAC/process claim.
- [ ] Validate the same top-K budget for competing methods where feasible.
- [ ] Save inputs, convergence status, outputs, failures, versions and compute cost.
- [ ] Compare predicted and independent ordering, uncertainty and failure modes.

Exit criteria: the strongest material claims have evidence independent of the
model used to select candidates.

### P4.3 Run sensitivity and ablation studies

- [ ] Vary `h/J` uncertainty, scaling and sparsification.
- [ ] Vary hard-constraint bounds, charge assumptions and block library.
- [ ] Compare raw SNN output, thresholding and distance repair separately.
- [ ] Ablate pairwise `J` terms against an additive-only model.
- [ ] Measure stability across SNN/SA seeds and budgets.
- [ ] Analyze results versus problem size, density, curvature and constraint
  tightness.
- [ ] Keep negative and nonconverged results in denominators.

Exit criteria: conclusions remain supported under reasonable modeling choices, or
their sensitivity is explicitly bounded.

### P4.4 Evaluate neuromorphic deployment claims honestly

- [ ] Keep CPU wall-clock results as descriptive software measurements.
- [ ] Define a target SNN hardware platform and measurement protocol if an energy
  or speed claim is retained.
- [ ] Measure preprocessing, encoding, execution, decoding and repair, including
  host overhead and failed runs.
- [ ] Otherwise state energy-efficient neuromorphic execution as a future
  deployment hypothesis.

Exit criteria: no CPU-simulation headline claims unsupported hardware speed or
energy superiority over optimized SA or Gurobi.

### P4.5 Statistical analysis and figures

- [ ] Freeze scripts and regenerate every table/figure from raw artifacts.
- [ ] Report seed distributions, feasible fractions, gaps and confidence intervals
  instead of only best runs.
- [ ] Separate numerical-optimizer figures from material-prediction figures.
- [ ] Include violations, failed cases, repair cost and data coverage.
- [ ] Create at minimum: workflow, benchmark-quality, feasibility, material-error,
  ranking/top-K and sensitivity figures.
- [ ] Put dataset split, units, sample count and limitations in captions.

Exit criteria: every plotted number traces to a saved machine-readable artifact.

### P4.6 Reproducibility bundle

- [ ] Pin Python, CUDA, solver and model versions.
- [ ] Save environment files, seeds, configurations and data manifests.
- [ ] Provide CPU instructions for synthetic tests and Kaggle GPU instructions for
  external model runs.
- [ ] Verify a clean-environment rerun of tests and a representative experiment
  from each track.
- [ ] Scan archives and Git history for secrets, private data and oversized files.
- [ ] Document licenses and access requirements for data, models and structures.

Exit criteria: another researcher can reproduce reported aggregates using the
documented inputs without receiving the Hugging Face token.

### P4.7 Manuscript and final audit

- [ ] Write methods: representation, constraints, parameter sourcing, SNN mapping,
  baselines, data splits, target and validation.
- [ ] Separate numerical, predictive and chemical-validity results.
- [ ] State the nonconvex SNN limitation and absence of a global guarantee.
- [ ] State that paired adsorption energy/delta is not DAC working capacity or
  experimental selectivity.
- [ ] Complete and verify the literature review before claiming novelty.
- [ ] Include unsuccessful runs, assumptions, data and hardware limitations.
- [ ] Run milestone, code, data-leakage, security and citation audits.
- [ ] Obtain professor review of chemistry assumptions and final claims.

Exit criteria: manuscript claims match the evidence and every result has a
traceable source artifact.

## Decisions requiring professor or user input

Prepare concrete options before requesting these decisions:

1. Exact real design family and finite linker/amine library.
2. Slot semantics, UiO-66 cell multiplicities, protonation/capping and defect
   policy.
3. Final physical objective beyond the adsorption-energy competition diagnostic,
   especially if working capacity or humid-air performance is claimed.
4. Independent validation method and affordable top-K budget.
5. Availability of direct neuromorphic hardware measurements.
6. Target venue, manuscript format and submission deadline.

Training extraction, baseline scaffolding, compatibility audits and analysis code
can continue before these decisions are finalized.

## Compute and storage plan

| Work | Minimum practical resource | Notes |
|---|---|---|
| Local tests, QUBO, SA and small Gurobi runs | CPU | Current suite runs locally; no GPU needed. |
| ODAC25 archive profiling/materialization | Kaggle CPU plus sufficient disk | Stream bounded shards; do not retain the full archive. |
| UMA adsorption calculations | Kaggle T4 GPU | Current environment succeeded on T4 and failed on P100 architecture support. |
| Composition baseline | CPU | Fit after training features are frozen. |
| CGCNN/MOFTransformer training | T4x2 or comparable GPU | Measure memory/runtime after model and batch size selection. |
| DFT/GCMC validation | External compute allocation | Method and budget require professor agreement. |
| Neuromorphic energy claim | Target neuromorphic hardware | CPU simulation cannot supply this evidence. |

## Immediate execution order

1. Add bounded ODAC25 training-shard discovery/materialization.
2. Freeze training targets and parent-MOF composition features.
3. Implement and run constant plus composition baselines.
4. Build and verify UMA adsorbed/bare/gas triplets; run UMA on T4.
5. Select and run one compatible graph/Transformer baseline.
6. Produce the frozen 138-MOF material-ranking comparison.
7. Freeze the real block/slot chemistry and learn auditable `h/J` coefficients.
8. Run grounded SNN/SA/Gurobi optimization and reconstruct top candidates.
9. Complete independent validation, ablations, figures and manuscript.

## Final completion checklist

- [ ] Phase 3 material baseline comparison passes its exit criteria.
- [ ] Real `h/J` sourcing and grounded optimization pass their exit criteria.
- [ ] Phase 4 structure and independent top-K validation pass.
- [ ] Sensitivity, failure and solver ablation analyses are complete.
- [ ] Reproducibility bundle reruns and contains no credentials.
- [ ] Manuscript, citations and claim audit are complete.
- [ ] Professor approves chemistry assumptions and final interpretation.
