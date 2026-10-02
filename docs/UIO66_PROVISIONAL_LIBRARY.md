# Provisional UiO-66 design library

User authorized development on 2026-10-02. This is a reviewable design proposal,
not an approved chemistry library or assembled structural dataset.

Use [uio66_provisional.json](../data/design/uio66_provisional.json). Fix the ideal
hydroxylated Zr6O4(OH)4 node and fcu topology. Linker choices are BDC and
2-amino-BDC. No defect/cap/dehydroxylation or amino protonation change is included.
The [UiO-66 structural study](https://pmc.ncbi.nlm.nih.gov/articles/PMC5006632/)
supports the node and topology. The publisher excerpt for the
[mixed-linker study](https://pubs.rsc.org/en/content/articlehtml/2017/cp/c6cp07801j)
describes six primitive-cell linkers and amino substitutions; full text access
returned 403, so its optimized geometries have not been inspected.

## Variable and graph contract

Six bits select substitution at always-occupied slots: `0=BDC`, `1=NH2_BDC`.
This eliminates the one-hot fitting gauge of the synthetic two-choice encoding.
The node has 12 incident connections, but a periodic cell owns six bridging
linkers because each connects two nodes. Slot atom IDs and periodic endpoints
must come from a verified CIF; L0–L5 are provisional labels.

The proposed composition is `C48 H(28+k) N(k) O32 Zr6`, where `k=sum(x)`.
Formal node charge is +12 and each linker is -2, so all substitutions preserve
zero formal charge under the stated ideal assumptions. This arithmetic is not
an oxidation-state calculation or proof of chemical/structural validity.

`python -m scripts.build_uio66_design` enumerates 64 nominal configurations.
Its graph stores six variable nodes and 15 possible pair-regression terms.
These edges are not bonds or established physical interactions. Coefficients
remain null and optimization is prohibited until measured/predicted labels
have provenance. Symmetry-unique count is unknown; no train/test split is
assigned before structural identity and symmetry duplicates are resolved.

## Grounding sequence

1. Obtain a licensed provenance-bearing ideal parent CIF with hydrogen atoms;
   hash it, verify primitive-cell multiplicity and map the six complete linkers.
2. Freeze one amino orientation per slot, periodic endpoints and substitution
   atom mapping. Generate structures; validate coordinates, overlap, coordination
   and stoichiometry. Broaden orientation choices only as a separate experiment.
3. Deduplicate symmetry-equivalent structures before grouping/splitting. Keep
   configurations across amino counts: fixed-count-only data can make a full
   quadratic model unidentifiable.
4. Score paired adsorption under a consistent placement, relaxation and energy
   reference protocol. Bare crystal energy alone cannot supply adsorption h/J.
5. Fit `c + h@x + sum(J_ij*x_i*x_j)` using the existing `fit_pairwise` routine.
   The six-bit full basis has 22 parameters. Require full rank, held-out errors,
   an additive-model comparison and uncertainty before calling it grounded.
6. Freeze a chemistry-reviewed amino budget and run SNN/SA/Gurobi on the same
   grounded model. Independent chemistry validation remains Phase 4 work.

## Executed structural prototype, 2026-10-02

An authenticated ODAC25 bare frame was exported locally: `jz4002345_si_002`,
source index 184693, trajectory `jz4002345_si_002_w_H2O_random_2`, fid 7,
composition C48H28O32Zr6. The source ID points to the
[UiO-66 mechanical stability study](https://pubs.acs.org/doi/10.1021/jz4002345);
the publisher lists supporting CIFs, but equality with its original CIF has
not been established. Coordinates are the ODAC25 re-relaxed geometry, not an
invented reconstruction. ODAC25's dataset card declares CC-BY-4.0.

Parent JSON/CIF and source hashes are preserved under
`artifacts/kaggle/odac25_reference_audit_2026-10-02/final_frames/`.
`mof_dac/uio66_structures.py` infers periodic organic connectivity with explicit
C-C/C-H/C-O distance cutoffs and retains cell-image shifts. It found six complete
C8H4O4 linkers and a remaining Zr6O8H4 node. Bond inference is a hypothesis.

```powershell
python -m scripts.build_uio66_structures --parent artifacts/kaggle/odac25_reference_audit_2026-10-02/final_frames/phase3_uio66_candidate_parent.json
```

Executed output: `artifacts/phase3/uio66_structures/`, containing an atom mapping,
manifest with file hashes and 64 CIF initial geometries. A deterministic ring H
per linker is replaced by N, with two added H; C-N=1.39 and N-H=1.01 Angstrom,
planar amino geometry. These distances and orientations are initialization
assumptions requiring relaxation and chemistry review. All 64 compositions pass;
no periodic pair is closer than 0.7 Angstrom. This is only a severe-contact filter,
not a steric-energy, coordination or synthesis-feasibility certificate.

The structures are unrelaxed. Symmetry deduplication, full topology review,
paired adsorption labels, fitted coefficients and chemical approval remain
pending. The 138 ODAC25 validation MOFs are a separate prediction benchmark;
their labels are not used to fit these 64 configurations. The parent comes from
validation, so this separate design experiment must not enter the ODAC25
training table or alter the frozen held-out benchmark.
