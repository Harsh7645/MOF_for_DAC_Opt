# Structural model record v1 — ideal ordered UiO-66 models

27 October 2026. Consolidation of existing computational evidence, **not chemical
approval**. Coordinates, proton positions, fits and historical results unchanged.
The 64 bit patterns are ideal ordered computational models, not 64 experimentally
established materials or exhaustive positional/rotamer/symmetry variants.

## Provenance and verified observations

|Topic|Saved computational observation|Remaining chemical limitation|
|---|---|---|
|Parent|`jz4002345_si_002`, original bare-shard SHA256 `9b1025cf1b5b4dd65e6c6a237458a6b736f261876498fc19b7a0c9cd5c585f83`, index 184693/fid 7; exported arrays match the library parent exactly.|This establishes export-to-library provenance, not experimentally correct coordinates/protons. Parent is a guest-removed/re-relaxed trajectory-derived frame.|
|Publication comparison|Original SI CIF SHA256 `b6a00ed555775ff1a9620e599852e1d9140d98fc33ce5559fcfbba66d6694618`;456 atoms, Zr24C192H112O128. Analysis-only primitive copy has114 atoms, same composition as ODAC parent; volume differs by+0.0014333%.|Source says `data_calc0`, GDIS, P1; do not call it experimental refinement. Unique periodic atom/proton correspondence is unresolved. A recorded CIF symmetry-parser warning is retained.|
|Six linker map|Six disjoint C8H4O4 fragments plus Zr6O8H4 node. Existing64-design audit reports one periodic connected network with winding rank 3, eight O neighbors per Zr.|Distance/image graph checks are operational, not a bond-order, stability or topology certificate independent of cutoffs.|
|Four node hydroxyls|Parent node H indices 8,15,19,24 map by the recorded cutoff to O96,109,100,83, respectively (zero-based archived atom order). Original-CIF primitive analysis also counts four H–O neighbors within 1.3 Angstrom.|Counts and plausible lengths do not prove identical proton sites/orientations across source and ODAC cells.|
|Frozen inspected checkpoints|All28 node-H records (four per seven snapshots) retained. O–H0.968958–0.972520 Angstrom; six Zr retain eight O neighbors under 2.8-A cutoff; Zr–O approximately2.056–2.279 Angstrom.|Scope is seven selected snapshots; no proof of equilibrium protonation or chemical validity from distances.|
|Amino construction|Lowest-index aromatic H per slot replaced by N; two H added. Initial C–N1.39/N–H1.01 Angstrom and planar geometry. Recorded relaxed structures can become pyramidal.|One positional choice and initial rotamer per slot; alternatives are not exhaustively sampled. No experimental ordering assumption is verified.|
|Contacts/motions|Initial builder rejects periodic contacts below 0.7 Angstrom. Existing inspections retain 122 guest/host contacts within 3.5 Angstrom, amino/linker motions and nonbonded crowding descriptors. Matched diagnostics show substantial framework motion without detected image-bond changes.|Cutoff pass is not chemical acceptance. Optimization trajectories are not diffusion pathways; absence of a cutoff bond change does not rule out model error or proton/coordination problems.|

Sources: [parent audit](../artifacts/phase3/uio66_frozen_dft_v2_qe75/parent_audit.json),
[later publication comparison](../artifacts/phase3/uio66_frozen_dft_v2_qe75/provenance/publication_comparison.json),
[mapping](../artifacts/phase3/uio66_structures/atom_mapping.json),
[64-design audit](../artifacts/phase3/uio66_sampling_audit_v2_verified.json),
[builder](../mof_dac/uio66_structures.py), [inspection tables](UIO66_FROZEN_DFT_DIAGNOSTIC.md).
The old parent-audit/inspection statement that the SI CIF was unavailable is
historical; the later comparison above supersedes it without altering the archive.

## Composition, charge and closed-shell assumptions

For k amino substitutions: **C48H(28+k)NkO32Zr6**, with 114+2k atoms. A substitution
removes one ring H and adds NH2: net N1H1, not N1H2. The original 28 H comprise
24 linker H plus four node H. The formal bookkeeping
`6 Zr(IV) + 4 O(2−) + 4 OH(−) + 6 BDC(2−) = 0`
is consistent with a neutral ideal Zr6O4(OH)4(BDC)6 node/linker model and neutral
amine substitution. This is an assumption-based charge balance, not measured
oxidation-state/spin evidence. Neutral, nonmagnetic, fixed occupations were used
in the exploratory DFT baseline; even electron counts alone do not prove the
correct spin/electronic state.

**No demonstrated composition/proton-count inconsistency was found in the
reviewed saved artifacts.** This is not a new exhaustive structure audit or a
resolution of proton identity. If a reviewer identifies missing/extra protons,
inconsistent charge or unsuitable geometry, stop physical interpretation and
record effects on reference energies/comparability. Preserve original evidence;
any corrected structures require a new version and separately authorized work.

|Slot|Original ring H replaced (also N index)|Attached ring C|
|---|---:|---:|
|L0|10|36|
|L1|22|66|
|L2|11|63|
|L3|7|62|
|L4|6|41|
|L5|9|69|

The bit order in every fit is L0…L5. These atom-index choices are reproducible
construction rules, not experimentally established preferred regioisomers.

## Unanswered questions for a qualified chemistry reviewer

1. Is the publication-to-ODAC mapping and the particular four-OH proton pattern
   adequate for an **ideal ordered model case**, and which proton/source
   correspondence limitations must remain explicit?
2. Is neutral Zr6O4(OH)4 with six BDC-type linkers, no defects/terminal ligands and
   the stated closed-shell assumption a chemically coherent model for this
   limited purpose? Identify any demonstrable inconsistency, not merely unknowns.
3. Are the specified amino positions/rotamers and observed linker/amino motions
   acceptable to analyze as provisional configurations, or does a particular
   contact/geometry invalidate that interpretation? Which alternatives are omitted?
4. Do any retained contacts/OH/amino/coordination records indicate a specific
   proton-transfer, decoordination or electronic-state issue requiring qualification
   before publication? Does the score need wording beyond “sampled energetic
   difference,” given one guest per fixed periodic cell and no thermodynamic sampling?

Record reviewer name/qualification, date, exact evidence versions, answer per
question, blocking findings and disposition in the closure review record. No
reviewer identity, answer or approval is supplied by this document. No request sent.
