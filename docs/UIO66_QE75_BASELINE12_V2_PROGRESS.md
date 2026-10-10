# Authorized remaining baseline batch recovery v2

Status: **completed**. Elapsed 18.498 h of immutable 48 h.

|Order|Manifest ID|State|Runtime through cleanup (s)|Peak GiB|Evidence|
|---|---|---|---:|---:|---|
|1|`uio66_110111_H2O_s28_f0.010_host`|completed|4058.322767496109|9.522621154785156|`evidence/qe75-baseline12-recovery-v2/job01`|
|2|`uio66_110111_H2O_s28_f0.005_host`|completed|4130.211340665817|9.427398681640625|`evidence/qe75-baseline12-recovery-v2/job02`|
|3|`uio66_110111_CO2_s7_f0.020_complex`|completed|4286.6621351242065|9.377010345458984|`evidence/qe75-baseline12-recovery-v2/job03`|
|4|`uio66_110111_CO2_s7_f0.020_host`|completed|4038.736759185791|9.256462097167969|`evidence/qe75-baseline12-recovery-v2/job04`|
|5|`uio66_110111_CO2_s7_f0.010_complex`|completed|4266.710968732834|9.302181243896484|`evidence/qe75-baseline12-recovery-v2/job05`|
|6|`uio66_110111_CO2_s7_f0.010_host`|completed|4061.29362988472|9.431346893310547|`evidence/qe75-baseline12-recovery-v2/job06`|
|7|`uio66_110111_CO2_s7_f0.005_complex`|completed|4556.908764839172|9.537063598632812|`evidence/qe75-baseline12-recovery-v2/job07`|
|8|`uio66_110111_CO2_s7_f0.005_host`|completed|4679.876195669174|9.489349365234375|`evidence/qe75-baseline12-recovery-v2/job08`|
|9|`uio66_000000_CO2_s16_f0.010_complex`|completed|3891.9408247470856|9.405624389648438|`evidence/qe75-baseline12-recovery-v2/job09`|
|10|`uio66_000000_CO2_s16_f0.010_host`|completed|3649.7983014583588|9.320816040039062|`evidence/qe75-baseline12-recovery-v2/job10`|
|11|`uio66_000000_CO2_s16_f0.005_complex`|completed|3872.9884111881256|9.202964782714844|`evidence/qe75-baseline12-recovery-v2/job11`|
|12|`uio66_000000_CO2_s16_f0.005_host`|completed|3700.121311187744|9.118217468261719|`evidence/qe75-baseline12-recovery-v2/job12`|

Updated UTC: 2026-10-10T03:47:31.359376+00:00
Automatic update every 10 minutes while active, and on every start/finish/stop.
Original batch deadline: 2026-10-11 09:17:37 UTC (14:47:37 IST); Windows/offline time counts.
Previous job01 attempt interrupted by confirmed switch to Windows; preserved under v1. Recovery uses clean new directory because XML/density checkpoint is absent.
Do not reboot, log out, switch OS or close the lid during calculation. Sleep inhibition does not prevent shutdown.


Blocker: none

Four physical cores, 11-GiB hard / 10-GiB high, zero job swap, 96 tasks. One recovery attempt for interrupted job01; one original attempt for each other ID. Fixed per-job and batch deadlines; no retries. Two completed water complexes excluded. Each pending launch requires fresh AC, >=12-GiB available RAM, disk, workers and inhibitor checks. Cutoff/physical accuracy and Phase 3 unresolved.

Raw outputs/checkpoints: `local/qe75-baseline12-recovery-v2/jobNN/run01/`. Comparisons: `evidence/qe75-baseline12-recovery-v2/comparisons.json`.
