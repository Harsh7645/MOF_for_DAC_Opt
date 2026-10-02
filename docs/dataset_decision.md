# Phase 3 external-data decision

Research checked 2026-09-12. The user has ODAC25 and UMA Hugging Face access and
approved paired CO2/H2O atomistic targets with Kaggle GPU compute. Authenticated
inventory and one filtered-validation GCMC schema inspection succeeded. A
16-record UMA T4 execution smoke also succeeded. A target-bearing
`mof_plus_adsorbate` shard remains pending.

| Source | Useful content | Fit and limit |
|---|---|---|
| [ODAC25](https://fair-chem.github.io/odac25/) | About 15,000 MOFs and DFT energies/forces for CO2, H2O, N2 and O2; CC BY 4.0 | Best direct DAC source. Very large; labels are atomistic energies/forces, not automatically process working capacity. |
| [ODAC23](https://pubs.acs.org/doi/10.1021/acscentsci.3c01629) | More than 8,000 MOFs with CO2/H2O adsorption calculations and published splits/models | Stable published benchmark, superseded for new modeling by ODAC25. |
| [CoRE MOF 2024](https://zenodo.org/records/15055758) | Curated experimental structures, descriptors and public SI subset | Strong candidate-identity source; does not provide a complete DAC target for every structure. |
| [ARC-MOF](https://zenodo.org/records/6908728) | Large structure set, DFT-derived charges and gas-separation process tables | Useful for adsorption/process studies; its listed process conditions are not automatically ambient-air DAC conditions. |
| [MOFTransformer](https://github.com/hspark1212/MOFTransformer) | Pretrained structure representation and CO2 Henry-coefficient task | Matches the report baseline family, but requires PyTorch, structure preprocessing and a target-compatible fine-tuned checkpoint. |

## Recommendation

Use an ODAC25 subset with official structure-disjoint splits as the primary
material benchmark. Use a current FAIR-Chem ODAC model for a data-ingestion smoke
test, and add MOFTransformer or CGCNN only when its target exactly matches the
selected label. Keep CoRE MOF identifiers as an experimental-structure crosswalk
where licensing permits.

Two valid targets lead to different projects:

1. **Atomistic adsorption target:** CO2 adsorption energy with H2O competition.
   ODAC25 labels and pretrained models directly support this route, but adsorption
   energy alone is not a complete DAC process metric.
2. **Process target:** working capacity/selectivity under explicit adsorption and
   regeneration temperature, pressure, composition and humidity. This requires
   compatible isotherm/GCMC data or new simulations; ODAC25 energies alone are
   insufficient.

The selected target is the paired atomistic route. Its frozen definition and the
required distinction from process performance are in `ODAC25_TARGET_CONTRACT.md`.
The next evidence gate is a target-bearing `mof_plus_adsorbate` extraction with
verified CO2/H2O pairing and structure-disjoint split mapping.
