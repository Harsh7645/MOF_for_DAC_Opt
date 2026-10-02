# Retrieval checks

Graphify 0.9.54, 2026-09-10. Successful local commands:

```powershell
graphify query "repair rounding" --budget 1200
graphify query "slot charge phase" --budget 1500
graphify explain "Charge Audit and Equality Rank"
```

The first query located `repair_nearest()` at `mof_dac/optimizers.py:L47`, its
distance-decoding documentation, callers and tests. The second found the slot
contract and charge/equality-rank discussion in `docs/phase1_formulation.md`.
The focused explain returned one concept and three neighbors with source evidence.

Budget limitation: the second query reported approximately 3238 tokens despite
requesting 1500. The tool preserves all edges once nodes fit. Even `--context call`
did not enforce a hard cap in a follow-up check. Prefer exact-node/explain queries
for known concepts and use source pointers for the small amount of detail needed.
Do not dump the full graph into chat to save tokens.

Graphify's benchmark initially estimated 4.0x reduction (10133 naive tokens vs
2533 per sample query); this is a built-in retrieval-size heuristic, not actual
agent/session token accounting. Its estimated 7600-word corpus differs from the
detector's full file word count. No model billing or realized savings claim follows.

Core navigation hubs: `Problem`, `load_instance()`, `run()`, `repair_nearest()`.
Useful cross-document link: charge audit and equality rank connect the proposed
slot formulation to SLSQP's current limitations. Proposed does not mean approved.
