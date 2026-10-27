# Focused chemistry inspection v2 — assessment pending

27 October 2026. Exact archived coordinates, existing inspection descriptors and
new **display-only** periodic images. No repair, proton change, relaxation,
energy/force inference or new scientific fit. Neither this packet nor its
AI-assisted narrative constitutes qualified chemical approval.

## Structures and labels

The [exact-geometry directory](../plans/phase3-review-response-v2/inspection/exact)
contains byte-copied JSON and original checkpoint trajectories for:

- 110111 H2O start 28: 0.01 and 0.005 eV/Angstrom (before/after).
- 110111 CO2 start 7: 0.02, 0.01 and 0.005 eV/Angstrom (two successive transitions).
- The unmodified parent export and original-publication CIF, kept as distinct sources.

[Source records](../plans/phase3-review-response-v2/inspection/source_geometries.json)
give checkpoint/frame indices, original file hashes, optimizer checkpoints and
saved UMA energies. JSON round-trips the source float64 values exactly;
checkpoint numbers, coordinates and cells were compared without rounding.
[Coordinates CSV](../plans/phase3-review-response-v2/inspection/coordinates.csv)
has 749 rows (five 127-atom complexes plus the 114-atom parent), with original
zero-based atom indices. [Cell vectors](../plans/phase3-review-response-v2/inspection/cells.csv)
are in Angstrom. No symmetry standardization, sorting or atom permutation was applied.

Labels such as `H8@(0,-1,1)` identify the original atom and an integer lattice
image. Display position is `source_position + image @ cell`; the exact image and
position of every plotted point are in
[view_images.csv](../plans/phase3-review-response-v2/inspection/view_images.csv).
Two orthographic projections reduce ambiguity; projected overlaps are not atomic
collisions. A periodic framework cannot be represented as one unbroken finite molecule.

## Node, proton, amino and contact evidence

[Parent node view](../plans/phase3-review-response-v2/inspection/views/parent_node.svg)
shows the four hydroxyl protons. H8/O96, H15/O109, H19/O100 and H24/O83 are stable
indices in the ideal-model parent order. The five checkpoint OH panels show all
four environments, coordinating Zr images and the three nearest saved candidate
acceptors. All acceptors remain in the tables; drawing only three is a display
choice, not an exclusion from assessment.

|Inspection item|Exact/table evidence|
|---|---|
|OH positions, donor correspondence and candidate acceptors|[node_protons.csv](../plans/phase3-review-response-v2/inspection/node_protons.csv)|
|Oriented O-image→H Cartesian vectors and original saved lengths|[OH_vectors.csv](../plans/phase3-review-response-v2/inspection/OH_vectors.csv)|
|Zr–O distances and explicit images|[Zr_O_contacts.csv](../plans/phase3-review-response-v2/inspection/Zr_O_contacts.csv)|
|Carboxylate O/C assignments, ring torsions and O–Zr contacts|[carboxylates.csv](../plans/phase3-review-response-v2/inspection/carboxylates.csv)|
|Amino C/N/H indices, lengths and angles|[amino.csv](../plans/phase3-review-response-v2/inspection/amino.csv)|
|Closest saved nonbonded/crowding flags, excluding shared bonded neighbors|[crowding table](../plans/phase3-review-response-v2/inspection/crowding_excluding_shared_bonded_neighbor.csv)|
|Guest/host contacts, including periodic images|[guest_contacts.csv](../plans/phase3-review-response-v2/inspection/guest_contacts.csv)|

These tables filter existing archived descriptors to the five poses. Their
distance cutoffs remain diagnostic conventions: Zr coordination counts use
2.8 Angstrom; contact lists reach 3.5 Angstrom. The archived carboxylate
`O_Zr_contacts` list inherits the broader 3.5-A contact collection, even though
the row labels the 2.8-A coordination cutoff; **apply the explicit distance
filter before interpreting a coordination count**. No table alone establishes
electronic bonding. Crowding tables retain only the original nearest 30 flags,
not an exhaustive steric proof. Full saved per-pose descriptor JSON is included.

New labeled OH/guest panels are in [views](../plans/phase3-review-response-v2/inspection/views).
The original Zr-aligned before/after images and display-coordinate JSON are
copied unchanged: [water](../plans/phase3-review-response-v2/inspection/views/uio66_110111_H2O_b1_random_archived.png),
[CO2](../plans/phase3-review-response-v2/inspection/views/uio66_110111_CO2_b0_targeted_archived.png).
Optimization paths are numerical relaxation paths, not diffusion trajectories.

## Source-CIF correspondence versus the defined ideal model

The [publication comparison](../plans/phase3-review-response-v2/inspection/source_publication_comparison.json)
supports composition/cell consistency and four OH per primitive model, but does
not establish unique periodic atom/proton correspondence. Its source describes
a calculated structure, not an experimentally refined realization of our amino
models. The supplied source CIF and parent JSON use different atom orders and
representations; model labels must not be transferred to the CIF by row number.

The defined model has Zr6O4(OH)4 with six BDC-type linkers and four explicit node
H. For k amino substitutions its formula is C48H(28+k)NkO32Zr6; neutral charge
and closed-shell state are assumptions of the ideal model. One selected H per
linker is replaced by NH2 under a fixed atom-index/orientation rule. No demonstrated
composition/proton-count inconsistency has been identified in the saved evidence;
that observation is **not approval of proton positions, conformations or physics**.

## Two open clarification items — qualified reviewer required

**Q1 — source/proton correspondence.** Does the archived parent define a chemically
coherent ideal Zr6O4(OH)4(BDC)6 model with the four listed hydroxyl assignments and
orientations? What source-CIF-to-model correspondence can actually be justified,
and what ambiguity must remain? Identify any proton-count, placement or formal-charge
inconsistency; do not require an unsupported claim of experimental identity.

**Q2 — geometry/model adequacy.** For the exact water-28 and CO2-7 checkpoints,
are the amino/linker/proton configurations, carboxylate coordination and periodic
contacts chemically interpretable as provisional ordered configurations, or is
there a specific implausible geometry, proton transfer, decoordination, crowding
or spin/charge assumption that blocks that interpretation? State the limitations
from fixed amino choices, rotamers and periodic single-guest loading.

Both remain **OPEN** until an appropriately qualified reviewer records identity,
qualification, date, reviewed snapshot hash, answers and disposition of blocking
findings. Absence of a demonstrated blocker is not approval. Do not repair a
questionable configuration: retain it as evidence and propose any correction
separately. No request has been sent.
