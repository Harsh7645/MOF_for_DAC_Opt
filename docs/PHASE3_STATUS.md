# Phase 3 status — DFT baseline complete; material validation open

Documentation reviewed **26 October 2026**; scientific records through **10 October**.
**Phase 3 is incomplete.** The 138-MOF ODAC25 benchmark, 64-configuration UiO-66
fit and selected frozen-snapshot DFT diagnostic are separate studies.

| Workstream | Current evidence and limit |
|---|---|
| Synthetic optimizer benchmark | Complete; SA 55/60 at 4,000 steps on 50 bits, decoded SNN 7/20. |
| 138-MOF ODAC25 prediction/ranking | Targets frozen; compatible training/reference data and shared ridge/UMA/CGCNN results pending. |
| 64-configuration UiO-66 experiment | UMA labels, provisional h/J and solver comparison complete; sampling stability and physical validity unresolved. |
| Independent DFT diagnostics | 14 baseline SCFs complete: seven complex snapshots and seven stripped hosts; not top-ten material validation. |
| Numerical convergence | v2.1 prepared, no refined result; algebra confirmation and machine/build/allocation pending. |

Read [remaining work](REMAINING_WORK.md), [baseline results](UIO66_QE75_BASELINE14_RESULTS_V1.md)
and [convergence v2.1](UIO66_QE75_WATER_CONVERGENCE_V2.md) for current decisions.
Earlier dated milestones below describe progress at their recorded dates.
No new calculation or scientific signoff is reported by this documentation refresh.

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
- Material-ranking comparison on the 138-MOF pool: NOT RUN.
- Separate provisional UiO-66 labels/h/J and solver comparison: COMPLETE, not physically validated.
- Selected frozen-snapshot DFT baseline: 14/14 SCFs COMPLETE and verified.
- Numerical convergence/refinement checks: PREPARED, NOT RUN.

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
protocol and limitations. At this early milestone, paired labels and the fit
were not yet available; the later completed design result below supersedes that
state. Full-pool prediction and independent material validity remain open.

## Paired design pilot, 2026-10-03

The separate UMA design experiment now has two audited paired pilot targets,
from 8/8 accepted starts. At the pilot stage the full 64-state/four-start run
was active and fitting had not executed. The completed result below supersedes
that running state; it is not a currently active job.
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

## Sampling and matched-geometry diagnostics, 4–5 October

The larger eight-design/32-start-per-gas pilot completed 512 starts and 16
force continuations but failed its registered sampling-stability gate. The
48-path matched diagnostic subsequently saved 144 checkpoints; 44/48 component
paths met the initial last-energy-change target. Replay agreement and relaxed
paths help investigate sensitivity; they do not establish physical UMA accuracy
or reverse the failed ranking-stability gate. The 13 originally held-out design
states have since informed development and are not an untouched final test.
See [sampling results](UIO66_SAMPLING_PILOT_RESULTS.md) and
[matched diagnostic results](UIO66_MATCHED_DIAGNOSTIC_V2_RESULTS.md).

## Independent frozen DFT baseline, completed 10 October

All seven selected complex snapshots and seven matching stripped hosts completed
QE 7.5 PBE-D3(BJ) SCFs at 80/600 Ry with Gamma sampling, without ionic relaxation.
Windows offline verification checked 471 payload hashes, 14 SCFs, 1,717 force
vectors and four energy comparisons. The recorded integration suite passed
42 targeted tests; these checks were not rerun for this documentation refresh.

For later-minus-earlier complex-energy changes, DFT and archived UMA agree in
direction in all four selected comparisons. Their discrepancies are 2.14–4.39 meV
at the baseline settings, not a general model-accuracy estimate.
`Delta E_guest-associated = Delta E_complex - Delta E_stripped-host` includes
interaction and guest deformation, not isolated adsorption energy. The late CO2
remainder is -0.294481 meV; its sign is not numerically resolved. The largest
baseline force is 0.565884531 eV/Angstrom on a stripped-host H. These frozen
snapshots are not DFT-relaxed minima; SCF convergence is not numerical or physical
convergence. See [baseline results](UIO66_QE75_BASELINE14_RESULTS_V1.md) and
[offline review](UIO66_QE75_WINDOWS_OFFLINE_REVIEW_20261010.md).

## Current convergence preparation, v2.1

The [current specification](UIO66_QE75_WATER_CONVERGENCE_V2.md) registers
2.0 meV per energy-difference comparison, without per-atom normalization, and
maximum per-atom force-vector change <=0.005 eV/Angstrom separately per structure,
including all atoms. Both successive registered refinements and eventual common
refined protocol versus the original archived baseline must be assessed.
These are sensitivity rules, not absolute error bounds. Energy algebra remains
explicitly reconstructed pending focused confirmation; machine/build/allocation
are unassigned. No refinement SCF has run.

Two 80/750-Ry water checks are prepared. A machine/build change requires two
separate 80/600-Ry reproductions first; each stage has a proposed 8-hour/32-core-hour
ceiling. The proposed larger-memory workstation is not a verified allocation.
Water-complex checks alone do not validate hosts/CO2; wavefunction cutoff,
electronic tolerance and k-points remain separate. Preserve the original
professor packet as historical: its open threshold-choice request is superseded
by v2.1, while formula confirmation and scientific review remain pending.

The four missing UMA host results, failed sampling pilot, ODAC25 reference
mismatch, chemistry/proton correspondence, shared-pool surrogate comparison
and independent top-ten candidate validation remain open. No refit, expansion
or calculation is authorized by this status report.
