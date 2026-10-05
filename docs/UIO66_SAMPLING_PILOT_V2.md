# Eight-design sampling pilot v2 — preregistered 2026-10-03

Status: prepared and CPU-verified; **no new UMA calculations launched**.
Methods-focused research, with the 64-design family as a provisional case study.
No established physical ranking, fitted-score validity or SNN advantage.
Historical v1 evidence and the 51/13 split are unchanged. ODAC25's reference
mismatch remains a separate unresolved workstream.

## Fresh computational audit

`python -m scripts.audit_uio66_sampling` re-read the actual local archives.
Evidence: `artifacts/phase3/uio66_sampling_audit_v2.json`.

- Recomputed the parent mapping: six disjoint C8H4O4 linker components and one
  Zr6O8H4 node; same substitution indices and image shifts as the stored mapping.
- Rebuilt all 64 amino proposals and checked their hashed initial CIFs within
  1e-6 Å. Initial C–N/N–H distances are initialization assumptions (1.39/1.01 Å).
- Every bare host has a connected inferred periodic graph of winding rank three,
  eight O neighbors per Zr, four node H each bonded to one node O. The parent's
  six linkers bridge two node images each, giving twelve distinct node neighbors;
  each linker has a six-carbon ring and two carboxyl groups. The graph and image
  translations are in the frozen pilot manifest.
- No image-aware inferred host-edge changes from initial proposals to bare
  relaxation, or in any of the 512 adsorbed/stripped-empty relaxations. The
  historical atom-pair-only check could miss multiple/self-image edges; new v2
  acceptance adds image edges after unwrapping final atoms into the initial gauge.
- All substituted N retain one designated ring C and two H. Bare C–N distances
  1.359406–1.373136 Å; N–H 1.008496–1.017748 Å. The maximum absolute C/N/H scalar
  triple product is 0.615234 Å³: some final amino geometries are not planar.
  This is an orientation diagnostic, not a defect or chemistry verdict.
- Regenerated all 512 v1 initial guest placements within 1e-9 Å. Same seed 41
  was reused across both gases and all configurations in v1; those starts are
  not independent batches. New v2 has separate per-design/gas/batch/start streams.
- Rechecked saved trajectory/CIF composition, fixed cell, final energy/force,
  contacts, inferred bonds and energy subtraction, and archived source/input
  hashes. Same checkpoint/task throughout; isolated reference energies agree
  across workers. No system gained/lost inferred typed bond edges in v1.

Distances and graph cutoffs do not verify electronic bonding, protonation,
charge/spin, regioisomer choice, experimental structure identity or synthesis.
See [chemistry review and DFT proposal](UIO66_CHEMISTRY_REVIEW.md).

Safe code changes: added separate periodic diagnostics/stratified sampling;
enabled a supplied proposal factory and optional periodic guards in the existing
relaxation loop. Corrected the generic relaxation metadata from “bare crystal”
to component total energy. The v1 default placement, energies and acceptance
path stay unchanged; archived executed sources remain the authority for v1.

## Frozen selection — before new energies

Bits are L0…L5 in the stored mapping; 1 replaces that linker's selected H by NH2.
Indices are not spatial adjacency. These are eight distinct historical duplicate
groups, not a random statistical sample or a complete isomer library.

| Pattern | NH2 count | Reason | Historical fitted / sampled rank | Historical role |
|---|---:|---|---:|---|
| 000000 | 0 | Unfunctionalized end member; node/linker control | 14 / 23 | train |
| 111111 | 6 | Fully aminated end member; best sampled state | 5 / 1 | train |
| 110111 | 5 | Fitted optimum, different from sampled optimum | 1 / 2 | train |
| 001001 | 2 | Largest absolute historical rank disagreement | 57 / 20 | test |
| 000110 | 2 | Opposite-direction rank disagreement; matched composition | 23 / 56 | test |
| 001100 | 2 | Third two-amino slot arrangement | 25 / 52 | test |
| 000111 | 3 | Matched-composition arrangement with 010101 | 7 / 15 | test |
| 010101 | 3 | Different three-amino arrangement | 12 / 16 | train |

Selection, reasons, ranks, source/input hashes, seed identities and all 512
initial guest coordinate arrays are frozen in
[`data/design/uio66_sampling_pilot_v2.json`](../data/design/uio66_sampling_pilot_v2.json).
SHA256: `f5b4cd746c471838b141c91d88442026ab4f1bcc0bf7548d5665a8924724f68e`.
Use this file, not a new output-driven selection. CPU placement generation took
9.1905 s; a separate runner check validated 512 placements in 2.7260 s.

All 13 historical test designs have already been scored. Four enter this
development pilot deliberately. The old split remains a historical comparator;
none of its designs constitute an untouched final test set. Do not refit h/J
from these pilot outcomes and describe that as independently validated. Future
prospective testing needs a separately frozen, expert-approved unseen cohort,
preferably new MOF/template families with leakage/duplicate safeguards.

## Sampling and calculation contract

Exactly **8 × 32 × 2 = 512 guest relaxations**, plus 512 stripped-empty
relaxations, eight initial bares and isolated-gas references per worker.

For each configuration/gas: two independent 16-start batches A/B. Each batch:
two node-OH starts, two node-oxo starts, two linker-face starts, two substitution
pocket starts, eight random-void starts. Pocket class is NH2 where present and
the corresponding C–H control otherwise. All four targeted classes remain
available in both end members. Nodes are saturated in this ideal template;
“node site” does not mean an open Zr coordination site.

Targeted centers: 3.0–4.5 Å from operational anchors, with directional jitter
near OH, linker faces and substitution sites; free directions near oxo O.
All orientations use independent uniform SO(3) draws. Random centers are uniform
fractional draws. Each start has a separate SeedSequence entropy
`[20261003, configuration_index, gas_index, batch, batch_slot]`.
Rejection enforces 2 Å minimum host–guest distance, at most 2,000 proposals/start.
No silent random fallback or replacement of failed starts. These are exploratory
site heuristics, not certified adsorption sites, orientations or a uniform pore
volume measure. Review their chemically relevant coverage before the GPU pilot.

Initial gas coordinates use fixed ASE geometries. Frozen coordinates are checked
for rigidity and periodic clearance. Isolated gases are separately relaxed with
the same model; no ODAC25 DFT constants enter subtraction. Re-relax imported
bares; if frozen guest poses then clash, stop that configuration and review,
do not adaptively generate replacements.

UMA-s-1p2p1, task odac, checkpoint revision
`f611b917d9c68566bbbeccbb0aa0f7cad1696cb2`, SHA256
`b2673b85037b075674c25f55c34ffe1ff1e15db924be977b10a184765df0d5ce`.
fairchem-core 2.23.0; record every runtime package/GPU version. LBFGS, all atoms
flexible, fixed cell, maxstep 0.1 Å, **fmax 0.05 eV/Å, 400 steps** for every
system/empty. Preserve source snapshots, trajectory, final CIF, forces, time,
placement, status and failures; atomic report after each start.

`Eads = Ecombo - lowest_accepted_common_empty - Eisolated`.
Compute A, B and pooled targets with their own declared reference pools, including
desorbed empty states from both gases. Report reference shifts independently.
Delta cancels the common empty reference. These are periodic one-molecule sampled
energies, not equilibrium humidity selectivity, uptake, enthalpy or DAC performance.
The component accounting follows the
[FAIR-Chem flexible adsorption tutorial](https://facebookresearch.github.io/fairchem/adsorption-energy/);
sampling and acceptance choices are our explicit protocol.

## Minima, stability and failed-run assessment

Minima: deterministic complete-link clustering, requiring every pair in a cluster
to satisfy |ΔEcombo| ≤0.01 eV, host RMSD ≤0.15 Å and guest RMSD ≤0.35 Å.
Remove whole-system translation using the ordered framework; use periodic minimum
images and permutations of equivalent CO2 O / water H. Do not rotate the fixed
cell. Record basin members, minimum, targeted/random provenance, number of
cross-batch basins and whether both batches found the lowest basin. Unmerged
symmetry-related poses may overcount minima; no exact crystallographic basin claim.

Assess the **initial 0.01 eV target**, without assuming it is universal:

1. All 32 starts/gas must pass force, contact, intramolecular and image-aware
   host connectivity diagnostics. All eight paired targets required for ranking.
   Failures stay in 512 denominator; no successful-only subset. A failed job's
   partial trajectories/progress stay archived. Transient failures may be retried
   only from the identical frozen pose in a separately named run; no replacement.
2. For all eight, compare independent A/B gas Eads minima, reference-independent
   Ecombo minima, delta and 16→32 pooled changes. Initial energy criterion:
   every absolute change ≤0.01 eV. Report actual values even if this fails.
3. Ranking: A/B Spearman ≥0.9, exact top-two overlap, no reversed decisive pairs.
   Any gap ≤0.02 eV is a near tie. A near tie at the top-two boundary makes this
   ranking criterion inconclusive, rather than forcing arbitrary ordering.
4. Basin agreement and targeted-versus-random improvement are supporting
   diagnostics, not independent error bars. Two batches do not establish a
   statistical convergence distribution or guarantee the global minimum.
5. Perform the registered representative force check below. Passing numerical
   criteria permits chemistry/protocol review; it does not automatically authorize
   full 64-state expansion or establish material/optimizer advantage.

No-go: incomplete pairs, topology/reference failure, changes above initial target,
unresolved ranking/ties or consequential tighter-force shifts. Diagnose first.
If reference or chemistry assumptions fail, revise a separately named protocol,
preserving v1/v2 evidence. Do not tune thresholds using the historical test labels.

## Representative force check — separately budgeted

Four preregistered configurations: 000000, 111111, 110111, 001001. For each gas,
continue the lowest-energy accepted targeted and random-void starts, selected by
the rule frozen before new results. This adds **16 guest refinements**, not part
of the 512 initial starts. Use 0.02 eV/Å and 600 steps; also refine four best common
bares, two isolated gases and the 16 stripped empty states. Report component
energy shifts, reference shifts, Eads shifts and representative delta shifts,
with all failures. Assess |shift| ≤0.01 eV initially; no universal bound claimed.

This continuation tests force sensitivity around selected basins. It is not a
second full 32-start search at tight forces and can miss basins reached by
tighter optimization from original initial poses. If changes are consequential,
no-go; register a matched-initial-pose tolerance study before scaling. The force
runner audits the eight-design loose reports before loading UMA. Force results
need saved-trajectory/CIF verification before scientific use.

## Measured cost and allocation review

Archived main GPU cell: **4,386.176 s = 73.103 min**, two T4s, four single-thread
workers (two/GPU). Guest elapsed sum 13,004.808 s; empty sum 1,021.067 s; bare/gas
sum 50.021 s. Median/p90 guest 23.007/41.585 s, max 102.847 s; 29,356 guest LBFGS
steps. These are wall times inside concurrent processes, not CPU throughput or
measured utilization GPU-hours. Timing comes from the downloaded executed notebook.

Scale the selected eight historical costs by 8 (four→32 starts), then apply the
observed whole-cell overhead factor 1.2464. Nominal main pilot:
**1.109 h on two T4s/four workers**. Reserve **1.1–3.3 h**, reflecting new targeted
sites and a 400-step ceiling. Add a **25% planning allowance** for tighter-force
comparisons: total approximately **1.4–4.2 h on two T4s** (2.8–8.4 allocated
GPU-hours). The allowance is not a measured tighter-force runtime.

One T4/two workers: estimated main 2.2–6.7 h; including allowance 2.8–8.3 h.
One T4/one worker: estimated main 4.4–13.3 h, plus allowance. Concurrency scaling
is an extrapolation from the observed setup, not a speed benchmark. CPU-only UMA
throughput is unmeasured; inexpensive CPU checks do not establish it. Recommend
two T4s for this proposed allocation; no inference launch performed here.

Archived main raw files: 259,413,088 bytes (~0.24 GiB); compressed archive
133,472,188 bytes (~0.12 GiB). Plan 0.24–0.72 GiB raw main outputs; tighter study
adds storage. Reserve **2 GiB output space**, separately from checkpoint,
environment/cache and existing datasets. UMA's recorded allocator peaks ~1.6 GB
per worker exclude CUDA context/framework/other allocations; do not treat them
as total VRAM requirements. The eight-design bundle contains no token or weights.

## Reviewable execution

Local dry run (already executed; use a new path to repeat):

```powershell
python -m scripts.run_uio66_sampling_pilot --output artifacts/phase3/uio66_sampling_dry_v2_repeat/report.json
```

Build the eight-CIF replay bundle:

```powershell
python -m scripts.package_kaggle --sampling-pilot --output artifacts/kaggle/UIO66_Sampling_Pilot_v2.zip
```

Kaggle setup: extract this bundle into a new writable repository directory,
verify every `bundle_manifest.json` SHA256 entry, set `PYTHONPATH` to that root,
install fairchem-core==2.23.0 and ase==3.26.0, enable two T4s. Obtain the pinned
checkpoint through the authorized HF_TOKEN secret; never print the token.
Existing isolated/bare evidence paths in the bundle are intentional: eight CIFs
retain their frozen relative paths. No full archived database is needed.

After allocation review, four independent worker commands (run from extracted
repo root; `$CHECKPOINT` is a non-secret local pinned checkpoint path):

```bash
CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=1 python -m scripts.run_uio66_sampling_pilot --execute --checkpoint "$CHECKPOINT" --ids uio66_000000 uio66_111111 --output /kaggle/working/uio66_sampling_v2/worker0/adsorption.json
CUDA_VISIBLE_DEVICES=1 OMP_NUM_THREADS=1 python -m scripts.run_uio66_sampling_pilot --execute --checkpoint "$CHECKPOINT" --ids uio66_110111 uio66_001001 --output /kaggle/working/uio66_sampling_v2/worker1/adsorption.json
CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=1 python -m scripts.run_uio66_sampling_pilot --execute --checkpoint "$CHECKPOINT" --ids uio66_000110 uio66_001100 --output /kaggle/working/uio66_sampling_v2/worker2/adsorption.json
CUDA_VISIBLE_DEVICES=1 OMP_NUM_THREADS=1 python -m scripts.run_uio66_sampling_pilot --execute --checkpoint "$CHECKPOINT" --ids uio66_000111 uio66_010101 --output /kaggle/working/uio66_sampling_v2/worker3/adsorption.json
```

These command lines are individual concurrent processes; use the supplied
`kaggle/uio66_sampling_pilot_v2.ipynb` orchestration cells to launch together,
retain logs, wait/check exit codes and download raw evidence. Do not run them
sequentially if relying on the four-worker estimate. The runner refuses an
existing output directory and any 64-design plan or budget override.

After all four reports exist, audit/assess and then separately review force output:

```bash
python -m scripts.assess_uio66_sampling_pilot --reports /kaggle/working/uio66_sampling_v2/worker{0,1,2,3}/adsorption.json --output /kaggle/working/uio66_sampling_v2/assessment.json
CUDA_VISIBLE_DEVICES=0 OMP_NUM_THREADS=1 python -m scripts.run_uio66_sampling_pilot --execute --checkpoint "$CHECKPOINT" --refine-reports /kaggle/working/uio66_sampling_v2/worker{0,1,2,3}/adsorption.json --output /kaggle/working/uio66_sampling_v2_force02/force_comparison.json
```

The four-configuration force command shown uses **one worker/one GPU**; its time
is not expected to be divided by four. The 25% allowance above is provisional;
measured force-study timing must replace it. Preserve all raw/partial outputs.
Do not launch the 4,096-guest full study or periodic DFT at this decision point.
