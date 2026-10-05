LATEST 2026-10-05: QE7.5 frozen DFT preparation revision2 SEALED; no SCF/UMA launched.
Read docs/UIO66_QE75_WATER_PILOT_V2.md. New inputs PBE-D3(BJ),threebody=false;
verified official SSSP1.3.0PBEPrecision5UPFs,metadata/archive/individualMD5+SHA256.
80/600Ry matches maximum recommendations;100/750refinement not proven converged.
Water complex522electrons/261bands;host514/257.31exact input roundtrips;
21canonical geometries and previous109filepackage/ZIP unchanged.91tests pass18.49s.
Original publication CIF now retrieved/hashverified:456atoms,114primitive;
composition/cell agree closely;unique atom/proton correspondence still unresolved.
New package artifacts/phase3/uio66_frozen_dft_v2_qe75/;140filehashes.
ZIP UIO66_Frozen_DFT_QE75_v2.zip SHA4ea11e147c529d8b893d2131c06812ec5978b24f0c7d8905c116c22e4e6d0554.
Receipt uio66_frozen_dft_v2_qe75_receipt.json pins hash-manifest too.
Linux/QE/MPI executable/build/allocation absent;32CPU/64GiB/100GiB,2serial4hjobs
REQUEST ONLY. Guarded launcher/tests prepared;realQE/parser integration untested.
Next obtain verified environment+allocation+review,then two complexSCFs only.
Four UMAhostSP missing separately;all14DFTresults absent. Phase3 incomplete.
No ionicrelaxation/refit/64expansion/ranking. ODAC25reference mismatch separate.
Older v1 unknownPP/threebody=true/noCIF notes below historical, superseded above.

2026-10-05 latest: [frozen DFT inspection packet](UIO66_FROZEN_DFT_DIAGNOSTIC.md)
contains7exact complex checkpoints,7stripped hosts,28node-proton and84carboxylate
records, amino/crowding/contact tables and consistent periodic displacement views.
Review original parent CIF/protons/amino rotamers and charge-spin; no chemistry
approval inferred from geometric cutoffs. No DFT environment confirmed; no DFT/UMA
launched. Current proposal is SINGLE POINT ONLY; older ionic-relaxation proposal
below is historical and is not part of this scope. No ODAC reference dependence.

2026-10-05: [matched v2 results](UIO66_MATCHED_DIAGNOSTIC_V2_RESULTS.md) now available.
All48paths complete;4guest last-energy changes exceed initial5meVtarget. Review
110111 H2O/start28 L3/L5 rocking11.40/18.36deg and aminoH123 motion1.252A;
CO2/start7 guest relocation3.054A (0.02->0.01) and later L4 aminoN6 motion0.490A.
Common empty host and all4 mappings pass numerically; rigid adsorbed host forces
remain0.076-0.477eV/A. No cutoff connectivity changes flagged; no chemistry proof.
Confirm protonation/parent/amino rotamers before deciding a specific DFT frozen
geometry/force comparison. No further calculations approved; earlier proposals preserved.

2026-10-04 V2: [shared-host diagnostic revision](UIO66_MATCHED_DIAGNOSTIC_V2.md) preregisters one empty110111 host, mapping rules and remaining causal confounds. Tight host does not exist yet; seed previews pass. No GPU/DFT launched; return revised package for review.

2026-10-04 addendum: see [matched diagnostic](UIO66_MATCHED_DIAGNOSTIC.md) for actual node-OH/contact/linker motion,156endpoint inventory, and new focused expert questions. Diagnostic prepared only; no new UMA or DFT launched. Earlier DFT plans remain proposals.

Latest2026-10-04: the replacement sampling pilot is complete and failed its
frozen energy/ranking/force criteria. See [verified results](UIO66_SAMPLING_PILOT_RESULTS.md).
Review template/site/rotamer and force convergence before any expansion.
The DFT plan below remains an unsubmitted proposal; no DFT authorized.

# UiO-66 chemistry review and representative DFT proposal

Local draft for the professor; **not sent**, no DFT submitted. The methods-focused
paper may use this family only as a provisional case study. Numerical convergence
and optimizer recovery do not establish physical ranking or an SNN advantage.

## Short review checklist

1. **Parent identity:** confirm ODAC25 `jz4002345_si_002`, exported source index
   184693/fid7, against the original CIF and intended experimental UiO-66 phase.
   Approve the fixed primitive cell and six-linker L0…L5 image map. Our inferred
   graph is 12-connected with six BDC bridges; this is not crystallographic proof.
2. **Node:** approve Zr6O4(OH)4, four specific OH positions/orientations,
   neutral/closed-shell assumptions and absent defects/terminal ligands. Computer
   audit finds four O–H bonds and eight O neighbors/Zr; it cannot determine the
   correct protonation, hydration, charge or spin state.
3. **Amino identity:** each slot replaces the lowest-index aromatic H, fixing one
   positional isomer per linker. Approve those regioisomers and linker orientations.
   Planar NH2 guesses became partly pyramidal after UMA relaxation. Review paired
   ring/linker/amino rotamers; decide whether multiple rotamers must be sampled.
4. **Library meaning:** the 64 bits describe substitutions on a fixed ideal
   occupied template, not 64 verified experimentally accessible frameworks. Review
   symmetry duplicates, cell repetition, attainable amino fractions and ordering.
5. **Adsorption:** approve one neutral CO2/H2O per primitive cell, flexible atoms,
   fixed cell, site classes (node OH/oxo, linker face, NH2 or CH pocket, random void),
   2 Å initial clearance and independent orientations. There are no open Zr sites
   in this ideal node. Which missing sites/rotamers/proton-transfer pathways matter?
6. **References:** approve same-model relaxed gas plus lowest accepted common
   re-relaxed empty reference. A changing bare basin can affect Eads; delta cancels
   the common reference. Do not mix ODAC25 constants or corrected/unadjusted DFT
   totals into UMA subtraction. The ODAC25 reference question remains separate.
7. **Claims:** approve describing delta as a sampled energetic competition score,
   not humidity selectivity, capacity, regeneration energy or DAC performance.
   Decide which independent measurements/calculations a material claim would need.

Review materials: frozen v2 manifest (slots, node-image bridges, 512 initial guest
poses), parent provenance and initial/relaxed CIFs, trajectories, audit/results in
[sampling protocol](UIO66_SAMPLING_PILOT_V2.md). Record answers/approval as an
explicit revision; user authorization to develop a provisional library is not
expert chemical approval.

## Representative DFT validation proposal — approval and resources first

Preselect **000000, 111111, 110111, 001001**: end members, fitted/sample-optimum
disagreement and largest historical rank discrepancy. After the sampling pilot,
use the frozen rule “lowest accepted targeted and random-void basin per gas.”
Review geometric duplicates before counting independent basins; retain the record
if fewer distinct basins exist rather than silently substituting candidates.

Nominal inventory: 16 MOF+guest relaxations (4×2 gases×2 poses), four initial
empty relaxations, 16 guest-removed empty relaxations and two isolated gases:
**38 component relaxations**, plus convergence single points. This is a budget
proposal, not a launch or an established DFT runtime. The expert may require
additional node/amino rotamers or a smaller first smoke set.

Stage 0: approve template, node hydrogens, cell, charge/spin, pseudopotentials,
code/version/license and available cluster allocation. Two end-member triplets
are a useful first resource smoke test. Stop if chemistry/protonation changes.

Provisional settings for comparison to the ODAC methodology: periodic PBE with
D3(BJ), PAW/pseudopotentials recorded, approximately 600 eV starting cutoff,
k mesh initially `ceil(40/a) × ceil(40/b) × ceil(40/c)` in Å and spin-polarized
calculations with reviewed initialization. These are starting settings from the
[ODAC25 methodology](https://arxiv.org/html/2508.03162), not sufficient convergence
evidence or a requirement to use a particular licensed code.

Stage 1: converge cutoff and k mesh on a representative adsorbed/empty pair;
use *adsorption-energy differences*, not total-energy change alone, with 0.01 eV
as an initial assessment target. Check isolation-box dependence for CO2/H2O
(e.g. 20→30 Å, Gamma sampling; water dipole treatment reviewed). Record energy
quantity consistently (e.g. agreed zero-smearing/extrapolated energy), charge,
spin, functional and dispersion in every component. No imported k-point average
correction or mixture of energy conventions. If the initial target fails, revise
the convergence plan with the expert before further DFT.

Stage 2: positions-only relaxation at the same fixed cell, initially 0.02 eV/Å;
compare selected continuations at 0.05 versus 0.02. Record forces/steps and any
bond/protonation changes; reject unsupported reaction branches for the declared
library, while retaining them as failed/review cases. Variable-cell, defects and
hydration studies would be separate approved protocols.

Stage 3: remove each gas and relax the empty host under identical DFT settings.
Use the lowest accepted common DFT bare reference for both gases in each design,
and independently converged same-method isolated-gas references. Compute
`Eads = Ecombo - Ebare - Egas`. The
[FAIR-Chem reference procedure](https://facebookresearch.github.io/fairchem/adsorption-energy/)
motivates retaining desorption-induced empty relaxations; this proposal is not a
claim to reconstruct ODAC25's unresolved field-to-frame mapping.

Compare paired component shifts, Eads/delta MAE and maximum error, geometry/basin
changes and pair ordering with near ties explicit. Do not calibrate UMA or refit
h/J on these chosen cases and call the same cases independent final validation.
These are deliberately informative development checks. A final validation cohort
needs separate preregistration and unseen structures/labels. Existing 51/13 split
and scores stay immutable historical evidence; all 13 have already been viewed.

Go/no-go: only after expert approval, numerical/reference convergence and a
measured smoke-job cost. No periodic DFT or full 64×32×2 calculation authorized
by this draft. No dataset-author contact or publication/performance claim made.
