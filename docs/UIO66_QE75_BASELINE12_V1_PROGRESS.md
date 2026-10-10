# Authorized remaining baseline batch v1

Status: **stopped**. Elapsed 0.427 h of immutable 48 h.

|Order|Manifest ID|State|Runtime through cleanup (s)|Peak GiB|Evidence|
|---|---|---|---:|---:|---|
|1|`uio66_110111_H2O_s28_f0.010_host`|interrupted|695.718|9.20755386352539|`evidence/qe75-baseline12-v1/job01`|
|2|`uio66_110111_H2O_s28_f0.005_host`|pending|||`evidence/qe75-baseline12-v1/job02`|
|3|`uio66_110111_CO2_s7_f0.020_complex`|pending|||`evidence/qe75-baseline12-v1/job03`|
|4|`uio66_110111_CO2_s7_f0.020_host`|pending|||`evidence/qe75-baseline12-v1/job04`|
|5|`uio66_110111_CO2_s7_f0.010_complex`|pending|||`evidence/qe75-baseline12-v1/job05`|
|6|`uio66_110111_CO2_s7_f0.010_host`|pending|||`evidence/qe75-baseline12-v1/job06`|
|7|`uio66_110111_CO2_s7_f0.005_complex`|pending|||`evidence/qe75-baseline12-v1/job07`|
|8|`uio66_110111_CO2_s7_f0.005_host`|pending|||`evidence/qe75-baseline12-v1/job08`|
|9|`uio66_000000_CO2_s16_f0.010_complex`|pending|||`evidence/qe75-baseline12-v1/job09`|
|10|`uio66_000000_CO2_s16_f0.010_host`|pending|||`evidence/qe75-baseline12-v1/job10`|
|11|`uio66_000000_CO2_s16_f0.005_complex`|pending|||`evidence/qe75-baseline12-v1/job11`|
|12|`uio66_000000_CO2_s16_f0.005_host`|pending|||`evidence/qe75-baseline12-v1/job12`|

Blocker: User-session shutdown interrupted job01; incomplete unconverged result. Guardian cleanup timeout left stale ledger; no automatic retry.

Four physical cores, 11-GiB hard / 10-GiB high, zero job swap, 96 tasks. One attempt per manifest ID. Fixed per-job and batch deadlines; no retries. Two completed water complexes excluded. Each pending launch requires fresh AC, >=12-GiB available RAM, disk, workers and inhibitor checks. Cutoff/physical accuracy and Phase 3 unresolved.

Raw outputs/checkpoints: `local/qe75-baseline12-v1/jobNN/run01/`. Comparisons: `evidence/qe75-baseline12-v1/comparisons.json`.
