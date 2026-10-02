# MOF optimization for a computer scientist

## 1. What are we trying to build?

Think of a material as a repeating three-dimensional graph with useful empty space inside it. A metal-organic framework (MOF) contains metal-containing junctions connected by organic molecules called linkers. The empty channels are pores. Gas molecules can enter those pores and interact with the internal surfaces.

Direct air capture (DAC) asks for a material that captures CO2 from very dilute air and later releases it so the material can be reused. The proposal focuses on zirconium-containing junctions and amine-functionalized linkers, initially UiO-66 derivatives. "Amine-functionalized" means adding nitrogen-containing chemical groups to a linker; in the model these become candidate features whose benefits and costs need validation.

For now, translate the task into: **select compatible components under global constraints to minimize a graph cost**. This is a constrained combinatorial optimization problem. It is not initially a task of training a neural network on labels.

The report uses approximately 400 ppm CO2 as a design condition. That means roughly 400 CO2 molecules per million gas molecules. It is not a promise that a material with a favorable score captures useful quantities at that concentration.

## 2. Chemistry terms as software concepts

| Term | CS translation | Where the analogy stops |
|---|---|---|
| Metal node / cluster | A junction type with a connection interface | A cluster contains several atoms; a type ID does not describe its coordinates or charge state. |
| Organic linker | A connector with length, shape and attachment rules | Selecting one does not determine a valid 3D placement. |
| Functional group | A feature attached to a connector | Feature effects depend on its surroundings; rewards are not always additive. |
| Pore | Free space in an assembled graph embedding | Connectivity alone cannot compute accessible pore size. |
| Adsorption | A gas molecule stays near an internal surface | It depends on temperature, pressure, water and interactions. |
| Steric clash | Two selected objects collide geometrically | A soft penalty discourages collision; a hard constraint forbids it in the model. |
| Charge balance | A weighted conservation invariant | Weights require a consistent chemical and stoichiometric interpretation. |
| DFT | An expensive electronic-structure calculation | It is not a ready-made table of the project's h/J coefficients. |
| CoRE MOF | A dataset of assembled experimental structures prepared for computation | It does not directly supply every hypothetical component pair's cost. |
| Hamiltonian | The scalar objective function | Here it is a pseudo-energy score until calibrated to physical quantities. |

The report mentions a CO2 kinetic diameter of about 3.3 angstroms. One angstrom is 0.1 nanometers. Treat that as a motivating size scale, not a rule saying every pore should be exactly 3.3 angstroms wide. Accessibility, flexibility, interactions and water still matter.

## 3. There are two different graphs

**Selection graph:** vertices are candidate building-block choices. A vertex stores an ID, kind, linear score h, and provenance. An edge stores the pairwise score J and its provenance. Choosing a subset means setting a binary vector x. This is the graph implemented in the foundation.

**Crystal graph:** vertices are atoms in an actual structure, with geometry and periodic neighbors. Edges encode bonding or spatial neighborhoods. A crystal model also needs a repeating unit cell and positions. This is the kind of structural input needed for material validation and structure-based ML.

Do not confuse the two. A valid subset of component IDs is not yet a crystal file. A future assembly step must translate selection choices into a concrete periodic structure and verify it. Multiple structures may correspond to the same type selection, so variable design is a research decision.

The input is an edge list rather than a giant hand-entered matrix. The loader checks that every edge endpoint exists and every unordered pair appears once. It converts the graph to arrays only at the numerical boundary. Missing pairs count as zero only because the dataset explicitly declares that modeling assumption.

## 4. How the score works

For n choices, x has shape `(n,)`. Initially each entry is 0 or 1:

```text
x[i] = 0: exclude choice i
x[i] = 1: include choice i

H(x) = sum(h[i] * x[i]) + sum(J[i,j] * x[i] * x[j], i < j)
```

A negative h rewards a useful individual component. A positive J charges a cost when two particular components are selected together. A negative J rewards co-selection. An edge contributes nothing unless both endpoints are selected.

Example: h is `[-2, -1]` and the only pair has J=4. Choosing neither costs 0; choosing the first costs -2; choosing the second costs -1; choosing both costs `-2-1+4=1`. The interaction can reverse the preference implied by individual scores.

Represent this with symmetric zero-diagonal W:

```text
W = [[0, 4], [4, 0]]
H(x) = h @ x + 0.5 * x @ W @ x
```

The factor 0.5 prevents counting each undirected edge twice. Binary QUBO matrix Q is `diag(h) + W/2`; its quadratic form gives the same score for bits because `x[i]**2 == x[i]` for bits. That identity fails for fractions: 0.5 squared is 0.25. The continuous optimizer therefore receives W and h separately.

## 5. Why pairwise penalties are insufficient

Imagine a package manager that scores pairs of libraries for compatibility. Compatible pairs do not guarantee you selected exactly one database engine or stayed within a memory budget. MOF selection has the same issue.

The professor requires at least:

1. Exactly one metal-node type: sum of metal-choice bits equals 1.
2. A linker budget or occupancy requirement: weighted linker count lies in an allowed range.
3. Charge balance: weighted selected charge equals a target, usually zero.

These become linear rows `A_eq @ x == b_eq` and `A_ub @ x <= b_ub`. If two choices truly cannot coexist, `x[i]+x[j]<=1` is an explicit incompatibility row.

The demonstration has two abstract metal choices, each with toy charge +4, and four abstract linker choices with toy charge -2. Exactly one metal and two linkers give charge `4-2-2=0`. These numbers are invented for a numerical test; they do not represent a real zirconium unit cell. The linker budget plus charge row force two linkers without adding a redundant equality.

In a real crystal, choosing one linker *type* does not mean there is one linker molecule in a cell. You must fix multiplicities or use slot-specific choices. Defects, protonation and extra capping groups can change charge. This is why Phase 1 must settle variable semantics with chemical input.

Even all these rows together do not prove a connected, stable, buildable crystal. They define the current numerical feasible set. Geometry and synthesis validity require additional evidence.

## 6. Why relax bits into fractions?

With n unconstrained bits there are `2**n` assignments. Fifty bits already give roughly 1.13 quadrillion possibilities. Exact enumeration is useful only for tiny controls.

The proposed SNN-QP route temporarily lets each choice be any real number between 0 and 1. That makes derivatives available: `gradient = h + W @ x`. An iterative optimizer can move using these derivatives while enforcing linear constraints.

A fractional value such as 0.37 is a search state. It is not automatically a predicted occupancy, synthesis ratio or calibrated probability. Relaxation changes the search domain, and its optimum may have no direct physical interpretation.

Convex objectives have curvature that does not bend downward in any direction. With a convex feasible set, a local minimum is global. An indefinite Hessian has positive and negative curvature directions, so a local method can settle differently from different starts, stall or fail. Looking at coefficient signs is insufficient; inspect eigenvalues of the symmetric Hessian. Equality constraints can restrict which directions are actually accessible.

The lab's published framework concerns convex optimization. Using its dynamics on a nonconvex MOF surrogate is a research experiment. A software termination flag is not a theorem that the binary optimum was found.

## 7. What the spiking network does

The lab solver describes gradient-driven continuous motion interrupted by projection events when constraints are violated. Those events are interpreted as spikes. In an ordinary feed-forward ML model, weights are learned to predict labels. Here the problem's coefficients and constraints define optimization dynamics; the immediate goal is to solve an instance.

The lab API expects an objective `0.5*x@A@x + b@x` and inequalities `C@x+d<=0`. Our mapping is `A=W`, `b=h`. An equality `a@x=r` can be represented by two opposing inequalities; an optional epsilon band loosens that equality and must be recorded. Bounds become additional rows or the upstream solver's documented bound arguments.

The current foundation can export these arrays. It conservatively rejects non-PSD problems for the convex adapter. The complete nonconvex SNN loop remains Phase 2 work; the runnable SciPy control is explicitly labeled SLSQP, not SNN.

NumPy/SciPy are sufficient for the current array arithmetic and match the upstream runtime. PyTorch becomes useful for actual surrogate training or justified GPU batching; adding it now would not turn the optimization loop into validated ML.

## 8. Rounding is another algorithm

Suppose two mutually exclusive choices each equal 0.5. They satisfy `x[0]+x[1]=1`, but thresholding both with `>=0.5` selects both and violates the constraint. Thresholding with `>0.5` selects neither and also violates it.

Always keep three records: relaxed state, raw rounded bits, and repaired bits. Measure violations before and after repair. Do not discard a failure merely because repair later found a good state.

For tiny instances the foundation searches all feasible bits for the one nearest the relaxed state. It minimizes distance, not Hamiltonian energy, and breaks ties deterministically. This still does substantial work, so its time is reported separately. It has an explicit 20-variable ceiling. A larger instance will require an appropriately budgeted decoding method; silently running an exact energy solver as "repair" would invalidate the benchmark.

## 9. How to know whether the research works

There are three comparison categories in the report:

- **SA:** a randomized classical search that occasionally accepts uphill moves. Compare achievable feasible energy and repeat over seeds. The foundation uses a simple feasible one/two-bit proposal scheme; this can miss disconnected parts of the feasible set and is not a production baseline.
- **Gurobi:** a mathematical optimizer that can certify small constrained binary optima. Its incumbent is only proven optimal when the bound/status support that claim. Time-limited output may be useful without being exact.
- **MOFTransformer or CGCNN screening:** models score already assembled candidate structures, then expensive validation examines top-K candidates. These are property predictors that need suitable training/validation targets. MOFTransformer is a Transformer model, not simply another CGCNN.

These comparisons answer different questions. Under a shared H, compare optimization quality. Under independently evaluated material properties, compare candidate ranking or recovery. A heuristic can minimize a poor H perfectly and still propose poor materials.

Primary metrics are valid binary energy, feasibility rate, gap to a certified optimum and success rate over independent seeds. Material metrics need real structures and labels. Runtime is secondary; CPU timings do not establish lower hardware energy consumption. The professor explicitly asks that the headline be quality, not a presumed speed victory over highly optimized solvers.

## 10. Why synthetic data first?

CoRE gives us structures, not the answer to "what is the universal J for these two hypothetical blocks?" Deriving that J depends on environment, geometry and how the full-material property is decomposed. More favorable adsorption energy alone can also conflict with easy regeneration, moisture tolerance or transport.

Stage A uses deliberately simple coefficients with exact tiny answers. It tests indexing, signs, constraints, solver handling, rounding and evaluation. Stage B introduces justified heuristics and then DFT-grounded parameters with provenance and independent validation. You should be able to swap datasets without rewriting the solver.

Never tune h/J to make selected known structures win, then claim their recovery is independent validation. Freeze the parameterization and evaluate on structures not used to set it.

## 11. Working through the four phases

Phase 1, weeks 1-3: understand Lucas's mapping methods, define the selection graph and constraints, run tiny controls, and map the literature and data sources. Phase 2, weeks 4-6: validate the lab integration on convex controls, investigate nonconvex handling, and pilot roughly 50 variables after replacing tiny-only decoding. Phase 3, weeks 7-9: freeze benchmark datasets, scale and compare all baseline categories. Phase 4, weeks 10-12: validate material claims, analyze failures, and write the manuscript. These are provisional relative estimates.

Start with the commands in `README.md`. Inspect `data/synthetic/toy.json`, then `mof_dac/data.py`, `formulation.py`, `optimizers.py` and `__main__.py`. Read `results/demo.json` after running. Check whether selected bits are feasible before interpreting their energy. That habit is the first safeguard against an impressive-looking but invalid research result.

Sources: local report pp.1-4 and professor feedback; external primary references and precise upstream review details are listed in [docs/references.md](docs/references.md). Chemical explanations are introductory interpretations, not a validation of the proposed material class.
