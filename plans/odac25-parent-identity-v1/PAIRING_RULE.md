# Proposed corrected pool v1 — NOT an admitted benchmark

Historical input remains `artifacts/kaggle/odac25_paired_targets_2026-09-14/paired_targets.json`.
Its 138 IDs, labels and source selections are unchanged. This proposal is a
separate dataset version. Current admitted count **0**, not 110. Composition
candidates are awaiting authoritative identity evidence.

## Deterministic admission and selection

1. Pin release, split, source shard/member checksum and extraction version.
   Retain source-local index, trajectory name, sid and fid. Index alone is not
   portable between shards or releases. `sid` alone is not certified globally
   unique. Use the release/shard + trajectory + sid/fid tuple and atom checksum.
2. Require an authoritative trajectory-to-**parent state** mapping, including
   initial tagged framework, base/family ID, defect realization, functionalization
   sites, protonation/charge and any preloaded/reacted CO2. Names, formulas,
   reference-energy equality and fragment hashes cannot supply that mapping.
   Missing evidence means quarantine, not inference of an identifier.
3. Require a documented representation mapping: cell, PBC, supercell transform,
   atom identities/permutation and proton/cap occupancy. Compare the same
   representation for this version. An apparent integer composition multiple
   is not automatically normalized or admitted. Future representation conversion
   requires a separately recorded atom mapping and energy normalization rule.
4. Check **original** per-atom tags. Framework=tag 0; adsorbates=tags 1–4.
   Retain tag-zero defect caps, functional groups and preloaded species.
   Exactly one CO2 or one H2O and zero other tagged guests are necessary but
   insufficient: a reacted CO2-bearing framework is a separate parent state.
   Ordinary-parent competition excludes reactive-water variants unless an
   explicit same-state task is approved; no deletion of their extra C/O atoms.
5. Require compatible corrected adsorption labels in eV per one guest, with
   the same released reference convention, gas constants, normalization and
   documented reference-parent link. Check the scalar identity
   `Eads_corrected = energy_old - energy_mof - Σ n_g Egas,g`.
   Its agreement does not verify the referenced structure. The separate 62
   unmatched bare-reference energies remain open; author-confirmed direct-label
   compatibility could permit label use without solving the full bare lookup,
   but that permission/evidence is not established by this audit.
6. Group by `(release, parent_state_id, representation_id, reference_scheme_id)`.
   Within each gas and trajectory, use maximum **stored** fid, preserving the
   historical extraction convention. This does not itself prove convergence.
   Require complete trajectory inventories and the release's acceptance/status
   metadata. Flag missing trajectories and contradictory duplicate fid records.
   Identical duplicates may be collapsed only with a provenance alias list;
   conflicting duplicates remain quarantined.
7. For each admitted state/gas choose minimum corrected final-frame target from
   the complete eligible inventory. Break exact ties lexically by trajectory,
   sid and source key within the pinned release. Never select arbitrary mirror
   survivors when a lower historical frame is missing.
8. Pair only within the same group from step 6. Retain both source records,
   hashes and counts. Preserve all excluded/incomplete records and reasons.
   Changes in labels, membership or number of parent states produce a new
   version, never an in-place correction to the 138-MOF file.
9. Reserve all original 138 evaluation IDs **and all their parent-state/base-family
   aliases** from training, even when excluded from this proposed corrected pool.
   Reject cross-split exact-structure duplicates and related defect/functionalized
   records using authoritative family links. Missing family mapping blocks fitting.
   Composition equality alone neither proves duplication nor clears leakage.

## Present coverage

| Category | Count | Action |
|---|---:|---|
| Composition matched; identity unverified | 110 | Candidate queue; not admitted |
| Selected framework composition conflicts | 27 | Exclude these selected pairs; retain both records |
| Incomplete EPONEE | 1 | Retain historical selection; recover exact missing frame |
| Identity- and compatibility-verified pairs | 0 | No corrected benchmark or real fitting yet |

The 110/138 (79.71%) figure is candidate coverage only. A future complete export
could yield different same-state pairs for some excluded names; that requires new
source-based selection and a versioned coverage report. No replacements are made here.

## Reproduction

From the repository root, using the existing pinned range cache:

```powershell
python -m scripts.audit_odac25_parent_identity --output local/odac25-parent-identity-replay-NEW
python -m pytest tests/test_odac25_parent_identity.py tests/test_odac25_acquisition.py -q -p no:cacheprovider --basetemp local/odac25-parent-tests-NEW
```

Use new output/temp paths; the audit refuses to overwrite its output directory.
`--fetch-eponee` permits only the two indexed EPONEE single-CO2 record reads with
a 2-MiB counted range cap. All 275 selected-record structural reads remain offline.
No command performs a full database download, model fitting or inference.

`receipt.json` hashes the generated audit outputs and input/source files.
`review_receipt.json` additionally seals this policy, acquisition requirements,
the report and test evidence. Raw range receipts hash local byte ranges, not the
entire remote LMDB; do not describe them as full-file checksum verification.
