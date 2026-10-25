# Professor review: frozen UiO-66 DFT baseline

2026-10-10. **Decision requested: numerical acceptance rules and a suitable
allocation for the proposed convergence checks. No execution approval assumed.**
All 14 baseline SCFs are complete; Phase 3 is incomplete. Ordered patterns are
computational models, not validated material rankings.

## Evidence and conventions

Seven exact saved complex geometries and their seven matching guest-stripped
hosts were evaluated without ionic/cell relaxation: QE 7.5, periodic PBE-D3(BJ)
(pairwise, three-body disabled), approved SSSP 1.3.0 PBE Precision potentials,
80/600-Ry wavefunction/density cutoffs, Gamma sampling, neutral nonmagnetic fixed
occupations, electronic convergence threshold 1e-8 Ry.

Windows previously verified **471 payload hashes, 14 SCFs and 1,717 force vectors**;
42 targeted tests passed. This packet reuses that verified offline analysis; no
completed audit or calculation was rerun. Source archive SHA256:
`8f7fbf7abc4839117595f18e14b42db05d8392547cede539232ae937e99bf0d7`.
The checkpoint labels below are **UMA relaxation force tolerances in eV/Angstrom**,
not DFT force convergence thresholds. Within each row, B is the later/tighter
checkpoint and A is the earlier checkpoint, at identical composition.

\[
\Delta E_c=E_{complex}(B)-E_{complex}(A),\qquad
\Delta E_h=E_{stripped\ host}(B)-E_{stripped\ host}(A)
\]
\[
\Delta E_{guest-associated}=\Delta E_c-\Delta E_h,\qquad
D=\Delta E_c^{DFT}-\Delta E_c^{UMA}.
\]

Negative means lower energy at B; positive means higher. **All table values are
meV; 1 meV = 0.001 eV.** Each host retains the exact corresponding complex's host
coordinates and cell. No relaxed-host or isolated-gas reference enters these
same-composition differences; they are independent of the ODAC25 reference mismatch.
Guest-associated includes interaction, guest internal deformation and periodic
image effects. It is not a pure adsorption energy. Four UMA host single points
remain missing, so a complete analogous UMA host decomposition is unavailable.

|Frozen checkpoint transition|DFT complex|UMA complex|DFT minus UMA|DFT host|DFT guest-associated|
|---|---:|---:|---:|---:|---:|
|110111 H2O s28: 0.010 to 0.005|-38.396707|-41.461081|+3.064374|-21.725487|-16.671220|
|110111 CO2 s7: 0.020 to 0.010|-79.440623|-75.053958|-4.386665|+1.189612|-80.630235|
|110111 CO2 s7: 0.010 to 0.005|-10.155191|-13.873650|+3.718459|-9.860710|-0.294481|
|000000 CO2 s16: 0.010 to 0.005|-15.607560|-17.749933|+2.142373|-0.203710|-15.403850|

## Why the small CO2 remainder is unresolved

For 110111 CO2 s7, 0.010 to 0.005:

\[
-10.155190922-(-9.860709655)=-0.294481267\ \mathrm{meV}.
\]

Nearly the entire complex decrease is matched by a decrease in the stripped-host
energy. Subtracting those similar changes leaves a small guest-associated
remainder. Its negative sign is arithmetic at the current settings, **not yet a
numerically reliable stabilization sign**. The initially suggested 2-3 meV
stability targets exceed this remainder and are not measured error bars.

Numerical cancellation cannot be presumed: an error in the remainder is
`error(Delta Ec) - error(Delta Eh)`; its worst-case magnitude can be the sum of
those errors. Correlation might help, but has not been established. Test the
remainder itself with matched complex/host settings; a water-complex-only check
cannot establish this CO2 remainder's sign. Preserve full precision internally;
six-decimal table formatting does not assert six-decimal physical accuracy.

## Confirmed baseline versus open conclusions

**Confirmed from archived results:** all 14 SCFs converged with unchanged frozen
geometries, approved settings/potentials and finite mapped forces. DFT and UMA
complex changes have the same negative sign for all four comparisons; their
changes differ by 2.142-4.387 meV. At this baseline, the water decomposition has
negative host and guest-associated terms; the last CO2 s7 decrease is mainly in
the host term. These are computed decompositions, not proven causal mechanisms.

The largest force across all 14 structures is **0.565884531 eV/Angstrom**, on H
(QE atom115/source index114) in water f0.010 stripped host. The archived report's
0.435954 value is the largest new *complex* force; raw evidence remains unchanged.
Frozen snapshots are not DFT-relaxed minima. SCF convergence and parser consistency
do not establish basis/grid convergence or physical accuracy.

**Still open:** density/grid and wavefunction-cutoff convergence, electronic
threshold sensitivity, k-points, transfer from water complexes to hosts/CO2,
persistent negative pseudocharge behavior, functional/pseudopotential model error,
parent/proton correspondence and amino geometry. No UMA accuracy claim, material
ranking, SNN advantage or Phase 3 completion follows from this baseline.

## Acceptance decisions needed before new results

1. Choose one binding energy threshold, not the historical **2-3 meV range**, and
   define its scope: complex change, host change and guest-associated remainder.
   For the density pair assess
   `delta(Delta E) = [E(B,750)-E(A,750)] - [E(B,600)-E(A,600)]` in signed and
   absolute meV, plus individual cutoff shifts. A sub-meV sign claim needs a
   correspondingly justified uncertainty bound; ordinary target acceptance alone
   does not resolve the -0.294481-meV remainder.
2. Choose one force threshold, not the historical **0.005-0.01 eV/Angstrom range**,
   and the primary statistic: maximum absolute Cartesian component, maximum
   per-atom vector norm, group RMS, or a specified combination. Define the atom
   groups and outlier rule. Compare `delta F_i = F_i(750)-F_i(600)` at each exact
   frozen geometry; do not apply the tolerance to the force magnitude itself.
3. Preserve/report all signed components, vector norms, group RMS/maxima and
   whole-structure maxima, including water, moving amino/linker atoms and node
   protons. Use the registered atom mapping. Projections onto archived local
   motion are optional diagnostics; zero-motion directions are undefined and
   optimization secants are not physical diffusion paths.
4. Register how negative pseudocharge, actual FFT/G counts, SCF failures and
   resource stops affect assessment. Unconverged/stopped runs are diagnostic only.
   Existing serialization/text-XML tolerances are provenance checks, not numerical
   acceptance thresholds. Two cutoff points test sensitivity, not an asymptotic limit.

## Proposed compute, not a confirmed allocation

**First stage already prepared:** two frozen water-complex SCFs at 80/750 Ry;
only ecutrho changes from 600 to 750. Same scientific conventions and verified
QE/MPI build, clean separate scratch, four physical CPU cores/four bound MPI ranks,
one thread per rank, no GPU and no checkpoint reuse. No initialization-only probe.

|Requirement|Existing proposal; must verify before authorization|
|---|---|
|Host|At least 32 GiB physical RAM and 20 GiB available at launch; no competing QE jobs|
|Job memory|Candidate 15 GiB high /16 GiB hard, zero job swap, 96-task cap; guard/reserve semantics require review|
|Estimate|12.005-13.017 GiB at750 Ry from analytical/calibrated scaling; not a measured peak or guaranteed bound|
|Current laptop|10 GiB high /11 GiB hard remain unchanged: **no-go** for this proposal|
|Disk|At least 40 GiB persistent free; 20 GiB per-job scratch stop and 20 GiB free-disk stop; retain partial outputs/checkpoints|
|Time ceiling|Two sequential jobs, maximum 4 h each including setup/finalization: 8 wall-hours /32 core-hours, not a runtime prediction|
|Stop rules|One attempt/geometry, no retry/extension; graceful exit by 3h40m, external stop 3h54m45s, workers gone by 3h55m, final 5 min retention/cleanup|
|Sequencing|Second job only after first result/resource/control review passes; stop on high/max/OOM/tasks/swap events; preserve failures|

The software/toolchain, scheduler/cgroup enforcement, shared storage and actual
allocation must be verified on the selected host. No cluster CPU entitlement is
inferred from prior SSH access. Four physical cores and time ceilings are proposed
bounds, not an application to an unverified site.

A **separate wavefunction-cutoff stage** and representative host/CO2 checks still
need exact inputs, acceptance scope, resource sizing and bounded authorization.
The earlier 100/750-Ry suggestion changes both cutoffs relative to 80/600; it does
not isolate wavefunction sensitivity. An 80/750 versus 100/750 comparison would do
so at fixed density cutoff, subject to review and further convergence evidence.
Do not inherit the density-pair memory estimate or promise completion for those
larger calculations. Recalculate each affected comparison group at common accepted
settings if the baseline changes; never mix complex/host or endpoints across cutoffs.

## Review sources

- [Windows reconstructed results](UIO66_QE75_WINDOWS_OFFLINE_REVIEW_20261010.md)
- [Portable evidence/retention guide](UIO66_QE75_WINDOWS_BASELINE14_GUIDE.md)
- [Prepared density pair](UIO66_QE75_RHO750_PAIR_PREPARATION_V1.md) (its October 9
  baseline-pending counts are historical; **all 14 baseline SCFs are now complete**)
- [Registered assessment specification](../plans/qe75-rho750-pair-v1/assessment-spec.json)

**Requested response:** fix the energy threshold, force metric/threshold and
scope; identify a suitable allocation; then review a bounded execution package.
This packet itself authorizes no computation. Phase 3 remains incomplete.
