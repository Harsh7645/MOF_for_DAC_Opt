# Parameter sourcing and validation contract

Status: Phase 1 design frozen; only Stage A has executed. Stages B/C require real
data and chemistry review. A stage label records evidence strength, not accuracy.

## Stage A — controlled synthetic coefficients

`mof_dac.instances.slot_problem` defines two choices per abstract fixed-template
slot. The fixed metal/node is removed from the decision vector. Each slot is
one-hot; the number of abstract functionalized B options is exact; a redundant
total-occupancy row mimics a charge audit. Linear coefficients are seeded normal
draws and pair coefficients occur only on a declared ring contact graph. Values
are dimensionless and have no chemical identities.

The full pairwise regression model is
`y = c + sum_i h_i*x_i + sum_(i<j) J_ij*x_i*x_j + error`.
`mof_dac.parameters.fit_pairwise` reconstructs it with least squares and rejects
rank-deficient designs. A test recovers known coefficients on the complete
four-bit hypercube to numerical precision. This verifies feature ordering and the
factor-of-two convention; it does not validate adsorption. Feasible one-hot data
generally creates gauge/rank dependencies, so real fitting needs a reduced encoding
or explicit gauge and must report design rank.

## Stage B — interpretable heuristic model

Required inputs: stable slot IDs, explicit linker identities/protonation, a fixed
template/contact graph and one common score scale. Candidate linear features may
represent sourced affinity proxies, functional-group count, size or regeneration
penalties. Pair features may represent contact multiplicity, geometric overlap and
environment-specific compatibility. Every feature needs source/version, units,
transformation, missing-value policy and uncertainty. Fit only on a development
split; report rank, condition number, held-out error/ranking, ablation and sensitivity.

Acceptance requires reproducible construction, no silent missing-as-zero values,
identifiable parameters, stable conclusions under coefficient perturbation and
better held-out prediction/ranking than constant and additive controls. Until then,
Stage B remains a design rather than a chemistry model.

## Stage C — DFT/physics-grounded second pass

Choose a licensed reference CIF and reconstruct every selected configuration.
Freeze cell convention, functionalization/protonation, charge/capping, defects and
target conditions. Compute labels for whole configurations; do not treat CoRE
structures as h/J observations. Fit the pairwise surrogate on a rank-audited design,
validate on held-out configurations, and inspect systematic residuals. If residuals
depend on three-site motifs or loading, extend the model or narrow its domain.

Record code/version, functional/basis or force field, dispersion treatment,
geometry protocol, convergence thresholds, cell/CO2 state, target units and raw
outputs. Compare top-K candidates with independent higher-fidelity calculations.
Only Stage C supports material-ranking claims; synthesis/DAC claims still require
appropriate experimental or validated simulation evidence.
