# Matched diagnostic v2: one common tightly relaxed empty host

2026-10-04. **Review package only; no new UMA inference or GPU/DFT launch.**
This revision supersedes only the v1 rigid-control definition and scheduling.
The [v1 preparation](UIO66_MATCHED_DIAGNOSTIC.md), its manifest, notebook and
read-only release ZIP remain preserved as the previous version. The original
failed sampling pilot and thresholds remain unchanged. No refitting or expansion.

## One explicitly defined host, selected before new results

Use the existing `uio66_110111_bare` job, with124 framework atoms, no guest,
the same fixed cell, atom identities, charge0 and spin0. It is the saved endpoint
of the initial guest-free bare relaxation in replacement worker1. This choice
does not search guest-conditioned empty-host basins or select a host using new
adsorption energies.

- Frozen seed: `poses/uio66_110111_bare.traj`, SHA256
  `d7b787bd577bd7e4d24e34526d12072dd9af31ac70844d064c308529f62b9edc`.
- Original source trajectory SHA256:
  `fe2b0fbbcce60c91d87c4fca6a930e7b9c222dde84173c133198a408e49f23da`.
- Relax this seed through0.02→0.01→0.005eV/Å, one continuous LBFGS history,
 1200 total steps/20-minute path cap, same pinned UMA/ODAC settings as v1.
- Define **H\*** as the exact final complete0.005 checkpoint. H\* is a
  reproducibly specified local empty-host endpoint, not a global empty-host minimum.
- A nonconverged/missing seed blocks all four rigid paths. No alternative host,
  relaxed adsorption host, looser checkpoint, repair or fallback is allowed.
  Independent flexible paths can proceed within the original allocation.

H\* coordinates and energy **do not yet exist**. Offline checks below use its
saved seed; actual tight-host validation is a mandatory runtime prerequisite.

## Four guest mappings, fixed rules

Keep the v1 guest sources:110111 CO2 starts7 and31, H2O starts6 and28.
Keep all16 original flexible matched endpoints and four original-pose replays,
byte-for-byte; the four rigid sources remain their corresponding saved endpoints.

For each rigid source:

1. Require identical host atom species/order, cell and periodicity to H\*.
2. For corresponding Zr atoms0…5, calculate minimum-image displacements from
   source host to H\*. Translate the guest by their mean displacement.
3. Unwrap the three guest atoms about their first atom (C for CO2, O for H2O),
   preserving all internal distances and its cell-frame orientation. Replace all
   source framework coordinates with the exact H\* coordinates. No rotation,
   strain, local-site fitting, optimization or sampling is part of mapping.
4. Require finite coordinates; maximum Zr residual after translation<=0.25Å;
   minimum host–guest distance>=1.0Å; no cross-fragment covalent-cutoff edges;
   guest distances preserved within1e-9Å; guest connectivity preserved after
   periodic-image alignment; exact host coordinate/hash identity.
5. Store all four mapped geometries and check records **before any rigid guest
   relaxation**. An invalid mapping triggers a scientific hold, retaining the
   invalid pose. No nudging or replacement pose. These tests establish numerical
   geometric admissibility, not chemical validity or preservation of a motif.

Offline seed preview (all four pass):

| Source | Minimum host–guest distance | Maximum Zr residual |
|---|---:|---:|
| CO2 start7 | 1.859444Å | 0.010799Å |
| CO2 start31 | 2.877908Å | 0.010830Å |
| H2O start6 | 1.581226Å | 0.017156Å |
| H2O start28 | 1.778345Å | 0.013913Å |

All four preview hosts have geometry SHA256
`c558b4e5601c045c548c28ded54d205da776564ec340e981a2db7f83b64617b3`.
Maximum guest distance roundoff6.7e-16Å. No new cross-fragment cutoff bonds.
[Preview records](../artifacts/phase3/uio66_matched_diagnostic_v2/mapping_preview.json)
include per-pose geometry hashes; these are explicitly **not tight-host results**.

## Exact shared reference and comparisons

After the empty-host path completes, evaluate one same-model single point on
**the exact H\* coordinates**, with no constraints masking empty-host forces.
Require finite energy/forces and maximum force<0.005eV/Å. Store the host trajectory,
geometry hash, source-checkpoint hash, energy and force in
`shared_rigid_host/reference.json`. All four controls use that same reference;
do not re-relax or independently replace it for any gas/start.

For each threshold t:

`E_rigid(g,s,t) = E(H* + guest_relaxed(g,s,t)) - E(H*) - E_isolated(g,t)`.

H\* stays identical for0.02,0.01 and0.005 guest checkpoints. Only guest atoms
move. Unconstrained host forces in each complex remain reported. The assessor
verifies shared-reference provenance and exact host identity in every available
rigid checkpoint; a mismatch makes rigid energies unassessable, never silently
substituting another bare reference.

Flexible references remain as in v1: complete common bare pool per design and
tolerance, including initial bare and desorbed empty paths. These energies must
not be confused with the H\* reference. For a same-gas flexible/rigid comparison,
their **complex total-energy difference** is also their binding-energy difference
if both are explicitly expressed against H\* and the same isolated gas.
Comparing the existing flexible Eads to rigid E directly additionally includes
the difference between its common bare minimum and E(H\*).

Report each gas separately, their paired difference, each reference and each
last-checkpoint change. <=0.005eV remains an initial numerical target, not a
physical-accuracy guarantee; paired cancellation cannot hide unstable gases.

**What this can establish:** whether the selected guest poses reproducibly
relax to the same/different contact motifs and energies on **one fixed empty-host
conformation**, and how those outcomes differ from retained flexible calculations.
It removes differences between the four rigid host conformations and host-energy
references. Starting-pose sensitivity on H\* remains measurable.

**What remains confounded:** a rigid/flexible energy difference combines the
constraint, different initial host conformations, mapping/contact changes and
possibly different basins. This is not a pure causal host-freezing ablation.
Only two selected poses/gas are tested, inherited from guest-conditioned flexible
endpoints; there is no unbiased coverage or independent thermodynamic sampling.
One empty-host basin, fixed cell, protonation, amino rotamers, UMA error and
finite force tolerance remain unresolved. No material ranking, selectivity,
global minimum or explanation solely by framework flexibility follows. A true
constraint-only comparison would later need flexible replays from these exact
mapped H\*+guest geometries; **those additional paths are not included or launched**.

## Schedule, cost and retention

Counts remain **24 guest paths +24 reference relaxations =48 LBFGS paths**.
The shared host reuses an existing bare path; it adds no relaxation. Exact-host
single points reduce from four to **one**.

- GPU0:110111 bare first; common-host single point and all-four mapping checks;
  four rigid controls; ten flexible/replay paths with their ten derived empties.
  Nominal25 relaxation paths.
- GPU1:two isolated gases,000000 bare, then the other ten flexible/replay paths
  and their ten empties. Nominal23 paths; it can work while H\* is prepared.
- Host step-limit/incomplete result blocks the four rigid paths; preserve those
  entries and continue independent work. A scientific hold, worker crash or hard
  path watchdog stops model workers. Normal step-limited paths remain in all
  denominators. No automatic retry, host swap or deadline extension.
- The same **two-T4/two-hour cap** starts before notebook setup. Workers stop
  by115 minutes; five minutes are reserved for retention. Terminate both workers
  at the deadline, then retain partial trajectories, restart/checkpoint files,
  mapping/reference failures, missing-job inventory, logs and output hashes/ZIP.
  Notebook setup also stops at115 minutes; assessment gets at most the first
  half of the retention reserve. The final evidence archive uses uncompressed
  ZIP storage to reduce packaging CPU time. Platform finalization is recorded at
  execution; the reserve is not a claim that external teardown latency is known.

Archived force-study throughput remains0.203719 component seconds/step, measured
at0.02, not at0.005. Revised estimate uses the heavier25-path GPU queue:

| Average steps/path | Queue estimate, before startup/mapping/diagnostic overhead |
|---:|---:|
|100|8.49min|
|300|25.46min|
|600|50.93min|
|1200 cap|101.86min|

The former97.79-minute number assumed perfect48/2 balance. The revised schedule
exposes the mandatory host dependency and25/23 split. At1.5× measured step cost,
the cap scenario needs~153min and will stop incomplete. Completion is not promised.
Storage remains~431MB maximum trajectory estimate; reserve2GiB for outputs,
checkpoints and archives, plus checkpoint/environment caches. Mapping/reference
files add only a small amount relative to trajectories.
[Machine-readable estimate](../artifacts/phase3/uio66_matched_diagnostic_v2/cost_estimate.json).

## Package and commands for review

Verification: **71 tests passed in23.19s**, including periodic-image-invariant
guest mapping, invalid mapping rejection, one exact shared reference, host
tamper detection, dependency scheduling, unchanged flexible inputs, and a mocked
deadline that terminates both workers and archives all48 incomplete entries.
CPU validation passes all28 frozen inputs. Actual tight-host convergence and
GPU runtime validation remain pending. Existing ASE/NumPy/spglib deprecation
warnings remain; no new chemical energies were generated.

Manifest SHA256:
`33c3d63d407f0fa82e80f270a4159e0daa90ddfd8f80f26eb9a7023f102cde0a`.
Tracked copy: [data/design/uio66_matched_diagnostic_v2.json](../data/design/uio66_matched_diagnostic_v2.json).
Review notebook: `kaggle/uio66_matched_diagnostic_v2.ipynb`, **APPROVED=False**.
Read-only archive: `artifacts/phase3/UIO66_Matched_Diagnostic_v2.zip`.
Its external SHA receipt is `artifacts/phase3/uio66_matched_diagnostic_v2/package_verification.json`.

CPU-only validation:

```powershell
python -m scripts.run_uio66_matched_diagnostic --manifest artifacts/phase3/uio66_matched_diagnostic_v2/manifest.json
python -m pytest tests/test_shared_rigid_host.py tests/test_matched_diagnostic.py -q -p no:cacheprovider
```

Future reviewed execution, from the extracted v2 bundle directory (the notebook
resolves the checkpoint path and records ORIGINAL_EPOCH before setup):

```bash
python -m scripts.run_uio66_matched_diagnostic --manifest manifest.json \
  --output /kaggle/working/matched_diagnostic_results_v2 \
  --checkpoint /ABSOLUTE/PATH/TO/uma-s-1p2p1.pt \
  --execute --approved-wall-hours 2 --allocation-start-epoch ORIGINAL_EPOCH
python -m scripts.assess_uio66_matched_diagnostic --manifest manifest.json \
  --output /kaggle/working/matched_diagnostic_results_v2
```

Exact runnable orchestration is in the disabled notebook; do not start a new
GPU session or change APPROVED until this revised package is reviewed. Validate
actual GPU allocation, bundle and checkpoint hashes before inference. No DFT.
ODAC25 reference mismatch remains a separate unresolved workstream. All original
51/13 historical results and failed-pilot criteria remain intact.
