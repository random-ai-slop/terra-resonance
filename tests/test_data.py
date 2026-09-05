"""Data identity, scientific validity and durable project roundtrips."""
from copy import deepcopy
import math

import numpy as np
import pytest

from earth_modes.data import (bundle_hash, canonical_hash, default_scene, load_bundle, load_project,
                             make_project, mass_integral, model_hash, save_bundle, save_project,
                             validate_bundle, validate_export_spec, validate_model, validate_scene, validate_probe)
from earth_modes.models import homogeneous_model, prem_model
from test_fields import field_bundle


def test_jcs_identity_unknown_metadata_and_invalid_domain():
    assert canonical_hash({"n": 1, "z": -0.0}) == canonical_hash({"z": 0, "n": 1.0})
    assert canonical_hash({"b": 1e-7, "a": "地球🙂"}) == canonical_hash({"a": "地球🙂", "b": 0.0000001})
    for invalid in (float("inf"), float("nan"), 2**53, "\ud800", {"metadata": [float("nan")]}):
        with pytest.raises(ValueError):
            canonical_hash(invalid)
    bundle = field_bundle()
    original = deepcopy(bundle)
    assert validate_bundle(bundle) == original
    changed = deepcopy(bundle)
    changed["model"]["provenance"]["note"] = "retained metadata"
    assert model_hash(changed["model"]) == model_hash(bundle["model"])
    assert bundle_hash(changed) != bundle_hash(bundle)
    changed["model"]["name"] = "Renamed"
    assert model_hash(changed["model"]) != model_hash(bundle["model"])


def test_mass_quadrature_and_center_validation_are_not_relabeling():
    bundle = field_bundle()
    mode = bundle["modes"][1]
    assert math.isclose(mass_integral(bundle["model"], mode), 1, rel_tol=1e-14)
    # Different density and eigenfunction grids, with an independently
    # calculated sum: r=[0,1,2], rho=[2,3,4], u=r gives trap [0,3,64]=35.
    model = homogeneous_model(2.0, 2.0, 4.0, 2.0)
    model["layers"][0]["rho_kg_m3"] = [2.0, 4.0]
    raw = deepcopy(mode)
    raw["regions"][0]["u"] = [0.0, 1.0, 2.0]
    assert mass_integral(model, raw) == 35.0
    bad = deepcopy(bundle)
    bad["modes"][0]["normalization"] = "surface_1"
    with pytest.raises(ValueError, match="normalization"):
        validate_bundle(bad)
    bad = deepcopy(bundle)
    bad["modes"][0]["regions"][0]["v"][0] *= 0.9  # r=0 norm contribution remains zero.
    with pytest.raises(ValueError, match="center regularity"):
        validate_bundle(bad)
    bad = deepcopy(bundle)
    bad["modes"][1]["regions"][0]["u"][1] *= 2
    with pytest.raises(ValueError, match="mass integral"):
        validate_bundle(bad)
    bad = deepcopy(bundle)
    bad["modes"][0]["provenance"]["quality"]["status"] = "converged"
    with pytest.raises(ValueError, match="evidence"):
        validate_bundle(bad)


def test_model_interfaces_phase_and_bundled_prem():
    prem = prem_model()
    assert prem["radius_m"] == 6371000
    assert len(prem["layers"]) == 13
    assert sum(layer["phase"] == "fluid" for layer in prem["layers"]) == 1
    assert prem["reference_frequency_hz"] == 0.003
    assert all("q_shear" not in layer for layer in prem["layers"])
    for left, right in zip(prem["layers"], prem["layers"][1:]):
        assert left["r_m"][-1] == right["r_m"][0]
    bad = deepcopy(prem)
    bad["layers"][1]["vs_m_s"][0] = 10
    with pytest.raises(ValueError, match="fluid"):
        validate_model(bad)
    bad = homogeneous_model()
    bad["layers"][0]["q_bulk"] = [0, None]
    with pytest.raises(ValueError):
        validate_model(bad)
    assert homogeneous_model(vs_m_s=0)["layers"][0]["phase"] == "fluid"


def test_project_roundtrip_atomic_existing_file_and_no_mutation(tmp_path):
    bundle = field_bundle()
    scene = default_scene(bundle)
    original = deepcopy((bundle, scene))
    project = make_project(bundle, scene, export={"format": "gif"})
    assert (bundle, scene) == original
    scene["time_s"] = 99  # Project owns its snapshot.
    assert project["scene"]["time_s"] == 0
    path = tmp_path / "project.json"
    save_project(project, path)
    assert load_project(path) == project
    before = path.read_bytes()
    with pytest.raises(FileExistsError):
        save_project(project, path)
    assert path.read_bytes() == before
    save_project(project, path, overwrite=True)
    save_bundle(bundle, tmp_path / "bundle.json")
    assert load_bundle(tmp_path / "bundle.json") == bundle
    corrupt = deepcopy(project)
    corrupt["bundle"]["provenance"]["edited"] = True
    with pytest.raises(ValueError, match="bundle_hash"):
        save_project(corrupt, path, overwrite=True)
    assert path.read_bytes() == before
    path.write_text('{"format":"terra-project","format":"bad"}')
    with pytest.raises(ValueError, match="duplicate"):
        load_project(path)


def test_scene_point_trajectory_nodes_and_production_options():
    bundle = field_bundle()
    scene = default_scene(bundle)
    original = deepcopy(scene)
    validate_scene(scene, bundle)
    assert scene == original
    scene["geography"] = True
    scene["radius_fraction"] = 0.5
    with pytest.raises(ValueError, match="geography"):
        validate_scene(scene, bundle)
    scene = deepcopy(original)
    scene["trajectory"]["enabled"] = True
    with pytest.raises(ValueError, match="requires scene.point"):
        validate_scene(scene, bundle)
    scene["point"] = {"latitude_deg": 30, "longitude_deg": 100, "radius_fraction": 1}
    validate_scene(scene, bundle)
    scene["trajectory"]["samples"] = 8
    with pytest.raises(ValueError, match="24"):
        validate_scene(scene, bundle)
    scene = deepcopy(original)
    scene["point"] = {"latitude_deg": 30, "longitude_deg": 100}
    with pytest.raises(ValueError, match="radius_fraction"):
        validate_scene(scene, bundle)
    probe = {"latitude_deg": 30, "longitude_deg": 100, "start_s": 0, "step_s": 1, "sample_count": 2}
    validate_probe(probe, bundle)  # Probe, unlike a saved Scene point, permits default radius.
    assert validate_probe({**probe, "derivative": 1.0}, bundle)["derivative"] == 1
    with pytest.raises(ValueError, match="derivative"):
        validate_probe({**probe, "derivative": 1.5}, bundle)
    with pytest.raises(ValueError, match="time resolution"):
        validate_probe({**probe, "start_s": 1e12, "step_s": 1e-5}, bundle)
    validate_probe({**probe, "start_s": 1e12, "step_s": .001}, bundle)
    validate_probe({**probe, "start_s": 1e12, "step_s": 1e-5, "sample_count": 1}, bundle)
    scene = deepcopy(original)
    scene["nodes"] = True
    scene["color"] = "magnitude"
    with pytest.raises(ValueError, match="nodes"):
        validate_scene(scene, bundle)
    assert validate_export_spec({"format": "gif"})["fps"] is None
    with pytest.raises(ValueError, match="GIF"):
        validate_export_spec({"format": "gif", "fps": 24})
    with pytest.raises(ValueError, match="transparency"):
        validate_export_spec({"format": "mp4", "transparent": True})
    with pytest.raises(ValueError, match="unknown"):
        validate_export_spec({"format": "png", "aspect": 2})


def test_frequency_evidence_must_match_model_quantity_and_actual_error():
    bundle = field_bundle()
    mode = bundle["modes"][0]
    benchmark = dict(source="Analytic fixture, not an Earth benchmark", quantity="frequency_hz",
                     reference_frequency_hz=mode["frequency_hz"], relative_error=0,
                     tolerance=.005, model_hash=model_hash(bundle["model"]))
    mode["provenance"]["quality"].update(status="benchmark_checked", benchmark=benchmark)
    assert validate_bundle(bundle) is bundle
    for key, value in (("model_hash", "0" * 64), ("quantity", "unrelated"),
                       ("reference_frequency_hz", 2 * mode["frequency_hz"]), ("relative_error", .1)):
        bad = deepcopy(bundle)
        bad["modes"][0]["provenance"]["quality"]["benchmark"][key] = value
        with pytest.raises(ValueError, match="benchmark"):
            validate_bundle(bad)
    # Allow equivalent formulas' binary64 subtraction rounding, not stale evidence.
    benchmark["relative_error"] = np.finfo(float).eps
    validate_bundle(bundle)
    from pathlib import Path
    load_bundle(Path(__file__).parents[1] / "examples/prem-modes.json")


def test_json_integer_values_preserve_hash_and_execute_fields_and_exports(tmp_path):
    from earth_modes.fields import evaluate_field
    from earth_modes.export import export_artifact, export_probe
    bundle = field_bundle()
    identity = bundle_hash(bundle)
    for mode in bundle["modes"]:
        mode["l"], mode["n"] = float(mode["l"]), float(mode["n"])
    validate_bundle(bundle)
    assert bundle_hash(bundle) == identity
    assert isinstance(bundle["modes"][0]["l"], float)
    scene = default_scene(bundle)
    scene["terms"][0]["m"] = 0.0
    scene["point"] = {"latitude_deg": 30, "longitude_deg": 10, "radius_fraction": 1}
    scene["trajectory"].update(enabled=True, samples=32.0)
    scene["quality"] = "draft"
    validate_scene(scene, bundle)
    assert np.isfinite(evaluate_field(bundle, scene["terms"], [[0, 0, 0]], 0)).all()
    probe = {"latitude_deg": 30, "longitude_deg": 10, "start_s": 0, "step_s": 1,
             "sample_count": 3.0, "derivative": 1.0}
    export_probe(bundle, scene, probe, tmp_path / "probe.csv")
    export_artifact(bundle, scene, tmp_path / "frame.png", {"width": 64.0, "height": 64.0})
    for invalid in (True, .5, 1e21):
        bad = deepcopy(bundle)
        bad["modes"][0]["n"] = invalid
        with pytest.raises(ValueError, match="integer"):
            validate_bundle(bad)
