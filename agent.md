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
