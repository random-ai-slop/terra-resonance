#!/usr/bin/env python3
"""Audit current-version archives and exercise independently installed packages.

Run after ``python -m build --outdir dist/ci``. Each archive is installed into
its own temporary venv; the child runs with -I outside the source checkout.
This checks package usability, not the independent full numerical benchmarks.
"""
from __future__ import annotations

import argparse
import ast
import csv
from email.parser import BytesParser
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import venv
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "assets/examples/prem-modes.json", "assets/examples/lessons.json",
    "assets/prem-isotropic-3mhz.txt", "assets/coastlines.json", "assets/palettes.json",
    "assets/schema/mode-bundle.schema.json", "assets/schema/scene.schema.json",
    "assets/schema/project.schema.json", "vendor/Ouroboros/LICENSE", "vendor/README.md",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def metadata_version(tag=None):
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    version = project["version"]
    tree = ast.parse((ROOT / "packages/earth_modes/__init__.py").read_text())
    declared = next(ast.literal_eval(node.value) for node in tree.body
                    if isinstance(node, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "__version__" for t in node.targets))
    require(declared == version, "pyproject and earth_modes.__version__ disagree")
    web = json.loads((ROOT / "apps/web/package.json").read_text())
    require(web["version"] == version, "Python and web package versions disagree")
    if tag is not None:
        require(tag == "v" + version, f"Tag {tag!r} does not match v{version}")
    return version


def audit(path, version):
    wheel = path.suffix == ".whl"
    if wheel:
        with zipfile.ZipFile(path) as archive:
            files = {n: archive.read(n) for n in archive.namelist() if not n.endswith("/")}
        metadata = next(data for name, data in files.items() if name.endswith(".dist-info/METADATA"))
        prefix = "earth_modes/"
    else:
        with tarfile.open(path) as archive:
            files = {m.name.split("/", 1)[1]: archive.extractfile(m).read()
                     for m in archive.getmembers() if m.isfile() and "/" in m.name}
        metadata = files["PKG-INFO"]
        prefix = "packages/earth_modes/"
        for name in ("README.md", "LICENSE", "pyproject.toml", "MANIFEST.in",
                     "examples/recipes/render.py", "scripts/check_distribution.py"):
            require(name in files, f"Missing sdist file: {name}")
    fields = BytesParser().parsebytes(metadata)
    require(fields["Name"] == "terra-resonance" and fields["Version"] == version,
            f"Wrong distribution metadata in {path.name}")
    project_license = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["license"]
    require(fields["License-Expression"] == project_license, "SPDX license differs from source metadata")
    require(any(name.endswith("LICENSE") and "dist-info/licenses" in name for name in files)
            if wheel else "LICENSE" in files, "Missing distribution license text")
    for name in REQUIRED:
        require(prefix + name in files, f"Missing packaged resource: {name}")
    require(not any("__pycache__" in n or n.endswith(".pyc") for n in files), "Bytecode in distribution")
    require(not any(n == "docs/team/CURRENT.md" or n.startswith("docs/team/handoffs/")
                    or "/.codex/" in n for n in files), "Operational/private state in distribution")
    runtime = {n[len(prefix):]: data for n, data in files.items() if n.startswith(prefix)}
    expected = {str(p.relative_to(ROOT / "packages/earth_modes")): p.read_bytes()
                for p in (ROOT / "packages/earth_modes").rglob("*")
                if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"
                and p.name != ".DS_Store"}
    require(runtime == expected, f"Runtime/assets differ from source in {path.name}")
    return {"name": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes": path.stat().st_size, "runtime_files": len(runtime),
            "license_expression": fields["License-Expression"]}


def installed_check(version):
    import earth_modes
    import numpy as np
    from importlib import metadata, resources
    from PIL import Image
    from earth_modes import list_examples, load_example
    from earth_modes.data import default_scene, validate_bundle, validate_project
    from earth_modes.models import homogeneous_model
    from earth_modes.solver import solve
    from earth_modes.experimental import solve_toroidal
    from earth_modes.export import export_image, export_plot, export_probe, export_glb
    from earth_modes.fields import evaluate_field

    package = Path(earth_modes.__file__).resolve()
    require(package.is_relative_to(Path(sys.prefix).resolve()), "Import escaped installed venv")
    require(not package.is_relative_to(ROOT), "Source package shadowed installation")
    require(sys.flags.isolated and "PYTHONPATH" not in os.environ, "Installed check needs -I and no PYTHONPATH")
    require(metadata.version("terra-resonance") == version, "Installed version mismatch")
    for name in REQUIRED:
        require(resources.files("earth_modes").joinpath(name).is_file(), f"Installed resource missing: {name}")
    ids = list_examples()
    require(len(ids) == 6 and len(set(ids)) == 6, "Expected six distinct installed examples")
    for identity in ids:
        project = load_example(identity)
        validate_project(project)
        original = json.dumps(project, sort_keys=True)
        project["scene"]["terms"][0]["amplitude"] = .12345
        require(json.dumps(load_example(identity), sort_keys=True) == original, "Example loads share mutable state")
    cli = Path(sys.executable).with_name("terra.exe" if os.name == "nt" else "terra")
    subprocess.run([str(cli), "example", "03-indices", "--out", "example.json"], check=True)
    validate_project(json.loads(Path("example.json").read_text()))
    model = homogeneous_model(radius_m=1e6, rho_kg_m3=5000, vp_m_s=8000, vs_m_s=4000)
    bundle = solve(model, families=["T"], l_min=2, l_max=2, mesh_size=20,
                   gravity=0, frequency_max_hz=.01)
    pilot = solve_toroidal(model, l_min=2, l_max=2, mesh_size=20, frequency_max_hz=.01)
    validate_bundle(pilot)
    require(bool(bundle["modes"]) and bool(pilot["modes"]), "Small installed solvers returned no modes")
    scene = default_scene(bundle)
    scene.update(quality="draft", surface="wireframe", wireframe_spacing_deg=30)
    scene["color"] = "magnitude"
    export_image(bundle, scene, "field.png", width=320, height=240)
    with Image.open("field.png") as image:
        image.load()
        require(image.size == (320, 240), "PNG dimensions differ")
    export_plot(bundle, "radial.svg", mode_id=scene["terms"][0]["mode_id"])
    require(ET.parse("radial.svg").getroot().tag.endswith("svg"), "Invalid SVG")
    probe = dict(latitude_deg=20, longitude_deg=30, start_s=0, step_s=1, sample_count=4)
    export_probe(bundle, scene, probe, "probe.csv")
    rows = list(csv.reader(Path("probe.csv").open()))
    require(len(rows) == 5 and np.isfinite(np.asarray(rows[1:], float)).all(), "Invalid probe CSV")
    export_glb(bundle, scene, "field.glb", duration_s=.25)
    raw = Path("field.glb").read_bytes()
    require(struct.unpack_from("<4sII", raw) == (b"glTF", 2, len(raw)), "Invalid GLB header")
    length, kind = struct.unpack_from("<I4s", raw, 12)
    require(kind == b"JSON", "Missing GLB JSON chunk")
    doc = json.loads(raw[20:20 + length])
    binary_length, binary_kind = struct.unpack_from("<I4s", raw, 20 + length)
    require(binary_kind == b"BIN\0" and 28 + length + binary_length == len(raw), "Invalid GLB binary chunk")
    binary = raw[28 + length:]

    def array(index):
        a = doc["accessors"][index]; view = doc["bufferViews"][a["bufferView"]]
        width = {"SCALAR": 1, "VEC3": 3, "VEC4": 4}[a["type"]]
        start = view.get("byteOffset", 0) + a.get("byteOffset", 0)
        require(start + a["count"] * width * 4 <= len(binary), "GLB accessor exceeds buffer")
        return np.frombuffer(binary, dtype={5126: "<f4", 5125: "<u4"}[a["componentType"]],
                             count=a["count"] * width, offset=start).reshape(-1, width)

    for i in range(len(doc["accessors"])):
        array(i)
    primitive = doc["meshes"][0]["primitives"][0]
    require(primitive["mode"] == 1, "Grid export is not a line primitive")
    points = array(primitive["attributes"]["POSITION"]).astype(float)
    points /= np.linalg.norm(points, axis=1)[:, None]  # Restore the exact mathematical shell radius.
    targets = np.stack([array(t["POSITION"]) for t in primitive["targets"]])
    sampler = doc["animations"][0]["samplers"][0]
    keys = array(sampler["input"]).ravel(); weights = array(sampler["output"]).reshape(len(keys), len(targets))
    time = float(keys[-1]) * .413
    upper = np.searchsorted(keys, time); alpha = (time - keys[upper - 1]) / (keys[upper] - keys[upper - 1])
    displacement = np.einsum("t,tnc->nc", (1-alpha)*weights[upper-1]+alpha*weights[upper], targets)
    reference = scene["deformation"] * evaluate_field(bundle, scene["terms"], points*model["radius_m"], time*scene["time_scale"])
    bound = scene["deformation"] * scene["color_limit"]
    error = float(np.max(np.linalg.norm(displacement-reference, axis=1)))
    require(error <= .01*bound, "GLB non-key reconstruction exceeds fixed bound")
    subprocess.run([sys.executable, "-m", "pip", "check"], check=True)
    return {"package": str(package), "python": sys.version.split()[0], "version": version,
            "examples": ids, "solver_modes": len(bundle["modes"]), "pilot_modes": len(pilot["modes"]),
            "png": [320, 240], "svg": True, "probe_samples": 4, "glb_error": error}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist-dir", type=Path, default=ROOT / "dist/ci")
    parser.add_argument("--tag", help="Require exact v<package version> metadata agreement")
    parser.add_argument("--metadata-only", action="store_true")
    parser.add_argument("--kind", choices=("wheel", "sdist", "both"), default="both")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--installed", metavar="VERSION", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.installed:
        result = installed_check(args.installed)
    else:
        version = metadata_version(args.tag)
        if args.metadata_only:
            print(version)
            return
        folder = args.dist_dir.resolve()
        paths = [folder / f"terra_resonance-{version}-py3-none-any.whl",
                 folder / f"terra_resonance-{version}.tar.gz"]
        audits = [audit(path, version) for path in paths]
        selected = paths if args.kind == "both" else [paths[0 if args.kind == "wheel" else 1]]
        checks = []
        with tempfile.TemporaryDirectory(prefix="terra-distribution-") as directory:
            scratch = Path(directory)
            env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
            env.update(MPLCONFIGDIR=str(scratch / "mpl"), XDG_CACHE_HOME=str(scratch / "cache"),
                       MPLBACKEND="Agg", OPENBLAS_NUM_THREADS="1")
            for index, path in enumerate(selected):
                destination = scratch / f"env-{index}"
                venv.EnvBuilder(with_pip=True).create(destination)
                python = destination / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
                subprocess.run([str(python), "-m", "pip", "install", str(path)], check=True, cwd=scratch, env=env)
                work = scratch / f"run-{index}"; work.mkdir()
                report = scratch / f"check-{index}.json"
                subprocess.run([str(python), "-I", str(Path(__file__).resolve()), "--installed", version,
                                "--report", str(report)], check=True, cwd=work, env=env)
                checks.append({"archive": path.name, **json.loads(report.read_text())})
        (folder / "SHA256SUMS").write_text("".join(f"{a['sha256']}  {a['name']}\n" for a in audits))
        result = {"version": version, "archives": audits, "installed": checks}
    if args.report:
        args.report.resolve().parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
