# Scientific clarifications v2 — 27 October 2026

Response to findings supplied through the user's instruction. Source inspection
and drafting are AI-assisted; this is **not qualified human approval**. No new
fit, solver run or energy/force calculation. Historical results remain unchanged.

## 1. Exact-count decoding is not objective optimization

For synthetic slot s, the continuous state has entries `(x_A, x_B)`.
`decode_slot_state` sorts **descending `x_B-x_A`** and assigns B to the first k
slots; every other slot gets A. `np.argsort(..., kind="stable")` preserves input
slot order for exact ties, so lower slot index wins. There is no fuzzy tie tolerance.
It sets one entry to 1 and the other to 0. Required k is fixed by the instance,
not chosen to lower energy: the held-out 12/20/50-bit cases have 6/10/25 slots
and k=3/5/12, respectively.

This is the nearest squared-Euclidean binary assignment under these slot/count
constraints: changing one slot from A to B changes squared distance by
`2*(x_A-x_B)`. It does **not** evaluate h, W or H and does not optimize the
quadratic objective. It does not guarantee arbitrary additional inequalities;
all output constraints are checked afterward. The held-out family has the
slot/count equalities and box constraints, without the optional frustrated
inequality. Other tiny-oracle/repair paths are separate and must not be attributed
to this decoder. Sources: [instances.py](../mof_dac/instances.py), lines 65–79;
[phase3.py](../mof_dac/phase3.py), lines 66–101.

|Reported check|Actual rule|Scope|
|---|---|---|
|Continuous feasible|max equality, positive inequality and box residual ≤1e-7|Does not test integrality.|
|Binary feasible|Same checks plus max `abs(x-rint(x))` ≤1e-7|Raw binary flags and all decoded candidates.|
|Synthetic optimum hit|`np.isclose(gap,0,atol=1e-8)`|Effective absolute tolerance 1e-8 synthetic objective units: the reference argument is zero, so default relative tolerance contributes zero.|
|Six-bit optimum hit|Binary feasible and absolute objective gap ≤1e-8 eV|Fitted objective only; shared offset cancels.|

Source: [formulation.py](../mof_dac/formulation.py), lines 53–73;
[phase3.py](../mof_dac/phase3.py), lines 23–30;
[six-bit benchmark](../scripts/benchmark_uio66_fit.py), lines 34–44, 66–71.
The enumeration/reference *consistency assertion* in phase3.py line 45 is a
different check: `np.isclose(E, Eoracle, atol=1e-8)` retains NumPy's default
rtol=1e-5 on a nonzero reference. Do not mislabel it as the optimum-hit criterion.

The six-bit case uses six substitution bits and **no prescribed amino count**.
Its decoder is simply `x>=0.5` (equality goes to 1), with no energy search or
exact-count repair. This is distinct from the synthetic two-option slot decoder.
Raw/decoded distinctions, actual unequal budgets and feasibility counts remain
in the [central evidence](../plans/phase3-methods-scope-v1/EVIDENCE_INDEX.md).

## 2. Exactly which bootstrap summaries are conditional?

Only the original 51 development patterns/42 frozen duplicate groups enter
the new exploratory bootstrap. The historical 13 have already been inspected.
Each of 1,000 draws samples 42 whole groups with replacement, preserving repeated
groups and all member rows. Seed is 20261027 (`protocol seed 20261026 + 1`),
separate from CV. Every draw and per-model rank/status is retained. A deficient
matrix returns no coefficients; there is no retry, replacement, regularization
or pseudoinverse substitute. Additive: **1,000 included, 0 excluded**. Pairwise:
**977 included, 23 excluded (2.3%)** from coefficient/prediction summaries.

The 23 zero-based draw IDs are 50, 278, 304, 317, 328, 330, 358, 448, 449, 477,
483, 549, 562, 593, 604, 619, 625, 639, 712, 750, 819, 927 and 985.
Draw 562 has rank 20; the other 22 have rank 21 (22 parameters required).
They remain in [all draw statuses](../plans/phase3-review-response-v2/inspection/bootstrap_draw_status.csv)
and the original [bootstrap records](../plans/uio66-offline-development-v1/results/bootstrap_fits.json).

|Summary|Endpoints / definition|Pairwise denominator|
|---|---|---:|
|Coefficient ranges/median (F3), signs, positive fractions; J ranges crossing zero and median range width|2.5th, 50th, 97.5th percentiles; fraction strictly >0|977; 23 excluded|
|Per-pattern rank range/median (S2)|5th, 50th, 95th percentiles; average ranks for ties|977; 23 excluded|
|Top-10 overlap and Spearman summaries (T4/S2)|5th, 50th, 95th percentiles against the full-development fit|977; 23 excluded|
|Preferred-pattern counts/frequencies and count of distinct preferred patterns|Argmin over the 51 development patterns; stable stored ID order for ties|977; 23 excluded|
|Full-fit coefficients, full-fit preferred pattern, condition number, historical metrics and grouped-CV metrics|Separate full-data or CV results|Not computed from the bootstrap subset|

Additive versions of conditional summaries use all 1,000 draws. Numeric endpoints
are supplied in [coefficient CSV](../plans/phase3-review-response-v2/inspection/coefficient_endpoints.csv)
and [all saved stability summaries](../plans/phase3-review-response-v2/inspection/saved_stability_summaries.json).
NumPy percentile uses its default linear interpolation. Source:
[analysis implementation](../scripts/analyze_uio66_development.py), lines 168–200;
[plot implementation](../scripts/plot_uio66_development.py), coefficient/rank sections.
The original historical fit's 200-draw bootstrap is a different preserved analysis;
do not combine it with these 1,000 development draws.

Ranges are conditional resampling diagnostics for **fixed sampled labels** and
identifiable fits, not physical uncertainty bounds, chemical interactions,
unconditional model stability or a multiple-comparison-adjusted significance test.
Additive remains a descriptive reference. The pairwise leave-group-out RMSE
exception remains visible: 38.551 versus 41.042 meV additive, while its MAE is worse.

## 3. Selection, seed streams and preserved failed gates

The preregistered selection is **000000, 111111, 110111, 001001, 000110, 001100,
000111, 010101**. End members, fitted/sample disagreement and matched compositions
were deliberately selected using historical information. It is neither a random
sample nor a new blind evaluation: four selected patterns belonged to the exposed
historical 13. [Selection table](../plans/phase3-review-response-v2/inspection/pilot_selection.csv)
retains each original reason, ranks and split role without new ranking inference.

For each design/gas, two 16-start batches have quotas 2 node-OH, 2 node-oxo,
2 linker-face, 2 substitution-pocket and 8 random-void starts. Configuration index
is 0–7 in the order above; gas index CO2=0, H2O=1; batch=0/1; slot=0–15;
start=`16*batch+slot`. SeedSequence entropy is
`[20261003, configuration_index, gas_index, batch, slot]`.
[All 512 streams](../plans/phase3-review-response-v2/inspection/pilot_seed_streams.csv)
and [the original frozen pose manifest](../data/design/uio66_sampling_pilot_v2.json)
retain exact placements and source hashes.

The RNG streams differ, but accepted poses are conditional on the same host,
anchors, rejection rules and pinned UMA checkpoint/task. Uniform SO(3) *proposals*
and uniform fractional random-center *proposals* are conditioned by ≥2 Angstrom
clearance, 2,000-attempt limit and exact-duplicate rejection against previously
accepted poses (max coordinate difference <1e-8 Angstrom). Consequently accepted
poses are not an unconditional IID pore distribution. This is limited computational
batch independence, not replication of independent physical models or calibrated
uncertainty. Historical four-start seed 41 was reused across gases/configurations
and is not this batch protocol. Source: [sampling.py](../mof_dac/sampling.py),
lines 201–244; [preparation](../scripts/prepare_uio66_sampling_pilot.py), lines 66–67.

The successful replacement retained 512/512 accepted guest relaxations, 16/16
representative force continuations and zero recorded guest failures. This does
not erase the earlier lost/unverifiable interactive attempt or the failed
stability criteria. Initial force tolerance was 0.05 eV/Angstrom, 400-step cap;
representative continuations used 0.02 eV/Angstrom, 600-step cap.

Gas-specific batch gaps and paired gaps remain in
[T5](../plans/phase3-methods-scope-v1/evidence/T5_sampling.csv). Only **001100 (1/8)**
passed the full 10-meV energy gate (both gas adsorption minima, system minima,
paired difference and 16-to-32 changes). Largest H2O gap: 80.546 meV; largest
CO2 gap: 31.752 meV. The small paired gap for 110111 (1.294 meV) masks CO2/H2O
gaps of 19.717/21.010 meV; it did not pass.

Batch Spearman 0.523810 fails ≥0.90; top-two overlap 50% fails 100%; three
decisive reversals fail the none-reversed rule; a top-two boundary near tie makes
that ranking criterion inconclusive. All four representative force-check designs
failed the joint 10-meV adsorption/paired-change target. In the later matched
diagnostic all 48 component paths completed, but four guest paths failed the
initial 5-meV last-checkpoint target. See [T6](../plans/phase3-methods-scope-v1/evidence/T6_relaxation.csv)
and the saved [pilot](../plans/phase3-methods-scope-v1/evidence/inputs/pilot.json)/
[matched](../plans/phase3-methods-scope-v1/evidence/inputs/matched.json) assessments.
509 geometric clusters do not establish 509 physical minima. No thresholds were
changed; no failure was silently discarded.

## 4. Scope and loading terminology

Use **64 encoded ordered patterns**. Six chosen binary substitutions enumerate
the encoding; they do not enumerate regioisomers, amino/proton rotamers, defects,
symmetry-distinct structures or experimentally accessible materials. Stable atom
labels are computational indices, not proven source-CIF atom correspondence.

Each guest calculation contains **one CO2 or one H2O molecule per periodic
primitive framework cell** (six linkers, one Zr6 node), with fixed cell and
periodically repeated loading. These are separate single-species cells, not
coadsorption simulations or the infinite-dilution limit. Loading dependence,
guest/image interactions, finite-size convergence, temperature/free energies,
water clustering, competition and humid-air effects have not been tested.
Subtracting separately sampled gas energies does not establish humidity selectivity.

No exhaustive coverage, symmetry uniqueness, experimental accessibility,
validated material ranking, general UMA accuracy or general solver superiority
is claimed. Unequal solver budgets, historical 13-design exposure, conditional
bootstrap limits and the pairwise RMSE exception remain central limitations.
DFT remains exploratory supplementary baseline evidence; ODAC25 is deferred,
paused and unsent. [Chemistry questions](CHEMISTRY_INSPECTION_REVIEW_V2.md) remain open.
