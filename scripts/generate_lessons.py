#!/usr/bin/env python3
"""Generate six self-contained, scientifically checked teaching projects.

The web catalog and saved projects share exactly the same scenes and probe
specifications. Source modes are never modified or relabeled for a lesson.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
import math
from pathlib import Path

import numpy as np

from earth_modes.data import (
    load_bundle,
    default_scene,
    default_color_limit,
    make_project,
    save_project,
    validate_project,
    bundle_hash,
)
from earth_modes.fields import evaluate_field, sample_probe, mode_scale
from earth_modes.export import export_image, export_probe

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "examples/lessons"


def point(latitude=28.0, longitude=34.0, radius=1.0, layer_id=None):
    p = dict(latitude_deg=latitude, longitude_deg=longitude, radius_fraction=radius)
    if layer_id is not None:
        p["layer_id"] = layer_id
    return p


def vector(p):
    lat, lon = np.deg2rad([p["latitude_deg"], p["longitude_deg"]])
    return (
        np.array([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)])
        * p["radius_fraction"]
    )


def term(mode_id, m=0, amplitude=1.0, phase=0.0):
    return dict(
        mode_id=mode_id, m=m, amplitude=float(amplitude), phase_rad=float(phase)
    )


def probe(p, duration, samples=1025):
    return dict(
        **p,
        start_s=0.0,
        step_s=float(duration / (samples - 1)),
        sample_count=samples,
        derivative=0,
        normalized=True,
    )


def recommended_color_limit(bundle, scene):
    """Exact low-degree component envelopes for the six curated examples.

    Canonical piecewise-linear radial functions attain maxima at source knots.
    The real l=2 harmonics and selected T phi derivative have analytic angular
    maxima. Sum term envelopes, except the exact quadrature traveling pair.
    This is one fixed all-time range, never an instantaneous frame rescaling.
    """
    lookup = {mode["id"]: mode for mode in bundle["modes"]}
    bounds = []
    for term in scene["terms"]:
        mode = lookup[term["mode_id"]]
        scale = mode_scale(mode)
        key = "w" if scene["color"] == "phi" else "u"
        if scene["cutaway"]:
            radial = (
                max(abs(value) for region in mode["regions"] for value in region[key])
                / scale
            )
        else:
            radial = (
                max(
                    (
                        abs(region[key][-1])
                        for region in mode["regions"]
                        if region["r_m"][-1] == bundle["model"]["radius_m"]
                    ),
                    default=0,
                )
                / scale
            )
        if scene["color"] == "phi":
            assert mode["family"] == "T" and mode["l"] == 2 and abs(term["m"]) == 1
            angular = math.sqrt(15 / (4 * np.pi)) / math.sqrt(6)
        elif term["m"] == 0:
            angular = math.sqrt((2 * mode["l"] + 1) / (4 * np.pi))
        else:
            assert mode["l"] == 2 and abs(term["m"]) in (1, 2)
            angular = math.sqrt(15 / (16 * np.pi))
        bounds.append(abs(term["amplitude"]) * radial * angular)
    combined = sum(bounds)
    method = "sum of analytic component envelopes"
    if len(scene["terms"]) == 2:
        a, b = scene["terms"]
        if (
            a["mode_id"] == b["mode_id"]
            and a["m"] == -b["m"]
            and abs(a["m"]) == 2
            and abs(a["amplitude"]) == abs(b["amplitude"])
            and abs(abs(a["phase_rad"] - b["phase_rad"]) - np.pi / 2) < 1e-14
        ):
            combined = max(bounds)
            method = "exact quadrature traveling-pair envelope"
    assert combined > 0
    return 1.05 * combined, dict(
        method=method,
        component=scene["color"],
        analytic_envelope=combined,
        safety_factor=1.05,
        scope="all radii and both material sides" if scene["cutaway"] else "surface",
        temporal_policy="fixed for the complete scene; no frame or Q rescaling",
    )


def generate(bundle):
    modes = {m["id"]: m for m in bundle["modes"]}
    R = bundle["model"]["radius_m"]
    mantle = next(
        m
        for m in bundle["modes"]
        if m["family"] == "T"
        and m["n"] == 0
        and m["l"] == 2
        and any(r["r_m"][-1] == R for r in m["regions"])
    )
    lessons = []

    def add(
        id,
        title,
        terms,
        steps,
        conclusion,
        caution,
        *,
        selected_point=None,
        cutaway=False,
        nodes=False,
        color="radial",
        duration=None,
        export_duration=8.0,
        verification=None,
        variants=None,
        camera=None,
    ):
        sc = default_scene(bundle)
        sc["terms"] = terms
        period = 1 / modes[terms[0]["mode_id"]]["frequency_hz"]
        duration = duration or period
        sc.update(
            color=color,
            color_limit=default_color_limit(bundle, terms),
            cutaway=cutaway,
            nodes=nodes,
            arrows=True,
            point=selected_point or point(),
            time_scale=duration / export_duration,
        )
        if camera is not None:
            sc["camera"].update(camera)
        sc["color_limit"], color_policy = recommended_color_limit(bundle, sc)
        fastest = max(
            modes[t["mode_id"]]["frequency_hz"] for t in terms if t["amplitude"]
        )
        trajectory_samples = max(256, math.ceil(24 * fastest * duration) + 1)
        if trajectory_samples > 2048:
            raise ValueError("Lesson trajectory exceeds explicit sampling budget")
        sc["trajectory"] = dict(
            enabled=True,
            start_s=0.0,
            duration_s=float(duration),
            samples=trajectory_samples,
        )
        ex = dict(
            format="mp4",
            width=960,
            height=720,
            duration_s=float(export_duration),
            fps=24,
            transparent=False,
            annotation=True,
            omit_arrows=False,
            omit_geography=False,
            omit_analysis_overlays=False,
        )
        caution += " This lesson uses a fixed component color range without changing the modes or physical amplitudes."
        entry = dict(
            id=id,
            title=title,
            steps=steps,
            conclusion=conclusion,
            caution=caution,
            scene=sc,
            probe=probe(sc["point"], duration, 4097 if id == "06-beats" else 1025),
            export=ex,
            verification={**(verification or {}), "color_policy": color_policy},
            variants=variants or [],
        )
        assert len(steps) <= 3
        project = make_project(bundle, sc, entry["probe"], ex)
        project["teaching"] = {
            k: deepcopy(entry[k])
            for k in (
                "id",
                "title",
                "steps",
                "conclusion",
                "caution",
                "verification",
                "variants",
            )
        }
        validate_project(project)
        lessons.append((entry, project))
        return entry

    # 1. The l=0 harmonic is angle-independent; vector direction remains radial.
    t = [term("R0_0")]
    p = point()
    directions = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], vector(p)])
    fields = evaluate_field(bundle, t, directions * R, 0)
    radial = np.sum(fields * directions, axis=1)
    half = evaluate_field(
        bundle, t, directions * R, 0.5 / modes["R0_0"]["frequency_hz"]
    )
    assert np.ptp(radial) < 1e-12 and np.max(abs(fields + half)) < 1e-12
    add(
        "01-breathing",
        "A breathing sphere",
        t,
        [
            "Play one period and compare radial arrows in different directions on the sphere.",
            "Pause and change time from 0 to T/2; verify that expansion and contraction exchange.",
            "Halve the geometric gain and confirm that the eigenfrequency and material-point period stay fixed.",
        ],
        "The surface radial coefficient of R0_0 is independent of direction; displacement reverses after half a period.",
        "Display gain makes motion visible; these amplitudes are not earthquake displacements in metres.",
        verification=dict(
            mode_id="R0_0",
            frequency_hz=modes["R0_0"]["frequency_hz"],
            surface_radial_spread=float(np.ptp(radial)),
            half_period_reversal_error=float(np.max(abs(fields + half))),
        ),
    )

    # 2. A real single mode has one fixed spatial vector times one sinusoid.
    t = [term(mantle["id"], 1)]
    times = np.linspace(0, 1 / mantle["frequency_hz"], 129)
    values = sample_probe(bundle, dict(terms=t), 28, 34, 1, times)
    normal = vector(point())
    tangency = float(np.max(abs(values @ normal)))
    rank = np.linalg.svd(values, compute_uv=False)
    assert tangency < 1e-12 and rank[1] / rank[0] < 1e-12
    add(
        "02-tangential",
        "Purely tangential motion?",
        t,
        [
            "Check whether displacement arrows are perpendicular to the reference radius.",
            "Follow the gold material point for one period; it moves back and forth along a fixed tangent.",
            "Increase and decrease geometric gain to distinguish first-order tangential displacement from the radius change of the exaggerated position.",
        ],
        "Displacement of this surface-solid-domain T0_2 mode is tangential everywhere; a single real mode gives a local line-segment trajectory.",
        "Tangential oscillation is not planetary rotation; finite displayed displacement creates a second-order geometric radius change.",
        color="phi",
        verification=dict(
            mode_id=mantle["id"],
            solid_domain_id=mantle["provenance"]["solid_domain_id"],
            max_radial_projection=tangency,
            trajectory_secondary_singular_ratio=float(rank[1] / rank[0]),
        ),
    )

    # 3. Explicit one-parameter comparisons, all from the same true catalog.
    variants = [
        dict(label="Change only m: 0 → 2", terms=[term("S0_2", 2)]),
        dict(
            label="Return to the baseline; change only l: 2 → 3",
            terms=[term("S0_3", 0)],
        ),
        dict(
            label="Return to the baseline; change only n: 0 → 1",
            terms=[term("S1_2", 0)],
        ),
    ]
    add(
        "03-indices",
        "What do n, l and m change?",
        [term("S0_2", 0)],
        [
            "Keep S0_2 and change only m from 0 to 2; compare the node pattern and frequency.",
            "Return to S0_2, m=0, then select S0_3; compare only angular degree l.",
            "Return to the baseline again, then select S1_2; compare radial eigenfunctions at the same l.",
        ],
        "In a spherical model, m selects a degenerate angular basis without changing frequency; changing n or l selects a different eigenmode.",
        "The branch label n is not the total zero count of every U/V/W component in a layered solid-fluid model.",
        nodes=True,
        cutaway=True,
        variants=variants,
        camera=dict(azimuth_deg=-45.0, elevation_deg=20.0, distance=2.9),
        verification=dict(
            m_variants_share_mode_id="S0_2",
            same_frequency_hz=modes["S0_2"]["frequency_hz"],
            l_comparison_hz=modes["S0_3"]["frequency_hz"],
            n_comparison_hz=modes["S1_2"]["frequency_hz"],
        ),
    )

    # 4. Keep the two sides as distinct material samples.
    mode = modes["S0_2"]
    regions = {r["layer_id"]: r for r in mode["regions"]}
    fluid = next(l for l in bundle["model"]["layers"] if l["phase"] == "fluid")
    index = bundle["model"]["layers"].index(fluid)
    solid = bundle["model"]["layers"][index + 1]
    a = regions[fluid["id"]]
    b = regions[solid["id"]]
    scale = mode_scale(mode)
    jump_u = abs(a["u"][-1] - b["u"][0]) / scale
    jump_v = abs(a["v"][-1] - b["v"][0]) / scale
    assert jump_u < 1e-5 and jump_v > 0.01
    p = point(28, 0, radius=fluid["r_m"][-1] / R, layer_id=fluid["id"])
    add(
        "04-liquid-core",
        "Across the liquid core boundary",
        [term("S0_2", 1)],
        [
            "Use the cutaway and U/V curves to locate the outer-core–mantle boundary.",
            "Compare U on the fluid and solid sides at the same boundary radius; normal displacement is continuous.",
            "Switch the linked point from the fluid material side to the solid side; tangential displacement may jump.",
        ],
        "A fluid-solid interface couples normal motion, but tangential displacement need not be continuous; interpolation must not smooth across it.",
        "The fluid is not stationary: it participates in S/R modes; an ideal fluid does not support elastic T modes.",
        cutaway=True,
        selected_point=p,
        camera=dict(azimuth_deg=-45.0, elevation_deg=20.0, distance=2.9),
        verification=dict(
            boundary_radius_m=fluid["r_m"][-1],
            fluid_layer_id=fluid["id"],
            solid_layer_id=solid["id"],
            normalized_u_jump=jump_u,
            normalized_v_jump=jump_v,
            opposite_side_point=point(
                28, 0, radius=fluid["r_m"][-1] / R, layer_id=solid["id"]
            ),
        ),
    )

    # 5. cos(m phi)cos(wt)-sin(m phi)sin(wt)=cos(m phi+wt).
    t = [term("S0_2", 2), term("S0_2", -2, phase=np.pi / 2)]
    mode = modes["S0_2"]
    time = 0.125 / mode["frequency_hz"]
    p0 = point(28, 34)
    shift = -360 * mode["frequency_hz"] * time / 2
    p1 = point(28, 34 + shift)
    f0 = evaluate_field(bundle, t, [vector(p0) * R], 0)[0] @ vector(p0)
    f1 = evaluate_field(bundle, t, [vector(p1) * R], time)[0] @ vector(p1)
    assert abs(f0 - f1) < 1e-12
    add(
        "05-traveling",
        "Building a traveling pattern",
        t,
        [
            "Inspect the two terms: m=+2 and m=-2 of S0_2, with equal amplitudes and a phase difference of π/2.",
            "Advance from t=0 to T/8; the pattern shifts 22.5° toward decreasing longitude.",
            "Observe the closed local trajectory of a fixed material point, then remove one term to compare a standing wave.",
        ],
        "Two degenerate real bases in quadrature produce cos(2φ+ωt), a traveling pattern with angular speed −ω/2.",
        "The pattern moves; material points oscillate locally rather than following its peaks around the planet.",
        verification=dict(
            frequency_hz=mode["frequency_hz"],
            negative_m_phase_rad=float(np.pi / 2),
            test_physical_time_s=time,
            longitude_shift_deg=shift,
            radial_translation_error=abs(f0 - f1),
        ),
    )

    # 6. At the equator these even-l,m=0 modes have a nonzero pure-x signal.
    first, second = modes["S0_4"], modes["S1_2"]
    p = point(0, 0)
    raw = np.array(
        [
            evaluate_field(bundle, [term(m["id"])], [[R, 0, 0]], 0)[0]
            for m in [first, second]
        ]
    )
    assert np.all(abs(raw[:, 0]) > 0.01) and np.max(abs(raw[:, 1:])) < 1e-12
    common = float(min(abs(raw[:, 0])))
    amplitudes = common / abs(raw[:, 0])
    phases = np.where(raw[:, 0] < 0, np.pi, 0.0)
    t = [
        term(m["id"], 0, amplitudes[i], phases[i])
        for i, m in enumerate([first, second])
    ]
    difference = abs(first["frequency_hz"] - second["frequency_hz"])
    relative = difference / min(first["frequency_hz"], second["frequency_hz"])
    assert 0.025 <= relative <= 0.12
    beat_period = 1 / difference
    duration = 2 * beat_period
    times = np.linspace(0, duration, 4097)
    values = sample_probe(bundle, dict(terms=t), 0, 0, 1, times)
    expected = (
        2
        * common
        * np.cos(np.pi * difference * times)
        * np.cos(np.pi * (first["frequency_hz"] + second["frequency_hz"]) * times)
    )
    analytic_error = float(np.max(abs(values[:, 0] - expected)))
    assert analytic_error < 1e-11
    minima = sample_probe(
        bundle, dict(terms=t), 0, 0, 1, np.array([0.5, 1.5]) * beat_period
    )
    assert np.max(abs(minima)) < 1e-11
    add(
        "06-beats",
        "Beats at a fixed point",
        t,
        [
            "Read the x time series at the gold point on the equator at zero longitude; the two local amplitudes are explicitly balanced.",
            "Inspect at least two envelope periods and compare cancellation near T_beat/2 and 3T_beat/2.",
            "Disable each term in turn, then restore the sum to confirm that the slow envelope follows the frequency difference.",
        ],
        f"The frequency difference is {difference*1000:.6g} mHz; the amplitude-envelope period at this point is 1/Δf ≈ {beat_period/3600:.4g} hours.",
        "The x component is balanced at this receiver; beat depth can change at another location. Two-frequency superposition does not guarantee a seamless loop.",
        selected_point=p,
        duration=duration,
        export_duration=24.0,
        verification=dict(
            mode_ids=[first["id"], second["id"]],
            frequency_difference_hz=difference,
            relative_frequency_difference=relative,
            local_unweighted_x=raw[:, 0].tolist(),
            balanced_local_amplitude=common,
            beat_envelope_period_s=beat_period,
            probe_window_s=duration,
            complete_envelope_periods=2,
            analytic_x_signal_max_error=analytic_error,
            cancellation_sample_max=float(np.max(abs(minima))),
            amplitude_policy="equal local x amplitudes at equator/lon0; retain global illustration normalization",
        ),
    )
    return lessons


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-previews", action="store_true")
    args = parser.parse_args()
    bundle = load_bundle(ROOT / "examples/prem-modes.json")
    lessons = generate(bundle)
    DEST.mkdir(parents=True, exist_ok=True)
    for entry, project in lessons:
        save_project(project, DEST / (entry["id"] + ".terra.json"), overwrite=True)
    catalog = dict(
        bundle_hash=bundle_hash(bundle), lessons=[entry for entry, _ in lessons]
    )
    (DEST / "catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    )
    if not args.no_previews:
        for entry, project in lessons:
            export_image(
                project["bundle"],
                project["scene"],
                DEST / (entry["id"] + ".png"),
                960,
                720,
                overwrite=True,
            )
        beats = lessons[5][1]
        export_probe(
            beats["bundle"],
            beats["scene"],
            beats["probe"],
            DEST / "06-beats-probe.png",
            overwrite=True,
        )
        export_probe(
            beats["bundle"],
            beats["scene"],
            beats["probe"],
            DEST / "06-beats-probe.csv",
            overwrite=True,
        )
    rows = [
        "# Six scientific normal-mode lessons",
        "",
        "Each `.terra.json` contains the complete 47-mode PREM bundle, SceneSpec, ProbeSpec, ExportSpec and English teaching notes for independent import. The catalog does not duplicate the bundle; its hash must match the canonical PREM bundle. Package examples and website copies use this same catalog.",
        "",
        "Frequencies and eigenfunctions come from the validated default solution. Illustration normalization is fixed per mode; geometric gain is not source calibration. Curated color limits use 1.05 times the all-time analytic component envelope, including both material sides on sections. No per-frame rescaling or change to general scene defaults is applied. See `teaching.verification.color_policy` and each mode's quality provenance.",
        "",
        "Regenerate with `OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/generate_lessons.py`. `--no-previews` skips only PNG/CSV production; projects and scientific assertions are still generated and checked.",
        "",
    ]
    for entry, _ in lessons:
        rows += [
            f"## {entry['title']}",
            "",
            f"Project: [{entry['id']}.terra.json]({entry['id']}.terra.json)",
            "",
        ]
        rows += [f"{i+1}. {step}" for i, step in enumerate(entry["steps"])]
        rows += [
            "",
            f"Checkable conclusion: {entry['conclusion']}",
            "",
            f"Interpretation caution: {entry['caution']}",
            "",
        ]
    rows += [
        "## Outputs from the same projects",
        "",
        "Each named PNG is exported from its lesson SceneSpec. `06-beats-probe.png` and the CSV use the sixth lesson's ProbeSpec. JSON sidecars retain the scene, sampling and bundle hash; a hash is not a replacement for the input data.",
        "",
        "The beat case uses 0S4 and 1S2 with m=0 at the equator/zero-longitude surface point. Explicit amplitudes and π phases balance the local x components. Its 4097 samples include the endpoint of two envelope periods. The traveling case uses ±m=2 of 0S2 in quadrature, without an artificial frequency difference.",
        "",
        "Generation verifies these teaching constructions and data contracts. Release-level implementation review is recorded separately in the review log.",
        "",
    ]
    (DEST / "README.md").write_text("\n".join(rows))
    print(
        f'Generated and validated {len(lessons)} self-contained lessons; catalog bundle hash {catalog["bundle_hash"]}'
    )
    print(json.dumps(lessons[-1][0]["verification"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
