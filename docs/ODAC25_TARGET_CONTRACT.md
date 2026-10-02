# ODAC25 paired-target contract v1

Approved direction: paired CO2/H2O atomistic adsorption targets using ODAC25 and
Kaggle NVIDIA compute. This contract does not define DAC working capacity.

## Target

For matched parent MOF and explicit isolated-molecule references:

\[
E_{ads}=E(MOF+n_cCO_2+n_wH_2O)-E(MOF)-n_cE(CO_2)-n_wE(H_2O).
\]

The paired single-adsorbate target is
`[E_ads(CO2), E_ads(H2O)]` in eV. The competition diagnostic is
`delta = E_ads(CO2) - E_ads(H2O)`; lower values indicate stronger CO2 binding
relative to H2O within this energy definition. Delta is not adsorption selectivity,
working capacity or performance at 400 ppm.

## Evidence rules

- Read actual ODAC25 metadata before mapping parent IDs or adsorbate counts.
- Require the same parent MOF identity and split for each pair.
- Reject duplicates, missing references, nonfinite energies and cross-split IDs.
- Preserve official split and revision; do not tune on validation/test labels.
- Report CO2 MAE/RMSE, H2O MAE/RMSE, delta MAE and delta top-K overlap.
- UMA total-energy output is not an adsorption energy until the subtraction above
  uses compatible calculations and reference states.
- Paired targets do not create building-block h/J coefficients automatically.

## Model sequence

1. Inventory a revision-pinned ODAC25 subset and inspect `Atoms.info` schema.
2. Run UMA 1.2.1 with `task_name="odac"` on a small untouched shard.
3. Profile a target-bearing shard, then freeze the trajectory/frame selection rule
   from observed metadata before constructing verified paired adsorption records.
4. Establish frozen UMA and simple composition baselines.
5. Fine-tune on training data only if the smoke result, disk budget and metadata
   support a reproducible run.
6. Add a CGCNN/MOFTransformer-family baseline to preserve the original report's
   comparison category; do not force an incompatible pretrained target.

## Frozen relaxation reduction v1

Authenticated profiling of `val/mof_plus_adsorbate/part_00000.aselmdb` found
560,208 rows, 151 MOFs, 3,590 trajectories, 138 MOFs with both pure CO2 and pure
H2O records, and 285 repeated MOF-gas groups. All target fields were present and
finite; adsorbate-count consistency failures were zero. The pure-gas counts do
not by themselves imply `nads == 1`.

Materialization therefore:

1. keeps exact one-molecule CO2 or H2O rows only;
2. retains the largest `fid` within each trajectory (final stored frame);
3. retains the lowest `energy_ads_corrected` among final frames sampled for the
   same MOF/gas;
4. pairs gases only by identical `mof_name` and split.

The final-frame rule follows the dataset's relaxation-trajectory/fid semantics.
The minimum across trajectories represents the strongest sampled configuration,
not equilibrium selectivity or DAC working capacity. Every selected trajectory,
fid and source index is retained for audit.

## Authenticated materialization result

The v1 rule executed on Kaggle on 2026-09-14 over all 560,208 validation rows.
It produced 285 exact single-gas targets and 138 paired MOFs. Evidence is stored
under `../artifacts/kaggle/odac25_paired_targets_2026-09-14/`; the downloaded
archive SHA-256 is
`9BDD96948D41C3C32AB8847BE20217B09CE909BF83174C093B20D8AFE9FE0C50`.

This freezes the validation target table. Training statistics, feature fitting
and hyperparameter selection must use training data only.

Authentication uses the Kaggle secret `HF_TOKEN`. Tokens, checkpoints, raw LMDBs
and generated artifacts are excluded from Git.
