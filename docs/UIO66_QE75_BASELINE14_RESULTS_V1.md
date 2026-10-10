# Frozen 80/600-Ry baseline — terminal results, 2026-10-10

**All 12 authorized remaining jobs converged and passed independent offline verification. Together with the two previously verified water complexes, all 14 mandatory baseline single points are now available. No further calculation is authorized.**

## Verification and execution

- Independently reconstructed SCF convergence, text/XML energies, composition-specific electrons, frozen coordinates/cell/atom identities, scientific settings and all **1,463 new total force vectors** from raw stdout/XML. All **320 raw file hashes** match. Both prior water input/stdout/XML pins rechecked; all 14 geometry force statistics and available archived UMA force differences independently reconstructed.
- All jobs exited successfully with JOB DONE and converged XML. SCF steps: 16–18; maximum final estimated SCF error **9.48046878554e-9 Ry**, below the unchanged 1e-8-Ry threshold. All requested forces finite. No diagonalization or other parser-identified warning lines; nonzero negative-pseudocharge diagnostics remain separately recorded.
- Four physical cores; 11-GiB hard/10-GiB high, zero job swap, 96-task limit preserved. Highest measured job peak **9.537064 GiB**; minimum sampled host available RAM **3.530083 GiB**. All recorded AC/inhibitor checks passed; zero observed memory/task-limit events or job swap.
- New runs plus worker cleanup total **13.664881 hours**. Original batch start through terminal finalization **18.498312 hours**, including the interrupted attempt, Windows/offline interval and preparation; below the original 48-hour ceiling. Every successful attempt finished within its four-hour envelope. Job01 has the one explicitly authorized clean recovery; all others ran once.
- Retained new scratch totals **9.093915 GiB**. Every new result has final XML, charge density, PAW data and four rank wavefunction files. Checkpoints remain on Fedora; future restart would still require exact build/input/parallelization compatibility checks and authorization.
- Fresh post-batch inspection confirms no QE/MPI workers, task inhibitors or temporary runtime overrides. All 48 job/guardian/timer units are inactive or failed-empty; batch service is inactive. Final cgroups were removed on normal exit, so absent final counters are not fabricated: lifetime service peaks, full sampled counters and journals provide the resource evidence.

## Per-job results

|Job|Manifest ID|Atoms / electrons|SCF steps|Final error Ry|Peak GiB|Run + cleanup min|Max force eV/Å|Final negative pseudocharge e|
|---:|---|---:|---:|---:|---:|---:|---:|---:|
|1|`uio66_110111_H2O_s28_f0.010_host`|124 / 514|16|3.90846e-09|9.522621|67.64|0.565885|0.3938|
|2|`uio66_110111_H2O_s28_f0.005_host`|124 / 514|16|7.10503e-09|9.427399|68.84|0.543679|0.3946|
|3|`uio66_110111_CO2_s7_f0.020_complex`|127 / 530|16|5.1032e-09|9.377010|71.44|0.417915|0.3938|
|4|`uio66_110111_CO2_s7_f0.020_host`|124 / 514|16|6.41524e-09|9.256462|67.31|0.262444|0.3938|
|5|`uio66_110111_CO2_s7_f0.010_complex`|127 / 530|16|9.48047e-09|9.302181|71.11|0.430901|0.3943|
|6|`uio66_110111_CO2_s7_f0.010_host`|124 / 514|16|7.70471e-09|9.431347|67.69|0.244591|0.3943|
|7|`uio66_110111_CO2_s7_f0.005_complex`|127 / 530|17|4.75467e-09|9.537064|75.95|0.435954|0.3941|
|8|`uio66_110111_CO2_s7_f0.005_host`|124 / 514|18|1.75403e-09|9.489349|78.00|0.236645|0.3941|
|9|`uio66_000000_CO2_s16_f0.010_complex`|117 / 500|16|7.35633e-09|9.405624|64.87|0.425309|0.3935|
|10|`uio66_000000_CO2_s16_f0.010_host`|114 / 484|16|3.21272e-09|9.320816|60.83|0.255001|0.3935|
|11|`uio66_000000_CO2_s16_f0.005_complex`|117 / 500|16|3.70897e-09|9.202965|64.55|0.428985|0.3943|
|12|`uio66_000000_CO2_s16_f0.005_host`|114 / 484|16|2.5542e-09|9.118217|61.67|0.277925|0.3943|

## Provisional energy differences

All differences are **later checkpoint minus earlier checkpoint**, at fixed composition. Units below are **meV**. `Guest-associated = complex difference − matching stripped-host difference`; it includes deformation/interaction/image changes and is not an isolated adsorption energy. Never compare raw total energies across different compositions as a material ranking.

|Transition|DFT complex|UMA complex|DFT − UMA complex|DFT host|DFT guest-associated|
|---|---:|---:|---:|---:|---:|
|110111 H₂O s28: 0.010 → 0.005|-38.396707|-41.461081|+3.064374|-21.725487|-16.671220|
|110111 CO₂ s7: 0.020 → 0.010|-79.440623|-75.053958|-4.386665|+1.189612|-80.630235|
|110111 CO₂ s7: 0.010 → 0.005|-10.155191|-13.873650|+3.718459|-9.860710|-0.294481|
|000000 CO₂ s16: 0.010 → 0.005|-15.607560|-17.749933|+2.142373|-0.203710|-15.403850|

DFT and archived UMA both favor the later complex checkpoint in these four transitions at present settings. Their complex energy-change discrepancies are roughly **2.14–4.39 meV**, and cannot establish model accuracy before numerical checks. The 110111 CO₂ 0.010→0.005 guest-associated remainder is only **−0.294481 meV**, much smaller than the historically proposed 2–3-meV assessment range; its sign must not be treated as numerically resolved.

## Forces and limitations

Total-force rows were separated from verbose force-component tables. Verified XML Ha/bohr ×2 equals stdout Ry/bohr; eV/Å conversion uses Ry=13.605693122994017 eV and bohr=0.529177210903 Å. Source indices, species/type mapping and frozen structures match. All per-atom component comparisons, group maxima/RMS and archived UMA force differences are retained in `force-comparisons.json`; the independent 1,463-vector crosscheck is `terminal-review-v1/all-force-crosschecks.csv`.

The largest new **complex** force is about **0.435954 eV/Å** on a CO₂ complex. Across all twelve new jobs, the largest force is **0.565885 eV/Å**, on atom 115 of the f0.010 water stripped host. The immutable review ZIP retains the earlier wording; its raw forces, per-job table and machine-readable statistics already give the correct host value. These are deliberately frozen snapshots, not DFT-relaxed minima; large finite forces are findings rather than automatic SCF failures. Final negative pseudocharge spans **0.3935–0.3946 electrons**, with full trajectories retained. Its persistence alone is neither an accuracy pass nor rejection.

SCF convergence does **not** establish density/grid, wavefunction-cutoff, k-point or physical convergence, validate UMA, resolve publication proton correspondence, or repair the earlier failed sampling-stability pilot. Four missing UMA host single points remain separate; no values were inferred and no UMA was launched. **Phase 3 remains incomplete.**

## Next decision

Review this complete baseline and the paired force/energy evidence. The smallest already prepared next numerical check is **two paired water-complex 80/750-Ry calculations**, all other settings fixed, on a verified larger-memory allocation. Existing 12–13-GiB memory estimates exceed this laptop’s unchanged 10/11-GiB guards. No such run or limit increase is authorized. Set a binding assessment rule before interpreting the historical ranges of 2–3 meV and 0.005–0.01 eV/Å; these are not automatically selected pass thresholds. Density-only checks leave 80-Ry wavefunction cutoff, k-points and transfer to hosts/CO₂ unresolved.

## Evidence

- Raw new results: `local/qe75-baseline12-recovery-v2/job01/run01/` through `job12/run01/`.
- Ledger/accounting: `evidence/qe75-baseline12-recovery-v2/progress.json`, `batch-allocation.json`, `batch-terminal.json`, per-job `assessment.json`, `result.json`, `postflight.json`, `raw-file-hashes.json`, and resource samples.
- Independent audit: `evidence/qe75-baseline12-recovery-v2/terminal-review-v1/independent-audit.json`, `comparison-audit.json`, `all-force-crosschecks.csv`.
- Comparisons: `evidence/qe75-baseline12-recovery-v2/comparisons.json` and `force-comparisons.json`.
- Original interrupted run and all historical results preserved unchanged. No calculation was invoked during this review.
- Portable review ZIP: `artifacts/phase3/uio66_qe_baseline14_review_v1.zip`; receipt in `terminal-review-v1/portable-review-receipt.json`. Contains inputs, complete text outputs, final XML, potentials, forces, accounting and checksums. Large binary checkpoints remain in the original Fedora raw directories and are intentionally not duplicated in this review-only archive.

## Windows continuation

See `docs/UIO66_QE75_WINDOWS_BASELINE14_GUIDE.md` for Git-delivered evidence, checksum verification, portable offline analysis, the force-summary wording correction and Fedora-only checkpoint locations. No additional scientific calculation was run.
