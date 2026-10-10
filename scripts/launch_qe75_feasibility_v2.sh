#!/usr/bin/env bash
set -euo pipefail
set -C  # Refuse to overwrite retained service-console.log.
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
if [[ -e local/qe75-fedora-feasibility-v2/run01/execution-started.json ]]; then
  echo 'The one-test authorization is consumed; refusing another launch.' >&2
  exit 1
fi
# Python verifies actual limits and an exclusive one-run marker before invoking MPI.
# No retries or automatic restarts. The authorization is consumed before launch.
systemd-run --user --wait --pipe --unit=qe75-feasibility-v2 \
  --working-directory="$PWD" \
  -p MemoryHigh=10G -p MemoryMax=11G -p MemorySwapMax=0 \
  -p RuntimeMaxSec=585s -p TimeoutStopSec=15s -p KillMode=control-group \
  -p SendSIGKILL=yes -p OOMPolicy=kill -p TasksMax=96 \
  -p CPUAffinity=0-7 -p MemoryAccounting=yes -p IOAccounting=yes \
  /usr/bin/python3 "$PWD/scripts/qe75_feasibility_v2.py" --execute \
  > evidence/qe75-fedora-feasibility-v2/service-console.log 2>&1
