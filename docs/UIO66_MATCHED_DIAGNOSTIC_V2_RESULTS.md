# Matched diagnostic v2 — executed results

2026-10-05. **Execution complete; numerical stability mixed; return for review.**
All48 registered relaxation paths completed. No replacement host, pose repair,
retry, deadline extension, refit,64-design expansion or DFT calculation occurred.
The failed sampling pilot and both previous preparation versions remain unchanged.
The two ordered patterns are computational models, not experimentally validated materials.

## Execution and evidence

- Private Kaggle Version1,355186088: [saved run](https://www.kaggle.com/code/sahuharsh/uio66-matched-diagnostic-v2?scriptVersionId=355186088).
- Actual allocation: **two Tesla T4s,15360MiB each**. GPU UUIDs, environment,
  pinned checkpoint and release hashes retained in `raw/matched_diagnostic_results_v2/allocation.json`.
- First-cell start2026-10-04 14:13:15.893UTC. Controller completed after1203.408s,
  both workers exit0. Kaggle total1227.2s (**20min27s**, approximately0.682 allocated
  GPU-hours), including setup and finalization; well below115min worker/120min cap.
  Zero active events independently observed after completion. External conservative
  submission bound14:12:45UTC was also respected.
- **24/24 guest paths:**16 matched continuations,4 original-pose replays,4 rigid controls.
  **24/24 reference paths:**2 initial bare hosts,2 isolated gases,20 derived empties.
  **0 incomplete,0 failed,0 scientific holds.** One exact common-host single point.
- Runtime passed actual-GPU, package/74file, fixed-input, and checkpoint checks
  before model workers. Executed notebook code matches the authorized launch copy.
  Only launch-copy changes were the approval flag, byte-identical `.bin` transport
  (Kaggle auto-extracts ZIPs), and an additional bundle-SHA assertion.
- Frozen bundle SHA256:
  `027f634ce1545c5810f9e19535ef5dd190df6714999a5e28d5502d171b50c83a`.
  UMA checkpoint SHA256:
  `b2673b85037b075674c25f55c34ffe1ff1e15db924be977b10a184765df0d5ce`.
- [Local evidence directory](../artifacts/phase3/uio66_matched_v2_results_20261005/):
  downloaded archive110588341bytes, SHA256
  `b448c23d138163d46e43c6f11877f93e8465edf5996e1ef3a49f26ffe013f153`.
  Archive CRC,469 recorded raw-output hashes and74 release hashes verified.
  Independent local assessment agrees with the remote JSON to1e-10 numeric tolerance.
  Tuple/list serialization was normalized for comparison; scientific values unchanged.
  The archive and raw files are retained separately from derived local analysis.

## Shared host and rigid controls

The registered empty110111 seed reached0.005eV/A. Exact-host single-point energy
**-919.262007122586eV**, force maximum**0.00434184eV/A**. Geometry SHA256
`d64b90a44b0bb53fd1a2c1779c034fd60c36c9e5b46e337da9c23e04ecc9a964`.
All four mappings passed before rigid inference; local reconstruction reproduced
each mapped geometry hash. Every rigid checkpoint retained this exact host.

| Guest source | Minimum host/guest distance(A) | Maximum Zr translation residual(A) |
|---|---:|---:|
| CO2 start7 |1.779080|0.010392|
| CO2 start31|2.873757|0.011406|
| H2O start6 |1.488981|0.018859|
| H2O start28|1.946815|0.008854|

All four rigid energy changes passed the initial5meV target. Three crossed0.01
and0.005 in the same step, so their zero last-change values are **coincident
checkpoints**, not independent confirmation at two geometries. Final unconstrained
all-atom force maxima were0.07618,0.14139,0.34050,0.47700eV/A respectively:
the guest converged under the constraint; the adsorbed frozen host is not relaxed.

## Checkpoint energy and geometry changes

All144 checkpoint structures independently satisfy their recorded mobile-force
tolerance and saved energy. **44/48 component paths** meet the initial
`abs(E_0.005-E_0.01)<=0.005eV` diagnostic target:20/24 guests and24/24 references.
This target measures checkpoint sensitivity; it does not certify physical accuracy
or convergence below0.005eV/A. Three of16 matched guests and one replay fail it.

| Path | dE0.02→0.01(eV) | dE0.01→0.005(eV) | Last host max movement(A) | Last guest max movement(A) |
|---|---:|---:|---:|---:|
|000000 CO2 batch1 targeted/start16|-0.000988|-0.017750|0.216762|1.201771|
|110111 CO2 batch0 targeted/start7|-0.075054|-0.013874|0.489633|0.128863|
|110111 CO2 original-pose replay/start31|-0.005257|-0.007480|0.551971|0.084816|
|110111 H2O batch1 random/start28|-0.008063|-0.041461|1.252070|0.179017|
|110111 CO2 batch1 random/start31|-0.010044|-0.003302|0.301563|0.143109|

Displacements are atom-indexed minimum-image differences, including collective
translation; they are not distances between proven physical basins. The last row
passes the energy target despite measurable continuing framework motion.
For CO2/start7, the earlier0.02→0.01 interval moves a guest atom3.05360A and a host
atom1.36821A. Its last interval moves L4 aminoN6 by0.48963A and rocks L4 by6.65degrees.
For H2O/start28, the last interval moves L5 aminoH123 by1.25207A and N9 by0.91506A;
L3/L5 rings rock11.40/18.36degrees. These are substantial conformation changes
requiring expert review. The registered image-aware bond-cutoff detector reported
no connectivity change; that does not exclude subtle chemical/model problems.

All48 rows, absolute energies and both geometry intervals:
[checkpoint CSV](../artifacts/phase3/uio66_matched_v2_results_20261005/analysis/checkpoint_changes.csv).
Contacts, amino torsions and ring/OH descriptors at each guest checkpoint:
[geometry JSON](../artifacts/phase3/uio66_matched_v2_results_20261005/analysis/geometry_analysis.json).

![Energy sensitivity](../artifacts/phase3/uio66_matched_v2_results_20261005/analysis/energy_stability.png)

Each gas was assessed separately using the frozen reference rules. The same four
guest paths fail the adsorption-energy target: changes-0.017727,-0.013260,
-0.006866,-0.040847eV in table order. All24 reference last changes pass; the largest
reference change is0.004043eV. **5/8 matched CO2-minus-H2O pairs pass**, with both
gases individually stable;3/8 fail. Paired cancellation was not used to pass an
unstable gas. Detailed values remain in `local_assessment.json`.

## Reproduction of the original start31 motion

The fresh continuation's0.02 checkpoint reproduces the archived tighter endpoint:
complex energy difference**+0.000000717eV**, maximum indexed displacement
**0.00010998A**. This strongly supports numerical reproducibility for this input,
model and optimizer procedure, not independent validation of the energy model.

Through0.005, the complex loses0.0869624eV relative to its frozen0.05 input.
The trajectory remains gradual: largest adjacent-frame decrease0.0019813eV.
H15···CO2O126 shortens2.86024→about2.20A during the original approach, then ends
at2.28505A. L1 rocking reaches12.45369degrees relative to input. Later relaxation
includes L3 amino/linker motion: total H118 displacement1.17042A and N7 displacement
0.88281A. It is a coupled guest/framework rearrangement, not merely guest translation.

![Start31 continuation](../artifacts/phase3/uio66_matched_v2_results_20261005/analysis/start31_continuation.png)

## Original-pose replays versus endpoint continuations

Final0.005 comparisons; dE=replay minus matched complex. Guest RMSD accounts for
the identical guest-atom swap and removes mean indexed-Zr translation. It does
not test all framework symmetries or lattice-site equivalences.

| Design/gas | dE(eV) | Guest RMSD(A) | Host RMSD(A), Zr translation removed |
|---|---:|---:|---:|
|000000 CO2|-0.00000794|0.004553|0.000875|
|000000 H2O|+0.00050966|0.031087|0.006615|
|110111 CO2|+0.00048247|0.035212|0.012793|
|110111 H2O|-0.00024969|0.031466|0.011473|

All four are numerically close at the final tolerance. Close final agreement can
coexist with different intermediate first-crossing energies:110111CO2 replay
fails its last-change target while the matched continuation passes. These are
matched inputs, not four independent adsorption-site discoveries. Contact labels
are cutoff descriptors; a minor label difference does not alone prove another motif.

## Rigid versus flexible and remaining sampling sensitivity

|110111 source|Rigid minus flexible complex energy(eV)|Guest RMSD(A)|Host RMSD(A)|
|---|---:|---:|---:|
|CO2 start7|+0.084888|2.517943|0.321589|
|CO2 start31|+0.020724|0.270435|0.229858|
|H2O start6|+0.110504|2.145393|0.362990|
|H2O start28|+0.064865|0.248244|0.312146|

RMSDs here remove indexed-Zr translation. Differences combine host constraints,
different initial host conformations, translation mapping/contact changes, and
possibly different reached basins. They **cannot isolate a causal flexibility
benefit**. Binding-energy differences use the above values only if both complexes
are explicitly referenced to the sameH* and gas; the ordinary flexible common-bare
reference is different. One shared host removes variation among rigid host
references but does not resolve these remaining confounders.

Across the four matched starts per design/gas, final energy spans are:
000000CO2=0.000448eV;000000H2O=0.263261eV;110111CO2=0.022716eV;
110111H2O=0.022081eV. These support configuration/site sensitivity, especially the
weak000000H2O random endpoint; they do not count minima or establish global minima.
The old509 clusters remain diagnostic descriptors, not proven physical minima.

## Assessment and next decision

1. **Incomplete relaxation supported:** original loose checkpoints change materially
   on continuation; three matched paths and one replay still fail the initial
   last-energy-change target even though all final mobile forces satisfy0.005.
2. **Missed configurations remain plausible:** different fixed starts retain
   different energies/contact geometries. This small selected diagnostic cannot
   distinguish exhaustive coverage, basin equivalence, or unsampled lower states.
3. **Host-conformation effects supported as a component:** linker/amino motion is
   directly observed and rigid/flexible outcomes differ. Magnitudes are not a
   pure constraint-only causal estimate.
4. **UMA error remains unresolved:** internal reproducibility cannot establish
   physical correctness. Expert review should first examine the larger L3/L5
   water-associated motion and CO2/start7 relocation, along with parent coordinates,
   node protons and amino orientations. No proton transfer/decoordination was
   flagged by the operational graph check; chemistry review is still required.

**Decision: retain NO-GO for model refitting or64-design expansion. Review these
results before choosing any further calculation.** A specific later DFT diagnostic
could compare expert-approved frozen pre/post-rearrangement geometries and forces
for110111H2O/start28 (0.01 versus0.005) and/or CO2/start7, with consistent empty/gas
references. This is a proposal only, not an approved or launched DFT job. A smaller
numerical force threshold alone cannot validate UMA or establish material ranking.
Historical51/13 split/fit retained; viewed13 designs remain development evidence.
ODAC25 reference-field mismatch remains a separate unresolved workstream.

## Reproduction and checks

Frozen assessor rerun locally, raw output unmodified; independent report saved as
`artifacts/phase3/uio66_matched_v2_results_20261005/local_assessment.json`.
Supplemental CPU-only script added:

```powershell
python -m scripts.summarize_uio66_matched_results --manifest artifacts/phase3/uio66_matched_v2_results_20261005/raw/matched_diagnostic_frozen_v2/manifest.json --raw artifacts/phase3/uio66_matched_v2_results_20261005/raw/matched_diagnostic_results_v2 --output tmp/matched_geometry_review
python -m pytest tests/test_matched_diagnostic.py tests/test_shared_rigid_host.py -q -p no:cacheprovider --basetemp=tmp/matched_review_tests
```

Choose a new output directory; the summary script refuses to overwrite analysis.
CPU integration checks:48paths/144checkpoints,4mapping reconstructions pass.
Safety tests: **15passed in4.04s**. Initial test invocation hit Windows temporary
directory permissions; a fresh repository-local temp directory resolved this.
ASE/NumPy deprecation warnings remain. No model inference ran locally.
