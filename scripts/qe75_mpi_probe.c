#define _GNU_SOURCE
#include <mpi.h>
#include <sched.h>
#include <stdio.h>
#include <unistd.h>

/* Software-only MPI collective and core-affinity check; no QE or model data. */
int main(int argc, char **argv) {
    int rank, size, total, length;
    char hostname[MPI_MAX_PROCESSOR_NAME];
    cpu_set_t affinity;
    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Get_processor_name(hostname, &length);
    MPI_Allreduce(&rank, &total, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD);
    if (sched_getaffinity(0, sizeof(affinity), &affinity) != 0) MPI_Abort(MPI_COMM_WORLD, 2);
    for (int turn = 0; turn < size; turn++) {
        MPI_Barrier(MPI_COMM_WORLD);
        if (turn == rank) {
            printf("rank=%d size=%d sum=%d host=%s cpus=", rank, size, total, hostname);
            for (int cpu = 0; cpu < CPU_SETSIZE; cpu++)
                if (CPU_ISSET(cpu, &affinity)) printf("%d,", cpu);
            printf("\n");
            fflush(stdout);
        }
    }
    MPI_Finalize();
    return size == 4 && total == 6 ? 0 : 1;
}
