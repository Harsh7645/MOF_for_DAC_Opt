# Focused numerical-review question — draft, not sent

For this frozen127atom/522electron UiO-66 water complex, does the persistent negative
valence pseudocharge below primarily suggest finite density-cutoff sensitivity,
USPP/PAW augmentation behavior, or a different issue? Would one625Ry density-cutoff
probe at fixed80Ry wavefunction cutoff be informative despite unchanged225³FFTgrid,
or is a larger-grid comparison essential and therefore better moved to more RAM?

Exact relevant input (complete input/geometry in rho600.in):

```fortran
calculation='scf', restart_mode='from_scratch', tprnfor=.true.
ecutwfc=80, ecutrho=600
input_dft='PBE', vdw_corr='grimme-d3', dftd3_version=4, dftd3_threebody=.false.
occupations='fixed', tot_charge=0, nspin=1, nosym=.true., noinv=.true.
diagonalization='cg', mixing_ndim=4, mixing_beta=0.3
conv_thr=1.0d-8, electron_maxstep=200, scf_must_converge=.true.
K_POINTS gamma
```

Exact diagnostic excerpts (up/down label is generic for nspin1):

```text
starting charge     521.9847, renormalised to     522.0000
negative rho (up, down):  3.659E-01 0.000E+00
iteration 1: negative rho 3.741E-01; estimated scf accuracy <20.00902028 Ry
iteration 2: negative rho 3.836E-01; estimated scf accuracy < 2.51087335 Ry
iteration 3: negative rho 3.887E-01; estimated scf accuracy < 0.66475787 Ry
iteration 4: negative rho 3.940E-01; estimated scf accuracy < 0.26218816 Ry
```

Combined iteration lines above align unaltered numeric fields for brevity; original
line-numbered excerpts are `evidence/qe75-rho-diagnostic-plan-v1/output-excerpts.txt`.
Source confirms negative charge is integrated over mixed valence pseudodensity in
unconverged SCF. We do not use0.1 or0.522electrons as acceptance thresholds.

UPFs: Zr_pbe_v1.uspp.F.UPF (USPP,NLCC);N.oncvpsp.upf(NC,NLCC);
H_ONCV_PBE-1.0.oncvpsp.upf(NC);C.pbe-n-kjpaw_psl.1.0.0.UPF and
O.pbe-n-kjpaw_psl.0.1.UPF(PAW,NLCC). Exact SHA256 and SSSP1.3.0 PBE Precision
recommendations are in pseudopotential-pins.json.600Ry meets the largest recommendation.
No explicit FFT overrides; dense225³/G1902004;smooth160³/G741079. Increasing only
rho to625 gives225³/G2022032 in offline source-matched enumeration.650 gives240³;
750 gives243³. Cutoff convergence and final density are unmeasured.

Prior early-SCF peak9.314GiB; proposed625 estimated9.71–9.90GiB under11GiBhard,
10GiBhigh/zero swap.750 estimated12–13GiB does not fit this allocation. No higher-
cutoff QE run has occurred. No complete checkpoint/converged energy/forces exist.
