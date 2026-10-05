# Matched-geometry diagnostic: preregistration and offline evidence

2026-10-04. **Prepared, not executed. No new UMA inference or DFT.**
The original eight-design pilot remains failed under its original thresholds.
No refitting, full64 expansion, untouched-test claim or material ranking.
The two ordered patterns are provisional computational models.

## Verified motion in 110111 / CO2 / start31

Source: completed replacement pilot, `force02/structures/uio66_110111_tight_CO2_31.traj`.
83 saved frames, 82 steps, 17.088 seconds of recorded component runtime. All
131 replacement source files used in the main offline analysis match the original
download hash receipt. Historical raw data were read only.

| Quantity | Verified observation |
|---|---|
| Total complex energy | -942.5368909783 to -942.6105091011 eV; decrease0.07361812 eV |
| Largest one-step decrease | 0.00199642 eV; energy descent distributed over many steps |
| Maximum displacement | guest O125:0.925020 Å; C124:0.794184 Å; O126:0.712601 Å |
| Largest framework motion | L1 amino H117:0.623177 Å; N22:0.568565 Å; H116:0.486882 Å |
| Guest translation/orientation | COM0.825621 Å after Zr translation removal; axis11.362° |
| Ring rotations | L1:11.053°; L3:7.062°; L2:5.450° |
| Node-OH contact | O109-H15···O126: H···O2.860240→2.199495 Å; angle160.586→168.231° |
| Node proton bond | O109-H15 stays0.970590–0.972505 Å; OH rotation0.274° endpoint difference |
| Amino internal torsion | L1 H116:+6.512°; H117:-7.512°; no large amino rotamer flip identified |
| Connectivity | No image-aware bond-cutoff edge change in any of83 frames |
| Final maximum force | 0.01829174 eV/Å |

**Interpretation from actual coordinates:** progressive guest sliding/reorientation
toward a node-OH hydrogen-bond-like contact, accompanied by linker rocking and
amino displacement. The amino nitrogen motion is not evidence of an N-CO2 bond.
The node proton stays on its original O. No decoordination or proton transfer was
detected by the declared distance graph; these checks do not certify electronic
bonding. Force spikes occur during LBFGS steps although energy falls gradually.
The H-bond diagnostic first crosses its arbitrary distance/angle cutoffs at
step50; that label transition is not a demonstrated discontinuous physical event.
The fastest descent is around steps40–60, not a single energy jump.

The adsorption-energy change is **-0.05916147 eV**, different from the complex's
-0.07361812 eV because reference energies also change. The historical loose
endpoint and its newly evaluated first tight frame differ by about7.2e-7 eV.
The isolated trajectory cannot establish causal energy decomposition or
reproducibility. Those are questions for the matched diagnostic.

Plots inspected against the saved coordinates:

- [Energy, forces, contacts, guest position and framework motion](../artifacts/phase3/uio66_matched_diagnostic_analysis_v2/trajectory_diagnostics.png).
- [Initial/final local atomic structures, zero-based indices](../artifacts/phase3/uio66_matched_diagnostic_analysis_v2/local_structures.png).
- [Every atom's displacement](../artifacts/phase3/uio66_matched_diagnostic_analysis_v2/atom_displacements.csv).
- [Per-step numerical data](../artifacts/phase3/uio66_matched_diagnostic_analysis_v2/tight_trajectory_steps.csv),
  [contacts/H bonds](../artifacts/phase3/uio66_matched_diagnostic_analysis_v2/contact_history.json),
  [full host conformation history](../artifacts/phase3/uio66_matched_diagnostic_analysis_v2/host_conformation_history.json).

## Endpoint inventory and motif recovery

[Complete156-row table](../artifacts/phase3/uio66_matched_diagnostic_analysis_v2/all_available_endpoints.csv)
and [structured records](../artifacts/phase3/uio66_matched_diagnostic_analysis_v2/all_available_endpoints.json):
128 replacement32-start endpoints, eight tighter continuations,20 older
four-start/smoke endpoints. Every referenced endpoint trajectory is available.
Older runs and continuations are labeled separately, not independent batches.
Each record retains gas/start/batch, energy, contact atom identities, H-bond
distances/angles, fractional guest COM, orientation, ring normals, amino torsions,
node-OH vectors, geometric cavity/window label, source path and hash.

Contact descriptor: nearest eight atom pairs; motif summary includes pairs within
3.2 Å. H-bond-like diagnostic is D=N/O, A=N/O, donor-H<1.3 Å,
H···A<=2.5 Å and D-H···A>=120°. These are operational descriptors, not bond orders.
T+/T-/O and window IDs label nearest centers in an ideal fcc Zr-node template,
derived from the actual cell/node center. They are **not validated pore-accessibility
or crystallographic cage assignments**. Cell-face crossings and equivalent
framework sites require expert/symmetry review before merging motifs.

| Design/gas | Observed recovery across replacement batches |
|---|---|
| 000000 CO2 | node-OH class recurs: starts1 and16; energy gap0.031774eV; different node atom identities |
| 000000 H2O | node-OH class recurs; best opposite-batch gap0.007137eV; site/host geometries differ |
| 110111 CO2 | loose start31 lacks an H bond under the declared cutoff; its tighter endpoint approaches O109-H15, also contacted by loose start17. Same broad node-contact class does not establish same minimum |
| 110111 H2O | lowest sampled start28 has aminoNH→guest alone; that exact broad H-bond class is absent in the other batch. Start6 has a multi-contact amino/water network instead |

No verified recovery of an identical lowest physical minimum is established.
The original509 complete-link clusters remain a geometry/threshold diagnostic,
not509 proven minima. Broad contact recurrence and tight basin recurrence are
different observations. No clustering threshold has been retroactively changed
to make the failed pilot pass.

## Frozen pose selection, before new results

Selection manifest: [manifest.json](../artifacts/phase3/uio66_matched_diagnostic_v1/manifest.json),
SHA256 `536b883cb364a956422143adbec4a852994b993fb624fd831ab56c7b7b173cac`.
Within each design/gas/batch/category, choose the accepted0.05 endpoint with
lowest total complex energy; break ties by start index. Same gas/design references
are constant, so this also minimizes its recorded adsorption energy.
Copy the saved trajectory's final coordinates directly; no CIF rounding or pose
regeneration. Source trajectory SHA, report SHA, frame index, copied pose SHA and
original energy are recorded. The source starts and unusual outcomes remain intact.

| Design | Gas | Batch0 targeted | Batch0 random | Batch1 targeted | Batch1 random |
|---|---|---:|---:|---:|---:|
| 000000 | CO2 | 1 | 8 | 16 | 24 |
| 000000 | H2O | 1 | 11 | 17 | 31 |
| 110111 | CO2 | 7 | 14 | 17 | 31 |
| 110111 | H2O | 6 | 15 | 17 | 28 |

Four direct replays use frame0 of the pooled lowest selected start per design/gas:
000000/CO2:1;000000/H2O:1;110111/CO2:31;110111/H2O:28.
The four110111 rigid-host controls use the lower-energy selected endpoint in each
gas/batch:CO2 starts7,31;H2O starts6,28. Each has an exact flexible paired path.
Framework motion observed above is the preregistered justification for adding them.

## Execution protocol and references

**24 guest paths**, plus **24 reference relaxation paths** =48 nominal LBFGS paths,
and four exact fixed-host single points. No fresh adsorption positions or seeds.

- Sixteen matched and four rigid paths continue0.02→0.01→0.005eV/Å. A fresh
  LBFGS instance starts each new path; the same instance/history persists between
  thresholds. Historical pilot optimizer histories are not claimed to be resumed.
- Four original-pose replays run directly to0.005 with the same optimizer settings.
  An observer saves first crossings of0.02,0.01 and0.005 without stopping/resetting.
  A first-crossing checkpoint is not a promise forces stay below it afterward.
- Fixed cell; LBFGS maximum step0.1Å; same pinned UMA checkpoint and ODAC task,
  batch inference settings, fairchem-core2.23.0 and ASE3.26.0. Actual environment
  versions/GPU UUIDs/memory are recorded. No SNN or fitted score is involved.
- Maximum1200 cumulative optimizer steps/path, not1200 per threshold; maximum
 20 minutes/path. Incomplete paths stay in denominators; no retries/resampling.
- Two initial empty-host paths and two same-model isolated-gas paths run through
  all thresholds. Each of20 completed flexible guest paths yields an empty-host
  relaxation starting from that exact final0.005 host. At each tolerance, use
  the lowest **complete accepted common bare pool** for that design across its
  initial bare and ten desorbed paths. Incomplete reference pools make Eads
  unassessable; never substitute missing energies or import ODAC25 constants.
- Rigid controls freeze the entire host at the selected0.05 geometry and optimize
  only the guest. Their reference is a single point on that **exact frozen host**,
  plus the shared isolated gas. Report rigid interaction energies separately from
  flexible adsorption energies. Retain unconstrained host forces as well.
- Save trajectory and energy/force log every step, each threshold's exact structure,
  LBFGS restart history, elapsed time, errors and final/partial state. Missing or
  unusual structures are never silently discarded. Retain output hashes and ZIP.
- A nonfinite state, changed image-aware bond graph, cell change, rigid-host drift
  or contact below0.7Å causes a global scientific hold. These conservative flags
  may be cutoff artifacts; retain them for review. Worker crash or hard path
  watchdog stops the allocation. An ordinary step limit allows independent jobs
  to proceed within the unchanged global deadline.

ASE's optimizer preserves its state across repeated calls on the same instance;
the local harmonic test additionally verifies identical staged and uninterrupted
step trajectories. See [official ASE LBFGS source](https://docs.ase-lib.org/_modules/ase/optimize/lbfgs.html).

## Assessment frozen before execution

1. Require all intended48 paths and four rigid-host references to be present;
   list every failure/missing checkpoint explicitly. No automatic expansion.
2. Report0.02→0.01 and0.01→0.005 changes in every complex/reference total energy,
   **each gas's Eads**, and paired CO2-minus-H2O difference. The professor's
   <=0.005eV last-checkpoint change is an initial numerical diagnostic target,
   not proof of correct chemistry or UMA accuracy. Paired-score cancellation
   cannot pass unstable gas components.
3. Compare matched continuation against its original-pose direct replay using
   total energy, guest permutation-aware MIC RMSD, orientation/contact identities
   and host RMSD after Zr translation removal. Retain indexed values too.
   Reproducibility here means deterministic path/geometry robustness, not a new
   statistically independent sampling campaign. Framework symmetry is not assumed.
4. **Incomplete relaxation:** sizable checkpoint changes in the same contact/host
   arrangement suggest remaining descent. **Missed motifs:** distinct tight
   contact/site arrangements and energy differences across fixed starts suggest
   sampling coverage limits. **Host effects:** flexible/rigid paired differences,
   ring/amino motions and desorbed-host energy basins test framework contributions.
   These explanations can coexist; they are not mutually exclusive labels.
5. **Possible UMA error:** reproducibly converged unusual geometry or disagreement
   with expert-reviewed parent/protonation raises a model/structure question.
   UMA self-consistency alone cannot distinguish model error from real chemistry.
   No definitive model-error attribution without independent targeted evidence.

## Measured cost and bounded allocation proposal

[Measured cost receipt](../artifacts/phase3/uio66_matched_diagnostic_analysis_v2/measured_cost.json):
the archived force study contains38 component relaxations,1070 steps,
217.979 component-seconds and450.422 total worker-seconds. Measured average
0.203719 seconds/step includes component overhead but excludes worker startup.
Its1108 frames occupy8,277,112 bytes (~7,470 bytes/frame).

Assuming that throughput and ideal two-GPU load balance:

| Average steps across48 paths | Ideal compute time on two T4s |
|---:|---:|
| 100 | 8.15min |
| 300 | 24.45min |
| 600 | 48.89min |
| 1200 hard cap | 97.79min |

These are scenarios, **not measured0.005 convergence estimates**. Startup,
CPU connectivity checks, reference/guest atom counts, unequal path lengths,
numerical force noise and tighter relaxation can add substantial time. A1.5×
slowdown at the step cap exceeds the proposal; the run would stop incomplete.

**Proposed maximum: two T4s for two wall-hours, four allocated GPU-hours.**
Record the original start before notebook setup; never refresh it. Stop model
workers by115 minutes, reserve the last5 minutes for retention/batch finalization.
No guarantee every path finishes. Stop on scientific hold or watchdog before that.
Estimated trajectory ceiling~431MB at measured bytes/frame; reserve2GiB outputs
including archives/checkpoints, plus model and environment caches. Actual allocation
and external platform finalization must be checked at execution; this is not a bill.

## Commands and execution decision

Local verification: **64 tests passed in25.87s** (eight new diagnostic tests),
including preserved LBFGS history, rigid-host immobility/raw forces, failure/step
retention, periodic guest geometry, stratified selection and paired-score
cancellation. The28 frozen inputs pass CPU validation; the numerical regression
demo remains synthetic, oracle energy-4.6, SNN not run. ASE/NumPy and spglib
deprecation warnings remain; no GPU-runtime validation has occurred yet.
The sealed review bundle includes the archived tight start31 trajectory so its
new0.02 checkpoint can be compared directly with the historical0.02 endpoint.

Local CPU validation, safe now:

```powershell
python -m scripts.run_uio66_matched_diagnostic --manifest artifacts/phase3/uio66_matched_diagnostic_v1/manifest.json
python -m pytest tests/test_matched_diagnostic.py -q -p no:cacheprovider
```

After explicit review/approval, use the sealed bundle's own working directory
and the notebook's original allocation timestamp (never generate a replacement
timestamp for an existing run):

```bash
python -m scripts.run_uio66_matched_diagnostic --manifest manifest.json \
  --output /kaggle/working/matched_diagnostic_results \
  --checkpoint /ABSOLUTE/PATH/TO/uma-s-1p2p1.pt \
  --execute --approved-wall-hours 2 --allocation-start-epoch ORIGINAL_EPOCH
python -m scripts.assess_uio66_matched_diagnostic --manifest manifest.json \
  --output /kaggle/working/matched_diagnostic_results
```

The prepared `kaggle/uio66_matched_diagnostic.ipynb` stays `APPROVED=False`.
It verifies release/pose/checkpoint hashes and actual twoT4 allocation before
inference, accepts HF_TOKEN only via Kaggle Secrets, and packages failures too.
Use a private saved batch, not a nonpersistent interactive session. All earlier
pilot approvals concern different work; this diagnostic has not been launched.

**Decision required:** approve or revise this24-guest/24-reference/four-single-point
diagnostic and the two-hour/twoT4 cap, after reviewing the chemistry questions below.
No full64 expansion, refit or DFT is part of that decision.

## Questions for professor/MOF expert; no message sent

- Confirm the parent coordinates, six-linker periodic mapping, Zr6O4(OH)4 proton
  locations/orientations, charge and defect-free idealization for this cell.
- Are the fixed amino substitution orientations appropriate? Do modest L1 torsion
  changes and11° linker rocking stay within the intended ordered computational
  model, or is a broader rotamer library required?
- Does O109-H15···O126 at2.199Å/168° represent a reasonable CO2 adsorption contact
  in this model? NodeOH bond stayed near0.972Å; no proton transfer was detected.
- Review large linker/amino displacement, the node-contact versus amino-pocket
  water networks, and the geometric cage/window labels. No observed edge loss is
  a guarantee against subtler coordination or electronic changes.
- If tightly converged UMA still favors this rearrangement, a **later** small DFT
  comparison could evaluate the same loose/tight start31 pair and consistent
  empty/gas references, first with expert-approved protonation/cell/method.
  Compare energy difference and forces along the observed guest/linker displacement
  before contemplating more relaxations. No DFT job or universal cutoff is approved.

ODAC25 reference-field mismatch remains a separate unresolved workstream. Existing
51/13 split and historical fitted results remain unchanged; the13 viewed designs
are development evidence, not an untouched final test set.
