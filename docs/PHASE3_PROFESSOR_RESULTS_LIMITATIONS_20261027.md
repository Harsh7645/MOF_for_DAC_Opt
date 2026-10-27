# Results and limitations — professor-review draft

27 October 2026. **Methods-focused draft; Phase 3 incomplete.** This document
consolidates saved evidence. No new fits, solver runs, QE/UMA calculations or
dataset investigation were performed. Historical artifacts are unchanged.
ODAC25 investigation remains paused; its request is **unsent**, with no contact
authorized. The evidence ledger below defines the scope of each proposed claim.

## Short results narrative

**Numerical objectives (C1–C2).** The pipeline compares feasible-solution quality
against certified synthetic references, then separately tests solvers on a fitted
UiO-66 objective. Across 60 synthetic instances, Gurobi certified all optima;
exact enumeration agreed on the 40 smaller instances. At 50 bits, SA reached the
optimum in 55/60 runs at 4,000 steps, versus 7/20 decoded SNN outputs at 2,000
iterations. These unequal budgets/starts describe the registered experiment,
not a universal solver ordering. All tested methods recovered the optimum of
the small fitted UiO-66 objective; that does not validate the objective or
demonstrate an SNN advantage. [Synthetic table](PHASE3_STATUS.md#frozen-held-out-benchmark),
[raw synthetic results](phase3_results.json), [UiO-66 solver table](uio66_design_results.json).

**Sampled UMA targets (C3–C5).** The historical 51/13 split and fits reproduce.
Historical evaluation MAE is 23.803 meV additive and 30.175 meV pairwise. New
development-only grouped CV gives median MAE 29.408 versus 33.690 meV; pairwise
is worse in 19/20 repetitions. The exception remains material: leave-group-out
RMSE favors pairwise, 38.551 versus 41.042 meV. Residuals vary by amino count and
arrangement. Coefficient/ranking instability supports **additive as a descriptive
reference, not a physically validated predictor**. The previously inspected 13
designs are historical evaluation, never a fresh untouched test.
[Fit/CV plot](../plans/uio66-offline-development-v1/results/fit_and_grouped_cv.png),
[pattern residuals](../plans/uio66-offline-development-v1/results/residual_patterns.png),
[coefficient plot](../plans/uio66-offline-development-v1/results/coefficient_stability.png).

**Sampling and relaxation (C6–C8).** Four-start labels are sensitive to sampling;
the subsequent 32-start pilot failed its frozen stability criteria. Matched-geometry
continuations reproduce the selected start 31 rearrangement numerically, while
other paths continue to change at tighter tolerances. This demonstrates limits
of sampled-target construction and convergence, not calibrated error bars or
independently verified adsorption mechanisms. [Sampling plot](../plans/uio66-offline-development-v1/results/sampling_vs_fitting.png),
[pilot tables](UIO66_SAMPLING_PILOT_RESULTS.md#frozen-assessment),
[matched energy/geometry tables](UIO66_MATCHED_DIAGNOSTIC_V2_RESULTS.md#checkpoint-energy-and-geometry-changes).

**Selected baseline DFT comparisons (C9–C10).** Seven frozen complexes and seven
matching stripped hosts have electronically converged baseline single points.
DFT and UMA agree on the direction of four selected complex-energy changes.
The decomposition below distinguishes frozen-host conformation changes from
guest-associated contributions. Cutoff/grid/k-point convergence and quantitative
UMA accuracy remain unresolved. These selected snapshots do not establish
stable material rankings. [Verified baseline table](UIO66_QE75_BASELINE14_RESULTS_V1.md#provisional-energy-differences).

**External-data boundary (C11–C12).** The 138-ID ODAC25 pool remains historical:
110 pairs match composition but lack verified parent identity, 27 have different
selected framework compositions, and EPONEE lacks its exact selected CO2 mirror
record. No corrected pair is admitted. The 62 unmatched bare-reference energies
are a separate unresolved issue. These findings constrain claims; they do not
invalidate or validate the independent same-composition DFT differences above.
[Identity table](../plans/odac25-parent-identity-v1/pair_status_v1.csv),
[identity report](ODAC25_PARENT_IDENTITY_V1.md), [request status](ODAC25_REQUEST_STATUS.json).

### Four selected energy comparisons

For earlier geometry A and later B, at the same composition:
`Delta Ec = Ec(B)-Ec(A)`; `Delta Eh = Eh(B)-Eh(A)`;
**`Delta Eg = Delta Ec - Delta Eh` (guest-associated)**.
Negative means lower energy. All entries below are **meV**, not meV/atom.
The checkpoint labels are UMA force tolerances in eV/Angstrom, not DFT thresholds.

| Pattern/gas/start; checkpoint transition | DFT Delta Ec | UMA Delta Ec | DFT Delta Eh | DFT Delta Eg |
|---|---:|---:|---:|---:|
|110111 H2O s28;0.010→0.005|−38.396707|−41.461081|−21.725487|−16.671220|
|110111 CO2 s7;0.020→0.010|−79.440623|−75.053958|+1.189612|−80.630235|
|110111 CO2 s7;0.010→0.005|−10.155191|−13.873650|−9.860710|−0.294481|
|000000 CO2 s16;0.010→0.005|−15.607560|−17.749933|−0.203710|−15.403850|

Delta Eh compares **frozen framework conformations**, not deformation relative
to an equilibrium host. Delta Eg includes interaction changes and guest internal
deformation; it is not pure binding energy. The late CO2 remainder comes from
`−10.155191 − (−9.860710) = −0.294481 meV`: near-cancellation leaves an
**unresolved sign**. Do not prioritize resolving it unless the paper needs that sign.

## Claim–evidence–scope–limitation ledger

Evidence types: **SYN** = artificial optimization objective; **UMA** = sampled
model energies/derived surrogate; **DFT0** = baseline frozen-geometry single points.
All proposed claims are bounded by the last two columns; none implies DAC performance.

|ID / proposed claim|Supporting saved evidence|Scope|Limitation / wording to exclude|
|---|---|---|---|
|C1. Synthetic solver feasibility and quality were measured against certified optima.|[phase3_results.json](phase3_results.json): `heldout.summary_by_bits`, protocol and 60 instances; Gurobi 60/60 certified; at 50 bits SA 55/60 at 4000 steps, decoded SNN 7/20.|SYN; seeds 100–119; 12/20/50 bits; synthetic energy units.|SA has 3 seeds/instance, SNN one deterministic start; decoding is distinct from raw SNN feasibility (0% at 50 bits). No universal superiority, CPU-speed or hardware-energy claim.|
|C2. Solvers recover the optimum of the saved six-bit fitted objective.|[uio66_design_results.json](uio66_design_results.json): `solver_comparison`; enumeration 64 states; Gurobi 1/1, SA 10/10, raw/threshold SNN 10/10 hits.|UMA-derived mathematical objective; not a physical objective oracle.|All methods succeed on this small instance. Indefinite relaxation is heuristic outside convex guarantees. No demonstrated SNN advantage or material optimum.|
|C3. Additive is the descriptive reference; pairwise MAE is generally worse, with an RMSE exception.|[Offline report](UIO66_OFFLINE_DEVELOPMENT_V1.md), [analysis JSON](../plans/uio66-offline-development-v1/results/analysis.json), [historical reproduction](../plans/uio66-offline-development-v1/results/historical_reproduction.json). Historical MAE 23.803/30.175; repeated grouped-CV median 29.408/33.690; leave-group-out RMSE 41.042/38.551 meV (additive/pairwise).|UMA; original 51 development patterns / 42 groups; 13 historical evaluation patterns excluded from new fitting.|No new untouched test. Repetitions overlap;19/20 is not an independent-trials p-value. Neither predictor is physically validated.|
|C4. Residuals depend on count and arrangement; additional flexibility has mixed benefits.|[Pattern CSV](../plans/uio66-offline-development-v1/results/residuals_by_pattern.csv); count table in offline report. Count 3 development OOF MAE16.709/24.360; count 5 51.811/38.757 meV.|UMA fixed labels; pattern-level descriptive diagnostics.|Counts 0/6 have one design each. Historical 13 contain 5/7/1 designs at counts 2/3/4. Error attribution is not a causal chemical mechanism; no outlier was discarded.|
|C5. Pairwise coefficients and predicted ranks are unstable under development-group resampling.|[Bootstrap records](../plans/uio66-offline-development-v1/results/bootstrap_fits.json), [rank plot](../plans/uio66-offline-development-v1/results/development_rank_stability.png).23/1000 pairwise draws rank-deficient; 14/15 J ranges cross 0; median top10 overlap 0.60 pairwise versus 0.70 additive.|UMA fixed-label, whole-group resampling; ranks restricted to 51 development patterns.|Ranges are conditional on identifiable draws and are not physical confidence intervals. Neither a range excluding 0 nor rank failure establishes a chemical interaction.|
|C6. Saved target values change with sampling effort.|[Analysis JSON](../plans/uio66-offline-development-v1/results/analysis.json): `sampling_sensitivity`; development two→four-start mean absolute paired change 15.123 meV, maximum 135.151 meV; gas components retained separately.|UMA; nested starts, common four-start bare reference.|Not independent replicate uncertainty, an error bound or equilibrium selectivity. Paired cancellation must not hide unstable components.|
|C7. The larger pilot failed its frozen stability gate.|[Pilot report](UIO66_SAMPLING_PILOT_RESULTS.md), [local assessment](../artifacts/phase3/uio66_saved_pilot_results_20261004/local_assessment.json). 512 starts; 1/8 passes full energy criterion; batch Spearman 0.523810 versus required 0.90; top-two overlap 50% versus 100%.|UMA; eight preselected patterns,32 starts/gas, frozen thresholds.|No-go for full expansion stands.509 geometric clusters are diagnostics, not509 proven physical minima; no reliable ranking.|
|C8. Selected relaxation motions are numerically reproducible but convergence is not uniform.|[Matched v2 report](UIO66_MATCHED_DIAGNOSTIC_V2_RESULTS.md), [assessment](../artifacts/phase3/uio66_matched_v2_results_20261005/local_assessment.json). 48 component paths complete; 44/48 pass initial 5-meV last-change target; start31 archived tighter endpoint reproduced within 0.000000717 eV and 0.00010998 Angstrom.|UMA; fixed matched inputs/procedure, including shared-host controls.|Four guest paths fail; numerical replay does not validate UMA. Optimization paths are not physical diffusion trajectories. Rigid/flexible differences confound host conformation, guest relaxation and interactions; no isolated causal energy attribution.|
|C9. Baseline DFT and UMA agree on directions of four selected complex-energy changes.|[Baseline14 report](UIO66_QE75_BASELINE14_RESULTS_V1.md), [Windows review](UIO66_QE75_WINDOWS_OFFLINE_REVIEW_20261010.md), table above.|DFT0: QE 7.5/PBE-D3(BJ), pairwise dispersion, SSSP 1.3.0 PBE Precision, 80/600 Ry, Gamma, 1e-8-Ry SCF; 7 complexes + 7 hosts.|SCF convergence is not numerical or physical convergence.2.14–4.39-meV DFT–UMA discrepancies are provisional, not an accuracy benchmark. Frozen snapshots are not DFT minima.|
|C10. Selected stabilization contains differing frozen-host and guest-associated contributions.|[Baseline decomposition](UIO66_QE75_BASELINE14_RESULTS_V1.md#provisional-energy-differences); explicit formulas/table above.|DFT0; same-composition differences; no isolated-gas/bare-reference subtraction needed.|Not pure binding or equilibrium-host deformation. Late CO2 approximately−0.29 meV has unresolved sign. Four missing UMA host single points prevent a complete matched UMA decomposition.|
|C11. Composition matching alone does not establish ODAC25 pairing identity.|[138-pair table](../plans/odac25-parent-identity-v1/pair_status_v1.csv), [proposal](../plans/odac25-parent-identity-v1/corrected_pool_proposal_v1.json). 110 unverified candidates, 27 conflicts, 1 incomplete; 0 admitted.|Metadata/derivative-mirror audit, not UMA fitting or DFT validation.|Original 138 preserved. Extra C1O2 and reactive trajectory names support a variant hypothesis, not authoritative row-level identity. No substitution for EPONEE.|
|C12. ODAC25 reference compatibility remains unresolved independently of identity.|[Acquisition report](ODAC25_ACQUISITION_INVESTIGATION_20261026.md), [reference audit](PHASE3_REFERENCE_AUDIT.md), [unsent request](ODAC25_PARENT_STATE_REVIEW_QUESTION_V2.md).62 unmatched bare-reference energies remain.|Released target/reference provenance; separate from the frozen same-composition DFT diagnostic.|Matching a scalar formula or reading corrected labels does not identify the reference structure or authorize fitting. Work paused; request not submitted.|

## Prioritized remaining work and dependencies

|Priority|Dependency|Minimum useful action / completion condition|
|---|---|---|
|P0|Professor decision + local writing|Approve the claim boundaries and methods-focused scope. Assemble the existing solver, surrogate and failure-diagnostic figures with reproducibility links; no new fits needed. Do not promise material discovery or acceleration.|
|P1|Professor/MOF expert review|Resolve or explicitly retain assumptions about original-parent/proton correspondence, amino orientations/rotamers and observed framework rearrangements. Review [chemistry questions](UIO66_CHEMISTRY_REVIEW.md) and [frozen inspection packet](UIO66_FROZEN_DFT_DIAGNOSTIC.md). Dated pre-DFT status text there is historical; baseline 14 is the current completed state.|
|P1|Professor confirmation + local preparation|Confirm the reconstructed energy-sensitivity algebra in [convergence v2.1](UIO66_QE75_WATER_CONVERGENCE_V2.md#reviewer-clarification-and-remaining-formula-provenance). Thresholds/comparison routes are registered; algebra was reconstructed from a malformed table, not quoted.|
|P2|Larger-memory CPU environment + separate execution approval|Identify actual machine/QE build/MPI/resources. Immediate next evidence: two frozen water complexes at 80/750 Ry, preserving other settings and reading actual FFT grids. Reproduce 80/600 water pair first if machine or build changes. Water-only checks do not validate hosts or CO2.|
|P3|Conditional numerical-compute scope|If quantitative claims retain all four DFT decompositions, justify convergence coverage of their complexes and hosts under a common protocol.100/750,120/750 and density toward900 remain conditional; tighter SCF/k-points are separate. No automatic calculation ladder.|
|Separate hold|Source-side identity/reference response|Keep ODAC25 investigation paused and request unsent until the user confirms submission. Needed: authoritative parent/state/family and reference links, original tags, exact EPONEE frame; then the [small complete training export](../plans/odac25-parent-identity-v1/TRAINING_EXPORT_REQUIREMENTS.md). No new fitting before compatibility/leakage gates.|
|Conditional, only if paper scope requires it|Separate UMA-inference authorization|Four exact-geometry missing host single points could complete the selected UMA decomposition. They do not block the existing complex comparison and would not settle DFT convergence. No inference is authorized here.|

**Compute request, not availability or runtime prediction:** the prepared workstation
profile is at least 32 GiB physical RAM / 24 GiB available, 20-GiB aggregate hard cap,
18-GiB graceful-stop trigger, zero job swap, four physical cores/four bound MPI
ranks/one thread each, preferably 100 GiB usable persistent storage. Adapt to
confirmed scheduler rules. Two sequential density jobs have ceilings of 4 h each
including finalization: 8 wall-hours / 32 core-hours. A changed machine/build adds
two separately budgeted baseline reproductions: another 8 wall-hours / 32 core-hours.
Keep the old laptop limits unchanged and retain failures/partial results.

**Acceptance scope:** energy-difference sensitivity<=2.0 meV per comparison,
without per-atom normalization; separately for each structure,
`max_i ||F_i(refined)-F_i(reference)||_2 <= 0.005 eV/Angstrom`, **all atoms**.
Apply criteria between successive registered refinements **and** from the eventual
common refined protocol directly to the original baseline. Passing sensitivity
checks is not an absolute accuracy bound or proof of the−0.29-meV sign.

## Specific decisions requested from the professor

1. **Paper scope:** make the contribution a staged evaluation of optimization,
   surrogate adequacy and target reliability, with ordered UiO-66 patterns as a
   provisional computational case study? Or require validated material prediction,
   which remains outside the available evidence?
2. **DFT evidence level:** retain the four comparisons explicitly as preliminary
   baseline diagnostics, or require numerical convergence before they support a
   quantitative central claim? The water pair is only the first resource/convergence
   check; all claimed host/CO2 decompositions would need justified coverage.
3. **Minimum physics checks:** which parent/proton/amino assumptions require expert
   signoff, and is any guest-versus-host mechanistic claim essential enough to
   justify the four missing UMA host points? Avoid pursuing the sub-meV remainder
   merely to assign a sign.
4. **Numerical rule confirmation:** is the reconstructed algebra
   `Sc=|DeltaEc(r)-DeltaEc(p)|`, `Sh=|DeltaEh(r)-DeltaEh(p)|`,
   `Sg=|[DeltaEc-DeltaEh](r)-[DeltaEc-DeltaEh](p)|`, each <=2.0 meV, correct?
   Both successive and direct-to-original comparison routes are already confirmed.
5. **ODAC25 role:** omit real-data benchmark claims from the current methods draft,
   retaining the unresolved provenance audit as a limitation, while awaiting the
   source-side mapping/reference export? The user must confirm any request submission;
   this draft sends nothing.

**Minimum defensible current position:** retain existing negative/diagnostic
results and all exceptions; use additive descriptively; keep DFT provisional;
claim neither reliable material rankings nor an SNN advantage. Additional
convergence or independent predictive validation is required only before making
the corresponding stronger claim—not silently assumed to have been completed.

Preparation validation and source hashes:
[review receipt](PHASE3_PROFESSOR_RESULTS_LIMITATIONS_20261027_SOURCES.json).
No historical scientific audit, fit or calculation was rerun for this draft.
