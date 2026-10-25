# Research execution, professor review and daily CV preparation

Updated 26 October 2026. The direction agreed on 3 October remains: continue feasible research, obtain professor verification alongside it, and practise the CV daily. The CV is locked. Scientific records currently extend through 10 October; this update does not report new calculations. The shareable repository copy is under `docs/placement/`.

**Near-term allocation**

The early-October test countdown is historical; no new interview date is assumed. Keep a repeatable 25-minute daily explanation session, plus a bounded research block that fits your placement preparation. Review completed evidence rather than rerunning experiments solely for practice.

**Three coordinated tracks**

| Track | Next work | Completion evidence |
|---|---|---|
| Research | Resolve ODAC25 references, inventory compatible training data, then execute simple and UMA baselines. Add one target-compatible structure model after the data gate. | Source-backed protocol, compatible targets, overlap checks, per-MOF predictions, reproducible metrics and failures. |
| DFT and professor review | Review the completed 14-SCF baseline and prepared convergence v2.1 plan; confirm algebra, chemistry and machine/allocation before new calculations. | Recorded reviewer decisions, comparable refined/baseline results, all-atom force checks and a bounded compute plan. No approval is inferred from silence. |
| CV preparation | Explain one topic aloud daily, trace its code and defend a result or limitation. | A short answer, a worked example or code walkthrough, and a list of questions you could not answer. |

The tracks progress together, but dependent scientific work uses a reviewed convention. Independent tooling, tests, source inventory and interview practice can continue while review is pending.

**Research milestones, retaining the existing four phases**

1. **Phase 3 data foundation:** determine the exact energy-reference convention; construct compatible training targets; check MOF identity overlap and freeze manifests. If a different protocol is required, document and review it as a separately named experiment rather than changing the frozen benchmark silently.
2. **Phase 3 material benchmark:** evaluate constant/ridge and UMA predictions on the fixed 138-MOF pool; add a suitable CGCNN or equivalent structure model. Record checkpoints, training-only tuning, all predictions, failures, errors, ranking metrics and costs.
3. **Phase 3 chemistry grounding:** preserve completed UMA relaxation/grouping, 64 paired targets/512 starts and the 22-parameter provisional fit. Resolve chemistry/proton correspondence, sampling instability and independent validity before accepting or refitting coefficients. Pairwise held-out MAE is 0.0301754 eV, worse than additive 0.0238031 eV; the inspected 13-state holdout is now development evidence.
4. **Phase 3 optimization and DFT diagnostics:** enumeration/Gurobi agree on the six-bit fitted optimum, and SA/SNN have already been run. All 14 baseline SCFs are complete. The next experimental gate is reviewed numerical convergence, not repeating these completed steps. Independent top-ten candidate validation remains separate.
5. **Phase 4:** reconstruct top candidates, perform the agreed independent checks, analyse sensitivity/ablations, reproduce results and write the manuscript. The interview milestone need not wait for paper submission.

The ODAC25 checkpoint is a compatible data/reference protocol. The separate DFT checkpoint is convergence and interpretation of selected same-composition snapshots. Neither closes the other workstream. A successful implementation or plausible-looking number does not establish an accepted full-pool adsorption benchmark.

Operational source: [remaining-work checklist](../../docs/REMAINING_WORK.md).

**ODAC25 professor review — still open**

Purpose: confirm what the physical target means and how its energy references should be reconstructed before full-model evaluation.

Current evidence:

- The frozen reducer produced 285 single-gas targets and 138 paired validation MOFs from 560,208 source rows.
- The sampled identity `energy_old - energy_mof - energy_ads_corrected` gives consistent CO2/H2O gas constants. Corrected total `energy` does not give the same identity.
- Final-frame bare minima fail to match 94 of 285 selected target references. A separate lookup over 189,504 bare rows finds stored energy matches for only 5 of 67 distinct unresolved reference energies.
- The preliminary training mirror lacks corrected labels and relaxation frame IDs required by the frozen reduction protocol.
- The current proposed evaluation uses DFT-selected geometries and reference metadata; it must be described as reference-assisted energy evaluation rather than prospective design screening.

Concrete questions:

1. Which bare geometry, calculation version, cell normalization and correction convention correspond to the stored adsorption labels? What evidence would establish the match?
2. Should we preserve the frozen target exactly, or define a separately named experiment if matching references cannot be reconstructed? Which comparisons remain scientifically interpretable?
3. Is the paired CO2-minus-H2O energy difference acceptable as a competition diagnostic for this study, and which DAC claims require additional properties?

Read with the professor: [reference audit](../../docs/PHASE3_REFERENCE_AUDIT.md) and [target contract](../../docs/ODAC25_TARGET_CONTRACT.md). The raw lookup remains local under `artifacts/kaggle/odac25_reference_audit_2026-10-02/reference_lookup/phase3_reference_frame_lookup.json`; it is ignored by Git.

The repository does not record scientific signoff for this workstream. This documentation refresh sends no message and does not infer approval.

**Current DFT review — baseline complete, convergence prepared**

Read the preserved [professor packet](../../docs/UIO66_QE75_PROFESSOR_REVIEW_20261010.md) with the newer [convergence v2.1 specification](../../docs/UIO66_QE75_WATER_CONVERGENCE_V2.md). The newer specification supersedes the packet's open threshold-choice proposal; the packet remains a historical review record.

- Fourteen SCFs cover seven saved complex geometries and seven stripped hosts, not 14 different MOFs or top-ten candidate validation. Recorded offline review verified 471 payload hashes, 14 SCFs and 1,717 force vectors.
- DFT and UMA complex changes agree in direction in four comparisons; 2.14–4.39 meV discrepancies remain provisional. Guest-associated changes are not isolated adsorption energies. The -0.294481-meV remainder's sign is unresolved.
- Registered sensitivity rules are 2.0 meV per energy comparison and maximum per-atom force-vector change <=0.005 eV/Angstrom, including all atoms. Both successive refinements and eventual common refined protocol versus original baseline are required. Reconstructed energy algebra still needs focused confirmation.
- Machine/build/allocation remain unassigned. The suggested workstation profile is 32 GiB physical/24 GiB available RAM, 20-GiB hard/18-GiB graceful-stop bounds, zero job swap and four physical CPU cores. It is a proposed profile, not a verified allocation.
- Two prepared water 80/750-Ry checks have an 8-hour/32-core-hour proposed ceiling. If machine or build changes, two 80/600-Ry reproductions require a separate 8-hour/32-core-hour stage first. Host/CO2, wavefunction-cutoff, electronic-tolerance and k-point checks remain separate. No new job is authorized by these notes.

**Next professor packets**

- **Chemistry:** authenticate the parent topology and six-linker mapping; review protonation, periodic connectivity, amino orientation, symmetry equivalence, relaxation and adsorption protocol. Use [the provisional library record](../../docs/UIO66_PROVISIONAL_LIBRARY.md).
- **Independent validation:** agree candidate selection, top-K, DFT or alternative method, gas/humidity conditions, convergence requirements and compute budget before costly runs.
- **Claims:** decide whether the paper studies solver behaviour, materials design or both. The 64-pattern family supports an enumerable pipeline test; an SNN scaling claim needs a larger valid problem.

**Daily CV practice — repeatable 25-minute session**

1. Five minutes: explain the project or today's topic aloud without notes.
2. Ten minutes: trace one relevant function or work through one numerical example.
3. Five minutes: answer two follow-up questions, including one limitation.
4. Five minutes: write down what you could not explain and the evidence you need.

Rotate through these topics:

| Day | Topic | Questions to answer |
|---|---|---|
| 1 | Problem and current scope | What is the project trying to prove? What has actually been completed? |
| 2 | Hamiltonian, QUBO and constraints | Why the factor of one half? Why does binary QUBO equivalence fail on fractional states? |
| 3 | SA, SNN and Gurobi | How does each work? Which guarantees apply? What uses upstream code? |
| 4 | Benchmark and decoding | Which method achieved 92%? What is raw versus decoded feasibility? Are budgets comparable? |
| 5 | ODAC25 and leakage | How were 138 pairs selected? How are identities, frames and split boundaries checked? |
| 6 | Predictors and energy references | What do ridge, UMA and CGCNN predict? Why is the current subtraction blocked? |
| 7 | UiO-66, fitted coefficients and DFT | Why 64 patterns and 22 parameters? Why did pairwise underperform additive? Why are SCF convergence and physical validation different? |

Repeat the rotation with deeper examples and new results. Keep a current ledger for each CV claim: exact wording, method, dataset, metric, date, artifact, personal contribution and limitation.

Fixed numerical clarifications: the existing 55/60 (approximately 92%) result belongs to SA at 4,000 steps on synthetic 50-bit instances; the existing 0.024 eV is a 16-structure UMA total-energy smoke-test MAE. Later work does not change the scope of those original measurements.

Use [the placement brief](PLACEMENT_PREP_BRIEF.md) and [CV evidence audit](CV_CLAIM_REVIEW.md) as the preparation references.
