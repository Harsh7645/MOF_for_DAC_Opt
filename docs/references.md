# Sources, review evidence and literature queue

Checked 2026-09-10. The completed scoped comparison is in
[`phase1_literature.md`](phase1_literature.md). It remains a living review, not
proof of novelty.

## Supplied primary project sources

- `sources/scoping_report.pdf`: local copy of the four-page proposal. p.1 scope
  and material target; p.2 H, relaxation and h/J definitions; p.3 named baselines
  and first half of timetable; p.4 remaining timetable and manuscript goal.
- `sources/scoping_report_extracted.txt`: full text extraction; original page
  renderings were visually checked during initialization.
- `sources/professor_feedback_1.png`, `sources/professor_feedback_2.png`: local
  screenshot copies. Summary: `sources/professor_feedback.md`.
- `sources/manifest.json`: SHA256 hashes and original local source paths.

## External primary references

1. [Lucas, Ising formulations of many NP problems (2014)](https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2014.00005/full),
   DOI 10.3389/fphy.2014.00005; [arXiv](https://arxiv.org/abs/1302.5843).
   Relevant derivations and applicability limits are recorded in
   `phase1_formulation.md` and `phase1_literature.md`.
2. [Mancoo, Keemink and Machens, Understanding spiking networks through convex optimization (NeurIPS 2020)](https://proceedings.neurips.cc/paper_files/paper/2020/hash/64714a86909d401f8feb83e8c2d94b23-Abstract.html).
   Abstract checked. Establishes the relevant convex-optimization framing;
   theorem assumptions must be studied before any extension claim.
3. [Lab SNN_opt repository](https://github.com/ahkhan03/SNN_opt).
   README read; API docs and equality example reviewed at commit
   `f6623472204b2b5b7955c98e91024a391cf96fff`; theory excerpts reviewed,
   not a full source audit. Objective `0.5*x.T@A@x+b.T@x`, inequalities
   `C@x+d<=0`, documented PSD Hessian. Source conventions guide `mof_dac/snn.py`.
   [Pinned API](https://github.com/ahkhan03/SNN_opt/blob/f6623472204b2b5b7955c98e91024a391cf96fff/docs/api.md),
   [pinned equality example](https://github.com/ahkhan03/SNN_opt/blob/f6623472204b2b5b7955c98e91024a391cf96fff/examples/example6_equality_constraint.py).
4. [Lab companion quickstart](https://snn.ahkhan.me/tutorials/quickstart/).
   Checked install/runtime and result conventions. Note its example comment
   says x0=[1,1] is feasible for x1+2*x2<=1, which is arithmetically false;
   do not copy that assertion. Independently evaluate all residuals.
5. [CoRE MOF 2019 dataset paper](https://pubs.acs.org/doi/10.1021/acs.jced.9b00835).
   Source description supports its role as computation-ready experimental
   structures, not a universal per-block interaction table. Dataset version
   and actual DAC property coverage remain to be selected and verified.
6. [MOFTransformer official repository](https://github.com/hspark1212/MOFTransformer)
   and [tutorial](https://hspark1212.github.io/MOFTransformer/tutorial.html).
   Candidate transfer-learning screening baseline from the report. No checkpoint
   installed, trained or validated here.
7. [CGCNN official repository](https://github.com/txie-93/cgcnn).
   Named report baseline; detailed implementation/data suitability review pending.

## Continuing literature scout

The Phase 1 scoped search covered quantum annealing / QUBO / Ising MOF design and
adsorption optimization. Continue backward/forward citation updates before publication.
For each primary paper record DOI, year, material family, variables, objective,
constraints, coefficient origin, solver/hardware, size, baselines, chemical
validation, code/data availability and overlap with this project's proposed claim.
Separate optimization of material composition from screening already enumerated
structures and from process optimization. Do not infer novelty from different
solver branding. No claim of comprehensive coverage is made by this source register.

## Integration audit next

- Reproduce an upstream convex example with pinned software and known optimum.
- Inspect actual PSD checks, step selection, joint feasibility and equality
  handling in source, then design a separately labeled nonconvex experiment.
- Verify convergence/feasibility tolerances against our 1e-7 scoring tolerance;
  upstream stopping flags cannot replace project-level residual checks.
- Review upstream versions and dependency compatibility before freezing a
  publication environment. The optional 0.6.0 dependency is not asserted to be
  byte-identical to the reviewed main-branch commit.
