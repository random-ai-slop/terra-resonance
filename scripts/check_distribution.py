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
import math
import os
import shutil
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
    "assets/schema/project.schema.json", "assets/schema/agreement.schema.json",
    "vendor/Ouroboros/LICENSE", "vendor/README.md",
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
                     "examples/recipes/render.py", "examples/recipes/agreement.py", "docs/AGREEMENT.md",
                     "scripts/check_distribution.py"):
            require(name in files, f"Missing sdist file: {name}")
        for name in ("examples/recipes/agreement.py", "docs/AGREEMENT.md"):
            require(files[name] == (ROOT / name).read_bytes(),
                    f"Archived {name} differs from the accepted source")
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
    # A received scientific artifact must work without the original source paths.
    from earth_modes.agreement import load_agreement, export_agreement
    from earth_modes.data import save_bundle
    from earth_modes.analysis import export_comparison
    selected = ["T0_2:solid:sphere", "T1_2:solid:sphere"]
    save_bundle(bundle, "agreement-reference.json")
    save_bundle(pilot, "agreement-candidate.json")
    compute = [str(cli), "agreement", "--reference", "agreement-reference.json",
               "--candidate", "agreement-candidate.json", "--out", "agreement.json"]
    for identity in selected:
        compute.extend(["--pair", identity, identity])
    subprocess.run(compute, check=True)
    agreement = load_agreement("agreement.json")
    require(len(agreement["rows"]) == 2 and agreement["generator_version"] == version,
            "Installed agreement report identity differs")
    export_agreement(agreement, "agreement.svg", pair_index=1, width=640, height=480)
    svg = ET.parse("agreement.svg").getroot()
    require(svg.tag.endswith("svg") and any(e.tag.endswith("path") for e in svg.iter()),
            "Agreement SVG lacks native paths")
    require(not any(e.tag.endswith("image") for e in svg.iter()), "Agreement SVG embeds a raster plot")
    Path("agreement-reference.json").unlink(); Path("agreement-candidate.json").unlink()
    Path("agreement.json").unlink()
    for output, options in (("recovered.csv", []),
                            ("recovered.png", ["--pair-index", "0", "--width", "640", "--height", "480"])):
        subprocess.run([str(cli), "agreement", "--report", "agreement.svg.json", "--out", output, *options], check=True)
    with Path("recovered.csv").open(newline="") as stream:
        recovered = list(csv.DictReader(stream))
    require([int(r["pair_index"]) for r in recovered] == [0, 1], "CSV lost explicit pair order")
    require(all(float(row["delta_frequency_hz"]) == expected["delta_frequency_hz"]
                for row, expected in zip(recovered, agreement["rows"])), "CSV changed frequency differences")
    with Image.open("recovered.png") as picture:
        picture.load(); require(picture.size == (640, 480), "Recovered PNG dimensions differ")
    sidecar = load_agreement("recovered.png.json")
    require(sidecar["sources"] == agreement["sources"], "Received sidecar lost full sources")
    bad = json.loads(Path("agreement.svg.json").read_text())
    bad["rows"][0]["shape_distance"] = -1e-15
    Path("tampered.json").write_text(json.dumps(bad))
    rejected = subprocess.run([str(cli), "agreement", "--report", "tampered.json", "--out", "invalid.csv"],
                              capture_output=True, text=True)
    require(rejected.returncode != 0 and not Path("invalid.csv").exists()
            and not Path("invalid.csv.json").exists(), "Tampered report published a valid-looking artifact")
    export_comparison(bundle, pilot, [(selected[0], selected[0])], "legacy-comparison.csv")
    require(json.loads(Path("legacy-comparison.csv.json").read_text())["generator_version"] == version,
            "Existing comparison producer version regressed")
    subprocess.run([sys.executable, "-m", "pip", "check"], check=True)
    return {"package": str(package), "python": sys.version.split()[0], "version": version,
            "examples": ids, "solver_modes": len(bundle["modes"]), "pilot_modes": len(pilot["modes"]),
            "png": [320, 240], "svg": True, "probe_samples": 4, "glb_error": error,
            "agreement_pairs": 2, "agreement_sidecar_only_recovery": True,
            "agreement_tamper_rejected": True, "existing_comparison": True}



def check_recipe_outputs(folder, version):
    """Read actual outputs from a copied recipe run by an isolated installation."""
    from PIL import Image
    import earth_modes
    from earth_modes.agreement import load_agreement
    from earth_modes.data import load_bundle

    package = Path(earth_modes.__file__).resolve()
    require(sys.flags.isolated and "PYTHONPATH" not in os.environ
            and package.is_relative_to(Path(sys.prefix).resolve())
            and not package.is_relative_to(ROOT), "Recipe readback escaped isolated installation")

    names = ("cross-20", "cross-40", "refinement-default", "refinement-pilot")
    selected = "T0_2:solid:sphere"
    bundles = {f"{method}-{mesh}": load_bundle(folder / f"{method}-{mesh}.json")
               for method in ("default", "pilot") for mesh in (20, 40)}
    for name, bundle in bundles.items():
        mesh = int(name.rsplit("-", 1)[1])
        provenance = bundle["provenance"]
        require(provenance["request"]["mesh_size"] == mesh
                and provenance["effective_settings"]["mesh_counts"] == {"sphere": mesh}
                and provenance["effective_settings"]["actual_mesh_size"] == mesh,
                "Copied recipe mislabeled its actual sphere resolution")
    comparisons = (("default-20", "pilot-20"), ("default-40", "pilot-40"),
                   ("default-20", "default-40"), ("pilot-20", "pilot-40"))
    reports = {}
    for name, sources in zip(names, comparisons):
        report = reports[name] = load_agreement(folder / (name + ".json"))
        require(report["generator_version"] == version and len(report["rows"]) == 1,
                "Copied recipe report has wrong producer or pair count")
        require(report["pairs"] == [[selected, selected]], "Copied recipe selected a different branch")
        for role, source in zip(("reference", "candidate"), sources):
            require(report["sources"][role]["bundle"] == bundles[source],
                    "Copied recipe report lost source identity or comparison direction")
        row = report["rows"][0]
        require(math.isfinite(row["shape_distance"]) and row["shape_distance"] <= .003,
                "Copied recipe shape regression exceeds named sphere bound")
    evidence = json.loads((folder / "independent-frequency.json").read_text())
    results = evidence["results"]
    require(len(results) == 4 and all(math.isfinite(row["relative_error"])
                                    and 0 <= row["relative_error"] <= .005 for row in results),
            "Copied recipe independent frequency check failed")
    require({row["bundle"] for row in results} == {name + ".json" for name in bundles},
            "Copied recipe frequency evidence duplicated or omitted a source")
    reference_hz = evidence["reference"]["frequency_hz"]
    require(math.isfinite(reference_hz) and reference_hz > 0, "Invalid independent frequency")
    for result in results:
        mode = next(m for m in bundles[result["bundle"][:-5]]["modes"] if m["id"] == selected)
        require(result["mode_id"] == selected and result["frequency_hz"] == mode["frequency_hz"]
                and result["relative_error"] == abs(mode["frequency_hz"] - reference_hz) / reference_hz,
                "Copied recipe frequency evidence differs from its saved mode")
    require(set(evidence["agreement_reports"]) == {name + ".json" for name in names},
            "Copied recipe omitted a method/refinement report")
    for suffix in ("csv", "svg", "png"):
        sidecar = load_agreement(folder / f"cross-40.{suffix}.json")
        require({key: value for key, value in sidecar.items() if key != "export_production"}
                == reports["cross-40"], "Copied recipe sidecar differs from its complete report")
    with Image.open(folder / "cross-40.png") as picture:
        picture.load(); require(picture.size == (1200, 800), "Copied recipe PNG differs from default dimensions")
    vector = ET.parse(folder / "cross-40.svg").getroot()
    require(any(node.tag.endswith("path") for node in vector.iter())
            and not any(node.tag.endswith("image") for node in vector.iter()), "Copied recipe SVG is not native")
    with (folder / "cross-40.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
        require(len(rows) == 1 and float(rows[0]["shape_distance"]) == reports["cross-40"]["rows"][0]["shape_distance"],
                "Copied recipe scalar CSV differs from its report")
    return {"reports": list(names), "independent_reference_hz": evidence["reference"]["frequency_hz"],
            "package": str(package), "source_directions_checked": True,
            "actual_sphere_elements": [20, 40],
            "maximum_independent_frequency_error": max(row["relative_error"] for row in results),
            "png": [1200, 800], "native_svg": True,
            "artifact_sha256": {str(path.relative_to(folder)): hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in sorted(folder.iterdir()) if path.is_file()}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist-dir", type=Path, default=ROOT / "dist/ci")
    parser.add_argument("--tag", help="Require exact v<package version> metadata agreement")
    parser.add_argument("--metadata-only", action="store_true")
    parser.add_argument("--kind", choices=("wheel", "sdist", "both"), default="both")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--installed", metavar="VERSION", help=argparse.SUPPRESS)
    parser.add_argument("--recipe-dir", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.installed:
        result = (check_recipe_outputs(args.recipe_dir, args.installed) if args.recipe_dir
                  else installed_check(args.installed))
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
            recipe = scratch / "agreement-recipe.py"
            shutil.copyfile(ROOT / "examples/recipes/agreement.py", recipe)
            recipe_digest = hashlib.sha256(recipe.read_bytes()).hexdigest()
            for index, path in enumerate(selected):
                destination = scratch / f"env-{index}"
                venv.EnvBuilder(with_pip=True).create(destination)
                python = destination / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
                subprocess.run([str(python), "-m", "pip", "install", str(path)], check=True, cwd=scratch, env=env)
                work = scratch / f"run-{index}"; work.mkdir()
                report = scratch / f"check-{index}.json"
                subprocess.run([str(python), "-I", str(Path(__file__).resolve()), "--installed", version,
                                "--report", str(report)], check=True, cwd=work, env=env)
                recipe_output = work / "recipe-output"
                subprocess.run([str(python), "-I", str(recipe), str(recipe_output)],
                               check=True, cwd=work, env=env)
                recipe_report = scratch / f"recipe-check-{index}.json"
                subprocess.run([str(python), "-I", str(Path(__file__).resolve()), "--installed", version,
                                "--recipe-dir", str(recipe_output), "--report", str(recipe_report)],
                               check=True, cwd=work, env=env)
                recipe_result = json.loads(recipe_report.read_text())
                before = recipe_result["artifact_sha256"]
                refused = subprocess.run([str(python), "-I", str(recipe), str(recipe_output)],
                                         cwd=work, env=env, capture_output=True, text=True)
                require(refused.returncode != 0, "Copied recipe reused an existing output directory")
                after = {str(p.relative_to(recipe_output)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in recipe_output.iterdir() if p.is_file()}
                require(before == after, "Failed recipe retry changed existing outputs")
                checks.append({"archive": path.name, **json.loads(report.read_text()),
                               "copied_recipe": {"script_sha256": recipe_digest, **recipe_result,
                                                 "existing_directory_protected": True}})
        (folder / "SHA256SUMS").write_text("".join(f"{a['sha256']}  {a['name']}\n" for a in audits))
        result = {"version": version, "archives": audits, "installed": checks}
    if args.report:
        args.report.resolve().parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
