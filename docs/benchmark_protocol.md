# Benchmark protocol v2

Numerical and material-ranking tracks are separate.

## Numerical track

- Development family: synthetic generator seeds 0–19, used for implementation.
- Frozen test family: dense frustrated generator seeds 100–119.
- Sizes: 12, 20 and 50 bits; exact enumeration runs through 20 bits.
- Gurobi receives a 30 s limit and one thread. SA budgets are 250, 1,000 and
  4,000 steps with solver seeds 0–2. SNN receives one deterministic start per
  instance, 2,000 iterations and exact equality constraints.
- Primary outputs: original binary feasibility, feasible-run fraction, gap to a
  certified optimum, optimum-hit rate and seed distribution. Infeasible raw SNN
  outputs receive no raw-state performance claim; decoded states stay separate.
- Secondary outputs: setup/solve/decode time, versions, seed, threads and stopping
  budgets. CPU time is descriptive and cannot support a neuromorphic speed claim.

`phase3_results.json` contains the 60-instance held-out run. The earlier seed-11
development experiment is excluded from its aggregates.

## Material-ranking track

Prerequisites: licensed assembled structures, stable identifiers, a fixed target
with temperature/pressure/composition/humidity, and a fixed candidate pool. Split
by chemistry/topology to control leakage. Select MOFTransformer, CGCNN or a current
DAC-specific model only after target/checkpoint compatibility is established.

Compare surrogate top-K against the same independently evaluated candidate pool.
Report preprocessing, training/inference and top-K validation cost. The QUBO/SNN
track ranks configurations under H; the material track tests whether H ranks the
physical target. A numerical optimum with poor physical labels is a model failure.
