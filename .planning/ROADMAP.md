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

LATEST 2026-10-05: frozen-geometry DFT diagnostic REVIEW PACKAGE prepared; NO new inference.
Read docs/UIO66_FROZEN_DFT_DIAGNOSTIC.md. User confirms no DFT code/PP/compute
confirmed; no VASP access assumed. Exact7complex checkpoints+7stripped hosts+
7optional extracted guests;21roundtrips;551historicalrawhashes verified.
Inspection:336ZrOcontacts,28nodeprotons,84carboxylates,25amino records,
periodic-contact/crowding CSVs,3consistent XY/XZ+Zr-displacement figures.
UMA7complex+3exacthost energies reusable;4mandatoryhostSP and7optionalguest missing.
All DFT values absent. Proposed2watercomplexpilot,14baseline total+10checks=24SP;
no ionicrelaxation/refit/expansion. Runtime/cost unknown until actualDFTpilot.
Packet artifacts/phase3/uio66_frozen_dft_v1_review/; ZIP UIO66_Frozen_DFT_Review_v1.zip
SHA572b56a936408bc06036a29becc69b02ca2064690ed024eeefacb9ddcbd14bca;109filehashes;76tests passed30.64s.
QE inputs deliberately UNVALIDATED templates with unknownPP/cutoffs.
Next: professor/institution code/version/PP/license/charge-spin/scheduler/resources;
validate backend/parser and return exact commands/allocation for review before launch.
Phase3 incomplete; failedpilot/thresholds/51-13fit intact;ODAC25 mismatch separate.
Older matchedV2 completion and earlier proposals below retained as historical.

LATEST 2026-10-05: matched diagnostic V2 COMPLETE, saved355186088;48/48paths.
Read docs/UIO66_MATCHED_DIAGNOSTIC_V2_RESULTS.md before further Phase3 work.
Actual2T4;20min27s incl setup; workersexit0;0activeevents. No retries/repair/extension.
Raw archive local: artifacts/phase3/uio66_matched_v2_results_20261005/;
SHA b448c23d138163d46e43c6f11877f93e8465edf5996e1ef3a49f26ffe013f153.
469output+74releasehashes verified; independent frozen assessment reproduced;
4runtime common-host mappings independently reconstructed.15safetytests pass.
44/48 last-energy targets pass;4guest paths fail <=0.005eV initial target.
Start31 historical0.02 reproduction within0.000110A/0.000000717eV;
all4 final replays within0.000510eV; rigid/flexible differences remain confounded.
Incomplete relaxation and configuration sensitivity supported; UMA accuracy untested.
NO further compute/refit/full64/DFT authorized. Return results for chemistry review;
Phase3 incomplete; ODAC25 reference mismatch separate. Prior ACTIVE/prepared-only
notes below are historical. Original failedpilot/thresholds/51-13split preserved.

2026-10-04 revision: matched diagnostic V2 uses one tightly relaxed empty110111 host for4rigid controls; preparation/test/package complete, execution not authorized. See docs/UIO66_MATCHED_DIAGNOSTIC_V2.md. Phase3 incomplete.

2026-10-04 milestone: offline matched-geometry analysis and diagnostic preregistration complete; execution requires review. Phase3 remains incomplete. See docs/UIO66_MATCHED_DIAGNOSTIC.md.

# Four-phase research roadmap

Status: Phases 1–2 computational scopes complete; Phase 3 active. Retain four phases. Relative 12-week schedule from report,
not a calendar commitment. Full source-derived mapping lives in `context.md`.

## Phase 1 - Formulation & Literature (weeks 1-3)

- [x] Read supplied report and professor feedback; archive sources with hashes.
- [x] Write project memory, agent instructions, beginner guide and chat state.
- [x] Initialize graph input, explicit constraints, QUBO/relaxation conventions.
- [x] Run synthetic loop and independent numerical checks.
- [x] Freeze controlled v1 slot semantics, multiplicities, topology and charge audit; real chemistry identities remain a later evidence gate.
- [x] Draft slot-based formulation alternatives, equations and worked example.
- [x] Complete scoped Lucas study and quantum/QUBO-MOF literature comparison.
- [x] Build an instance family beyond one fixture; include difficult/infeasible cases.
- [x] Validate Stage A parameter recovery and freeze Stage B/C sourcing contract.

Exit: PASS for the controlled synthetic scope. `docs/PHASE1_SUMMARY.md` records
evidence and the open real-chemistry gate; no material validity is claimed.

## Phase 2 - Algorithm & Integration (weeks 4-6)

- [x] Run pinned lab solver on a certified convex control.
- [x] Define an explicitly experimental nonconvex route preserving raw objective and constraints.
- [x] Add convergence/failure diagnostics, start sweeps and scalable slot decoding.
- [x] Pilot 50 variables on development-only synthetic instances.

Exit: PASS for integration. `docs/PHASE2_SUMMARY.md` records failed convergence,
strict-feasibility results and limits; no solver-performance claim is made.

## Phase 3 - Scaling & Benchmarking (weeks 7-9)

Current methods-focused case-study step: eight-design32-start-per-gas replacement
pilot executed and independently audited (512+16 accepted). Frozen stability
failed: NO-GO for expansion/refitting; chemistry/site/force review next.
See `../docs/UIO66_SAMPLING_PILOT_RESULTS.md`; no new compute authorized.
Historical51/13 results preserved; no untouched-final-test claim from those13.
ODAC25 reference/training/model-comparison gates stay separate and unresolved.

- [x] Execute frozen held-out synthetic instance sets; protocol is frozen.
- [x] Materialize paired CO2/H2O candidates. Authenticated execution produced
  285 exact single-gas targets and 138 paired validation MOFs with provenance.
- [x] Implement constraint-aware SA and Gurobi references with budgets/status/bounds.
- [ ] Execute UMA ODAC baseline, then integrate a CGCNN/MOFTransformer-family comparison on the same split.
- [x] Execute development and frozen held-out quality comparisons with seed distributions and honest timing limits.

Exit: reproducible comparisons across all three report baseline categories.

Continuation 2026-10-02: material scoring requires the reference audit in
`../docs/PHASE3_REFERENCE_AUDIT.md`. Provisional library:
`../docs/UIO66_PROVISIONAL_LIBRARY.md`. Actual structures, real h/J and grounded
solver results remain Phase 3 gates. Preserve the four-phase structure.

Milestone 2026-10-03: all 64 provisional UiO-66 bare structures were model-relaxed
on two T4 GPUs and audited locally (64 converged/contact-free/unchanged inferred
bonds). Initial declared-tolerance grouping and post-relaxation grouping were
executed. Bare preparation does not close the paired adsorption, real h/J,
chemistry review or material-baseline gates. See the provisional library document.

Paired design continuation: actual two-state UMA pilot audited (8/8 starts
accepted). Full 64-state/four-start run is active. Label-independent duplicate
split is frozen (51 train/13 test, rank 22). Fit/uncertainty/CPU solver scripts
are implemented but have not executed on the full model outputs. This separate
study preserves the frozen ODAC25 benchmark and does not close chemical validation.

Completed subsequently: 64 paired targets/512 starts audited, 51/13 train/test
fit and CPU SNN/SA/Gurobi execution. Pairwise held-out error exceeds additive;
two-vs-four-start top10 overlap .4. Provisional computational path is complete;
stable/independent material validation and required learned baselines remain open.

## Phase 4 - Analysis & Drafting (weeks 10-12)

- [ ] Validate reconstructed top candidates, structure identity and DAC conditions.
- [ ] Perform affordable independent top-K validation; document unsupported claims.
- [ ] Analyze parameter sensitivity, failures, constraint/repair and solver ablations.
- [ ] Produce figures, reproducibility bundle and manuscript.

Exit: defensible material claims and scientific narrative. Hardware energy benefit
is a deployment hypothesis unless directly measured.
