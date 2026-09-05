"""Command journeys use a real small solve and independently inspect saved outputs."""

import copy
import csv
import json
from pathlib import Path
import subprocess
import sys

import pytest

from earth_modes.cli import main
from earth_modes import __version__
from earth_modes.data import load_bundle, default_scene, make_project, save_project
from earth_modes.analysis import compare_bundles, select_pair


def test_model_solve_inspect_scene_export_probe_compare(tmp_path, capsys):
    model, bundle, scene = [tmp_path / name for name in ("model.json", "modes.json", "scene.json")]
    assert main(["model", "homogeneous", "--out", str(model)]) == 0
    config = tmp_path / "solve.json"
    config.write_text(
        json.dumps(
            dict(
                families=["T"],
                l_min=2,
                l_max=2,
                mesh_size=12,
                gravity=0,
                frequency_min_hz=0.00001,
                frequency_max_hz=0.001,
            )
        )
    )
    assert (
        main(
            [
                "solve",
                str(model),
                "--config",
                str(config),
                "--mesh",
                "16",
                "--f-max-mhz",
                "2",
                "--out",
                str(bundle),
            ]
        )
        == 0
    )
    data = load_bundle(bundle)
    assert data["modes"] and data["provenance"]["request"]["mesh_size"] == 16
    assert data["provenance"]["request"]["frequency_max_hz"] == 0.002
    assert main(["inspect", str(bundle), "--json"]) == 0
    output = capsys.readouterr().out
    assert "quality" in output and "frequency_hz" in output
    assert main(["scene", str(bundle), "--out", str(scene)]) == 0
    assert (
        main(
            [
                "export",
                str(bundle),
                str(scene),
                "--kind",
                "eigenfunctions",
                "--out",
                str(tmp_path / "mode.svg"),
            ]
        )
        == 0
    )
    assert "<svg" in (tmp_path / "mode.svg").read_text()
    probe = tmp_path / "probe.csv"
    assert (
        main(
            [
                "probe",
                str(bundle),
                str(scene),
                "--lat",
                "35",
                "--lon",
                "105",
                "--start",
                "1.3",
                "--duration",
                "1",
                "--step",
                ".3",
                "--raw",
                "--derivative",
                "1",
                "--out",
                str(probe),
            ]
        )
        == 0
    )
    lines = [line for line in probe.read_text().splitlines() if not line.startswith("#")]
    samples = list(csv.DictReader(lines))
    assert len(samples) == 4
    metadata = json.loads(Path(str(probe) + ".json").read_text())
    assert metadata["probe"]["normalized"] is False and metadata["probe"]["start_s"] == 1.3
    result = tmp_path / "comparison.svg"
    mode = data["modes"][0]
    assert (
        main(
            [
                "compare",
                str(bundle),
                str(bundle),
                "--family",
                "T",
                "--l",
                "2",
                "--n",
                str(mode["n"]),
                "--out",
                str(result),
            ]
        )
        == 0
    )
    comparison_metadata = json.loads(Path(str(result) + ".json").read_text())
    assert comparison_metadata["rows"][0]["delta_frequency_hz"] == 0
    assert comparison_metadata["generator_version"] == __version__
    project = make_project(
        data,
        default_scene(data),
        probe=metadata["probe"],
        export={"format": "png", "width": 128, "height": 128},
    )
    project_file = tmp_path / "project.json"
    save_project(project, project_file)
    assert main(["export", str(project_file), "--out", str(tmp_path / "image.png")]) == 0
    assert main(["probe", str(project_file), "--out", str(tmp_path / "saved-probe.csv")]) == 0
    original = bundle.read_bytes()
    assert main(["solve", str(model), "--config", str(config), "--out", str(bundle)]) == 2
    assert bundle.read_bytes() == original


def test_cli_errors_and_help(tmp_path, capsys):
    path = tmp_path / "model.json"
    assert main(["model", "homogeneous", "--vs", "0", "--out", str(path)]) == 0
    assert json.loads(path.read_text())["layers"][0]["phase"] == "fluid"
    assert main(["model", "homogeneous", "--rho", "-1", "--out", str(tmp_path / "bad.json")]) == 2
    assert not (tmp_path / "bad.json").exists()
    assert main(["model", "prem", "--vs", "0", "--out", str(path), "--overwrite"]) == 2
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text('{"families":["T"],"families":["S"]}')
    assert (
        main(
            ["solve", str(path), "--config", str(duplicate), "--out", str(tmp_path / "result.json")]
        )
        == 2
    )
    assert "duplicate JSON key" in capsys.readouterr().err
    for command in ("model", "solve", "inspect", "scene", "export", "probe", "compare"):
        result = subprocess.run(
            [sys.executable, "-m", "earth_modes.cli", command, "--help"],
            env={**__import__("os").environ, "PYTHONPATH": "packages"},
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0 and "usage:" in result.stdout
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "earth_modes.cli",
            "solve",
            str(path),
            "--mesh",
            "no",
            "--out",
            str(path),
        ],
        env={**__import__("os").environ, "PYTHONPATH": "packages"},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2 and "invalid int" in result.stderr


def test_installed_example_and_scientific_image_precedence(tmp_path, capsys):
    from PIL import Image
    project = tmp_path / "project.json"
    assert main(["example", "--list"]) == 0
    assert "03-indices" in capsys.readouterr().out
    assert main(["example", "03-indices", "--out", str(project)]) == 0
    value = json.loads(project.read_text())
    assert value["scene"]["schema_version"] == "1.1"
    value["export"] = {"format": "gif"}
    project.write_text(json.dumps(value))
    inherited = tmp_path / "inherited.png"
    assert main(["export", str(project), "--kind", "eigenfunctions", "--out", str(inherited)]) == 0
    with Image.open(inherited) as image:
        assert image.size == (1200, 900)
    explicit = tmp_path / "explicit.png"
    assert main(["probe", str(project), "--width", "640", "--height", "480", "--no-annotation", "--transparent", "--out", str(explicit)]) == 0
    with Image.open(explicit) as image:
        assert image.size == (640, 480)
    meta = json.loads(Path(str(explicit)+".json").read_text())
    assert meta["production"]["annotation"] is False and meta["annotation_language"] == "en"
    csv_path = tmp_path / "probe.csv"
    assert main(["probe", str(project), "--out", str(csv_path)]) == 0
    previous = csv_path.read_bytes()
    assert main(["probe", str(project), "--width", "640", "--out", str(csv_path), "--overwrite"]) == 2
    assert csv_path.read_bytes() == previous


def test_explicit_comparison_preserves_both_domains_and_independent_radii():
    a = load_bundle("examples/prem-modes.json")
    mode = next(m for m in a["modes"] if m["family"] == "T")
    b = copy.deepcopy(a)
    other = next(m for m in b["modes"] if m["id"] == mode["id"])
    other["frequency_hz"] *= 1.001
    # A synthetic frequency edit cannot retain the original benchmark evidence.
    other["provenance"]["quality"] = dict(status="unverified", mesh_convergence=None,
                                            benchmark=None, warnings=["Synthetic comparison fixture."])
    result = compare_bundles(a, b, [(mode["id"], other["id"])])
    assert result["rows"][0]["relative_frequency_change"] == pytest.approx(0.001)
    assert (
        result["curves"][0]["regions"][0]["radius_fraction"][0]
        == mode["regions"][0]["r_m"][0] / a["model"]["radius_m"]
    )
    other["provenance"]["solid_domain_id"] = "another-domain"
    explicit = compare_bundles(a, b, [(mode["id"], other["id"])])
    assert explicit["rows"][0]["candidate_solid_domain_id"] == "another-domain"
    assert explicit["rows"][0]["reference_solid_domain_id"] != "another-domain"
    a["modes"], b["modes"] = [mode], [other]
    with pytest.raises(ValueError, match="Expected one matching"):
        select_pair(a, b, mode["family"], mode["l"], mode["n"])


def test_probe_half_open_window_uses_actual_absolute_float_times(tmp_path):
    bundle = load_bundle("examples/prem-modes.json")
    project = tmp_path / "project.json"
    save_project(make_project(bundle, default_scene(bundle)), project)
    output = tmp_path / "probe.csv"
    assert main(["probe", str(project), "--lat", "0", "--lon", "0", "--start", "1000",
                 "--duration", "0.3000000000000001", "--step", "0.1", "--out", str(output)]) == 0
    timestamps = [float(row[0]) for row in list(csv.reader(output.open()))[1:]]
    assert timestamps == [1000.0, 1000.1, 1000.2]
    assert all(t < 1000 + .3000000000000001 for t in timestamps)
    assert json.loads(Path(str(output) + ".json").read_text())["probe"]["sample_count"] == 3
    bad = tmp_path / "bad.csv"
    assert main(["probe", str(project), "--lat", "0", "--lon", "0", "--start", "1e16",
                 "--duration", "1", "--step", "0.1", "--out", str(bad)]) == 2
    assert not bad.exists()


def test_cli_fast_glb_uses_adaptive_keys_but_video_rejects_aliasing(tmp_path):
    bundle = load_bundle("examples/prem-modes.json")
    bundle["modes"] = [next(m for m in bundle["modes"] if m["id"] == "R0_0")]
    scene = default_scene(bundle)
    scene.update(time_scale=10000.0, quality="draft")
    project = tmp_path / "fast.json"
    save_project(make_project(bundle, scene), project)
    assert (
        main(
            [
                "export",
                str(project),
                "--out",
                str(tmp_path / "fast.glb"),
                "--duration",
                "1",
                "--fps",
                "4",
            ]
        )
        == 0
    )
    metadata = json.loads((tmp_path / "fast.glb.json").read_text())
    assert (tmp_path / "fast.glb").read_bytes()[:4] == b"glTF"
    assert metadata["scene"]["time_scale"] == 10000.0
    assert (
        main(
            [
                "export",
                str(project),
                "--out",
                str(tmp_path / "aliased.mp4"),
                "--duration",
                "1",
                "--fps",
                "4",
            ]
        )
        == 2
    )
    assert not (tmp_path / "aliased.mp4").exists()


def test_glb_cli_budget_applies_saved_explicit_omissions(tmp_path):
    from test_fields import field_bundle
    from earth_modes.export_render import geometry
    from earth_modes.export import ExportLimits
    bundle = field_bundle()
    mode = bundle["modes"][-1]
    mode["l"] = 40
    bundle["modes"] = [mode]
    scene = default_scene(bundle)
    scene.update(surface="wireframe", wireframe_spacing_deg=30, nodes=True, quality="draft")
    with pytest.raises(ValueError, match="budget"):
        geometry(bundle, scene, ExportLimits(), preflight_only=True)
    project = make_project(bundle, scene, export={"format": "glb", "duration_s": .1,
                                                "omit_analysis_overlays": True})
    path = tmp_path / "omitted.json"
    save_project(project, path)
    output = tmp_path / "omitted.glb"
    assert main(["export", str(path), "--out", str(output)]) == 0
    manifest = json.loads(Path(str(output) + ".json").read_text())
    assert manifest["scene"]["nodes"] is True
    assert manifest["omitted"] == ["analysis_overlays"]
    assert manifest["resources"]["point_count"] < 250000
    assert json.loads(path.read_text())["scene"]["nodes"] is True
