# Provisional UiO-66 design library

User authorized development on 2026-10-02. This is a reviewable design proposal,
not an approved chemistry library. Initial and model-relaxed structures now exist;
the dated execution sections below define their limited validity.

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
remain null and optimization is prohibited until measured/predicted adsorption
labels have provenance. Declared-tolerance parent-operation groups have been
audited; complete crystallographic equivalence remains unverified. No train/test
split is assigned before duplicate groups are frozen.

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

## Executed grouping and bare relaxation, 2026-10-03

`mof_dac/structure_groups.py` checks species-preserving bijections under verified
parent operations, including periodic images and Cartesian cell rotations.
The initial audit found 64 groups at 1e-5 Angstrom (one operation), and 53 groups
at both 0.01 and 0.05 Angstrom (24 operations). Connected groups are conservative
split-safety units; approximate matches need not be mutually within tolerance.
This is not a certificate of 53 symmetry-unique crystals. Preserve detected
initial duplicates together even if later relaxation separates their geometries.
Evidence: [initial groups](../artifacts/phase3/uio66_groups.json).
After relaxation, the same parent-operation audit found 54 groups at 0.01
Angstrom and 53 at 0.05. Evidence:
[relaxed groups](../artifacts/phase3/uio66_relaxed_groups.json). Tolerance sensitivity
and relaxation differences reinforce the need to retain initial duplicate groups.

An actual four-structure T4 pilot converged, followed by all 64 nominal structures
split across two T4 GPUs. `kaggle/run_uio66_relaxation.py` used UMA-s-1p2p1,
task `odac`, heterogeneous `batch` inference, ASE LBFGS with maxstep 0.1 Angstrom,
fixed cells and all atomic positions free. Tolerance: 0.05 eV/Angstrom;
budget: 150 steps. All 64 converged in 0–42 steps, force norms
0.0185348–0.0499344 eV/Angstrom. All 64 have zero contacts below 0.7 Angstrom
and no changed inferred organic, amino, hydroxyl or Zr-O edges under the declared
diagnostic cutoffs. Maximum atom displacement: 0.337744 Angstrom. Each result
was saved immediately. Per-structure compute summed to 378.33 seconds across
the two processes; this excludes model startup/download and is not end-to-end
wall time or a solver-speed claim.

Pinned HF revision: `f611b917d9c68566bbbeccbb0aa0f7cad1696cb2`;
actual file: `checkpoints/uma-s-1p2p1.pt`;
SHA-256: `b2673b85037b075674c25f55c34ffe1ff1e15db924be977b10a184765df0d5ce`;
official MD5 verified: `3497615fd30a24c5b35cd3b41a682e6e`.
Runtime: fairchem-core 2.23.0, Torch 2.13.0, ASE 3.26.0, NumPy 2.0.2, Python 3.12.
The initial root-level checkpoint download returned 404; authenticated inventory
resolved the correct subdirectory before any calculation ran.

Downloaded trajectories, logs, final CIFs, pilot, executed sources and hashes:
[bare-run archive](../artifacts/kaggle/uio66_bare_2026-10-03/).
[audit_uio66_relaxation.py](../scripts/audit_uio66_relaxation.py) independently
recomputed final forces/energies from saved trajectories, checked structure
hashes and CIF contact/connectivity diagnostics. Its local output is
[uio66_relaxation_audit.json](../artifacts/phase3/uio66_relaxation_audit.json).
The secret-free [Kaggle notebook](../kaggle/uio66_relaxation.ipynb) reproduces
the pilot, full two-GPU run and audit from `UIO66_Phase3_bundle.zip`.

These are model-relaxed, fixed-cell proposals, not DFT-validated structures.
Coordination cutoffs and low force do not establish chemical identity, stability,
porosity, synthesizability, adsorption quality or DAC suitability. Bare energies
across different compositions must not be ranked as adsorption objectives or
fitted into adsorption h/J. Next: chemistry review, conservative duplicate groups,
paired placement/relaxation/reference protocol, adsorption labels, held-out
pairwise-fit diagnostics and grounded solver comparisons. Phase 3 is incomplete.
