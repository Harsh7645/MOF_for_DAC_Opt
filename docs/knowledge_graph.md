# Persistent Graphify knowledge graph

The codebase interaction fixture and the project knowledge graph are different.
`data/synthetic/toy.json` models optimization choices. `graphify-out/graph.json`
indexes code symbols, documentation concepts, dependencies and research decisions.

Outputs: `graphify-out/graph.html` (interactive), `graphify-out/graph.json`
(queryable data), `graphify-out/GRAPH_REPORT.md` (communities and audit), plus
`graphify-out/BUILD_AUDIT.json` (coverage, integrity and token-accounting limits).

## Read efficiently

From the project root:

```powershell
graphify query "Problem energy binary_qubo snn_arrays" --budget 1200
graphify query "repair_nearest rounding feasibility" --budget 1200
graphify query "slot occupancy charge balance Phase 1" --budget 1500
graphify explain "Problem"
```

Graphify 0.9.54's `--budget` is advisory: a tested 1500-token query reported
about 3238 tokens because it retained all edges once the nodes fit. For a known
symbol/concept, prefer `graphify explain "Charge Audit and Equality Rank"` or
an exact node lookup; broad BFS is not a hard token cap. The HTML visualization
loads vis-network from a CDN and therefore needs network access on first load.

Use vocabulary from graph labels if a natural-language query returns no hits.
Read cited source locations only as needed; never load the full graph JSON into
chat merely to answer a small question. The graph is a retrieval index, not a
complete substitute for source code, tests or original papers. Semantic edges
carry extracted/inferred/ambiguous confidence, not proof that a scientific claim
is true. Proposed model decisions remain proposed even when indexed.

## Freshness and updates

`graphify update .` refreshes code structure, and may flag changed documents for
semantic extraction. It is not evidence that all document changes were understood.
Use the Graphify skill for a full or incremental semantic refresh after research
documents change. Preserve source provenance and check `BUILD_AUDIT.json`/manifest
against changed files. Do not answer from known-stale nodes without inspecting
their source. Generated outputs, caches, binaries, raw datasets and duplicate
PDF/image originals are excluded; extracted report text and feedback summary are
indexed. This bounds cost while retaining accessible source pointers.

Installed tool: Graphify (`graphifyy`) in its existing uv tool environment,
independent of this project's NumPy/SciPy runtime. Tool paths are machine-local.
No API keys are required for local AST extraction and agent semantic extraction.
Agent token use is not precisely exposed; unknown counts must not be described
as zero-cost extraction or measured token savings.
