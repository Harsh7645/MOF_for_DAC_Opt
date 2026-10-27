# Smallest useful compatible export — request, not downloaded data

## First unblock identity (no training archive needed)

Request an existing-data, source-side export, with publisher provenance:

- Mapping for the **276 historical selected source tuples** in `pair_status_v1.csv`
  to official parent-state IDs, base-family IDs and their exact initial parent
  structures/atom hashes. Include unresolved/missing mappings explicitly.
- For the 27 conflicts: original tags and atom arrays for both selected frames,
  plus documented meaning of `CO2_COOH`/`CO2_NCOO` and their reference states.
- For the 110 composition matches: original parent identity/variant metadata;
  same-composition structures and molecular graphs are not unique identifiers.
- Exact EPONEE `EPONEE_w_CO2_random_1`, fid 665, corrected energy
  −0.3873819799998728 eV; source-local index 512478 in the pinned validation shard.
  Include sid, all tags, coordinates/cell and original source checksum.

Suggested filenames below are an **export contract**, not existing published URLs.
Start with compressed metadata only and provide actual byte counts/checksums
before structure transfer. A 5-MiB metadata cap is a requested transfer bound,
not a measured size. If exceeded, return a catalog/size estimate, not a truncated
inventory presented as complete. The pending author question is in
`docs/ODAC25_PARENT_STATE_REVIEW_QUESTION_V2.md`.

## Then a minimal real-training feasibility export

Eight fully documented training parent states from eight disjoint base families,
each with complete single-CO2 and single-H2O final-frame inventories, are a small
schema/leakage/CV feasibility sample: **16 paired components / 8 parent pairs**.
Selection must use official train split, deterministic parent-ID order after
eligibility/family filtering, never evaluation target performance. Sixteen
parent states may be requested if eight cannot support the registered grouped
validation. Neither sample size promises a useful or publishable ridge benchmark.
Full fitting remains blocked pending identity and target-compatibility gates.

| Export | Required fields |
|---|---|
| `release_manifest.json` | Publisher/release revision; filtered archive URL and member catalog; SHA256; split provenance; export script hash/version; extraction rules; byte counts |
| `parent_states.jsonl` | Official state ID and base-family ID; aliases; original parent structure path/hash; defect realization/caps, functionalization/site map, protonation/net charge and reacted/preloaded guests; cell/PBC/supercell and atom mapping |
| `parent_structures/` | Exact numbers, positions and cell without rounding, PBC, tags, charge/spin where recorded; original atom IDs; composition derived from tag 0, not guessed from filename |
| `final_frames.jsonl` | Parent/state/family IDs; official split; source member/hash/local index; name/sid/fid; gas counts/nads; tags/structure hash; stored-final selection rule; convergence/acceptance flags when supplied; energy, energy_old, energy_mof, energy_mof_old, energy_ads, energy_ads_corrected with units |
| `reference_conventions.json` | Exact corrected-target formula; isolated-gas constants and versions; referenced bare-state IDs/hash; k-point/old-energy distinctions; per-cell/per-guest normalization; documented identity of shared reference state |
| `trajectory_inventory.jsonl` | Complete expected trajectory IDs/counts per parent and gas; selected final fid/source key; omissions/failures and reason; an empty list is different from unavailable inventory |
| `paired_targets.jsonl` | Derived only after admission: both selected source tuples/energies/hashes, parent/state/family, reference scheme, selection rule, complete candidate counts |
| `split_membership.jsonl` | Official split plus family-level training/internal-validation groups; aliases of all original 138 reserved IDs; exact duplicates and cross-split family overlap audit |

An initial **25-MiB uncompressed export cap** is a request, not an estimated
payload size. Ask for a manifest with actual compressed/extracted sizes first.
Never silently truncate a parent's trajectory inventory to satisfy the cap.
No intermediate relaxation frames, forces or model features are needed for
the composition/constant/ridge baseline. Exact parent arrays and final labels
are sufficient once the identity/reference questions are answered.

## Why not download a large mirror now?

The previously inspected mirror train and validation files total
6,683,783,168 bytes (6,547,623,936 + 136,159,232). Both partitions derive from
original training with a record-level split. Their retained paired-parent and
family-safe coverage remains unknown; decomposition omissions can lose minima.
The official filtered validation archive is 11,117,673,531 compressed bytes;
its source member here was 8,418,258,944 bytes. Neither full download is needed
to answer the focused identity question. Current official training archive
location/catalog/extracted size is not confirmed. No large acquisition is authorized.

Parent identity and energy-reference compatibility are separate gates. Exact
source `energy_ads_corrected` avoids recreating missing references; it does not
establish that two gases share a parent or resolve the 62 unmatched reference
energies. Evaluation membership stays frozen while these gates are investigated.
