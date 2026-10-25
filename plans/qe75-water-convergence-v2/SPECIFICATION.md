# Current convergence specification: water pair v2.1

2026-10-10. Incorporates the user-supplied scientific review. **Preparation only;
no calculation authorized.** All 14 baseline SCFs are complete; Phase 3 remains
incomplete. This revision supersedes current proposals, not historical results.
The baseline archive, earlier plans and original professor packet are preserved.

## Scientific interpretation

Electronically converged baseline DFT and archived UMA **agree on the direction
of four selected complex-energy changes**. This is not quantitative UMA validation,
numerical convergence or evidence for a material ranking.

For an earlier frozen geometry A and later geometry B, define
`Delta Ec = Ec(B)-Ec(A)`, `Delta Eh = Eh(B)-Eh(A)` and
**`Delta Eg = Delta Ec - Delta Eh`**, called **guest-associated**. Stripped-host
differences compare two **frozen framework conformations**, not deformation from
an equilibrium host. Guest-associated includes interactions and guest internal
deformation; it is not pure binding energy. These same-composition differences
need neither a relaxed-host nor isolated-gas reference; ODAC25 remains separate.

All numbers below are **meV**, later minus earlier; negative means lower energy.
Checkpoint labels are saved UMA relaxation tolerances in eV/Angstrom, not DFT
convergence criteria. The table reuses the verified Windows analysis, not new runs.

|Selected transition|DFT complex|UMA complex|DFT frozen host|DFT guest-associated|
|---|---:|---:|---:|---:|
|110111 H2O s28, 0.010 to 0.005|-38.396707|-41.461081|-21.725487|-16.671220|
|110111 CO2 s7, 0.020 to 0.010|-79.440623|-75.053958|+1.189612|-80.630235|
|110111 CO2 s7, 0.010 to 0.005|-10.155191|-13.873650|-9.860710|-0.294481|
|000000 CO2 s16, 0.010 to 0.005|-15.607560|-17.749933|-0.203710|-15.403850|

The late CO2 remainder is approximately **-0.29 meV, with unresolved sign**:
`-10.155191 - (-9.860710) = -0.294481 meV`. Similar complex/host changes cancel.
Do not prioritize determining this sign unless a scientific conclusion requires it.
Passing the 2.0-meV sensitivity target would not by itself establish this sign.

## Registered sensitivity rules and reconstructed formulas

The **2.0-meV energy threshold** and **0.005-eV/Angstrom force criterion** are
registered by the latest review. The energy table was malformed: the following
formula reconstruction is explicitly **not an exact quotation** and awaits the
focused confirmation below. No per-atom energy normalization is allowed.

For protocol p and the same composition/checkpoint pair:

\[
\Delta E_c^p=E_c^p(B)-E_c^p(A),\quad
\Delta E_h^p=E_h^p(B)-E_h^p(A),\quad
\Delta E_g^p=\Delta E_c^p-\Delta E_h^p.
\]

Reconstructed intended sensitivities, with refined protocol r and reference p:

\[
S_c=|\Delta E_c^r-\Delta E_c^p|\le 2.0\ {\rm meV},
\]
\[
S_h=|\Delta E_h^r-\Delta E_h^p|\le 2.0\ {\rm meV},
\]
\[
S_g=|(\Delta E_c^r-\Delta E_h^r)-(\Delta E_c^p-\Delta E_h^p)|
\le 2.0\ {\rm meV}.
\]

These are separate tests: passing Sc and Sh does not imply passing Sg. Missing
host results mean **unevaluated**, never passed. Immediate water-complex checks
evaluate Sc only, plus the force test separately on A and B:

\[
\max_{i\in\text{all atoms of structure }s}
\|\mathbf F_i^{r}(s)-\mathbf F_i^{p}(s)\|_2
\le 0.005\ {\rm eV/\mathring A}.
\]

All 127 atoms in each water complex participate; **no exclusions**. This is a
maximum vector-difference norm, not a maximum component, RMS, force-magnitude
change or mean over structures. Preserve species/order, cell, coordinates and
source-index/QE-index mapping. Report signed components, per-atom norms and group
RMS/maxima as supplementary diagnostics; groups cannot exclude an outlier from
the primary criterion. XML forces are Ha/bohr; stdout is Ry/bohr; convert explicitly
to eV/Angstrom. Existing serialization/rounding checks remain distinct.

A passing refinement is **sensitivity evidence, not an absolute error bound**.
User clarification (2026-10-10) makes **both routes mandatory**, for both energy
and forces: apply the registered criteria between **each successive registered
refinement**, and compare the **eventual common refined protocol directly against
the original archived baseline**. Register protocols and predecessors before execution;
do not select comparisons retrospectively. A chain of individually passing refinements
cannot substitute for the direct endpoint test. For example, successive shifts of
1.5 meV each pass but their cumulative 3.0 meV fails; successive aligned force
changes of 0.003 eV/Angstrom each pass but cumulative 0.006 fails. These are synthetic
examples, not calculated outcomes.
For changed environments, report both refined-versus-reproduced-baseline and the
direct comparison to the archived baseline; first review reproduction continuity.
No refinement SCF or new sensitivity outcome is presently available.

### Reviewer clarification and remaining formula provenance

The user confirmed both comparison routes and that no machine is selected.
The formulas remain explicitly reconstructed rather than quoted. The previous
question is preserved in the original sealed v2 package and assessment history.
Only the algebra confirmation remains open:

> The comparison routes are now confirmed: successive registered refinements AND eventual common refined versus original baseline. Please confirm only the reconstructed energy algebra: Sc=abs(DeltaEc(r)-DeltaEc(p)), Sh=abs(DeltaEh(r)-DeltaEh(p)), Sg=abs([DeltaEc-DeltaEh](r)-[DeltaEc-DeltaEh](p)), each <=2.0 meV without per-atom normalization. Is this the intended reconstruction of the malformed table?

## Immediate portable inputs

Package directory: `plans/qe75-water-convergence-v2/`.
Two density inputs are **byte-identical to the historical v1 80/750 inputs**.
Each differs from its actual converged 80/600 execution input solely by
`ecutrho=600` becoming `ecutrho=750`. Preserve exact coordinates/cell, approved
potentials, PBE-D3(BJ) pairwise, neutral nspin=1/fixed occupations, Gamma,
`diagonalization='cg'`, mixing history 4, beta 0.3, 1e-8-Ry SCF tolerance,
disk_io high, force output and original clean-start choices. No pose repair,
symmetry standardization, ionic relaxation, new FFT override or checkpoint reuse.

Five approved UPFs, exact geometry JSONs, baseline energy/force references and
the unchanged 254-row atom map travel with the package. The two baseline inputs
are included solely for a **separately authorized conditional reproduction**.
All jobs use separate new work directories with relative `pseudo/` and `scratch/`.
No remote paths are assigned or directories created by this preparation.

Read actual dense/smooth FFT grids and G counts from eventual stdout/XML. Earlier
750-Ry predictions are not observations. Water complexes alone do **not** validate
the host decomposition, CO2 comparisons, physical accuracy or rankings.

Offline verification only (Python 3.10+, no scientific dependencies):

```powershell
python scripts/check_qe75_water_convergence_v2.py
# Or from an extracted portable package:
python verify.py --package .
```

## Environment and bounded staged inventory

**Machine/build not identified. No environment-specific launch proposal can yet
be finalized.** `environment-requirements.json` records null host/build/scheduler
and disabled execution. Confirm actual host identity, QE 7.5/build/hash, compiler/
MPI compatibility/binding, physical cores, memory enforcement/accounting, storage
quota/retention and any scheduler account/partition/QoS/charges. No remote install.

Suggested workstation profile: **at least 32 GiB physical RAM, at least 24 GiB
available at launch, 20-GiB hard aggregate job-memory cap, graceful-stop trigger
at 18 GiB, zero job swap; four physical cores, four bound MPI ranks, one thread
each; preferably 100 GiB usable persistent storage.** The 18-GiB stop trigger is
not silently equated with a scheduler/cgroup throttling limit. The adapter must
measure aggregate job memory and bound graceful termination before the hard cap.
Check usable quota as well as filesystem capacity and preserve earlier checkpoints.

Adapt to actual scheduler rules; do not translate workstation controls into an
unverified Slurm layout. The old laptop 10/11-GiB limits remain unchanged and are
unsuitable. Previous 750-Ry estimates 12.005-13.017 GiB are uncertain estimates, not
measurements or guarantees under a new build. No CPU allocation is inferred from SSH.

|Stage|Jobs|Trigger/order|Explicit proposed ceiling|
|---|---|---|---|
|R: baseline reproduction|R01/R02, exact 80/600 water A/B|Required if machine **or build** changes; complete/review before D|2 x 4 h = 8 wall-hours /32 core-hours|
|D: immediate density check|D01/D02, exact 80/750 water A/B|After environment/input review and R if required|2 x 4 h = 8 wall-hours /32 core-hours|
|Combined if R required|4 sequential jobs|Separate approval/budgets, not hidden inside D|16 wall-hours /64 core-hours|

Each four-hour limit includes preparation and finalization. One attempt/job,
no retry/extension; failed/incomplete/resource-stopped results remain retained
diagnostics, not valid comparisons. Review each terminal result before its successor.
Record clean-start provenance, inputs/UPFs/build, stdout/stderr/XML, all forces,
actual grids, accounting, exit status, failures and full checkpoints. A future
adapter must preserve bounded stop/kill/finalization within the original deadline;
the suggested memory profile is not authorization to change laptop limits.

If unchanged machine/build and archived comparability are verified, reuse completed
baseline rather than rerunning it. Otherwise R is an additional prerequisite with
its own explicit budget. Any reproduction discrepancy is a review hold, not an
automatic retry or permission to alter scientific settings.

## Conditional later proposals only

Record 100/750, 120/750 and a density refinement toward 900 Ry for later review.
Choose a common wavefunction cutoff for density comparisons. Exact later scope,
resources, inputs and budgets are **not approved or prepared for execution here**.
Keep tighter-SCF and k-point checks separate. No automatic ladder of launches.
Apply both registered criteria at every successive registered refinement.
After choosing a common refined protocol, assess it directly against the original baseline;
use consistent settings within every complex/host/guest-associated comparison.
Additional host/CO2 jobs require their own scientific justification and budgets.

Numerical convergence, quantitative UMA accuracy, chemistry review and material
rankings remain unresolved. Four missing UMA host results, the original failed
sampling pilot and ODAC25 reference mismatch remain separate workstreams.
