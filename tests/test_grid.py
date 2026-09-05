"""Grid density is appearance; scientific samples and material sides stay intact."""
from copy import deepcopy
import json

import numpy as np
import pytest

from earth_modes.data import default_scene, validate_scene, bundle_hash
from earth_modes.export import export_glb, export_image, ExportLimits
from earth_modes.export_render import geometry
from earth_modes.fields import evaluate_field
from test_fields import field_bundle
from test_export import decode_glb


def test_scene_versions_and_grid_density_do_not_mutate_physics():
    bundle = field_bundle()
    scene = default_scene(bundle)
    identity = bundle_hash(bundle)
    legacy = {k: v for k, v in scene.items() if k != "wireframe_spacing_deg"}
    legacy["schema_version"] = "1.0"
    before = deepcopy(legacy)
    assert validate_scene(legacy, bundle) == before
    for bad in ({**legacy, "wireframe_spacing_deg": 15},
                {k: v for k, v in scene.items() if k != "wireframe_spacing_deg"},
                {**scene, "wireframe_spacing_deg": True}, {**scene, "wireframe_spacing_deg": 20}):
        with pytest.raises(ValueError, match="wireframe_spacing_deg"):
            validate_scene(bad, bundle)
    scene.update(surface="wireframe", quality="draft")
    grids = [geometry(bundle, {**scene, "wireframe_spacing_deg": d}, ExportLimits()) for d in (5, 30)]
    assert grids[0].budget["grid_point_count"] > grids[1].budget["grid_point_count"]
    assert np.array_equal(grids[0].points[:grids[0].mesh_count], grids[1].points[:grids[1].mesh_count])
    assert np.array_equal(grids[0].bases[:, :grids[0].mesh_count], grids[1].bases[:, :grids[1].mesh_count])
    for d, geo in zip((5, 30), grids):
        n = 32
        assert geo.budget["grid_point_count"] == (180 // d - 1) * (2*n+1) + (360 // d)*(n+1)
        assert len(geo.wire_edges) == (180 // d - 1)*2*n + (360 // d)*n
    filled = geometry(bundle, {**scene, "surface": "solid"}, ExportLimits())
    assert filled.budget["grid_point_count"] == 0 and not filled.budget["grid_sparse_notice"]
    assert bundle_hash(bundle) == identity
    with pytest.raises(ValueError, match="budget"):
        geometry(bundle, {**scene, "wireframe_spacing_deg": 5},
                 ExportLimits(max_points=grids[1].budget["point_count"]), preflight_only=True)


def test_grid_cutaway_glb_retains_lines_filled_sections_and_non_key_motion(tmp_path):
    bundle = field_bundle()
    scene = default_scene(bundle)
    scene.update(surface="wireframe", cutaway=True, quality="draft", wireframe_spacing_deg=30)
    geo = geometry(bundle, scene, ExportLimits())
    midpoint = geo.points[geo.wire_edges].mean(axis=1)
    assert not np.any((midpoint[:, 0] > 0) & (midpoint[:, 1] < 0))
    boundary = midpoint[np.isclose(midpoint[:, 0], 0, atol=1e-15) & (midpoint[:, 1] < -.1)]
    assert len(boundary) > 0
    output = export_glb(bundle, scene, tmp_path / "grid.glb", duration_s=.5)
    doc, array = decode_glb(output)
    primitives = doc["meshes"][0]["primitives"]
    assert [p["mode"] for p in primitives] == [1, 4]
    line_indices = array(primitives[0]["indices"]).ravel()
    face_indices = array(primitives[1]["indices"]).ravel()
    assert line_indices.min() >= geo.mesh_count
    assert face_indices.min() >= geo.surface_count  # No hidden shell triangles obscure sparse wires.
    assert primitives[0]["targets"] == primitives[1]["targets"]
    targets = np.stack([array(a["POSITION"]) for a in primitives[0]["targets"]])
    sampler = doc["animations"][0]["samplers"][0]
    keys = array(sampler["input"]).ravel()
    weights = array(sampler["output"]).reshape(len(keys), len(targets))
    t = .137
    j = np.searchsorted(keys, t)
    blend = (t-keys[j-1])/(keys[j]-keys[j-1])
    displacement = np.einsum('t,tnc->nc', (1-blend)*weights[j-1]+blend*weights[j], targets)
    expected = scene["deformation"]*evaluate_field(bundle, scene["terms"], geo.points[:geo.animated_count]*bundle["model"]["radius_m"], scene["time_s"]+t*scene["time_scale"])
    assert np.max(np.linalg.norm(displacement-expected,axis=1)) < .001
    meta = json.loads((tmp_path / "grid.glb.json").read_text())
    assert meta["resources"]["grid_segment_count"] == len(geo.wire_edges)
    assert meta["annotation_language"] == "en"
    export_image(bundle, scene, tmp_path / "grid.png", width=320, height=240)


def test_high_degree_grid_sampling_and_morph_budget_include_curves(tmp_path):
    bundle = field_bundle()
    mode = bundle["modes"][-1]
    mode["l"] = 64
    bundle["modes"] = [mode]
    scene = default_scene(bundle)
    scene.update(surface="wireframe", wireframe_spacing_deg=30, quality="draft")
    geo = geometry(bundle, scene, ExportLimits())
    assert geo.budget["latitude_intervals"] == 260
    assert geo.budget["grid_sparse_notice"]
    assert len(geo.wire_edges) == 5*520+12*260
    # A limit sufficient for the old triangle buffers must not hide new curves.
    with pytest.raises(ValueError, match="GLB resource budget"):
        export_glb(bundle, scene, tmp_path / "too-large.glb", limits=ExportLimits(max_morph_values=geo.mesh_count*2))
    assert not (tmp_path / "too-large.glb").exists()


def test_offline_faces_and_grid_lines_share_physical_depth_order():
    """A rear line must not paint through a filled scientific section."""
    from types import SimpleNamespace
    from earth_modes.export_render import render
    bundle = field_bundle()
    scene = default_scene(bundle)
    scene.update(surface="wireframe", deformation=0, reference=False)
    scene["camera"].update(azimuth_deg=0, elevation_deg=0)
    points = np.array([[1, -.8, -.6], [1, .8, -.6], [1, 0, .8],
                       [-1, -.25, 0], [-1, .25, 0]], dtype=float)
    unit = points / np.linalg.norm(points, axis=1)[:, None]
    vectors = unit * np.array([1, 1, 1, -1, -1])[:, None]
    geo = SimpleNamespace(points=points, faces=np.array([[0, 1, 2]]),
                          surface_count=0, mesh_count=3, modes=[], budget={"grid_sparse_notice": False},
                          wire_edges=np.array([[3, 4]]),
                          coast_edges=np.empty((0, 2), int), arrow_indices=[],
                          field=lambda time: vectors)
    def pixels():
        fig, _ = render(bundle, scene, geo, 0, 240, 240, annotation=False)
        fig.canvas.draw()
        return np.asarray(fig.canvas.buffer_rgba()).copy()
    with_line = pixels()
    geo.wire_edges = np.empty((0, 2), int)
    without_line = pixels()
    # Compare the line's interior footprint; Matplotlib's single-path fast path
    # rasterizes the triangle perimeter differently when the line is absent.
    # The previous separate zorder=2 collection violates this occlusion check.
    assert np.array_equal(with_line[110:130, 100:140], without_line[110:130, 100:140])
    geo.wire_edges = np.array([[3, 4]])
    points[3:, 0] = 2  # The same line in front must now be visible.
    assert np.any(pixels()[110:130, 100:140] != without_line[110:130, 100:140])


def test_small_annotated_images_keep_notes_and_colorbar_inside_canvas():
    from earth_modes.export_render import render
    bundle = field_bundle()
    scene = default_scene(bundle)
    scene.update(quality="draft")
    geo = geometry(bundle, scene, ExportLimits())
    for width, height in [(320, 240), (640, 480), (1200, 900)]:
        figure, _ = render(bundle, scene, geo, 0, width, height)
        figure.canvas.draw()
        renderer = figure.canvas.get_renderer()
        boxes = [text.get_window_extent(renderer) for text in figure.texts]
        boxes.append(figure.axes[1].yaxis.label.get_window_extent(renderer))
        assert all(box.x0 >= 0 and box.y0 >= 0 and box.x1 <= width and box.y1 <= height for box in boxes)
        # Separate title/mode and the three lower notes remain non-overlapping.
        for a, b in [(0, 1), (2, 3), (3, 4)]:
            assert not boxes[a].overlaps(boxes[b])
