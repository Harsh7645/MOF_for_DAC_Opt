LATEST: superseded execution preparation by [QE7.5 revision2](UIO66_QE75_WATER_PILOT_V2.md). V1 package and this historical protocol remain intact below. Revision2 disables three-body D3, verifies SSSP potentials, obtains original publication CIF; no inference launched.

# Frozen-geometry DFT diagnostic: review package v1

2026-10-05. **Preparation complete; execution environment unconfirmed. No DFT or
additional UMA inference launched.** This replaces neither the failed pilot nor
the matched diagnostic. It proposes only single points on preserved coordinates.
No ionic relaxation, refitting, library expansion or material ranking is included.

Package: [uio66_frozen_dft_v1_review](../artifacts/phase3/uio66_frozen_dft_v1_review/).
The manifest, canonical trajectory/JSON geometries, inspection tables and plots,
unvalidated QE templates, result schema and missing-data assessment are included.
The earlier `uio66_frozen_dft_v1` directory is a retained preparation draft;
use **v1_review** and its release hashes for review.

## Exact geometries

All indices are zero-based. Each checkpoint trajectory contains one frame(index0).
The table's index is its exact matching frame in the complete source `path.traj`;
it also equals the recorded LBFGS step here. Atom identities, source paths,
trajectory/checkpoint SHA256, full coordinates/cell and stored energy/forces are
in `manifest.json`. Complex trajectories were copied byte-for-byte. Host structures
remove only the last three guest atoms; no relaxed host substitutes were used.

|Ordered model/gas/start|Force checkpoint(eV/A)|Source frame/step|Atoms complex/host|Archived UMA complex energy(eV)|
|---|---:|---:|---:|---:|
|110111 H2O28|0.010|59|127/124|-934.002463971617|
|110111 H2O28|0.005|230|127/124|-934.0439250522884|
|110111 CO2 7|0.020|62|127/124|-942.5495437419065|
|110111 CO2 7|0.010|294|127/124|-942.6245977001048|
|110111 CO2 7|0.005|438|127/124|-942.6384713499559|
|000000 CO2 16|0.010|78|117/114|-880.6320042753329|
|000000 CO2 16|0.005|209|117/114|-880.6497542081438|

Canonical JSON uses round-trip float serialization, with exact NumPy array equality
and geometry hashes checked after reading. Text input templates use round-trip
float representations, retain source atom order and Cartesian cell, and perform
no symmetry standardization, coordinate wrapping or repair. Display transformations
are separate files, explicitly **not DFT inputs**. Seven extracted-guest geometries
are optional only; they retain the same periodic cell and three source coordinates.

## Chemistry-inspection packet

`inspection/` contains three multi-panel XY/XZ views and Zr-aligned displacement
plots; each also has a 3D display-only trajectory. The first geometry's node,
linkers and guest are unwrapped as fragments, then each atom's image is carried
consistently to later checkpoints. Alignment subtracts mean indexed-Zr translation;
no rotation or change to the physical cell. A periodic framework cannot be represented
as one finite unbroken molecule; all boundary contacts use explicit image vectors
in the tables. Do not infer absence of a bond from a boundary cut in a picture.

- `Zr_O_contacts.csv`:336 image-explicit contacts up to3.5A, including coordination
  assessment under the existing2.8A cutoff. All six Zr retain eight O neighbors
  in all seven geometries; those distances span approximately2.056–2.279A.
- `carboxylates.csv`:84 records(12 per checkpoint), C/O atom identities, C–O
  distances, ring attachment, two ring–carboxylate torsions and image-explicit Zr
  contacts. Membership is distance-inferred; it is not a bond-order certificate.
- `node_protons.csv`:all28 node-H records(four per checkpoint), original positions,
  nearest node O, O–H length and nearby periodic N/O acceptors. O–H spans
  0.968958–0.972520A. No alternate proton placement was inserted.
- `amino.csv`:25 amino-group records, indexed C/N/H, C–N/N–H lengths, H–N–H
  angle and sum of the three angles at N. C–N spans1.361997–1.383457A;
  N–H spans1.009586–1.023444A. Per-checkpoint JSON also gives amino torsions.
- `crowding_excluding_shared_bonded_neighbor.csv`:nearest short pairs excluding
  the operational bonded pairs and pairs sharing a bonded neighbor. This avoids
  labelling ordinary within-water H···H separation as intermolecular crowding.
  Raw short nonbonded pairs, with shared-neighbor flags, remain in JSON.
- `guest_contacts.csv`:122 guest/host periodic contacts within3.5A. JSON includes
  all guest internal distances/angle and operational H-bond/contact descriptors.
  Water angles105.163→105.236degrees; CO2/start7 angles177.412→178.046→178.220;
  CO2/start16 angles179.317→179.280. Slight bending is retained for diagnosis.

The matched results already show substantial linker/amino motion for H2O28 and
CO2 7. These geometries are **preserved questionable evidence**, not repaired
structures or chemically accepted minima. Cutoff coordination and plausible
distances cannot verify protonation, electronic structure or framework stability.

### Parent comparison

The exact ordered parent arrays embedded in the original library manifest match
the archived ODAC25 export: atom numbers, positions, cell, periodicity, dataset
SHA and source index184693 all agree exactly. Metadata identifies
`jz4002345_si_002`,fid7. `parent_source.json` and `parent_audit.json` retain this
comparison and both source hashes. This checks the **export-to-library chain**.
The DOI10.1021/jz4002345 resolver was inaccessible to the web tool; the original
publication CIF has not been obtained/compared. Thus experimental parent identity,
original atom mapping, node proton locations and possible dataset preprocessing
remain questions for the professor. No claim of agreement with the publication CIF.

## Energy decomposition and archived UMA coverage

For each fixed-composition before/after pair:

```text
Delta Ecomplex = Ecomplex(after) - Ecomplex(before)
Delta Ehost = Ehost(after, guest stripped only) - Ehost(before, guest stripped only)
Delta Eguest-associated = Delta Ecomplex - Delta Ehost
```

Negative values favor the later geometry for that component. The last term includes
changed guest/framework interactions **and guest internal deformation**, plus any
consistent periodic guest-image contribution; it is not a pure binding energy.
It does not require a relaxed empty-host minimum, isolated-gas reference or ODAC25
reference-field mapping. Constant composition-dependent offsets cancel within each
same-composition difference. Never compare raw DFT and UMA total energies directly.

Optional extracted-guest single points permit
`Delta Einteraction = Delta Eguest-associated - Delta Eextracted-guest` using the
same periodic cell/convention. Calling this strictly isolated molecular deformation
would require separately converging guest-image effects in a common molecular box;
that changed setup is not silently included in the seven optional templates.

|Transition|Archived UMA Delta Ecomplex(eV)|Delta Ehost|Delta Eguest-associated|
|---|---:|---|---|
|110111 H2O28:0.010→0.005|-0.041461081|missing|missing|
|110111 CO2 7:0.020→0.010|-0.075053958|missing|missing|
|110111 CO2 7:0.010→0.005|-0.013873650|missing|missing|
|000000 CO2 16:0.010→0.005|-0.017749933|missing|missing|

Seven complex energies/forces are reusable. An exact geometry-hash search over
all matched-v2 empty/bare/gas reference trajectories and H* finds three host
single points at the **initial frame of the corresponding derived-empty trajectory**:
H2O28/0.005=-919.2642681239176eV;CO2 7/0.005=-919.2698490042077eV;
CO2 16/0.005=-857.324593826259eV. These are unrelaxed stripped-host values, not
the trajectories' relaxed endpoints. Their coordinates, cell, order, PBC, task
and checkpoint convention match exactly. Source path/hash/frame and forces retained.

**Missing mandatory UMA single points:4 hosts:**H2O28/0.010;CO2 7/0.020 and0.010;
CO2 16/0.010. All seven optional extracted-guest values are missing. No zeros,
nearby-geometry values or relaxed-bare energies were substituted; no inference launched.

## Environment and unvalidated input templates

User confirms **no code, pseudopotentials or DFT compute allocation is established**.
Local inspection found no `pw.x`,CP2K,VASP,MPI launcher,Slurm orPBS command on PATH;
WSL reports not installed. No project pseudopotential/scheduler configuration was
found in inspected project sources. This is not a scan of every institutional system.
Local CPU:Ryzen5 5500U,6cores/12threads; installed RAM16456007680bytes(~15.33GiB).
That inventory establishes neither DFT support nor suitability for these calculations.
Previous Kaggle/T4 UMA access does not establish a DFT environment or VASP license.

`templates/*.qe.in.template` are **unvalidated Quantum ESPRESSO examples only**,
not a selected execution backend. They specify fixed-cell/position SCF, forces,
PBE-D3(BJ), provisional neutral/nonmagnetic closed-shell occupation, and explicit
three-body D3 inclusion. QE documents BJ as`dftd3_version=4`; the additional
three-body choice must also be agreed and held fixed. Pseudopotential filenames,
directory and both Ry cutoffs remain mandatory placeholders. See
[official QE input specification](https://www.quantum-espresso.org/Doc/INPUT_PW.html).
All fourteen required and seven optional structures have templates; none is runnable
unchanged. No pseudopotential is fabricated, downloaded or licensed on your behalf.

Proposed neutral charge0/nonmagnetic spin and fixed occupations need expert approval
for complexes, stripped hosts and optional guests. Verify a compatible electron count
and insulating solution. If that branch is unsuitable, stop and revise all comparable
settings; do not silently change charge, smearing or spin for a difficult geometry.
For QE fixed occupations, use the converged total SCF energy including dispersion
consistently and retain force components including dispersion. Record the exact
reported quantity, code/version and corrections in the finalized adapter.

If VASP is later provided, prepare a separate validated input revision after
license/POTCAR confirmation. Its approximately600eV starting cutoff is **VASP-specific**;
do not translate it into a universal QE cutoff. VASP identifies D3(BJ) with`IVDW=12`
([official documentation](https://vasp.at/wiki/IVDW)); no VASP installation or access
is assumed in this package.

## Staged proposal and convergence scope

**Stage A: two complex-only H2O28 single points**,0.010 and0.005, serially on the
same allocation type. Measure total/SCF time, iterations, memory maximum, scratch
peak, basis size, actual CPU/GPU ranks/threads and residual electronic error.
The two results are part of the seven complexes if their final conventions are retained.

**Stage B: baseline14 components total**,seven complexes plus seven stripped hosts:
12 additional jobs after successful Stage A. No optional guests by default.

**Stage C: ten additional numerical checks**,registered before outputs:

|Check|Structures|Additional evaluations|Change|
|---|---|---:|---|
|Basis/cutoffs|H2O28 before/after,complex andhost|4|Increase both wavefunction and density cutoffs by25% from PP-reviewed baseline; hold other settings fixed|
|k mesh|Same quartet|4|Gamma1x1x1→unshifted2x2x2; same baseline cutoffs/electronic settings|
|SCF threshold|H2O28 complex pair|2|QE example1e-8→1e-10Ry total electronic threshold; corresponding code-specific settings required for another engine|

Baseline cutoffs come from the **chosen complete PP set**, including Zr semicore
and density-cutoff recommendations. No numerical baseline is invented now. The
25% increase is a first stress test, not an automatic convergence certificate.
Gamma is a trial for this fixed cell, not an established converged mesh. Keep mesh,
grid offsets, FFT/real-space treatment, D3 settings and energy convention identical
within each four-component decomposition. Tests vary one setting family at a time.

Assess changes in **Delta Ecomplex,Delta Ehost and their difference**, initially
targeting2–3meV. Compare forces by atom/group, initially targeting changes
0.005–0.01eV/A on moving guest/amino/linker atoms; also report maxima across all atoms.
Use conservative summed component numerical bounds for decomposition signs, without
assuming cancellation. The two extra SCF checks cover only complexes; baseline host
SCF diagnostics and remaining geometries still require inspection. A failed/ambiguous
check requires a revised proposal, not an automatic extra sweep. This limited
water-quartet study does not establish transferable convergence for every CO2 case.

Total proposed initial scope:**14+10=24 single points**,with Stage A included.
If changed settings must be promoted to the baseline, additional recomputation is
not hidden in24; pause and price the revised consistent set. Optional seven guests
and any further cutoff/density/k-mesh/SCF studies are separate decisions.

### Resource limits and cost measurement

No DFT wall-time prediction is available. **Do not extrapolate from UMA/T4 runtime.**
A provisional request for institutional review is one CPU node,32physical cores,
64GiB RAM and100GiB scratch, maximum4wall-hours per pilot job, two jobs serially:
an8wall-hour/256core-hour ceiling, **not an estimate or approved allocation**.
The administrator may select another supported layout before this package is finalized.
No GPU resource is required by this proposal or assumed supported by the eventual code.

Set SCF maximum200iterations. QE template `max_seconds=13800` allows orderly
retention before a proposed4h scheduler limit14400s; scheduler hard-kill remains
necessary. Use isolated job directories; no automatic retries, changed algorithms,
shared mutable restart files, repairs or ionic moves. On timeout, SCF failure,
memory/disk limit, missing forces or unexpected charge/spin, stop that stage and
retain stdout/stderr, input, PP hashes, scheduler accounting and all partial/restart
files. An unconverged energy stays recorded but cannot enter accepted differences.
Do not submit later stages while Stage A is unresolved.

After Stage A, report observed `t1,t2`,peak RAM/scratch,SCF counts and hardware.
Quote remaining work as a scenario sum over12 baseline jobs and10 checks using
the measured slower pilot as a reference, with separate scaling assumptions for
cutoff/basis and k-point changes. A2x2x2 mesh may change cost substantially; estimate
from actual irreducible/full k count and chosen parallelization, not an assumed GPU
speedup. Add an explicit safety factor and request the resulting allocation. Size
memory/scratch above measured peaks with documented headroom; revise job limits
before submission if4h would be inadequate. Never auto-extend a running budget.

## Analysis prepared; DFT results deliberately absent

`scripts/assess_uio66_frozen_dft.py` consumes normalized, provenance-bearing result
records and emits energy decompositions, missing components and grouped force
comparisons. It rejects geometry-hash changes, nonfinite/wrong-shaped forces,
missing raw-output hashes, inconsistent method/PP/energy conventions, and excludes
unconverged or ionically moved jobs. A code-specific parser must be validated once
the code is selected; a manually filled schema alone does not certify an output.

Compare UMA and DFT **differences**,not absolute totals. Compare forces at each
same exact geometry on guest, amino, moving-amino subset, rings/carboxylates and
node. Moving amino means an N/H group with any atom moving>=0.1A over a selected
checkpoint interval after Zr translation removal; all amino atoms remain reported.
Local projection directions use adjacent saved UMA frames around each checkpoint,
minimum-image displacement and removed indexed-Zr translation; frame IDs retained.
Projection is`sum(F_i dot u_i)/sqrt(sum(u_i dot u_i))`,in eV/A, with zero directions
reported missing. The direction is an **optimizer secant**,not physical diffusion,
time evolution or an activation barrier. No NEB/barrier claim follows.

- Agreement:DFT stabilization and the component attribution agree beyond assessed
  numerical uncertainty, with compatible local force projections. This is support
  for selected frozen differences, not global minima or full physical accuracy.
- Resolved disagreement:opposite stabilization sign or component/force tendency
  survives numerical checks; flag UMA/functional sensitivity for expert review.
- Residual-force issue:large converged DFT forces mean a UMA endpoint need not be a
  DFT stationary point. Retain the single-point evidence; do not relax it automatically.
- Numerically unresolved:SCF failure, varying k/cutoff results, missing components,
  or effect sizes comparable to bounds. No sign/attribution claim until resolved.

No DFT values are present. `assessment_no_dft.json` explicitly retains all14 mandatory
DFT entries as missing. The four missing UMA host energies prevent full UMA attribution.

## Exact information needed from professor/institution

1. Selected code, exact version/build and supported PBE-D3(BJ) implementation;
   agree two-body/three-body dispersion terms. Provide executable/module/container
   identifier and a working single-point invocation example. VASP requires confirmed
   institutional license/access; none is assumed.
2. Actual Zr/C/O/N/H pseudopotential or PAW files, library/version, SHA256, valence
   electrons(including Zr semicore), relativity, PBE compatibility and recommended
   wavefunction/density cutoffs; permission to use/distribute them. For another basis,
   provide its corresponding basis/grid specification.
3. Chemistry approval of parent/source mapping, four node protons, amino positional
   isomers/rotamers and neutral closed-shell branch; whether all seven questionable
   structures are meaningful diagnostic inputs. Obtain original publication CIF.
4. Exact energy quantity/occupation convention and force output, dispersion included;
   whether the nonmagnetic/fixed-occupation proposal is appropriate. Agree k-point
   grids and numerical target interpretation.
5. Compute access and scheduler(or workstation), account/partition/QOS, CPU/node
   architecture, available RAM/scratch, MPI/thread layout, hard time/storage limits,
   output-transfer location and allowed allocation. Do not send credentials in chat.
6. Review the two-job Stage A resource ceiling and failed-job retention policy;
   define who approves Stage B/C after measured runtime/SCF evidence.

### Commands available now

CPU-only regeneration(use a new output directory):

```powershell
python -m scripts.prepare_uio66_frozen_dft --output tmp/frozen_dft_review_copy
python -m scripts.assess_uio66_frozen_dft --package artifacts/phase3/uio66_frozen_dft_v1_review --records artifacts/phase3/uio66_frozen_dft_v1_review/dft_records_empty.json --output tmp/frozen_dft_missing_assessment.json
python -m pytest tests/test_frozen_dft.py -q -p no:cacheprovider --basetemp=tmp/frozen_dft_tests_new
```

**No executable DFT pilot command exists yet**,because the code/PP/allocation is
unknown. A conditional QE pattern, not ready to copy/run, is:

```text
[approved MPI launcher and ranks] [verified pw.x binary] -in [validated H2O28 complex input] > stdout.log 2> stderr.log
```

Finalize and hash the inputs, pseudopotentials, parser and scheduler script after
those details arrive, then return the exact two commands and allocation for review.
The failed pilot, historical thresholds,51/13 split and fitted scores stay intact.
ODAC25 reference-field mismatch remains separate and does not block this decomposition.
