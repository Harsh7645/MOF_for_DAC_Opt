# Provisional UiO-66 paired adsorption protocol v1

Frozen before pilot results, 2026-10-03. This separate design experiment uses
the user-authorized provisional library. It does not replace ODAC25 targets,
train on its validation labels, or claim DFT/chemistry validation.

## Inputs and scope

All 64 six-bit BDC/NH2-BDC configurations have hashed, model-relaxed bare CIFs
under `artifacts/kaggle/uio66_bare_2026-10-03/`. Require their accepted bare
diagnostics and the same UMA-s-1p2p1 checkpoint SHA-256. Seed 41; fairchem 2.23.0,
task odac, batch inference. The input cell remains fixed and all positions are
free. Ideal protonation, defects and topology stay provisional.

For each state, evaluate one CO2 or one H2O molecule per primitive cell.
This is periodic single-molecule adsorption at the specified cell/loading;
there is no pressure, temperature, humidity or equilibrium uptake calculation.

## Calculation and acceptance

1. Initialize isolated CO2/H2O using ASE's built-in molecular geometries. Relax
   with the same odac model in a nonperiodic 30-Angstrom box. Retain gas energies,
   forces, structures and connectivity diagnostics; no DFT constants substituted.
2. Re-relax the imported bare CIF under the current calculator. This makes
   energy accounting consistent despite CIF coordinate rounding and runtime
   floating-point differences.
3. Generate uniform fractional centers and uniform SO(3) molecular orientations,
   using the same seed per state/gas. Reject host–guest distances below 2 Angstrom
   under periodic minimum images. Maximum 10,000 proposals; no placeholder if
   the requested count cannot be placed. Rejection can change accepted centers
   across substitution states. Initial geometry distances are assumptions.
4. Relax every MOF + gas using fixed-cell ASE LBFGS, maxstep 0.1 Angstrom,
   fmax 0.05 eV/Angstrom and 200 steps. Pilot: two states (000000/111111),
   two starts per gas. Main experiment: all 64 states, four starts per gas.
   Pilot and main results remain separate. Later larger sampling/budgets must
   be saved as separately named experiments.
5. Strip the gas from each resulting system and re-relax that empty MOF under
   the same limits. Accept only converged, contact-free results with unchanged
   inferred host and intramolecular gas bonds. Cross host/guest edges are
   diagnostic; a physical intermolecular contact alone is not a rejection.
6. Choose the lowest accepted bare energy among the initial empty structure and
   gas-removed re-relaxations from BOTH gases for each configuration. Exclude
   rejected/reacted states from that reference pool. Define
   `E_ads(g) = E_combo(g) - E_bare_common - E_isolated(g)` in eV.
7. The per-gas target is the minimum among its declared starts. Save all starts,
   failures, convergence flags, sampled energy range and selected start.
   A paired target is accepted only when every requested start and both gas
   references pass; otherwise keep it null. No silent incomplete-sample minimum.
8. `delta = min_sample E_ads(CO2) - min_sample E_ads(H2O)` is a competition
   diagnostic. Negative delta favors CO2 energetically under this model; it is
   not equilibrium selectivity or DAC performance.

The [official FAIR-Chem tutorial](https://facebookresearch.github.io/fairchem/adsorption-energy/)
supports relaxed-component energy subtraction and checking a gas-removed bare
relaxation for a lower reference. Our deterministic sampling and strict
acceptance rules are implementation choices, not claims that this search finds
a global ground state or reproduces the ODAC dataset's preprocessing.

## Before fitting coefficients

Audit saved trajectory energies/forces and input/output/source/checkpoint hashes.
Keep initial parent-operation duplicate groups together across train/test splits,
also merging newly detected duplicates. Require complete paired labels, full
rank for the 22-parameter design, held-out errors, additive comparison and
sampling-budget sensitivity. All coefficients would be UMA-derived provisional
coefficients; independent physics/chemistry validation remains open.

Current implementation: `mof_dac/adsorption.py`,
`kaggle/run_uio66_adsorption.py`. Tests cover periodic placement, shared bare
reference selection, failed-start null targets and saved-system bookkeeping
with an explicitly synthetic calculator. Authenticated execution is recorded
only after actual output is downloaded and audited.

## Executed pilot and frozen fit split

Actual two-state pilot, downloaded/audited 2026-10-03: all eight starts accepted.
Common-bare, same-model isolated references were CO2 -22.99743964487037 eV
and H2O -14.382842608318448 eV. Do not substitute ODAC25 DFT constants.

| State | Minimum CO2 Eads (eV) | Minimum H2O Eads (eV) | Delta (eV) | CO2 / H2O site ranges (eV) |
|---|---:|---:|---:|---:|
| 000000 | -0.287453 | -0.317142 | +0.029689 | 0.176822 / 0.369442 |
| 111111 | -0.308323 | -0.321023 | +0.012699 | 0.109191 / 0.089528 |

These are two-start UMA predictions, not independent physics, synthesis or DAC
validation. Sample spreads exceed the apparent difference between these states;
no robust material ordering is established. Raw evidence:
`artifacts/kaggle/uio66_adsorption_2026-10-03/pilot/`; local audit:
`artifacts/phase3/uio66_adsorption_pilot_audit.json`.

`data/design/uio66_fit_split.json` was frozen without full-run labels: merge
initial and relaxed 0.05-Angstrom duplicate groups, keep both inspected pilot
groups in training, seed 41, hold out 20% of groups. Result: 53 groups,
51 train / 13 test states; training rank 22. Do not change this split after
viewing scores. Approximate grouping does not establish crystallographic uniqueness.

`scripts/fit_uio66_adsorption.py` audits every report/trajectory, verifies frozen
source hashes and rejects incomplete/mixed-budget targets. Train-only OLS fits
`delta(x) = offset + h@x + 0.5*x@W@x` with symmetric zero-diagonal W;
each undirected edge stores J=W_ij. Compare seven-parameter additive OLS with
22-parameter pairwise OLS on the same held-out states. No ridge tuning or
all-data refit is hidden in this comparison. Training-group bootstrap uses
200 draws, discards unidentifiable draws and reports their count; intervals are
conditional sampling diagnostics, not calibrated physical error bars.
Nested two-start versus four-start delta/ordering/coefficient sensitivity is
also retained; this does not prove the four-start minimum is global.

Exported parameters use `parameter_regime=heuristic` with explicit UMA-derived
provenance and eV units. They are effective coefficients of a sampled competition
target, not measured intrinsic atomic affinities or steric interaction energies.
Six bits select substitutions in an already occupied neutral template. No new
chemical budget/charge/defect rules are invented. Chemical review remains open.

`scripts/benchmark_uio66_fit.py` compares the exported original polynomial on CPU:
64-state exact enumeration, one-thread Gurobi (60 s), SA seeds 0..9 (2,000 moves,
2 to 0.01 eV temperatures, up to four flips), and raw/thresholded SNN seeds 0..9
(2,000 iterations, no PSD shift, threshold x>=0.5, no exact energy repair).
Offsets are retained for target predictions and omitted consistently in gap
calculations. Failed runs stay in denominators. These routines are implemented;
no full real fit or solver result has executed at this milestone.

Replay: `kaggle/uio66_adsorption.ipynb`. Package audited bare inputs with:

```powershell
python -m scripts.package_kaggle --output artifacts/kaggle/UIO66_Adsorption_bundle.zip --uio66-bare-results artifacts/kaggle/uio66_bare_2026-10-03/uio66_full
```

Full-run outputs remain pending. These same-family diagnostics do not replace
the required unseen-MOF CGCNN/MOFTransformer comparison, frozen ODAC25 scores
or independent chemical validation.

## Full v1 execution and negative validation finding

Full outputs subsequently completed and were downloaded/audited on 2026-10-03:
64/64 complete pairs, 512/512 accepted starts, all four workers exit0. Saved
trajectory energies/forces, contacts, inferred bonds, CIF coordinates and
archived source/input hashes passed remote and local checks. Maximum system
force .049972475 eV/Angstrom; maximum steps200. The 133,472,188-byte archive
SHA-256 is `aee36cc47cda2b2088fc30c44f7fd240bad7e5731f71932a63018c4fc6bb1837`.

Frozen train-only fit executed: rank22, condition17.8487; 193/200 training-group
bootstrap draws identifiable. Actual prediction errors:

| Fit | Train MAE (eV) | Test MAE (eV) | Test RMSE (eV) | Test max error (eV) |
|---|---:|---:|---:|---:|
| Pairwise, 22 parameters | 0.0171251 | 0.0301754 | 0.0413030 | 0.1006442 |
| Additive, 7 parameters | 0.0240373 | 0.0238031 | 0.0275139 | 0.0510118 |

The pairwise model fits training better but predicts this holdout worse.
This is a negative validation result; coefficients are not validated material
interactions. No test-driven refit, ridge tuning or split replacement was done.

Nested two-to-four starts changed delta by a mean .0130766 eV and maximum
.1351513 eV. All-family Spearman .7260, top10 overlap .4; maximum train-fitted
h/J changes .0206631/.0506196 eV. Site-range medians CO2/H2O .135686/.326160
eV; maxima .196987/.467891 eV. These results establish sensitivity within this
sample, not a calibrated physical uncertainty bound. They do not support stable
rankings; more uniformly sampled sites/seeds and independent validation are needed.

Actual CPU comparison executed on this unchanged trained polynomial. Enumeration
and Gurobi agree on state110111, predicted delta -.0474215 eV (sampled -.0436706).
SA, raw SNN and thresholded SNN each found that fitted optimum in10/10 runs.
Hessian eigenvalue range -.086836 to .135148 eV; nonconvex experimental route,
no PSD shift. The best sampled state was111111, delta -.0879886 eV. Model/sample
top5 overlap .8 uses all64 including training and is not held-out validation.
Tiny six-bit recovery is an execution result, not evidence of large-scale solver
advantage, global SNN guarantees, reliable screening or improved DAC performance.

Recomputable evidence: [uio66_design_results.json](uio66_design_results.json).
Provisional coefficient graph:
[uio66_uma_train_fit_v1.json](../data/design/uio66_uma_train_fit_v1.json).
Raw data: `artifacts/kaggle/uio66_adsorption_2026-10-03/main/`;
local fit/solver reports: `artifacts/phase3/uio66_uma_fit/`.
The chemistry library and frozen ODAC25 comparison gates remain unapproved/open.
Phase3 overall remains incomplete.
