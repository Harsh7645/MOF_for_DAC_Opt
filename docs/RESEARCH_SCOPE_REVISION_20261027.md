# Research scope revision v1 — 27 October 2026

**Authority:** reviewer recommendation communicated and instructed by the user
on 27 October 2026. This changes deliverables, not historical outcomes. It is
not the independent final scientific review or chemistry assessment required
for Phase 3 closure.

**Research question:** “How should discrete optimization, surrogate adequacy and
adsorption-target reliability be assessed separately before interpreting an
optimized MOF design physically?”

**Working title:** “Separating Optimization Performance from Target Reliability
in a Discrete MOF Design Workflow.”

## Rationale and scope boundary

The saved evidence demonstrates numerical solver behavior, limited surrogate
adequacy, and sampling/relaxation sensitivity. It does not establish reliable
physical rankings, general UMA accuracy or SNN superiority. The original goal
of a validated materials-screening pipeline would require evidence not yet
available. The revised methods study reports these distinctions and negative
findings explicitly instead of presenting incomplete validation as success.

The original roadmap is retained byte-for-byte in
[ROADMAP_pre_scope_20261027.md](../.planning/ROADMAP_pre_scope_20261027.md), with
its hash in the revision receipt. Current roadmap guidance is a new prefix;
all earlier entries and the original relative schedule remain historical.

|Original objective|Actual disposition|Revised role|
|---|---|---|
|Phase 1 formulation, constraints and synthetic recovery|Completed for controlled computational scope; chemistry never certified|Methods foundation|
|Phase 2 convex control and experimental nonconvex SNN integration|Completed integration; convex guarantee does not cover indefinite experiments|Explicit algorithm/theory boundary|
|Synthetic held-out solver comparison|Completed under recorded unequal budgets|Central numerical-objective evidence|
|64-design UMA generation, fit and fitted-objective solver comparison|Execution completed; pairwise did not provide robust MAE improvement|Central provisional ordered-model case; negative results retained|
|Sampling/relaxation stability|Experiments completed; registered sampling gate failed, several tight paths remain sensitive|Central reliability diagnostic; **original stable-target objective not completed**|
|ODAC25 paired-target benchmark and real training|Extraction/provenance investigation completed; identity/reference/training gates unresolved|**Deferred separate extension**, not a completed benchmark; frozen 138 and unsent request preserved|
|Independent physical validation/material rankings/top-K candidates|Not established|**Deferred**, no reliable-ranking or DAC-performance claims|
|Fourteen frozen DFT baseline single points|Baseline execution completed; cutoff/grid/k-point convergence unresolved|Exploratory supplementary evidence only; no central quantitative inference|
|Further DFT convergence and four missing UMA host points|Not completed|**Deferred extensions**; larger-memory access is not a dependency of this limited scope|
|Original Phase 4 analysis/manuscript|Some analysis now completed; manuscript foundation prepared in revised scope|Final review, literature positioning and publication/reproducibility preparation remain|

## Revised Phase 3 completion criteria

1. Frozen evidence separates synthetic numerical objectives, sampled UMA labels,
   regression adequacy and target reliability; actual budgets/feasibility/decoding
   are visible. No cross-regime ratio or dominance claim.
2. The original 51/13 split and historical fits remain unchanged. Exposed13 are
   historical evaluation; all exploratory resampling uses only 51 development
   designs, grouping duplicates and retaining rank failures. Both MAE and the
   reported pairwise RMSE exception remain visible.
3. Figures/tables regenerate offline from pinned saved artifacts; claims have
   source pointers, scopes and limitations. No additional solver run or fit is
   needed merely to reformat evidence.
4. Structural model record gives provenance, composition/four node hydroxyls,
   explicit construction assumptions and unresolved chemistry. A **qualified
   chemistry assessment must be documented**, including required corrections
   or explicit limits for using ideal ordered models. No inferred approval.
5. Methods/results draft explains a transferable assessment procedure and
   distinguishes demonstrated contributions from unverified novelty claims.
6. Future numerical rules are recorded as confirmed, without launching jobs.
   baseline DFT remains supplementary; no cutoff-unconverged quantity is central.
7. **Independent final scientific review is documented**, identifies reviewer,
   date, reviewed hashes, findings and disposition. Self-checks, user approval of
   this scope and automated tests do not satisfy this gate. Unresolved blocking
   findings prevent completion.

Criteria1–3,5–6 can be checked locally. Criteria4 and 7 remain external scientific
gates. Phase 3 is **not complete** until both are documented and blocking findings
are resolved. Numerical instability may remain an explicit result; passing a
physical-ranking gate is not required for the limited methods scope.

## Deferred-work preservation

ODAC25 remains paused/unsent per [its unchanged status](ODAC25_REQUEST_STATUS.json).
No benchmark scores are reported; no record is replaced or re-paired. Existing
identity/reference findings, original 138 selection and source request remain
available for a separately scoped extension. No contact is authorized.

baseline DFT is supplemental exploratory baseline evidence. The 14 calculations and
historical protocols remain immutable. New convergence/inference/expansion work
requires a separate scope and execution authorization. Historical approval flags
are not authorization. See [confirmed future rules](FUTURE_CONVERGENCE_RULES_V3.md).

## Revised Phase 4

- Incorporate the required independent/chemistry reviews and resolve findings.
- Verify literature citations and compare the demonstrated procedure with prior
  work before making any novelty claim; this is scholarly positioning, not an
  assertion that the workflow is the first of its kind.
- Finalize manuscript, captions, supplementary model/provenance records and
  explicit exclusions; choose a venue and author-approved scope.
- Prepare the shareable reproduction archive, environment/software/license and
  data-access documentation; perform a clean-environment packaging check if needed.
- Author approval of submission/release is separate. No submission or messaging
  is authorized here. Physical optimization and hardware studies stay extensions.
