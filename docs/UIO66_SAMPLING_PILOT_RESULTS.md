# Eight-design UiO-66 pilot: verified results

Updated 2026-10-04. **Execution complete; frozen stability assessment: NO-GO for
full64 expansion.** Phase3 remains incomplete. These are provisional UMA model
calculations, not DFT validation, demonstrated DAC performance, or an SNN advantage.
No models were refitted and no new material ranking is established.

## Execution and retained evidence

Private Kaggle saved Version1, id354989784, completed on2026-10-03UTC:
[saved job](https://www.kaggle.com/code/sahuharsh/uio66-sampling-replacement-saved-pilot/log?scriptVersionId=354989784).
All **512/512 guest starts** and **16/16 registered force continuations** were
accepted. Zero recorded guest failures. Including bare, isolated-gas and
guest-removed empty references:1040 main and38 tight-force component relaxations,
all recorded converged. Failed-run handling was not needed for this completed
replacement; the earlier lost interactive attempt stays separately documented
and unverifiable in [the incident record](UIO66_PILOT_RECOVERY.md).

The archive was downloaded, matched to the saved-job SHA256, CRC-checked,
extracted with path containment, and inventoried with a hash for every raw file.
All3278 archived files are retained, including trajectories, CIFs, executed
sources, input/checkpoint identities, logs, allocation and original assessments.
Archive115,956,555bytes; uncompressed225,090,796bytes. SHA256:
`fff5aabd928c41c10cd11d0fe4472cd0d322a196fbcdf7ee424ff1838abdb374`.
The74-file execution bundle is unchanged, SHA256
`a0afe73fccbccae5b59dfb53e8005f1f0381d973ca7da6789100c66679823ddc`.
The frozen512-pose manifest and pinned UMA checkpoint passed GPU-environment
verification before inference. Historical51/13 split and fit hashes still match
the pre-run receipt. The13 viewed designs remain development evidence.

Main evidence: `artifacts/phase3/uio66_saved_pilot_results_20261004/`.
`download_verification.json` inventories raw bytes;
`assessment_equivalence.json` records exact equality of all scientific sections
of remote and local assessments. Chrome blocked the executed `.ipynb` export
with `ERR_BLOCKED_BY_CLIENT`; it has not been claimed as downloaded. The exact
pre-run notebook is frozen in the release and embedded execution bundle, and
the saved UI log rows are archived locally. No output or criterion was rebuilt
from invented data to fill that export limitation.

## Frozen scope and selection

Patterns, selected before these results: **000000,111111,110111,001001,000110,
001100,000111,010101**. Both end members;111111 was the historical sampled optimum;
110111 the fitted optimum. The three two-amino arrangements001001/000110/001100
cover matched composition and historical fitted-versus-sampled disagreements.
000111/010101 are matched three-amino arrangements. See the original
[selection and sampling protocol](UIO66_SAMPLING_PILOT_V2.md).

Each design received32CO2 and32H2O starts in two independent16-start batches.
Each batch used the same targeted-site/random-void quotas and frozen seeds/poses.
Main force tolerance0.05eV/Angstrom; four representative designs received the
registered0.02eV/Angstrom continuations. No post-result selection or thresholds.

## Frozen assessment

The initial0.01eV convergence target is an assessed design target, not a universal
physical error guarantee. Only **1/8 designs** met the complete energy criterion,
which includes Eads, paired delta, system minima and16-to32 changes.

| Pattern | Absolute CO2 batch gap,eV | Absolute H2O batch gap,eV | Absolute delta batch gap,eV | Full energy criterion |
|---|---:|---:|---:|---|
| 000000 | 0.031752 | 0.007115 | 0.024637 | Fail |
| 111111 | 0.022563 | 0.059079 | 0.081642 | Fail |
| 110111 | 0.019717 | 0.021010 | 0.001294 | Fail |
| 001001 | 0.014225 | 0.009200 | 0.005025 | Fail |
| 000110 | 0.022292 | 0.004176 | 0.026468 | Fail |
| 001100 | 0.003925 | 0.000720 | 0.003205 | Pass |
| 000111 | 0.015038 | 0.022360 | 0.037398 | Fail |
| 010101 | 0.010517 | 0.080546 | 0.091063 | Fail |

Maximum adsorption batch gap and16-to32 change:0.080546eV. Maximum paired-delta
batch gap:0.091063eV. Maximum system-minimum batch gap:0.087932eV.
Bare-reference batch differences reach0.009814eV and are retained separately;
the paired delta cancels the common bare reference.

| Ranking-stability diagnostic | Frozen requirement | Observed |
|---|---|---|
| Batch Spearman correlation | >=0.90 | 0.523810 |
| Top-two overlap | 100% | 50% |
| Decisive pair-order reversals | None | 3 |
| Top-two boundary near-tie | None | Present |

Reversal pairs:111111/110111,111111/010101,110111/010101. These describe
disagreement between computational batches, not a defensible materials ranking.

The frozen complete-link diagnostic produced509 clusters across16design/gas
groups (31-32clusters from32starts per group); only1/16 lowest clusters was seen
in both batches. This diagnostic lacks exhaustive crystal symmetry equivalence
and depends on geometric tolerances. It does not prove509 physically distinct
minima or complete adsorption-site coverage.

### Representative force comparison

All16 continuations completed; **0/4 designs** met the initial0.01eV joint
adsorption/delta criterion. These are selected-basin continuations, not a new
32-start tight-force search or a complete tight-force ranking.

| Pattern | Maximum absolute Eads shift,eV | Paired delta shift,eV | Initial target |
|---|---:|---:|---|
| 000000 | 0.032167 | +0.008034 | Fail |
| 111111 | 0.032074 | -0.003088 | Fail |
| 110111 | 0.059161 | -0.069213 | Fail |
| 001001 | 0.015917 | -0.012912 | Fail |

The110111 paired score changes by-0.069213eV despite its small loose-force batch
delta gap. Agreement between loose-force batches alone would therefore be
insufficient evidence of force convergence.

## Allocation and cost

Kaggle reports4181.1s (**69min41s**) for the saved job. The conservative receipt,
starting before upload/setup, records4282.522s (**71.38min**) to controller finish,
well below15120s/4.2h. Controller finished20:48:40UTC, wrapper20:48:46UTC, before
the23:49:17UTC deadline. Kaggle Active Events was verified atzero on resumption.

Actual GPUs: two TeslaT4,15360MiB each. UUIDs:
`GPU-992b4479-1ef8-14bf-825d-d8e45cb9b633` and
`GPU-6e0816f6-0bbb-eb9e-9217-a73926efde3a`.
Main:four workers,two/GPU,one CPU thread/worker; longest worker3076.101s.
Force stage:one worker/GPU0,450.422s. Receipt's conservative allocation accounting
is2.379GPU-hours to controller finish; it is not billed quota or utilization.
CPU-only inference performance remains unmeasured. Package identities are in
the allocation receipt (fairchem-core2.23.0,ASE3.26.0,torch2.13.0).

## Independent local verification and code change

Local CPU re-audit checked original report/input/source hashes, trajectories,
CIF correspondence, final energies/forces, fixed cell/atom order, contacts,
periodic host connectivity, frozen pose/seed identity, reference subtraction,
minima grouping, batch criteria, registered force-pose selection and tight-force
reference accounting. Every frozen scientific output section exactly matches
the remote assessment.

One safe portability change: `--report-path-map` explicitly maps the four
original Linux report paths to their downloaded Windows paths. It requires a
one-to-one mapping and identical raw SHA256 values; original reports remain
unchanged. Scientific equations, thresholds and selection rules are unchanged.
The independent local assessor hash and original frozen assessor hash are both
recorded.56tests passed24.65s; fresh workspace temporary paths were needed after
default pytest temporary/cache setup errors. Deprecation warnings remain.

Reproduce locally from the project root (no model inference):

```powershell
$pilot = 'artifacts/phase3/uio66_saved_pilot_results_20261004'
$reports = 0..3 | ForEach-Object { "$pilot/raw/uio66_sampling_authorized/worker$_/adsorption.json" }
python -m scripts.assess_uio66_sampling_pilot --reports $reports --force-report "$pilot/raw/uio66_sampling_authorized/force02/force_comparison.json" --report-path-map "$pilot/report_path_map.json" --output "$pilot/local_assessment_repeat.json"
```

Choose a new output filename for each repeat. The explicit map is machine-local;
when relocating again, map only the same four report byte streams and retain
their frozen original keys/hashes. Do not edit downloaded reports.

## Next decision and professor review

**NO-GO for full64 expansion, refitting or material-ranking claims.** The approved
replacement is complete. No additional GPU allocation or DFT was launched.

Review these specific questions with the professor/MOF expert:

1. Approve or correct the parent six-linker mapping, node hydroxyl/protonation
   and fixed NH2 regioisomers/rotamers; computational topology checks cannot do this.
2. Assess missing site classes/host or amino rotamers and the limitations of the
   cluster equivalence definition before proposing another sampling protocol.
3. Use the0.02 results to decide a scientifically justified force-convergence
   study and meaningful energy/tie tolerances. Do not relax the preregistered
   thresholds retrospectively and call this pilot a pass.
4. Review the representative DFT proposal in
   [the chemistry checklist](UIO66_CHEMISTRY_REVIEW.md) only after template/site
   review and an explicit resource allocation; its cases are development checks,
   not untouched final tests.

Any revised study requires a separately versioned protocol and compute approval.
The ODAC25 reference mismatch remains a separate unresolved workstream.
No dataset authors or professor were contacted; no publication/performance claim.
