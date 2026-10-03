# Model handoff — 2026-09-14

## Resume here

Latest verified milestone (2026-10-03): the full UiO-66 paired experiment and
provisional fitting/solver loop HAVE EXECUTED. This supersedes active-run/no-fit
notes below. Read `docs/UIO66_ADSORPTION_PROTOCOL.md`,
`docs/uio66_design_results.json` and `.planning/STATE.md`.
64/64 pairs, 512/512 starts accepted; downloaded 133,472,188-byte main archive,
SHA-256 aee36cc47cda2b2088fc30c44f7fd240bad7e5731f71932a63018c4fc6bb1837.
Remote and local trajectory/contact/connectivity/CIF/source/input audits passed.
Train-only fit: rank22, condition17.85, 51 train/13 test, 193/200 bootstrap draws
identifiable. Held-out pairwise MAE .0301754 eV vs additive .0238031 eV: pairwise
is worse. Two-vs-four-start top10 overlap .4, max delta change .135151 eV:
sampling/ranking is unstable. Do not claim validated h/J or reliable material ranking.
`data/design/uio66_uma_train_fit_v1.json` is a provisional UMA-derived heuristic
graph. CPU enumeration/Gurobi agree; SA and raw/thresholded SNN each hit the
fitted six-bit optimum 10/10. This does not establish larger-scale performance.
Main artifacts: `artifacts/kaggle/uio66_adsorption_2026-10-03/main/`;
fit/solver output: `artifacts/phase3/uio66_uma_fit/`. No GPU job remains active.
Kaggle still reports draft save failure; raw evidence and replay notebook are
local. Do not claim successful Save Version. Phase 3 overall remains incomplete.
Next independent step: separately named, uniformly expanded site-sampling study;
preserve v1 labels/split and inspect additive-vs-pairwise quality, never retune
on test labels. ODAC25 reference/training and learned-baseline gates still open.

Latest continuation (2026-10-03, paired adsorption) supersedes older counts below:
read `docs/UIO66_ADSORPTION_PROTOCOL.md` and `.planning/STATE.md`. The actual
two-state UMA pilot produced 8/8 accepted starts and two paired model targets;
downloaded evidence passed the local trajectory/contact/connectivity audit.
The full 64-state, four-start-per-gas run is ACTIVE in the existing Chrome Kaggle
notebook. Do not reload/Run All/stop it. Four workers, two per T4; outputs
`/kaggle/working/uio66_ads_full/worker*/adsorption.json`. Download and audit the
full archive before fitting. `data/design/uio66_fit_split.json` froze 53 duplicate
groups, 51 train/13 test, rank 22; both inspected pilot states are train-only.
No real h/J fit or solver comparison has executed yet. Reproducible notebook:
`kaggle/uio66_adsorption.ipynb`; bundle `artifacts/kaggle/UIO66_Adsorption_bundle.zip`.
Fit CLI: `python -m scripts.fit_uio66_adsorption --reports <four reports>
--output-dir artifacts/phase3/uio66_uma_fit`. It rejects incomplete targets and
changed protocols/splits. Then run `scripts.benchmark_uio66_fit` on fit/instance.
These are provisional UMA coefficients, never DFT-grounded validation. Phase 3
remains incomplete; frozen ODAC25 reference/training and learned-baseline gates
are unresolved. Notebook draft save conflict: backup downloaded locally; do not
reload a busy kernel. See `artifacts/kaggle/uio66_adsorption_2026-10-03/README.md`.

Current milestone (2026-10-03): read `docs/UIO66_PROVISIONAL_LIBRARY.md` and
`.planning/STATE.md`. All 64 provisional UiO-66 bare structures ran on two Kaggle
T4 GPUs with pinned UMA: 64 converged, 64 contact-free, 64 unchanged inferred
connectivity. Trajectories/CIFs/sources are downloaded to
`artifacts/kaggle/uio66_bare_2026-10-03/`; local independent audit passed.
Initial parent-operation grouping found 53 groups at 0.01/0.05 Angstrom,
64 at 1e-5. Retain initial duplicate groups for leakage safety.
39 tests pass; synthetic demo -4.6. Reproducible notebook:
`kaggle/uio66_relaxation.ipynb`. Phase 3 remains incomplete: these are bare
model energies, not paired adsorption labels or real h/J. ODAC25's 62 unmatched
reference energies and training-field mismatch still block full material scoring;
`docs/ODAC25_REFERENCE_QUESTION.md` is a local clarification draft, not sent.
Preserve frozen validation and the separate design experiment. Graphify's
`BUILD_AUDIT.json` records corpus/source freshness after refresh.

Current continuation (2026-10-02) supersedes stale counts below. Read
`.planning/STATE.md`, `docs/PHASE3_REFERENCE_AUDIT.md` and
`docs/UIO66_PROVISIONAL_LIBRARY.md` first. Phase 3 is incomplete. A fresh Kaggle
T4 run is auditing corrected total-energy versus `energy_old` adsorption
conventions and matched bare references. Preserve the notebook and download
results before ending the session. The user approved a provisional six-slot
BDC/NH2-BDC library; 64 unrelaxed CIF proposals now exist from an authenticated
ODAC25 parent with inferred periodic atom mapping. No real adsorption labels or
h/J exist. Bare-minimum matching still fails for 94 of 285 selected targets;
direct all-frame lookup completed on 189,504 rows: 62 of 67 distinct unresolved
energies have no exact stored match at 1e-5 eV. Preserve the frozen benchmark;
a separate target protocol needs explicit approval. Downloaded audit evidence is in
`artifacts/kaggle/odac25_reference_audit_2026-10-02/`.
Training mirror lacks corrected labels/fid.

Workspace: `C:/Users/hp/Documents/GitHub/MOF_for_DAC_Opt`.
Phases 1–2 and the Phase 3 frozen numerical track are complete. The paired
CO2/H2O ODAC25 validation target table has been materialized and downloaded.
Authenticated ODAC25 inventory, GCMC schema evidence and a successful 16-record
T4 UMA smoke output exist. The target-bearing shard was extracted and fully
profiled: 560,208 rows, 151 MOFs, 3,590 trajectories, 138 MOFs with pure CO2/H2O
records and 285 repeated MOF-gas groups. The deterministic exact-single-molecule,
final-frame, strongest-sampled-configuration reducer is implemented and tested.
The frozen reducer produced 285 single-gas targets and 138 paired validation
MOFs. Run non-leaking adsorption-energy baselines next; no predicted paired
ranking exists yet.
Read `.planning/STATE.md`, `docs/ODAC25_TARGET_CONTRACT.md` and
`docs/ODAC25_KAGGLE_RUNBOOK.md` for authoritative continuation state.
Use `docs/REMAINING_WORK.md` as the detailed checklist for every unfinished
Phase 3/4 deliverable and exit criterion.

Read `AGENTS.md` -> `agent.md`, this file, `.planning/STATE.md` and
`.planning/ROADMAP.md`; read `context.md` for the source-derived mathematical
contract. `chat_context.md` contains prior work/evidence. Original report text and
professor feedback are in `sources/`; do not request the originals again.

## Verified state before handoff

- NumPy/SciPy implementation exists: graph loader, Hamiltonian/QUBO construction,
  explicit linear constraints, SA, SLSQP, tiny enumeration and distance repair.
- Last recorded tests: 12 passed. Toy exact optimum -4.6; synthetic only.
  Tests were not rerun for this documentation-only handoff.
- SNN 0.6.0 and Gurobi 13.0.3 have now executed; read Phase 2/3 artifacts for the
  newer evidence. Surrogate inference, real chemistry coefficients, DFT and
  hardware measurement have not run.
- Phases 1–2 computational scopes are complete. Phase 3 is active and incomplete.
- The T4 UMA smoke run used `uma-s-1p2p1` with task `odac` and completed 16 GCMC
  structures on CUDA. Total-energy MAE was 0.0236525 eV, RMSE 0.0248619 eV and
  maximum absolute error 0.0355138 eV. Raw evidence is in
  `artifacts/kaggle/odac25_uma_t4_smoke_2026-09-12/`. This is an execution check;
  sampled paired adsorption fields were null.
- The authenticated target profile selected an 8,418,258,944-byte
  `mof_plus_adsorbate` database with SHA-256
  `2927f1ebb3af5fd4ea6e5d1072f9bdef549afa9e53ce3f0605955885da4b6c8c`.
  Persisted evidence is under
  `artifacts/kaggle/odac25_target_profile_2026-09-13/`.
- Current verification: 26 tests pass. Authenticated `paired_targets.json`
  evidence is in `artifacts/kaggle/odac25_paired_targets_2026-09-14/`.
- All project files remain untracked; no commit/push was made. Preserve files.

## Next implementation sequence

1. Preserve the frozen 138-pair validation table; do not use its labels to fit
   baselines or tune hyperparameters.
2. Materialize matching training targets/features with the same v1 rule.
3. Evaluate a mean/composition baseline and UMA adsorption-energy baseline on the
   same frozen validation records. Preserve official split boundaries.
4. Add a compatible CGCNN/MOFTransformer-family comparison or document a concrete
   target/interface incompatibility. Then produce the first material-ranking
   table with paired metrics and top-K overlap.
5. Move to Phase 4 validation, sensitivity analysis, figures and manuscript only
   after the material-ranking gate passes.

## Research leads already found (reopen before asserting details)

These are continuation leads, not a finished systematic review or proof that all
full texts were read. Prior browsing found:

- Lucas 2014, Ising formulations; equality/one-hot penalties and integer slack:
  https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2014.00005/full
- Mancoo et al. convex SNN/QP paper; inspect exact assumptions:
  https://proceedings.neurips.cc/paper_files/paper/2020/file/64714a86909d401f8feb83e8c2d94b23-Paper.pdf
- Greene-Diniz et al. 2022, MOF carbon capture via quantum electronic structure,
  not building-block QUBO: https://arxiv.org/abs/2203.15546
  https://link.springer.com/article/10.1140/epjqt/s40507-022-00155-w
- Kitai et al. 2020, factorization machines + quantum annealing for metamaterials;
  methodological analogy, not MOF study: https://www.tsudalab.org/publication/2020-kitai-designing/
- Periodic MOF quantum simulation: https://arxiv.org/abs/2510.02550 ; published
  version https://doi.org/10.1039/d6dd00023a . Distinguish VQE from annealing.
- MOFTransformer: https://www.nature.com/articles/s42256-023-00628-2
- Classical SA/NN potential orientational isomerism candidate:
  https://onlinelibrary.wiley.com/doi/10.1002/jcc.70349
- Unverified candidate for follow-up: https://arxiv.org/abs/2504.17453
- CoRE sources: https://doi.org/10.1021/acs.jced.9b00835 ;
  https://zenodo.org/records/14184621 . Structures are not ready-made block h/J.
- Possible fixed-template chemistry sources, not validated implementation:
  https://pubs.rsc.org/en/content/articlehtml/2017/cp/c6cp07801j ;
  https://www.nature.com/articles/ncomms5176 . Verify sharing/multiplicities,
  protonation and defects before assigning UiO-66 charges or building a library.

## Efficient retrieval and continuity

- Read `docs/knowledge_graph.md`; use Graphify exact-symbol `explain` first.
  Never dump the entire graph into context. Follow source pointers as needed.
- Current graph was refreshed after the October reference/structure milestone.
  `graphify-out/BUILD_AUDIT.json` contains the authoritative counts and source
  SHA-256 audit. Graph, coverage, directed imports, HTML and local links passed.
- Graphify budgets are advisory. Graph records are an index, not complete memory
  or scientific evidence. Refresh AST and semantic documents after work, audit
  freshness and preserve extracted/inferred distinctions.
- Graphify executable: `C:/Users/hp/.local/bin/graphify.exe`; Python environment:
  `C:/Users/hp/AppData/Roaming/uv/tools/graphifyy/Scripts/python.exe`.
- Prior build helper `tmp/build_graph.py` is ignored and requires regenerated
  extraction intermediates. `tmp/verify_graph.py` now checks dynamic counts and
  source SHA-256 freshness.
  Do not blindly rerun either or assume helper existence in a fresh checkout.
- Keep changes minimal, array-native and tested. No PyTorch dependency until an
  actual ML/GPU workload needs it. Apply available requested skills and RTK rules.
- Update chat_context, STATE and roadmap after each meaningful work block; record
  failures and exact next actions. Routine implementation choices can proceed;
  data access, licenses and physical measurements cannot be fabricated.
