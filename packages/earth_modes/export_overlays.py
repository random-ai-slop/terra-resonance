"""Small, field-derived explanatory overlays; never particle advection solvers."""

from dataclasses import dataclass
import numpy as np
from .fields import evaluate_field, sample_probe
from .data import _integer
from .export_render import scalar
from .export_common import ExportLimits


@dataclass
class Overlays:
    node_points: np.ndarray
    node_bases: np.ndarray
    node_note: str
    point: np.ndarray | None
    point_bases: np.ndarray | None
    trajectory: np.ndarray | None
    trajectory_times: np.ndarray | None


def build_overlays(bundle, scene, geo, limits=None):
    limits = limits or ExportLimits()
    node_points, node_bases = [], []
    notes = []
    if scene.get("nodes", False):
        active = [i for i, t in enumerate(scene["terms"]) if t["amplitude"] != 0]
        if len(active) != 1 or scene["color"] == "magnitude":
            raise ValueError("Nodes require one nonzero real term and a signed scalar component.")
        basis = geo.bases[active[0]]
        values = scalar(geo.points, basis, scene["color"])
        for start, stop, side in geo.sides:
            if start >= geo.mesh_count:
                continue
            faces = geo.faces[np.all((geo.faces >= start) & (geo.faces < stop), axis=1)]
            if not len(faces):
                continue
            scale = float(np.max(np.abs(values[start:stop])))
            vector_scale = float(np.max(np.linalg.norm(basis[start:stop], axis=1)))
            if scale <= 64 * np.finfo(float).eps * max(vector_scale, 1e-300):
                notes.append(
                    f"{side or 'shell'}: component numerically zero on this sampled surface / contour not applicable"
                )
                continue
            epsilon = scale * 1e-10
            for face in faces:
                v = values[face]
                if v.min() > epsilon or v.max() < -epsilon:
                    continue
                intersections = []
                for a, b in ((0, 1), (1, 2), (2, 0)):
                    va, vb = v[a], v[b]
                    if abs(va) <= epsilon:
                        intersections.append((geo.points[face[a]], geo.bases[:, face[a]]))
                    elif va * vb < 0:
                        fraction = va / (va - vb)
                        intersections.append(
                            (
                                (1 - fraction) * geo.points[face[a]]
                                + fraction * geo.points[face[b]],
                                (1 - fraction) * geo.bases[:, face[a]]
                                + fraction * geo.bases[:, face[b]],
                            )
                        )
                unique = []
                for item in intersections:
                    if not any(np.linalg.norm(item[0] - old[0]) < 1e-12 for old in unique):
                        unique.append(item)
                if len(unique) == 2:
                    overlay_bytes = (len(node_points) + 1) * 2 * 3 * 8 * (1 + len(scene["terms"]))
                    if geo.budget["field_cache_bytes"] + overlay_bytes > limits.max_cache_bytes:
                        raise ValueError(
                            "Node overlay exceeds the display cache budget; reduce quality or terms."
                        )
                    node_points.append([unique[0][0], unique[1][0]])
                    node_bases.append([unique[0][1], unique[1][1]])
    point, point_bases, trajectory, trajectory_times = None, None, None, None
    spec = scene.get("point")
    if spec is not None:
        lat, lon = np.deg2rad([spec["latitude_deg"], spec["longitude_deg"]])
        point = (
            np.array([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)])
            * spec["radius_fraction"]
        )
        point_bases = np.array(
            [
                evaluate_field(
                    bundle,
                    [{**term, "amplitude": 1, "phase_rad": 0}],
                    point[None] * bundle["model"]["radius_m"],
                    0,
                    normalized=True,
                    layer_id=spec.get("layer_id"),
                )[0]
                for term in scene["terms"]
            ]
        )
        window = scene.get("trajectory", {})
        if window.get("enabled", False):
            samples = _integer(window["samples"], "trajectory.samples", 2)
            if samples > 2048:
                raise ValueError("Trajectory samples must be an integer between 2 and 2048.")
            lookup = {m["id"]: m for m in bundle["modes"]}
            fastest = max(
                (lookup[t["mode_id"]]["frequency_hz"] for t in scene["terms"] if t["amplitude"]),
                default=0,
            )
            if (samples - 1) < 24 * fastest * window["duration_s"]:
                raise ValueError(
                    "Trajectory needs at least 24 sampling intervals per fastest included period."
                )
            trajectory_times = np.linspace(
                window["start_s"], window["start_s"] + window["duration_s"], samples
            )
            vectors = sample_probe(
                bundle,
                scene,
                spec["latitude_deg"],
                spec["longitude_deg"],
                spec["radius_fraction"],
                trajectory_times,
                normalized=True,
                layer_id=spec.get("layer_id"),
            )
            trajectory = point + scene["deformation"] * vectors
    return Overlays(
        np.asarray(node_points),
        np.asarray(node_bases),
        "; ".join(notes),
        point,
        point_bases,
        trajectory,
        trajectory_times,
    )


def overlay_metadata(overlays, scene):
    """Scientific meaning and sampling retained even for a clean visual export."""
    return {
        "nodes": {
            "enabled": scene.get("nodes", False),
            "component": scene["color"],
            "definition": "single-real-term spatial component zero contour; temporal factor removed",
            "relative_zero_threshold": 1e-10,
            "segment_count": len(overlays.node_points),
            "note": overlays.node_note,
        },
        "material_point": scene.get("point"),
        "trajectory": scene.get("trajectory"),
        "trajectory_definition": "fixed material point sampled on the saved fixed physical interval; current marker follows scene time",
    }
