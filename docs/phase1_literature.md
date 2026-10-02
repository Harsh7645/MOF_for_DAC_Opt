# Phase 1 literature comparison

Search frozen 2026-09-10. This is a scoped comparison, not proof of novelty or a
systematic review. Searches combined MOF, direct air capture/CO2 adsorption,
QUBO, Ising, quantum annealing, SNN optimization, linker selection and material
design. Papers were classified by the optimization object because electronic-
structure quantum algorithms and combinatorial annealing solve different problems.

| Source | Object and method | Relation to this project | Boundary |
|---|---|---|---|
| [Lucas 2014](https://doi.org/10.3389/fphy.2014.00005) | General Ising encodings for NP problems; equality penalties, assignment and inequality constructions | Supplies constraint-encoding vocabulary and penalty-scale reasoning | No MOF, DAC, SNN or chemistry parameter model |
| [Mancoo, Keemink & Machens 2020](https://proceedings.neurips.cc/paper_files/paper/2020/file/64714a86909d401f8feb83e8c2d94b23-Paper.pdf) | LIF networks interpreted through constrained convex LP/QP dynamics | Supports the convex-control mapping used to validate the lab solver | Does not justify indefinite nonconvex QP guarantees |
| [Kitai et al. 2020](https://www.tsudalab.org/publication/2020-kitai-designing/) | Factorization-machine quadratic surrogate plus D-Wave candidate selection for thermofunctional metamaterials | Closest retrieved analogue to a learned quadratic material-design loop | Different materials and target; no MOF/DAC chemistry |
| [Greene-Diniz et al. 2022](https://doi.org/10.1140/epjqt/s40507-022-00155-w) | DMET fragmentation and a variational quantum fragment solver for CO2 adsorption in Al-fumarate | Relevant quantum-computing carbon-capture context | Electronic-structure calculation, not QUBO building-block selection |
| [Kang et al. 2023, MOFTransformer](https://doi.org/10.1038/s42256-023-00628-2) | Multimodal pretrained representation for property transfer learning on assembled MOFs | Candidate report-named surrogate-screening baseline | Does not supply pairwise h/J values or an automatically valid DAC label |
| [Owens et al. 2025](https://arxiv.org/abs/2504.17453) | VQE/UCCSD simulations of a molecular analogue of an amine-functionalized MOF | Relevant material motif and quantum-chemistry limitations | Simulated QPUs and restricted active spaces; no annealing/SNN selection |
| [Hörfarter et al. 2026](https://doi.org/10.1002/jcc.70349) | Monte Carlo simulated annealing of linker orientations using a neural-network potential, including UiO-66(Zr)-NH2 | Strong classical comparator for configuration search and move design | Optimizes orientation energy, not DAC performance or the present h/J model |
| [Rocca et al. 2026](https://doi.org/10.1039/D6DD00023A) | Periodic Fe-MOF-74 adsorption study using DFT, active-space reduction, VQE and sample-based quantum diagonalization | Shows a modern validation chain and publishes code/data | Electronic structure on a fixed material, not combinatorial QUBO selection |
| [CoRE MOF 2019](https://doi.org/10.1021/acs.jced.9b00835) | Computation-ready experimental MOF structures | Candidate source for assembled structures and known examples | Not a table of per-block h_i and J_ij coefficients |

## Mapping conclusions

Lucas supports the algebra, not the chemistry. For bits, one-hot occupancy uses
`rho*(sum(x)-1)^2`; an integer inequality needs bounded slack before squaring.
The main implementation retains constraints explicitly. A later hardware QUBO
export must report ancilla count, coefficient range and embedding cost.

Mancoo et al. formulate the relevant SNN interpretation around convex objectives
and inequality-bounded dynamics. The project's generally indefinite W therefore
falls outside the cited guarantee. Phase 2 starts with convex controls and labels
subsequent nonconvex behavior experimental.

The retrieved MOF quantum-computing papers use VQE or related electronic-structure
workflows. They estimate energies for fixed systems; they do not solve the proposed
building-block QUBO. Kitai supplies a closer algorithmic analogy, while Hörfarter
supplies a closer MOF configuration-search comparator.

No reviewed source directly combined all of constrained MOF slot selection,
pairwise QUBO, DAC objective and an SNN-QP solver. This is a provisional gap
statement from the scoped search, not a first-of-kind claim. Update it through
backward/forward citation searches before any manuscript novelty statement.
