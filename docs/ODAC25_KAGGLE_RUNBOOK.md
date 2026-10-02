# Kaggle ODAC25/UMA runbook

Use a T4x2 notebook with Internet enabled. Kaggle's current PyTorch 2.13 CUDA 13
build does not include P100 `sm_60` kernels. The smoke run uses one T4.

1. Add a private Kaggle secret named `HF_TOKEN` and grant the notebook access.
2. Upload `artifacts/kaggle/MOF_DAC_Kaggle_bundle.zip` as a **private Kaggle
   Dataset**, not as a Kaggle Model. Attach that Dataset through the notebook's
   Input pane.
3. Import `kaggle/ODAC25_UMA_Smoke.ipynb`, or copy the cells from
   `kaggle/odac25_uma_pipeline.py` into a Python notebook.
4. Run inventory cells. The gated repository currently contains eight metadata
   files and official archive links, not `.aselmdb` shards.
5. Stream-extract `val/gcmc/part_00000.aselmdb` (847,228,928 bytes) from the
   official filtered-validation archive without retaining the 12 GB archive.
6. Run schema inspection and the 16-structure UMA smoke evaluation.
7. Download four non-secret artifacts: `inventory.json`, `DATASET.md`,
   `schema.json`, and `uma_smoke.json`.

Do not paste the token into notebook cells, output, Git, chat or artifacts. The
GCMC schema samples have null `energy_ads_corrected`, so this shard validates UMA
execution but cannot validate paired adsorption targets. A `mof_plus_adsorbate`
shard is required next.

## Target-bearing profile

Upload the refreshed bundle and import `kaggle/ODAC25_Target_Profile.ipynb` as a
second notebook. A CPU session is sufficient. It streams through the validation
archive to the first `val/mof_plus_adsorbate/*.aselmdb` member, retains only that
database, inspects 32 records and profiles every record in the shard. Download
`ODAC25_target_analysis_artifacts.zip` when it finishes.

The extractor caps compressed bytes read at 20 GiB and the retained member at
10 GiB, validates the archive path and records its SHA-256 digest. The bound
covers the observed 8,418,258,944-byte validation target shard. The authenticated
profile found 560,208 rows, 151 MOFs, 3,590 trajectories and 138 MOFs containing
both pure CO2 and pure H2O records. It also found 285 repeated MOF-gas groups.
The following materialization pass applies the frozen exact-single-molecule,
final-frame and strongest-sampled-configuration rule in
`ODAC25_TARGET_CONTRACT.md` and writes `paired_targets.json`.

## Full Phase 3 material benchmark

Use `kaggle/ODAC25_Phase3_Material_Benchmark.ipynb` with the refreshed project
bundle, Internet, the `HF_TOKEN` secret and one T4 GPU. Run the cells in order.
The notebook:

1. downloads the pinned `co/co_9.parquet` ColabFit training shard at revision
   `064de0077b3de4745f58c58e7a34da933c8b727e`;
2. stream-extracts the target-bearing and bare-MOF validation databases;
3. rebuilds the frozen 138-MOF paired validation pool and checks its size;
4. fits constant and composition-ridge baselines using training records only;
5. evaluates the ODAC25-filtered eSEN checkpoint and `uma-s-1p2p1` with
   `task_name="odac"` on the same structures; and
6. writes `ODAC25_Phase3_material_artifacts.zip` with component predictions,
   metrics, failure rows, timings, versions and input/checkpoint hashes.

The bounded training mirror does not expose `fid` or corrected adsorption
energy. The pipeline therefore records its use of the last stored trajectory
row and the original `energy_ads` field. Validation remains frozen on
`energy_ads_corrected`; this target-field mismatch must stay visible in any
comparison or manuscript text. The model baselines are intended to reconstruct ODAC25 Eq. 2
from predicted adsorbed and composition-matched bare total energies plus the
recorded fixed gas reference. The CO2 and H2O systems may use different
supercells; each is matched to its own bare structure.

Current execution gate: [PHASE3_REFERENCE_AUDIT.md](PHASE3_REFERENCE_AUDIT.md).
Do not score MLIPs until the gas-reference identity audit passes. The pipeline
rejects inconsistent inferred references and stale cached dataset fingerprints.
Kaggle sessions are ephemeral: download progress/results before ending a session.
