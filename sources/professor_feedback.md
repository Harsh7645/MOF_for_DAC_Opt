# Professor feedback record

Source: user-supplied Discord screenshots. Message author shown as
`ameerhamzakhan`. Screenshot 2 shows June 1, 2026, 10:32 PM. Images were
captured September 10, 2026. This is a faithful summary, not a verbatim transcript.

1. Acknowledge nonconvexity and limits of the SNN-QP claim. The professor describes
   the interaction matrix as indefinite and the nonconvex solver as a heuristic
   finding local optima rather than a guaranteed global optimum. Benchmark
   solution quality against Gurobi on small instances and known good CoRE MOFs.
   Add an honest formulation statement.
2. Add explicit global selection constraints: exactly one metal-node type, a
   linker budget and charge balance. Pairwise penalties cannot enforce all these
   rules. Their inclusion produces a constrained QP, matching the lab solver's
   focus on constraint handling.
3. Decouple numerical development from chemistry parameter sourcing. CoRE stores
   assembled MOFs rather than per-block h/J values. Start with synthetic or
   controlled heuristic parameters, such as amine-density and simple geometry
   rules, and verify known-ground-truth numerical recovery. Add DFT-grounded
   coefficients in a second pass. Make both stages explicit in Phase 1.
4. Do not headline CPU wall-clock superiority over SA or Gurobi. Prioritize
   solution quality; report SA time-to-solution secondarily and honestly.
   Neuromorphic/FPGA parallelism and energy efficiency belong to a deployment
   case, not an unsupported CPU speed claim.

Professor also requests reviewing documentation and examples in
https://github.com/ahkhan03/SNN_opt/ and continuing the Lucas paper and
quantum-annealer/QUBO-MOF literature scout.

Screenshot 2 contains the student's earlier note that Lucas reading, solver code
review and literature scouting had started. It does not establish completed
literature results. The professor acknowledges the revised mathematical class
as improved, then requests the four deeper corrections before finalizing QUBO.

Implementation refinements, distinguished from source: mixed signs alone do not
prove indefiniteness; eigenvalue checks are required. Nonconvex finite-iteration
dynamics do not automatically guarantee a local minimum. Simple selection rows
are necessary but do not certify a physically realizable periodic MOF.
