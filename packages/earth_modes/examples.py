"""Installed scientific examples assembled from one bundle and a lesson catalog.

The package resources are generated copies of the validated repository sources.
Every call reads fresh JSON so caller mutations cannot affect another example.
"""

from __future__ import annotations

import json
from importlib.resources import files

from .data import bundle_hash, make_project, validate_project


def _resource(name: str):
    return json.loads(
        files("earth_modes").joinpath("assets", "examples", name).read_text()
    )


def _catalog():
    catalog = _resource("lessons.json")
    lessons = catalog.get("lessons")
    if not isinstance(lessons, list) or not lessons:
        raise ValueError("Installed example catalog has no lessons.")
    ids = [entry.get("id") for entry in lessons if isinstance(entry, dict)]
    if len(ids) != len(lessons) or any(not isinstance(id, str) or not id for id in ids):
        raise ValueError("Installed example catalog contains an invalid lesson ID.")
    if len(set(ids)) != len(ids):
        raise ValueError("Installed example catalog contains duplicate lesson IDs.")
    return catalog


def list_examples() -> list[str]:
    """Return the six installed lesson IDs in their teaching order."""
    return [entry["id"] for entry in _catalog()["lessons"]]


def load_example(id: str = "03-indices") -> dict:
    """Return a fresh, validated, self-contained teaching Project.

    No source checkout, browser, network access or external encoder is needed.
    The returned scene, probe, output settings and English teaching metadata are
    editable; they do not modify the packaged reference data.
    """
    catalog = _catalog()
    lesson = next((entry for entry in catalog["lessons"] if entry["id"] == id), None)
    if lesson is None:
        choices = ", ".join(entry["id"] for entry in catalog["lessons"])
        raise ValueError(f"Unknown example {id!r}. Available examples: {choices}.")
    bundle = _resource("prem-modes.json")
    if bundle_hash(bundle) != catalog.get("bundle_hash"):
        raise ValueError("Installed example catalog does not match its PREM bundle.")
    project = make_project(
        bundle, lesson["scene"], lesson.get("probe"), lesson.get("export")
    )
    project["teaching"] = {
        key: value
        for key, value in lesson.items()
        if key not in ("scene", "probe", "export")
    }
    return validate_project(project)
