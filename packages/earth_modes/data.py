"""Validate and serialize the versioned scientific and scene dictionaries.

Validation never normalizes, resamples, or discards provenance. Material
interfaces belong to two independently sampled layers by design.
"""
from __future__ import annotations

import json
import math
import hashlib
import os
import tempfile
from copy import deepcopy
from pathlib import Path

import numpy as np
import rfc8785

SCHEMA_VERSION = "1.0"
SCENE_VERSION = "1.1"
MAX_VISUAL_DEGREE = 64
MAX_TERMS = 32
MAX_SAFE_INTEGER = 2**53 - 1


def _json_tree(value, name="value"):
    """Reject values which cannot round-trip through the shared JCS domain."""
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, str):
        if any(0xD800 <= ord(char) <= 0xDFFF for char in value):
            raise ValueError(f"{name} contains a lone Unicode surrogate")
    elif isinstance(value, (int, float)):
        if isinstance(value, int) and abs(value) > MAX_SAFE_INTEGER:
            raise ValueError(f"{name} integer exceeds the JavaScript safe range; encode identifiers as strings")
        if not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _json_tree(item, f"{name}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{name} keys must be strings")
            _json_tree(key, name)
            _json_tree(item, f"{name}.{key}")
    else:
        raise ValueError(f"{name} is not a JSON-compatible value")


def canonical_hash(value) -> str:
    """SHA-256 of RFC 8785 bytes; shared fixtures cover JS number formatting."""
    _json_tree(value)
    return hashlib.sha256(rfc8785.dumps(value)).hexdigest()


def model_hash(model) -> str:
    validate_model(model)
    return canonical_hash({key: value for key, value in model.items() if key != "provenance"})


def bundle_hash(bundle) -> str:
    validate_bundle(bundle)
    return canonical_hash(bundle)


def _number(value, name, minimum=None, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    if positive and value <= 0 or minimum is not None and value < minimum:
        raise ValueError(f"{name} is outside its allowed range")
    return value


def _integer(value, name, minimum=0):
    # JSON Schema integer and JavaScript Number do not distinguish 1 from 1.0.
    # Return a local native integer; validators never rewrite caller data.
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or value != math.trunc(value)
            or abs(value) > MAX_SAFE_INTEGER or value < minimum):
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return int(value)


def _string(value, name):
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a nonempty string")
    return value


def _mapping(value, name):
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    return value


def _array(value, name, length=None):
    if not isinstance(value, list) or len(value) < 2 or length is not None and len(value) != length:
        raise ValueError(f"{name} must be a numeric array of matching length (at least 2)")
    for item in value:
        _number(item, name)
    return value


def _radii(value, name):
    values = _array(value, name)
    if values[0] < 0 or any(b <= a for a, b in zip(values, values[1:])):
        raise ValueError(f"{name} must be nonnegative and strictly increasing within its region")
    return values


def _same_radius(a, b, radius):
    return math.isclose(a, b, rel_tol=0, abs_tol=boundary_tolerance(radius))


def boundary_tolerance(radius_m):
    return 64 * np.finfo(float).eps * radius_m


def validate_model(model: dict) -> dict:
    """Check SI material layers, preserving the two sides of each interface."""
    _mapping(model, "model")
    _json_tree(model, "model")
    _string(model.get("id"), "model.id")
    _string(model.get("name"), "model.name")
    radius = _number(model.get("radius_m"), "model.radius_m", positive=True)
    layers = model.get("layers")
    if not isinstance(layers, list) or not layers:
        raise ValueError("model.layers must be a nonempty list")
    ids, previous = set(), 0.0
    for layer in layers:
        _mapping(layer, "layer")
        layer_id = _string(layer.get("id"), "layer.id")
        if layer_id in ids:
            raise ValueError(f"duplicate layer id: {layer_id}")
        ids.add(layer_id)
        _string(layer.get("name"), "layer.name")
        if layer.get("phase") not in ("solid", "fluid"):
            raise ValueError("layer.phase must be solid or fluid")
        r = _radii(layer.get("r_m"), "layer.r_m")
        if not _same_radius(r[0], previous, radius) or r[-1] > radius + boundary_tolerance(radius):
            raise ValueError("layers must tile the model from center to surface without gaps or overlaps")
        if r[-1] - r[0] <= 2 * boundary_tolerance(radius):
            raise ValueError("material boundaries are too close to resolve at this radius")
        previous = r[-1]
        rho = _array(layer.get("rho_kg_m3"), "layer.rho_kg_m3", len(r))
        vp = _array(layer.get("vp_m_s"), "layer.vp_m_s", len(r))
        vs = _array(layer.get("vs_m_s"), "layer.vs_m_s", len(r))
        if any(x <= 0 for x in rho + vp) or any(x < 0 for x in vs):
            raise ValueError("density and vp must be positive; vs must be nonnegative")
        if layer["phase"] == "fluid" and any(x != 0 for x in vs):
            raise ValueError("fluid layers require zero shear speed")
        if layer["phase"] == "solid" and any(x <= 0 for x in vs):
            raise ValueError("solid layers require positive shear speed")
        if any(p * p <= 4.0 / 3.0 * s * s for p, s in zip(vp, vs)):
            raise ValueError("material requires positive bulk modulus (vp² > 4vs²/3)")
        for key in ("q_bulk", "q_shear"):
            if key in layer:
                q_values = layer[key]
                if not isinstance(q_values, list) or len(q_values) != len(r):
                    raise ValueError(f"layer.{key} must match the radial sample count")
                for q_value in q_values:
                    if q_value is not None:
                        _number(q_value, f"layer.{key}", positive=True)
                if key == "q_shear" and layer["phase"] == "fluid" and any(q is not None for q in q_values):
                    raise ValueError("fluid shear Q must be null")
    if not _same_radius(previous, radius, radius):
        raise ValueError("last layer must end at model.radius_m")
    if "reference_frequency_hz" in model:
        _number(model["reference_frequency_hz"], "model.reference_frequency_hz", positive=True)
    if "provenance" in model:
        _mapping(model["provenance"], "model.provenance")
    return model


def mass_integral(model, mode) -> float:
    """Canonical discrete norm, interpolating density only within each layer."""
    layers = {layer["id"]: layer for layer in model["layers"]}
    integral = 0.0
    for region in mode["regions"]:
        layer = layers[region["layer_id"]]
        r = np.asarray(region["r_m"], dtype=float)
        rho = np.interp(r, layer["r_m"], layer["rho_kg_m3"])
        squared = sum(np.asarray(region[key], dtype=float) ** 2 for key in ("u", "v", "w"))
        integral += float(np.trapezoid(rho * r**2 * squared, r))
    return integral


def _validate_quality(quality, frequency_hz, expected_model_hash):
    _mapping(quality, "mode.provenance.quality")
    status = quality.get("status")
    if status not in ("unverified", "unconverged", "converged", "benchmark_checked"):
        raise ValueError("invalid mode quality status")
    warnings = quality.get("warnings")
    if not isinstance(warnings, list) or any(not isinstance(item, str) for item in warnings):
        raise ValueError("quality.warnings must be a list of strings")
    if "mesh_convergence" not in quality or "benchmark" not in quality:
        raise ValueError("quality must declare independent mesh_convergence and benchmark evidence (or null)")
    mesh = quality["mesh_convergence"]
    if mesh is not None:
        _mapping(mesh, "quality.mesh_convergence")
        for key in ("coarse_mesh", "fine_mesh"):
            _integer(mesh.get(key), f"mesh_convergence.{key}", 1)
        if mesh["fine_mesh"] <= mesh["coarse_mesh"]:
            raise ValueError("fine_mesh must exceed coarse_mesh")
        _number(mesh.get("relative_frequency_change"), "mesh_convergence.relative_frequency_change", minimum=0)
        _number(mesh.get("tolerance"), "mesh_convergence.tolerance", positive=True)
    benchmark = quality["benchmark"]
    if benchmark is not None:
        _mapping(benchmark, "quality.benchmark")
        for key in ("source", "quantity", "model_hash"):
            _string(benchmark.get(key), f"benchmark.{key}")
        _number(benchmark.get("reference_frequency_hz"), "benchmark.reference_frequency_hz", positive=True)
        _number(benchmark.get("relative_error"), "benchmark.relative_error", minimum=0)
        _number(benchmark.get("tolerance"), "benchmark.tolerance", positive=True)
        if benchmark["quantity"] != "frequency_hz":
            raise ValueError("benchmark.quantity must be frequency_hz")
        if benchmark["model_hash"] != expected_model_hash:
            raise ValueError("benchmark.model_hash does not match bundle.model")
        measured = abs(frequency_hz - benchmark["reference_frequency_hz"]) / benchmark["reference_frequency_hz"]
        rounding = 64 * np.finfo(float).eps * max(1.0, measured, benchmark["relative_error"])
        if not math.isfinite(measured) or abs(measured - benchmark["relative_error"]) > rounding:
            raise ValueError("benchmark.relative_error is inconsistent with mode frequency and reference")
    if status == "converged" and (mesh is None or mesh["relative_frequency_change"] > mesh["tolerance"]):
        raise ValueError("converged status requires passing mesh evidence")
    if status == "unconverged" and (mesh is None or mesh["relative_frequency_change"] <= mesh["tolerance"]):
        raise ValueError("unconverged status requires failing mesh evidence")
    if status == "benchmark_checked" and (benchmark is None or benchmark["relative_error"] > benchmark["tolerance"]):
        raise ValueError("benchmark_checked requires passing benchmark evidence")


def _validate_groups(groups):
    if not isinstance(groups, list):
        raise ValueError("bundle.provenance.groups must be a list")
    for group in groups:
        _mapping(group, "group")
        if group.get("family") not in ("R", "S", "T") or group.get("status") not in ("success", "not_applicable"):
            raise ValueError("invalid solver group family or status")
        _integer(group.get("l"), "group.l")
        _integer(group.get("matrix_dimension"), "group.matrix_dimension")
        spectrum = _mapping(group.get("spectrum"), "group.spectrum")
        for key in ("negative", "near_zero", "positive"):
            _integer(spectrum.get(key), f"spectrum.{key}")
        _number(spectrum.get("threshold"), "spectrum.threshold", minimum=0)
        completeness = _mapping(group.get("spectral_completeness"), "group.spectral_completeness")
        if completeness.get("status") not in ("complete", "truncated") or not isinstance(completeness.get("reason"), str):
            raise ValueError("group spectral completeness requires status and reason")


def validate_bundle(bundle: dict) -> dict:
    _mapping(bundle, "bundle")
    _json_tree(bundle, "bundle")
    if bundle.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported bundle schema_version")
    model = validate_model(bundle.get("model"))
    _mapping(bundle.get("provenance"), "bundle.provenance")
    if "groups" in bundle["provenance"]:
        _validate_groups(bundle["provenance"]["groups"])
    layers = {layer["id"]: layer for layer in model["layers"]}
    modes = bundle.get("modes")
    if not isinstance(modes, list):
        raise ValueError("bundle.modes must be a list")
    ids = set()
    expected_model_hash = canonical_hash({key: value for key, value in model.items() if key != "provenance"})
    for mode in modes:
        _mapping(mode, "mode")
        mode_id = _string(mode.get("id"), "mode.id")
        if mode_id in ids:
            raise ValueError(f"duplicate mode id: {mode_id}")
        ids.add(mode_id)
        family = mode.get("family")
        if family not in ("R", "S", "T"):
            raise ValueError("mode.family must be R, S or T")
        _integer(mode.get("n"), "mode.n")
        degree = _integer(mode.get("l"), "mode.l")
        if family == "R" and degree != 0 or family != "R" and degree == 0:
            raise ValueError("radial modes require l=0; S/T require l>=1")
        _number(mode.get("frequency_hz"), "mode.frequency_hz", positive=True)
        if "q" not in mode:
            raise ValueError("mode.q must be a positive number or null")
        if mode.get("q") is not None:
            _number(mode["q"], "mode.q", positive=True)
        if mode.get("normalization") != "mass_integral_1":
            raise ValueError("unsupported normalization; convert eigenfunctions to mass_integral_1 before import")
        _mapping(mode.get("provenance"), "mode.provenance")
        _validate_quality(mode["provenance"].get("quality"), mode["frequency_hz"], expected_model_hash)
        regions = mode.get("regions")
        if not isinstance(regions, list) or not regions:
            raise ValueError("mode.regions must be nonempty")
        seen = set()
        for region in regions:
            _mapping(region, "region")
            layer_id = region.get("layer_id")
            if layer_id not in layers or layer_id in seen:
                raise ValueError("regions require unique known layer_id values")
            seen.add(layer_id)
            layer = layers[layer_id]
            if family == "T" and layer["phase"] != "solid":
                raise ValueError("toroidal modes may only occupy solid layers")
            r = _radii(region.get("r_m"), "region.r_m")
            if not _same_radius(r[0], layer["r_m"][0], model["radius_m"]) or not _same_radius(r[-1], layer["r_m"][-1], model["radius_m"]):
                raise ValueError("each region must span its named material layer")
            components = {key: _array(region.get(key), f"region.{key}", len(r)) for key in ("u", "v", "w")}
            if "potential" in region:
                _array(region["potential"], "region.potential", len(r))
            forbidden = ("v", "w") if family == "R" else ("u", "v") if family == "T" else ("w",)
            if any(any(x != 0 for x in components[key]) for key in forbidden):
                raise ValueError(f"{family} mode contains forbidden displacement components")
        norm = mass_integral(model, mode)
        if not math.isfinite(norm) or not math.isclose(norm, 1.0, rel_tol=1e-6, abs_tol=1e-8):
            raise ValueError(f"mode {mode_id} mass integral must be 1; got {norm:.9g}")
        scale = max(float(np.max(np.sqrt(sum(np.asarray(region[key]) ** 2 for key in ("u", "v", "w"))))) for region in regions)
        center_region = next((region for region in regions if region["r_m"][0] == 0), None)
        if center_region is not None:
            u0, v0, w0 = (center_region[key][0] for key in ("u", "v", "w"))
            error = abs(v0 - math.sqrt(2) * u0) if family == "S" and degree == 1 else max(abs(u0), abs(v0), abs(w0))
            if error > 1e-6 * scale:
                raise ValueError(f"mode {mode_id} violates center regularity")
        if any("potential" in region for region in regions):
            potential = _mapping(mode["provenance"].get("potential"), "mode.provenance.potential")
            if potential.get("status") not in ("solved", "postprocessed"):
                raise ValueError("potential metadata requires solved/postprocessed status")
            _string(potential.get("units"), "potential.units")
    return bundle


def load_bundle(path) -> dict:
    return validate_bundle(_read_json(path))


def save_bundle(bundle, path, overwrite=False):
    validate_bundle(bundle)
    _write_json(bundle, path, overwrite)


def validate_terms(terms, bundle):
    """Validate the independently callable field evaluator's term list."""
    if not isinstance(terms, list) or len(terms) > MAX_TERMS:
        raise ValueError(f"terms must be a list with at most {MAX_TERMS} entries")
    modes = {mode["id"]: mode for mode in bundle["modes"]}
    for term in terms:
        _mapping(term, "term")
        if term.get("mode_id") not in modes:
            raise ValueError("term references an unknown mode_id")
        mode = modes[term["mode_id"]]
        if mode["l"] > MAX_VISUAL_DEGREE:
            raise ValueError(f"field rendering supports l <= {MAX_VISUAL_DEGREE}; higher modes remain available as data")
        m = _integer(term.get("m"), "term.m", -MAX_VISUAL_DEGREE)
        if abs(m) > mode["l"]:
            raise ValueError("term.m must be an integer satisfying |m| <= l")
        _number(term.get("amplitude"), "term.amplitude")
        _number(term.get("phase_rad"), "term.phase_rad")
    return terms


def validate_scene(scene: dict, bundle: dict) -> dict:
    _mapping(scene, "scene")
    _json_tree(scene, "scene")
    version = scene.get("schema_version")
    if version not in ("1.0", SCENE_VERSION) or scene.get("model_id") != bundle["model"]["id"]:
        raise ValueError("scene schema or model_id does not match bundle")
    spacing = scene.get("wireframe_spacing_deg")
    if version == "1.0" and spacing is not None:
        raise ValueError("Scene 1.0 requires absent/null wireframe_spacing_deg; choose Scene 1.1 explicitly")
    if version == SCENE_VERSION and "wireframe_spacing_deg" not in scene:
        raise ValueError("Scene 1.1 requires wireframe_spacing_deg")
    if spacing is not None and _integer(spacing, "wireframe_spacing_deg", 1) not in (5, 10, 15, 30):
        raise ValueError("wireframe_spacing_deg must be null, 5, 10, 15, or 30")
    if scene.get("bundle_hash") != bundle_hash(bundle):
        raise ValueError("scene.bundle_hash does not match this bundle")
    validate_terms(scene.get("terms"), bundle)
    _number(scene.get("time_s"), "scene.time_s", minimum=0)
    _number(scene.get("time_scale"), "scene.time_scale", positive=True)
    _number(scene.get("deformation"), "scene.deformation", minimum=0)
    _number(scene.get("arrow_scale"), "scene.arrow_scale", minimum=0)
    _number(scene.get("color_limit"), "scene.color_limit", positive=True)
    radius = _number(scene.get("radius_fraction"), "scene.radius_fraction", positive=True)
    if radius > 1:
        raise ValueError("radius_fraction must be <= 1")
    for field, values in {"surface": ("solid", "wireframe"), "color": ("radial", "magnitude", "theta", "phi"), "background": ("dark", "light"), "quality": ("draft", "standard", "high")}.items():
        if scene.get(field) not in values:
            raise ValueError(f"invalid scene.{field}")
    for field in ("arrows", "reference", "cutaway", "geography"):
        if not isinstance(scene.get(field), bool):
            raise ValueError(f"scene.{field} must be boolean")
    if scene["geography"] and radius != 1:
        raise ValueError("geography is a surface reference and requires radius_fraction=1")
    camera = _mapping(scene.get("camera"), "scene.camera")
    _number(camera.get("azimuth_deg"), "camera.azimuth_deg")
    elevation = _number(camera.get("elevation_deg"), "camera.elevation_deg")
    if abs(elevation) > 90:
        raise ValueError("camera.elevation_deg must be in [-90, 90]")
    _number(camera.get("distance"), "camera.distance", positive=True)
    if "point" not in scene:
        raise ValueError("scene.point must be a MaterialPoint or null")
    if scene["point"] is not None:
        _mapping(scene["point"], "scene.point")
        if "radius_fraction" not in scene["point"]:
            raise ValueError("scene.point.radius_fraction is required")
        validate_material_point(scene["point"], bundle)
    trajectory = _mapping(scene.get("trajectory"), "scene.trajectory")
    if not isinstance(trajectory.get("enabled"), bool):
        raise ValueError("trajectory.enabled must be boolean")
    _number(trajectory.get("start_s"), "trajectory.start_s", minimum=0)
    _number(trajectory.get("duration_s"), "trajectory.duration_s", positive=True)
    samples = _integer(trajectory.get("samples"), "trajectory.samples", 2)
    if samples > 2048:
        raise ValueError("trajectory.samples must not exceed 2048")
    if trajectory["enabled"]:
        if scene["point"] is None:
            raise ValueError("an enabled trajectory requires scene.point")
        modes = {mode["id"]: mode for mode in bundle["modes"]}
        fastest = max((modes[term["mode_id"]]["frequency_hz"] for term in scene["terms"] if term["amplitude"] != 0), default=0)
        if samples - 1 < 24 * fastest * trajectory["duration_s"]:
            raise ValueError("trajectory requires at least 24 sample intervals per fastest included cycle")
    if not isinstance(scene.get("nodes"), bool):
        raise ValueError("scene.nodes must be boolean")
    if scene["nodes"] and (scene["color"] == "magnitude" or sum(term["amplitude"] != 0 for term in scene["terms"]) != 1):
        raise ValueError("spatial nodes require one active real term and a signed component")
    return scene


def default_scene(bundle: dict) -> dict:
    validate_bundle(bundle)
    candidates = [mode for mode in bundle["modes"] if mode["l"] <= MAX_VISUAL_DEGREE]
    if not candidates:
        raise ValueError("bundle has no modes within the visual degree limit")
    mode = next((mode for mode in candidates if mode["family"] == "S" and mode["l"] == 2), candidates[0])
    return {"schema_version": SCENE_VERSION, "wireframe_spacing_deg": 15,
            "model_id": bundle["model"]["id"], "bundle_hash": bundle_hash(bundle),
            "terms": [{"mode_id": mode["id"], "m": 0, "amplitude": 1.0, "phase_rad": 0.0}],
            "time_s": 0.0, "time_scale": 1.0 / mode["frequency_hz"] / 8.0,
            "deformation": 0.035, "surface": "solid", "geography": False, "color": "radial", "arrows": False,
            "reference": True, "cutaway": False, "radius_fraction": 1.0,
            "quality": "standard", "arrow_scale": 0.12, "color_limit": math.sqrt(3 * (2 * mode["l"] + 1) / (4 * math.pi)),
            "point": None, "trajectory": {"enabled": False, "start_s": 0.0, "duration_s": 1.0 / mode["frequency_hz"], "samples": 256}, "nodes": False,
            "camera": {"azimuth_deg": 25.0, "elevation_deg": 18.0, "distance": 3.2}, "background": "dark"}


def validate_material_point(point, bundle=None):
    _mapping(point, "point")
    _json_tree(point, "point")
    lat = _number(point.get("latitude_deg"), "point.latitude_deg")
    _number(point.get("longitude_deg"), "point.longitude_deg")
    radius = _number(point.get("radius_fraction", 1.0), "point.radius_fraction", minimum=0)
    if abs(lat) > 90 or radius > 1:
        raise ValueError("point requires latitude in [-90,90] and radius_fraction in [0,1]")
    if "layer_id" in point:
        layer_id = _string(point["layer_id"], "point.layer_id")
        if bundle is not None:
            model = bundle["model"]
            layer = next((layer for layer in model["layers"] if layer["id"] == layer_id), None)
            if layer is None:
                raise ValueError("point.layer_id is unknown")
            r = radius * model["radius_m"]
            tolerance = boundary_tolerance(model["radius_m"])
            if r < layer["r_m"][0] - tolerance or r > layer["r_m"][-1] + tolerance:
                raise ValueError("point radius does not lie in its selected layer")
    return point


def validate_probe(probe, bundle=None):
    """Validate a ProbeSpec without adding defaults or mutating it."""
    validate_material_point(probe, bundle)
    allowed = {"latitude_deg", "longitude_deg", "radius_fraction", "layer_id", "start_s", "step_s", "sample_count", "derivative", "normalized"}
    if set(probe) - allowed:
        raise ValueError(f"unknown ProbeSpec keys: {sorted(set(probe) - allowed)}")
    _number(probe.get("start_s"), "probe.start_s", minimum=0)
    _number(probe.get("step_s"), "probe.step_s", positive=True)
    _integer(probe.get("sample_count"), "probe.sample_count", 1)
    if _integer(probe.get("derivative", 0), "probe.derivative") not in (0, 1, 2):
        raise ValueError("probe.derivative must be 0, 1, or 2")
    if not isinstance(probe.get("normalized", True), bool):
        raise ValueError("probe.normalized must be boolean")
    last_time = probe["start_s"] + (probe["sample_count"] - 1) * probe["step_s"]
    if not math.isfinite(last_time):
        raise ValueError("probe time range must remain finite")
    if probe["sample_count"] > 1 and probe["step_s"] < math.ulp(last_time):
        raise ValueError("probe.step_s is below the floating-point time resolution at this start")
    return probe


def default_color_limit(bundle, terms):
    validate_terms(terms, bundle)
    modes = {mode["id"]: mode for mode in bundle["modes"]}
    return max(1e-12, sum(abs(term["amplitude"]) * math.sqrt(3 * (2 * modes[term["mode_id"]]["l"] + 1) / (4 * math.pi)) for term in terms))


def default_export_spec(format="png"):
    return validate_export_spec({"format": format})


def validate_export_spec(spec):
    """Return a new fully resolved portable ExportSpec, preserving the input."""
    _mapping(spec, "export")
    _json_tree(spec, "export")
    defaults = {"format": "png", "width": 1200, "height": 900, "duration_s": 8.0, "fps": None,
                "transparent": False, "annotation": True, "omit_arrows": False, "omit_geography": False,
                "omit_analysis_overlays": False}
    if set(spec) - set(defaults):
        raise ValueError(f"unknown ExportSpec keys: {sorted(set(spec) - set(defaults))}")
    result = {**defaults, **deepcopy(spec)}
    if result["format"] not in ("png", "svg", "csv", "frames", "gif", "mp4", "glb"):
        raise ValueError("unsupported export.format")
    for key in ("width", "height"):
        result[key] = _integer(result[key], f"export.{key}", 1)
    _number(result["duration_s"], "export.duration_s", positive=True)
    if result["fps"] is not None:
        _number(result["fps"], "export.fps", positive=True)
        if result["format"] == "gif" and result["fps"] not in (1, 2, 4, 5, 10, 20, 25, 50):
            raise ValueError("GIF fps must have an exact integer 10 ms frame delay")
    for key in ("transparent", "annotation", "omit_arrows", "omit_geography", "omit_analysis_overlays"):
        if not isinstance(result[key], bool):
            raise ValueError(f"export.{key} must be boolean")
    if result["transparent"] and result["format"] not in ("png", "svg"):
        raise ValueError("transparency is supported only for PNG/SVG")
    return result


def make_project(bundle, scene, probe=None, export=None):
    project = {"format": "terra-project", "version": SCHEMA_VERSION,
               "bundle": deepcopy(bundle), "scene": deepcopy(scene)}
    if probe is not None:
        project["probe"] = deepcopy(probe)
    if export is not None:
        project["export"] = validate_export_spec(export)
    return validate_project(project)


def validate_project(project):
    _mapping(project, "project")
    _json_tree(project, "project")
    if project.get("format") != "terra-project" or project.get("version") != SCHEMA_VERSION:
        raise ValueError("unsupported terra-project format/version")
    bundle = validate_bundle(project.get("bundle"))
    validate_scene(project.get("scene"), bundle)
    if "probe" in project:
        validate_probe(project["probe"], bundle)
    if "export" in project:
        validate_export_spec(project["export"])
    return project


def load_project(path):
    return validate_project(_read_json(path))


def save_project(project, path, overwrite=False):
    validate_project(project)
    _write_json(project, path, overwrite)


def _read_json(path, *, max_bytes=None):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError(f"nonfinite JSON constant: {value}")

    if max_bytes is not None:
        bound = _integer(max_bytes, "max_bytes", 1)
        with Path(path).open("rb") as stream:
            raw = stream.read(bound + 1)
        if len(raw) > bound:
            raise ValueError(f"JSON input exceeds {bound} bytes")
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                          parse_constant=invalid_constant)
    with Path(path).open(encoding="utf-8") as stream:
        return json.load(stream, object_pairs_hook=unique_object, parse_constant=invalid_constant)


def _write_json(value, path, overwrite=False):
    """Commit a completed JSON file; an interrupted write never truncates old data."""
    _json_tree(value)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and not overwrite:
        raise FileExistsError(f"output exists: {target}; pass overwrite=True to replace it")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=target.parent, prefix=f".{target.name}.", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        if overwrite:
            os.replace(temporary, target)
        else:
            # A hard link is atomic and fails if a concurrent writer won the
            # target name. Both paths are on the same filesystem.
            os.link(temporary, target)
            temporary.unlink()
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
