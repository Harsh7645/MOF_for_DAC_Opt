"""Independent numerical checks for the research contract."""

import copy
import io
import itertools
import json
import tarfile
from pathlib import Path

import numpy as np
import pytest

from mof_dac.__main__ import run, summarize
from mof_dac.data import load_instance
from mof_dac.formulation import Problem
from mof_dac.instances import decode_slot_state, phase1_instances, slot_problem
from mof_dac.materials import load_material_manifest
from mof_dac.odac25 import (adsorption_energy, pair_adsorbate_rows, paired_metrics,
                            profile_adsorbate_rows, select_relaxed_adsorbate_targets)
from mof_dac.odac25_archive import extract_first_database
from mof_dac.optimizers import (Result, exact, repair_nearest, simulated_annealing,
                                slsqp_relaxation, slot_simulated_annealing)
from mof_dac.parameters import fit_pairwise, pairwise_design
from mof_dac.phase1 import run_sweep
from mof_dac.phase3 import run_benchmark
from mof_dac.snn import solve_convex_control


FIXTURE = Path(__file__).resolve().parents[1] / "data/synthetic/toy.json"


def test_energy_qubo_gradient_and_penalty():
    p, raw = load_instance(FIXTURE)
    for bits in itertools.product((0, 1), repeat=p.n):
        x = np.array(bits, dtype=float)
        lookup = dict(zip(p.ids, bits))
        expected = sum(node["h"] * lookup[node["id"]] for node in raw["nodes"])
        expected += sum(edge["J"] * lookup[edge["i"]] * lookup[edge["j"]] for edge in raw["edges"])
        assert p.energy(x) == pytest.approx(expected)
        assert x @ p.binary_qubo() @ x == pytest.approx(expected)
        Q, offset = p.equality_penalty_qubo(7)
        assert x @ Q @ x + offset == pytest.approx(expected + 7 * np.sum((p.E @ x - p.e)**2))
    x = np.linspace(0.1, 0.8, p.n)
    assert p.energy(x) != pytest.approx(x @ p.binary_qubo() @ x)
    numerical = np.array([(p.energy(x + delta * 1e-6) - p.energy(x - delta * 1e-6)) / 2e-6
                          for delta in np.eye(p.n)])
    np.testing.assert_allclose(p.gradient(x), numerical, atol=1e-8)


def test_exact_hand_computed_solution_and_constraints():
    p, _ = load_instance(FIXTURE)
    result = exact(p)
    assert result.status == "optimal"
    assert result.diagnostics["feasible_states"] == 10
    np.testing.assert_array_equal(result.x, [1, 0, 1, 1, 0, 0])
    assert p.energy(result.x) == pytest.approx(-4.6)
    assert not p.feasible(np.zeros(p.n), binary=True)
    assert not p.feasible([1, 0, 1, 0, 1, 0], binary=True)  # hard clash
    assert not p.feasible([1, 1, 1, 1, 1, 1], binary=True)  # two metals
    A, b, C, d = p.snn_arrays()
    np.testing.assert_allclose(0.5 * result.x @ A @ result.x + b @ result.x, -4.6)
    assert np.max(C @ result.x + d) <= 1e-7
    assert p.spectrum()["min_eigenvalue"] < 0 < p.spectrum()["max_eigenvalue"]
    with pytest.raises(ValueError, match="Indefinite"):
        solve_convex_control(p, result.x)


def test_rounding_failure_repair_and_no_energy_leakage():
    p = Problem(("a", "b"), np.array([10., -10.]), np.zeros((2, 2)),
                np.ones((1, 2)), np.array([1.]), np.empty((0, 2)), np.empty(0))
    relaxed = np.array([0.5, 0.5])
    assert p.feasible(relaxed)
    rounded = (relaxed >= 0.5).astype(float)
    assert not p.feasible(rounded, binary=True)
    repaired = repair_nearest(p, relaxed)
    np.testing.assert_array_equal(repaired.x, [1, 0])  # distance tie; first integer, worse energy
    np.testing.assert_array_equal(exact(p).x, [0, 1])
    assert summarize(p, Result("threshold", rounded, 0, "rounded"), -10)["absolute_gap"] is None
    _, _, C, d = p.snn_arrays(equality_band=0.01)
    assert np.max(C @ np.array([0.5, 0.505]) + d) <= 0
    assert not p.feasible([0.5, 0.505])  # band is not exact equality


@pytest.mark.parametrize("mutation", ["edge", "endpoint", "units", "nan", "constraint", "missing", "duplicate_node"])
def test_loader_rejects_corrupt_input(tmp_path, mutation):
    raw = json.loads(FIXTURE.read_text())
    if mutation == "edge":
        raw["edges"].append({**raw["edges"][0], "i": "L0", "j": "M0"})
    elif mutation == "endpoint":
        raw["edges"][0]["i"] = "absent"
    elif mutation == "units":
        raw["nodes"][0]["units"] = "eV"
    elif mutation == "nan":
        raw["nodes"][0]["h"] = float("nan")
    elif mutation == "constraint":
        raw["constraints"][0]["coefficients"]["absent"] = 1
    elif mutation == "missing":
        raw["missing_interactions"] = "unknown"
    else:
        raw["nodes"].append(copy.deepcopy(raw["nodes"][0]))
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValueError):
        load_instance(path)


def test_seeded_solvers_and_pipeline():
    p, _ = load_instance(FIXTURE)
    a, b = simulated_annealing(p, seed=7), simulated_annealing(p, seed=7)
    np.testing.assert_array_equal(a.x, b.x)
    assert a.diagnostics == b.diagnostics
    assert p.feasible(a.x, binary=True)
    relaxed = slsqp_relaxation(p, seed=7, restarts=3)
    assert relaxed.x is not None and p.feasible(relaxed.x)
    assert p.feasible(repair_nearest(p, relaxed.x).x, binary=True)
    report = run(FIXTURE, seed=7)
    json.dumps(report, allow_nan=False)
    assert report["oracle"]["energy"] == pytest.approx(-4.6)
    assert report["snn"]["status"] == "not_run"


def test_infeasible_and_resource_limits():
    p = Problem(("a",), np.zeros(1), np.zeros((1, 1)), np.ones((1, 1)),
                np.array([2.]), np.empty((0, 1)), np.empty(0))
    assert exact(p).status == "infeasible"
    assert repair_nearest(p, [0.5]).x is None
    assert slsqp_relaxation(p, restarts=1).x is None
    assert simulated_annealing(p, initialization_attempts=10).status == "initialization_failed"
    large = Problem(tuple(map(str, range(21))), np.zeros(21), np.zeros((21, 21)),
                    np.empty((0, 21)), np.empty(0), np.empty((0, 21)), np.empty(0))
    with pytest.raises(ValueError, match="n<=20"):
        exact(large)
    with pytest.raises(ValueError):
        p.energy([float("nan")])


def test_redundant_and_inconsistent_equalities():
    p = slot_problem(4, seed=4)
    result = slsqp_relaxation(p, restarts=2)
    assert result.x is not None and p.feasible(result.x)
    audit = result.diagnostics["equality_audit"]
    assert audit["original_rows"] == 6 and audit["rank"] == 5
    inconsistent = Problem(("a", "b"), np.zeros(2), np.zeros((2, 2)),
                           np.array([[1., 1.], [2e6, 2e6]]), np.array([1., 2e6 + 1.]),
                           np.empty((0, 2)), np.empty(0))
    assert slsqp_relaxation(inconsistent).status == "inconsistent_equalities"


def test_slot_family_energy_feasibility_and_edge_cases():
    family = phase1_instances()
    for name, problem in family.items():
        result = exact(problem)
        assert (result.status == "infeasible") == name.endswith("infeasible")
        if result.x is not None:
            assert problem.feasible(result.x, binary=True)
            assert result.diagnostics["feasible_states"] > 0
    degenerate = family["slots4_degenerate"]
    assert exact(degenerate).diagnostics["feasible_states"] > 1
    assert degenerate.energy(exact(degenerate).x) == 0
    fractional = np.full(family["slots4_frustrated"].n, 0.5)
    assert family["slots4_frustrated"].feasible(fractional)
    assert not family["slots4_frustrated"].feasible((fractional >= 0.5).astype(float), binary=True)


def test_pairwise_parameter_recovery_and_rank_guard():
    problem = slot_problem(2, seed=9)
    states = np.array(list(itertools.product((0., 1.), repeat=problem.n)))
    targets = 2.5 + problem.energy(states)
    fit = fit_pairwise(states, targets)
    assert fit["offset"] == pytest.approx(2.5)
    np.testing.assert_allclose(fit["h"], problem.h, atol=1e-10)
    np.testing.assert_allclose(fit["W"], problem.W, atol=1e-10)
    assert fit["rmse"] < 1e-10
    with pytest.raises(ValueError, match="unidentifiable"):
        fit_pairwise(states[:2], targets[:2])
    assert pairwise_design(states).shape == (16, 11)


def test_phase1_sweep_contract():
    report = run_sweep(seeds=range(2))
    assert report["parameter_regime"] == "synthetic"
    assert len(report["instances"]) == 6
    assert all(row["sa_feasible_runs"] == row["sa_runs"]
               for row in report["instances"] if not row["expected_infeasible"])


def test_scalable_slot_decoder():
    state = np.array([0.9, 0.1, 0.2, 0.8, 0.6, 0.4])
    decoded = decode_slot_state(state, 1)
    np.testing.assert_array_equal(decoded, [1, 0, 0, 1, 1, 0])
    assert slot_problem(3, functionalized=1).feasible(decoded, binary=True)


def test_live_convex_snn_control():
    pytest.importorskip("snn_opt")
    p = Problem(("a", "b"), np.array([-1., -2.]), np.zeros((2, 2)),
                np.ones((1, 2)), np.array([1.]), np.empty((0, 2)), np.empty(0))
    result = solve_convex_control(p, [0.5, 0.5], max_iterations=5000, equality_band=0)
    np.testing.assert_allclose(result.x, [0, 1], atol=1e-7)
    assert result.status == "converged_feasible"
    assert result.diagnostics["original_constraints_feasible"]


def test_dense_slot_generator_is_reproducible():
    a = slot_problem(8, seed=100, interaction_density=0.4, interaction_scale=1.0)
    b = slot_problem(8, seed=100, interaction_density=0.4, interaction_scale=1.0)
    np.testing.assert_array_equal(a.h, b.h)
    np.testing.assert_array_equal(a.W, b.W)
    assert np.count_nonzero(a.W) > 0 and a.spectrum()["min_eigenvalue"] < 0
    with pytest.raises(ValueError):
        slot_problem(4, interaction_density=1.1)


def test_slot_sa_is_reproducible_and_feasible():
    p = slot_problem(6, seed=2, functionalized=3)
    a = slot_simulated_annealing(p, 3, seed=5, steps=100)
    b = slot_simulated_annealing(p, 3, seed=5, steps=100)
    np.testing.assert_array_equal(a.x, b.x)
    assert a.diagnostics == b.diagnostics and p.feasible(a.x, binary=True)


def test_gurobi_matches_tiny_oracle():
    pytest.importorskip("gurobipy")
    from mof_dac.gurobi import solve_gurobi
    p, _ = load_instance(FIXTURE)
    result = solve_gurobi(p, time_limit=10)
    assert result.status == "optimal"
    assert p.feasible(result.x, binary=True)
    assert p.energy(result.x) == pytest.approx(p.energy(exact(p).x))
    assert result.diagnostics["best_bound"] == pytest.approx(p.energy(result.x))


def test_phase3_quick_heldout_contract(tmp_path):
    pytest.importorskip("gurobipy")
    pytest.importorskip("snn_opt")
    source = tmp_path / "phase2.json"
    source.write_text('{"schema_version": 2}', encoding="utf-8")
    report = run_benchmark(source, quick=True)
    heldout = report["heldout"]
    assert len(heldout["instances"]) == 9
    assert all(row["reference"]["status"] == "optimal" for row in heldout["instances"])
    assert all(row["snn_run"]["decoded_feasible"] for row in heldout["instances"])
    assert all(summary["sa_feasible_fraction"] == 1
               for summary in heldout["summary_by_bits"].values())


def test_material_manifest_requires_provenance_conditions_and_files(tmp_path):
    cif = tmp_path / "sample.cif"
    cif.write_text("data_test\n", encoding="utf-8")
    header = "structure_id,cif_path,target,target_units,split,source,license,conditions_json\n"
    manifest = tmp_path / "manifest.csv"
    manifest.write_text(header +
                        'm1,sample.cif,-0.4,eV,test,doi:test,CC BY 4.0,"{""adsorbate"":""CO2""}"\n',
                        encoding="utf-8")
    rows = load_material_manifest(manifest)
    assert rows[0]["target"] == pytest.approx(-0.4)
    assert rows[0]["conditions"] == {"adsorbate": "CO2"}
    manifest.write_text(header +
                        'm1,missing.cif,-0.4,eV,test,doi:test,CC BY 4.0,"{}"\n',
                        encoding="utf-8")
    with pytest.raises(ValueError):
        load_material_manifest(manifest)


def test_odac25_pairing_energy_and_metrics():
    assert adsorption_energy(-15, -10, -2, -1, 2, 1) == pytest.approx(0)
    rows = [
        {"mof_id": "m1", "split": "test", "adsorbate": "co2",
         "adsorption_energy_ev": -0.5},
        {"mof_id": "m1", "split": "test", "adsorbate": "h2o",
         "adsorption_energy_ev": -0.2},
        {"mof_id": "m2", "split": "test", "adsorbate": "co2",
         "adsorption_energy_ev": -0.3},
    ]
    paired = pair_adsorbate_rows(rows)
    assert paired == [{"mof_id": "m1", "split": "test",
                       "co2_adsorption_energy_ev": -0.5,
                       "h2o_adsorption_energy_ev": -0.2}]
    metrics = paired_metrics([[-0.5, -0.2], [-0.1, -0.4]],
                             [[-0.4, -0.2], [-0.2, -0.3]], top_k=1)
    np.testing.assert_allclose(metrics["mae_ev"], [0.1, 0.05])
    assert metrics["competition_top_k_overlap"] == 1
    with pytest.raises(ValueError, match="Split leakage"):
        pair_adsorbate_rows(rows + [{"mof_id": "m1", "split": "train",
                                     "adsorbate": "co2", "adsorption_energy_ev": -0.4}])


def test_odac25_stream_extract_and_target_profile(tmp_path):
    archive = io.BytesIO()
    with tarfile.open(fileobj=archive, mode="w:gz") as tar:
        for name, content in (("val/gcmc/part_0.aselmdb", b"skip"),
                              ("val/mof_plus_adsorbate/part_0.aselmdb", b"target")):
            info = tarfile.TarInfo(name)
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))
    archive.seek(0)
    result = extract_first_database(archive, "val/mof_plus_adsorbate", tmp_path,
                                    max_scan_bytes=1024**2)
    selected = Path(result["selected"]["local_path"])
    assert selected.read_bytes() == b"target"
    assert result["selected"]["size_bytes"] == 6

    rows = [
        {"mof_name": "m1", "name": "m1_co2", "fid": 0, "nco2": 1,
         "nh2o": 0, "nn2": 0, "no2": 0, "nads": 1,
         "energy_ads_corrected": -0.4},
        {"mof_name": "m1", "name": "m1_co2", "fid": 1, "nco2": 1,
         "nh2o": 0, "nn2": 0, "no2": 0, "nads": 1,
         "energy_ads_corrected": -0.5},
        {"mof_name": "m1", "name": "m1_h2o", "fid": 0, "nco2": 0,
         "nh2o": 1, "nn2": 0, "no2": 0, "nads": 1,
         "energy_ads_corrected": -0.2},
        {"mof_name": "bad", "name": "bad", "fid": 0, "nco2": 1,
         "nh2o": 1, "nn2": 0, "no2": 0, "nads": 1,
         "energy_ads_corrected": -0.1},
    ]
    profile = profile_adsorbate_rows(rows)
    assert profile["records"] == 4
    assert profile["finite_corrected_targets"] == {"co2": 2, "h2o": 1}
    assert profile["mofs_with_both_single_adsorbates"] == 1
    assert profile["mof_adsorbate_groups_with_multiple_records"] == 1
    assert profile["inconsistent_adsorbate_count_rows"] == 1


def test_odac25_relaxation_target_selection_is_deterministic():
    def row(mof, name, fid, co2, h2o, energy):
        return {"mof_name": mof, "name": name, "fid": fid, "nco2": co2,
                "nh2o": h2o, "nn2": 0, "no2": 0, "nads": co2 + h2o,
                "energy_ads_corrected": energy}

    rows = [
        row("m1", "c_a", 0, 1, 0, -0.9),
        row("m1", "c_a", 2, 1, 0, -0.4),
        row("m1", "c_b", 3, 1, 0, -0.6),
        row("m1", "w_a", 1, 0, 1, -0.3),
        row("m1", "mixed", 1, 1, 1, -2.0),
    ]
    selected = select_relaxed_adsorbate_targets(rows, split="validation")
    assert [(item["adsorbate"], item["adsorption_energy_ev"])
            for item in selected] == [("co2", -0.6), ("h2o", -0.3)]
    assert selected[0]["selected_trajectory"] == "c_b"
    assert selected[0]["trajectory_candidates"] == 2
    paired = pair_adsorbate_rows(selected)
    assert paired[0]["co2_adsorption_energy_ev"] == pytest.approx(-0.6)

    with pytest.raises(ValueError, match="Duplicate final-frame"):
        select_relaxed_adsorbate_targets([rows[0], rows[0]], split="validation")


def test_material_baselines_are_train_only_and_reproducible():
    from mof_dac.material_baselines import evaluate_composition_baselines

    def paired(mof, split, element, co2, h2o):
        return {"mof_id": mof, "split": split,
                "bare_atomic_numbers": [6, 6, 8, element],
                "co2_adsorption_energy_ev": co2,
                "h2o_adsorption_energy_ev": h2o}

    train = [paired(f"t{i}", "train", 12 + i, -0.1 * i, -0.05 * i)
             for i in range(6)]
    validation = [paired("v0", "val", 14, -0.25, -0.15),
                  paired("v1", "val", 16, -0.45, -0.30)]
    first = evaluate_composition_baselines(train, validation, top_k=1)
    second = evaluate_composition_baselines(train, validation, top_k=1)
    assert first == second
    assert first["train_samples"] == 6 and first["validation_samples"] == 2
    assert first["selected_alpha"] in {0.01, 0.1, 1.0, 10.0}
    with pytest.raises(ValueError, match="leakage"):
        evaluate_composition_baselines(train, [paired("t0", "val", 14, -0.2, -0.1)])


def test_prediction_rows_require_the_same_material_pool():
    from mof_dac.odac25 import evaluate_prediction_rows

    target = [{"mof_id": "m1", "split": "val", "adsorbate": gas,
               "adsorption_energy_ev": value}
              for gas, value in (("co2", -0.4), ("h2o", -0.2))]
    result = evaluate_prediction_rows(target, target, split="val", top_k=1)
    assert result["metrics"]["mae_ev"] == [0.0, 0.0]
    assert result["metrics"]["competition_spearman"] is None
    with pytest.raises(ValueError, match="pool mismatch"):
        evaluate_prediction_rows(target, [], split="val")
