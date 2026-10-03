# ODAC25 reference convention: technical clarification draft

Prepared locally; not sent to the professor or dataset authors.

## Reproducible observation

Frozen validation source: `val/mof_plus_adsorbate/part_00000.aselmdb`,
SHA-256 `2927f1ebb3af5fd4ea6e5d1072f9bdef549afa9e53ce3f0605955885da4b6c8c`.
The target rule keeps exact single molecules, largest fid per trajectory, then
the lowest final-frame `energy_ads_corrected` per MOF/gas. There are 285 targets,
forming 138 paired MOFs. This pool remains unchanged.

Across an authenticated 2,048-row audit, the stored identity
`energy_old - energy_mof - energy_ads_corrected` gives the isolated-gas constants
-22.990396 eV for CO2 and -14.236396 eV for H2O, with spreads below 3.3e-14 eV.
Using corrected `energy` instead breaks this identity.

Searching original and corrected energies of all 189,504 stored bare-MOF rows
for the same MOF at 1e-5 eV tolerance finds matches for only 5 of 67 distinct
previously unresolved reference energies. Examples without a match:

| MOF identifier | Expected reference (eV) | Nearest stored error (eV) |
|---|---:|---:|
| CAXVOO_0.08_0_eeen_19 | -2159.1267650500004 | 0.00012453000044843066 |
| CAXVOO_0.08_0_mmen_14 | -1927.38452796 | 0.03457721000017955 |
| MALROJ_0.11_0_een_44 | -2529.68042662 | 0.15087859999948705 |

Evidence: [reference lookup](../artifacts/kaggle/odac25_reference_audit_2026-10-02/reference_lookup/phase3_reference_frame_lookup.json)
and [audit explanation](PHASE3_REFERENCE_AUDIT.md).

## Questions for review

1. Which trajectory/frame identifier and bare-reference calculation produced
   `energy_mof` for each target? Is a mapping table available?
2. Is that value a final high-k-point single-point energy, a VASP free energy,
   an extrapolated energy, an average corrected trajectory energy, or another
   convention? How does it map to exported bare `energy` and `energy_old`?
3. Are reference energies normalized to a primitive cell or supercell? Which
   dataset revision contains the matching geometries and energies?
4. Can matching training final-frame `energy_ads_corrected`, `fid` and reference
   metadata be obtained from bounded shards? The inspected training mirror does
   not supply the frozen target contract's corrected field and fid.

The [ODAC25 paper](https://arxiv.org/html/2508.03162) describes average k-point
corrections and re-relaxed bare reference selection, but the exact field-to-frame
export mapping remains unresolved. Energy convention/version/cell normalization
are hypotheses, not established explanations. Missing numerical matches alone
do not prove missing geometries. Do not loosen the guard or substitute a smaller
candidate pool and present it as the frozen benchmark.
