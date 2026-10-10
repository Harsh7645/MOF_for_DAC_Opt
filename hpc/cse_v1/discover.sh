#!/usr/bin/env bash
# Read-only login-node discovery. No pw.x, srun, build, submission or directory creation.
set -u
exec 2>&1  # Authenticated command errors only; SSH password prompts stay local.
probe() { printf '\n--- %s ---\n' "$*"; timeout 20s "$@"; printf 'exit=%s\n' "$?"; }
probe date -u
probe hostname -f
probe id
printf 'home=%s\n' "$HOME"
probe python3 --version
probe sinfo -h -o '%P|%a|%l|%D|%c|%m|%G'
probe scontrol show partition
printf '\n--- CPU partition nodes (scheduler metadata only) ---\n'
nodes=$(timeout 20s sinfo -h -p cpupart -o '%N' | sort -u)
if [ -n "$nodes" ]; then
  while IFS= read -r node_list; do probe scontrol show node "$node_list"; done <<< "$nodes"
fi
printf '\n--- scheduler limits and accounting ---\n'
timeout 20s scontrol show config | grep -E 'ProctrackType|TaskPlugin|SelectType|JobAcctGather|AccountingStorage|PriorityWeightTRES|EnforcePartLimits|SlurmctldParameters'
probe sacctmgr -nP show assoc where "user=$(id -un)" format=Cluster,Account,User,Partition,QOS,DefaultQOS,GrpTRES,GrpTRESMins,MaxTRES,MaxWall
probe sacctmgr -nP show user "$(id -un)" withassoc
probe sacctmgr -nP show qos format=Name,MaxWall,MaxTRESPerJob,MaxTRESPU,GrpTRES,GrpTRESMins
probe sshare -l -u "$(id -un)"
probe quota -s
for utility in myquota sbalance; do
  if command -v "$utility" >/dev/null; then probe "$utility"; fi
done
printf '\n--- storage candidates: existence does not establish permission or retention ---\n'
for location in "$HOME" "/scratch/$(id -un)" /scratch /work /data; do
  if [ -d "$location" ]; then
    probe ls -ld "$location"
    probe df -h "$location"
    probe findmnt -T "$location" -o TARGET,SOURCE,FSTYPE,OPTIONS
  fi
done
if [ -r /etc/motd ]; then probe head -100 /etc/motd; fi
printf '\n--- available QE/compiler/MPI/Python modules ---\n'
if type module >/dev/null 2>&1; then
  module -t avail 2>&1 | grep -iE 'espresso|quantum|(^|/)qe|intel|openmpi|mpich|python' | head -100
  module list 2>&1
fi
if command -v spack >/dev/null; then probe spack find -lv quantum-espresso; fi
printf '\n--- executable paths; no scientific execution ---\n'
command -v pw.x mpirun mpiexec srun sbatch python3 || true
if command -v mpirun >/dev/null; then probe mpirun --version; fi
if command -v pw.x >/dev/null; then
  executable=$(readlink -f "$(command -v pw.x)")
  probe ls -l "$executable"
  probe sha256sum "$executable"
  probe file "$executable"
  probe ldd "$executable"
fi
printf '\nUnavailable/restricted queries remain unknown. No compute entitlement inferred.\n'
