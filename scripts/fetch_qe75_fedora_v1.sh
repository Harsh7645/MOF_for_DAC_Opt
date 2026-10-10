#!/usr/bin/env bash
# Official source and release-pinned dependency retrieval; no build or calculation.
set -euo pipefail
cd "$(dirname "$0")/.."
qe_base="$PWD/local/qe75-fedora-v1"
qe_source="$qe_base/q-e-qe-7.5"
mkdir -p "$qe_base"
if [[ ! -f "$qe_base/q-e-qe-7.5.tar.gz" ]]; then
    curl -fL --connect-timeout 20 --max-time 180 \
        https://gitlab.com/QEF/q-e/-/archive/qe-7.5/q-e-qe-7.5.tar.gz \
        -o "$qe_base/q-e-qe-7.5.tar.gz"
fi
printf '%s  %s\n' 7e1f7a9a21b63192f5135218bee20a5321b66582e4756536681b76e9c59b3cc8 "$qe_base/q-e-qe-7.5.tar.gz" | sha256sum -c -
if [[ ! -d "$qe_source" ]]; then
    tar -xzf "$qe_base/q-e-qe-7.5.tar.gz" -C "$qe_base"
fi
while read -r qe_commit qe_dependency; do
    case "$qe_dependency" in
        fox|mbd|devxlib|wannier90)
            qe_dest="$qe_source/external/$qe_dependency"
            if [[ ! -d "$qe_dest/.git" ]]; then
                qe_url="$(git config --file "$qe_source/.gitmodules" --get "submodule.external/$qe_dependency.url")"
                git init "$qe_dest"
                git -C "$qe_dest" remote add origin "$qe_url"
                if [[ "$qe_dependency" = wannier90 ]]; then
                    git -C "$qe_dest" config remote.origin.promisor true
                    git -C "$qe_dest" config remote.origin.partialclonefilter blob:none
                    timeout 180 git -C "$qe_dest" fetch --depth 1 --filter=blob:none origin "$qe_commit"
                    git -C "$qe_dest" sparse-checkout set src
                else
                    timeout 180 git -C "$qe_dest" fetch --depth 1 origin "$qe_commit"
                fi
                timeout 180 git -C "$qe_dest" checkout --detach "$qe_commit"
            fi
            test "$(git -C "$qe_dest" rev-parse HEAD)" = "$qe_commit"
            git -C "$qe_dest" diff --exit-code HEAD --
            ;;
    esac
done < "$qe_source/external/submodule_commit_hash_records"
