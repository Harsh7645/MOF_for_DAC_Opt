#!/usr/bin/env bash
# Lightweight read-only login-node discovery. No pw.x, build, allocation or submission.
set -u
probe() { printf '\n--- %s ---\n' "$*"; timeout 25s "$@"; printf 'exit=%s\n' "$?"; }
probe date -u
probe hostname -f
probe id
printf 'home=%s\n' "$HOME"
probe python3 --version
probe sinfo -h -o '%P|%a|%l|%D|%c|%m'
probe scontrol show partition
printf '\n--- scheduler enforcement/accounting configuration (read-only) ---\n'
timeout 25s scontrol show config | grep -E 'ProctrackType|TaskPlugin|SelectTypeParameters|JobAcctGatherType|JobAcctGatherFrequency|AccountingStorageTRES|PriorityWeightTRES'
probe sacctmgr -nP show assoc where "user=$(id -un)" format=Cluster,Account,User,Partition,QOS,DefaultQOS,GrpTRES,GrpTRESMins,MaxTRES,MaxWall
probe sacctmgr -nP show user "$(id -un)" withassoc
probe sbalance
probe myquota
probe df -h "$HOME" "/scratch/$(id -un)"
probe ls -ld "$HOME" "/scratch/$(id -un)" /home/iitkgp/slurm-scripts
printf '\n--- available QE/compiler/MPI module names ---\n'
module -t avail 2>&1 | grep -iE 'espresso|quantum|(^|/)qe|intel|openmpi|mpich|python' | head -100
printf '\n--- loaded modules ---\n'
module list 2>&1
printf '\n--- installed Spack QE only ---\n'
if command -v spack >/dev/null; then probe spack find -lv quantum-espresso; fi
printf '\n--- relevant executable paths (no inference) ---\n'
command -v pw.x mpirun mpiexec srun sbatch python3 || true
printf '\n--- site example filenames, not execution ---\n'
find /home/iitkgp/slurm-scripts -maxdepth 2 -type f 2>/dev/null | head -50
printf '\nDiscovery finished. Restricted/failed commands are unknown facts, not zero limits.\n'
