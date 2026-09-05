"""Installed examples must be complete, stable and safe to edit independently."""

import pytest

from earth_modes import list_examples, load_example, bundle_hash


def test_packaged_examples_preserve_science_and_material_side():
    ids = list_examples()
    assert ids == [
        "01-breathing",
        "02-tangential",
        "03-indices",
        "04-liquid-core",
        "05-traveling",
        "06-beats",
    ]
    hashes = set()
    for id in ids:
        project = load_example(id)
        assert project["teaching"]["id"] == id
        assert project["scene"]["schema_version"] == "1.1"
        assert project["scene"]["wireframe_spacing_deg"] == 15
        assert project["scene"]["bundle_hash"] == bundle_hash(project["bundle"])
        assert len(project["bundle"]["modes"]) == 47
        hashes.add(project["scene"]["bundle_hash"])
    assert len(hashes) == 1
    core = load_example("04-liquid-core")
    fluid = core["teaching"]["verification"]["fluid_layer_id"]
    assert core["scene"]["point"]["layer_id"] == fluid
    assert core["probe"]["layer_id"] == fluid


def test_examples_are_fresh_and_unknown_ids_are_actionable():
    before = load_example()
    changed = load_example()
    changed["bundle"]["model"]["name"] = "Researcher edit"
    changed["scene"]["terms"][0]["amplitude"] = -2
    changed["teaching"]["steps"].clear()
    assert load_example() == before
    listed = list_examples()
    listed.clear()
    assert len(list_examples()) == 6
    with pytest.raises(
        ValueError, match="Unknown example.*Available examples:.*03-indices"
    ):
        load_example("missing-example")
