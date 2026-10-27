# Draft only — ODAC25 parent-state and compact-export question

Not sent to the authors or professor. Proposed addressee: professor first; dataset
authors only after the user authorizes contact.

We froze single-CO2/H2O targets from the 20250918 filtered validation release using
max stored fid per trajectory and minimum final `energy_ads_corrected` per
`mof_name`/gas. A bounded check against the pinned AtomMOF mirror matched 275 of
276 selected records exactly in ID, trajectory, fid and corrected energy. However,
27 of the 138 selected gas pairs have different framework compositions.

For `CAXVOO_0.08_0_eeen_19`:

- CO2 source row **101**, fid **101**, `..._w_CO2_1`: tag-derived mirror framework
  C112H95N8O72Fe24; `energy_mof = -2136.45421843 eV`.
- H2O source row **2680**, fid **370**, `..._w_CO2_COOH_w_H2O_random_1`: framework
  C113H95N8O74Fe24; `energy_mof = -2159.1267650500004 eV`.
- Both records declare `nads=1`, with one CO2 or one H2O guest respectively. The
  C1O2 difference is retained within the mirror's framework blocks. Original raw
  per-atom tags have not been re-exported; the mirror's partition follows the
  source preprocessing's tag-zero convention. We have not changed the frozen data.

**Main question:** Does the H2O trajectory represent adsorption on a CO2-reacted
framework state, and which official identifier should distinguish that state from
the parent used for the CO2 target? Should paired competition be restricted to an
identical tagged parent state, rather than `mof_name` alone? Please also specify
the canonical base-framework/family mapping for keeping related functionalized
or defective records together across training and evaluation.

**Reference/extraction follow-up:** Is
`energy_ads_corrected = energy_old - energy_mof - sum(n_g Egas,g)` the intended
20250918 field convention, with `energy` separately k-point corrected? Which
exact re-relaxed bare record (and any supercell normalization) supplies
`energy_mof` for these two examples? Our full bare-shard energy lookup still has
62 unmatched reference energies; matching scalar field identities has not resolved
their structures.

Could you provide the current filtered-training archive URL, checksum and member
catalog, or a small source-side export of complete final-frame records for 8–16
training parents with official splits, parent-state/family IDs and tagged parent
structures? We need `name`, `sid`, `fid`, source index/shard hash, gas counts,
`supercell`, corrected/old energy fields and expected trajectory counts. The
mirror's record-level train/val split and omitted decompositions cannot establish
completeness. We also need original validation row **512478** (`EPONEE`, CO2),
which is absent from the mirror; we will not substitute another frame.

This request is for metadata/existing structure export only, not new DFT/UMA
calculations or authorization to redefine the benchmark. Until clarified, the
frozen 138-MOF table remains historical and real-data fitting/ranking stays on hold.
