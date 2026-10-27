# Phase 3 closure checklist — revised methods scope, 27 October 2026

**Status: incomplete; local preparation complete, independent review gates open.**
Working title: *Separating Optimization Performance from Target Reliability in
a Discrete MOF Design Workflow.* See [scope revision](RESEARCH_SCOPE_REVISION_20261027.md).

## Passed local requirements

- [x] Original roadmap preserved; completed/failed/deferred original objectives
  distinguished from revised deliverables. No deferred benchmark marked complete.
- [x] Central evidence package: six CSV/Markdown tables, seven PNG/SVG figure
  pairs, saved input snapshots and offline formatting command with hashes.
- [x] Actual synthetic budgets, raw/decoded feasibility and six-bit objective
  comparison retained separately from sampled-target errors.
- [x] Historical 51/13 exposure, development-only resampling, pairwise MAE pattern
  **and RMSE exception**, coefficient/ranking/identifiability limits retained.
- [x] Sampling/relaxation failures remain results; no uncertainty calibration,
  error-dominance, SNN-superiority or reliable-ranking assertion.
- [x] Structural record consolidates provenance, composition, four node OH,
  charge/spin and amino/rotamer/contact assumptions; unanswered questions explicit.
- [x] Future Sc/Sh/Sg and all-atom force rules confirmed; successive and direct
  baseline comparisons retained with refined-convergence/baseline-drift distinction.
- [x] Methods/results foundation and claim-to-evidence ledger prepared; unsupported
  novelty claims excluded. DFT baseline is supplementary only.

## Required independent scientific review — not passed

- [ ] Qualified chemistry assessment of the ideal model, proton/source mapping,
  amino choices and observed configurations. Document answers, limitations and
  any demonstrable inconsistency; resolve findings blocking the limited case study.
- [ ] Independent final review of the central claims, methods, budgets, statistics,
  scope and reproduction package. Record reviewer/date/hash/findings/disposition.
- [ ] Incorporate both reviews and document closure of blocking findings. Only
  then decide whether revised Phase 3 criteria pass. Do not infer approval.

Use [review_status.json](../plans/phase3-methods-scope-v1/review_status.json),
currently explicit null/pending fields. No review request has been sent.

## Remaining concrete local tasks

After reviewer feedback: apply required corrections in a new documented revision,
update the claim ledger and package receipt, then reassess the closure gates.
There is no known additional Windows calculation needed to assemble the current
central evidence. Literature positioning/citation verification and manuscript
polish remain Phase 4 work; scientific corrections may return work to Phase 3.

## Deferred extensions — not completed, not closure dependencies

- ODAC25 parent identity/reference compatibility, missing EPONEE frame, training
  export, leakage-safe fits and benchmark. Original138 frozen; request unsent;
  investigation paused pending source-side response/user instruction.
- DFT cutoff/grid/SCF/k-point refinement and quantitative validation; larger-memory
  environment/allocation. Existing14 baseline SCFs are complete but not fully
  numerically converged in this sense. No central DFT quantitative claim.
- Four missing UMA host single points, expanded sampling/rotamer search and
  physical/material ranking/top-K validation.
- Neuromorphic hardware speed/energy comparisons and general solver superiority.

## Phase 4 under revised scope

1. Integrate documented independent/chemistry review and finish authors' wording.
2. Verify primary citations and novelty/related-work positioning; avoid first-of-kind claims without evidence.
3. Finalize manuscript, central figures/tables, supplementary model record and
   clearly labeled exploratory DFT appendix; no mixed-unit error-budget argument.
4. Prepare archival reproduction/data/software-license documentation and a
   clean-environment packaging check as needed. Obtain author approval before
   publication, release or submission; none is authorized by this task.

Local validation: [scope package receipt](../plans/phase3-methods-scope-v1/scope_receipt.json).
No fit, solver search, QE/UMA calculation or historical audit was rerun.
