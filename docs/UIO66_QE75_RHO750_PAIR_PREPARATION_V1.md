# Paired 80/750-Ry preparation v1 — 2026-10-09

**Offline preparation only. No new calculation or initialization probe authorized or launched. Local execution is a NO-GO under the unchanged memory guards.** Two frozen 80/600-Ry water SCFs are electronically converged; Phase 3, numerical convergence and physical/UMA accuracy remain unresolved.

## Inventory verified against frozen sources

Source: `artifacts/phase3/uio66_frozen_dft_v2_qe75_fedora_verified01/manifest.json`. Its hash matches the previously verified comparison receipt. Targeted checks verified all 14 baseline geometry/input file hashes against the sealed file manifest, geometry identity hashes, five UPFs, executable and the two completed input pins. The full sealed archive and prior portable archives were **not** redundantly audited or changed. Graphify is unavailable in this Fedora shell; targeted source/JSON reads were used without rebuilding or dumping the graph.

Reused independent accepted-result reviews: `evidence/qe75-first-independent-review-v6/review.json` and `evidence/qe75-second-v7/independent-audit-v2.json`. A targeted XML check reconfirmed convergence, 522 electrons, 127 atoms and the reviewed energy for each. The local QE XML inventory contains these two converged results and the unconverged initialization/625-Ry outputs; failed v3/v6 attempts are not completed baseline entries. The sealed manifest's `dft: null` fields are historical: completion status is maintained in a separate inventory, not written into the sealed package.

**14 baseline jobs = 7 complexes + 7 matching stripped hosts. Completed: 2 complexes. Remaining: 5 complexes + 7 hosts = 12.** Optional seven isolated guests are outside this baseline. The new pair is **two additional density checks**, separate from those 12 jobs and from the original ten-check convergence menu.

### All baseline manifest IDs

|Complex manifest ID|Complex state|Matching stripped-host manifest ID|Host state|
|---|---|---|---|
|`uio66_110111_H2O_s28_f0.010_complex`|Converged, first|`uio66_110111_H2O_s28_f0.010_host`|Remaining|
|`uio66_110111_H2O_s28_f0.005_complex`|Converged, second|`uio66_110111_H2O_s28_f0.005_host`|Remaining|
|`uio66_110111_CO2_s7_f0.020_complex`|Remaining|`uio66_110111_CO2_s7_f0.020_host`|Remaining|
|`uio66_110111_CO2_s7_f0.010_complex`|Remaining|`uio66_110111_CO2_s7_f0.010_host`|Remaining|
|`uio66_110111_CO2_s7_f0.005_complex`|Remaining|`uio66_110111_CO2_s7_f0.005_host`|Remaining|
|`uio66_000000_CO2_s16_f0.010_complex`|Remaining|`uio66_000000_CO2_s16_f0.010_host`|Remaining|
|`uio66_000000_CO2_s16_f0.005_complex`|Remaining|`uio66_000000_CO2_s16_f0.005_host`|Remaining|

The 110111 complexes/hosts contain 127/124 atoms; 000000 complexes/hosts 117/114. Hosts are distinct exact stripped geometries, not interchangeable relaxed references. Machine-readable IDs, sealed input paths and source-atom mappings: `plans/qe75-rho750-pair-v1/inventory.json`.

## Prepared two-job batch

Inputs are in `plans/qe75-rho750-pair-v1/inputs/`:

1. `uio66_110111_H2O_s28_f0.010_complex__rho750.in`
2. `uio66_110111_H2O_s28_f0.005_complex__rho750.in`

Each is byte-identical to its actual converged 600-Ry input **except one replacement `ecutrho=600` → `ecutrho=750`**. Frozen atoms/order/cell, SSSP 1.3.0 PBE Precision UPFs, PBE-D3(BJ), `dftd3_version=4`, threebody false, 80-Ry wavefunction cutoff, Gamma, neutral nspin=1, fixed occupations, nosym/noinv, `conv_thr=1d-8`, `mixing_beta=0.3`, CG, mixing history 4, disk_io high and force output are retained. QE max_seconds stays 12948; no explicit FFT dimension override is added. Keep the same QE/MPI build and one compute thread per rank; another host must verify compatibility rather than assume the Fedora binary runs there.

Both start clean using the same default atomic starting charge/atomic-plus-random wavefunctions, four MPI ranks and core binding. Do not reuse either 600- or 625-Ry scratch/checkpoints. Record starting charge, number of starting wavefunctions and any initialization differences from actual output; clean-start defaults do not guarantee bit-identical random coefficients across hosts/builds. Scientific comparison requires both final SCFs converged at the same threshold.

Planned separate working directories (not created or launched):

- `local/qe75-rho750-pair-v1/water01/run01/`
- `local/qe75-rho750-pair-v1/water02/run01/`

Within each, `input.in` is the corresponding pinned candidate, `pseudo/` contains the pinned five potentials, and `scratch/` is private. Identical per-geometry prefixes are safe only because their output directories are isolated. Preserve stdout, stderr, full checkpoints/XML, accounting, hashes and failures. Never overwrite the v5/v7 or diagnostic evidence.

`batch.json` explicitly has `execution_authorized=false`, `execution_enabled=false`. The old v7 launcher is consumed, input-pinned and **not a launcher for this batch**. Existing successful control checks are reused as evidence for unchanged algorithms; an adapter for a verified new allocation/target must be reviewed and only changed controls checked before executable approval. No controller changes or new dummy runs were necessary for this offline preparation.

## Laptop feasibility: do not launch

Snapshot: `evidence/qe75-rho750-preparation-v1/resources.json`, 2026-10-09 08:58:31 UTC.

|Resource|Observed / retained|
|---|---|
|Physical RAM / available|14.936 / **11.066 GiB**|
|CPU|6 physical cores, 12 logical threads; proposed jobs use 4 physical cores|
|System swap/zram|8 GiB, unused; not additional physical RAM|
|Persistent free disk|203.833 GiB|
|Power / workers|AC connected; no QE/MPI workers|
|Existing memory high / hard|**10 / 11 GiB**, unchanged|
|Job swap / tasks|0 bytes / 96, unchanged|
|Start gate|12 GiB available; snapshot short by 0.934 GiB|
|Additional existing controls|3.5-GiB total host reserve; host-available stop 0.75 GiB; memory-current stop 10.75 GiB; stop on any high/max/OOM/task event|

Completed 600-Ry peaks were **9.253384 and 9.245415 GiB**, each with zero job swap. Earlier maximum calibration anchor 9.313965 GiB is retained conservatively. Reuse `evidence/qe75-rho-diagnostic-plan-v1/source-grid-memory-audit.json`, whose source-based offline enumeration reproduced observed 600/625 grids and G counts:

|Quantity|600 Ry observed|750 Ry predicted, not measured|
|---|---:|---:|
|Dense FFT|225 × 225 × 225|**243 × 243 × 243**|
|Dense Gamma-reduced G vectors|1,902,004|**2,658,579**|
|Smooth FFT / Gamma G|160³ / 741,079|160³ / 741,079|
|Full reciprocal dense G count|3,804,007|5,317,157|

Dense FFT storage rises 25.9712%; dense G count rises about 39.78%. Source-based analytical base plus species workspace is **11.335 GiB**. Calibrated and uniform-G scaling estimates are **12.005 and 13.017 GiB**. They are sensitivity estimates, not measured peaks or rigorous bounds; FFT/PAW force workspace, allocator/cache and rank imbalance remain uncertain. Even the analytical estimate exceeds the hard cap. The calibrated range exceeds the high guard by **2.005–3.017 GiB** and hard cap by **1.005–2.017 GiB**. Changing application memory cannot fix those enforced job limits.

**Conclusion: the paired 750-Ry SCFs cannot reasonably be approved on this laptop under the existing guards. No apps were closed, limits raised or swap/power settings changed.** More laptop MemAvailable alone would not remove this blocker. Disk is adequate at present; additional checkpoints/archives must be retained and accounted for.

### Initialization probe decision

No initialization-only probe is needed or proposed now. The previously source-verified QE 7.5 `nstep=0` path returns before `init_run/electrons`; its approximately 0.79-GiB peak did not measure SCF allocations. Repeating it at 750 Ry might verify a printed grid but cannot establish safe SCF/force memory under 11 GiB. A real short SCF is a calculation requiring separate authorization, not an initialization-only substitute. Verify actual FFT/G counts in the eventual authorized larger-memory calculation.

### Candidate allocation for the next executable proposal

Obtain a **verified larger-memory host**, provisionally at least **32 GiB physical / 20 GiB available**, four physical cores, persistent free disk at least 40 GiB, no competing QE jobs. A candidate **16-GiB hard / 15-GiB high** profile with zero job swap, 96 tasks and at least 4 GiB launch headroom is a **new resource proposal only**, not applied or approved here. It leaves about 2 GiB between the upper estimate and high guard; actual demand is still uncertain. Do not transplant that profile to this 14.94-GiB laptop. The approved laptop profile remains 11/10 GiB. Stop on high/max/OOM/tasks/swap events; never increase limits following a failure. The candidate profile needs its memory guard and reserve semantics explicitly reviewed before launch.

Budget **two serial allocations of at most four hours each (8 wall-hours / 32 core-hours total)**, setup and finalization included. One clean attempt per geometry, no retry/extension. For each immutable allocation: graceful EXIT by +3h40m (QE's retained max_seconds can stop earlier); external whole-cgroup stop +3h54m45s, kill after at most 15s, workers gone by +3h55m; final five minutes for cleanup. On unexpected late resume, stop immediately against the original deadline. Temporary sleep:idle inhibition through cleanup; verify AC where applicable. Finish early on convergence. Run job 2 only after job 1 is terminal, its result/control/resource review passes and cleanup is verified; otherwise preserve the failure and hold.

Retain 20-GiB per-job scratch stop, 20-GiB free-disk stop, all outputs on stops. Observed 600-Ry scratch was 0.774 GiB per geometry; it is not a guaranteed 750-Ry bound. Each 600-Ry run took about 70.4–70.7 minutes through cleanup; increased dense storage does not translate into a reliable runtime scaling law. Four hours is a ceiling, not a completion promise.

## Predefined assessment

Full specification: `plans/qe75-rho750-pair-v1/assessment-spec.json`; exact 254-row two-geometry atom/group mapping: `force-atom-map.csv`.

Let A = f0.010 and B = f0.005. Compute using full-precision XML energies (Hartree converted consistently), independently crosschecked against final stdout:

- ΔE600 = E(B,600) − E(A,600) = **−0.03839670675722525 eV**.
- ΔE750 = E(B,750) − E(A,750).
- **δΔE = ΔE750 − ΔE600**, report signed and absolute meV. Also report each individual cutoff energy shift.

For each geometry separately, compute every corresponding force component **δF(i,α) = F750(i,α) − F600(i,α)**. Verify identical 127 atoms/order/cell/coordinates against the manifest and input/output XML; source index 0 maps to QE atom 1. Verify QE species/type mapping. Extract only the 127 total-force rows following the `Forces acting on atoms (cartesian axes, Ry/au)` header, excluding verbose component blocks that caused the historical parser error.

XML root must declare Hartree atomic units: force Ha/bohr ×2 = stdout Ry/bohr; multiply Ry/bohr by **13.605693122994017 / 0.529177210903** to get eV/Å. Preserve all 381 signed components per geometry, per-atom vector differences, maximum absolute component, group/whole maximum norm and RMS vector norm. Inspect every water atom, moving amino/linker atoms and each node proton identified from manifest group plus element. Project onto the exact archived local-motion directions; zero displacement has undefined direction, not an invented projection. These directions are optimization secants, not diffusion trajectories.

Prior independent audit's 2e-8-Å geometry serialization check and 5.1e-9 Ry / Ry-bohr text/XML rounding checks are provenance checks, **not** cutoff-acceptance tolerances. Recheck all finite forces, SCF error <1e-8 Ry, 522 electrons, final diagonalization status, XML convergence, exit/JOB DONE and resource accounting before using a result. A timeout/unconverged result provides diagnostics only, no accepted energy difference.

### Exact reviewed numerical targets — ambiguity retained

`docs/UIO66_QE75_WATER_PILOT_V2.md` states **“2-3 meV”** for energy-difference changes and **“0.005-0.01 eV/A”** for relevant force changes, explicitly assessment targets rather than physical-accuracy guarantees. `docs/UIO66_FROZEN_DFT_DIAGNOSTIC.md`, Stage C, applies the energy target to ΔEcomplex, ΔEhost and their difference, and the force range to moving guest/amino/linker atoms plus reporting maxima across all atoms.

These ranges do **not** specify one binding 2-versus-3-meV threshold, one 0.005-versus-0.01-eV/Å threshold, or a definitive component/norm/RMS aggregation. No automatic numerical pass threshold is invented. Report values below/within/above each reviewed range, separately by metric; reviewer must select the binding criterion before numerical acceptance. This two-complex pair can only assess ΔEcomplex; host/decomposition convergence remains untested.

Record initial and every SCF/final negative pseudocharge with iteration and SCF error, diagonalization warnings, actual dense/smooth FFTs and G counts. Neither 0.1 nor 0.522 electrons is an acceptance threshold. A decrease in negative pseudocharge does not prove accurate energy; no decrease does not exclude cutoff sensitivity.

This pair tests **density/augmentation resolution and its induced FFT-grid change at fixed ecutwfc=80 Ry**. It cannot separate cutoff-shell from grid-size effects, establish an asymptotic limit from two points, or establish wavefunction-cutoff, k-point, tighter-SCF-threshold, host/CO2 transfer, pseudopotential/functional or physical accuracy. Original proposed 100/750-Ry water quartet, Gamma→2×2×2 quartet and 1e-10-Ry complex pair remain separate, unlaunched proposals. The new 80/750 pair does not replace them automatically. Proton correspondence with the publication remains unresolved.

## Remaining baseline sequence and dependencies

After the numerical-protocol decision, separately approve bounded batches; no blanket baseline execution is authorized:

1. The two matching water hosts (2 jobs) unlock water ΔEhost and ΔEcomplex−ΔEhost at one consistent protocol.
2. `110111/CO2/s7`: each complex and its exact host at f0.020, f0.010, f0.005 (6 jobs). Inspect the first complex/host pair before pricing the rest.
3. `000000/CO2/s16`: each complex and exact host at f0.010, f0.005 (4 jobs).

SCFs are computationally independent; scientific differences require both endpoints and matching hosts at the same accepted PP/functional/dispersion/cutoff/k-point/spin/charge/occupation/SCF conventions, preserving each structure's atom identity and composition-dependent electron count. Use the sealed baseline templates, with reviewed CG/history/disk execution settings applied in separately versioned copies. Do not copy the water 522-electron or 127-atom checks to other compositions. No geometry relaxation. Verify each input-to-manifest roundtrip and its actual resources before launch.

Within equal compositions, ΔEguest-associated = ΔEcomplex − ΔEhost includes guest deformation and interaction/image changes; it is not an isolated adsorption energy. Optional guest references remain outside the baseline. Four missing archived UMA host single points remain separate and must not be filled by inference or launched here. Do not subtract raw total energies across different compositions as a material ranking.

If 80/600 remains accepted for the intended comparisons, keep both existing water results and use that consistent baseline for the 12 remaining jobs. If 80/750 becomes the accepted baseline, the two new converged water checks can serve as water baseline results at that protocol, and all 12 remaining jobs must use 80/750. If wavefunction cutoff, mesh or another setting changes, recalculate every result needed in each affected energy/force comparison at the common accepted settings, including water results where necessary. Never mix complex-750 with host-600 or one water endpoint at each cutoff. Preserve all historical results rather than rewriting them. Reprice additional recomputation explicitly.

The measured water times give a **rough reference of about 14.1 serial hours for 12 jobs** if their cost happened to match water. CO2, host composition, SCF difficulty and force work can change time/memory materially; this is not a forecast. A provisional four-hour ceiling per remaining job totals **48 serial wall-hours / 192 core-hours**, separately staged and approved; resource gates still apply individually. The density pair's proposed 8-hour ceiling is **additional**. No simultaneous jobs on this laptop and no allocation inferred from the old 32-core proposal.

## Commands and readiness

Run this safe offline verification from the repository root:

```bash
python scripts/check_qe75_rho750_preparation_v1.py
```

To inspect the two exact future MPI payloads and working directories, without executing them:

```bash
python - <<'PY'
import json, shlex
b = json.load(open('plans/qe75-rho750-pair-v1/batch.json'))
for j in b['jobs']:
    print(j['manifest_id'], '\n cwd:', j['work_root'])
    print(' payload:', shlex.join(j['worker_argv']))
PY
```

The payloads use `mpirun --host localhost:4 -np 4 --map-by core --bind-to core --nooversubscribe --report-bindings <pinned-pw.x> -in input.in`, OMP/OpenBLAS/MKL threads=1, with stdout/stderr retained. **They are worker commands for the future bounded controller, not standalone launch instructions.** There is deliberately no executable launch command under the current unsafe allocation. Input staging must copy the pinned candidate as `input.in` and the five pinned UPFs into each new job directory, refuse existing directories, and create private scratch only after an approved allocation begins.

**Recommendation:** procure/verify the larger-memory allocation and settle the explicit numerical acceptance rule, then finalize the bounded adapter for exactly these two pinned inputs. The next execution approval should cover this two-job serial batch, its specific verified host/resource profile and fixed per-job deadlines. Input/provenance preparation is complete; runtime readiness is blocked by memory and the unverified larger allocation. Do not request or use approval for an unsuitable laptop launch or a repeat initialization test.

Evidence: `evidence/qe75-rho750-preparation-v1/`; preparation files/hashes: `plans/qe75-rho750-pair-v1/`. No original result, sealed input, control configuration, controller test or scientific package was modified.
