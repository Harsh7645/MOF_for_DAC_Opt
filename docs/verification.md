# Verification record — 2026-09-11

Scope: Phases 1–2 computational work and Phase 3 frozen synthetic numerical track.
This is not chemical validation or a material-screening result.

## Environment and commands

Windows 11; Python 3.14.6; 12 logical CPUs; NumPy 2.5.3; SciPy 1.18.1;
snn-opt 0.6.0; Gurobi 13.0.3 with restricted non-production license. No usable
NVIDIA runtime was established because `nvidia-smi` was unavailable.

```powershell
python -m compileall -q mof_dac
python -m pytest -q
python -m mof_dac.phase2 --iterations 5000 --equality-band 0 --output docs/phase2_results.json
python -m mof_dac.phase3 --output docs/phase3_results.json
```

Tests: **24 passed**. Added checks require true convergence of the live convex SNN
control at exact equality, reproducible dense interaction generation, a quick
held-out Phase 3 pipeline, and strict external-material manifest validation.

## Phase 2 evidence

- Convex control: exact solution `[0,1]`, energy `-2`, `converged_feasible`, 251
  iterations, equality residual `1.11e-16`.
- Equality sensitivity: bands 0 and `1e-6` converge; `1e-3` returns the right
  feasible point but fails the upstream KKT threshold.
- Nonconvex 50-variable experiment: 0/5 raw states pass strict project feasibility;
  5/5 decoded states pass. Raw equality residuals are about `3.96e-6`–`5.20e-6`.

## Phase 3 synthetic evidence

- 60 held-out instances: seeds 100–119 at 12, 20 and 50 bits.
- Gurobi certified 60/60 optima; exact enumeration agreed on all 40 instances at
  12 and 20 bits.
- SA: 540/540 feasible. At 4,000 steps, optimum hits were 60/60, 59/60 and
  55/60 by increasing size.
- SNN: decoded feasibility 60/60; decoded optimum hits 15/20, 10/20 and 7/20.
  Raw feasibility was 3/20, 0/20 and 0/20.

Per-run records, budgets, versions, constraints, gaps and timings are retained in
`phase2_results.json` and `phase3_results.json`. All timings are local CPU
observations. No external dataset, surrogate, DFT, hardware-energy or material
discovery claim has been executed.

## ODAC25/UMA readiness

- Paired adsorption-energy construction and competition metrics: unit tested.
- Duplicate pair and structure-level split leakage rejection: unit tested.
- HF token accepted only through `HF_TOKEN`; no CLI token parameter or committed
  credential path exists.
- Revision-pinned inventory: authenticated PASS. The repository contained eight
  metadata files and external archive links, requiring a corrected streamed
  member extraction path.
- Filtered validation GCMC member: 847,228,928 bytes; schema inspection PASS on
  41,926 structures. Sampled adsorption-energy fields were null.
- Kaggle pipeline syntax and CLI help: PASS.
- Kaggle bundle secret-pattern scan: PASS across 20 packaged files.

UMA P100 execution failed because Kaggle's current PyTorch build excludes `sm_60`.
The T4x2 rerun completed while using one T4. `uma-s-1p2p1` with task `odac`
returned all 16 requested GCMC records on CUDA. Total-energy MAE was 0.0236525 eV,
RMSE 0.0248619 eV, maximum absolute error 0.0355138 eV and mean signed error
-0.0236525 eV. The inference cell took 216.508 s with first-use compilation and
cell overhead. Evidence is retained in
`../artifacts/kaggle/odac25_uma_t4_smoke_2026-09-12/`.

This validates the authenticated ODAC25-to-UMA execution path only. The sampled
GCMC structures have null paired adsorption-energy fields, so this run does not
validate the CO2/H2O target, rank materials or establish chemistry accuracy.
