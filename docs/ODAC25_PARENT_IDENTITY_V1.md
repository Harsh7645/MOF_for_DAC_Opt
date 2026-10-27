# ODAC25 parent-identity investigation v1 — 26 October 2026

**Real fitting remains on hold.** All 138 historical IDs and labels are preserved.
The separate corrected-pool proposal admits **zero** pairs pending authoritative
parent identity and compatible references. It contains a 110-pair candidate queue,
27 excluded selected pairs and one incomplete pair; it is not a replacement benchmark.

## Versioned evidence

- [All 138 pairs: CSV](../plans/odac25-parent-identity-v1/pair_status_v1.csv),
  [JSON](../plans/odac25-parent-identity-v1/pair_status_v1.json).
  Each row retains both frozen trajectories, source-local indices, fids, targets,
  candidate counts, split/shard checksum, mirror revision, available sids,
  per-gas host/guest atomic-number counts and record hashes. EPONEE's unknown
  CO2 composition/sid remain absent; historical target provenance is present.
- [275 structural diagnostics](../plans/odac25-parent-identity-v1/selected_structure_diagnostics.jsonl),
  [summary](../plans/odac25-parent-identity-v1/summary.json),
  [source/output receipt](../plans/odac25-parent-identity-v1/receipt.json).
- [Corrected-pool proposal](../plans/odac25-parent-identity-v1/corrected_pool_proposal_v1.json),
  [deterministic admission/selection rule](../plans/odac25-parent-identity-v1/PAIRING_RULE.md),
  [minimal export requirements](../plans/odac25-parent-identity-v1/TRAINING_EXPORT_REQUIREMENTS.md).

Original targets SHA256 remains
`58c5dd5bec75366e3cd95dbd7ba9d714d1ff0163a560158cf154640aed5095bf`.
Pinned mirror revision is `81a85299823a7e75e0ed7fe39640c99297906080`;
preprocessing commit is `7589209ff53514a136f20043e77408108d6f8530`.
This is a derivative mirror, not a replacement for official parent metadata.

## What establishes identity, and what was actually recovered?

| Diagnostic | 110 composition candidates | 27 composition conflicts |
|---|---:|---:|
| Identical stored cell matrices | 110 | 27 |
| Identical supercell metadata | 110 | 27 |
| Equal mirror fragment signatures | 86 | 0 |
| Different mirror fragment signatures | 24 | 27 |
| Available authoritative shared parent-state IDs | 0 | 0 |

All 275 selected available records say `supercell=[1,1,1]`. Thus the **observed**
composition conflicts are not explained by differing reported supercell factors.
This does not establish the release's original primitive-cell representation.
All 110 candidate pairs also have the same scalar `energy_mof` within
1.14e-13 eV (107 bit-identical; three differ only at floating-point roundoff).
Equal cell/reference scalars still do not distinguish isomers, proton placements,
defect sites, topological or reacted states.

Additional structural checks use stored fragment graphs: atomic numbers,
per-atom formal-charge labels, bond types, fragment roles and explicit H-neighbor
environments. Their sorted 3-iteration Weisfeiler–Lehman signatures are invariant
to atom reordering in tests. These are **diagnostics**, not unique structural
identifiers or isomorphism proofs. They omit interfragment periodic connectivity;
mirror bond/charge perception and decomposition can change with relaxation.
The 24 differing cases need original structures/mapping; they are not declared
different parent materials. Matching signatures do not certify the other 86.

The stored records contain name, sid/fid, mof_name/type, supercell and energy/gas
fields, but no explicit authoritative parent-state or base-family mapping.
Identity needs the original initial tagged framework plus documented defect,
protonation, functionalization and preloaded-state provenance. Adsorbed final
coordinates may differ physically even for one parent; coordinate equality is
not an appropriate requirement. No guessed name parsing supplies these links.

## Audit of the 27 conflicts

Every available selected record passes: exact frozen name/fid/corrected label;
one intended guest; host+guest conservation of every element; and expected
single-gas stoichiometry. Guest removal preserves NODE, LINKER and SOLVENT blocks.
Removing all water-looking fragments would incorrectly remove framework caps.

Source tracing confirms [mirror framework extraction uses tag 0](https://github.com/nayoung10/AtomMOF/blob/7589209ff53514a136f20043e77408108d6f8530/src/preprocess/odac25/extract_mofid.py)
and [guest extraction uses nonzero tags](https://github.com/nayoung10/AtomMOF/blob/7589209ff53514a136f20043e77408108d6f8530/src/preprocess/odac25/extract_blocks.py).
The [dataset author's tag definition](https://github.com/facebookresearch/fairchem/issues/1463#issuecomment-3263599760)
agrees. An [author clarification on a functionalized defective structure](https://github.com/facebookresearch/fairchem/issues/1562#issuecomment-3533484896)
explains framework water caps and COOH groups; it does not identify all our rows.

**All 27 deltas are water-host minus CO2-host = C1O2**, with no H or metal-count
difference. Water names contain `CO2_COOH` in 20 cases and `CO2_NCOO` in seven.
Each pair shares mof_name and cell but has different framework composition and
reference energy. The [ODAC25 paper §2.2.2](https://arxiv.org/html/2508.03162v2)
describes reactive CO2 placements followed by added water, and explicitly excludes
reactive-water cases from its single-gas functionalization comparison. This is
documented support for the parent-variant explanation. Mapping those mechanisms
to every selected row remains an inference pending official tags/state links.

No arithmetic guest-removal error was found in the current mirror partition.
**Original raw tags are unavailable**, so the mirror cannot independently prove
correct original tagging. A further warning: concatenated reconstructed-block
atomic-number order matches the stored structure order in 214/275 records and
differs in 61. Element multisets still match. Therefore block indices must not
be used as original-structure atom IDs. This audit uses fragment-local graphs,
not cross-array coordinate assignments or an invented periodic atom mapping.
See source reconstruction in [extract_feats.py](https://github.com/nayoung10/AtomMOF/blob/7589209ff53514a136f20043e77408108d6f8530/src/preprocess/odac25/extract_feats.py).

## EPONEE: exact missing selection, no substitute

The complete small mirror index has 3,582 keys. The original selected key
`512478` is absent. The index's ordinal mapping was cross-checked against all
275 available selected records. The two retained EPONEE single-CO2 records are:

| Source key | Mirror ordinal | Trajectory | sid | fid | Corrected target (eV) |
|---|---:|---|---:|---:|---:|
| 511812 | 3066 | EPONEE_w_CO2_1 | 88026 | 170 | −0.33779519999984586 |
| 512637 | 3067 | EPONEE_w_CO2_random_2 | 106701 | 158 | +0.08577904000014769 |

Neither is the selected **EPONEE_w_CO2_random_1 / fid665 /
−0.3873819799998728 eV**. Its sid remains unknown. Its selected water partner is
source516486 / EPONEE_w_H2O_random_2 / fid306. Exact-name/index web searches did
not expose the missing authoritative record; this is not proof of global absence.
It is absent from this pinned derivative, whose preprocessing can omit records.

`512478` is an **AseDBDataset source-local index** in the pinned shard, not a
universal database row or mirror row ordinal. Source hash + trajectory + fid,
with sid/atom hashes when recovered, are required for reconciliation. No name-only
replacement or recomputed minimum from the two survivors was made.

## Energy compatibility remains a separate gate

The previous 275-record audit's scalar identity was rechecked while validating
records: `energy_ads_corrected = energy_old - energy_mof - Σ n_g Egas,g`,
with CO2 −22.990396 and H2O −14.236396 eV. Targets are per single guest, not
per atom. `energy` is a different corrected-total field and is not substituted.
Largest stored fid per trajectory is an extraction rule, not proof of physical
convergence. Then the historical selector minimizes per mof_name/gas; that
grouping is precisely what the identity proposal changes prospectively.

Direct published labels avoid re-deriving missing bare references. They do not
resolve the **62 unmatched bare-reference energies**, prove a common reference
structure or make unlike parents a competition pair. No real model fit, score,
ranking or claim of reference resolution was produced.

## Acquisition, validation and next action

All selected structural checks replayed existing local ranges. New database
payloads were only two EPONEE record ranges: **23,069 + 23,402 = 46,471 bytes**,
including overflow headers. The public versioned paper HTML was cached at
460,865 bytes with a separate source receipt. No full database was downloaded.
The five-record local structural smoke check took approximately 0.051 seconds;
the complete audit plus two bounded reads took approximately 8.2 seconds.
This is a small CPU metadata/graph check, not an ML calculation. Generated audit
files before explanatory documents total 2,170,089 bytes.

**Validation:** ten targeted tests pass (1.91 seconds). Tests cover inert pickle
handling, range guards, numeric decoding, atom-permutation invariance,
proton-neighbor/charge changes, invalid bonds, missing pairs and no admission
from composition equality. The first test invocation had two setup errors from
Windows temporary-directory permissions; a new repository-local temporary path
passed without modifying old temporary files. An offline replay reproduces all
seven generated files byte-for-byte. All original investigation files and the
failed first parsing attempt remain intact. No historical DFT audit was rerun.

Next smallest action: obtain official parent-state/family mappings, raw tags for
the conflicting examples, and the exact EPONEE record, followed by a complete
eight-parent training export if compatible. The [short review request](ODAC25_PARENT_STATE_REVIEW_QUESTION_V2.md)
is drafted, **not sent**. Actual export sizes must be supplied before transfer;
the request specifies small caps, not invented size estimates. No model code
changed. Higher-cutoff DFT remains deferred for RAM; Phase 3 remains incomplete.
