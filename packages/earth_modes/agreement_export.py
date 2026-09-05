"""Checked agreement reports, scalar tables and material-sided native figures."""
from __future__ import annotations

import csv
from pathlib import Path

from . import __version__
from .agreement import MAX_REPORT_BYTES, _bounded_json_size, _checked_evaluation
from .data import _integer, _write_json
from .export_common import transaction


CSV_COLUMNS = (
    "pair_index", "reference_mode_id", "candidate_mode_id", "l", "reference_n",
    "candidate_n", "radial_label_mismatch", "reference_solver", "candidate_solver",
    "reference_frequency_hz", "candidate_frequency_hz", "delta_frequency_hz",
    "relative_frequency_change", "reference_continuous_norm", "candidate_continuous_norm",
    "signed_overlap", "overlap", "alignment_sign", "alignment_indeterminate", "shape_distance",
    "reference_domain_elements", "candidate_domain_elements", "reference_domain_samples",
    "candidate_domain_samples", "model_hash", "reference_bundle_hash", "candidate_bundle_hash",
)


def _solver(report, role):
    value = report["sources"][role]["bundle"]["provenance"].get("solver")
    return value if isinstance(value, str) and value.strip() else "unknown"


def _csv_rows(report, rows):
    for row in rows:
        result = {key: row[key] for key in CSV_COLUMNS if key in row}
        result["model_hash"] = report["model_hash"]
        for role in ("reference", "candidate"):
            result[role + "_solver"] = _solver(report, role)
            result[role + "_bundle_hash"] = report["sources"][role]["bundle_hash"]
            counts = list(row[role + "_mesh_elements"].values())
            result[role + "_domain_elements"] = sum(counts) if all(x is not None for x in counts) else None
            result[role + "_domain_samples"] = sum(row[role + "_radial_samples"].values())
        yield result


def _fit_label(artist, value, max_width, *, prefix="", suffix=""):
    """Ellipsize only the user text using this figure's measured pixel width."""
    text = " ".join(str(value).split())
    renderer = artist.figure.canvas.get_renderer()
    artist.set_text(prefix + text + suffix)
    if artist.get_window_extent(renderer).width <= max_width:
        return
    lo, hi = 0, len(text)
    while lo < hi:
        middle = (lo + hi + 1) // 2
        artist.set_text(prefix + text[:middle] + "…" + suffix)
        if artist.get_window_extent(renderer).width <= max_width:
            lo = middle
        else:
            hi = middle - 1
    artist.set_text(prefix + text[:lo] + "…" + suffix)


def _figure(report, evaluated, index, width, height):
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.ticker import ScalarFormatter, MaxNLocator

    row, curves = evaluated["rows"][index], evaluated["curves"][index]
    radius = report["sources"]["reference"]["bundle"]["model"]["radius_m"]
    font = 9 if width < 800 else 11
    fig = Figure(figsize=(width / 100, height / 100), dpi=100)
    FigureCanvasAgg(fig)
    top, residual = fig.subplots(2, 1, sharex=True, gridspec_kw={"height_ratios": [1.3, 1]})
    fig.subplots_adjust(left=.145, right=.955, bottom=.21 if height < 600 else .18,
                        top=.69, hspace=.31)
    colors = ("#176287", "#b25b20")
    for j, curve in enumerate(curves):
        r = [x / radius for x in curve["r_m"]]
        for key, color, style, label in (
            ("reference_w", colors[0], "-", "Reference"),
            ("candidate_w", colors[1], "--", "Aligned candidate"),
        ):
            top.plot(r, curve[key], color=color, linestyle=style, linewidth=1.7,
                     label=label if j == 0 else "_nolegend_")
        residual.plot(r, curve["residual_w"], color="#61497b", linewidth=1.5)
    lo, hi = curves[0]["r_m"][0] / radius, curves[-1]["r_m"][-1] / radius
    for axis in (top, residual):
        axis.set_xlim(lo, hi)
        axis.tick_params(labelsize=font - 1)
        axis.yaxis.set_major_locator(MaxNLocator(nbins=3))
        formatter = ScalarFormatter(useOffset=False, useMathText=True)
        formatter.set_powerlimits((-2, 3))
        axis.yaxis.set_major_formatter(formatter)
        axis.yaxis.get_offset_text().set_fontsize(font - 1)
        axis.grid(alpha=.17)
        for boundary in [c["r_m"][0] / radius for c in curves] + [hi]:
            axis.axvline(boundary, color="#777777", linestyle=":", linewidth=.8)
        axis.spines[["top", "right"]].set_visible(False)
    top.set_ylabel("Normalized W\n[kg$^{-1/2}$]", fontsize=font)
    residual.set_ylabel("Residual\n[kg$^{-1/2}$]", fontsize=font)
    residual.set_title("Residual: reference − aligned candidate", loc="right", fontsize=font - 1, pad=5)
    residual.set_xlabel("Common radius r/R", fontsize=font)
    top.legend(loc="best", fontsize=font - 1, frameon=False, ncols=2)
    residual.axhline(0, color="#777777", linewidth=.6)
    peak = max(abs(x) for curve in curves for x in curve["residual_w"])
    if peak == 0:
        scale = max(abs(x) for curve in curves for x in curve["reference_w"])
        residual.set_ylim(-.05 * scale, .05 * scale)
        residual.text(.98, .91, "Exact zero residual", transform=residual.transAxes,
                      ha="right", va="top", fontsize=font - 1)
    else:
        residual.set_ylim(-1.12 * peak, 1.12 * peak)
    label = f"T agreement · pair {index} of {len(evaluated['rows'])} (zero-based) · l={row['l']} · n={row['reference_n']} → {row['candidate_n']}"
    fig.text(.055, .96, label, fontsize=font + 2, weight="bold", va="top")
    for y, role, color in ((.91, "reference", colors[0]), (.872, "candidate", colors[1])):
        method = fig.text(.055, y, "", color=color, fontsize=font, va="top", parse_math=False)
        _fit_label(method, _solver(report, role), .9 * width - 4, prefix=f"{role.capitalize()}: ")
    fig.text(.055, .827,
             f"f: {row['reference_frequency_hz']:.8g} → {row['candidate_frequency_hz']:.8g} Hz"
             f"    Δf/f: {row['relative_frequency_change']:+.5g}", fontsize=font, va="top")
    fig.text(.055, .788,
             f"Shape distance: {row['shape_distance']:.6g}    sign: {row['alignment_sign']:+d}"
             "    Residual scale is separate", fontsize=font, va="top")
    warnings = []
    if row["radial_label_mismatch"]:
        warnings.append("Different n labels; explicit pairing")
    if row["alignment_indeterminate"]:
        warnings.append("Near-zero overlap; sign +1 is indeterminate")
    model = report["sources"]["reference"]["bundle"]["model"]
    # Reserve measured line heights from the bottom, including both notices.
    # Width may increase the font even on a short canvas, so fractions alone
    # cannot guarantee a gap between the footer, accuracy caption and x label.
    renderer = fig.canvas.get_renderer()
    gap = max(6, font)
    accuracy = fig.text(.055, max(12, .025 * height) / height,
                        "Agreement is not continuum accuracy. Full IDs, norms, mesh and quality: adjacent .json sidecar.",
                        fontsize=font - 1, va="bottom", color="#444444")
    footer_y = (accuracy.get_window_extent(renderer).y1 + gap) / height
    footer = fig.text(.055, footer_y, "\n".join(warnings),
                      color="#8a4523" if warnings else "#555555", fontsize=font - 1,
                      va="bottom", linespacing=1.25, parse_math=False)
    if not warnings:
        _fit_label(footer, model["name"], .9 * width - 4,
                   prefix="Model: ", suffix=" · material boundaries dotted")
    decorations = residual.bbox.y0 - residual.get_tightbbox(renderer).y0
    minimum_bottom = (footer.get_window_extent(renderer).y1 + gap + decorations) / height
    fig.subplots_adjust(bottom=max(fig.subplotpars.bottom, minimum_bottom))
    return fig


def export_agreement(report, path, *, pair_index=None, width=None, height=None, overwrite=False):
    """Validate before publishing JSON, all-row CSV, or one selected SVG/PNG pair.

    Figure sidecars and CSV sidecars are directly reloadable full reports.
    Individual artifact/sidecar commits roll back controlled failures; several
    exports are not a batch transaction or a power-loss guarantee.
    """
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix not in (".json", ".csv", ".svg", ".png"):
        raise ValueError("Agreement output must be .json, .csv, .svg or .png")
    figure = suffix in (".svg", ".png")
    if not figure and any(x is not None for x in (pair_index, width, height)):
        raise ValueError("pair_index, width and height apply only to agreement figures")
    if figure:
        width = 1200 if width is None else _integer(width, "width", 640)
        height = 800 if height is None else _integer(height, "height", 480)
        if width > 4096 or height > 4096:
            raise ValueError("figure dimensions must not exceed 4096")
        if pair_index is not None:
            pair_index = _integer(pair_index, "pair_index")
    evaluated = _checked_evaluation(report)
    if figure:
        if pair_index is None:
            if len(evaluated["rows"]) != 1:
                raise ValueError("a multi-pair figure requires an explicit zero-based pair_index")
            pair_index = 0
        if pair_index >= len(evaluated["rows"]):
            raise ValueError("pair_index is outside the report")
    if suffix == ".json":
        _write_json(report, path, overwrite=overwrite)
        return path
    production = dict(renderer="earth_modes.agreement_export", renderer_version=__version__,
                      annotation_language="en", format=suffix[1:])
    if figure:
        production.update(pair_index=pair_index, width=width, height=height)
    sidecar = dict(report, export_production=production)
    _bounded_json_size(sidecar, MAX_REPORT_BYTES, "agreement export sidecar")
    path.parent.mkdir(parents=True, exist_ok=True)
    with transaction(path, overwrite) as (staged, info):
        info.update(sidecar)
        if suffix == ".csv":
            with staged.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=CSV_COLUMNS)
                writer.writeheader()
                writer.writerows(_csv_rows(report, evaluated["rows"]))
        else:
            fig = _figure(report, evaluated, pair_index, width, height)
            try:
                fig.savefig(staged, format=suffix[1:], dpi=100, facecolor="white")
            finally:
                fig.clear()
    return path
