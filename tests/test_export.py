"""Independent artifact readback: timing, native vectors and morph reconstruction."""

import json
from pathlib import Path
import shutil
import struct
import numpy as np
import pytest
from PIL import Image
from earth_modes.data import default_scene, mass_integral, validate_bundle
from earth_modes.fields import evaluate_field
from earth_modes.export import (
    export_image,
    export_frames,
    export_video,
    export_plot,
    export_tables,
    export_glb,
    export_probe,
    export_artifact,
    ExportLimits,
)
from earth_modes.export_render import geometry
from earth_modes.export_overlays import build_overlays
from earth_modes.export_common import transaction, times


@pytest.fixture
def setup_scene():
    model = {
        "id": "manufactured",
        "name": "Manufactured export fixture",
        "radius_m": 1000.0,
        "layers": [
            {
                "id": "solid",
                "name": "solid",
                "phase": "solid",
                "r_m": [0.0, 500.0, 1000.0],
                "rho_kg_m3": [5000.0] * 3,
                "vp_m_s": [10000.0] * 3,
                "vs_m_s": [5000.0] * 3,
            }
        ],
    }
    mode = {
        "id": "0S2",
        "family": "S",
        "n": 0,
        "l": 2,
        "frequency_hz": 0.25,
        "q": 20.0,
        "normalization": "mass_integral_1",
        "provenance": {
            "quality": {
                "status": "unverified",
                "mesh_convergence": None,
                "benchmark": None,
                "warnings": ["Manufactured test, not a solved Earth mode."],
            }
        },
        "regions": [
            {
                "layer_id": "solid",
                "r_m": [0.0, 500.0, 1000.0],
                "u": [0.0, 0.5, 1.0],
                "v": [0.0, 0.15, 0.3],
                "w": [0.0, 0.0, 0.0],
            }
        ],
    }
    norm = np.sqrt(mass_integral(model, mode))
    for key in ("u", "v", "w"):
        mode["regions"][0][key] = (np.asarray(mode["regions"][0][key]) / norm).tolist()
    bundle = {
        "schema_version": "1.0",
        "model": model,
        "modes": [mode],
        "provenance": {"source": "manufactured unit fixture"},
    }
    validate_bundle(bundle)
    scene = default_scene(bundle)
    scene.update(quality="draft", time_s=0.37, time_scale=0.5, deformation=0.12)
    return bundle, scene


def decode_glb(path):
    raw = Path(path).read_bytes()
    magic, version, total = struct.unpack_from("<4sII", raw)
    assert (magic, version, total) == (b"glTF", 2, len(raw))
    length, kind = struct.unpack_from("<I4s", raw, 12)
    assert kind == b"JSON"
    doc = json.loads(raw[20 : 20 + length])
    offset = 20 + length
    length, kind = struct.unpack_from("<I4s", raw, offset)
    assert kind == b"BIN\0"
    binary = raw[offset + 8 : offset + 8 + length]

    def array(index):
        a = doc["accessors"][index]
        view = doc["bufferViews"][a["bufferView"]]
        dtype = {5126: "<f4", 5125: "<u4"}[a["componentType"]]
        width = {"SCALAR": 1, "VEC3": 3, "VEC4": 4}[a["type"]]
        start = view.get("byteOffset", 0) + a.get("byteOffset", 0)
        assert start + a["count"] * width * 4 <= len(binary)
        return np.frombuffer(binary, dtype=dtype, count=a["count"] * width, offset=start).reshape(
            a["count"], width
        )

    for index in range(len(doc["accessors"])):
        array(index)
    return doc, array


def test_static_plots_and_tables(tmp_path, setup_scene):
    bundle, scene = setup_scene
    scene.update(cutaway=True, arrows=True, geography=True, nodes=True)
    scene["point"] = {"latitude_deg": 30.0, "longitude_deg": -30.0, "radius_fraction": 1.0}
    scene["trajectory"] = {"enabled": True, "start_s": 0.0, "duration_s": 4.0, "samples": 128}
    output = export_image(bundle, scene, tmp_path / "field.png", 640, 480, transparent=True)
    with Image.open(output) as im:
        assert im.size == (640, 480)
        assert im.mode == "RGBA" and im.getextrema()[3][0] == 0
        assert np.asarray(im)[:, :, :3].std() > 10
    meta = json.loads(Path(str(output) + ".json").read_text())
    assert meta["scene"] == scene and meta["bundle_hash"] == scene["bundle_hash"]
    for kind in ("eigenfunctions", "model", "frequencies"):
        p = export_plot(bundle, tmp_path / f"{kind}.svg", kind=kind)
        raw = p.read_text()
        assert "<path" in raw and "<image" not in raw
    bundle["model"]["layers"][0].update(q_bulk=[300.0] * 3, q_shear=[200.0] * 3)
    bundle["model"]["reference_frequency_hz"] = 0.01
    tables = export_tables(bundle, tmp_path / "tables")
    import csv

    with tables[0].open() as stream:
        rows = list(csv.DictReader(stream))
    assert float(rows[0]["frequency_hz"]) == bundle["modes"][0]["frequency_hz"]
    with (tmp_path / "tables" / "model.csv").open() as stream:
        materials = list(csv.DictReader(stream))
    assert float(materials[0]["q_bulk"]) == 300 and float(materials[0]["q_shear"]) == 200
    table_meta = json.loads((tmp_path / "tables.json").read_text())
    assert table_meta["model_reference_frequency_hz"] == 0.01
    # Restore the scene-bound input before testing overwrite protection.
    bundle["model"]["layers"][0].pop("q_bulk")
    bundle["model"]["layers"][0].pop("q_shear")
    bundle["model"].pop("reference_frequency_hz")
    with pytest.raises(FileExistsError):
        export_image(bundle, scene, output, 640, 480)


def test_nodes_match_analytic_y20_and_preserve_field(tmp_path, setup_scene):
    bundle, scene = setup_scene
    scene.update(nodes=True, cutaway=False)
    geo = geometry(bundle, scene, ExportLimits())
    overlay = build_overlays(bundle, scene, geo)
    assert len(overlay.node_points) > 20
    points = overlay.node_points.reshape(-1, 3)
    # Y20 zeros occur at z/r=+-1/sqrt(3), independent of phase and frequency.
    np.testing.assert_allclose(
        np.abs(points[:, 2] / np.linalg.norm(points, axis=1)), 1 / np.sqrt(3), atol=0.003
    )
    scene2 = {**scene, "time_s": scene["time_s"] + 1}
    overlay2 = build_overlays(bundle, scene2, geo)
    np.testing.assert_array_equal(overlay.node_points, overlay2.node_points)


def test_glb_non_keyframe_reconstruction(tmp_path, setup_scene):
    bundle, scene = setup_scene
    scene["terms"][0]["phase_rad"] = 0.43
    output = export_glb(bundle, scene, tmp_path / "mode.glb", duration_s=1, fps=4)
    doc, array = decode_glb(output)
    mesh = doc["meshes"][0]
    p = mesh["primitives"][0]
    base = array(p["attributes"]["POSITION"])
    ids = array(p["indices"]).ravel()
    assert ids.max() < len(base)
    targets = np.array([array(t["POSITION"]) for t in p["targets"]])
    sampler = doc["animations"][0]["samplers"][0]
    keys = array(sampler["input"]).ravel()
    weights = array(sampler["output"]).reshape(len(keys), len(targets))
    for t in (0.137, 0.413, 0.819):
        w = np.array([np.interp(t, keys, weights[:, j]) for j in range(len(targets))])
        actual = np.einsum("t,tnc->nc", w, targets)
        # GLB uses float32 coordinates. Restore the declared material shell radius
        # before physical sampling; rounding must not turn surface points into outside points.
        material = (
            base.astype(float)
            / np.linalg.norm(base.astype(float), axis=1)[:, None]
            * scene["radius_fraction"]
        )
        truth = scene["deformation"] * evaluate_field(
            bundle,
            scene["terms"],
            material * bundle["model"]["radius_m"],
            scene["time_s"] + t * scene["time_scale"],
        )
        assert (
            np.max(np.linalg.norm(actual - truth, axis=1))
            < 0.01 * scene["deformation"] * scene["color_limit"]
        )
    assert np.ptp(weights[:, 0]) > 0 and "cameras" in doc
    assert doc["nodes"][0]["rotation"][0] < 0  # explicit canonical z-up -> glTF y-up


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="FFmpeg is an optional executable")
def test_video_frame_timing_and_default_gif(tmp_path, setup_scene):
    bundle, scene = setup_scene
    gif = export_video(
        bundle,
        scene,
        tmp_path / "movie.gif",
        duration_s=0.2,
        width=320,
        height=240,
        annotation=False,
    )
    with Image.open(gif) as im:
        assert im.n_frames == 4
        assert im.info["duration"] == 50
    mp4 = export_video(
        bundle,
        scene,
        tmp_path / "movie.mp4",
        duration_s=0.25,
        width=320,
        height=240,
        annotation=False,
    )
    import subprocess

    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-count_frames",
            "-show_entries",
            "stream=nb_read_frames,width,height",
            "-of",
            "json",
            str(mp4),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    stream = json.loads(result.stdout)["streams"][0]
    assert stream["nb_read_frames"] == "6" and stream["width"] == 320
    directory = export_frames(
        bundle,
        scene,
        tmp_path / "frames",
        duration_s=0.125,
        fps=20,
        width=320,
        height=240,
        annotation=False,
    )
    assert (
        len(list(directory.glob("frame_*.png"))) == 3
    )  # floor(2.5+.5), not Python bankers rounding
    first = np.asarray(Image.open(directory / "frame_000000.png"))
    last = np.asarray(Image.open(directory / "frame_000002.png"))
    assert np.any(first != last)
    meta = json.loads(Path(str(directory) + ".json").read_text())
    np.testing.assert_allclose(
        meta["physical_times_s"], scene["time_s"] + np.arange(3) * scene["time_scale"] / 20
    )


def test_probe_raw_units_and_transparency(tmp_path, setup_scene):
    bundle, scene = setup_scene
    probe = {
        "latitude_deg": 35.0,
        "longitude_deg": 105.0,
        "radius_fraction": 1.0,
        "start_s": 0.3,
        "step_s": 0.2,
        "sample_count": 10,
        "derivative": 1,
        "normalized": False,
    }
    path = export_probe(bundle, scene, probe, tmp_path / "probe.csv")
    values = np.loadtxt(path, delimiter=",", skiprows=1)
    expected = np.array(
        [
            evaluate_field(
                bundle,
                scene["terms"],
                np.array(
                    [
                        [
                            np.cos(np.deg2rad(35)) * np.cos(np.deg2rad(105)),
                            np.cos(np.deg2rad(35)) * np.sin(np.deg2rad(105)),
                            np.sin(np.deg2rad(35)),
                        ]
                    ]
                )
                * 1000,
                t,
                derivative=1,
                normalized=False,
            )[0]
            for t in values[:, 0]
        ]
    )
    np.testing.assert_allclose(values[:, 1:], expected, rtol=1e-12, atol=1e-20)
    assert "kg^(-1/2) s^-1" in path.read_text().splitlines()[0]
    export_probe(bundle, scene, probe, tmp_path / "probe.svg")


def test_preflight_rejection_and_rollback(tmp_path, setup_scene, monkeypatch):
    bundle, scene = setup_scene
    with pytest.raises(ValueError, match="GIF fps"):
        export_video(bundle, scene, tmp_path / "bad.gif", fps=24)
    with pytest.raises(ValueError, match="budget"):
        export_image(bundle, scene, tmp_path / "bad.png", limits=ExportLimits(max_points=5))
    assert not (tmp_path / "bad.png").exists()
    aliased = {**scene, "time_scale": 100.0}
    with pytest.raises(ValueError, match="aliasing"):
        times(bundle, aliased, 1, 20, ExportLimits())
    scene = {**scene, "arrows": True}
    with pytest.raises(ValueError, match="omit_arrows"):
        export_glb(bundle, scene, tmp_path / "bad.glb")
    target = tmp_path / "keep.txt"
    sidecar = tmp_path / "keep.txt.json"
    target.write_text("old")
    sidecar.write_text("{}")
    import earth_modes.export_common as common

    original = common.os.replace

    def fail(source, dest):
        if Path(source).name == "keep.txt.json" and str(source) != str(sidecar):
            raise OSError("simulated commit failure")
        return original(source, dest)

    monkeypatch.setattr(common.os, "replace", fail)
    with pytest.raises(OSError):
        with transaction(target, overwrite=True) as (staged, info):
            staged.write_text("new")
            info.update(ok=True)
    assert target.read_text() == "old" and sidecar.read_text() == "{}"


@pytest.mark.parametrize("directory", [False, True])
def test_no_overwrite_commit_preserves_a_concurrent_winner(tmp_path, directory):
    target = tmp_path / ("frames" if directory else "image.png")
    sidecar = Path(str(target) + ".json")
    with pytest.raises(FileExistsError):
        with transaction(target, overwrite=False, directory=directory) as (staged, info):
            (staged / "our.png" if directory else staged).write_bytes(b"our result")
            info["source"] = "ours"
            if directory:
                target.mkdir()  # Even an empty winning directory is protected.
            else:
                target.write_bytes(b"winning result")
            sidecar.write_text('{"source":"winner"}')
    assert json.loads(sidecar.read_text())["source"] == "winner"
    assert list(target.iterdir()) == [] if directory else target.read_bytes() == b"winning result"


def test_failed_sidecar_publication_removes_only_its_owned_artifact(tmp_path, monkeypatch):
    import earth_modes.export_common as common
    target, sidecar = tmp_path / "image.png", tmp_path / "image.png.json"
    original = common.os.link
    def race(source, destination):
        if Path(destination) == sidecar:
            replacement = tmp_path / "winner.png"
            replacement.write_bytes(b"replacement belongs to another producer")
            common.os.replace(replacement, target)
            sidecar.write_text('{"source":"winner"}')
        return original(source, destination)
    monkeypatch.setattr(common.os, "link", race)
    with pytest.raises(FileExistsError):
        with transaction(target) as (staged, info):
            staged.write_bytes(b"ours")
            info["source"] = "ours"
    assert target.read_bytes() == b"replacement belongs to another producer"
    assert json.loads(sidecar.read_text())["source"] == "winner"


@pytest.mark.parametrize("directory", [False, True])
def test_sidecar_collision_rolls_back_only_the_new_artifact(tmp_path, directory):
    target = tmp_path / "output"
    sidecar = Path(str(target) + ".json")
    with pytest.raises(FileExistsError):
        with transaction(target, directory=directory) as (staged, info):
            (staged / "frame.png" if directory else staged).write_bytes(b"ours")
            info["source"] = "ours"
            sidecar.write_text('{"source":"other producer"}')
    assert not target.exists()
    assert json.loads(sidecar.read_text())["source"] == "other producer"


def test_scientific_production_metadata_matches_pixels_and_format(tmp_path, setup_scene):
    bundle, scene = setup_scene
    probe = dict(latitude_deg=20, longitude_deg=30, start_s=0, step_s=1, sample_count=4)
    for name, output in [("plot", lambda p: export_plot(bundle, p, transparent=True, annotation=False)),
                         ("probe", lambda p: export_probe(bundle, scene, probe, p, width=640, height=400, transparent=True, annotation=False))]:
        path = tmp_path / (name + ".png")
        output(path)
        spec = json.loads(Path(str(path) + ".json").read_text())["export_spec"]
        with Image.open(path) as image:
            assert image.size == (spec["width"], spec["height"])
            assert image.getchannel("A").getextrema()[0] == 0
        assert spec["transparent"] is True and spec["annotation"] is False
    with pytest.raises(ValueError, match="requires output suffix"):
        export_artifact(bundle, scene, tmp_path / "wrong.mp4", {"format": "gif"})
    assert not (tmp_path / "wrong.mp4").exists()


def test_cutaway_retains_high_radial_knots_and_rechecks_budget(setup_scene):
    bundle, _ = setup_scene
    mode = bundle["modes"][0]
    mode.update(family="R", l=0)
    region = mode["regions"][0]
    radius = np.linspace(0, 1000, 241)
    wave = np.sin(24 * np.pi * radius / 1000)
    wave[[0, -1]] = 0
    region.update(
        r_m=radius.tolist(), u=wave.tolist(), v=np.zeros(241).tolist(), w=np.zeros(241).tolist()
    )
    region["u"] = (wave / np.sqrt(mass_integral(bundle["model"], mode))).tolist()
    scene = default_scene(bundle)
    scene.update(quality="draft", cutaway=True, nodes=True, geography=False, arrows=False)
    geo = geometry(bundle, scene, ExportLimits())
    start, stop, _ = geo.sides[1]
    rendered_radii = np.unique(np.linalg.norm(geo.points[start:stop], axis=1))
    assert all(np.min(abs(rendered_radii - r / 1000)) < 1e-14 for r in radius)
    assert np.max(abs(geo.bases[:, start:stop])) > 0.2
    overlay = build_overlays(bundle, scene, geo)
    assert len(overlay.node_points) > 100 and "solid:" not in overlay.node_note
    with pytest.raises(ValueError, match="budget"):
        geometry(bundle, scene, ExportLimits(max_points=10000), preflight_only=True)
