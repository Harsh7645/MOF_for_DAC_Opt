# Draft v2 — not sent

Previous draft `ODAC25_PARENT_STATE_REVIEW_QUESTION.md` is preserved.

For the ODAC25 20250918 filtered validation release, can you provide the
authoritative trajectory-to-parent-state and base-family mapping, including
defects, protonation and reacted/preloaded CO2?

Our unchanged 138-name selection has 110 composition-matched but
identity-unverified pairs, 27 framework-composition conflicts and one missing
mirror record. All 27 water-side frameworks contain C1O2 more than their CO2-side
counterparts; 20 names contain `CO2_COOH`, seven `CO2_NCOO`. Your paper §2.2.2
excludes reactive-water cases from its comparison. For example,
`CAXVOO_0.08_0_eeen_19`: CO2 index101/sid7679/fid101 has C112H95N8O72Fe24;
water index2680/sid62435/fid370 has C113H95N8O74Fe24. Can you confirm the original
tags and distinct parent/reference states, and the identifier to use for pairing?

Please also recover **EPONEE_w_CO2_random_1, fid665** (source index512478;
`energy_ads_corrected = -0.3873819799998728 eV`) with sid, original tags and
geometry. Index refers to `val/mof_plus_adsorbate/part_00000.aselmdb`, SHA256
`2927f1ebb3af5fd4ea6e5d1072f9bdef549afa9e53ce3f0605955885da4b6c8c`.
The mirror's two other CO2 trajectories are not substitutes.

Separately, please confirm the corrected-target convention
`energy_old - energy_mof - sum(n_g Egas,g)` and exact bare-state links. Our 62
unmatched references remain unresolved. Could you supply a compact existing-data
export for eight complete paired training parents, with final-frame inventories,
state/family IDs and official splits, excluding all 138 evaluation families?
The export field specification is in `plans/odac25-parent-identity-v1/TRAINING_EXPORT_REQUIREMENTS.md`.
