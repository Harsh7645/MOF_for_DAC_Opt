# MOF for DAC: placement preparation brief

Updated on 26 October 2026 against the saved evidence in `C:/Users/hp/Documents/GitHub/MOF_for_DAC_Opt`. The latest scientific results and convergence preparation are dated 10 October; this documentation update does not represent new calculations. The repository copy under `docs/placement/` is the shareable preparation reference.

**The project in one sentence**

The project investigates whether constrained spiking-neural-network optimization can select useful MOF building-block arrangements, using classical solvers as references and eventually grounding the scoring function in CO2 and water adsorption evidence.

**An interview introduction you can use**

“My project studies computational design of metal–organic frameworks for direct air capture. I represent design choices as binary variables with explicit constraints, integrate a spiking neural optimization solver, and compare it with simulated annealing and Gurobi. The synthetic benchmark is complete. Separately, the project curated 138 paired CO2/water validation MOFs, evaluated 64 provisional UiO-66 configurations with UMA, and fitted a quadratic score. Fourteen Quantum ESPRESSO single-point calculations now provide independent diagnostics on selected geometries. The full 138-MOF surrogate comparison, numerical convergence checks and physical validation remain ongoing.”

This is a project-level account. Before saying “I implemented” or “I designed,” identify your actual contribution, what used an existing library, and what was developed with AI assistance. The SNN algorithm is integrated from the lab's `snn-opt` package; this repository is not evidence that you invented that algorithm or trained a material predictor successfully.

**What is complete and what remains**

| Part | Supported current status |
|---|---|
| Phase 1: formulation and scoped literature work | Complete for controlled synthetic problems; real chemistry and novelty remain evidence questions. |
| Phase 2: algorithm integration | Actual `snn-opt==0.6.0` execution, convex control, experimental nonconvex route and decoding are complete. |
| Phase 3: numerical benchmarking | Frozen synthetic comparison of SNN, SA and Gurobi is complete. |
| Phase 3: 138-MOF material benchmark | Validation targets and ridge code exist; compatible training/reference data, UMA adsorption predictions and CGCNN evaluation remain open. |
| Phase 3: separate UiO-66 design experiment | 64 bare structures relaxed and paired targets audited; provisional UMA-derived h/J fitted and enumerated/optimized. Sampling stability and independent validity remain open. |
| Phase 3: independent DFT diagnostics | 14 frozen baseline SCFs complete and verified: seven complex snapshots plus seven matching stripped hosts. Convergence v2.1 is prepared, not executed. |
| Phase 4 | Independent candidate validation, sensitivity studies, reproducibility package and manuscript remain. |

Optimization correctness, surrogate prediction quality and physical material validity are separate questions. A solver finding the minimum of the fitted score does not validate the score or establish improved DAC performance.

**The mathematical formulation to understand**

The canonical score is

`H(x) = sum(h_i*x_i) + sum_{i<j}(J_ij*x_i*x_j)`.

Each binary variable is a design choice. `h_i` represents its individual contribution; `J_ij` represents an additional pair contribution. The 50-bit benchmark uses synthetic coefficients. The separate six-bit UiO-66 fit uses provisional UMA-derived coefficients, with chemistry and sampling limitations.

The code stores symmetric, zero-diagonal `W`, with `W[i,j] = J_ij`, and evaluates

`H(x) = h @ x + 0.5 * x @ W @ x`.

The factor of one half prevents counting each unordered pair twice. Constraints remain explicit: `E @ x = e`, `U @ x <= u`, with binary choices or relaxed bounds `0 <= x <= 1`. A soft pair cost is not a hard selection rule.

The binary QUBO export is `Q = diag(h) + W/2`. Its equivalence uses `x_i**2 = x_i`. On fractional states, replacing the linear term with diagonal quadratic terms changes the relaxation. For the intended relaxation, the gradient is `h + W @ x` and Hessian is `W`. Curvature is checked through eigenvalues. The nonconvex SNN route has no guaranteed convergence or global optimum.

The synthetic slot family uses two variables per slot with one-hot occupancy. Thus 12, 20 and 50 benchmark bits represent 6, 10 and 25 abstract slots. The provisional real UiO-66 library instead uses one substitution bit per always-occupied linker: six bits total. Do not conflate these encodings, or confuse the original six-variable toy fixture with the UiO-66 library.

Source: [formulation.py](../../mof_dac/formulation.py), [instances.py](../../mof_dac/instances.py).

**How the three solvers fit together**

| Method | Implementation and interpretation |
|---|---|
| Simulated annealing | Seeded stochastic search. The benchmark exchanges an A slot and a B slot to preserve the fixed B count, rejecting other violations. Worse moves can be accepted using `exp(-delta/T)`. No optimality certificate. |
| Gurobi | Solves the original constrained binary quadratic model. The saved status, bound and gap establish whether a result is certified; a timeout alone would not. |
| SNN | Calls the existing `snn_opt.solve_qp` on a continuous relaxation. Raw state, convergence diagnostics and constraint violations are recorded; a separate decoder converts it into binary choices. |

The fixed-count decoder selects the slots with the largest B-minus-A state differences. It finds a nearest fixed-count assignment rather than secretly optimizing the energy. It costs approximately `O(s log s)` for `s` slots and must be distinguished from the raw SNN dynamics. Independent feasibility checks still matter.

Source: [optimizers.py](../../mof_dac/optimizers.py), [snn.py](../../mof_dac/snn.py), [decoder](../../mof_dac/instances.py).

**Results worth remembering**

The frozen benchmark used 20 instances at each size, with instance seeds 100–119. Gurobi used one thread and a 30-second limit. SNN used one deterministic start per instance and 2,000 iterations. SA used three seeds and three budgets: 250, 1,000 and 4,000 steps.

| Bits | Gurobi certified optima | Decoded SNN optimum hits | Raw SNN feasible fraction | SA optimum hits at 4,000 steps |
|---:|---:|---:|---:|---:|
| 12 | 20/20 | 15/20 | 15% | 60/60 |
| 20 | 20/20 | 10/20 | 0% | 59/60 |
| 50 | 20/20 | 7/20 | 0% | 55/60 |

Enumeration independently agreed with Gurobi on the 40 smaller instances. All 540 SA runs and all 60 decoded SNN outputs were feasible. Mean decoded SNN gaps were approximately 0.0840, 0.5256 and 2.8450 synthetic score units. SA and SNN have different run counts and budgets; their optimum-hit fractions describe the tested protocol, not a universal performance comparison.

The defensible interpretation is that the integration works, decoding restores feasibility in this benchmark, and SNN quality declines with size under these settings. There is no demonstrated SNN superiority, hardware energy saving or improved CO2 capture.

Source: [benchmark status](../../docs/PHASE3_STATUS.md), [raw benchmark JSON](../../docs/phase3_results.json).

**Two separate material datasets**

The 138-MOF set is a frozen validation subset extracted from ODAC25. The reducer processed 560,208 source rows, retained exact one-molecule records, selected the largest frame ID within each trajectory and then the lowest corrected final-frame adsorption energy for each MOF/gas. It produced 285 single-gas targets and 138 paired MOFs, with source indices and trajectory/frame provenance. These are source-calculated labels, not measurements performed by this project.

The 64 UiO-66 proposals are a separate design experiment. The parent is an authenticated ODAC25 structure identified as `jz4002345_si_002`, source index 184693, frame ID 7. Distance-based periodic mapping identified six BDC linkers. Each of six always-filled slots chooses ordinary BDC or NH2-BDC, giving `2**6 = 64` labeled patterns. The builder replaces a selected ring H with N and adds two H using a deterministic initial orientation.

All 64 configurations completed fixed-cell UMA bare relaxation and passed the saved composition, severe-contact and inferred-connectivity checks. Structural grouping was performed; labeled patterns are not necessarily distinct materials. All 64 paired targets from 512 adsorption starts were audited. A 22-parameter fit used the frozen 51/13 group split. Pairwise held-out MAE was 0.0301754 eV versus 0.0238031 eV for the additive model; the pairwise model was worse. The 13 states have since informed development and are not an untouched final test. The parent comes from validation, so this experiment remains outside the ODAC25 training table.

Enumeration and Gurobi agreed on fitted optimum `110111`; SA and SNN each hit it in 10/10 tested runs. This is a six-bit fitted-objective result, separate from the 50-bit synthetic benchmark. The best sampled label belonged to `111111`, so the fitted optimum is not the best sampled configuration. Two-versus-four-start top-ten overlap was 0.4, and the larger eight-design pilot failed its registered stability gate. Further refitting or expansion has not been justified by these diagnostics.

Source: [UiO-66 proposal and structural evidence](../../docs/UIO66_PROVISIONAL_LIBRARY.md), [paired-target contract](../../docs/ODAC25_TARGET_CONTRACT.md). The raw paired-target JSON is retained locally under `artifacts/kaggle/odac25_paired_targets_2026-09-14/`; it is ignored by Git.

**Two separate scientific workstreams**

Adsorption energy subtracts the bare-MOF and gas reference energies from the MOF-plus-gas energy. Those components must use compatible conventions. The audit found that `energy_old`, rather than corrected total `energy`, reproduces the stored adsorption-field identity. Matching bare references still fails: final-frame minima mismatch 94 of 285 targets; a separate lookup over 189,504 bare rows finds no exact stored match for 62 of 67 distinct unresolved energies.

This does not prove the required geometries are absent. Calculation version, correction or cell normalization may differ. It does prevent the current identity check from passing. A valid benchmark cannot be manufactured by dropping difficult candidates or mixing conventions.

A 16-structure UMA T4 smoke run succeeded, with total-energy MAE about 0.02365 eV. That is an execution check on a small sample, not a full adsorption-energy ranking result. The preliminary training mirror also lacks corrected labels and frame IDs required by the frozen protocol. Baseline code exists, but compatible training data and accepted full-pool results remain open.

Source: [reference audit](../../docs/PHASE3_REFERENCE_AUDIT.md).

The separate frozen-snapshot DFT experiment does not need the unresolved ODAC25 reference match for its same-composition energy changes. Seven complex snapshots and their seven stripped hosts completed QE 7.5 SCFs at 80/600 Ry, PBE-D3(BJ), with Gamma sampling. Portable offline review verified 471 payload hashes, 14 SCFs and 1,717 force vectors. DFT and archived UMA favor the later complex geometry in all four selected comparisons; energy-change discrepancies are 2.14–4.39 meV at the baseline settings. These are selected diagnostics, not a general UMA accuracy score or validation of ten ranked candidates.

`Delta E_guest-associated = Delta E_complex - Delta E_stripped-host`. It includes interaction and guest deformation; it is not an isolated adsorption energy. The late CO2 remainder is -0.294481 meV and its sign remains numerically unresolved. SCF convergence does not establish cutoff, grid or k-point convergence. Frozen snapshots are not DFT-relaxed minima; the largest baseline force is about 0.565885 eV/Angstrom on a stripped-host H.

Convergence v2.1 registers 2.0 meV per energy-difference comparison and maximum per-atom force-vector change <=0.005 eV/Angstrom, including all atoms. Both successive registered refinements and the eventual common refined protocol versus the original baseline must be checked. The energy algebra still awaits focused confirmation; the execution machine is unassigned. Prepared water checks do not validate hosts/CO2 by themselves, and no refinement result is available.

Sources: [baseline results](../../docs/UIO66_QE75_BASELINE14_RESULTS_V1.md), [current convergence specification](../../docs/UIO66_QE75_WATER_CONVERGENCE_V2.md).

**Remaining work in dependency order**

1. Resolve energy-reference identities and construct matching training targets with no MOF overlap with validation.
2. Run constant/composition, UMA and one compatible graph/Transformer baseline on the frozen 138-MOF pool. Report per-gas MAE/RMSE, competition-difference error, top-10 overlap, rank correlation, failures and cost.
3. In parallel with the ODAC25 workstream, confirm the convergence algebra and a suitable machine/allocation, then execute only the separately reviewed convergence checks. Baseline reproduction is conditional on a machine/build change.
4. Resolve chemistry/proton correspondence, missing UMA host results and failed sampling stability before accepting or refitting UiO-66 coefficients. Six substitution bits require 22 parameters: one intercept, six linear terms and 15 pairs. The existing fit and additive comparison are provisional evidence, not tasks to rerun automatically.
5. Reassess optimization only when an accepted physical score changes. The current six-bit objective has already been enumerated and tested with SNN, SA and Gurobi. A scaling-advantage claim needs a larger chemically valid design space.
6. Independently validate top structures, perform sensitivity/ablation studies, produce reproducible figures and write the manuscript.

Human scientific review matters when choosing the physical target and paper claim, accepting the energy convention, approving structures and conditions, selecting independent validation and signing off on interpretation. The previous chat's 3–6-month estimate was conditional, not a deadline or an estimate for placement preparation.

Source: [remaining-work checklist](../../docs/REMAINING_WORK.md).

**Code map for interview preparation**

| Responsibility | Files to understand |
|---|---|
| Input validation and mathematical contract | `mof_dac/data.py`, `formulation.py` |
| Classical search and exact references | `optimizers.py`, `gurobi.py` |
| SNN integration, synthetic generation and decoding | `snn.py`, `instances.py` |
| Benchmark execution and aggregation | `phase1.py`, `phase2.py`, `phase3.py` |
| Coefficient recovery and identifiability | `parameters.py` |
| Target reduction, pairing and ranking metrics | `odac25.py`, `material_baselines.py` |
| Bounded data extraction and inference safeguards | `odac25_archive.py`, `kaggle/phase3_material_pipeline.py` |
| Provisional design and periodic substitutions | `uio66.py`, `uio66_structures.py` |
| UMA relaxation, adsorption and fitted coefficients | `relaxation.py`, `adsorption.py`, `design_fit.py`, `scripts/fit_uio66_adsorption.py` |
| Portable DFT evidence and convergence preparation | `scripts/review_qe75_baseline14_portable.py`, `scripts/check_qe75_water_convergence_v2.py` |
| Mathematical, failure-path and provenance checks | `tests/test_foundation.py`, `test_material_pipeline.py`, `test_uio66.py` |

There are three distinct graphs: the numerical selection/interactions graph, the periodic atomic connectivity graph, and Graphify's code/document retrieval graph. They serve different purposes. The numerical kernels use NumPy/SciPy; ASE handles atomistic structures; optional integrations supply SNN, Gurobi and material-model execution.

**Preparation sequence**

1. Explain the project in 60 seconds, then in three minutes, using the introduction above.
2. Work one two-choice scoring example by hand; explain constraints, the factor of two and the binary/fractional distinction.
3. Explain SA moves, SNN relaxation and decoding, and Gurobi certificates from the actual code.
4. Interpret the benchmark table, including raw versus decoded feasibility and unequal budgets.
5. Explain target extraction, leakage protection, provenance hashes and the energy-reference failure.
6. Identify your personal contribution and one difficult decision you can defend from code and evidence.

Questions to practice: Why use synthetic data first? Why are penalties insufficient for hard rules? Why can thresholding violate a budget? Why is the SNN not guaranteed to converge? Why compare with Gurobi? Why enumerate 64 designs? Why do the 138 validation MOFs and 64 designs remain separate? Why did the additive fit outperform pairwise? Why are 14 SCFs not 14 MOFs or top-ten validation? Why does SCF convergence differ from numerical/physical convergence? Why is the sub-meV remainder unresolved? How would you prevent leakage?

Role-specific emphasis and your interview date are still unknown. For software/ML interviews, prioritize numerical implementation, algorithms, evaluation and data engineering. For materials interviews, add more depth on the structure assumptions, adsorption protocol and independent validation.

**Review limits and correction to the earlier chat**

The 3 October review established the original architecture and CV distinctions. This 26 October update reads the later saved design, DFT and convergence records. Recorded Windows baseline integration checks passed 42 targeted tests; convergence v2.1 preparation records five targeted tests and a 21-payload/254-atom verifier pass. These are historical results, not a fresh full-suite run.

The last verified local and remote `main` commit before this documentation update was `2ead186` (10 October). Later convergence preparation and this refresh require committing. Git status must be checked again when committing; this paragraph is not a live clean-tree assertion. The generated Graphify graph remains an explicitly historical 5 October snapshot; use the current document navigation for newer evidence. No scientific calculation or protocol change is implied by this refresh.
