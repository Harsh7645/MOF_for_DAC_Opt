# MOF for DAC optimization

Working title: **Separating Optimization Performance from Target Reliability in a
Discrete MOF Design Workflow.**

The revised methods question separates fixed-objective solver performance,
surrogate adequacy and adsorption-target reliability before physical interpretation.
The 64 ordered UiO-66 patterns are provisional computational models, not established materials.

## Current status - 27 October 2026

Phases 1-2 computational scopes are complete. **Phase 3 remains incomplete** pending
qualified chemistry assessment and independent final review; local evidence and
manuscript preparation are complete. See the [scope revision](docs/RESEARCH_SCOPE_REVISION_20261027.md)
and [closure checklist](docs/PHASE3_CLOSURE_CHECKLIST_V2.md).

- [Central package](plans/phase3-methods-scope-v1/EVIDENCE_INDEX.md): actual synthetic
  budgets, raw/decoded feasibility, six-bit fitted objective, surrogate adequacy,
  development-only stability and failed sampling/relaxation criteria.
- [Methods/results draft](docs/MANUSCRIPT_METHODS_RESULTS_V2.md) and
  [structural record](docs/STRUCTURAL_MODEL_RECORD_V1.md) retain explicit limitations.
  No SNN advantage, physical predictor or reliable material ranking is established.
- ODAC25 is a deferred extension. Historical 138 selections are preserved, but
  parent identity/reference compatibility and benchmark remain unresolved.
  Investigation is paused; the request remains unsent.
- All 14 frozen baseline DFT SCFs are complete, but cutoff/grid/k-point convergence
  is unresolved. They are exploratory supplementary evidence only. Further DFT and
  larger-memory access are not dependencies of the limited methods scope.
- [Future convergence rules](docs/FUTURE_CONVERGENCE_RULES_V3.md) are confirmed:
  Sc/Sh/Sg each 2.0 meV where applicable, direct Sg testing, all-atom maximum force
  vector change 0.005 eV/Angstrom. Preserve both successive and direct-to-baseline
  comparisons; baseline drift does not prevent later refined convergence.

Original roadmap/evidence preserved. No new calculations, contacts or publication authorized.

Review revision: [response table](docs/PHASE3_REVIEW_RESPONSE_V2.md), [exact chemistry packet](docs/CHEMISTRY_INSPECTION_REVIEW_V2.md) and [fixed snapshot](plans/phase3-review-response-v2/README.md). Q1/Q2 and independent final review remain open.

## Start here

- [Beginner guide](beginner_guide.md): chemistry translated into graphs and optimization.
- [Project memory](context.md): source-derived math, four phases, decisions and open questions.
- [Agent instructions](agent.md): persistent research and benchmark requirements.
- [Chat handoff](chat_context.md): completed work, verification and next step.
- [Roadmap](.planning/ROADMAP.md): four provisional phases.
- [Detailed remaining work](docs/REMAINING_WORK.md): Phase 3/4 tasks, dependencies, deliverables and exit criteria.
- [Phase 1 summary](docs/PHASE1_SUMMARY.md): exit audit, results and open evidence gate.
- [Phase 2 summary](docs/PHASE2_SUMMARY.md): live SNN controls, 50-variable pilot and limits.
- [Phase 3 status](docs/PHASE3_STATUS.md): synthetic benchmark, provisional UiO-66 fit, completed DFT baseline and open validation gates.
- [Dataset decision](docs/dataset_decision.md): external DAC sources, recommendation and required target choice.
- [ODAC25 target contract](docs/ODAC25_TARGET_CONTRACT.md): paired CO2/H2O energy target and evidence rules.
- [Kaggle runbook](docs/ODAC25_KAGGLE_RUNBOOK.md): secret-safe ODAC25 inventory and UMA smoke workflow.

## Run locally (PowerShell, repository root)

```powershell
cd C:\Users\hp\Documents\GitHub\MOF_for_DAC_Opt
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m mof_dac --output results/demo.json
```

If NumPy, SciPy and pytest already exist in your interpreter, the last two commands
can be run directly as `python -m pytest -q` and `python -m mof_dac` without installation.
The foundation was verified this way on Python 3.14. Core supports Python 3.10+;
upstream SNN dependency/platform compatibility must be checked separately. For
Phase 2, prefer a supported Python 3.12/3.13 environment per the upstream wheel documentation.

Custom graph:

```powershell
python -m mof_dac --instance data/synthetic/toy.json --seed 7 --output results/seed7.json
```

This command intentionally limits n to 20 because it runs exhaustive reference and
distance decoding. It will not silently enumerate a proposed 50-variable instance.
Default output path is overwritten on rerun; use distinct names for experiments.

## Execution and architecture

```text
data/synthetic/toy.json    nodes + undirected edges + explicit linear constraints
        |
mof_dac/data.py           validate IDs, provenance, numeric values, units
        |
mof_dac/formulation.py    h,W,E,e,U,u; energy, residuals, binary Q, SNN arrays
        |
mof_dac/optimizers.py     seeded SA + SLSQP control + tiny oracle/distance repair
        |
mof_dac/__main__.py       evaluate raw/rounded/repaired output; save run manifest

mof_dac/snn.py            separate optional convex-only upstream adapter
mof_dac/materials.py      external structure/label manifest validation
tests/test_foundation.py  independent mathematical and failure-path checks
```

Arrays are float64. `h[n]`, `W[n,n]`, `E[me,n]`, `e[me]`, `U[mu,n]`, `u[mu]`.
Objective: `h @ x + 0.5 * x @ W @ x`. Explicit constraints: `E@x=e`, `U@x<=u`,
`0<=x<=1`. Binary QUBO export is `diag(h)+W/2`; using it directly as a fractional
quadratic changes the linear term. Dense matrices suit this initial scale; sparse
storage should be added only after profiling larger instances.

The [Graphify knowledge graph](graphify-out/graph.html) is a historical **5 October**
source/document snapshot. Its generated nodes do not cover the later DFT and
convergence work. Use the [current navigation supplement](graphify-out/CURRENT_STATUS.md)
for those records and the [freshness guide](docs/knowledge_graph.md) before relying
on a graph result. It is separate from the numerical interaction graph in the fixture.

Phase 1 completed its synthetic-first scope with a [formulation contract](docs/phase1_formulation.md):
fixed-template slot choices, occupancy/budget/charge rules, and a worked example.
Chemistry assumptions remain proposed pending review.

## What the demonstration proves

Fixture: 6 variables, 64 binary states, 10 feasible states; unique minimum
`[1,0,1,1,0,0]`, selecting M0, L0 and L1, with H=-4.6. Toy charge balance
and linker budget force two linkers. No actual chemical identity is attached to these IDs.

Run JSON includes input SHA256, environment/version details, settings, spectrum,
raw residuals, timings, oracle, and separate relaxed/rounded/repaired outputs.
SA is an initial feasible-move implementation, not a fully tuned publication baseline.
SLSQP is a local control, not a neuromorphic solver. Enumeration only certifies the
tiny model. Repair optimizes distance rather than energy and is separately timed.

## SNN and benchmark status

`Problem.snn_arrays()` exports `A=W`, `b=h`, and rows for `C@x+d<=0`, including
equalities and bounds. `solve_convex_control` calls optional `snn_opt` only when
the full-space Hessian passes a PSD check. The separate nonconvex entry point sends
raw W with no diagonal shift and labels every run experimental. `snn-opt==0.6.0`
has been executed; see the Phase 2 summary. Optional install:
`python -m pip install -e ".[snn]"`.

Gurobi 13.0.3, constraint-aware SA and decoded SNN have been run on 60 frozen
held-out synthetic instances at 12, 20 and 50 bits; see the Phase 3 status.
The ODAC25 paired validation target is frozen; compatible training/reference
data, target-compatible model checkpoints and the shared-pool material comparison
remain open. The separate UiO-66 design fit and DFT snapshot diagnostics do not
complete that benchmark. Independent chemistry and numerical validation remain.

Source PDFs/screenshots are archived locally under `sources/` and ignored by Git;
text extraction, summaries and hashes remain reviewable. Generated results and raw
datasets are generally ignored; consult each evidence guide for tracked review
payloads and machine-local checkpoints. A repository commit does not by itself
publish every raw calculation artifact. This documentation refresh runs no calculation.
