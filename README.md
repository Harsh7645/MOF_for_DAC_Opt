# MOF for DAC optimization

Research foundation for constrained building-block selection using a pseudo-energy
Hamiltonian and SNN-QP integration. Target material family: amine-functionalized
zirconium MOFs / UiO-66 derivatives. Synthetic optimizer evidence and real ODAC25
validation targets exist; **no material discovery is claimed.**

## Start here

- [Beginner guide](beginner_guide.md): chemistry translated into graphs and optimization.
- [Project memory](context.md): source-derived math, four phases, decisions and open questions.
- [Agent instructions](agent.md): persistent research and benchmark requirements.
- [Chat handoff](chat_context.md): completed work, verification and next step.
- [Roadmap](.planning/ROADMAP.md): four provisional phases.
- [Detailed remaining work](docs/REMAINING_WORK.md): Phase 3/4 tasks, dependencies, deliverables and exit criteria.
- [Phase 1 summary](docs/PHASE1_SUMMARY.md): exit audit, results and open evidence gate.
- [Phase 2 summary](docs/PHASE2_SUMMARY.md): live SNN controls, 50-variable pilot and limits.
- [Phase 3 status](docs/PHASE3_STATUS.md): frozen numerical benchmark and material-data gate.
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

The [Graphify knowledge graph](graphify-out/graph.html) indexes source and research
documents. [Query and refresh instructions](docs/knowledge_graph.md) keep future
lookups focused. It is separate from the numerical interaction graph in the fixture.

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
MOFTransformer/CGCNN or a current DAC model still requires assembled structures,
a fixed target, access to validated checkpoints and a shared candidate pool. The
paired ODAC25 validation target is frozen and its authenticated artifacts are
verified. Predictive material baselines and independent chemistry validation remain.

Source PDFs/screenshots are archived locally under `sources/` and ignored by Git;
text extraction, summaries and hashes remain reviewable. Generated results and raw
datasets are ignored. No commit, remote push or external message was made.
