"""Public deterministic export API for figures, movies, tables and GLB assets."""

from pathlib import Path
import csv
import json
import shutil
import subprocess
import tempfile
import numpy as np
from .fields import sample_probe
from .export_common import ExportLimits, prepare, transaction, manifest, size, times, media_budget
from .export_render import geometry, render
from .export_overlays import build_overlays, overlay_metadata


def _frame(bundle, scene, geo, overlays, time_s, path, width, height, transparent, annotation):
    figure, clipping = render(
        bundle,
        scene,
        geo,
        time_s,
        width,
        height,
        overlays=overlays,
        annotation=annotation,
        transparent=transparent,
    )
    figure.savefig(
        path,
        dpi=100,
        transparent=transparent,
        facecolor="none" if transparent else figure.get_facecolor(),
    )
    figure.clear()
    from PIL import Image

    with Image.open(path) as check:
        if check.size != (width, height):
            raise RuntimeError("PNG dimensions do not match the export request.")
        check.verify()
    return clipping


def export_image(
    bundle,
    scene,
    path,
    width=1200,
    height=900,
    *,
    transparent=False,
    annotation=True,
    overwrite=False,
    limits=None,
):
    limits = limits or ExportLimits()
    path = prepare(bundle, scene, path, (".png",))
    size(width, height, limits)
    with transaction(path, overwrite) as (staged, info):
        geo = geometry(bundle, scene, limits)
        overlays = build_overlays(bundle, scene, geo, limits)
        clipped = _frame(
            bundle,
            scene,
            geo,
            overlays,
            scene["time_s"],
            staged,
            width,
            height,
            transparent,
            annotation,
        )
        info.update(
            manifest(
                bundle,
                scene,
                format="png",
                width=width,
                height=height,
                transparent=transparent,
                annotation=annotation,
                clipping_samples=clipped,
                overlay_note=overlays.node_note,
                analysis_overlays=overlay_metadata(overlays, scene),
                resources=geo.budget,
                renderer="matplotlib orthographic",
                export_spec=dict(
                    format="png",
                    width=width,
                    height=height,
                    transparent=transparent,
                    annotation=annotation,
                ),
            )
        )
    return path


def _frames(bundle, scene, directory, duration_s, fps, width, height, annotation, limits):
    playback, physical, notes = times(bundle, scene, duration_s, fps, limits)
    budget = media_budget(width, height, len(playback), directory, limits)
    geo = geometry(bundle, scene, limits)
    overlays = build_overlays(bundle, scene, geo, limits)
    clipping = []
    for index, time_s in enumerate(physical):
        clipping.append(
            _frame(
                bundle,
                scene,
                geo,
                overlays,
                float(time_s),
                directory / f"frame_{index:06d}.png",
                width,
                height,
                False,
                annotation,
            )
        )
    return manifest(
        bundle,
        scene,
        format="frames",
        width=width,
        height=height,
        fps=fps,
        frame_count=len(playback),
        physical_times_s=physical.tolist(),
        endpoint_included=False,
        requested_duration_s=duration_s,
        playback_duration_s=len(playback) / fps,
        clipping_samples=clipping,
        warnings=notes,
        resources={**budget, **geo.budget},
        annotation=annotation,
        overlay_note=overlays.node_note,
        analysis_overlays=overlay_metadata(overlays, scene),
        export_spec=dict(
            format="frames",
            width=width,
            height=height,
            duration_s=duration_s,
            fps=fps,
            annotation=annotation,
        ),
    )


def export_frames(
    bundle,
    scene,
    output_dir,
    duration_s=8,
    fps=24,
    width=960,
    height=720,
    *,
    annotation=True,
    overwrite=False,
    limits=None,
):
    limits = limits or ExportLimits()
    directory = prepare(bundle, scene, output_dir, None)
    with transaction(directory, overwrite, directory=True) as (staged, info):
        info.update(
            _frames(bundle, scene, staged, duration_s, fps, width, height, annotation, limits)
        )
    return directory


def _ffmpeg(suffix):
    executable = shutil.which("ffmpeg")
    if executable is None:
        raise RuntimeError("FFmpeg is required for GIF/MP4; install ffmpeg or export PNG frames.")
    probe = subprocess.run(
        [executable, "-hide_banner", "-encoders"], capture_output=True, text=True, check=True
    )
    available = {line.split()[1] for line in probe.stdout.splitlines() if len(line.split()) >= 2}
    if suffix == ".mp4" and "libx264" not in available:
        raise RuntimeError("This FFmpeg build lacks libx264 required for MP4 export.")
    version = subprocess.run(
        [executable, "-version"], capture_output=True, text=True, check=True
    ).stdout.splitlines()[0]
    return executable, version


def _run(command):
    process = subprocess.run(command, capture_output=True, text=True)
    if process.returncode:
        raise RuntimeError(f"FFmpeg failed: {process.stderr[-3000:]}")


def export_video(
    bundle,
    scene,
    path,
    duration_s=8,
    fps=None,
    width=960,
    height=720,
    *,
    annotation=True,
    transparent=False,
    overwrite=False,
    limits=None,
):
    limits = limits or ExportLimits()
    path = prepare(bundle, scene, path, (".gif", ".mp4"))
    if transparent:
        raise ValueError("Transparent video is not supported; export transparent PNG instead.")
    suffix = path.suffix.lower()
    fps = (20 if suffix == ".gif" else 24) if fps is None else fps
    if suffix == ".gif" and fps not in (1, 2, 4, 5, 10, 20, 25, 50):
        raise ValueError("GIF fps must exactly divide 100: choose 1,2,4,5,10,20,25,50.")
    size(width, height, limits)
    if suffix == ".mp4" and (width % 2 or height % 2):
        raise ValueError("MP4 requires even width and height for yuv420p.")
    times(bundle, scene, duration_s, fps, limits)
    executable, version = _ffmpeg(suffix)
    with transaction(path, overwrite) as (staged, info):
        with tempfile.TemporaryDirectory(prefix="frames-", dir=staged.parent) as temporary:
            directory = Path(temporary)
            info.update(
                _frames(
                    bundle, scene, directory, duration_s, fps, width, height, annotation, limits
                )
            )
            command = [
                executable,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-framerate",
                str(fps),
                "-i",
                str(directory / "frame_%06d.png"),
            ]
            if suffix == ".mp4":
                _run(
                    command
                    + [
                        "-c:v",
                        "libx264",
                        "-pix_fmt",
                        "yuv420p",
                        "-crf",
                        "18",
                        "-movflags",
                        "+faststart",
                        str(staged),
                    ]
                )
            else:
                palette = directory / "palette.png"
                _run(
                    command + ["-vf", "palettegen=stats_mode=full", "-frames:v", "1", str(palette)]
                )
                _run(
                    command
                    + [
                        "-i",
                        str(palette),
                        "-lavfi",
                        "paletteuse=dither=bayer",
                        "-loop",
                        "0",
                        str(staged),
                    ]
                )
            info.update(
                format=suffix[1:],
                encoder_version=version,
                loop_note=(
                    "GIF repeats; Q and multifrequency scenes are not necessarily seamless."
                    if suffix == ".gif"
                    else None
                ),
            )
            info["export_spec"]["format"] = suffix[1:]
            if not staged.exists() or staged.stat().st_size < 32:
                raise RuntimeError("Video encoder produced an invalid empty file.")
            _run(
                [
                    executable,
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-i",
                    str(staged),
                    "-f",
                    "null",
                    "-",
                ]
            )
    return path


def _plot_figure(width=800, height=500):
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg

    size(width, height, ExportLimits())
    fig = Figure(figsize=(width / 100, height / 100), dpi=100, layout="constrained", facecolor="#faf9f5")
    FigureCanvasAgg(fig)
    return fig


def _scientific_production(path, width, height, transparent, annotation):
    production = dict(width=width, height=height, dpi=100, transparent=transparent,
                      annotation=annotation, layout="scientific figure")
    result = {"production": production}
    if path.suffix.lower() in (".png", ".svg"):
        result["export_spec"] = dict(format=path.suffix.lower()[1:], width=width, height=height,
                                     transparent=transparent, annotation=annotation)
    return result


def _roots(radius, values):
    r, v = np.asarray(radius), np.asarray(values)
    roots = []
    for i in range(len(r) - 1):
        if v[i] * v[i + 1] < 0:
            roots.append(r[i] - v[i] * (r[i + 1] - r[i]) / (v[i + 1] - v[i]))
        elif 0 < i < len(r) - 1 and v[i] == 0 and v[i - 1] * v[i + 1] < 0:
            roots.append(r[i])
    return roots


def export_plot(
    bundle,
    path,
    kind="eigenfunctions",
    mode_id=None,
    *,
    transparent=False,
    annotation=True,
    overwrite=False,
    width=800,
    height=500,
):
    path = prepare(bundle, None, path, (".svg", ".png", ".pdf"))
    fig = _plot_figure(width, height)
    nodes = []
    if kind == "eigenfunctions":
        mode = next((m for m in bundle["modes"] if mode_id is None or m["id"] == mode_id), None)
        if mode is None:
            raise ValueError(f"No mode found for {mode_id!r}.")
        potential = any("potential" in r for r in mode["regions"])
        axes = np.atleast_1d(fig.subplots(2 if potential else 1, 1))
        ax = axes[0]
        for j, region in enumerate(mode["regions"]):
            rr = np.asarray(region["r_m"]) / 1000
            for key, color in zip(("u", "v", "w"), ("#267788", "#b66c28", "#705887")):
                ax.plot(rr, region[key], color=color, label=key.upper() if j == 0 else None)
                roots = _roots(rr, region[key])
                nodes.extend(
                    {"layer_id": region["layer_id"], "component": key, "radius_m": x * 1000}
                    for x in roots
                )
                ax.plot(roots, np.zeros(len(roots)), "o", color=color, markersize=3)
            ax.axvline(rr[0], color="#888888", linewidth=0.5, alpha=0.5)
            if potential and "potential" in region:
                axes[1].plot(rr, region["potential"], color="#437b65")
        ax.axhline(0, color="#777777", linewidth=0.5)
        ax.set(xlabel="Radius (km)", ylabel="Canonical eigenfunction (kg^(-1/2))")
        ax.legend()
        if annotation:
            ax.set_title(f"{mode['id']} — {mode['frequency_hz']*1000:.6g} mHz")
        if potential:
            axes[1].set(
                xlabel="Radius (km)",
                ylabel="Potential (" + mode["provenance"]["potential"]["units"] + ")",
            )
    elif kind in ("frequencies", "dispersion"):
        ax = fig.subplots()
        axes = [ax]
        for family, color in zip(("R", "S", "T"), ("#705887", "#267788", "#b66c28")):
            modes = [m for m in bundle["modes"] if m["family"] == family]
            if modes:
                ax.scatter(
                    [m["l"] for m in modes],
                    [m["frequency_hz"] * 1000 for m in modes],
                    label=family,
                    color=color,
                    s=22,
                )
        ax.set(xlabel="Angular degree l", ylabel="Frequency (mHz)")
        ax.legend()
    elif kind == "model":
        axes = fig.subplots(2, 1)
        ax = axes[0]
        for j, layer in enumerate(bundle["model"]["layers"]):
            r = np.asarray(layer["r_m"]) / 1000
            for key, label, color in (("vp_m_s", "Vp", "#267788"), ("vs_m_s", "Vs", "#b66c28")):
                axes[0].plot(
                    r, np.asarray(layer[key]) / 1000, label=label if j == 0 else None, color=color
                )
            axes[1].plot(r, layer["rho_kg_m3"], color="#705887")
            for a in axes:
                a.axvline(r[0], color="#888888", linewidth=0.5, alpha=0.5)
        axes[0].set(xlabel="Radius (km)", ylabel="Wave speed (km/s)")
        axes[0].legend()
        axes[1].set(xlabel="Radius (km)", ylabel="Density (kg/m^3)")
    else:
        raise ValueError("Plot kind must be eigenfunctions, frequencies, dispersion, or model.")
    for a in axes:
        a.grid(alpha=0.18)
    if annotation and kind != "eigenfunctions":
        ax.set_title(bundle["model"]["name"])
    with transaction(path, overwrite) as (staged, info):
        fig.savefig(staged, transparent=transparent)
        info.update(
            manifest(
                bundle,
                format=path.suffix[1:],
                plot_kind=kind,
                mode_id=mode_id,
                normalization="mass_integral_1",
                radial_zero_crossings=nodes,
                **_scientific_production(path, width, height, transparent, annotation),
            )
        )
    fig.clear()
    return path


def export_tables(bundle, output_dir, *, overwrite=False):
    path = prepare(bundle, None, output_dir, None)
    datasets = {
        "frequencies.csv": (
            ["mode_id", "family", "n", "l", "frequency_hz", "q", "normalization"],
            [
                [m[k] for k in ("id", "family", "n", "l", "frequency_hz", "q", "normalization")]
                for m in bundle["modes"]
            ],
        ),
        "eigenfunctions.csv": (
            [
                "mode_id",
                "layer_id",
                "radius_m",
                "u_kg^-0.5",
                "v_kg^-0.5",
                "w_kg^-0.5",
                "potential",
                "potential_units",
            ],
            [
                [
                    m["id"],
                    r["layer_id"],
                    radius,
                    r["u"][i],
                    r["v"][i],
                    r["w"][i],
                    r["potential"][i] if "potential" in r else None,
                    m["provenance"].get("potential", {}).get("units", ""),
                ]
                for m in bundle["modes"]
                for r in m["regions"]
                for i, radius in enumerate(r["r_m"])
            ],
        ),
        "model.csv": (
            [
                "layer_id",
                "phase",
                "radius_m",
                "density_kg_m3",
                "vp_m_s",
                "vs_m_s",
                "q_bulk",
                "q_shear",
            ],
            [
                [
                    l["id"],
                    l["phase"],
                    r,
                    l["rho_kg_m3"][i],
                    l["vp_m_s"][i],
                    l["vs_m_s"][i],
                    l["q_bulk"][i] if "q_bulk" in l else None,
                    l["q_shear"][i] if "q_shear" in l else None,
                ]
                for l in bundle["model"]["layers"]
                for i, r in enumerate(l["r_m"])
            ],
        ),
    }
    with transaction(path, overwrite, directory=True) as (staged, info):
        for name, (header, rows) in datasets.items():
            with (staged / name).open("w", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(header)
                writer.writerows(rows)
            (staged / (name + ".json")).write_text(
                json.dumps(manifest(bundle, format="csv", table=name), indent=2) + "\n"
            )
        # CSV blank cells cannot distinguish absent Q from explicit infinite-Q nulls.
        # Preserve the exact validated material input alongside its flat table.
        (staged / "model.json").write_text(
            json.dumps(bundle["model"], indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        )
        info.update(
            manifest(
                bundle,
                format="tables",
                files=[*datasets, "model.json"],
                material_json="model.json",
                q_blank_semantics="CSV blank means absent or infinite Q; model.json preserves field presence and explicit nulls.",
            )
        )
    return [path / name for name in datasets]


def export_probe(
    bundle, scene, probe, path, *, overwrite=False, transparent=False, annotation=True,
    width=None, height=None,
):
    from .data import validate_probe

    path = prepare(bundle, scene, path, (".csv", ".svg", ".png"))
    if transparent and path.suffix.lower() == ".csv":
        raise ValueError("CSV has no transparent background; transparency applies to PNG/SVG only.")
    if path.suffix.lower() == ".csv" and (width is not None or height is not None):
        raise ValueError("CSV has no image dimensions; width/height apply to PNG/SVG only.")
    width, height = 800 if width is None else width, 500 if height is None else height
    probe = validate_probe(
        {"radius_fraction": 1.0, "derivative": 0, "normalized": True, **probe}, bundle
    )
    times_s = probe["start_s"] + np.arange(int(probe["sample_count"])) * probe["step_s"]
    field = sample_probe(
        bundle,
        scene,
        probe["latitude_deg"],
        probe["longitude_deg"],
        probe["radius_fraction"],
        times_s,
        derivative=int(probe["derivative"]),
        normalized=probe["normalized"],
        layer_id=probe.get("layer_id"),
    )
    degree = int(probe["derivative"])
    units = ("1" if probe["normalized"] else "kg^(-1/2)") + (f" s^-{degree}" if degree else "")
    with transaction(path, overwrite) as (staged, info):
        if path.suffix.lower() == ".csv":
            with staged.open("w", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(["time_s"] + [f"{axis} [{units}]" for axis in "xyz"])
                writer.writerows(np.column_stack((times_s, field)))
        else:
            fig = _plot_figure(width, height)
            ax = fig.subplots()
            for i, color in enumerate(("#267788", "#b66c28", "#705887")):
                ax.plot(times_s, field[:, i], color=color, label="xyz"[i])
            ax.set(xlabel="Physical time (s)", ylabel=f"Derivative order {degree} ({units})")
            if annotation:
                ax.set_title("Modal receiver signal — not source-calibrated motion")
            ax.legend()
            ax.grid(alpha=0.18)
            fig.savefig(staged, transparent=transparent)
            fig.clear()
        info.update(
            manifest(
                bundle,
                scene,
                format=path.suffix[1:],
                probe=probe,
                units=units,
                coordinates="Cartesian x at lat0/lon0, y at lat0/lon90E, z north",
                **(_scientific_production(path, width, height, transparent, annotation)
                   if path.suffix.lower() != ".csv" else
                   {"production": {"layout": "table", "visual_options": "not applicable"}}),
            )
        )
    return path


def export_glb(*args, **kwargs):
    from .export_glb import write_glb

    return write_glb(*args, **kwargs)


def export_artifact(bundle, scene, path, spec=None, *, overwrite=False, limits=None):
    from .data import validate_export_spec

    spec = validate_export_spec(spec or {"format": Path(path).suffix.lower().lstrip(".")})
    common = {"overwrite": overwrite}
    fmt = spec["format"]
    if fmt in ("png", "gif", "mp4", "glb") and Path(path).suffix.lower() != "." + fmt:
        raise ValueError(f"ExportSpec format={fmt} requires output suffix .{fmt}.")
    if fmt != "glb" and any(
        spec[key] for key in ("omit_arrows", "omit_geography", "omit_analysis_overlays")
    ):
        raise ValueError(
            "Explicit omission options apply to GLB only; image/video exports preserve enabled layers."
        )
    if spec["transparent"] and fmt not in ("png", "svg"):
        raise ValueError(f"Transparency is not supported for {fmt}.")
    if fmt == "png":
        return export_image(
            bundle,
            scene,
            path,
            spec["width"],
            spec["height"],
            transparent=spec["transparent"],
            annotation=spec["annotation"],
            limits=limits,
            **common,
        )
    if fmt in ("mp4", "gif"):
        return export_video(
            bundle,
            scene,
            path,
            spec["duration_s"],
            spec["fps"],
            spec["width"],
            spec["height"],
            annotation=spec["annotation"],
            limits=limits,
            **common,
        )
    if fmt == "frames":
        return export_frames(
            bundle,
            scene,
            path,
            spec["duration_s"],
            spec["fps"] or 24,
            spec["width"],
            spec["height"],
            annotation=spec["annotation"],
            limits=limits,
            **common,
        )
    if fmt == "glb":
        return export_glb(
            bundle,
            scene,
            path,
            spec["duration_s"],
            spec["fps"] or 24,
            width=spec["width"],
            height=spec["height"],
            omit_arrows=spec["omit_arrows"],
            omit_geography=spec["omit_geography"],
            omit_analysis_overlays=spec["omit_analysis_overlays"],
            annotation=spec["annotation"],
            limits=limits,
            **common,
        )
    raise ValueError(
        "Use export_plot/export_probe/export_tables for explicit scientific SVG/CSV operations."
    )
