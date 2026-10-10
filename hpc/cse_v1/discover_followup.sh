#!/usr/bin/env bash
# Login-node metadata only. No compute allocation or scientific execution.
set -u
exec 2>&1
probe() { printf '\n--- %s ---\n' "$*"; timeout 20s "$@"; printf 'exit=%s\n' "$?"; }
probe hostname -f
probe scontrol --version
probe scontrol show partition cpupart
probe sinfo -a -h -o '%P|%a|%l|%D|%c|%m|%G'
probe scontrol show node cnode1
probe scontrol show node cnode2
probe scontrol show config
probe sacctmgr -nP show assoc where "user=$(id -un)"
probe sacctmgr -nP show user "$(id -un)" withassoc
printf '\n--- bounded module/application inventory ---\n'
if type module >/dev/null 2>&1; then module -t avail 2>&1 | head -100; fi
for location in /opt /usr/local/bin /usr/local/lib /apps /software /data; do
  if [ -d "$location" ]; then probe ls -ld "$location"; probe ls "$location"; fi
done
probe dpkg-query -W 'quantum-espresso*' 'openmpi*' 'gfortran*' 'libfftw3*' 'libblas*' 'liblapack*'
printf '\n--- QE executable names under bounded software roots ---\n'
for location in /opt /usr/local /apps /software; do
  if [ -d "$location" ]; then
    timeout 20s find "$location" -maxdepth 4 \( -name pw.x -o -iname '*espresso*' -o -iname '*qe-7*' \) -print 2>/dev/null | head -50
  fi
done
printf '\n--- quota/policy tooling ---\n'
command -v quota lfs xfs_quota getquota myquota sbalance || true
printf '\nNo jobs, builds, inference or site-policy assumptions.\n'
