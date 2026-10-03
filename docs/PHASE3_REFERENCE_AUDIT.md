# Phase 3 material benchmark audit

Updated 2026-10-02. Phase 3 remains incomplete. Numerical benchmarks passed;
the material benchmark must pass the gates below before publication.

## Preserved execution evidence

The saved Kaggle draft contains September outputs: 92 training pairs from
ColabFit `co/co_9.parquet`, 138 validation pairs, and an eSEN run with 68 CUDA
OOM failures in 700.4877 seconds. That model run has no valid full-pool score.
Notebook history survived; its JSON results were not downloaded before the
session ended. UMA's 16-record total-energy smoke is preserved locally and is
separate from this benchmark.

The training mirror supplies `adsorption_energy`, but not the corrected field
or relaxation `fid`. Extraction uses the last stored row per trajectory. This
is a preliminary protocol, not the frozen v1 reduction required by P3.1.

## Reference and geometry gates

[ODAC25 section 3.1, Eq. 2](https://arxiv.org/html/2508.03162#S3.SS1)
uses predicted system/bare-MOF energies with a gas-phase reference. Section
2.1.3 explains the re-relaxed bare minimum. A fixed DFT gas reference can be
a declared protocol; it need not be a model-predicted isolated gas energy.

The old pipeline inferred gas energies from validation medians of
`energy - energy_mof - energy_ads_corrected`. Deviations were approximately
0.705 eV CO2 and 0.756 eV H2O: these cannot be treated as one constant without
resolving the field convention. The pipeline now rejects inconsistent offsets
at 1e-5 eV. This is an identity tolerance, not a model accuracy target.

`kaggle/audit_odac25_references.py` compares corrected/original field
combinations on uniformly spaced records and saves metadata examples. A low
spread alone does not establish physical interpretation; source documentation
and matching bare energies must also agree.

The pool uses DFT-selected strongest sampled adsorption configurations and
the DFT-selected reference bare geometry, once identity matching succeeds. This tests
energy prediction on oracle-selected geometries. It does not test prospective
placement, relaxation, model-selected bare minima, or material discovery.
Different CO2/H2O supercells retain separate bare indices.

## Implemented safeguards

- Notebook packaging-cell syntax corrected; all 21 existing code cells compiled.
  An automated syntax regression check is included.
- eSEN uses heterogeneous `inference_settings="batch"`; rerun pending.
- Training pairs retain bare indices and gas trajectory/source provenance.
- Cached bases bind indices to SHA-256 hashes of all three inputs.
- Optional frozen-target input verifies source index, MOF/gas, trajectory, fid
  and energy instead of rescanning the large target database.
- Inference persists predictions/failures every 10 records.

## Outstanding exit gates

Authenticated audit 2026-10-02: 2,048 uniformly spaced rows included 358 CO2 and
439 H2O exact-single records. `energy_old - energy_mof - energy_ads_corrected`
gave -22.990396/-14.236396 eV with spreads below 3.3e-14 eV. Using `energy`
instead gave spreads 1.07278/1.48885 eV. These are actual dataset-field identities,
not fitted validation parameters. The first minimum-original-bare matching
attempt failed on ANUGEW_deen_33 CO2. Original and corrected bare minima are
being compared; no new paired MLIP score has been accepted.

Both original/corrected minima across all stored bare frames failed to match
145 of 285 single-gas references. Restricting bare candidates to largest fid
per trajectory reduced this to 94 mismatches. The frozen pool is unchanged;
no partial-pool score is substituted. Direct energy lookup among all stored
bare frames is the next diagnostic, to distinguish reference selection from
absent reference geometry. These are actual failures, not completed benchmarks.
The direct lookup executed on all 189,504 bare rows: 67 distinct unresolved
energies, 5 with a matching original/corrected stored energy at 1e-5 eV and
62 without a match. This does not prove geometry is absent: a reference may use
a different energy convention, calculation version or cell normalization.
It does establish that the current exact energy-identity guard cannot pass.
Do not invent a mapping or change the target pool to manufacture completion.
Downloaded audit JSON, the source digest/environment record and the exported
candidate UiO-66 parent are in
`artifacts/kaggle/odac25_reference_audit_2026-10-02/`.

The implementation reverses recorded system/bare k-point offsets to evaluate
the frozen pre-k-point adsorption fields. This reference-assisted protocol uses
DFT metadata at evaluation time and cannot be called prospective screening.

1. Resolve reference identities against actual data and primary sources.
2. Materialize training data under the corrected/final-frame contract, or
   approve and clearly name a different training experiment.
3. Execute/download valid eSEN and UMA full-pool predictions and environment
   records. Keep failures in denominators and pin checkpoint identities.
4. Recompute shared-pool metrics; save ranking tables and figures.
5. Review a fixed-template structural library and real h/J evidence. Whole-MOF
   energies do not identify per-block interactions.

See [REMAINING_WORK.md](REMAINING_WORK.md) for the full four-phase checklist.

## Bounded training lead checked 2026-10-03

The [AtomMOF research mirror](https://huggingface.co/datasets/nayoung10/AtomMOF-data)
offers smaller processed ODAC25 files. At code commit
`7589209ff53514a136f20043e77408108d6f8530`, its
[block extraction](https://github.com/nayoung10/AtomMOF/blob/7589209ff53514a136f20043e77408108d6f8530/src/preprocess/odac25/extract_blocks.py)
preserves `atoms.info`; feature assembly carries that into the saved structure.
Its [split script](https://github.com/nayoung10/AtomMOF/blob/7589209ff53514a136f20043e77408108d6f8530/src/preprocess/odac25/split_dataset_random.py)
renames original validation to test and partitions original training by records.
Thus mirror split names alone do not prove our official MOF-level split boundary.

Downloaded only 57,701-byte test metadata at dataset revision
`81a85299823a7e75e0ed7fe39640c99297906080`, SHA256
`d5f40dd368522f46728b85d705bf49c364180a3fc2bc06e9946a89c1ab41834c`.
Restricted inspection found 3,582 records containing atom counts only, no
executable/class pickle opcodes. This metadata does not supply targets or
resolve the bare-reference mapping. The actual LMDB/retained info fields,
source-index identity, corrected labels, final fid and official split overlap
still need inspection before this mirror can become a training source.
No mirror-target extraction or learned-model benchmark is claimed.
