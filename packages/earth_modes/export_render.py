"""Shared material geometry and deterministic orthographic offline rendering."""

from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import json
import numpy as np
from .fields import evaluate_field

ASSETS = Path(__file__).with_name("assets")


@lru_cache(maxsize=2)
def asset(name):
    return json.loads((ASSETS / name).read_text())


def rgba(values, scene):
    palette = np.asarray(
        asset("palettes.json")["magnitude" if scene["color"] == "magnitude" else "signed"]
    )
    limit = scene["color_limit"]
    t = values / limit if scene["color"] == "magnitude" else (values + limit) / (2 * limit)
    return np.column_stack(
        (palette[np.floor(np.clip(t, 0, 1) * 255).astype(int)], np.ones(len(values)))
    )


def scalar(points, field, color):
    if color == "magnitude":
        return np.linalg.norm(field, axis=1)
    norm = np.linalg.norm(points, axis=1)
    unit = np.divide(points, norm[:, None], out=np.zeros_like(points), where=norm[:, None] > 0)
    phi = np.arctan2(points[:, 1], points[:, 0])
    phi[np.hypot(points[:, 0], points[:, 1]) < 1e-14] = 0
    if color == "radial":
        basis = unit
    elif color == "phi":
        basis = np.column_stack((-np.sin(phi), np.cos(phi), np.zeros_like(phi)))
    else:
        basis = np.column_stack(
            (unit[:, 2] * np.cos(phi), unit[:, 2] * np.sin(phi), -np.hypot(unit[:, 0], unit[:, 1]))
        )
    return np.sum(field * basis, axis=1)


def retained(points, cutaway):
    return (
        ~((points[:, 0] > 1e-12) & (points[:, 1] < -1e-12))
        if cutaway
        else np.ones(len(points), dtype=bool)
    )


def sphere(theta, phi):
    return np.column_stack(
        (
            np.sin(theta).ravel() * np.cos(phi).ravel(),
            np.sin(theta).ravel() * np.sin(phi).ravel(),
            np.cos(theta).ravel(),
        )
    )


def camera_basis(scene):
    az, el = np.deg2rad([scene["camera"]["azimuth_deg"], scene["camera"]["elevation_deg"]])
    eye = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    right = np.array([-np.sin(az), np.cos(az), 0])
    up = np.cross(eye, right)
    return np.column_stack((right, up, eye))


@dataclass
class Geometry:
    points: np.ndarray
    faces: np.ndarray
    sides: list
    arrow_indices: np.ndarray
    coast_edges: np.ndarray
    mesh_count: int
    bases: np.ndarray
    modes: list
    terms: list
    budget: dict
    surface_count: int
    wire_edges: np.ndarray
    animated_count: int

    def coefficients(self, physical_times):
        t = np.atleast_1d(physical_times)
        result = []
        for mode, term in zip(self.modes, self.terms):
            c = term["amplitude"] * np.cos(2 * np.pi * mode["frequency_hz"] * t + term["phase_rad"])
            if mode["q"] is not None:
                c *= np.exp(-np.pi * mode["frequency_hz"] * t / mode["q"])
            result.append(c)
        return np.asarray(result).T if result else np.empty((len(t), 0))

    def field(self, physical_time):
        return np.einsum("t,tnc->nc", self.coefficients(physical_time)[0], self.bases)


def geometry(bundle, scene, limits, preflight_only=False):
    lookup = {m["id"]: m for m in bundle["modes"]}
    degree = max((lookup[t["mode_id"]]["l"] for t in scene["terms"]), default=0)
    base = {"draft": 32, "standard": 48, "high": 96}[scene["quality"]]
    n = int(max(base, 4 * (degree + 1)))
    r = scene["radius_fraction"]
    radius = bundle["model"]["radius_m"]
    from .sampling import layer_radial_nodes

    layers = (
        layer_radial_nodes(bundle, scene["terms"], r, base // 2, max_nodes=limits.max_points)
        if scene["cutaway"]
        else []
    )
    surface_count = (n + 1) * (2 * n + 1)
    mesh_count = surface_count + sum(2 * len(nodes) * (n + 1) for _, nodes in layers)
    spacing = scene.get("wireframe_spacing_deg") if scene["surface"] == "wireframe" else None
    line_count = (int(180 / spacing) - 1) * (2 * n + 1) + int(360 / spacing) * (n + 1) if spacing else 0
    animated_count = mesh_count + line_count
    coast = asset("coastlines.json")["lines"] if scene["geography"] else []
    arrow_count = 266 if scene["arrows"] else 0
    count = animated_count + arrow_count + sum(map(len, coast))
    field_cache = 8 * 3 * count * len(scene["terms"])
    triangle_bound = 4 * n * n + sum(4 * (len(nodes) - 1) * n for _, nodes in layers)
    overlay_reserve = 2 * triangle_bound if scene.get("nodes") else 0
    if scene.get("point") is not None:
        overlay_reserve += 1 + (int(scene["trajectory"]["samples"]) if scene["trajectory"]["enabled"] else 0)
    cache = field_cache + 24 * overlay_reserve * (len(scene["terms"]) + 1)
    if count + overlay_reserve > limits.max_points or cache > limits.max_cache_bytes:
        raise ValueError(
            f"Display budget exceeded: {count + overlay_reserve} points including overlay reserve, {cache} spatial-cache bytes; reduce terms/quality."
        )
    budget = {"point_count": count + overlay_reserve, "geometry_point_count": count,
              "overlay_point_reserve": overlay_reserve, "mesh_count": mesh_count,
              "animated_point_count": animated_count, "grid_point_count": line_count,
              "spatial_cache_bytes": cache, "field_cache_bytes": field_cache, "latitude_intervals": n,
              "wireframe_spacing_deg": spacing,
              "grid_sparse_notice": bool(spacing and spacing * degree >= 90),
              "grid_sampling": "n=max(quality_base,4*(l_max+1)); parallel 2n segments, meridian n segments",
              "section_surface": "filled scientific triangles (including legacy Scene 1.0)"}
    if preflight_only:
        return budget
    points = np.empty((count, 3))
    theta, phi = np.meshgrid(
        np.linspace(0, np.pi, n + 1), np.linspace(0, 2 * np.pi, 2 * n + 1), indexing="ij"
    )
    points[:surface_count] = sphere(theta, phi) * r
    sides = [(0, surface_count, None)]
    faces = []

    def grid_faces(start, rows, columns):
        aa = np.arange(rows - 1)[:, None] * columns + np.arange(columns - 1)[None, :] + start
        a = aa.ravel()
        return np.concatenate(
            (
                np.column_stack((a, a + columns, a + 1)),
                np.column_stack((a + 1, a + columns, a + columns + 1)),
            )
        )

    outer_faces = grid_faces(0, n + 1, 2 * n + 1)
    outer_faces = outer_faces[retained(points[outer_faces].mean(axis=1), scene["cutaway"])]
    faces.append(outer_faces)
    cursor = surface_count
    for layer_id, nodes in layers:
        rr, tt = np.meshgrid(nodes, np.linspace(0, np.pi, n + 1), indexing="ij")
        for plane in (0, 1):
            stop = cursor + rr.size
            cap = np.zeros((rr.size, 3))
            cap[:, 1 - plane] = (rr * np.sin(tt)).ravel() * (-1 if plane == 0 else 1)
            cap[:, 2] = (rr * np.cos(tt)).ravel()
            points[cursor:stop] = cap
            faces.append(grid_faces(cursor, len(nodes), n + 1))
            sides.append((cursor, stop, layer_id))
            cursor = stop
    triangles = np.concatenate(faces).astype(np.uint32)
    p = points[triangles]
    areas = np.linalg.norm(np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]), axis=1)
    triangles = triangles[areas > 1e-14]
    wire_edges = []
    if spacing:
        def add_curve(theta, phi):
            nonlocal cursor
            curve = sphere(theta, phi) * r
            # Exact axes keep strict quadrant membership independent of sin(pi)
            # roundoff. Do not classify against the time-dependent displacement.
            curve[np.abs(curve) < 8 * np.finfo(float).eps * r] = 0
            stop = cursor + len(curve)
            points[cursor:stop] = curve
            edges = np.column_stack((np.arange(cursor, stop - 1), np.arange(cursor + 1, stop)))
            if scene["cutaway"]:
                mid = points[edges].mean(axis=1)
                edges = edges[~((mid[:, 0] > 0) & (mid[:, 1] < 0))]
            wire_edges.append(edges)
            cursor = stop
        for j in range(1, int(180 / spacing)):
            add_curve(np.full(2 * n + 1, np.deg2rad(j * spacing)), np.linspace(0, 2 * np.pi, 2 * n + 1))
        for k in range(int(360 / spacing)):
            add_curve(np.linspace(0, np.pi, n + 1), np.full(n + 1, np.deg2rad(k * spacing)))
        sides.append((mesh_count, animated_count, None))
    wire_edges = np.concatenate(wire_edges) if wire_edges else np.empty((0, 2), dtype=np.uint32)
    budget["grid_segment_count"] = len(wire_edges)
    arrow_indices = np.array([], dtype=int)
    if scene["arrows"]:
        tt, pp = np.meshgrid(
            np.arange(1, 12) * np.pi / 12, np.arange(24) * np.pi / 12, indexing="ij"
        )
        seeds = np.concatenate((sphere(tt, pp), [[0, 0, 1], [0, 0, -1]])) * r
        points[cursor : cursor + arrow_count] = seeds
        arrow_indices = np.arange(cursor, cursor + arrow_count)[retained(seeds, scene["cutaway"])]
        sides.append((cursor, cursor + arrow_count, None))
        cursor += arrow_count
    edges = []
    for line in coast:
        lon, lat = np.deg2rad(np.asarray(line)).T
        pp = sphere(np.pi / 2 - lat, lon)
        points[cursor : cursor + len(pp)] = pp
        edge = np.column_stack(
            (np.arange(cursor, cursor + len(pp) - 1), np.arange(cursor + 1, cursor + len(pp)))
        )
        edges.append(edge[retained(points[edge].mean(axis=1), scene["cutaway"])])
        sides.append((cursor, cursor + len(pp), None))
        cursor += len(pp)
    coast_edges = np.concatenate(edges) if edges else np.empty((0, 2), dtype=int)
    bases = np.empty((len(scene["terms"]), count, 3))
    for j, term in enumerate(scene["terms"]):
        for start, stop, layer_id in sides:
            bases[j, start:stop] = evaluate_field(
                bundle,
                [{**term, "amplitude": 1, "phase_rad": 0}],
                points[start:stop] * radius,
                0,
                normalized=True,
                layer_id=layer_id,
            )
    return Geometry(
        points,
        triangles,
        sides,
        arrow_indices,
        coast_edges,
        mesh_count,
        bases,
        [lookup[t["mode_id"]] for t in scene["terms"]],
        scene["terms"],
        budget,
        surface_count,
        wire_edges,
        animated_count,
    )


def render(
    bundle,
    scene,
    geo,
    physical_time,
    width,
    height,
    *,
    overlays=None,
    annotation=True,
    transparent=False,
):
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.collections import PolyCollection, LineCollection
    from matplotlib.colors import ListedColormap, Normalize
    from matplotlib.cm import ScalarMappable

    bg, ink = ("#101d2d", "#e6edf3") if scene["background"] == "dark" else ("#f6f5f0", "#233340")
    fig = Figure(figsize=(width / 100, height / 100), dpi=100, facecolor=bg)
    FigureCanvasAgg(fig)
    # Camera span applies exactly to this named viewport, without mplot3d's implicit zoom.
    rect = (0.025, 0.13, 0.795, 0.73) if annotation else (0, 0, 1, 1)
    # Font sizes are points, while figure locations are fractions. Scale both
    # axes labels and notes to preserve their layout in small requested images.
    font_scale = min(1.0, width / 640, height / 480)
    ax = fig.add_axes(rect, facecolor=bg)
    span = scene["camera"]["distance"]
    aspect = (width * rect[2]) / (height * rect[3])
    ax.set(xlim=(-span * aspect / 2, span * aspect / 2), ylim=(-span / 2, span / 2))
    ax.set_aspect("equal", adjustable="box")
    ax.set_axis_off()
    cam = camera_basis(scene)
    field = geo.field(physical_time)
    deformed = geo.points + scene["deformation"] * field
    projected = deformed @ cam
    values = scalar(geo.points, field, scene["color"])
    face_values = values[geo.faces].mean(axis=1)
    facecolors = rgba(face_values, scene)
    if scene["reference"]:
        p = np.linspace(0, 2 * np.pi, 97)
        c = np.column_stack((np.cos(p), np.sin(p), np.zeros_like(p))) * scene["radius_fraction"]
        for line in (c, c[:, [0, 2, 1]], c[:, [2, 0, 1]]):
            q = line @ cam
            ax.plot(q[:, 0], q[:, 1], color=ink, linewidth=0.65, alpha=0.3, zorder=0)
    wire = scene["surface"] == "wireframe"
    shell = np.all(geo.faces < geo.surface_count, axis=1)
    # One painter order must contain both filled faces and wires. Separate
    # collections let far-side caps cover the opaque foreground shell, or let
    # rear grid lines show through filled caps irrespective of physical depth.
    keep_faces = ~(shell & wire) if wire and scene.get("wireframe_spacing_deg") is not None else np.ones(len(shell), dtype=bool)
    face_ids = np.flatnonzero(keep_faces)
    vertices = [v for v in projected[geo.faces[face_ids], :2]]
    depth = projected[geo.faces[face_ids], 2].mean(axis=1)
    fill = facecolors[face_ids].copy()
    edge = np.zeros_like(fill)
    widths = np.zeros(len(face_ids))
    shell_wires = shell[face_ids] & wire
    fill[shell_wires, 3] = 0
    edge[shell_wires] = facecolors[face_ids[shell_wires]]
    widths[shell_wires] = 0.35
    if len(geo.wire_edges):
        vertices.extend(projected[geo.wire_edges, :2])
        depth = np.concatenate((depth, projected[geo.wire_edges, 2].mean(axis=1)))
        fill = np.concatenate((fill, np.zeros((len(geo.wire_edges), 4))))
        edge = np.concatenate((edge, rgba(values[geo.wire_edges].mean(axis=1), scene)))
        widths = np.concatenate((widths, np.full(len(geo.wire_edges), 0.5)))
    order = np.argsort(depth, kind="stable")
    ax.add_collection(PolyCollection(
        [vertices[i] for i in order], facecolors=fill[order], edgecolors=edge[order],
        linewidths=widths[order], antialiaseds=widths[order] > 0, rasterized=True))
    if scene["cutaway"]:
        intervals = geo.budget["latitude_intervals"]
        for j, (start, stop, side) in enumerate(geo.sides[1:]):
            if start >= geo.mesh_count:
                break
            normal = np.array([1.0, 0.0, 0.0]) if j % 2 == 0 else np.array([0.0, -1.0, 0.0])
            if normal @ cam[:, 2] <= 0:
                continue
            for indices in (
                np.arange(start, start + intervals + 1),
                np.arange(stop - intervals - 1, stop),
            ):
                q = projected[indices]
                ax.plot(q[:, 0], q[:, 1], color="#677581", linewidth=0.55, alpha=0.8, zorder=2)
    if len(geo.coast_edges):
        edges = geo.coast_edges
        front = (geo.points[edges].mean(axis=1) @ cam)[:, 2] > 0
        ax.add_collection(
            LineCollection(projected[edges[front], :2], colors=ink, linewidths=0.6, zorder=3)
        )
    if len(geo.arrow_indices):
        ii = geo.arrow_indices
        ii = ii[(geo.points[ii] @ cam)[:, 2] >= 0]
        vectors = (scene["arrow_scale"] * field[ii]) @ cam
        ax.quiver(
            projected[ii, 0],
            projected[ii, 1],
            vectors[:, 0],
            vectors[:, 1],
            angles="xy",
            scale_units="xy",
            scale=1,
            width=0.0025,
            color=ink,
            zorder=4,
        )
    if overlays is not None:
        if len(overlays.node_points):
            # Stored interpolation weights follow the same material mesh field.
            displacement = np.einsum(
                "t,setc->sec", geo.coefficients(physical_time)[0], overlays.node_bases
            )
            segments = (overlays.node_points + scene["deformation"] * displacement) @ cam
            keep = (overlays.node_points @ cam)[:, :, 2].mean(axis=1) >= -1e-6
            ax.add_collection(
                LineCollection(segments[keep, :, :2], colors="#193e49", linewidths=1.15, zorder=5)
            )
        if overlays.trajectory is not None:
            track = overlays.trajectory @ cam
            ax.plot(track[:, 0], track[:, 1], color="#eea853", linewidth=1.3, zorder=6)
        if overlays.point is not None:
            p = overlays.point + scene["deformation"] * np.einsum(
                "t,tc->c", geo.coefficients(physical_time)[0], overlays.point_bases
            )
            q = p @ cam
            ax.scatter(q[0], q[1], color="#eea853", edgecolors=ink, s=22, zorder=7)
    palette = asset("palettes.json")["magnitude" if scene["color"] == "magnitude" else "signed"]
    limit = scene["color_limit"]
    norm = Normalize(0 if scene["color"] == "magnitude" else -limit, limit)
    cb = fig.colorbar(
        ScalarMappable(norm=norm, cmap=ListedColormap(palette)),
        cax=fig.add_axes((0.86, 0.28, 0.018, 0.43)),
    )
    cb.ax.tick_params(colors=ink, labelsize=8 * font_scale, pad=2 * font_scale, length=3 * font_scale)
    cb.outline.set_edgecolor(ink)
    cb.set_label(f"{scene['color']} (illustration units)", color=ink, fontsize=9 * font_scale, labelpad=2 * font_scale)
    clipping = int(
        np.count_nonzero(
            (values[:geo.mesh_count] > limit) | (values[:geo.mesh_count] < (0 if scene["color"] == "magnitude" else -limit))
        )
    )
    fig.text(0.045, 0.94, bundle["model"]["name"], color=ink, fontsize=14 * font_scale, weight="bold")
    modes = " + ".join(f"{t['mode_id']} [m={t['m']}]" for t in scene["terms"])
    fig.text(0.045, 0.902, modes[:145], color=ink, fontsize=9 * font_scale)
    first_period = 1 / geo.modes[0]["frequency_hz"] if geo.modes else 0.0
    fig.text(
        0.045,
        0.087,
        f"t = {physical_time:.5g} s   |   T(first) = {first_period:.5g} s"
        f"   |   playback = {scene['time_scale']:.4g} physical s/s",
        color=ink,
        fontsize=8 * font_scale,
    )
    fig.text(
        0.045,
        0.054,
        f"Geometry: {scene['deformation']:.4g} R/unit   |   Arrows: {scene['arrow_scale']:.4g} R/unit"
        + (f"   |   Color clipped: {clipping} samples" if clipping else ""),
        color=ink,
        fontsize=8 * font_scale,
    )
    fig.text(
        0.045,
        0.025,
        "Normalized modal illustration, not earthquake excitation."
        + ("  Coastline: Natural Earth, public domain." if scene["geography"] else ""),
        color=ink,
        fontsize=8 * font_scale,
    )
    if overlays is not None and overlays.trajectory_times is not None and annotation:
        window = overlays.trajectory_times
        fig.text(
            0.045,
            0.147,
            f"Material trajectory: {window[0]:.5g}–{window[-1]:.5g} physical s (fixed window)",
            color=ink,
            fontsize=7 * font_scale,
        )
    if overlays is not None and overlays.node_note and annotation:
        fig.text(0.045, 0.115, overlays.node_note[:155], color=ink, fontsize=7 * font_scale)
    if geo.budget["grid_sparse_notice"] and annotation:
        fig.text(0.045, 0.175, "Sparse surface grid: extrema between curves may be hidden; use filled surface or smaller spacing.", color=ink, fontsize=7 * font_scale)
    if not annotation:
        for text in fig.texts:
            text.set_visible(False)
        cb.ax.set_visible(False)
    if transparent:
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
    return fig, clipping
