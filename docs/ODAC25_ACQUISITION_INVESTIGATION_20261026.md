# ODAC25 acquisition investigation — 26 October 2026

**Decision: hold real fitting.** Compatible fields were recovered from a small
training sample, but no complete paired training pool or leakage-safe family map
was established. More importantly, **27 frozen evaluation pairs have different
selected framework compositions**. Preserve their labels; review the intended
task before treating their difference as competition on one parent framework.

No constant/ridge implementation was changed in this investigation. Earlier local
edits remain intact. No QE, UMA, CGCNN, full database download, message to authors
or material-ranking calculation ran. Phase 3 remains incomplete.

## Authoritative release and procedure

The authoritative data publisher is [FAIR's ODAC25 release](https://huggingface.co/facebook/ODAC25),
linked by the [official FAIR documentation](https://facebookresearch.github.io/fairchem/odac25/)
and [ODAC25 paper, version 2](https://arxiv.org/html/2508.03162v2). The public
repository API currently reports the same revision as our archived inventory:
`43f37d9592a35377380fd20832ddc2164ddb2492`. This pins the repository metadata,
not a checksum of externally hosted tar archives.

Our frozen validation shard came from the **20250918 filtered** archive. An
[author response on release correction](https://github.com/facebookresearch/fairchem/issues/1463#issuecomment-3315616564)
reports corrected dataset links in September 2025; the locally saved API response
retains the exact comment URL/date. Do not use an older
archive merely because its filename resembles the current one.

The current `DATASET.md` is gated: unauthenticated access returns 401, and no local
HF credential was available. Its archived inventory size is 4,080 bytes. We did
not bypass access controls. The official training URL/member inventory, compressed
size, extracted sizes and archive checksum still need confirmation from that card
or an authenticated source-side inventory. The same-directory training URL probe
returned 403; this does **not** establish that it is a valid current object.

The official format is ASE-compatible `*.aselmdb`, read with
`AseDBDataset({'src': ...}).get_atoms(index)`. Preserve `atoms.info`, raw atomic
numbers, positions/cell/PBC and **per-atom tags** in an export. An
[author explanation of tags](https://github.com/facebookresearch/fairchem/issues/1463)
defines tag 0 as framework and tags 1–4 as CO2/H2O/N2/O2. A separate
[author clarification](https://github.com/facebookresearch/fairchem/issues/1562#issuecomment-3533484896)
explains that apparent extra water can be intentional defect caps or functional
groups. Neither visual resemblance nor composition subtraction authorizes removal.

For compatible labels, stream metadata, group by official split and trajectory
`name`, retain greatest integer `fid`, then apply the existing exact-single-gas
filter and minimum final `energy_ads_corrected` per material/state/gas. Retain all
ties, candidate counts and source indices for audit. The project's existing v1
tie-break is deterministic trajectory/fid order. A largest stored `fid` is not
proof of force convergence. This material-level reduction is **our registered
protocol**, not an official precomputed 138-MOF benchmark supplied by the authors.

Do not assume a shard boundary is a trajectory or parent boundary. Before taking
a minimum, establish that all relevant final trajectories for an admitted parent
are present across the chosen shard set. Export rejected/missing cases as well.

## Target, references and identity

Stored energies are eV, not per-atom normalized. For n molecules, the intended
adsorption definition is `Ecomplex − Eframework − sum(n_g Egas,g)`.
The frozen field identity is explicitly:

```text
energy_ads_corrected = energy_old - energy_mof - sum(n_g Egas,g)
energy_ads           = energy_old - energy_mof_old - sum(n_g Egas,g)
```

The original/pre-k-point `energy_old` must not be replaced with `energy`. The
archived audit and newly inspected single-gas records agree on gas offsets
−22.990396 eV for CO2 and −14.236396 eV for H2O. The paper describes both
trajectory-level k-point corrections and re-relaxed empty-framework references;
the exact released field identities above are supported by observed records.

The **62 unmatched stored reference energies remain unresolved**. Reading the
same corrected field in training/evaluation avoids reconstructing that reference
for supervised label regression; it does not solve the missing geometry mapping
or validate MLIP adsorption energies. Never infer a universal correction from
validation medians or substitute an arbitrary bare minimum.

Preserve `mof_name`, `mof_type`, `name`, `sid`, `fid`, `supercell`, `nco2`, `nh2o`,
`nn2`, `no2`, `nads`, all five energy/reference fields above, official split,
release/shard digest and row index. **`mof_name` alone is insufficient to establish
the adsorption parent state** in the affected functionalized records. A practical
audit key additionally retains tag-zero composition, supercell and trajectory
state; it is not yet an author-approved canonical family ID. `sid` and mirror row
ordinal likewise cannot silently replace an official parent identity.

## Recovered evidence and the 31/107 investigation

The research mirror is [AtomMOF-data at pinned revision](https://huggingface.co/datasets/nayoung10/AtomMOF-data/tree/81a85299823a7e75e0ed7fe39640c99297906080)
`81a85299823a7e75e0ed7fe39640c99297906080`. Source procedures were pinned to
[AtomMOF commit](https://github.com/nayoung10/AtomMOF/tree/7589209ff53514a136f20043e77408108d6f8530)
`7589209ff53514a136f20043e77408108d6f8530`:

- `extract_final_frames.py` explicitly chooses max fid by trajectory name.
- `extract_mofid.py` selects tag-zero framework atoms and can Niggli-reduce cells.
- `extract_blocks.py` separates nonzero-tag guest atoms; retains framework
  NODE/LINKER/**SOLVENT** blocks. SOLVENT here must not be deleted.
- `extract_feats.py` retains `info` and original source-index keys, reconstructs
  blocks/coordinates and can omit failed decompositions. Mirror geometry is not
  automatically an exact original ASE structure.
- `split_dataset_random.py` renames original validation to test and partitions
  original training by **records**, not parents. Both mirror train and val are
  needed to recover all its retained original-training trajectories.

The 41,052-byte `test_system_indices.pkl` passed its published LFS SHA256 and was
decoded with only `collections.defaultdict` and `builtins.list` permitted. It
contains 683 material/loading groups, 151 names and 3,582 records, covering all
138 evaluation IDs. This is identity evidence from a derivative source, not proof
that every selected frame or original parent structure survived preprocessing.

HTTP range samples first checked six selected validation records and three
training records. Then a **32-MiB maximum** audit queried only the 276 exact frozen
evaluation source keys. The audit consumed 15,753,216 counted range bytes,
including repeated cached page reads; the saved unique range files across probes
and samples total 11,384,796 bytes (~10.86 MiB). No complete LMDB was downloaded.

**275/276 records** match frozen `mof_name`, trajectory, fid, source key, gas count
and corrected energy, and satisfy the reference-field identity. Framework and
guest block counts conserve the record's total atomic numbers. All recovered
framework fractions match one of the archived bare-cache candidates.

|Prior category|New observation|Count|
|---|---|---:|
|107 cache-consistent IDs|Both selected gases have the same framework composition, matching cache|106|
|107 cache-consistent IDs|Frozen EPONEE CO2 source key 512478 absent from mirror|1|
|31 cache-ambiguous IDs|Selected CO2/H2O framework compositions agree|4|
|31 cache-ambiguous IDs|Selected CO2/H2O framework compositions differ|27|

The four matching selected pairs are `ANUGEW_deen_33`, `CAXVOO_nmen_16`,
`PIBPIA_ipen_25`, `RAVXAP_ipen_83`. Their other cached compositions are retained,
not deleted or relabelled. Composition agreement does not prove identical
connectivity, proton state, conformation or family independence.

All 31 original ambiguities consist of two cached compositions differing by
**C1O2**. The larger candidate names include `CO2_COOH` or `CO2_NCOO`; this supports
a state-dependent interpretation, not an authorized repair. For example:

|Frozen CAXVOO_0.08_0_eeen_19 target|Source index / fid|Selected framework composition|`energy_mof`, eV|
|---|---|---|---:|
|CO2, `..._w_CO2_1`|101 / 101|C112 H95 N8 O72 Fe24|−2136.45421843|
|H2O, `..._w_CO2_COOH_w_H2O_random_1`|2680 / 370|C113 H95 N8 O74 Fe24|−2159.1267650500004|

The guest blocks are exactly CO2 and H2O respectively. Thus the additional C1O2
is in the mirror's framework partition, not an extra guest silently inferred from
counts. For these states, subtracting the two labels is not yet justified as
competition on one unchanged framework. **Do not drop the 27 cases, choose the
smaller parent, change the frozen minimum rule or publish a 110-MOF replacement.**

The EPONEE mirror includes other CO2 records, but none was substituted for the
missing frozen winner. The complete 138 target file still has SHA256
`58c5dd5bec75366e3cd95dbd7ba9d714d1ff0163a560158cf154640aed5095bf`.

Three training samples recover `energy_ads_corrected`, reference fields and fid:
source keys `10000133`, `1000021`, `10000233`. They cover `WIYFAM_0.08_0` (two pure
CO2 final records) and `ASOVEL` (CO2+2H2O, excluded from the single-gas task). Neither
exact ID occurs in the frozen pool. **No paired training parent was established**;
family leakage and trajectory completeness remain unchecked. These examples prove
field availability, not usable training coverage or an approved training release.

## Smallest acquisition options — no large download performed

|Exact source/file|Download bytes|Extracted/storage requirement|Coverage and limitation|
|---|---:|---|---|
|Official pinned `DATASET.md`|4,080 in archived inventory|Small text|Authenticated release URLs and member catalog needed; current read blocked|
|Official `20250918/odac25_filtered_val.tar.gz`|11,117,673,531 via HEAD|Selected system shard is 8,418,258,944; bare shard/full extraction size not newly established|Evaluation only; unnecessary to redownload if source-side export is available|
|Mirror `odac25/test_system_indices.pkl`|41,052|Decoded JSON ~0.1 MB|Already recovered; IDs/ordinals only, not labels|
|Mirror `odac25/odac25_test.lmdb`|141,197,312|Same bytes, uncompressed LMDB|3,582 records; original validation; one frozen key missing|
|Mirror `odac25/odac25_train.lmdb`|6,547,623,936|Same bytes, uncompressed LMDB|153,249 retained records, exact paired-parent count unknown|
|Mirror `odac25/odac25_val.lmdb`|136,159,232|Same bytes, uncompressed LMDB|3,130 retained original-training records; must not be mistaken for official evaluation|

Mirror sizes are pinned publication metadata; entry counts also came from bounded
LMDB headers. The two training-side files together are **6,683,783,168 bytes
(~6.22 GiB), 156,379 records**, not 156,379 independent parents or pairs. Reserve
at least 8 GiB for direct files plus measured export growth, or 14 GiB if a cache
duplicates downloads. A full mirror scan still cannot prove that failed original
trajectories did not contain a lower final target. No original training archive
size or exact internal shard list has been established; do not invent either.

**Recommended smallest next action:** obtain a compact export from an existing
authenticated official installation, rather than downloading the full archive:

1. Exact original EPONEE CO2 row **512478** from
   `val/mof_plus_adsorbate/part_00000.aselmdb` (SHA256
   `2927f1ebb3af5fd4ea6e5d1072f9bdef549afa9e53ce3f0605955885da4b6c8c`), including
   metadata, atom tags/numbers and cell. Do not replace the frozen label.
2. Original tagged records for the CAXVOO pair above, plus the author/professor's
   parent-state interpretation. This is the smallest scientific clarification
   needed before the paired task can be admitted.
3. A source-side metadata inventory of original **training** trajectories, parent
   IDs/families and shard locations; no positions/forces needed initially. Choose
   8–16 complete training parents by deterministic ID order after excluding the
   frozen parents and related families, **without looking at their energies**.
4. For those parents export every final trajectory's corrected fields, reference
   metadata and tagged parent compositions; include verified raw parent structures
   and counts of expected/exported trajectories. Bound the first transfer to
   **32 MiB** and stop/report if exceeded. This is a proposed ceiling, not a
   measured export size or promised number of paired targets. At least two
   independent paired training groups are required even for a fit smoke check;
   meaningful baseline evaluation needs a justified larger training pool.

Do not run the mirror's full decomposition or random splitting scripts on this
PC. The original source-side reducer can stream metadata or maintain final-frame
indices in SQLite, keeping one frame index per trajectory and emitting the compact
export. No GPU, MLIP or DFT is needed. Confirm archive membership/complete parent
coverage before using the existing reducer. A revised scientific target, if
approved, needs a separately versioned contract while retaining this frozen table.

## Verification and reproducible evidence

Read-only investigation scripts: `scripts/inspect_odac25_mirror_sample.py` and
`scripts/audit_odac25_acquisition.py`. The parser is restricted to the observed
little-endian LMDB layout, checked against [LMDB 0.9.31 source](https://github.com/LMDB/lmdb/blob/LMDB_0.9.31/libraries/liblmdb/mdb.c).
It requires exact HTTP 206 ranges, bounds file/range/record sizes, and represents
pickle globals as inert placeholders; no dataset class constructors execute.
Five new offline tests passed, including a malicious callable fixture, ignored
range rejection, exact-key lookup and integer-buffer validation.

The initial parser omitted documented SOLVENT blocks; its interrupted output,
failures and source are preserved in `selected-audit-v1/` and `audit_parser_v1.py`.
Corrected v2 includes them as framework atoms. A full **offline replay matched all
275 records, the one missing-key failure, pair classifications and every range
hash**. No numerical/model audit was rerun. All four earlier surrogate source
hashes remain unchanged this turn.

```powershell
# Offline only; use a new output directory to preserve prior evidence.
python -m scripts.audit_odac25_acquisition --cache local/odac25-acquisition-20261026/ranges --output local/odac25-acquisition-replay
python -m pytest tests/test_odac25_acquisition.py -q -p no:cacheprovider --basetemp=local/odac-acquisition-tests-new
```

Raw source receipts, bounded ranges and reports are under
`local/odac25-acquisition-20261026/`. Tracked summaries:
[pair identity table](odac25_acquisition_pair_audit_20261026.csv),
[machine-readable assessment](odac25_acquisition_assessment_20261026.json).
Full-database LFS hashes were **not** verified from partial ranges: evidence is
bound to pinned mirror revision/URL, local range hashes and exact frozen matches.
This must not be described as raw authoritative structure verification.

The focused [review question](ODAC25_PARENT_STATE_REVIEW_QUESTION.md) is drafted
only, **not sent**. The existing reference mismatch and higher-cutoff DFT/RAM
workstreams remain separately outstanding.
