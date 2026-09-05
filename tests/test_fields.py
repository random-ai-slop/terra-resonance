"""Independent low-order identities and the field's important physical edges."""
from copy import deepcopy
import math

import numpy as np
import pytest

from earth_modes.data import default_scene, validate_bundle
from earth_modes.fields import evaluate_field, mode_scale, real_harmonic, sample_probe
from earth_modes.models import homogeneous_model


def field_bundle():
    """Analytic field fixtures, explicitly not eigenmodes of an elastic sphere.

    For rho=2 and r=[0,1,2], trapezoidal ∫rho*r^4 dr=18 and
    ∫3*rho*r² dr=18, so the norms below are independently known.
    """
    root18 = math.sqrt(18)
    quality = {"status": "unverified", "mesh_convergence": None, "benchmark": None,
               "warnings": ["Analytic field test fixture; not a solved planetary eigenmode."]}
    model = homogeneous_model(radius_m=2.0, rho_kg_m3=2.0, vp_m_s=4.0, vs_m_s=2.0)
    modes = []
    for name, family, degree, u, v, w in (
        ("dipole", "S", 1, [1, 1, 1], [math.sqrt(2)] * 3, [0, 0, 0]),
        ("radial", "R", 0, [0, 1, 2], [0, 0, 0], [0, 0, 0]),
        ("toroidal", "T", 1, [0, 0, 0], [0, 0, 0], [0, 1, 2]),
        ("quadrupole", "S", 2, [0, 1, 2], [0, 0, 0], [0, 0, 0]),
    ):
        modes.append({"id": name, "family": family, "n": 1, "l": degree,
                      "frequency_hz": 0.125, "q": None, "normalization": "mass_integral_1",
                      "regions": [{"layer_id": "sphere", "r_m": [0.0, 1.0, 2.0],
                                   "u": [x / root18 for x in u], "v": [x / root18 for x in v],
                                   "w": [x / root18 for x in w]}],
                      "provenance": {"kind": "analytic_field_fixture", "quality": deepcopy(quality)}})
    return validate_bundle({"schema_version": "1.0", "model": model, "modes": modes,
                            "provenance": {"purpose": "Independent field identities; not solved eigenfrequencies"}})


def interface_bundle():
    """Toroidal support stops at a fluid interface; no interpolation through it."""
    bundle = field_bundle()
    bundle["model"] = {"id": "interface", "name": "Solid and fluid fixture", "radius_m": 2.0,
                       "layers": [{"id": "solid", "name": "Solid", "phase": "solid", "r_m": [0.0, 1.0],
                                   "rho_kg_m3": [2.0, 2.0], "vp_m_s": [4.0, 4.0], "vs_m_s": [2.0, 2.0]},
                                  {"id": "fluid", "name": "Fluid", "phase": "fluid", "r_m": [1.0, 2.0],
                                   "rho_kg_m3": [1.0, 1.0], "vp_m_s": [3.0, 3.0], "vs_m_s": [0.0, 0.0]}]}
    mode = deepcopy(bundle["modes"][2])
    mode["regions"] = [{"layer_id": "solid", "r_m": [0.0, 1.0], "u": [0.0, 0.0], "v": [0.0, 0.0], "w": [0.0, 1.0]}]
    mode["provenance"]["solid_domain_id"] = "solid-0"
    bundle["modes"] = [mode]
    return validate_bundle(bundle)


def term(mode_id, m=0, amplitude=1.0, phase=0.0):
    return {"mode_id": mode_id, "m": m, "amplitude": amplitude, "phase_rad": phase}


def test_harmonic_low_order_poles_and_orthonormality():
    theta = np.array([0.0, 0.3, 1.2, math.pi])
    phi = np.array([0.1, 0.4, 2.3, 0.9])
    a = math.sqrt(3 / (4 * math.pi))
    for m in (1, -1):
        trig = np.cos(phi) if m == 1 else np.sin(phi)
        other = np.sin(phi) if m == 1 else -np.cos(phi)
        y, yt, yp = real_harmonic(1, m, theta, phi)
        np.testing.assert_allclose(y, -a * np.sin(theta) * trig, atol=2e-15)
        np.testing.assert_allclose(yt, -a * np.cos(theta) * trig, atol=2e-15)
        np.testing.assert_allclose(yp, a * other, atol=2e-15)
    # Gauss-Legendre integration in cos(theta) and a uniform periodic azimuth
    # independently checks orthonormality, not implementation recursion.
    x, weights = np.polynomial.legendre.leggauss(24)
    azimuth = np.arange(64) * 2 * math.pi / 64
    values = [real_harmonic(l, m, np.arccos(x[:, None]), azimuth[None, :])[0]
              for l, m in ((0, 0), (1, -1), (2, 0), (3, 2), (5, -4))]
    gram = np.array([[np.sum(a * b * weights[:, None]) * 2 * math.pi / 64 for b in values] for a in values])
    np.testing.assert_allclose(gram, np.eye(len(values)), atol=1e-13)
    for l in (2, 32, 64):
        assert all(np.all(np.isfinite(x)) for x in real_harmonic(l, 1, theta, phi))


def test_dipole_cartesian_field_including_exact_center():
    bundle = field_bundle()
    points = np.array([[0, 0, 0], [0, 0, 2], [0, 0, -2], [2, 0, 0], [0.3, 0.4, 0.5], [1e-8, -2e-8, 3e-8]])
    a = math.sqrt(3 / (4 * math.pi)) / math.sqrt(18)
    for m, direction in ((0, [0, 0, 1]), (1, [-1, 0, 0]), (-1, [0, -1, 0])):
        expected = np.tile(a * np.array(direction), (len(points), 1))
        raw = evaluate_field(bundle, [term("dipole", m)], points, 0, normalized=False)
        np.testing.assert_allclose(raw, expected, atol=1e-15)
        illustrated = evaluate_field(bundle, [term("dipole", m)], points, 0)
        np.testing.assert_allclose(illustrated * mode_scale(bundle["modes"][0]), expected, atol=1e-15)


def test_radial_toroidal_center_and_vector_invariants():
    bundle = field_bundle()
    points = np.array([[1.0, 0.2, 0.5], [0, 0, 2], [0, 0, -2], [0, 0, 0]])
    radial = evaluate_field(bundle, [term("radial")], points, 0, normalized=False)
    np.testing.assert_allclose(radial, points / math.sqrt(18 * 4 * math.pi), atol=1e-15)
    for m in (-1, 0, 1):
        toroidal = evaluate_field(bundle, [term("toroidal", m)], points, 0)
        np.testing.assert_allclose(np.sum(toroidal * points, axis=1), 0, atol=1e-15)
        np.testing.assert_array_equal(toroidal[-1], [0, 0, 0])


def test_interface_sides_missing_support_and_roundoff():
    bundle = interface_bundle()
    points = np.array([[1.0, 0, 0], [1 - 1e-10, 0, 0], [1 + 1e-10, 0, 0], [2.1, 0, 0]])
    default = evaluate_field(bundle, [term("toroidal")], points, 0)
    assert np.linalg.norm(default[1]) > 0
    np.testing.assert_array_equal(default[[0, 2, 3]], np.zeros((3, 3)))
    explicit = evaluate_field(bundle, [term("toroidal")], points[:1], 0, layer_id="solid")
    assert np.linalg.norm(explicit[0]) > 0
    # A representational perturbation is snapped to the outer side, while
    # physically separated points above remain on their respective sides.
    near = evaluate_field(bundle, [term("toroidal")], [[np.nextafter(1.0, 0), 0, 0]], 0)
    np.testing.assert_array_equal(near, [[0, 0, 0]])
    raw_probe = sample_probe(bundle, {"terms": [term("toroidal")]}, 0, 0, 0.5, [0, 1], normalized=False, layer_id="solid")
    np.testing.assert_allclose(raw_probe[0], explicit[0], atol=1e-15)
    with pytest.raises(ValueError, match="layer"):
        sample_probe(bundle, {"terms": [term("toroidal")]}, 0, 0, 0.8, [0], layer_id="solid")
    # Planet surface stays populated despite norm rounding beyond R.
    sphere = field_bundle()
    field = evaluate_field(sphere, [term("radial")], [[np.nextafter(2.0, math.inf), 0, 0]], 0)
    assert np.linalg.norm(field) > 0


def test_q_time_derivatives_probe_and_superposition():
    bundle = field_bundle()
    bundle["modes"][1]["q"] = 7.0
    mode = bundle["modes"][1]
    scene = default_scene(bundle)
    scene["terms"] = [term("radial", amplitude=1.3, phase=0.7)]
    times = np.array([0.0, 1.25, 9.0, 30.0])
    omega = 2 * math.pi * mode["frequency_hz"]
    gamma = math.pi * mode["frequency_hz"] / mode["q"]
    angle = omega * times + 0.7
    envelope = 1.3 * np.exp(-gamma * times)
    multipliers = [envelope * np.cos(angle), envelope * (-omega * np.sin(angle) - gamma * np.cos(angle)),
                   envelope * ((gamma**2 - omega**2) * np.cos(angle) + 2 * gamma * omega * np.sin(angle))]
    spatial = 2 / math.sqrt(18 * 4 * math.pi)
    for derivative in (0, 1, 2):
        probe = sample_probe(bundle, scene, 0, 0, 1, times, derivative=derivative, normalized=False)
        np.testing.assert_allclose(probe[:, 0], spatial * multipliers[derivative], atol=2e-15)
        np.testing.assert_allclose(probe[:, 1:], 0, atol=2e-15)
        for i, time in enumerate(times):
            np.testing.assert_allclose(evaluate_field(bundle, scene["terms"], [[2, 0, 0]], time, derivative, False)[0], probe[i], atol=1e-15)
    terms = [term("dipole", 1, phase=0.2), term("toroidal", -1, amplitude=-0.7)]
    points = [[1, 0.1, 0.3], [0, 0, -2]]
    combined = evaluate_field(bundle, terms, points, 3)
    np.testing.assert_allclose(combined, sum(evaluate_field(bundle, [t], points, 3) for t in terms), atol=1e-15)
