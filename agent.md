REVIEW RESPONSE v2 - 2026-10-27; no new scientific calculations or fits.
Read docs/PHASE3_REVIEW_RESPONSE_V2.md, docs/PHASE3_SCIENTIFIC_CLARIFICATIONS_V2.md,
docs/MANUSCRIPT_METHODS_RESULTS_V2.md and docs/CHEMISTRY_INSPECTION_REVIEW_V2.md.
Updated checklist: docs/PHASE3_CLOSURE_CHECKLIST_V2.md. Fixed review package:
plans/phase3-review-response-v2/README.md (snapshot.zip and checksum receipt).
Exact decoder/tolerances, bootstrap endpoints/23 exclusions/977 conditional fits,
eight-pattern seeds/gas-specific failures and periodic loading limitations documented.
Five exact checkpoints + parent/CIF;749 coordinate rows;20 OH environments;stable image labels.
Four targeted checks pass; v1 scope and historical scientific evidence unchanged.
PHASE 3 INCOMPLETE: Q1 source/proton correspondence and Q2 geometry adequacy OPEN;
qualified chemistry assessment and independent final review still required.
User-communicated findings have no supplied signed reviewer identity/qualification;
AI response is NOT human approval. No demonstrated blocker is NOT a passed gate.
Keep fixed snapshot immutable; record later responses separately with its hash.
ODAC25 deferred/paused/UNSENT; DFT supplementary; no contact/compute authorized.

CURRENT SCOPE REVISION - 2026-10-27; supersedes older completion gates below.
Title: Separating Optimization Performance from Target Reliability in a Discrete MOF Design Workflow.
Read docs/RESEARCH_SCOPE_REVISION_20261027.md, docs/PHASE3_CLOSURE_CHECKLIST_V1.md,
docs/MANUSCRIPT_METHODS_RESULTS_V1.md and plans/phase3-methods-scope-v1/EVIDENCE_INDEX.md.
Local preparation: six tables, seven figure pairs, saved snapshots, claim ledger and structural record.
Reformat only: no new solver runs, fits, QE/UMA or unchanged scientific audits.
PHASE 3 INCOMPLETE: qualified chemistry assessment AND independent final review pending;
record reviewer/date/evidence hashes/findings/disposition; no inferred approval.
ODAC25 formally DEFERRED extension; investigation PAUSED; request UNSENT; frozen138 intact.
14 DFT baselines supplementary only; higher-memory access/refinement NOT a limited-scope closure dependency.
Sc/Sh/Sg each2.0meV where applicable; test Sg directly; all-atom max vector force change0.005eV/A.
Both successive and direct-original-baseline comparisons required. Baseline drift does not preclude
later refined convergence. See docs/FUTURE_CONVERGENCE_RULES_V3.md; old sealed rules preserved.
Additive descriptive only; pairwise RMSE exception, exposed13, rank failures and sampling limits retained.
No SNN advantage, calibrated uncertainty, chemical approval or reliable material ranking.
Phase4: review integration, citation/novelty checks, manuscript/supplement, archive and author approval.
No computation, contacts or publication authorized. Older entries below are historical.

# Repository agent instructions

These are persistent project instructions, subordinate to runtime system/developer rules and current user direction. They do not replace an assistant's system prompt. Root `AGENTS.md` routes agents here.

## Resume protocol

1. Read `context.md`, `chat_context.md`, `.planning/ROADMAP.md` and `.planning/STATE.md`.
2. Check current Git status; preserve user edits. Read relevant source and tests before editing.
   For codebase questions, query `graphify-out/graph.json` through `graphify query`
   with a 1200-1500 token budget first; follow source pointers for details. Check
   freshness and refresh changed documents semantically. See `docs/knowledge_graph.md`.
   Graphify 0.9.54 budgets are advisory, not hard limits. Prefer `graphify explain`
   for known symbols; narrow to exact nodes when BFS output expands beyond budget.
3. Work in this repository. Keep four phases unless the user agrees to change them. Complete a runnable numerical loop before introducing new frameworks.
4. Update state with exact commands/results, decisions, failures and next work. Never imply cross-session memory exists beyond files.

## Research invariants

- Professor's four corrections govern: nonconvex honesty; explicit selection constraints; synthetic-first then chemistry-grounded parameters; quality-first benchmarks with no presumed CPU speed win.
- Canonical objective `h@x + 0.5*x@W@x`; symmetric zero-diagonal `W`. Binary QUBO `diag(h)+W/2`. Preserve factor-of-two and fractional-domain distinctions.
- Validate dimensions, finite values, IDs, duplicate unordered edges, input provenance and constraint senses. Never replace missing measurements with silent zeros.
- Record per-instance spectrum; never infer curvature just from signs. No concealed PSD shift, penalty, scaling or objective change.
- Explicitly label numerical surrogate validity, binary feasibility and chemical validity separately. No optimizer output proves synthesis feasibility, selectivity, uptake, regeneration cost or stability.
- CoRE contains assembled structures and associated data, not a ready-made per-block h/J table. Synthetic fixtures must say synthetic. Every real coefficient needs source, derivation, units and uncertainty/validation plan.
- Hard rules belong in constraints. A large positive pair coefficient is a soft cost. Validate post-threshold and post-repair feasibility independently.
- Never present a SciPy control as an SNN. Never hide exact optimization in decoding and attribute its result to the heuristic. Charge repair time to the method and report before/after scores.
- Nonconvex SNN behavior is experimental, not guaranteed to find even a local minimum. Convex-only upstream APIs must not silently receive indefinite Hessians.
- Do not claim literature novelty, CPU dominance or neuromorphic energy savings without evidence.

## Required baselines

| Method from report p.3 | Role | Evidence required |
|---|---|---|
| Simulated Annealing (SA) | Classical heuristic; TTS comparison | Identical objective and constraints, declared moves or penalty/slack formulation, seed set, schedule, restart budget, feasibility and success distribution. |
| Gurobi Optimizer | Certified small-instance reference | Version/license availability, original constrained binary model, status, incumbent, best bound, MIP gap, seed/threads/time limit. Never equate timeout with exactness. |
| Surrogate screening: MOFTransformer or CGCNN | Primary competitive material-ranking baseline | Actual assembled structures and target labels, checkpoint/data provenance, train/validation/test separation, fixed candidate pool and K, inference and preprocessing cost, top-K independent validation. |

Enumeration is a tiny-instance oracle. SLSQP is a development relaxation control. Neither replaces the required methods. Final surrogate choice remains provisional; the report says "such as" and does not require both models.

## Metrics and fair comparisons

- Primary: feasible energy, constraint violation, feasible-run fraction, absolute/relative optimality gap, exact optimum hit rate across seeds. Define tolerance; count degenerate optimal states fairly.
- Recovery: known-good MOF recall/top-K quality only where representation and independent labels make comparison meaningful. No synthetic bit-string result labeled a recovered CoRE structure.
- Secondary: measured wall time, preprocessing, solve and decoding/repair times, TTS with defined energy target and success confidence. Log CPU/GPU/backend/thread count and environment. Failed runs stay in denominators.
- Record raw fractional states, thresholded states and repaired states separately. No energy gap for infeasible output. No global certificate from a local QP termination flag.
- Keep training/tuning out of held-out test sets. Compare both search quality under shared H and physical-property ranking separately; these are different tasks.

## Engineering protocol

- Dense, concise communication; detailed teaching documentation remains readable.
- Graphify is the persistent code/document retrieval index. Do not claim it contains
  every detail or replaces source verification. Preserve proposed-vs-approved status.
- Graph records for blocks/interactions, arrays for numerical kernels. Declare dimensions in docstrings. NumPy/SciPy now match the upstream solver; use PyTorch when a real ML or GPU workload needs it.
- Small modules with clear responsibilities; no routing framework, service layer or speculative abstractions. Use stdlib before dependencies.
- Read `C:/Users/hp/.codex/RTK.md` before RTK use. Prefer `C:/Users/hp/.local/bin/rtk.exe` for supported commands when useful; keep native PowerShell and raw diagnostic evidence when needed.
- Test mathematical equivalence, constraints, failure reporting and reproducibility. Run `python -m pytest -q` and `python -m mof_dac --output results/demo.json` after relevant changes.
- Do not commit private source PDFs/screenshots or generated datasets by accident; local source files are ignored. Do not push, message the professor or publish research claims without user authorization.
- Accept Hugging Face credentials only from the `HF_TOKEN` environment variable or
  Kaggle Secrets. Never request, print, store, or commit the token. Treat gated
  dataset/model access as available only after non-secret inventory, schema, and
  smoke-test artifacts have been captured.
