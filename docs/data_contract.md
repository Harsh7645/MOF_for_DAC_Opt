# Selection graph data contract v1

Reference input: `data/synthetic/toy.json`. Node array order fixes numerical indices;
changing that order changes x indexing, so record instance hashes.

| Field | Meaning |
|---|---|
| schema_version | Integer 1 |
| parameter_regime | synthetic, heuristic, or dft_grounded; a provenance label, not an automatic quality certificate |
| energy_units | Shared coefficient unit or dimensionless; loader rejects inconsistent per-record units |
| missing_interactions | Must equal modeled_zero; omitted pairs are deliberately zero in this model |
| nodes | Unique ID, metal/linker kind, h, source, method, units |
| edges | Distinct known endpoint IDs i/j, J, source, method, units; one record per unordered pair |
| constraints | Unique ID, coefficients keyed by node ID, sense eq/le, rhs, source, method |

All optimization coefficients must be finite JSON numbers. Duplicate JSON keys,
duplicate edges, self-loops and unknown variables are rejected. Graph loading
checks consistency, not whether a source claim is true or a constraint set admits
a solution. Solvers report infeasibility/initialization failure separately.

No automatic charge or budget inference: rows in the JSON are authoritative.
For real data, derive and inspect rows from explicit cell/slot multiplicities and
formal charges. Add source version/DOI, derivation, calibration dataset,
uncertainty and conditions to each scientific record; extra metadata is retained
in the returned dictionary. v1 enforces source/method/unit fields, not the
scientific validity or completeness of a DFT derivation.

An absent edge cannot stand for an unmeasured interaction if that uncertainty is
material. Measure/model it first, or create an explicitly labeled zero-assumption
ablation. Do not mix kcal/mol, kJ/mol, eV and dimensionless terms without an
explicit common-scale derivation. Synthetic parameters must never enter a
real-material benchmark without their synthetic label.

Full CoRE ingestion and crystal assembly are deliberately pending. A CIF file
describes an assembled periodic structure, not this selection graph schema.

## External material-ranking manifest

`mof_dac.materials.load_material_manifest` validates a separate CSV manifest for
the material track. Required columns are `structure_id`, `cif_path`, `target`,
`target_units`, `split`, `source`, `license` and `conditions_json`. CIF existence,
finite labels, unique IDs, provenance and nonempty conditions are checked before
model input. This manifest does not convert assembled structures into h/J values.
