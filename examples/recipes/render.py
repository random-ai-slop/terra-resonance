"""Generate a portable project and verified local outputs from the bundled PREM modes."""

from __future__ import annotations

import argparse
from pathlib import Path
import json
import shutil
import subprocess
import struct

from PIL import Image
import numpy as np

from earth_modes.data import (
    load_bundle,
    default_scene,
    make_project,
    save_project,
    bundle_hash,
    _write_json,
)
from earth_modes.export import (
    export_image,
    export_plot,
    export_probe,
    export_tables,
    export_video,
    export_glb,
)
from earth_modes.fields import evaluate_field

ROOT = Path(__file__).resolve().parents[2]


def read_glb(path, bundle, scene):
    """Independent byte readback, including non-keyframe linear morph weights."""
    raw = path.read_bytes()
    magic, version, length = struct.unpack_from("<4sII", raw)
    if (magic, version, length) != (b"glTF", 2, len(raw)):
        raise ValueError("Invalid GLB header")
    count, kind = struct.unpack_from("<I4s", raw, 12)
    if kind != b"JSON":
        raise ValueError("Missing JSON chunk")
    document = json.loads(raw[20 : 20 + count])
    offset = 20 + count
    binary_count, kind = struct.unpack_from("<I4s", raw, offset)
    if kind != b"BIN\0":
        raise ValueError("Missing BIN chunk")
    binary = raw[offset + 8 : offset + 8 + binary_count]

    def array(index):
        accessor = document["accessors"][index]
        view = document["bufferViews"][accessor["bufferView"]]
        width = {"SCALAR": 1, "VEC3": 3, "VEC4": 4}[accessor["type"]]
        start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
        if start + accessor["count"] * width * 4 > len(binary):
            raise ValueError("Accessor exceeds binary buffer")
        return np.frombuffer(
            binary,
            dtype={5126: "<f4", 5125: "<u4"}[accessor["componentType"]],
            count=accessor["count"] * width,
            offset=start,
        ).reshape(-1, width)

    for index in range(len(document["accessors"])):
        array(index)
    primitive = document["meshes"][0]["primitives"][0]
    base = array(primitive["attributes"]["POSITION"])
    targets = np.stack([array(target["POSITION"]) for target in primitive["targets"]])
    sampler = document["animations"][0]["samplers"][0]
    keys = array(sampler["input"]).ravel()
    weights = array(sampler["output"]).reshape(len(keys), len(targets))
    # This recipe uses a surface shell. Restore the mathematical radius after
    # serialized float32 roundoff; the scientific field keeps its strict boundary.
    material = base.astype(float)
    points = material / np.linalg.norm(material, axis=1)[:, None] * scene["radius_fraction"]
    errors = []
    for fraction in (0.137, 0.413, 0.819):
        t = float(keys[-1]) * fraction
        upper = np.searchsorted(keys, t)
        alpha = (t - keys[upper - 1]) / (keys[upper] - keys[upper - 1])
        w = weights[upper - 1] * (1 - alpha) + weights[upper] * alpha
        actual = np.einsum("t,tnc->nc", w, targets)
        expected = scene["deformation"] * evaluate_field(
            bundle,
            scene["terms"],
            points * bundle["model"]["radius_m"],
            scene["time_s"] + t * scene["time_scale"],
        )
        bound = scene["deformation"] * sum(
            abs(term["amplitude"])
            * np.sqrt(
                3
                * (
                    2 * next(mode["l"] for mode in bundle["modes"] if mode["id"] == term["mode_id"])
                    + 1
                )
                / (4 * np.pi)
            )
            for term in scene["terms"]
        )
        error = float(np.max(np.linalg.norm(actual - expected, axis=1)) / bound)
        if error > 0.01:
            raise ValueError(f"Off-key GLB morph error exceeds 1%: {error}")
        errors.append(dict(playback_s=t, error_fraction_fixed_bound=error))
    return dict(
        bytes=len(raw),
        vertex_count=len(base),
        target_count=len(targets),
        key_count=len(keys),
        non_keyframe_checks=errors,
    )


def render(output, media=False, duration=8.0, overwrite=False):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    bundle = load_bundle(ROOT / "examples/prem-modes.json")
    scene = default_scene(bundle)
    scene.update(quality="draft", geography=True, arrows=True, nodes=True)
    scene["point"] = dict(latitude_deg=32.0, longitude_deg=-48.0, radius_fraction=1.0)
    scene["trajectory"]["enabled"] = True
    probe = dict(
        latitude_deg=32.0,
        longitude_deg=-48.0,
        radius_fraction=1.0,
        start_s=0.0,
        step_s=10.0,
        sample_count=360,
        derivative=0,
        normalized=True,
    )
    save_project(
        make_project(
            bundle, scene, probe=probe, export={"format": "png", "width": 640, "height": 480}
        ),
        output / "project.json",
        overwrite=overwrite,
    )
    export_image(bundle, scene, output / "earth.png", 640, 480, overwrite=overwrite)
    with Image.open(output / "earth.png") as image:
        image.verify()
    export_plot(
        bundle,
        output / "eigenfunctions.svg",
        mode_id=scene["terms"][0]["mode_id"],
        overwrite=overwrite,
    )
    export_plot(bundle, output / "model.svg", kind="model", overwrite=overwrite)
    export_probe(bundle, scene, probe, output / "probe.csv", overwrite=overwrite)
    export_probe(bundle, scene, probe, output / "probe.svg", overwrite=overwrite)
    export_tables(bundle, output / "tables", overwrite=overwrite)
    report = dict(
        bundle_hash=bundle_hash(bundle),
        mode_id=scene["terms"][0]["mode_id"],
        static_outputs=[
            "earth.png",
            "eigenfunctions.svg",
            "model.svg",
            "probe.csv",
            "probe.svg",
            "tables",
        ],
        media_duration_s=duration if media else None,
        blender_native="not run by this recipe",
    )
    if media:
        for suffix in ("gif", "mp4"):
            export_video(
                bundle,
                scene,
                output / ("earth." + suffix),
                duration_s=duration,
                width=640,
                height=480,
                overwrite=overwrite,
            )
        with Image.open(output / "earth.gif") as image:
            report["gif"] = dict(
                frame_count=image.n_frames, size=list(image.size), frame_delays_ms=[]
            )
            for index in range(image.n_frames):
                image.seek(index)
                report["gif"]["frame_delays_ms"].append(image.info["duration"])
        report["mp4"] = json.loads(
            subprocess.check_output(
                [
                    shutil.which("ffprobe") or "ffprobe",
                    "-v",
                    "error",
                    "-select_streams",
                    "v:0",
                    "-show_entries",
                    "stream=codec_name,width,height,r_frame_rate,nb_frames,duration",
                    "-of",
                    "json",
                    str(output / "earth.mp4"),
                ],
                text=True,
            )
        )
        export_glb(
            bundle,
            scene,
            output / "earth.glb",
            duration_s=duration,
            fps=24,
            width=640,
            height=480,
            omit_arrows=True,
            omit_geography=True,
            omit_analysis_overlays=True,
            overwrite=overwrite,
        )
        report["glb"] = read_glb(output / "earth.glb", bundle, scene)
    _write_json(report, output / "verification.json", overwrite=overwrite)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument(
        "--media",
        action="store_true",
        help="Also render GIF, MP4 and morph GLB; requires ffmpeg and ffprobe.",
    )
    parser.add_argument("--duration", type=float, default=8.0)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    print(json.dumps(render(args.out, args.media, args.duration, args.overwrite), indent=2))
