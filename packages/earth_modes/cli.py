"""One local command surface for reproducible models, analysis and presentation."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

from . import __version__
from .data import (
    _read_json,
    _write_json,
    default_scene,
    load_bundle,
    save_bundle,
    validate_bundle,
    validate_model,
    validate_project,
    validate_scene,
    validate_export_spec,
)


def _output(parser):
    parser.add_argument(
        "--out", required=True, type=Path, help="Output path; existing files are protected."
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="Explicitly replace an existing output."
    )


def parser():
    root = argparse.ArgumentParser(
        prog="terra",
        description="Earth normal modes: SI physics, explicit display scaling, reproducible exports.",
    )
    root.add_argument("--version", action="version", version=__version__)
    commands = root.add_subparsers(dest="command", required=True)
    example = commands.add_parser("example", help="List or save an installed self-contained example project.")
    example.add_argument("id", nargs="?")
    example.add_argument("--list", action="store_true", help="List stable example IDs in catalog order.")
    example.add_argument("--out", type=Path)
    example.add_argument("--overwrite", action="store_true")
    model = commands.add_parser("model", help="Write a validated SI material Model JSON.")
    model.add_argument("preset", choices=["prem", "homogeneous"])
    for flag in ("radius", "rho", "vp", "vs"):
        model.add_argument(
            "--" + flag,
            type=float,
            help={
                "radius": "Radius in metres.",
                "rho": "Density in kg/m³.",
                "vp": "P-wave speed in m/s.",
                "vs": "S-wave speed in m/s; zero means fluid.",
            }[flag],
        )
    _output(model)
    solve = commands.add_parser(
        "solve", help="Solve a Model JSON; config keys use the Python SI API."
    )
    solve.add_argument("model", type=Path)
    solve.add_argument(
        "--config", type=Path, help="JSON solve options; explicit flags override these values."
    )
    solve.add_argument("--families", nargs="+", choices=["R", "S", "T"], default=argparse.SUPPRESS)
    for flag, dest in [
        ("l-min", "l_min"),
        ("l-max", "l_max"),
        ("mesh", "mesh_size"),
        ("n-max", "n_max"),
    ]:
        solve.add_argument("--" + flag, dest=dest, type=int, default=argparse.SUPPRESS)
    for flag in ("f-min-mhz", "f-max-mhz", "target-mhz", "memory-mib"):
        solve.add_argument("--" + flag, type=float, default=argparse.SUPPRESS)
    solve.add_argument(
        "--gravity",
        type=int,
        choices=[0, 1, 2],
        default=argparse.SUPPRESS,
        help="0: elastic; 1: background gravity; 2: perturbed self-gravity.",
    )
    for flag in ("linear-q", "convergence-check"):
        solve.add_argument(
            "--" + flag, action=argparse.BooleanOptionalAction, default=argparse.SUPPRESS
        )
    _output(solve)
    inspect = commands.add_parser(
        "inspect", help="Inspect frequencies and separate numerical quality evidence."
    )
    inspect.add_argument("input", type=Path)
    inspect.add_argument("--json", action="store_true", help="Print a machine-readable summary.")
    inspect.add_argument(
        "--details",
        action="store_true",
        help="Include full quality evidence and spectral group metadata.",
    )
    scene = commands.add_parser("scene", help="Create a recommended scene bound to a bundle hash.")
    scene.add_argument("input", type=Path)
    scene.add_argument(
        "--mode-id", help="Choose the initial mode; default is the first bundle mode."
    )
    scene.add_argument("--m", type=int, default=0)
    scene.add_argument("--wireframe-spacing-deg", choices=["legacy", "5", "10", "15", "30"],
                       help="Surface grid spacing in material degrees; legacy retains triangle edges. Does not change solver mesh.")
    _output(scene)
    export = commands.add_parser(
        "export", help="Render a bundle + scene, or a saved self-contained project."
    )
    export.add_argument("input", type=Path)
    export.add_argument(
        "scene",
        type=Path,
        nargs="?",
        help="Required for a bundle; a project contains its own scene.",
    )
    export.add_argument(
        "--kind",
        choices=[
            "field",
            "eigenfunctions",
            "model",
            "frequencies",
            "dispersion",
            "tables",
            "frames",
        ],
        default="field",
    )
    export.add_argument("--mode-id", help="Mode for the scientific eigenfunction plot.")
    for flag in ("width", "height", "fps"):
        export.add_argument("--" + flag, type=int)
    export.add_argument(
        "--duration",
        type=float,
        help="Playback duration in seconds; physical speed remains in SceneSpec.",
    )
    export.add_argument("--transparent", action=argparse.BooleanOptionalAction, default=None)
    export.add_argument("--annotation", action=argparse.BooleanOptionalAction, default=None)
    for flag in ("omit-arrows", "omit-geography", "omit-analysis-overlays"):
        export.add_argument(
            "--" + flag,
            action=argparse.BooleanOptionalAction,
            default=None,
            help="Explicit GLB-only omission; source scene is unchanged.",
        )
    _output(export)
    probe = commands.add_parser(
        "probe",
        help="Sample a fixed material point; raw units are canonical, not earthquake metres.",
    )
    probe.add_argument("input", type=Path)
    probe.add_argument("scene", type=Path, nargs="?")
    for flag in ("lat", "lon", "radius", "start", "duration", "step"):
        probe.add_argument(
            "--" + flag,
            type=float,
            help="Radius is r/R; times are physical seconds." if flag == "radius" else None,
        )
    probe.add_argument("--layer-id", help="Choose a material side exactly at an interface.")
    probe.add_argument("--derivative", type=int, choices=[0, 1, 2], default=None)
    for flag in ("width", "height"):
        probe.add_argument("--" + flag, type=int)
    for flag in ("transparent", "annotation"):
        probe.add_argument("--" + flag, action=argparse.BooleanOptionalAction, default=None)
    probe.add_argument(
        "--raw",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Canonical mass-normalized field [kg^(-1/2)]; not calibrated source motion.",
    )
    _output(probe)
    compare = commands.add_parser(
        "compare",
        help="Compare explicit identities in separate models; no automatic mode tracking.",
    )
    compare.add_argument("reference", type=Path)
    compare.add_argument("candidate", type=Path)
    compare.add_argument("--family", choices=["R", "S", "T"])
    compare.add_argument("--l", type=int)
    compare.add_argument("--n", type=int)
    compare.add_argument("--reference-mode")
    compare.add_argument("--candidate-mode")
    _output(compare)
    return root


def _load(path, scene_path=None, require_scene=False):
    value = _read_json(path)
    if isinstance(value, dict) and value.get("format") == "terra-project":
        validate_project(value)
        bundle, scene, project = value["bundle"], value["scene"], value
        if scene_path is not None:
            raise ValueError(
                "A project already contains a scene; do not provide a second scene file."
            )
    else:
        bundle, project = validate_bundle(value), {}
        scene = _read_json(scene_path) if scene_path is not None else None
        if scene is not None:
            validate_scene(scene, bundle)
    if require_scene and scene is None:
        raise ValueError("Provide a SceneSpec path after the bundle, or use a saved terra-project.")
    return bundle, scene, project


def _protected(path, overwrite, sidecar=False):
    if not overwrite and (path.exists() or (sidecar and Path(str(path) + ".json").exists())):
        raise FileExistsError(f"Output exists: {path}; pass --overwrite to replace it.")


def _quality(bundle):
    for mode in bundle["modes"]:
        quality = mode["provenance"]["quality"]
        print(
            f"  {mode['id']}: {quality['status']} · {mode['frequency_hz']*1000:.8g} mHz",
            file=sys.stderr,
        )
        for note in quality["warnings"]:
            print("    warning: " + note, file=sys.stderr)


def _solve(args):
    from .solver import solve, _request

    values = vars(args)
    options = _read_json(args.config) if args.config else {}
    if not isinstance(options, dict):
        raise ValueError("Solve config must be a JSON object of Python solve API options.")
    names = (
        "families",
        "l_min",
        "l_max",
        "mesh_size",
        "n_max",
        "gravity",
        "linear_q",
        "convergence_check",
        "memory_mib",
    )
    options.update({key: values[key] for key in names if key in values})
    for source, dest in [
        ("f_min_mhz", "frequency_min_hz"),
        ("f_max_mhz", "frequency_max_hz"),
        ("target_mhz", "target_frequency_hz"),
    ]:
        if source in values:
            options[dest] = values[source] * 0.001
    options = _request(options)
    model = validate_model(_read_json(args.model))
    _protected(args.out, args.overwrite)
    print(
        f"Solving {model['name']}: families {','.join(options['families'])}; l={options['l_min']}..{options['l_max']}; mesh={options['mesh_size']}; gravity={options['gravity']} → {args.out}",
        file=sys.stderr,
        flush=True,
    )
    bundle = solve(model, **options)
    save_bundle(bundle, args.out, overwrite=args.overwrite)
    _quality(bundle)
    print(f"Saved {len(bundle['modes'])} modes: {args.out}")


def _image_options(args, project, table=False):
    """Resolve image production without importing movie semantics into curves."""
    keys = ("width", "height", "transparent", "annotation")
    explicit = {key: getattr(args, key) for key in keys if getattr(args, key) is not None}
    if table:
        if explicit:
            raise ValueError("CSV/tables do not support explicit image options: " + ", ".join(explicit))
        return {}
    result = {"width": 800, "height": 500, "transparent": False, "annotation": True}
    if "export" in project:
        saved = validate_export_spec(project["export"])
        result.update({key: saved[key] for key in keys})
    result.update(explicit)
    return result


def _export(args):
    from .export import export_artifact, export_plot, export_tables
    from .export_common import ExportLimits, times
    from .export_render import geometry

    bundle, scene, project = _load(
        args.input, args.scene, require_scene=args.kind in ("field", "frames")
    )
    _protected(args.out, args.overwrite, sidecar=True)
    _quality(bundle)
    special = args.kind not in ("field", "frames")
    if special:
        ignored = [
            key
            for key in (
                "fps",
                "duration",
                "omit_arrows",
                "omit_geography",
                "omit_analysis_overlays",
            )
            if getattr(args, key) is not None
        ]
        if ignored:
            raise ValueError(
                "Scientific plots/tables do not support these options: " + ", ".join(ignored)
            )
        if args.kind == "tables":
            _image_options(args, project, table=True)
            if (
                args.transparent is not None
                or args.annotation is not None
                or args.mode_id is not None
            ):
                raise ValueError("tables has no transparency, annotation or mode filter options.")
            return export_tables(bundle, args.out, overwrite=args.overwrite)
        if args.mode_id and args.kind != "eigenfunctions":
            raise ValueError("--mode-id applies only to --kind eigenfunctions.")
        return export_plot(
            bundle,
            args.out,
            kind=args.kind,
            mode_id=args.mode_id,
            **_image_options(args, project),
            overwrite=args.overwrite,
        )
    if args.mode_id:
        raise ValueError(
            "Change scene terms to select a visual mode; --mode-id is for eigenfunction plots."
        )
    spec = dict(project.get("export", {}))
    spec["format"] = "frames" if args.kind == "frames" else args.out.suffix.lower().lstrip(".")
    for key in (
        "width",
        "height",
        "fps",
        "transparent",
        "annotation",
        "omit_arrows",
        "omit_geography",
        "omit_analysis_overlays",
    ):
        if getattr(args, key) is not None:
            spec[key] = getattr(args, key)
    if args.duration is not None:
        spec["duration_s"] = args.duration
    spec = validate_export_spec(spec)
    effective = scene
    if spec["format"] == "glb":
        from .export_glb import effective_glb_scene
        effective, _ = effective_glb_scene(scene, **{
            key: spec[key] for key in ("omit_arrows", "omit_geography", "omit_analysis_overlays")
        })
    resource = geometry(bundle, effective, ExportLimits(), preflight_only=True)
    print("Geometry preflight: " + json.dumps(resource), file=sys.stderr)
    if spec["format"] in ("gif", "mp4", "frames", "glb"):
        fps = spec["fps"] or (20 if spec["format"] == "gif" else 24)
        _, physical, _ = times(
            bundle,
            scene,
            spec["duration_s"],
            fps,
            ExportLimits(),
            check_alias=spec["format"] != "glb",
        )
        if spec["format"] == "glb":
            endpoint = scene["time_s"] + spec["duration_s"] * scene["time_scale"]
            print(
                f"GLB physical window t={scene['time_s']:.8g}..{endpoint:.8g} s; "
                "adaptive morph keys are independent of nominal video fps; "
                "scalar colors are frozen at the start.",
                file=sys.stderr,
            )
        else:
            print(
                f"{len(physical)} rendered frames; physical t={physical[0]:.8g}..{physical[-1]:.8g} s; "
                f"RGBA temporary estimate={4*spec['width']*spec['height']*len(physical)} bytes.",
                file=sys.stderr,
            )
    else:
        print(
            f"Physical t={scene['time_s']:.8g} s; {spec['width']} × {spec['height']} pixels.",
            file=sys.stderr,
        )
    return export_artifact(bundle, scene, args.out, spec, overwrite=args.overwrite)


def _probe(args):
    from .export import export_probe

    bundle, scene, project = _load(args.input, args.scene, require_scene=True)
    spec = dict(project.get("probe", {}))
    for key, name in [
        ("lat", "latitude_deg"),
        ("lon", "longitude_deg"),
        ("radius", "radius_fraction"),
        ("start", "start_s"),
        ("step", "step_s"),
        ("layer_id", "layer_id"),
        ("derivative", "derivative"),
    ]:
        if getattr(args, key) is not None:
            spec[name] = getattr(args, key)
    spec.setdefault("start_s", scene["time_s"])
    spec.setdefault("radius_fraction", 1.0)
    spec.setdefault("normalized", True)
    spec.setdefault("derivative", 0)
    if args.raw is not None:
        spec["normalized"] = not args.raw
    if args.duration is not None:
        duration, step = args.duration, spec.get("step_s")
        if (
            not math.isfinite(duration)
            or duration <= 0
            or step is None
            or not math.isfinite(step)
            or step <= 0
        ):
            raise ValueError("--duration and --step must be finite positive physical seconds.")
        quotient = duration / step
        if not math.isfinite(quotient) or quotient > 1_000_000:
            raise ValueError("Probe exceeds 1,000,000 samples; increase --step.")
        count = math.ceil(quotient)
        start = spec["start_s"]
        end = start + duration
        if not math.isfinite(start) or start < 0 or not math.isfinite(end) or end <= start:
            raise ValueError("Probe duration must advance the finite nonnegative start time.")
        if count > 1 and step < math.ulp(start):
            raise ValueError("Probe step is below the floating-point time resolution at this start.")
        while count > 0 and start + (count - 1) * step >= end:
            count -= 1
        spec["sample_count"] = count
    elif args.step is not None:
        raise ValueError("Changing --step requires --duration so the probe window is explicit.")
    missing = [
        key
        for key in ("latitude_deg", "longitude_deg", "step_s", "sample_count")
        if key not in spec
    ]
    if missing:
        raise ValueError(
            "Probe requires --lat, --lon, --duration and --step (or a saved ProbeSpec); missing "
            + ", ".join(missing)
        )
    return export_probe(bundle, scene, spec, args.out, overwrite=args.overwrite,
                        **_image_options(args, project, table=args.out.suffix.lower() == ".csv"))


def run(args):
    if args.command == "example":
        from .examples import list_examples, load_example
        from .data import save_project
        if args.list:
            if args.out or args.overwrite or args.id is not None:
                raise ValueError("example --list does not accept an ID, output path, or overwrite")
            print("\n".join(list_examples()))
        else:
            if args.out is None:
                raise ValueError("example requires --out project.json (or --list)")
            save_project(load_example(args.id or "03-indices"), args.out, overwrite=args.overwrite)
            print(args.out)
    elif args.command == "model":
        from .models import prem_model, homogeneous_model

        if args.preset == "prem":
            if any(getattr(args, key) is not None for key in ("radius", "rho", "vp", "vs")):
                raise ValueError(
                    "PREM has fixed documented parameters; material flags apply to homogeneous."
                )
            model = prem_model()
        else:
            options = {
                name: getattr(args, key)
                for key, name in [
                    ("radius", "radius_m"),
                    ("rho", "rho_kg_m3"),
                    ("vp", "vp_m_s"),
                    ("vs", "vs_m_s"),
                ]
                if getattr(args, key) is not None
            }
            model = homogeneous_model(**options)
        _write_json(model, args.out, overwrite=args.overwrite)
        print(args.out)
    elif args.command == "solve":
        _solve(args)
    elif args.command == "inspect":
        bundle, _, _ = _load(args.input)
        summary = dict(
            model=bundle["model"]["name"],
            mode_count=len(bundle["modes"]),
            groups=bundle["provenance"].get("groups", []),
            modes=[
                dict(
                    id=m["id"],
                    family=m["family"],
                    n=m["n"],
                    l=m["l"],
                    frequency_hz=m["frequency_hz"],
                    period_s=1 / m["frequency_hz"],
                    q=m["q"],
                    quality=m["provenance"]["quality"],
                )
                for m in bundle["modes"]
            ],
        )
        if args.json:
            print(json.dumps(summary, indent=2, ensure_ascii=False))
        else:
            print(f"{summary['model']} · {summary['mode_count']} modes")
            for mode in summary["modes"]:
                print(
                    f"{mode['id']:24} {mode['frequency_hz']*1000:12.7g} mHz {mode['period_s']:12.6g} s  Q={mode['q']}  {mode['quality']['status']}"
                )
                if args.details:
                    print("  quality evidence: " + json.dumps(mode["quality"], ensure_ascii=False))
            warnings = {}
            for mode in summary["modes"]:
                for warning in mode["quality"]["warnings"]:
                    warnings.setdefault(warning, []).append(mode["id"])
            for warning, mode_ids in warnings.items():
                print(f"Warning ({len(mode_ids)} modes): {warning}")
                if args.details:
                    print("  " + ", ".join(mode_ids))
            groups = summary["groups"]
            if groups:
                if args.details:
                    print("Spectral groups: " + json.dumps(groups, ensure_ascii=False))
                else:
                    statuses = {
                        key: sum(g["status"] == key for g in groups)
                        for key in ("success", "not_applicable")
                    }
                    truncated = sum(
                        g["spectral_completeness"]["status"] == "truncated" for g in groups
                    )
                    print(
                        f"Groups: {len(groups)}; successful={statuses['success']}; "
                        f"not applicable={statuses['not_applicable']}; truncated={truncated}. "
                        "Use --details or --json for evidence."
                    )
    elif args.command == "scene":
        bundle, _, _ = _load(args.input)
        scene = default_scene(bundle)
        if args.mode_id:
            if not any(m["id"] == args.mode_id for m in bundle["modes"]):
                raise ValueError("Unknown --mode-id: " + args.mode_id)
            # Recompute recommended time and color defaults for the selected mode.
            from .data import default_color_limit

            mode = next(m for m in bundle["modes"] if m["id"] == args.mode_id)
            scene["terms"][0]["mode_id"] = args.mode_id
            scene["time_scale"] = 1 / (8 * mode["frequency_hz"])
            scene["trajectory"]["duration_s"] = 1 / mode["frequency_hz"]
            scene["color_limit"] = default_color_limit(bundle, scene["terms"])
        scene["terms"][0]["m"] = args.m
        if args.wireframe_spacing_deg is not None:
            scene["wireframe_spacing_deg"] = None if args.wireframe_spacing_deg == "legacy" else int(args.wireframe_spacing_deg)
        validate_scene(scene, bundle)
        _write_json(scene, args.out, overwrite=args.overwrite)
        print(args.out)
    elif args.command == "export":
        print(_export(args))
    elif args.command == "probe":
        print(_probe(args))
    elif args.command == "compare":
        from .analysis import select_pair, export_comparison

        a, b = load_bundle(args.reference), load_bundle(args.candidate)
        explicit = (args.reference_mode, args.candidate_mode)
        if any(explicit):
            if not all(explicit) or any(
                value is not None for value in (args.family, args.l, args.n)
            ):
                raise ValueError(
                    "Use both explicit mode IDs, or family/l/n selection; do not combine them."
                )
            pair = explicit
        else:
            if any(value is None for value in (args.family, args.l, args.n)):
                raise ValueError("Provide --family, --l and --n, or both explicit mode IDs.")
            pair = select_pair(a, b, args.family, args.l, args.n)
        print(export_comparison(a, b, [pair], args.out, overwrite=args.overwrite))


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        run(args)
        return 0
    except KeyboardInterrupt:
        print("terra: interrupted; unfinished output was not committed.", file=sys.stderr)
        return 130
    except (ValueError, TypeError, KeyError, OSError, RuntimeError) as error:
        print(f"terra: {error}", file=sys.stderr)
        diagnostics = getattr(error, "diagnostics", None)
        if diagnostics:
            print(json.dumps(diagnostics, ensure_ascii=False, default=str), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
