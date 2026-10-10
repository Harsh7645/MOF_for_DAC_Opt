#!/usr/bin/env bash
# Software build only. No QE scientific input is run.
set -euo pipefail
cd "$(dirname "$0")/.."
qe_root="$PWD/local/qe75-fedora-v1"
mkdir -p "$qe_root" evidence/qe75-fedora-v1
qe_log_dir="evidence/qe75-fedora-v1/build-$(date -u +%Y%m%dT%H%M%SZ)"
mkdir "$qe_log_dir"
for tool in cmake make gcc gfortran /usr/lib64/openmpi/bin/mpif90 /usr/lib64/openmpi/bin/mpicc; do
    command -v "$tool" >/dev/null || { echo "Missing build dependency: $tool" >&2; exit 1; }
done
printf '%s  %s\n' 7e1f7a9a21b63192f5135218bee20a5321b66582e4756536681b76e9c59b3cc8 "$qe_root/q-e-qe-7.5.tar.gz" | sha256sum -c -
while read -r qe_commit qe_dependency; do
    case "$qe_dependency" in
        fox|mbd|devxlib|wannier90)
            qe_dependency_dir="$qe_root/q-e-qe-7.5/external/$qe_dependency"
            test "$(git -C "$qe_dependency_dir" rev-parse HEAD)" = "$qe_commit"
            git -C "$qe_dependency_dir" diff --exit-code HEAD --
            ;;
    esac
done < "$qe_root/q-e-qe-7.5/external/submodule_commit_hash_records"
export PATH="/usr/lib64/openmpi/bin:$PATH"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cmake -S "$qe_root/q-e-qe-7.5" -B "$qe_root/build" \
    -DCMAKE_C_COMPILER=/usr/lib64/openmpi/bin/mpicc \
    -DCMAKE_Fortran_COMPILER=/usr/lib64/openmpi/bin/mpif90 \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
    -DQE_ENABLE_MPI=ON -DQE_ENABLE_OPENMP=OFF -DQE_ENABLE_SCALAPACK=OFF \
    -DQE_ENABLE_HDF5=OFF -DQE_ENABLE_LIBXC=OFF -DQE_ENABLE_TEST=OFF \
    -DQE_FFTW_VENDOR=FFTW3 -DBLA_VENDOR=OpenBLAS \
    2>&1 | tee "$qe_log_dir/configure.log"
cmake --build "$qe_root/build" --target pw --parallel 2 \
    2>&1 | tee "$qe_log_dir/build.log"
sha256sum "$qe_root/build/bin/pw.x"
