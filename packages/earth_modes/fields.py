"""Canonical vector spherical harmonics and deterministic modal time evolution."""
from __future__ import annotations

import numpy as np
from scipy.special import sph_harm_y

from .data import MAX_VISUAL_DEGREE, boundary_tolerance, validate_terms, validate_material_point, _integer


def real_harmonic(l, m, theta, phi):
    """Return orthonormal real Y, dθY, and (dφY)/sinθ.

    Complex harmonics include Condon–Shortley phase. Positive m uses the
    cosine branch, negative m the sine branch. At the poles the directional
    derivatives are the continuous limit for the supplied longitude.
    """
    if isinstance(l, bool) or not isinstance(l, (int, np.integer)) or not 0 <= l <= MAX_VISUAL_DEGREE:
        raise ValueError(f"harmonic degree must be an integer in [0, {MAX_VISUAL_DEGREE}]")
    if isinstance(m, bool) or not isinstance(m, (int, np.integer)) or abs(m) > l:
        raise ValueError("harmonic order must satisfy |m| <= l")
    theta, phi = np.broadcast_arrays(np.asarray(theta, dtype=float), np.asarray(phi, dtype=float))
    if not np.all(np.isfinite(theta)) or not np.all(np.isfinite(phi)) or np.any((theta < 0) | (theta > np.pi)):
        raise ValueError("angles must be finite, with colatitude in [0, pi]")
    harmonic, gradient = sph_harm_y(l, abs(m), theta, phi, diff_n=1)
    # Dividing dφY by sinθ directly is undefined at the poles. The m=1
    # analytic limit is related to dθY; all other m have zero limit.
    sine = np.sin(theta)
    at_pole = np.abs(sine) < 1e-10
    azimuthal = np.divide(gradient[..., 1], sine, out=np.zeros_like(harmonic), where=~at_pole)
    if abs(m) == 1:
        limit = 1j * gradient[..., 0] * np.where(theta < np.pi / 2, 1.0, -1.0)
        azimuthal = np.where(at_pole, limit, azimuthal)
    component = np.imag if m < 0 else np.real
    factor = np.sqrt(2.0) if m else 1.0
    return tuple(factor * component(value) for value in (harmonic, gradient[..., 0], azimuthal))


def mode_scale(mode) -> float:
    """One fixed radial coefficient norm for illustration; never frame dependent."""
    maximum = max((float(np.max(np.sqrt(np.asarray(region["u"]) ** 2 + np.asarray(region["v"]) ** 2 + np.asarray(region["w"]) ** 2))) for region in mode["regions"]), default=0.0)
    if not np.isfinite(maximum) or maximum <= 0:
        raise ValueError("a mode must have finite nonzero displacement coefficients")
    return maximum


def _spatial_mode(bundle, mode, points, m, normalized, layer_id):
    radius = np.hypot(np.hypot(points[:, 0], points[:, 1]), points[:, 2])
    # atan2 retains the tiny colatitude of points close to a pole, unlike
    # arccos(z/r), which rounds to zero and loses transverse direction.
    theta = np.arctan2(np.hypot(points[:, 0], points[:, 1]), points[:, 2])
    phi = np.arctan2(points[:, 1], points[:, 0])
    layers = bundle["model"]["layers"]
    tolerance = boundary_tolerance(bundle["model"]["radius_m"])
    boundaries = sorted({float(r) for layer in layers for r in (layer["r_m"][0], layer["r_m"][-1])})
    for boundary in boundaries:
        radius[np.abs(radius - boundary) <= tolerance] = boundary
    sin_t, cos_t, sin_p, cos_p = np.sin(theta), np.cos(theta), np.sin(phi), np.cos(phi)
    er = np.column_stack((sin_t * cos_p, sin_t * sin_p, cos_t))
    et = np.column_stack((cos_t * cos_p, cos_t * sin_p, -sin_t))
    ep = np.column_stack((-sin_p, cos_p, np.zeros_like(phi)))
    y, yt, yp = real_harmonic(_integer(mode["l"], "mode.l"), int(m), theta, phi)
    radial = np.zeros((len(points), 3))
    regions = {region["layer_id"]: region for region in mode["regions"]}
    if layer_id is not None and layer_id not in {layer["id"] for layer in layers}:
        raise ValueError(f"unknown layer_id: {layer_id}")
    # Assignment by material layer (not by available mode regions) gives the
    # outer side even when that side has zero support for a toroidal mode.
    for index, layer in enumerate(layers):
        if layer_id is not None and layer["id"] != layer_id:
            continue
        lower, upper = layer["r_m"][0], layer["r_m"][-1]
        mask = (radius >= lower) & (radius <= upper if layer_id is not None or index == len(layers) - 1 else radius < upper)
        region = regions.get(layer["id"])
        if region is not None and np.any(mask):
            for component, key in enumerate(("u", "v", "w")):
                radial[mask, component] = np.interp(radius[mask], region["r_m"], region[key])
    if normalized:
        radial /= mode_scale(mode)
    k = np.sqrt(mode["l"] * (mode["l"] + 1))
    if k:
        yt, yp = yt / k, yp / k
    else:
        yt, yp = np.zeros_like(y), np.zeros_like(y)
    result = (radial[:, 0] * y)[:, None] * er
    result += (radial[:, 1] * yt - radial[:, 2] * yp)[:, None] * et
    result += (radial[:, 1] * yp + radial[:, 2] * yt)[:, None] * ep
    center = radius == 0
    if np.any(center):
        result[center] = 0.0
        center_region = next((region for region in mode["regions"] if region["r_m"][0] == 0), None)
        if center_region is not None and (layer_id is None or center_region["layer_id"] == layer_id):
            u0, v0, w0 = (center_region[key][0] for key in ("u", "v", "w"))
            is_dipole = mode["family"] == "S" and mode["l"] == 1
            error = abs(v0 - np.sqrt(2) * u0) if is_dipole else max(abs(u0), abs(v0), abs(w0))
            if error > 1e-6 * mode_scale(mode):
                raise ValueError("mode violates center regularity; cannot invent a directional center field")
            if is_dipole:
                direction = {0: (0.0, 0.0, 1.0), 1: (-1.0, 0.0, 0.0), -1: (0.0, -1.0, 0.0)}[m]
                factor = np.sqrt(3 / (4 * np.pi)) * u0 / (mode_scale(mode) if normalized else 1.0)
                result[center] = factor * np.asarray(direction)
    return result


def _temporal(mode, term, times, derivative):
    omega = 2 * np.pi * mode["frequency_hz"]
    gamma = np.pi * mode["frequency_hz"] / mode["q"] if mode.get("q") else 0.0
    exponent = -gamma + 1j * omega
    return term["amplitude"] * np.real(exponent ** derivative * np.exp(exponent * times + 1j * term["phase_rad"]))


def evaluate_field(bundle, terms, points_m, time_s, derivative=0, normalized=True, layer_id=None):
    """Evaluate Cartesian modal displacement (or its first/second derivative).

    ``normalized=True`` gives illustration coefficients; it never changes the
    bundle. With False, the result retains the input modal normalization.
    """
    validate_terms(terms, bundle)
    if isinstance(derivative, bool) or not isinstance(derivative, (int, np.integer)) or derivative not in (0, 1, 2):
        raise ValueError("derivative must be 0, 1, or 2")
    if isinstance(time_s, (bool, str)) or not np.isscalar(time_s) or not np.isfinite(time_s) or time_s < 0:
        raise ValueError("time_s must be finite and nonnegative")
    if not isinstance(normalized, bool):
        raise ValueError("normalized must be boolean")
    points = np.asarray(points_m, dtype=float)
    if points.ndim != 2 or points.shape[1] != 3 or not np.all(np.isfinite(points)):
        raise ValueError("points_m must be a finite [N, 3] array")
    result = np.zeros_like(points)
    modes = {mode["id"]: mode for mode in bundle["modes"]}
    for term in terms:
        mode = modes[term["mode_id"]]
        result += _spatial_mode(bundle, mode, points, term["m"], normalized, layer_id) * _temporal(mode, term, time_s, derivative)
    return result


def sample_probe(bundle, scene, lat_deg, lon_deg, radius_fraction, times_s, derivative=0, normalized=True, layer_id=None):
    """Sample one material location in Cartesian axes without display gain."""
    specification = {"latitude_deg": lat_deg, "longitude_deg": lon_deg, "radius_fraction": radius_fraction}
    if layer_id is not None:
        specification["layer_id"] = layer_id
    validate_material_point(specification, bundle)
    times = np.asarray(times_s, dtype=float)
    if times.ndim != 1 or not np.all(np.isfinite(times)) or np.any(times < 0):
        raise ValueError("times_s must be a finite nonnegative 1D array")
    validate_terms(scene["terms"], bundle)
    if isinstance(derivative, bool) or not isinstance(derivative, (int, np.integer)) or derivative not in (0, 1, 2):
        raise ValueError("derivative must be 0, 1, or 2")
    if not isinstance(normalized, bool):
        raise ValueError("normalized must be boolean")
    lat, lon = np.deg2rad([lat_deg, lon_deg])
    point = np.array([[np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)]]) * radius_fraction * bundle["model"]["radius_m"]
    modes = {mode["id"]: mode for mode in bundle["modes"]}
    result = np.zeros((len(times), 3))
    for term in scene["terms"]:
        mode = modes[term["mode_id"]]
        spatial = _spatial_mode(bundle, mode, point, term["m"], normalized, layer_id)[0]
        result += _temporal(mode, term, times, derivative)[:, None] * spatial
    return result
