"""Minimal standards-based glTF 2.0 writer for editable modal morph animation."""

from pathlib import Path
import json
import math
import struct
import warnings
import numpy as np
from .export_common import ExportLimits, prepare, transaction, manifest, times, default_bound, size
from .export_render import geometry, scalar, rgba, camera_basis


class _GLB:
    def __init__(self):
        self.binary = bytearray()
        self.doc = {
            "asset": {"version": "2.0", "generator": "Terra Resonance"},
            "scene": 0,
            "scenes": [{"nodes": [0]}],
            "nodes": [],
            "meshes": [],
            "bufferViews": [],
            "accessors": [],
            "materials": [
                {
                    "name": "Scientific static color",
                    "doubleSided": True,
                    "pbrMetallicRoughness": {"metallicFactor": 0, "roughnessFactor": 0.9},
                }
            ],
        }

    def accessor(self, values, kind, component=5126, target=None):
        a = np.asarray(values, dtype="<f4" if component == 5126 else "<u4")
        while len(self.binary) % 4:
            self.binary.append(0)
        offset = len(self.binary)
        self.binary.extend(a.tobytes())
        view = {"buffer": 0, "byteOffset": offset, "byteLength": a.nbytes}
        if target is not None:
            view["target"] = target
        self.doc["bufferViews"].append(view)
        width = {"SCALAR": 1, "VEC3": 3, "VEC4": 4}[kind]
        item = {
            "bufferView": len(self.doc["bufferViews"]) - 1,
            "componentType": component,
            "count": a.size // width,
            "type": kind,
        }
        if a.size:
            item.update(
                min=a.reshape(-1, width).min(axis=0).tolist(),
                max=a.reshape(-1, width).max(axis=0).tolist(),
            )
        self.doc["accessors"].append(item)
        return len(self.doc["accessors"]) - 1

    def save(self, path):
        self.doc["buffers"] = [{"byteLength": len(self.binary)}]
        raw = json.dumps(self.doc, separators=(",", ":"), allow_nan=False).encode()
        raw += b" " * ((-len(raw)) % 4)
        self.binary.extend(b"\0" * ((-len(self.binary)) % 4))
        with Path(path).open("wb") as stream:
            stream.write(struct.pack("<4sII", b"glTF", 2, 28 + len(raw) + len(self.binary)))
            stream.write(struct.pack("<I4s", len(raw), b"JSON"))
            stream.write(raw)
            stream.write(struct.pack("<I4s", len(self.binary), b"BIN\0"))
            stream.write(self.binary)


def _keyframes(geo, scene, duration, fps, limits, bound):
    fastest = max(
        (m["frequency_hz"] for m, t in zip(geo.modes, geo.terms) if t["amplitude"]), default=0
    )
    intervals = max(
        1, math.ceil(duration * fps), math.ceil(24 * duration * fastest * scene["time_scale"])
    )
    maxima = np.linalg.norm(geo.bases[:, : geo.animated_count], axis=2).max(axis=1)
    while True:
        if (intervals + 1) * 2 * len(geo.terms) > limits.max_key_weights:
            raise ValueError(
                "GLB interpolation cannot meet the 1% bound within the key-weight budget."
            )
        playback = np.linspace(0, duration, intervals + 1)
        coefficients = geo.coefficients(scene["time_s"] + playback * scene["time_scale"])
        # All interval midpoints and off-centre times, not just exact keyframes.
        maximum_error = 0.0
        for fraction in (0.5, 0.271828):
            probe = playback[:-1] + fraction * np.diff(playback)
            truth = geo.coefficients(scene["time_s"] + probe * scene["time_scale"])
            approx = (1 - fraction) * coefficients[:-1] + fraction * coefficients[1:]
            maximum_error = max(
                maximum_error, float((np.abs(truth - approx) @ maxima).max(initial=0))
            )
        if maximum_error <= 0.01 * bound:
            return playback, coefficients, maximum_error
        intervals *= 2


def effective_glb_scene(scene, *, omit_arrows=False, omit_geography=False,
                        omit_analysis_overlays=False):
    """Resolve explicit format omissions identically for CLI and writer preflight."""
    omitted = []
    for field, choice in (("arrows", omit_arrows), ("geography", omit_geography)):
        if scene[field]:
            if not choice:
                raise ValueError(
                    f"GLB cannot retain animated {field}; set omit_{field}=True explicitly."
                )
            omitted.append(field)
    if (
        scene.get("point") is not None
        or scene.get("nodes")
        or scene.get("trajectory", {}).get("enabled")
    ):
        if not omit_analysis_overlays:
            raise ValueError("GLB analysis overlays require explicit omit_analysis_overlays=True.")
        omitted.append("analysis_overlays")
    effective = {**scene, "arrows": False, "geography": False, "point": None, "nodes": False,
                 "trajectory": {**scene.get("trajectory", {}), "enabled": False}}
    return effective, omitted


def write_glb(
    bundle,
    scene,
    path,
    duration_s=8,
    fps=24,
    *,
    width=1200,
    height=900,
    omit_arrows=False,
    omit_geography=False,
    omit_analysis_overlays=False,
    transparent=False,
    annotation=True,
    overwrite=False,
    limits=None,
):
    limits = limits or ExportLimits()
    path = prepare(bundle, scene, path, (".glb",))
    size(width, height, limits)
    if transparent:
        raise ValueError("GLB transparency is viewer-controlled, not a transparent frame export.")
    if not scene["terms"]:
        raise ValueError("Animated GLB requires at least one mode term.")
    effective, omitted = effective_glb_scene(scene, omit_arrows=omit_arrows,
                                             omit_geography=omit_geography,
                                             omit_analysis_overlays=omit_analysis_overlays)
    warnings.warn(
        "GLB scientific colors are frozen at the export start; annotations remain in its manifest."
        + (f" Explicit omissions: {', '.join(omitted)}." if omitted else ""),
        UserWarning,
        stacklevel=2,
    )
    playback, _, _ = times(bundle, scene, duration_s, fps, limits, check_alias=False)
    duration = len(playback) / fps
    budget = geometry(bundle, effective, limits, preflight_only=True)
    morph_values = budget["animated_point_count"] * 2 * len(scene["terms"])
    estimate = 6 * 12 * morph_values + budget["spatial_cache_bytes"]
    if morph_values > limits.max_morph_values or estimate > limits.max_glb_bytes:
        raise ValueError(
            f"GLB resource budget exceeded: {morph_values} target vertices, {estimate} estimated bytes."
        )
    with transaction(path, overwrite) as (staged, info):
        geo = geometry(bundle, effective, limits)
        bound = default_bound(bundle, scene)
        keys, coefficients, error = _keyframes(geo, scene, duration, fps, limits, bound)
        glb = _GLB()
        d = glb.doc
        # File world uses glTF Y-up. Child coordinates retain scientific z-north.
        d["nodes"] = [
            {
                "name": "Scientific z-up to glTF y-up",
                "rotation": [-math.sqrt(0.5), 0, 0, math.sqrt(0.5)],
                "children": [1, 2],
            },
            {"mesh": 0, "name": bundle["model"]["name"]},
            {"camera": 0, "name": "Scene orthographic camera"},
        ]
        attributes = {"POSITION": glb.accessor(geo.points[: geo.animated_count], "VEC3", target=34962)}
        values = scalar(geo.points, geo.field(scene["time_s"]), scene["color"])
        colors = rgba(values[: geo.animated_count], scene)
        # glTF COLOR_0 is linear, whereas the shared presentation palette is sRGB.
        colors[:, :3] = np.where(
            colors[:, :3] <= 0.04045,
            colors[:, :3] / 12.92,
            ((colors[:, :3] + 0.055) / 1.055) ** 2.4,
        )
        attributes["COLOR_0"] = glb.accessor(colors, "VEC4", target=34962)
        targets = []
        groups = []
        if scene["surface"] == "wireframe":
            shell = np.all(geo.faces < geo.surface_count, axis=1)
            if scene.get("wireframe_spacing_deg") is not None:
                edges = geo.wire_edges
            else:
                f = geo.faces[shell]
                edges = np.unique(np.sort(np.concatenate((f[:, :2], f[:, 1:], f[:, [0, 2]])), axis=1), axis=0)
            groups = [(edges, 1), (geo.faces[~shell], 4)]
        else:
            groups = [(geo.faces, 4)]
        # Shared POSITION/COLOR/targets avoid duplicating the complete modal
        # buffers for filled sections and animated surface lines. One mesh has
        # one weight track, applied to both primitives by the glTF contract.
        primitives = [{"attributes": attributes,
                       "indices": glb.accessor(indices.ravel(), "SCALAR", 5125, 34963),
                       "mode": mode, "material": 0, "targets": targets}
                      for indices, mode in groups if len(indices)]
        target_names = []
        weights = []
        for index, term in enumerate(scene["terms"]):
            for sign in (1, -1):
                basis = sign * scene["deformation"] * geo.bases[index, : geo.animated_count]
                targets.append({"POSITION": glb.accessor(basis, "VEC3", target=34962)})
                weights.append(np.maximum(sign * coefficients[:, index], 0))
                target_names.append(
                    f"{term['mode_id']}_m{term['m']}_{'plus' if sign==1 else 'minus'}"
                )
        weight_array = np.asarray(weights).T
        d["meshes"].append(
            {
                "primitives": primitives,
                "weights": weight_array[0].tolist(),
                "extras": {"targetNames": target_names},
            }
        )
        d["animations"] = [
            {
                "name": "Physical modal displacement",
                "samplers": [
                    {
                        "input": glb.accessor(keys, "SCALAR"),
                        "output": glb.accessor(weight_array.ravel(), "SCALAR"),
                        "interpolation": "LINEAR",
                    }
                ],
                "channels": [{"sampler": 0, "target": {"node": 1, "path": "weights"}}],
            }
        ]
        cam = camera_basis(scene)
        matrix = np.eye(4)
        matrix[:3, :3] = cam
        matrix[:3, 3] = cam[:, 2] * 4
        d["nodes"][2]["matrix"] = matrix.T.ravel().tolist()
        d["cameras"] = [
            {
                "type": "orthographic",
                "orthographic": {
                    "xmag": scene["camera"]["distance"] * width / height / 2,
                    "ymag": scene["camera"]["distance"] / 2,
                    "znear": 0.01,
                    "zfar": 100,
                },
            }
        ]
        if scene["reference"]:
            p = np.linspace(0, 2 * np.pi, 97)
            c = np.column_stack((np.cos(p), np.sin(p), np.zeros_like(p))) * scene["radius_fraction"]
            ref = np.concatenate((c, c[:, [0, 2, 1]], c[:, [2, 0, 1]]))
            edges = np.array(
                [(j * len(p) + i, j * len(p) + i + 1) for j in range(3) for i in range(len(p) - 1)]
            )
            d["meshes"].append(
                {
                    "primitives": [
                        {
                            "attributes": {"POSITION": glb.accessor(ref, "VEC3", target=34962)},
                            "indices": glb.accessor(edges.ravel(), "SCALAR", 5125, 34963),
                            "mode": 1,
                        }
                    ]
                }
            )
            d["nodes"].append({"mesh": 1, "name": "Undeformed reference"})
            d["nodes"][0]["children"].append(3)
        details = manifest(
            bundle,
            scene,
            format="glb",
            width=width,
            height=height,
            aspect=width / height,
            requested_duration_s=duration_s,
            playback_duration_s=duration,
            playback_key_times_s=keys.tolist(),
            physical_key_times_s=(scene["time_s"] + keys * scene["time_scale"]).tolist(),
            sampled_interpolation_error_bound_illustration_units=error,
            interpolation_tolerance_fraction=0.01,
            fixed_geometry_displacement_bound_m=scene["deformation"]
            * bundle["model"]["radius_m"]
            * bound,
            material_regions=[
                {"start": a, "stop": min(b, geo.animated_count), "layer_id": c}
                for a, b, c in geo.sides
                if a < geo.animated_count
            ],
            quantization_note="POSITION is float32; physical readback restores declared surface/boundary radius before field evaluation.",
            mesh_coordinate_units="planet radius",
            mesh_coordinate_axes="x lon0, y lon90E, z north; root rotates to glTF Y-up",
            omitted=omitted,
            color_animation="static at scene.time_s",
            resources={**geo.budget, "morph_target_vertices": morph_values, "animated_weight_tracks": 1,
                       "estimated_glb_bytes": estimate},
            export_spec=dict(
                format="glb",
                width=width,
                height=height,
                duration_s=duration_s,
                fps=fps,
                omit_arrows=omit_arrows,
                omit_geography=omit_geography,
                omit_analysis_overlays=omit_analysis_overlays,
                annotation=annotation,
            ),
        )
        d["extras"] = details
        glb.save(staged)
        # Header plus total byte length are checked before committing the pair.
        raw = staged.read_bytes()
        if struct.unpack_from("<4sII", raw) != (b"glTF", 2, len(raw)):
            raise RuntimeError("Invalid GLB container.")
        info.update(details)
    return path
