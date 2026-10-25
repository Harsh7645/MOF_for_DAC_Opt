# Water convergence v2.1 - review package, no execution

Current interpretation/specification:
`SPECIFICATION.md` here, also `docs/UIO66_QE75_WATER_CONVERGENCE_V2.md` in the repository.
This portable directory has four exact inputs: **two density checks**, plus
**two separately budgeted baseline reproductions only if machine/build changes**.
It also includes five approved UPFs, two exact geometry JSON files, the unchanged
254-row atom map, archived baseline energy/force reference, and offline verifier.
No baseline source, completed result, previous plan or approval is rewritten.

## Offline verification (Windows or Linux; Python 3.10+, standard library)

After comparing the downloaded ZIP SHA256 and hash-manifest pin with its receipt:

```powershell
python verify.py --package .
```

This only verifies preparation and registered arithmetic; it cannot launch QE,
MPI, services, SSH, builds or installations. Passing is not scientific convergence.
Energy formula reconstruction remains pending the focused question below.
The primary force target is max_i norm2(F_refined-F_reference) <=0.005 eV/Angstrom
per structure over all 127 atoms; no exclusions. The energy sensitivity target
is 2.0 meV per comparison, with no per-atom normalization. See assessment-spec.json.

## Input use after separate environment verification and execution authorization

For each job, use a NEW private work directory, copy its selected input as
`input.in`, place the bundled UPFs in `pseudo/`, and use private `scratch/`.
Relative paths already match; do not edit scientific input bytes, atom order,
cell, prefix, CG/mixing controls, charge/spin or occupations. No directories are
created by this preparation for remote runs. Preserve all earlier scratch.

- D01/D02: 80/750 Ry. Only ecutrho differs from the converged water executions.
- R01/R02: 80/600 Ry exact converged execution inputs, conditional prerequisite on
  machine/build changes, with a separate 8-hour / 32-core-hour ceiling for the pair.
- D01/D02 have their own 8-hour / 32-core-hour pair ceiling. If reproduction is required,
  total proposed exposure is 16 hours / 64 core-hours (four jobs), not 8 hours. These are maxima,
  not expected runtimes. No runtime allocation is confirmed or authorized.
- Each job is sequential, one attempt, maximum 4 hours including setup/finalization.
  No retry, repaired pose, cutoff substitution or deadline extension.

The machine is UNASSIGNED. Proposed workstation requirements are 32 GiB physical,
24 GiB available at launch,20 GiB hard job memory, graceful stop at 18 GiB aggregate
job memory, zero job swap, four physical cores/four bound MPI ranks/one thread,
and preferably 100 GiB usable persistent storage. Actual scheduler, account,
CPU topology, enforcement, executable/build/MPI and storage/retention must be
verified. Workstation controls are not automatically a Slurm configuration.
The old laptop 10/11 GiB limits remain unchanged. No launch command is provided.

Keep complete inputs, checksums, build and allocation, stdout/stderr/XML, all
forces, measured FFT/G counts, resource accounting, checkpoints and failures.
Verify actual dense/smooth grids from eventual outputs;750Ry predictions in
historical v1 are not observed values. Water complexes alone cannot test host
or CO2 energy differences. A passing refinement is not an absolute error bound;
apply both criteria between successive registered refinements AND compare the
eventual common refined protocol directly against the original archived baseline.

Later 100/750, 120/750 and density toward 900 Ry are conditional proposals only.
Tighter-SCF and k-point checks remain separate. None of their inputs, launches
or budgets is authorized/prepared here. Phase 3 remains incomplete.

## Confirmed scope; remaining formula confirmation

Both comparison routes are user-confirmed. No machine is selected.

The comparison routes are now confirmed: successive registered refinements AND eventual common refined versus original baseline. Please confirm only the reconstructed energy algebra: Sc=abs(DeltaEc(r)-DeltaEc(p)), Sh=abs(DeltaEh(r)-DeltaEh(p)), Sg=abs([DeltaEc-DeltaEh](r)-[DeltaEc-DeltaEh](p)), each <=2.0 meV without per-atom normalization. Is this the intended reconstruction of the malformed table?
