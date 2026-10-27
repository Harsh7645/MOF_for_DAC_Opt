# Confirmed future convergence rules v3 — 27 October 2026

The user explicitly confirmed the energy algebra and force criterion in the
scope-revision instruction. This supersedes the **pending algebra confirmation**
in v2.1 as current guidance; prior documents and sealed inputs remain unchanged.
No new DFT inputs, resource allocation or calculation are authorized.

For fixed earlier/later geometries A/B, with exact species/order/cell and atom
correspondence, define for protocol p:

`DeltaEc(p)=Ec(B,p)-Ec(A,p)`

`DeltaEh(p)=Eh(B,p)-Eh(A,p)`

`DeltaEg(p)=DeltaEc(p)-DeltaEh(p)` (**guest-associated**, not pure binding).

For a registered refinement r versus reference p, independently require:

- `Sc=abs(DeltaEc(r)-DeltaEc(p)) <= 2.0 meV`.
- `Sh=abs(DeltaEh(r)-DeltaEh(p)) <= 2.0 meV` where matching hosts are included.
- `Sg=abs(DeltaEg(r)-DeltaEg(p)) <= 2.0 meV` where decomposition is included.
  **Test Sg directly**; separate Sc/Sh passes do not imply its pass.
- For **each** structure: `max_i ||Fi(r)-Fi(p)||_2 <= 0.005 eV/Angstrom`, with
  exact atom correspondence, all atoms and no exclusions. This is a vector
  difference, not difference of magnitudes, RMS or maximum component. Report
  signed components/group summaries only as supplementary diagnostics.

No per-atom energy normalization. Missing applicable results mean unevaluated,
not passed. SCF convergence, numerical sensitivity and physical/model accuracy
are separate judgments. Thresholds are sensitivity criteria, not absolute error bounds.

**Both comparisons must be recorded:** successive registered refinements, and
the eventual common refined protocol directly versus the original baseline.
The latter measures baseline sensitivity/cumulative drift; do not conceal it.
**A failed refined-versus-baseline sensitivity comparison does not prevent a
later refined protocol from converging against still finer registered settings.**
Report adjacent-refinement convergence and baseline drift separately. A sensitive
baseline remains unsuitable for central quantitative claims; do not waive that
fact or falsely label the later protocol unconverged solely because it differs
from baseline. One passing step is not a universal convergence proof.

Changed machine/build requires separately authorized baseline continuity checks.
Inspect actual FFT grids in future outputs. Water-only checks do not validate
hosts/CO2; cutoff, density/grid, SCF and k-point checks remain distinct. Same
composition differences do not depend on the unresolved ODAC25 reference mapping.

Under [the revised scope](RESEARCH_SCOPE_REVISION_20261027.md), these are future
extension rules. Higher-memory access and additional DFT are not Phase 3 closure
dependencies. The approximately−0.29-meV baseline guest-associated sign remains
unresolved and is not a central claim.
