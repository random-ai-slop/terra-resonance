"""Independent stored-field integrals and strict agreement report boundaries."""
from copy import deepcopy
from fractions import Fraction
import json
import math
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

from earth_modes import agreement
from earth_modes.agreement import (agreement_curves, load_agreement, toroidal_agreement,
                                   validate_agreement)
from earth_modes.data import (_read_json, bundle_hash, mass_integral, model_hash,
                              validate_bundle)
from earth_modes.models import homogeneous_model


def material(identity, radii, rho, phase="solid"):
    return dict(id=identity, name=identity, phase=phase, r_m=list(radii),
                rho_kg_m3=list(rho), vp_m_s=[2.] * len(radii),
                vs_m_s=[1. if phase == "solid" else 0.] * len(radii))


def model(layers=None):
    result = homogeneous_model(1., 1., 2., 1.)
    if layers is not None:
        result["layers"] = layers
    return result


def bundle(material_model=None, shapes=None, *, identity="a", n=0, frequency=.001):
    material_model = model() if material_model is None else material_model
    shapes = [("sphere", [0., 1.], [0., 1.])] if shapes is None else shapes
    mode = dict(id=identity, family="T", l=2, n=n, frequency_hz=frequency, q=None,
                normalization="mass_integral_1", provenance=dict(
                    fixture="Manufactured linear field; not a solved eigenmode",
                    quality=dict(status="unverified", mesh_convergence=None, benchmark=None, warnings=[])),
                regions=[dict(layer_id=key, r_m=list(r), w=list(w), u=[0.] * len(r), v=[0.] * len(r))
                         for key, r, w in shapes])
    norm = mass_integral(material_model, mode)
    for region in mode["regions"]:
        region["w"] = (np.asarray(region["w"]) / math.sqrt(norm)).tolist()
    result = dict(schema_version="1.0", model=deepcopy(material_model), modes=[mode], provenance={})
    return validate_bundle(result)


def compare(a, b):
    return toroidal_agreement(a, b, [(a["modes"][0]["id"], b["modes"][0]["id"])])


def test_same_linear_shape_different_canonical_factors_and_global_reversal():
    a = bundle()
    b = bundle(shapes=[("sphere", [0., .5, 1.], [0., .5, 1.])], identity="b")
    before = [bundle_hash(x) for x in (a, b)]
    report = compare(a, b)
    row = report["rows"][0]
    assert row["reference_continuous_norm"] == pytest.approx((1 / 5) / (1 / 2), rel=2e-15)
    assert row["candidate_continuous_norm"] == pytest.approx((1 / 5) / (9 / 32), rel=2e-15)
    assert row["overlap"] == pytest.approx(1, abs=2e-15)
    assert row["shape_distance"] < 4e-16
    b["modes"][0]["regions"][0]["w"] = [-w for w in b["modes"][0]["regions"][0]["w"]]
    reversed_report = compare(a, b)
    assert reversed_report["rows"][0]["alignment_sign"] == -1
    assert reversed_report["rows"][0]["signed_overlap"] == pytest.approx(-1)
    assert reversed_report["rows"][0]["shape_distance"] < 4e-16
    assert bundle_hash(a) == before[0]
    assert bundle_hash(report["sources"]["candidate"]["bundle"]) == before[1]
    report["sources"]["reference"]["bundle"]["model"]["name"] = "detached"
    assert a["model"]["name"] != "detached"
    b["modes"][0]["regions"][0]["w"] = [2 * w for w in b["modes"][0]["regions"][0]["w"]]
    with pytest.raises(ValueError, match="mass integral"):
        compare(a, b)


def test_density_knot_rational_antiderivative_oracle():
    m = model([material("sphere", [0., 1 / 3, 1.], [1., 9., 1.])])
    a = bundle(m)
    b = bundle(m, [("sphere", [0., .5, 1.], [0., .25, 1.])], identity="b")
    row = compare(a, b)["rows"][0]
    aa, bb, ab = map(float, (Fraction(727, 1215), Fraction(64007, 155520), Fraction(75931, 155520)))
    expected_c = ab / math.sqrt(aa * bb)
    assert row["signed_overlap"] == pytest.approx(expected_c, abs=3e-15)
    assert row["shape_distance"] == pytest.approx(.17966775814299688, abs=3e-15)
    curves = agreement_curves(compare(a, b), 0.)
    assert curves[0]["r_m"] == [0., 1 / 3, .5, 1.]
    assert curves[0]["residual_w"] == pytest.approx(np.subtract(curves[0]["reference_w"], curves[0]["candidate_w"]))


def sign_fixture():
    m = model([material("inner", [0., .5], [91 / 11] * 2), material("outer", [.5, 1.], [1.] * 2)])
    shapes = [("inner", [0., .25, .5], [0., 1., 0.]), ("outer", [.5, .75, 1.], [0., 1., 0.])]
    a = bundle(m, shapes)
    b = bundle(m, [shapes[0], ("outer", [.5, .75, 1.], [0., -1., 0.])], identity="b", n=1)
    return a, b


def test_one_sign_across_density_interface_and_explicit_n_mismatch():
    a, b = sign_fixture()
    report = compare(a, b)
    row = report["rows"][0]
    assert abs(row["signed_overlap"]) <= agreement.ROUNDING
    assert row["alignment_indeterminate"] is True
    assert row["alignment_sign"] == 1
    assert row["shape_distance"] == pytest.approx(math.sqrt(2), abs=3e-15)
    assert row["radial_label_mismatch"] is True
    curves = agreement_curves(report, 0)
    assert [c["layer_id"] for c in curves] == ["inner", "outer"]
    assert curves[0]["r_m"][-1] == curves[1]["r_m"][0] == .5
    assert curves[1]["candidate_w"][1] < 0
    # Stored order and forged provenance labels do not control integration order.
    b["modes"][0]["regions"].reverse()
    b["modes"][0]["provenance"]["solid_domain_id"] = "invented"
    assert compare(a, b)["rows"][0] == row


def test_matching_partial_support_and_different_domains_rejected():
    a, _ = sign_fixture()
    partial = bundle(a["model"], [("inner", [0., .25, .5], [0., 1., 0.])])
    with pytest.raises(ValueError, match="complete maximal connected"):
        compare(partial, partial)
    m = model([material("inner", [0., .2], [1.] * 2), material("fluid", [.2, .4], [1.] * 2, "fluid"),
               material("outer", [.4, 1.], [1.] * 2)])
    inner = bundle(m, [("inner", [0., .2], [0., 1.])])
    outer = bundle(m, [("outer", [.4, 1.], [0., 1.])])
    for item in (inner, outer):
        item["modes"][0]["provenance"]["solid_domain_id"] = "forged-equal"
    with pytest.raises(ValueError, match="complete maximal connected"):
        compare(inner, outer)
    spanning = bundle(m, [("inner", [0., .2], [0., 1.]), ("outer", [.4, 1.], [0., 1.])])
    with pytest.raises(ValueError, match="complete maximal connected"):
        compare(spanning, spanning)


def test_tiny_residual_against_extended_precision_polynomial_oracle():
    a = bundle(shapes=[("sphere", [0., .5, 1.], [0., .5, 1.])])
    b = bundle(shapes=[("sphere", [0., .5, 1.], [0., .5 + 1e-9, 1.])], identity="b", frequency=.001 + 4e-15)
    report = compare(a, b)
    row = report["rows"][0]
    # Independent closed-form moment matrices integrate r^2*(p+q*r)^2.
    dtype = np.longdouble
    nodes = [dtype(0), dtype(.5), dtype(1)]
    def coefficients(values):
        return [(dtype(values[i]) - (dtype(values[i+1])-dtype(values[i]))/(nodes[i+1]-nodes[i])*nodes[i],
                 (dtype(values[i+1])-dtype(values[i]))/(nodes[i+1]-nodes[i])) for i in range(2)]
    def integral(coeffs):
        return sum(p*p*(hi**3-lo**3)/3 + 2*p*q*(hi**4-lo**4)/4 + q*q*(hi**5-lo**5)/5
                   for (p,q),lo,hi in zip(coeffs,nodes,nodes[1:]))
    ca = coefficients(a["modes"][0]["regions"][0]["w"])
    cb = coefficients(b["modes"][0]["regions"][0]["w"])
    na, nb = np.sqrt(integral(ca)), np.sqrt(integral(cb))
    residual = [(pa/na-pb/nb, qa/na-qb/nb) for (pa,qa),(pb,qb) in zip(ca,cb)]
    expected = float(np.sqrt(integral(residual)))
    assert row["shape_distance"] > 1e-10
    assert row["shape_distance"] == pytest.approx(expected, rel=1e-6)
    assert row["delta_frequency_hz"] == b["modes"][0]["frequency_hz"] - .001 != 0
    tampered = deepcopy(report)
    tampered["rows"][0]["delta_frequency_hz"] = 0.
    with pytest.raises(ValueError, match="delta_frequency_hz"):
        validate_agreement(tampered)


@pytest.mark.parametrize("offset", [-8 * np.finfo(float).eps, 8 * np.finfo(float).eps])
def test_boundary_offsets_keep_original_nodes_and_clamped_tails(offset):
    a = bundle()
    b = bundle(shapes=[("sphere", [0., 1. + offset], [0., 1.])], identity="b")
    before = [bundle_hash(x) for x in (a, b)]
    report = compare(a, b)
    curves = agreement_curves(report, 0)[0]
    assert curves["r_m"][-1] == 1.
    assert (1. + offset in curves["r_m"]) == (offset < 0)
    # Exact continuous integral of the supplied line and its constant short tail.
    endpoint = 1. + offset
    raw_integral = endpoint**3/5 + (1-endpoint**3)/3 if offset < 0 else 1/(5*endpoint**2)
    canonical_factor = b["modes"][0]["regions"][0]["w"][-1]**2
    assert report["rows"][0]["candidate_continuous_norm"] == pytest.approx(raw_integral*canonical_factor, rel=3e-15)
    assert [bundle_hash(x) for x in (a, b)] == before
    bad = deepcopy(b)
    bad["modes"][0]["regions"][0]["r_m"][-1] = 1 + 128*np.finfo(float).eps
    with pytest.raises(ValueError, match="span"):
        compare(a, bad)


@pytest.mark.parametrize("declaration", [{"reference":"bundle.model"}, {"model":"MODEL"},
                                         {"reference":"bundle.model","model":"MODEL","model_hash":"HASH"}, None])
def test_supported_effective_model_shapes_and_unknown_provenance(declaration):
    a, b = bundle(), bundle(identity="b")
    if declaration is not None:
        declaration = deepcopy(declaration)
        if "model" in declaration:
            declaration["model"] = deepcopy(b["model"])
        if "model_hash" in declaration:
            declaration["model_hash"] = model_hash(b["model"])
        b["provenance"]["effective_model"] = declaration
    b["provenance"]["request"] = {"linear_q": False, "unknown":"保持原样"}
    assert validate_agreement(compare(a,b))


@pytest.mark.parametrize("provenance", [
    {"request":{"linear_q":True}}, {"request":{"linear_q":1}},
    {"effective_model":None}, {"effective_model":{}}, {"effective_model":{"model_hash":"stale"}},
    {"effective_model":{"reference":"elsewhere"}},
    {"effective_model":{"reference":"bundle.model","model_hash":"stale"}},
])
def test_malformed_known_declarations_rejected(provenance):
    a, b = bundle(), bundle()
    b["provenance"] = provenance
    with pytest.raises(ValueError, match="linear_q|effective_model"):
        compare(a,b)


def test_conflicting_effective_model_and_complete_unselected_bundle_validation():
    a, b = bundle(), bundle()
    different = deepcopy(b["model"])
    different["name"] = "different canonical model"
    b["provenance"]["effective_model"] = {"model":different, "model_hash":model_hash(b["model"])}
    with pytest.raises(ValueError, match="effective_model model differs"):
        compare(a,b)
    b = bundle()
    unselected = deepcopy(b["modes"][0])
    unselected.update(id="unselected", frequency_hz=-1)
    b["modes"].append(unselected)
    with pytest.raises(ValueError, match="frequency_hz"):
        compare(a,b)


@pytest.mark.parametrize("key,value", [("shape_distance",-1e-15), ("overlap",1+1e-13),
    ("signed_overlap",-1-1e-13), ("shape_distance",False), ("pair_index",False),
    ("alignment_sign",True), ("alignment_indeterminate",0), ("l",2.5),
    ("reference_continuous_norm",0), ("candidate_frequency_hz",float("nan")),
    ("reference_continuous_norm",float("inf")), ("overlap",.5),
    ("alignment_sign",-1), ("alignment_indeterminate",True)])
def test_tampered_types_ranges_and_recomputed_rows(key,value):
    report = compare(bundle(),bundle())
    report["rows"][0][key] = value
    with pytest.raises(ValueError):
        validate_agreement(report)


def test_report_reload_extensions_hashes_and_recomputed_curve_authority(tmp_path):
    report = compare(bundle(), bundle())
    report["generator_version"] = "historical-version"
    report["extension"] = {"note":"用户原文"}
    report["export_production"] = {"renderer":"another historical renderer"}
    report["rows"][0]["pair_index"] = 0.
    report["rows"][0]["extra"] = ["preserve"]
    curves = agreement_curves(report,0)
    report["rows"][0]["reference_continuous_norm"] *= 1+5e-13
    assert validate_agreement(report) is report
    assert agreement_curves(report,0) == curves
    path = tmp_path / "received.svg.json"
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    assert load_agreement(path) == report
    for path_keys in [("model_hash",), ("sources","reference","bundle_hash")]:
        bad = deepcopy(report)
        target = bad
        for key in path_keys[:-1]: target=target[key]
        target[path_keys[-1]] = "0"*64
        with pytest.raises(ValueError,match="hash mismatch"):
            validate_agreement(bad)
    bad=deepcopy(report)
    bad["sources"]["candidate"]["bundle"]["provenance"]["changed"] = True
    with pytest.raises(ValueError,match="bundle_hash mismatch"):
        validate_agreement(bad)


@pytest.mark.parametrize("pair_index", [True,-1,.5,2**53,1,"0",None])
def test_curve_indices_are_strict_safe_wire_integers(pair_index):
    with pytest.raises(ValueError,match="pair_index"):
        agreement_curves(compare(bundle(),bundle()),pair_index)


def test_mesh_counts_are_declared_not_inferred():
    a,b = bundle(),bundle()
    b["provenance"]["effective_settings"] = {"mesh_counts":{"sphere":4.}}
    row=compare(a,b)["rows"][0]
    assert row["reference_mesh_elements"] == {"sphere":None}
    assert row["candidate_mesh_elements"] == {"sphere":4.}
    assert row["reference_radial_samples"] == {"sphere":2}
    for bad_count in [0,-1,True,2.5,None,"4"]:
        b["provenance"]["effective_settings"]["mesh_counts"]["sphere"] = bad_count
        with pytest.raises(ValueError,match="mesh_counts"):
            compare(a,b)


@pytest.mark.parametrize("pairs", [[], [["a","a"]]*2, [["missing","a"]], [["a"]], [[True,"a"]], [["a","a"]]*65])
def test_pair_shape_budget_and_selection(pairs):
    with pytest.raises(ValueError):
        toroidal_agreement(bundle(),bundle(),pairs)


def test_resource_limits_before_cloning_quadrature_and_exact_repeated_accounting(monkeypatch):
    a,b = bundle(),bundle()
    def forbidden(*args,**kwargs):
        raise AssertionError("must reject before quadrature or cloning")
    monkeypatch.setattr(agreement,"_measure",forbidden)
    monkeypatch.setattr(agreement,"deepcopy",forbidden)
    monkeypatch.setattr(agreement,"MAX_INTERVALS",1)
    # Each distinct pair uses the same field, and counts its interval again.
    b["modes"].append(deepcopy(b["modes"][0]))
    b["modes"][1]["id"]="b2"
    with pytest.raises(ValueError,match="interval budget"):
        toroidal_agreement(a,b,[["a","a"],["a","b2"]])
    monkeypatch.setattr(agreement,"MAX_BUNDLE_BYTES",10)
    with pytest.raises(ValueError,match="serialized UTF-8"):
        compare(a,a)


def test_exact_serialization_bounds_include_unicode_unknown_metadata(monkeypatch):
    a=bundle()
    a["provenance"]["note"]="界"*20
    size=len((json.dumps(a,ensure_ascii=False,indent=2)+"\n").encode("utf-8"))
    assert agreement._bounded_json_size(a,size)==size
    with pytest.raises(ValueError,match="serialized UTF-8"):
        agreement._bounded_json_size(a,size-1)
    monkeypatch.setattr(agreement,"MAX_BUNDLE_BYTES",size)
    report=compare(a,a)
    monkeypatch.setattr(agreement,"MAX_REPORT_BYTES",len((json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode())-1)
    with pytest.raises(ValueError,match="report exceeds"):
        compare(a,a)
    with pytest.raises(ValueError,match="report exceeds"):
        validate_agreement(report)


@pytest.mark.parametrize("raw", ['{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}'])
def test_strict_duplicate_and_nonfinite_json(tmp_path,raw):
    path=tmp_path/"bad.json"
    path.write_text(raw)
    with pytest.raises(ValueError,match="duplicate|nonfinite"):
        load_agreement(path)


def test_reader_bound_counts_bytes_and_preserves_unbounded_default(tmp_path):
    path=tmp_path/"value.json"
    path.write_bytes('{"name":"界"}'.encode())
    size=len(path.read_bytes())
    assert _read_json(path)==_read_json(path,max_bytes=size)=={"name":"界"}
    with pytest.raises(ValueError,match="exceeds"):
        _read_json(path,max_bytes=size-1)


def test_no_plotting_imports_in_fresh_process():
    code="import sys; import earth_modes.agreement; assert not any(x in sys.modules for x in ('matplotlib','earth_modes.experimental.toroidal','earth_modes.agreement_export'))"
    subprocess.run([sys.executable,"-c",code],check=True)


def test_existing_broad_comparison_still_retains_supplied_sign_and_different_models():
    from earth_modes.analysis import compare_bundles
    a,b=bundle(),bundle()
    b["model"]["name"]="another model"
    b["modes"][0]["regions"][0]["w"] = [-w for w in b["modes"][0]["regions"][0]["w"]]
    result=compare_bundles(a,b,[["a","a"]])
    assert result["curves"][1]["regions"][0]["w"][-1] < 0
    with pytest.raises(ValueError,match="canonical model hashes"):
        compare(a,b)


def test_real_two_solver_pair_with_actual_counts():
    from earth_modes.experimental import solve_toroidal
    from earth_modes.solver import solve
    m=homogeneous_model(1e6,4000,8000,4000)
    a=solve(m,families=("T",),l_min=2,l_max=2,frequency_min_hz=1e-8,frequency_max_hz=.002,mesh_size=20,gravity=0,n_max=0)
    b=solve_toroidal(m,l_min=2,l_max=2,frequency_min_hz=1e-8,frequency_max_hz=.002,mesh_size=20)
    report=compare(a,b)
    row=report["rows"][0]
    assert abs(row["relative_frequency_change"]) < 1e-4
    assert row["shape_distance"] < .003
    assert row["reference_mesh_elements"] == row["candidate_mesh_elements"] == {"sphere":20}
    assert validate_agreement(report) is report


@pytest.mark.parametrize("identity", [[], {}, True, None, ""])
def test_invalid_source_id_fails_as_value_error(identity):
    a, b = bundle(), bundle()
    b["modes"][0]["id"] = identity
    with pytest.raises(ValueError, match="mode.id"):
        toroidal_agreement(a, b, [["a", "a"]])


@pytest.mark.parametrize("change", ["q", "degree", "family", "zero", "nonfinite"])
def test_ineligible_or_invalid_fields_fail_without_output(change):
    a, b = bundle(), bundle()
    mode = b["modes"][0]
    if change == "q":
        mode["q"] = 100.
    elif change == "degree":
        mode["l"] = 3
    elif change == "family":
        mode["family"] = "S"
        mode["regions"][0]["v"] = mode["regions"][0]["w"]
        mode["regions"][0]["w"] = [0., 0.]
    elif change == "zero":
        mode["regions"][0]["w"] = [0., 0.]
    else:
        mode["regions"][0]["w"][-1] = float("inf")
    with pytest.raises(ValueError):
        compare(a, b)


def test_budget_accepts_exact_union_and_rejects_density_only_excess(monkeypatch):
    m = model([material("sphere", [0., .25, .5, .75, 1.], [1.] * 5)])
    a = bundle(m)
    monkeypatch.setattr(agreement, "MAX_INTERVALS", 4)
    assert compare(a, a)["rows"][0]["shape_distance"] == 0.
    monkeypatch.setattr(agreement, "MAX_INTERVALS", 3)
    with pytest.raises(ValueError, match="interval budget"):
        compare(a, a)


def test_alignment_threshold_disagreement_has_specific_error():
    report = compare(*sign_fixture())
    report["rows"][0]["alignment_sign"] = -1
    with pytest.raises(ValueError, match="alignment-threshold consistency"):
        validate_agreement(report)


def test_public_schema_required_fields_and_embedded_reference_resolve():
    from importlib.resources import files
    directory = files("earth_modes").joinpath("assets/schema")
    schema = json.loads(directory.joinpath("agreement.schema.json").read_text())
    report = compare(bundle(), bundle())
    assert set(schema["required"]) == set(report)
    assert set(schema["properties"]["rows"]["items"]["required"]) == set(report["rows"][0])
    for role in ("reference", "candidate"):
        reference = schema["properties"]["sources"]["properties"][role]["properties"]["bundle"]["$ref"]
        assert json.loads(directory.joinpath(reference).read_text())["title"] == "ModeBundle 1.0"
