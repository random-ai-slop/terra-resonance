#!/usr/bin/env python3
"""Synchronize canonical scientific resources for the package and website."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tempfile
import os

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    "coastlines.json": ROOT / "packages/earth_modes/assets/coastlines.json",
    "palettes.json": ROOT / "packages/earth_modes/assets/palettes.json",
    "prem-modes.json": ROOT / "examples/prem-modes.json",
    "lessons.json": ROOT / "examples/lessons/catalog.json",
    "field-reference.json": ROOT / "examples/field-reference.json",
}
DESTINATION = ROOT / "apps/web/public/data"
PACKAGE_DESTINATION = ROOT / "packages/earth_modes/assets/examples"


def synchronize(check=False, target="all"):
    """Copy generated destinations, or verify them without writing.

    The target selector supports separately owned package and Site checkouts;
    the default command always checks or synchronizes every destination.
    """
    from earth_modes.data import bundle_hash, load_bundle, make_project

    if target not in ("all", "web", "package"):
        raise ValueError("target must be all, web or package")
    canonical = load_bundle(SOURCES["prem-modes.json"])
    catalog = json.loads(SOURCES["lessons.json"].read_text())
    if catalog.get("bundle_hash") != bundle_hash(canonical):
        raise ValueError(
            "Lesson catalog does not match the canonical PREM bundle; regenerate lessons first."
        )
    for lesson in catalog["lessons"]:
        make_project(
            canonical, lesson["scene"], lesson.get("probe"), lesson.get("export")
        )
    destinations = []
    if target in ("all", "web"):
        for name in SOURCES:
            path = (
                ROOT / "apps/web/tests/fixtures/field-reference.json"
                if name == "field-reference.json"
                else DESTINATION / name
            )
            destinations.append((name, name, path))
    if target in ("all", "package"):
        for name in ("prem-modes.json", "lessons.json"):
            destinations.append(("package/" + name, name, PACKAGE_DESTINATION / name))
    records, stale = {}, []
    for key, name, path in destinations:
        source = SOURCES[name]
        raw = source.read_bytes()
        json.loads(raw)
        digest = hashlib.sha256(raw).hexdigest()
        current = (
            hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        )
        if current != digest:
            stale.append(key)
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                temporary = None
                try:
                    with tempfile.NamedTemporaryFile(
                        dir=path.parent, prefix="." + name, delete=False
                    ) as stream:
                        temporary = Path(stream.name)
                        stream.write(raw)
                    os.replace(temporary, path)
                finally:
                    if temporary is not None:
                        temporary.unlink(missing_ok=True)
        records[key] = dict(
            source=str(source.relative_to(ROOT)),
            destination=str(path.relative_to(ROOT)),
            sha256=digest,
            bytes=len(raw),
            status="stale" if check and current != digest else "identical",
        )
        if not check and hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise RuntimeError(f"Hash mismatch after writing {path}")
    print(json.dumps(records, indent=2))
    if check and stale:
        raise ValueError(
            "Stale generated assets: "
            + ", ".join(stale)
            + "; run scripts/sync_web_assets.py"
        )
    return records


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="Read-only verification for CI/release."
    )
    parser.add_argument(
        "--target",
        choices=("all", "web", "package"),
        default="all",
        help="Select destinations; all is the release default.",
    )
    args = parser.parse_args()
    try:
        synchronize(args.check, args.target)
    except (ValueError, OSError, RuntimeError) as error:
        parser.exit(2, f"sync_web_assets: {error}\n")
