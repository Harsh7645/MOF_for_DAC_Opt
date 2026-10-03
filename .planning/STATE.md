# Current state

Updated 2026-10-03. Phases 1 and 2 computational scopes are complete. Phase 3
numerical track is complete; its material-ranking track has authenticated ODAC25
and UMA evidence plus a frozen table of 138 paired validation targets.

Phase 2 evidence: `../docs/PHASE2_SUMMARY.md` and
`../docs/phase2_results.json`. Exact-equality convex control now converges in 251
iterations; five raw nonconvex 50-variable runs remain infeasible at strict
tolerance, while 5/5 decoded states are feasible.

Phase 3 evidence: `../docs/PHASE3_STATUS.md` and
`../docs/phase3_results.json`. Frozen seeds 100–119 were run at 12, 20 and 50 bits.
Gurobi certified 60/60 optima, exact enumeration agreed for all 40 <=20-bit
instances, 540/540 SA runs were feasible, and 60/60 decoded SNN runs were feasible.

External data decision: `../docs/dataset_decision.md`. The user has ODAC25/UMA
Hugging Face access and approved paired CO2/H2O adsorption-energy targets on
Kaggle GPU. The target contract and guarded Kaggle smoke pipeline are implemented;
the bundle includes an importable cell-by-cell Kaggle notebook. Authenticated
inventory and schema inspection succeeded on one 847,228,928-byte validation GCMC
shard (41,926 structures). Its sampled adsorption-energy fields are null. UMA on
P100 failed because Kaggle's PyTorch build lacks `sm_60`. The rerun succeeded on
one T4 for 16 structures: total-energy MAE 0.0236525 eV, RMSE 0.0248619 eV and
maximum absolute error 0.0355138 eV. Downloaded raw evidence is under
`../artifacts/kaggle/odac25_uma_t4_smoke_2026-09-12/`.

Historical verification: 26 tests passed after the September evidence update.
Current verification is in the active continuation below. Graphify's authoritative
coverage, source digests and graph integrity are recorded in
`../graphify-out/BUILD_AUDIT.json`; older graph counts are superseded.
The
T4 result validates authenticated loading and UMA execution, not paired target
quality or material ranking. All chemistry claims remain open; all reported
optimization benchmark coefficients are synthetic.

Target gate executed 2026-09-13: bounded streaming extraction selected
`val/mof_plus_adsorbate/part_00000.aselmdb` (8,418,258,944 bytes; SHA-256
`2927f1ebb3af5fd4ea6e5d1072f9bdef549afa9e53ce3f0605955885da4b6c8c`). The
authenticated full profile found 560,208 rows, 151 MOFs, 3,590 trajectories, 138
MOFs with both pure CO2/H2O records and 285 repeated MOF-gas groups. Missing/null
targets and count inconsistencies were zero.

The deterministic reduction executed on all 560,208 target-shard rows: exact
one-molecule rows, largest `fid` per trajectory, then lowest corrected adsorption
energy among final frames for each MOF/gas. It retained source index, trajectory
and fid and produced 285 single-gas targets forming 138 paired MOFs. Evidence is
under `../artifacts/kaggle/odac25_paired_targets_2026-09-14/`. The next gate is
frozen, training-only composition and UMA adsorption-energy baselines, followed
by the graph-model comparison. No predicted material ranking is claimed yet.

The detailed remaining execution plan, dependencies, artifacts and exit criteria
are maintained in `../docs/REMAINING_WORK.md`.

## Active continuation 2026-10-03

64/64 provisional UiO-66 bare structures converged on two T4 GPUs using pinned
UMA-s-1p2p1, task odac, batch inference and fixed-cell LBFGS. Tolerance 0.05
eV/Angstrom, 150-step budget; observed 0–42 steps, maximum force 0.0499344.
All were contact-free below 0.7 Angstrom with unchanged distance-inferred bonds.
Trajectories/logs/CIFs and executed sources were downloaded to
`../artifacts/kaggle/uio66_bare_2026-10-03/`. Independent local trajectory-energy,
force, source/input/output hash and CIF diagnostics passed. Bare energies alone
are not adsorption h/J or chemical validation. See
`../docs/UIO66_PROVISIONAL_LIBRARY.md` for provenance and limitations.

Initial duplicate audit: 53 parent-operation groups at 0.01 and 0.05 Angstrom,
64 at 1e-5; not a full crystallographic equivalence certificate. Retain initial
duplicate groups together for future fitting. Reproducible notebook and small
structure-bearing bundle are implemented. Relaxed grouping found 54 groups at
0.01 Angstrom and 53 at 0.05. Retain initial duplicate groups conservatively.
Full suite: 39 passed in 10.81s;
synthetic demo remains -4.6. Upstream ASE/NumPy/spglib deprecation warnings remain.

Phase 3 is incomplete. Frozen ODAC25 reference convention and training-field
mismatch remain unresolved; local `../docs/ODAC25_REFERENCE_QUESTION.md` draft
records reproducible questions and has not been sent. Next independent work:
chemistry review and paired adsorption placement/relaxation/reference protocol
for the provisional family, followed by labels, uncertainty-aware h/J fitting,
and grounded solver comparisons. Preserve the 138-pair ODAC25 benchmark.

## Historical continuation 2026-10-02

Read `../docs/PHASE3_REFERENCE_AUDIT.md` and
`../docs/UIO66_PROVISIONAL_LIBRARY.md` first. September eSEN had 68 OOM failures;
no full-pool score is valid. Fresh Kaggle T4 execution restored bounded data
and audited 2,048 spaced rows. Adsorption fields use `energy_old`: gas constants
are -22.990396 eV CO2 and -14.236396 eV H2O; sample identity spreads are below
3.3e-14 eV. Corrected total `energy` cannot replace it. Scoring now reverses
recorded system/bare k-point shifts for frozen labels: reference-assisted
evaluation on DFT-selected geometries, not prospective screening. Matched bare
references and full inference are still being verified.

Safeguards: cached-input SHA-256 binding, frozen source-index verification,
retained training provenance, progress checkpoints and average-tie Spearman
(constant ranks produce null). Notebook syntax fixed; 21 cells compiled.
Final full suite: 36 passed in 14.17 seconds. All 64 CIF roundtrip checks pass.
ASE 3.26.0 emits an upstream NumPy 2.5 shape-deprecation warning. Synthetic
demo remains energy -4.6; no SNN run in that demo.

User approved a provisional UiO-66 library: 64 nominal six-slot BDC/NH2-BDC
patterns with ideal formal charge/stoichiometry. An authenticated ODAC25 parent
was exported (index 184693, `jz4002345_si_002`, fid 7); periodic mapping found
six complete BDC linkers, and all 64 unrelaxed CIF proposals passed composition
and severe-contact checks. Symmetry deduplication, adsorption labels and real
h/J remain absent. Training-mirror
corrected-field/fid incompatibility remains a P3.1 blocker. Do not mark Phase 3
complete or move its real-grounding gate to Phase 4.

Bare-reference audit: all-frame minima gave 145 mismatches; final-frame minima
gave 94 of 285. Direct lookup over all 189,504 bare rows completed: 67 distinct
unresolved energies, 5 with exact stored matches and 62 without. The convention
or reference version needs clarification. Do not
score an altered subset or bypass the energy-identity guard. Audit archives are
downloaded under `artifacts/kaggle/odac25_reference_audit_2026-10-02/`.
