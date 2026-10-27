# Review response v2 — 27 October 2026

The findings below were supplied in the user's current chat instruction. No
separately signed review, reviewer identity/qualification, original assessment
date or authenticated human approval was supplied with it. Attribution remains
**user-communicated findings; original reviewer provenance unverified**. This
response, manuscript revision and computational checks are AI-assisted project
work, not independent human scientific or qualified chemistry approval.
See [provenance](../plans/phase3-review-response-v2/reviewer_provenance.json).

“Addressed” means a documented implementation clarification or package correction;
it does not mean a reviewer accepted the response. Historical scope-v1 materials,
scientific records and failed criteria remain unchanged.

|ID / supplied finding|Exact documented change|Supporting artifact|Remaining status|
|---|---|---|---|
|R1 — SNN decoding and tolerances|Explain descending x_B−x_A, fixed k=3/5/12, stable lower-slot ties, nearest-distance interpretation and absence of H optimization. Separate six-bit ≥0.5 threshold. State 1e-7 feasibility and 1e-8 objective-hit tolerances; distinguish reference assertion's relative tolerance.|[Clarifications §1](PHASE3_SCIENTIFIC_CLARIFICATIONS_V2.md), [decoder](../mof_dac/instances.py), [feasibility](../mof_dac/formulation.py), [benchmark](../mof_dac/phase3.py)|Addressed in manuscript v2; independent acceptance pending.|
|R2 — bootstrap endpoints and exclusions|Report coefficient 2.5/50/97.5 percentiles versus rank/overlap/correlation 5/50/95. Retain all 1,000 draws; list 23 pairwise failures, all affected summaries and denominator 977. Additive denominator 1,000; historical 200-draw analysis separate.|[Clarifications §2](PHASE3_SCIENTIFIC_CLARIFICATIONS_V2.md), [draw status](../plans/phase3-review-response-v2/inspection/bootstrap_draw_status.csv), [endpoints](../plans/phase3-review-response-v2/inspection/coefficient_endpoints.csv), [analysis source](../scripts/analyze_uio66_development.py)|Addressed; ranges remain conditional diagnostics, not physical bounds.|
|R3 — eight-design selection and batches|Record all eight preselected patterns/reasons/historical roles, per-gas quotas, SeedSequence indices and 512 streams. Explain proposal conditioning and shared model. Preserve gas-specific results, lost attempt and failed energy/rank/force gates.|[Clarifications §3](PHASE3_SCIENTIFIC_CLARIFICATIONS_V2.md), [selection](../plans/phase3-review-response-v2/inspection/pilot_selection.csv), [streams](../plans/phase3-review-response-v2/inspection/pilot_seed_streams.csv), [frozen poses](../data/design/uio66_sampling_pilot_v2.json), [saved assessment](../plans/phase3-methods-scope-v1/evidence/inputs/pilot.json)|Addressed descriptively; target reliability remains unresolved.|
|R4 — terminology, loading and limitations|Use “64 encoded ordered patterns.” Exclude exhaustive regioisomers/rotamers, symmetry uniqueness, accessibility, validated ranking and general superiority. State one molecule per periodic primitive cell and untested loading/image/humid-air effects. Preserve exposed 13, unequal budgets and RMSE exception.|[Manuscript v2](MANUSCRIPT_METHODS_RESULTS_V2.md), [clarifications §4](PHASE3_SCIENTIFIC_CLARIFICATIONS_V2.md)|Addressed in current draft; no new physical claim.|
|R5 — inspection evidence beyond screenshots|Copy five exact original checkpoints, parent and source CIF; provide full-precision coordinates/cells, stable labels/image translations, OH vectors, copied coordination/amino/crowding/contact descriptors and before/after views.|[Inspection guide](CHEMISTRY_INSPECTION_REVIEW_V2.md), [source records](../plans/phase3-review-response-v2/inspection/source_geometries.json), [coordinates](../plans/phase3-review-response-v2/inspection/coordinates.csv)|Packet prepared and checked; distances/images do not establish chemistry.|
|Q1 — source/proton correspondence|Distinguish source CIF from explicitly defined ideal model; list exact four OH identities/orientations and qualified-review question. No proton repair or inferred identity.|[Q1](CHEMISTRY_INSPECTION_REVIEW_V2.md), [publication comparison](../plans/phase3-review-response-v2/inspection/source_publication_comparison.json)|**OPEN — qualified human assessment required.**|
|Q2 — ideal-model geometry/chemical adequacy|Present water-28/CO2-7 checkpoints, carboxylates, amino and periodic contacts; ask whether a specific geometry/proton/coordination/charge issue blocks interpretation.|[Q2](CHEMISTRY_INSPECTION_REVIEW_V2.md), [exact structures](../plans/phase3-review-response-v2/inspection/exact)|**OPEN — qualified human assessment required.**|
|R6 — fixed snapshot/provenance/reproduction|Versioned allowlisted snapshot with source revision and dirty-source hashes; SHA256 manifest/ZIP receipt; no credentials, machine launch state or new execution authorization. Separate figure replay from historical scientific execution; later responses outside snapshot.|[Snapshot guide](../plans/phase3-review-response-v2/README.md), [evidence index](../plans/phase3-review-response-v2/EVIDENCE_INDEX.md), [review status](../plans/phase3-review-response-v2/review_status.json)|Prepared for review, not reviewer acceptance. No overwrite after sealing.|
|R7 — closure rules and revised scope|Independent final review and qualified answers to Q1/Q2 remain mandatory. Absence of a demonstrated blocker does not close either gate. ODAC25 deferred/paused/unsent; DFT supplementary only.|[Closure checklist v2](PHASE3_CLOSURE_CHECKLIST_V2.md)|**Phase 3 incomplete.** No new calculations, fits, contact or scope expansion.|

Additional implementation clarification discovered while formatting inspection:
the archived carboxylate O–Zr contact list extends to 3.5 A, although its
coordination-count cutoff is 2.8 A. The inspection guide explicitly distinguishes
the list from counted coordination; archived descriptors were not silently changed.
No new scientific inconsistency or chemical approval is inferred from that correction.
