# Frozen water-complex DFT pilot: QE 7.5 revision 2

2026-10-06 environment update: see [Fedora revision 1](UIO66_QE75_FEDORA_V1.md).
QE/MPI software is built and the sealed artifacts are now verified on Fedora.
The [single initialization test](UIO66_QE75_FEDORA_INIT01_RESULTS.md) completed with
zero SCF steps. Its authorization is consumed; full SCF remains unauthorized.
The Windows environment inventory below describes the original preparation.

Preparation complete; **no DFT or UMA launched**. Professor supports the two-water
pilot once executable, pseudopotentials and allocation are verified. This revision
implements that preparation; it does not create an allocation or authorize execution.
Previous sealed v1 and all frozen coordinates remain unchanged.

Package: `artifacts/phase3/uio66_frozen_dft_v2_qe75/`.
Archive: `artifacts/phase3/UIO66_Frozen_DFT_QE75_v2.zip`.
The sibling receipt records ZIP and hash-manifest SHA256 and file count. Verify the ZIP before extraction and pin the manifest hash in the external environment config. Inside, `file_hashes.json`
covers the inputs, source, selected potentials, provenance, geometry and inspection files.

## Revision and dispersion decision

All new inputs specify:

```fortran
input_dft = 'PBE'
vdw_corr = 'grimme-d3'
dftd3_version = 4
dftd3_threebody = .false.
```

QE 7.5 documents version 4 as BJ damping and `dftd3_threebody=.false.` as retaining
only the two-body D3 contributions. This overrides QE's true default.
[Official QE 7.5 input documentation](https://www.quantum-espresso.org/Doc/INPUT_PW.html).
VASP identifies its built-in D3(BJ) route as `IVDW=12`; its support discussion
confirms the pairwise default and the differing QE default.
[VASP DFT-D3](https://vasp.at/wiki/DFT-D3),
[official VASP support discussion](https://vasp.at/forum/viewtopic.php?t=18485).

The professor's intended comparison therefore excludes the additional three-body
term. This is a dispersion-convention choice, **not evidence that QE and VASP give
identical energies or forces**. Different potentials, implementation/version,
cutoffs, integration grids and numerical settings remain relevant. The newer
external simple-DFT-D3 VASP route is not the comparison specified here. Any future
actual VASP comparison must record its version and dispersion implementation.
V1's three-body-enabled templates are historical and are not pilot inputs.

## Verified SSSP collection

Downloaded the exact **SSSP 1.3.0 PBE Precision** metadata and full 62,963,841-byte
archive from the official Materials Cloud record; did not use the site's current
default release. [Versioned official archive](https://archive.materialscloud.org/records/rcyfm-68h65),
[persistent DOI](https://doi.org/10.24435/materialscloud:f3-ym).

Published metadata MD5: `1692c5c9ce89e1c7c783f8f0eee0cbfa`.
Published archive MD5: `fde94756886f32ada7bf597547557eb5`.
Both matched. Each of the five extracted UPFs also matches the pinned metadata MD5;
local SHA256, original UPF header and metadata are retained in `pseudopotentials.json`.
All candidate filenames matched exactly; no substitutions.

|Element|File|Source family|Valence electrons|SSSP wfc/rho recommendation, Ry|
|---|---|---|---:|---:|
|Zr|Zr_pbe_v1.uspp.F.UPF|GBRV-1.2 ultrasoft|12|30 / 240|
|O|O.pbe-n-kjpaw_psl.0.1.UPF|031PAW|6|75 / 600|
|C|C.pbe-n-kjpaw_psl.1.0.0.UPF|100PAW|4|45 / 360|
|N|N.oncvpsp.upf|Dojo norm-conserving|5|80 / 320|
|H|H_ONCV_PBE-1.0.oncvpsp.upf|SG15 norm-conserving|1|80 / 320|

All headers describe scalar-relativistic potentials. Zr explicitly treats 4s2 and
4p6 semicore electrons in valence, together with 4d2/5s2; it also lists an empty 5p
channel. Its zero header cutoff fields are not usable recommendations. SSSP's
tested recommendations are distinct from generator/header estimates, all retained.
The collection combines US/PAW/NC potentials deliberately; no homogenization was made.

Starting 80/600 Ry meets the maximum of the five SSSP recommendations; 100/750 Ry
is the proposed 25% refinement. **Neither establishes convergence for these MOFs**.
The archive record specifies CC-BY-4.0; original per-potential headers and library
attribution are retained. Cite the SSSP work and underlying potential families for
publication. Full original archive is retained locally under
`data/external/sssp_1.3.0_pbe_precision/`; the review ZIP includes only the five needed
UPFs and full metadata, with original archive SHA256 recorded.

## Exact inputs and electron counting

Two pilot files, in this order:

1. `inputs/uio66_110111_H2O_s28_f0.010_complex__baseline.in`
2. `inputs/uio66_110111_H2O_s28_f0.005_complex__baseline.in`

These retain saved 110111/H2O/start28 checkpoint coordinates and cells, atom order,
and source hashes. Both contain Zr6 C48 H35 N5 O33, 127 atoms. From actual UPFs:
`6*12 + 48*4 + 35*1 + 5*5 + 33*6 = 522` electrons: 261 occupied bands for neutral,
`nspin=1`, fixed occupations. Their stripped hosts contain 514 electrons/257 bands.
An even count permits this branch; it does not prove an insulating ground state.
Stop for incompatible electronic behavior; do not silently switch charge/spin/smearing.

Inputs are ASCII/LF, fixed-position/fixed-cell `scf`, force output enabled,
`ibrav=0`, explicit symmetry disabled, initial `K_POINTS gamma`, and no ionic or cell
relaxation section. Coordinate serialization round-trips exactly through ASE for
all **31 inputs**: 14 mandatory baseline components, 7 optional guests and 10 planned
convergence variants. Original 21 canonical geometries are byte-identical to v1.
The old scientific `manifest.json` is also copied unchanged; `pilot_plan.json`
overrides its historical environment/template status for this revision.

Electronic `conv_thr=1.0d-8` is a **total estimated electronic error in Ry**, not
eV/atom and not a force criterion. The electronic refinement is `1.0d-10` Ry.
There is no ionic `forc_conv_thr` here. SCF maximum 200 iterations; QE soft stop
`max_seconds=13800`. Inputs are statically checked, **not exercised by QE**.

## Environment and bounded launch

Local inspection: Windows; no `pw.x`, MPI launcher or scheduler found on PATH;
WSL reports not installed. No accessible remote allocation/configuration was provided.
No verified executable path, version/build, MPI command, scheduler, account or
allocation exists. No installation, account creation or submission was attempted.

Request only: **one Linux CPU node, 32 physical cores, 64 GiB RAM, 100 GiB scratch**,
two jobs sequentially, maximum four hours each. Eight wall-hours / 256 core-hours is
a ceiling, not predicted usage. Initial MPI proposal: 32 ranks, one thread each.
Keep both jobs' scratch within the shared 100 GiB budget. Confirm persistent space
for outputs and partial/restart files before allocation expiry. No GPU assumed.

`environment.example.json` deliberately leaves executable path/hash, build,
MPI argv/hash, scratch path and approval references empty; allocation/execution
flags are false. Copy it outside the sealed package and fill only verified facts.
Do not edit the sealed example or guess a cluster command. A changed resource layout
requires a documented revision, not silently selecting all visible cores.

The stdlib launcher:

- Verifies package hashes, Linux, executable SHA256 and `pw.x -h` version 7.5,
  MPI launcher/build, physical cores in affinity, available RAM/disk, and explicit
  single-node binding, hard-limit and retention attestations.
- Captures executable help, build/library links, system inventory, configuration,
  exact MPI argv, unchanged input and potential copies, stdout/stderr, GNU time
  accounting, sampled process-session RSS and cumulative scratch usage.
- Uses new job directories/from-scratch SCF. At 14370 seconds sends TERM, then KILL
  after 15 seconds; no job may be accepted at or beyond 14400 seconds. The whole
  pair has a 28800-second ceiling. QE's soft stop starts earlier. No retries or
  extensions. First failed/incomplete job stops the queue; later job stays unstarted.
- Checks actual XML MPI ranks/threads, atom identities, geometry, electrons, SCF
  convergence, exit status and text/XML energies. Rejects incomplete outputs.
- Keeps failures, partial scratch, inputs, errors, XML and hash manifests. On an
  external uncatchable kill, partial files survive but final manifests may be missing;
  they are incomplete evidence, not valid comparisons.

Institutional hard memory/wall limits must be verified: sampled RSS is a conservative
sum that can double-count shared pages and miss brief peaks; GNU time's maximum RSS
is not aggregate MPI node memory. Retain scheduler/cgroup accounting for authoritative
peak memory and timeout/OOM evidence. Sampling is not a replacement for hard limits.
Scratch manifests are generated after workers stop and may require retention time;
do not delete partial scratch on a deadline. No cleanup command is supplied.

Conditional commands from the **unpacked package root**, once environment exists:

```bash
python3 scripts/run_qe_water_pilot.py --package "$PWD" --environment /verified/path/environment.json --output /persistent/path/preflight.json
# Only after allocation and execution approval; execute_approved must be true:
python3 scripts/run_qe_water_pilot.py --package "$PWD" --environment /verified/path/environment.json --output /persistent/path/water_pilot_run01 --execute
```

These are launcher commands with explicit environment/output placeholders, **not
currently executable DFT commands for this machine**. Exact MPI invocation will be
the reviewed `mpi_argv` followed by verified `pw_executable -in input.in`; no shell
evaluation, scheduler guess or automatic submission. Institution should return a
working MPI/binding command and wall/memory enforcement details before launch.

## Energy, forces and numerical assessment

Compare `Ecomplex(0.005)-Ecomplex(0.010)` against archived UMA
**-0.041461080671410855 eV**. Never compare raw absolute UMA and DFT energies.
Each accepted DFT value includes pairwise D3(BJ) once; do not add it again.
QE output XML uses Hartree atomic units, unlike stdout Ry; conversions follow
[QE 7.5 XML writer](https://github.com/QEF/q-e/blob/qe-7.5/Modules/qexsd.f90),
[force writer](https://github.com/QEF/q-e/blob/qe-7.5/Modules/qexsd_init.f90), and
[constants](https://github.com/QEF/q-e/blob/qe-7.5/Modules/constants.f90).
The parser rejects nonfinite data, geometry changes, wrong atom order/electrons,
unconverged SCF and mismatched version/allocation. Synthetic format tests have passed;
the first real QE XML/output must still be independently inspected before relying
on the adapter. XML/text format differences cause a hold, never a guessed value.

Following the two-complex pilot, review runtime, SCF behavior, basis sizes, forces,
peak memory and scratch. Price later stages from these measured DFT costs, not UMA.
No numerical accuracy or stabilization-sign conclusion from successful SCF alone.

|Stage/check|Jobs|Settings/decision|
|---|---:|---|
|Pilot now proposed|2 water complexes|80/600 Ry, Gamma, 1e-8 Ry|
|Remaining baseline, separately approved|12|Complete 7 complexes + 7 exact stripped hosts total|
|Cutoff refinement|4 water complex/host geometries|100/750 Ry, otherwise baseline|
|k-point refinement|4 same geometries|Unshifted 2x2x2, otherwise baseline|
|Electronic refinement|2 water complexes|1e-10 Ry, otherwise baseline|

14 baseline + 10 checks = 24 proposed jobs, with pilot included. Optional 7 extracted
guests are prepared but outside that scope. Ten checks isolate setting families;
they are not a full factorial convergence proof. Energy-difference changes should
initially be assessed against 2-3 meV; relevant force changes against 0.005-0.01 eV/A.
Treat those as assessment targets, not physical-accuracy guarantees. Host electronic
convergence and transfer to CO2 are still separate limitations. If raising baseline
settings is necessary, reprice consistent recomputations instead of hiding extra jobs.

Inspect every water force, all moving amino/linker atoms and each node proton, plus
group RMS/maxima and whole-structure maxima. Use exact indexed archived local motion
directions for projections; optimization secants are not physical diffusion paths.
Report energies and forces separately: favorable energy with large DFT forces does
not establish a DFT stationary point. Stable opposite energy/force tendencies flag
UMA/functional sensitivity; discrepancies at numerical uncertainty remain unresolved.

Stripped hosts allow `Delta Ehost` and
`Delta Eguest-associated = Delta Ecomplex - Delta Ehost`. The latter includes guest
deformation and interaction/image changes. All matching host inputs are ready.
Four missing UMA host single points remain separate: H2O28/0.010, CO2 7/0.020 and
0.010, CO2 16/0.010. They prevent complete UMA component attribution but **do not
block the initial DFT complex comparison**. None was inferred or calculated here.
No relaxed-bare reference or ODAC25 energy-field mapping is needed for these differences.

After downloading entire evidence and scratch trees, verify their manifests before
assessment. Normalized `records.json` can be passed to the existing assessment tool:

```bash
python3 scripts/run_qe_water_pilot.py --verify-evidence /downloaded/run --scratch /downloaded/scratch
python3 -m scripts.assess_uio66_frozen_dft --package /path/to/package --records /path/to/run/records.json --output /new/path/assessment.json
```

Relocated `raw_output` paths must be explicitly re-pointed in a **new** records copy
only after matching archived hashes. Preserve original records. The independent
assessment requires the repository analysis environment (NumPy/ASE); runner itself
is stdlib-only. No numeric uncertainty is invented; sign classification stays
unassessed until the convergence studies provide bounds.

## Original publication provenance: progress and limits

Retrieved original `jz4002345_si_002.cif` from
[ACS Figshare supplementary record](https://acs.figshare.com/articles/dataset/2022858),
[original file](https://ndownloader.figshare.com/files/3594150).
Published MD5 `dc66090fa4ba6d2d1ccb52aaa8e2314c` matches; SHA256
`b6a00ed555775ff1a9620e599852e1d9140d98fc33ce5559fcfbba66d6694618`.
Original metadata and file retained in `provenance/`.

Original CIF: 456 atoms, Zr24 C192 H112 O128, cubic 20.8663 A, P1, creation method
GDIS and block `data_calc0`. Do not call this an experimentally refined structure
without checking the paper's computational/SI description. An analysis-only primitive
cell contains 114 atoms and the same composition as the archived ODAC parent.
Primitive-volume difference is **+0.0014333%** for the archived parent; original
primitive length is about 14.75470 A with 60-degree angles. Both have four H within
1.3 A of O per primitive cell. This counts possible OH bonds; it does not prove
identical proton sites/orientations.

Only an analysis copy was reduced using spglib (no idealization); canonical inputs
were not transformed. ASE's CIF crystal-setting warning is recorded. A unique
periodic atom correspondence and original-to-ODAC frame7 transformation/relaxation
history are not established. Formula/cell/OH count agreement supports the source
lead but is not coordinate identity or chemistry approval. Amino substitutions and
their ordered rotamers remain computational models. No correction is justified or made.

## Environment handoff: still required

1. Accessible Linux host/allocation; QE **7.5** executable absolute path, SHA256,
   build/compiler/FFT/BLAS/MPI details and successful `pw.x -h` output.
2. Verified single-node MPI command and binding, launcher hash/version, actual
   32 physical cores with one thread/rank. No cluster or scheduler is assumed.
3. Explicit allocation approval/reference; scheduler/account/partition only if used;
   hard 4h/job memory enforcement, persistent evidence and scratch paths, quota,
   retention/export procedure and authoritative accounting method.
4. Professor/MOF-expert review of original/archived proton-site correspondence,
   parent preprocessing and amino rotamers; confirm neutral closed-shell fixed
   occupations for this diagnostic. Preserve the unusual geometries.
5. Review runtime preflight and exact MPI command before authorizing the two SCFs.
   Pseudopotentials and initial cutoff metadata are now verified, not missing.

No refit, ionic DFT relaxation, additional UMA inference, eight/64-design expansion
or material-ranking claim. Failed pilot, original thresholds and historical 51/13
results preserved. ODAC25 reference mismatch remains a separate unresolved workstream.

## Local validation result

Full repository suite: **91 passed in 18.49 seconds**; existing ASE/NumPy/spglib
API deprecation warnings only. Includes 15 new tests for actual pinned PP metadata,
static input conventions, XML Hartree versus stdout Ry conversion, invalid output
rejection, geometry/electron/allocation checks, unapproved-preflight blocking,
package tampering, failed-scratch retention and preservation of prior packages.
Command: `python -m pytest -q -p no:cacheprovider --basetemp=tmp/pytest_qe75_v2_final --tb=short`.
All 31 inputs passed exact position/cell/identity round trips; all 21 geometry pairs
remain byte-identical. Old package's 109 hashes and original ZIP hash verified.
Empty assessment retains 14 missing DFT results and four missing UMA host single
points. No synthetic parser fixture is a DFT result. Linux/QE/MPI integration,
actual resource enforcement and real output parsing remain untested locally.
