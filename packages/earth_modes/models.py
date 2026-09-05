"""Reproducible SI material models, independent of any solver or renderer."""
from __future__ import annotations

import hashlib
from importlib.resources import files

import numpy as np

from .data import validate_model


def homogeneous_model(radius_m=6371000, rho_kg_m3=5515, vp_m_s=10000, vs_m_s=5500) -> dict:
    """Build a uniform solid sphere, or a fluid sphere when vs_m_s=0."""
    phase = "fluid" if vs_m_s == 0 else "solid"
    model = {"id": f"homogeneous-{phase}", "name": f"Homogeneous {phase} sphere",
             "radius_m": radius_m, "layers": [{"id": "sphere", "name": "Uniform sphere", "phase": phase,
             "r_m": [0.0, radius_m], "rho_kg_m3": [rho_kg_m3, rho_kg_m3],
             "vp_m_s": [vp_m_s, vp_m_s], "vs_m_s": [vs_m_s, vs_m_s]}],
             "provenance": {"kind": "analytic_material_model", "description": "Uniform input material; this is not a solved mode."}}
    return validate_model(model)


def prem_model() -> dict:
    """Return the bundled isotropic, no-ocean PREM approximation at 3 mHz.

    This is the exact material table distributed with Ouroboros v6.0, not a
    hand-drawn Earth profile. Repeated radii preserve discontinuity sides.
    Its zero Q columns mean attenuation was removed; they are not modal Q=0.
    """
    source = files("earth_modes").joinpath("assets/prem-isotropic-3mhz.txt")
    raw = source.read_bytes()
    from io import BytesIO
    table = np.loadtxt(BytesIO(raw), skiprows=3)
    starts = np.r_[0, np.where(np.diff(table[:, 0]) == 0)[0] + 1]
    ends = np.r_[starts[1:], len(table)]
    layers = []
    for index, (start, end) in enumerate(zip(starts, ends)):
        rows = table[start:end]
        name = "Inner core" if index == 0 else "Outer core" if index == 1 else f"Mantle / crust region {index - 1}"
        layers.append({"id": f"prem-{index:02d}", "name": name,
                       "phase": "fluid" if np.all(rows[:, 3] == 0) else "solid",
                       "r_m": rows[:, 0].tolist(), "rho_kg_m3": rows[:, 1].tolist(),
                       "vp_m_s": rows[:, 2].tolist(), "vs_m_s": rows[:, 3].tolist()})
    return validate_model({"id": "prem-isotropic-noocean-3mhz", "name": "PREM · isotropic · no ocean · 3 mHz",
                           "radius_m": float(table[-1, 0]), "layers": layers,
                           "reference_frequency_hz": 0.003,
                           "provenance": {"source": "https://github.com/harrymd/Ouroboros",
                           "upstream_commit": "fa63363040a28c08d9fe2bd7d05dcc823d90dd1e",
                           "source_path": "example/input/models/prem_noocean_at_03.000_mHz_noq.txt",
                           "source_sha256": hashlib.sha256(raw).hexdigest(), "license": "GPL-3.0",
                           "approximations": ["isotropic mean of anisotropic speeds", "no ocean", "3 mHz reference dispersion correction", "attenuation removed in supplied table"],
                           "q_semantics": "Zero source Q columns are absent attenuation information, not finite zero Q."}})
