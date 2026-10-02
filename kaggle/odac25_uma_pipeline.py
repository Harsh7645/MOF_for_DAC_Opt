# %% [markdown]
# ODAC25 + UMA authenticated discovery and smoke evaluation.
# Add HF_TOKEN through Kaggle Add-ons -> Secrets. Never paste it into this file.

# %%
import os
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

subprocess.run([
    sys.executable, "-m", "pip", "install", "-q",
    "huggingface-hub>=0.28", "ase>=3.26", "fairchem-core>=2,<3",
    "fairchem-data-odac>=0.1,<1",
], check=True)

# %%
from kaggle_secrets import UserSecretsClient

os.environ["HF_TOKEN"] = UserSecretsClient().get_secret("HF_TOKEN")
assert os.environ["HF_TOKEN"], "Create a Kaggle secret named HF_TOKEN"

# Upload the bundle as a private Kaggle Dataset. Kaggle may expose its files at
# the Dataset root or preserve an enclosing directory, so locate the script.
candidates = [Path("/kaggle/working/MOF_for_DAC_Opt")]
candidates += [path.parents[1] for path in Path("/kaggle/input").rglob("scripts/odac25_hf.py")]
REPO = next((path for path in candidates if (path / "scripts/odac25_hf.py").is_file()), None)
if REPO is None:
    raise FileNotFoundError("Upload/clone MOF_for_DAC_Opt, then set REPO to its directory")
os.chdir(REPO)

# %% [markdown]
# Build a revision-pinned inventory and download the gated DATASET.md. No dataset
# shard is downloaded in this cell.

# %%
subprocess.run([
    sys.executable, "scripts/odac25_hf.py", "inventory",
    "--output", "/kaggle/working/odac25/inventory.json",
], check=True)

# %%
import json

inventory = json.loads(Path("/kaggle/working/odac25/inventory.json").read_text())
print("revision", inventory["revision"])
print("repository files", len(inventory["files"]))
print(Path("/kaggle/working/odac25/DATASET.md").read_text()[:12000])

# %% [markdown]
# The gated repository contains metadata and archive links, not LMDB shards.
# Stream one 0.79 GiB GCMC member from the filtered validation archive. This is
# a schema/UMA smoke source, not a paired adsorption-target source.

# %%
VAL_URL = "https://dl.fbaipublicfiles.com/dac/odac25/20250918/odac25_filtered_val.tar.gz"
WANTED = {
    "val/gcmc/part_00000.aselmdb-lock",
    "val/gcmc/part_00000.aselmdb",
}
data_root = Path("/kaggle/working/odac25/data")
extracted = []
with urllib.request.urlopen(VAL_URL, timeout=300) as response:
    with tarfile.open(fileobj=response, mode="r|gz") as archive:
        for member in archive:
            if member.name not in WANTED:
                continue
            if member.size > 2 * 1024**3:
                raise RuntimeError(f"Unexpected member size: {member.size}")
            destination = data_root / member.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(member)
            if source is None:
                raise RuntimeError(f"Cannot extract {member.name}")
            with source, destination.open("wb") as sink:
                shutil.copyfileobj(source, sink, length=8 * 1024 * 1024)
            extracted.append(member.name)
            if set(extracted) == WANTED:
                break
assert set(extracted) == WANTED, extracted
DATASET_SOURCE = data_root / "val/gcmc"

# %% [markdown]
# Inspect actual Atoms.info and calculator schemas before writing target joins.

# %%
subprocess.run([
    sys.executable, "scripts/odac25_hf.py", "inspect",
    str(DATASET_SOURCE),
    "--output", "/kaggle/working/odac25/schema.json", "--samples", "16",
], check=True)
print(Path("/kaggle/working/odac25/schema.json").read_text())

# %% [markdown]
# UMA 1.2.1 smoke evaluation using task_name="odac". This compares total-energy
# predictions only. Adsorption energies require verified bare-MOF and molecule
# references and are deliberately computed in the next stage.

# %%
import torch

assert torch.cuda.is_available(), "Enable a Kaggle GPU accelerator"
print(torch.cuda.get_device_name(0))
subprocess.run([
    sys.executable, "scripts/odac25_hf.py", "uma-smoke",
    str(DATASET_SOURCE),
    "--output", "/kaggle/working/odac25/uma_smoke.json",
    "--samples", "16", "--device", "cuda",
], check=True)
print(Path("/kaggle/working/odac25/uma_smoke.json").read_text())

# %% [markdown]
# Download inventory.json, DATASET.md, schema.json and uma_smoke.json from the
# Kaggle output. These contain no token. They are the evidence needed to freeze
# exact ODAC25 field mappings and start paired evaluation/fine-tuning.
