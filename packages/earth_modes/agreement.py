"""Checked, same-canonical-model elastic T agreement for stored linear fields.

Comparison normalization never changes the bundle's discrete mass convention.
Agreement is neither a continuum accuracy certificate nor provenance authentication.
Computation and loading do not solve, write files, or import plotting libraries.
"""
from __future__ import annotations

from copy import deepcopy
import heapq
import json
import math

import numpy as np

from .data import (_integer, _json_tree, _mapping, _number, _read_json, _string,
                   canonical_hash, model_hash, validate_bundle)

MAX_PAIRS = 64
MAX_INTERVALS = 200_000
MAX_BUNDLE_BYTES = 64 * 1024**2
MAX_REPORT_BYTES = 160 * 1024**2
ROUNDING = float(64 * np.finfo(float).eps)
INTERPRETATION = ("Same-canonical-model elastic T agreement; reference is a denominator, "
                  "not physical truth. Agreement and mesh change do not certify continuum accuracy.")
_HEADER = dict(schema_version="1.0", metric="toroidal-linear-mass-v1",
               generator="earth_modes.agreement", interpretation=INTERPRETATION)
_NORM_FIELDS = ("reference_continuous_norm", "candidate_continuous_norm")
_MEASURE_FIELDS = ("signed_overlap", "overlap", "shape_distance")


def _bounded_json_size(value, limit, name="JSON"):
    """Check the writer's UTF-8, indent=2, ensure_ascii=False form plus newline.

    Streaming counts avoid building another complete encoded document. Unknown
    metadata counts too. This is a rejection bound, not a peak-memory guarantee.
    Shared with the exporter so sidecar overhead uses the identical byte rule.
    """
    _json_tree(value, name)
    size = 1
    for chunk in json.JSONEncoder(ensure_ascii=False, indent=2, allow_nan=False).iterencode(value):
        size += len(chunk.encode("utf-8"))
        if size > limit:
            raise ValueError(f"{name} exceeds {limit} serialized UTF-8 bytes")
    return size


def _pairs(pairs):
    if not isinstance(pairs, (list, tuple)) or not 1 <= len(pairs) <= MAX_PAIRS:
        raise ValueError(f"pairs must contain 1..{MAX_PAIRS} explicit mode-ID pairs")
    result, seen = [], set()
    for pair in pairs:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError("each pair must contain two mode IDs")
        key = tuple(_string(value, "pair mode ID") for value in pair)
        if key in seen:
            raise ValueError("duplicate explicit pair")
        seen.add(key)
        result.append(list(key))
    return result


def _cheap_preflight(bundle, selected_ids):
    """Reject obvious shape/array budgets before deep validation or copying."""
    _mapping(bundle, "bundle")
    model = _mapping(bundle.get("model"), "bundle.model")
    if not isinstance(model.get("layers"), list) or not isinstance(bundle.get("modes"), list):
        raise ValueError("bundle requires model.layers and modes arrays")
    for mode in bundle["modes"]:
        _mapping(mode, "mode")
        if _string(mode.get("id"), "mode.id") not in selected_ids:
            continue
        if not isinstance(mode.get("regions"), list):
            raise ValueError("mode.regions must be an array")
        for region in mode["regions"]:
            _mapping(region, "region")
            r = region.get("r_m")
            if not isinstance(r, list):
                raise ValueError("region.r_m must be an array")
            # Two exterior endpoints may be tolerated; every interior node is
            # retained. Exact union accounting follows before quadrature.
            if len(r) > MAX_INTERVALS + 3:
                raise ValueError("integration interval budget exceeded by radial samples")
    for layer in model["layers"]:
        _mapping(layer, "layer")
        if not isinstance(layer.get("r_m"), list):
            raise ValueError("layer.r_m must be an array")


def _declarations(bundle, common_hash):
    provenance = bundle["provenance"]
    if "request" in provenance:
        request = _mapping(provenance["request"], "provenance.request")
        if "linear_q" in request:
            if not isinstance(request["linear_q"], bool):
                raise ValueError("provenance.request.linear_q must be Boolean")
            if request["linear_q"]:
                raise ValueError("linear_q=True is ineligible for elastic T agreement")
    if "effective_model" in provenance:
        effective = _mapping(provenance["effective_model"], "provenance.effective_model")
        if "reference" not in effective and "model" not in effective:
            raise ValueError("effective_model requires model or reference='bundle.model'")
        if "reference" in effective and effective["reference"] != "bundle.model":
            raise ValueError("effective_model.reference must be 'bundle.model'")
        if "model" in effective and model_hash(effective["model"]) != common_hash:
            raise ValueError("effective_model model differs from the canonical bundle model")
        if "model_hash" in effective and effective["model_hash"] != common_hash:
            raise ValueError("effective_model.model_hash is stale or inconsistent")
    counts = {}
    if "effective_settings" in provenance:
        settings = _mapping(provenance["effective_settings"], "provenance.effective_settings")
        if "mesh_counts" in settings:
            counts = _mapping(settings["mesh_counts"], "effective_settings.mesh_counts")
            for key, value in counts.items():
                _integer(value, f"mesh_counts.{key}", 1)
    return counts


def _domains(model):
    domains, active = [], []
    for layer in model["layers"]:
        if layer["phase"] == "solid":
            active.append(layer["id"])
        elif active:
            domains.append(active)
            active = []
    if active:
        domains.append(active)
    return domains


def _partition(layer, a, b, remaining):
    lo, hi = layer["r_m"][0], layer["r_m"][-1]
    streams = [(x for x in r if lo < x < hi)
               for r in (layer["r_m"], a["r_m"], b["r_m"])]
    # Merge monotone inputs without allocating a union larger than the budget.
    values = [lo]
    for value in heapq.merge(*streams):
        if value != values[-1]:
            if len(values) >= remaining + 1:
                raise ValueError(f"integration interval budget exceeds {MAX_INTERVALS}")
            values.append(value)
    if len(values) > remaining:
        raise ValueError(f"integration interval budget exceeds {MAX_INTERVALS}")
    values.append(hi)
    return values


def _positive_product(values):
    """Multiply positive factors without overflowing a representable result."""
    mantissa, exponent = 1.0, 0
    for value in values:
        if not math.isfinite(value) or value <= 0:
            raise ValueError("agreement numerical range: nonpositive or nonfinite norm")
        part, power = math.frexp(value)
        mantissa *= part
        mantissa, shift = math.frexp(mantissa)
        exponent += power + shift
    try:
        result = math.ldexp(mantissa, exponent)
    except OverflowError as error:
        raise ValueError("agreement numerical range: unrepresentable norm or scale") from error
    if not math.isfinite(result) or result <= 0:
        raise ValueError("agreement numerical range: unrepresentable norm or scale")
    return result


def _measure(model, layers, modes, partitions):
    radius = model["radius_m"]
    density_scale = max(x for layer in layers for x in layer["rho_kg_m3"])
    amplitudes = [max(abs(w) for region in mode["regions"] for w in region["w"]) for mode in modes]
    if min(amplitudes) <= 0:
        raise ValueError("agreement numerical range: zero comparison norm")
    region_maps = [{r["layer_id"]: r for r in mode["regions"]} for mode in modes]
    samples = []
    gauss_x = np.array([-math.sqrt(3 / 5), 0.0, math.sqrt(3 / 5)])
    gauss_w = np.array([5 / 9, 8 / 9, 5 / 9])
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        for layer, partition in zip(layers, partitions):
            knots = np.asarray(partition, dtype=float)
            half = (knots[1:] - knots[:-1]) / 2
            points = (knots[:-1, None] + half[:, None] * (1 + gauss_x)).ravel()
            rho = np.interp(points, layer["r_m"], np.asarray(layer["rho_kg_m3"]) / density_scale)
            weights = ((half / radius)[:, None] * gauss_w).ravel() * rho * (points / radius)**2
            values, curves = [], []
            for regions, amplitude in zip(region_maps, amplitudes):
                region = regions[layer["id"]]
                w = np.asarray(region["w"], dtype=float) / amplitude
                values.append(np.interp(points, region["r_m"], w))
                curves.append(np.interp(knots, region["r_m"], w))
            samples.append((weights, values, curves))
        norms = [math.fsum(float(x) for weights, values, _ in samples
                           for x in weights * values[i]**2) for i in range(2)]
        continuous = [_positive_product([norm, density_scale, radius, radius, radius, amp, amp])
                      for norm, amp in zip(norms, amplitudes)]
        roots = [math.sqrt(norm) for norm in norms]
        overlap = math.fsum(float(x) for weights, values, _ in samples
                            for x in weights * (values[0] / roots[0]) * (values[1] / roots[1]))
        if not math.isfinite(overlap) or abs(overlap) > 1 + ROUNDING:
            raise ValueError("agreement numerical range: Cauchy-Schwarz overlap violation")
        overlap = max(-1.0, min(1.0, overlap))
        indeterminate = abs(overlap) <= ROUNDING
        sign = 1 if indeterminate or overlap >= 0 else -1
        squared = math.fsum(float(x) for weights, values, _ in samples
                            for x in weights * (values[0] / roots[0] - sign * values[1] / roots[1])**2)
        distance = math.sqrt(squared)
        if not math.isfinite(distance) or distance > math.sqrt(2) + ROUNDING:
            raise ValueError("agreement numerical range: residual distance out of range")
        mass_root = _positive_product([math.sqrt(density_scale), radius, math.sqrt(radius)])
        curves = []
        for layer, partition, (_, _, values) in zip(layers, partitions, samples):
            a = values[0] / roots[0] / mass_root
            b = sign * values[1] / roots[1] / mass_root
            residual = a - b
            if not all(np.all(np.isfinite(value)) for value in (a, b, residual)):
                raise ValueError("agreement numerical range: unrepresentable comparison curve")
            curves.append(dict(layer_id=layer["id"], r_m=list(partition),
                               reference_w=a.tolist(), candidate_w=b.tolist(), residual_w=residual.tolist()))
    return dict(reference_continuous_norm=continuous[0], candidate_continuous_norm=continuous[1],
                signed_overlap=overlap, overlap=abs(overlap), alignment_sign=sign,
                alignment_indeterminate=indeterminate, shape_distance=distance), curves


def _evaluate(reference, candidate, pairs):
    pairs = _pairs(pairs)
    bundles = (reference, candidate)
    for index, bundle in enumerate(bundles):
        _cheap_preflight(bundle, {p[index] for p in pairs})
        _bounded_json_size(bundle, MAX_BUNDLE_BYTES, "bundle")
        validate_bundle(bundle)
    common_hash = model_hash(reference["model"])
    if model_hash(candidate["model"]) != common_hash:
        raise ValueError("agreement requires equal computed canonical model hashes")
    counts = [_declarations(bundle, common_hash) for bundle in bundles]
    model = reference["model"]
    layer_map = {layer["id"]: layer for layer in model["layers"]}
    domains = _domains(model)
    lookups = [{m["id"]: m for m in bundle["modes"]} for bundle in bundles]
    plans, interval_count = [], 0
    for pair in pairs:
        try:
            modes = [lookup[mode_id] for lookup, mode_id in zip(lookups, pair)]
        except KeyError as error:
            raise ValueError(f"unknown explicit mode ID: {error.args[0]}") from error
        if any(m["family"] != "T" or m["q"] is not None for m in modes) or modes[0]["l"] != modes[1]["l"]:
            raise ValueError("agreement requires elastic T modes with equal positive degree and q=null")
        supports = [{r["layer_id"] for r in mode["regions"]} for mode in modes]
        domain = next((d for d in domains if set(d) == supports[0] == supports[1]), None)
        if domain is None:
            raise ValueError("modes require the same complete maximal connected solid support")
        layers = [layer_map[key] for key in domain]
        region_maps = [{r["layer_id"]: r for r in mode["regions"]} for mode in modes]
        partitions = []
        for layer in layers:
            partition = _partition(layer, *(regions[layer["id"]] for regions in region_maps),
                                   MAX_INTERVALS - interval_count)
            interval_count += len(partition) - 1
            partitions.append(partition)
        plans.append((modes, layers, partitions))
    rows, curves = [], []
    try:
        for index, (modes, layers, partitions) in enumerate(plans):
            measures, pair_curves = _measure(model, layers, modes, partitions)
            a, b = modes
            fa, fb = a["frequency_hz"], b["frequency_hz"]
            row = dict(pair_index=index, reference_mode_id=a["id"], candidate_mode_id=b["id"],
                       l=a["l"], reference_n=a["n"], candidate_n=b["n"],
                       radial_label_mismatch=a["n"] != b["n"], layer_ids=[layer["id"] for layer in layers],
                       reference_frequency_hz=fa, candidate_frequency_hz=fb,
                       delta_frequency_hz=fb - fa, relative_frequency_change=(fb - fa) / fa, **measures)
            for role, mode, mesh in zip(("reference", "candidate"), modes, counts):
                region_map = {r["layer_id"]: r for r in mode["regions"]}
                row[role + "_mesh_elements"] = {layer["id"]: mesh.get(layer["id"]) for layer in layers}
                row[role + "_radial_samples"] = {layer["id"]: len(region_map[layer["id"]]["r_m"]) for layer in layers}
            _json_tree(row, "computed row")
            rows.append(row)
            curves.append(pair_curves)
    except (FloatingPointError, OverflowError, ZeroDivisionError) as error:
        raise ValueError("agreement numerical range: unrepresentable metric") from error
    return dict(model_hash=common_hash, pairs=pairs, rows=rows, curves=curves,
                bundle_hashes=[canonical_hash(bundle) for bundle in bundles])


def toroidal_agreement(reference, candidate, pairs):
    """Return a detached checked report for 1..64 explicit unique elastic T pairs.

    Both complete bundles must share a canonical model. Each pair must cover one
    entire common solid component. Unknown provenance stays unknown. Stored W and
    density are reconstructed linearly with material sides and endpoint clamping;
    three-point Gauss integration includes every density and field knot.
    """
    from . import __version__

    result = _evaluate(reference, candidate, pairs)
    report = dict(_HEADER, generator_version=__version__, model_hash=result["model_hash"],
                  pairs=result["pairs"], rows=result["rows"], sources={
                      role: dict(bundle_hash=digest, bundle=bundle)
                      for role, digest, bundle in zip(("reference", "candidate"), result["bundle_hashes"],
                                                      (reference, candidate))})
    _bounded_json_size(report, MAX_REPORT_BYTES, "agreement report")
    return deepcopy(report)


def _check_row_types(row):
    _mapping(row, "agreement row")
    for key in ("pair_index", "l", "reference_n", "candidate_n"):
        _integer(row.get(key), key, 1 if key == "l" else 0)
    if _integer(row.get("alignment_sign"), "alignment_sign", -1) not in (-1, 1):
        raise ValueError("alignment_sign must be -1 or +1")
    for key in ("radial_label_mismatch", "alignment_indeterminate"):
        if not isinstance(row.get(key), bool):
            raise ValueError(f"{key} must be Boolean")
    for key in ("reference_mode_id", "candidate_mode_id"):
        _string(row.get(key), key)
    ids = row.get("layer_ids")
    if not isinstance(ids, list) or not ids or any(not isinstance(x, str) or not x for x in ids):
        raise ValueError("layer_ids must be a nonempty string array")
    for key in ("reference_frequency_hz", "candidate_frequency_hz", *_NORM_FIELDS):
        _number(row.get(key), key, positive=True)
    for key in ("delta_frequency_hz", "relative_frequency_change", *_MEASURE_FIELDS):
        _number(row.get(key), key)
    if not -1 <= row["signed_overlap"] <= 1 or not 0 <= row["overlap"] <= 1:
        raise ValueError("stored overlap is outside its physical range")
    if not 0 <= row["shape_distance"] <= math.sqrt(2) + ROUNDING:
        raise ValueError("stored shape_distance is outside its physical range")
    for role in ("reference", "candidate"):
        for suffix in ("mesh_elements", "radial_samples"):
            mapping = _mapping(row.get(role + "_" + suffix), role + "_" + suffix)
            if set(mapping) != set(ids):
                raise ValueError("row count maps must cover exactly layer_ids")
            for key, value in mapping.items():
                if suffix == "mesh_elements" and value is None:
                    continue
                _integer(value, key, 2 if suffix == "radial_samples" else 1)


def _checked_evaluation(report):
    """Validate a report and return recomputed rows/curves for one export operation.

    Internal consumer boundary: never an 'already validated' bypass. Historical
    report values remain untouched, including tolerated arithmetic differences.
    """
    _mapping(report, "agreement report")
    for key, value in _HEADER.items():
        if report.get(key) != value:
            raise ValueError(f"unsupported agreement {key}")
    _string(report.get("generator_version"), "generator_version")
    pairs = _pairs(report.get("pairs"))
    rows = report.get("rows")
    if not isinstance(rows, list) or len(rows) != len(pairs):
        raise ValueError("agreement rows must match explicit pair count")
    for row in rows:
        _check_row_types(row)
    sources = _mapping(report.get("sources"), "sources")
    for role in ("reference", "candidate"):
        _mapping(sources.get(role), "sources." + role)
    # Cheap source-array checks also precede walking the complete report tree.
    for i, role in enumerate(("reference", "candidate")):
        _cheap_preflight(sources[role].get("bundle"), {p[i] for p in pairs})
    _bounded_json_size(report, MAX_REPORT_BYTES, "agreement report")
    evaluated = _evaluate(sources["reference"]["bundle"], sources["candidate"]["bundle"], pairs)
    if report.get("model_hash") != evaluated["model_hash"]:
        raise ValueError("agreement model_hash mismatch")
    for role, digest in zip(("reference", "candidate"), evaluated["bundle_hashes"]):
        if sources[role].get("bundle_hash") != digest:
            raise ValueError(f"agreement {role} bundle_hash mismatch")
    for stored, expected in zip(rows, evaluated["rows"]):
        for key, value in expected.items():
            actual = stored.get(key)
            if key in _NORM_FIELDS:
                matches = abs(actual - value) <= 1e-12 * abs(value)
            elif key in _MEASURE_FIELDS:
                matches = abs(actual - value) <= ROUNDING + 1e-12 * abs(value)
            else:
                matches = actual == value
            if not matches:
                if key in ("alignment_sign", "alignment_indeterminate"):
                    raise ValueError(f"alignment-threshold consistency error: {key}")
                raise ValueError(f"agreement row {expected['pair_index']} inconsistent {key}")
    return evaluated


def validate_agreement(report):
    """Check structure, full sources and recomputed metrics; return report unchanged."""
    _checked_evaluation(report)
    return report


def load_agreement(path):
    """Read at most 160 MiB+1 bytes of strict JSON, then check all scientific rows."""
    return validate_agreement(_read_json(path, max_bytes=MAX_REPORT_BYTES))


def agreement_curves(report, pair_index):
    """Return material-sided JSON arrays of normalized W and reference-minus-candidate.

    The candidate includes one whole-domain sign. Integer-valued safe JSON numbers
    (including 0.0) are accepted as indices; booleans and fractional values fail.
    """
    index = _integer(pair_index, "pair_index")
    evaluated = _checked_evaluation(report)
    if index >= len(evaluated["pairs"]):
        raise ValueError("pair_index is outside the report")
    return evaluated["curves"][index]


def export_agreement(report, path, *, pair_index=None, width=None, height=None, overwrite=False):
    """Lazily dispatch checked JSON/CSV/native SVG/PNG export to the I/O module."""
    from .agreement_export import export_agreement as export

    return export(report, path, pair_index=pair_index, width=width, height=height, overwrite=overwrite)
