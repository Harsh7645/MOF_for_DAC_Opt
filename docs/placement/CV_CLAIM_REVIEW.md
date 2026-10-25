# CV claim review and placement priorities

Updated 26 October 2026 using saved scientific evidence and convergence preparation dated through 10 October. The submitted CV cannot be changed. This document prepares an accurate explanation of its claims and distinguishes later progress from the evidence available when it was submitted. Its shareable repository copy is under `docs/placement/`.

**Recommendation**

Present the completed computational work as ongoing research. The 64-configuration UMA fit and 14 completed baseline DFT single points strengthen the technical discussion. They do not complete the three-model, 138-MOF ranking claim. Practise the actual implementation and evidence daily while progressing through the remaining scientific gates.

**Claim-by-claim findings**

| Submitted claim | Evidence | Required correction |
|---|---|---|
| Constrained QUBO pipeline for UiO66, 92% of 60 seeded 50-bit runs matching Gurobi | The numerical pipeline exists. The 92% is rounded from 55/60 **SA** runs at 4,000 steps, across 20 synthetic 50-bit instances and three solver seeds. SNN reached the optimum on 7/20 instances at this size. | Name SA, the budget and synthetic scope. This is not real UiO-66 optimization or an SNN 92% result. |
| 560,208 DFT rows compressed 4,000x into 138 leakage-safe pairs; UMA validated at 0.024 eV | 560,208 source rows were deterministically reduced to 285 single-gas targets and 138 paired validation MOFs. The row/pair ratio is about 4,059. UMA ran on 16 GCMC structures, with total-energy MAE 0.0236525 eV. | Say curated or reduced, rather than implying lossless compression. Specify provenance and frozen validation scope; a matching training dataset is unfinished. State 16 structures and total-energy MAE; this is not 138-MOF adsorption validation. |
| Built CGCNN, UMA and ridge surrogates ranking 138 unseen MOFs, grounded h/J, top-10 DFT checks | Ridge code exists; the accepted 138-MOF ridge/UMA/CGCNN comparison is not complete. Separately, 64 UiO-66 targets and provisional UMA-derived h/J were fitted and optimized. Fourteen baseline DFT SCFs cover seven complex snapshots plus seven stripped hosts. Sampling stability and convergence remain open. | Explain the two studies separately. The coefficients are provisional; the 14 SCFs are diagnostic snapshots, not top-ten candidate validation. CGCNN and full-pool ranking remain ongoing. |

Sources: [saved benchmark](../../docs/phase3_results.json), [Phase 3 status](../../docs/PHASE3_STATUS.md), [reference audit](../../docs/PHASE3_REFERENCE_AUDIT.md), [provisional coefficient graph](../../data/design/uio66_uma_train_fit_v1.json), [baseline DFT results](../../docs/UIO66_QE75_BASELINE14_RESULTS_V1.md).

The 55/60 and 7/20 counts were recomputed from saved per-run records in the original review. This update reuses those results. The remaining-work tracker still lists CGCNN evaluation and the shared-pool comparison as pending. The old library's null coefficient placeholder does not describe the later exported UMA-derived coefficient graph.

**Evidence-based wording for discussion or a future CV**

Use these only where they accurately describe your own contribution; identify upstream libraries and AI assistance when discussing how the work was done.

- Implemented a constrained QUBO/SNN optimization pipeline and benchmarked against Gurobi; simulated annealing matched certified optima in 55/60 runs on synthetic 50-bit problems.
- Curated 560,208 ODAC25 rows into 138 paired CO2/H2O validation targets with source/frame provenance; smoke-tested UMA on 16 structures (0.024 eV total-energy MAE).
- Evaluated 64 provisional UiO-66 configurations with UMA, fitted and benchmarked a six-bit quadratic score, and completed 14 frozen-geometry DFT single-point diagnostics; numerical convergence and material validation remain ongoing.

Label the project “ongoing.” Distinguish completed DFT calculations from completed numerical or physical validation. Do not describe the fitted objective as proven adsorption physics.

**Handling the submitted CV**

The submitted CV is locked. Clarify scope when first discussing the project, using dates and saved evidence. Later progress strengthens the account but does not change which experiments produced the original metrics. Use an updated copy only if the placement process permits one.

Suggested clarification:

“The 92% result is simulated annealing on synthetic 50-bit instances, and 0.024 eV is UMA total-energy MAE on 16 structures. Since submission, I have fitted a provisional UMA-derived score for 64 UiO-66 configurations and completed 14 independent DFT single-point diagnostics. The 138-MOF model comparison, convergence checks and top-ten validation are still ongoing.”

No correction was sent to recruiters or the placement cell by this review.

**Scientific distinctions to defend**

The [local target contract](../../docs/ODAC25_TARGET_CONTRACT.md) separates total-energy evaluation from adsorption-energy evaluation. Adsorption requires compatible complex, bare-MOF and gas references. The ODAC25 reference mismatch remains unresolved; the newer same-composition snapshot diagnostics do not repair it.

The [remaining-work tracker](../../docs/REMAINING_WORK.md) requires compatible targets, training-only model selection, a frozen checkpoint and saved per-MOF predictions. Installing a graph model does not establish adsorption prediction or a leakage-safe score.

The provisional 22-parameter pairwise fit has held-out MAE 0.0301754 eV, versus 0.0238031 eV for the additive fit. Explain why model complexity did not improve prediction. The 13 held-out states have since been inspected during development; they are not an untouched final test.

The four selected DFT/UMA complex-energy changes agree in direction, with 2.14–4.39 meV discrepancies at the baseline settings. This is not a general model-error estimate. The -0.294481-meV guest-associated remainder is numerically unresolved. Coding assistance does not replace the missing scientific evidence.

**Practical priorities from the current state**

The original three–four-day test deadline was reported on 3 October and is no longer a current scheduling assumption. The next interview date is unspecified. Use dependencies rather than promised completion times.

| Workstream | Sensible objective | Evidence needed |
|---|---|---|
| Daily interview preparation | Explain the synthetic benchmark, separate UiO-66 fit and DFT diagnostics from saved evidence. | Short pitch, code walkthrough, exact metric denominators and limitations. |
| Immediate scientific review | Confirm reconstructed convergence algebra and a suitable machine/allocation. | Recorded decisions, bounded execution plan and original-baseline comparison rules. |
| ODAC25 benchmark | Resolve reference/training compatibility, then evaluate ridge/UMA/CGCNN on the same 138-MOF pool. | Compatible labels, training-only tuning, saved predictions and ranking metrics. |
| UiO-66 validation | Complete reviewed numerical checks, chemistry review and sampling-stability investigation before accepting coefficients/rankings. | Comparable results, uncertainty, accepted sampling and independently justified candidate checks. |

The immediate interview goal is a defensible computational case study. A completed material-model benchmark would strengthen it, but its completion date is not established.

**Interview material to prepare**

Be able to explain `h @ x + 0.5*x @ W @ x`, explicit constraints, binary versus fractional states, SA's fixed-count swaps, the upstream SNN API, why decoding is separate, and what a Gurobi certificate means. Interpret raw SNN feasibility separately from feasible decoded outputs.

Explain why the 138 existing validation MOFs and the 64 new structure proposals are different experiments. Explain why 64 patterns can be enumerated and why they cannot establish an SNN scaling advantage by themselves. Describe the energy-reference bug as an investigation with saved evidence, without claiming it is fixed.

For software/ML roles, the current project can support a substantial technical discussion if you understand these decisions and your personal contribution. For materials-research roles, the incomplete physical validation will be a larger limitation. Hiring outcomes still depend on the role and the rest of your preparation.

Read the fuller [placement preparation brief](PLACEMENT_PREP_BRIEF.md) for the architecture and study sequence.
