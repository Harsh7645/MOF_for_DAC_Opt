# Phase 1 formulation contract

Date: 2026-09-10. Status: **frozen for controlled synthetic work; not chemically validated**.
Scope: first concrete Phase 1 research deliverable. Preserve all four phases.

## Decision

Start with a fixed periodic topology, fixed zirconium node chemistry and a finite
set of linker slots. Optimize the linker choice at each slot. Initially allow
no vacancies, mixed metals, protonation changes or node defects. Broader chemistry
can be a separately named model once assembly and charge rules are established.

This is an engineering proposal, not a conclusion dictated by the report. It
reduces ambiguity between selecting a component type and specifying its count
and placement. It also retains a direct mapping back to a reference structure.

| Encoding | Variables | What it determines | Limitation | Decision |
|---|---|---|---|---|
| Type presence | x_k: type k is present somewhere | A set of types | No count, position or unique assembled structure | Keep existing toy as a software test only |
| Slot occupancy | x_sk: slot s uses option k | A labeled assignment on a fixed template | Needs template, periodic contacts and symmetry handling | Recommended initial research model |
| Counts/composition | n_k or binary-encoded counts | Composition totals | Different spatial arrangements collapse together | Possible composition-screening ablation later |
| Topology/defect co-design | Occupancy, vacancies, node and bond variables | Broader structural design | Larger constraint/assembly problem and more parameters | Defer until simpler model is validated |

Primary literature reports mixed-linker UiO-66 models with six BDC linkers in a
primitive-cell representation, supporting the plausibility of slot-based
functionalization studies. This does not supply this project's geometry or
coefficients. Cell convention must be fixed from an actual reference structure.
[Mixed-linker UiO-66 study, DOI 10.1039/C6CP07801J](https://pubs.rsc.org/en/content/articlehtml/2017/cp/c6cp07801j).
Only the indexed methods excerpt was accessible in this session; full methods
and supplementary structures still need review.

## Variable contract

- S slots, each with an allowed set K_s. Flatten (s,k) deterministically into
  index i. Record slot ID, option ID, cell reference, periodic image convention
  and multiplicity in metadata.
- x_sk in {0,1}; exactly one option occupies each slot. A value between zero
  and one is a numerical relaxed state, not a synthesis ratio or probability.
- Optional metal-type bits y_m satisfy sum_m y_m=1. With one fixed metal type,
  y_0=1 can be eliminated algebraically. Record this elimination, its constant
  energy contribution and any linear linker contributions from y_0*x_sk.
- Variable count before metal elimination is |M| + sum_s |K_s|. Six slots and
  two options per slot yield 12 linker bits and 64 slot assignments, despite
  4096 unrestricted linker-bit assignments. This example count is combinatorial,
  not evidence of 64 distinct crystals after symmetry.

## Objective and interactions

Let i denote a slot-option variable. Use the existing polynomial

\[
H(x)=c+h^Tx+\tfrac12x^TWx,
\]

with symmetric zero-diagonal W. Here c is a documented constant if variables
were eliminated; current core has no constant field, so such preprocessing must
retain the offset externally until an explicit implementation is added.

Interpret h_sk as a slot-conditioned surrogate contribution, not a universal
free-linker adsorption enthalpy. Pair J_(sk,tl) depends on the chosen template
and periodic contact enumeration. Store an unordered variable pair once;
aggregate any symmetry-equivalent/contact multiplicities explicitly. Do not
count the same periodic physical interaction twice.

For alternatives in the same slot, co-selection is forbidden by one-hot rows.
Set within-slot pair terms to zero in the initial model and record that choice.
Though those products vanish for feasible bits, arbitrary within-slot penalties
would change the continuous relaxation. Do not add them as an invisible tweak.

Scores remain dimensionless synthetic values initially. A later heuristic stage
may use amine-related features and geometric compatibility, but the coefficients,
normalization and conditions need independent calibration. A lower H is not
automatically higher uptake, selectivity or easier regeneration.

## Explicit constraints

Occupancy and metal selection:

\[
\sum_{k\in K_s}x_{sk}=1\ (s=1,\ldots,S),\qquad \sum_m y_m=1.
\]

Budget on a functionalized subset F_s:

\[
B_{min}\leq\sum_s\sum_{k\in F_s}\nu_s x_{sk}\leq B_{max}.
\]

nu_s is a fixed integer count of represented slots, not a floating estimate.
Full occupancy already fixes the total number of linkers. A total-linker budget
below that fixed count makes the model infeasible; a budget above it adds no
restriction. If the professor intends variable total occupancy, vacancy choices
and their charge/coordination consequences must be designed first.

Charge balance with a consistent cell convention:

\[
q_{fixed}+\sum_m N_m q_m y_m+
\sum_s\sum_k \nu_s q_{sk}x_{sk}=q_{target}.
\]

All species counted by q_fixed, N_m and nu_s must refer to the same periodic cell.
If all permitted linkers have identical charge and occupancy is fixed, this row
may be redundant or reveal an inconsistent template. Preserve it as a scientific
audit. The SLSQP wrapper now checks augmented-matrix consistency, normalizes rows
and passes an independent equality basis to SciPy while checking final states
against every original row.

Hard pair incompatibility: x_sk+x_tl<=1. Metal-option compatibility can similarly
use y_m+x_sk<=1 for forbidden combinations. Never infer such rows solely from an
arbitrary positive soft cost. Geometry-based exclusion needs evidence and a
documented tolerance. Missing-linker defects need explicit charge compensation;
they are not modeled by deleting a linker bit without changing other rules.
[Free Energy of Ligand Removal in UiO-66](https://pmc.ncbi.nlm.nih.gov/articles/PMC5010357/)
identifies charge-compensation modeling as part of defect calculations; full-text
access was challenged in this session, so detailed defect energetics remain unread.

## Worked numerical example (abstract, not a UiO-66 cell)

Three slots each have choices A or B. Let z_s=1 mean choice B, and use x_sA=1-z_s,
x_sB=z_s. Fix exactly two B choices: z_0+z_1+z_2=2. Example objective:

\[
H(z)=-2z_0-z_1-0.5z_2+3z_0z_1-z_0z_2.
\]

| B-selected slots | z | Feasible energy |
|---|---|---:|
| 0, 1 | (1,1,0) | 0 |
| 0, 2 | (1,0,1) | -3.5 |
| 1, 2 | (0,1,1) | -1.5 |

The best assignment is B/A/B. This can be encoded with six one-hot linker bits
or three reduced bits; binary energies must match after substituting out A.
Different encodings/relaxations should be named and compared, not silently swapped.
The relaxed z=(0.5,0.5,1) satisfies the budget, but thresholding at >=0.5 selects
three B choices and violates it. Numerical decoding still requires validation.

## Lucas mapping notes: what applies here

Lucas uses assignment bits and squared counting constraints in several mappings;
graph coloring section 6.1 is a useful analogy for exactly-one option per slot.
The analogy concerns assignment constraints, not a claim that MOF chemistry is
graph coloring. Sections 3 and 5 are next reading targets for linear constraints
and inequalities. [Lucas (2014)](https://www.frontiersin.org/journals/physics/articles/10.3389/fphy.2014.00005/full).

Independent derivation for a one-hot slot:

\[
\rho(\sum_k x_k-1)^2=
\rho[1-\sum_k x_k+2\sum_{k<l}x_kx_l]\quad\text{on bits}.
\]

For equality rows Ex=e, current equality-penalty export correctly retains
rho*e^T e as an offset. It is not a full unconstrained QUBO while Ux<=u remains.
For an integer inequality a^T x<=B, introduce integer slack s>=0 with a verified
finite range and encode a^T x+s=B. Squaring a^T x-B directly incorrectly penalizes
feasible under-budget states. Float-valued physical constraints need a justified
discretization before using integer slack encodings.

A conservative independent sufficient penalty bound: if every violation has
integer squared residual at least 1, a feasible assignment exists, and R is an
upper bound on the base objective's total range, rho>R separates all infeasible
states from a feasible optimum. For our polynomial, sum|h_i|+sum_{i<j}|J_ij|
is one loose range bound. Loose bounds may damage conditioning; explicit
constraints avoid choosing penalties for the main SNN-QP route.

## Before freezing real chemistry

1. Select a licensed reference CIF, identify cell convention and build stable
   slot IDs. Confirm an unambiguous assembly/reconstruction procedure.
2. Agree initial linker option identities, functionalization positions and
   protonation states. Do not import a linker based only on its display name.
3. Verify multiplicities and charge inventory, including node oxygen/hydroxyl
   species and capping groups. Reconcile formula-level and geometric counting.
4. Specify whether the budget constrains functionalized linkers, composition,
   total occupancy or cost. These are distinct models.
5. Specify the physical evaluation target and conditions: pressure/CO2 fraction,
   temperature, humidity, uptake/selectivity/regeneration metric and data split.
6. Agree symmetry deduplication and which known structures are representable.
   A restricted library cannot recover arbitrary CoRE entries.

## Next executable slice

Generate synthetic slot-assignment instances independent of chemistry. Include
sizes, multiple seeds, hard incompatibilities, contradictory budgets, equal-energy
degeneracy and fractional rounding failures. Compare direct assignment enumeration
against matrix energy; retain the original toy regression. Handle redundant
equalities before claiming robust SLSQP support for explicit charge-audit rows.

Then validate a genuine convex SNN control. Nonconvex SNN experiments remain a
separate Phase 2 decision. Execution evidence is in `PHASE1_SUMMARY.md`.
