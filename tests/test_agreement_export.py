"""Actual report/sidecar journeys, native artifacts and controlled failure readback."""
from copy import deepcopy
import csv
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

from PIL import Image
import pytest

from earth_modes import agreement, agreement_export
from earth_modes.agreement import export_agreement, load_agreement, toroidal_agreement
from earth_modes.cli import main
from earth_modes.data import save_bundle
from test_agreement import bundle, compare, sign_fixture


@pytest.fixture
def report():
    a, b = bundle(), bundle(identity="b", shapes=[("sphere", [0., .5, 1.], [0., .5 + 1e-9, 1.])])
    a["provenance"]["solver"] = "Reference method"
    b["provenance"]["solver"] = "Candidate method"
    b["modes"][0]["frequency_hz"] += 1e-15
    result = compare(a, b)
    result["generator_version"] = "historical-0.3"
    result["user_note"] = "Preserve Δ and 用户 metadata"
    return result


def test_all_formats_preserve_full_report_and_recompute_csv(report, tmp_path):
    expected = agreement._checked_evaluation(report)["rows"][0]
    report["rows"][0]["shape_distance"] += 1e-15  # permitted arithmetic variation
    before = deepcopy(report)
    for suffix in ("json", "csv", "svg", "png"):
        path = tmp_path / ("report." + suffix)
        assert export_agreement(report, path) == path
        saved = load_agreement(path if suffix == "json" else Path(str(path) + ".json"))
        if suffix != "json":
            production = saved.pop("export_production")
            assert production["renderer"] == "earth_modes.agreement_export"
            assert production["annotation_language"] == "en"
        assert saved == before
    assert not (tmp_path / "report.json.json").exists()
    assert report == before
    with (tmp_path / "report.csv").open(newline="") as stream:
        reader = csv.DictReader(stream)
        assert reader.fieldnames == list(agreement_export.CSV_COLUMNS)
        row, = reader
    assert float(row["shape_distance"]) == expected["shape_distance"]
    assert float(row["relative_frequency_change"]) == expected["relative_frequency_change"] != 0
    assert row["reference_domain_elements"] == ""
    assert row["reference_solver"] == "Reference method"
    assert row["reference_domain_samples"] == "2"
    with Image.open(tmp_path / "report.png") as picture:
        picture.load()
        assert picture.size == (1200, 800)
        assert picture.convert("RGB").getextrema() != ((255, 255),) * 3
    root = ET.parse(tmp_path / "report.svg").getroot()
    assert not root.findall(".//{http://www.w3.org/2000/svg}image")
    assert len(root.findall(".//{http://www.w3.org/2000/svg}path")) > 10


def test_selected_pair_retains_full_sidecar_and_integer_json_options(tmp_path):
    a, b = sign_fixture()
    # Second explicit pair adds a distinct n label without automatic matching.
    second = deepcopy(b["modes"][0])
    second.update(id="second", n=2)
    b["modes"].append(second)
    report = toroidal_agreement(a, b, [("a", "b"), ("a", "second")])
    output = tmp_path / "pair.png"
    with pytest.raises(ValueError, match="multi-pair"):
        export_agreement(report, output)
    assert not output.exists()
    export_agreement(report, output, pair_index=1., width=640., height=480.)
    saved = load_agreement(str(output) + ".json")
    assert len(saved["rows"]) == 2 and saved["export_production"]["pair_index"] == 1
    assert saved["rows"][1]["alignment_indeterminate"]
    with Image.open(output) as image:
        image.load()
        assert image.size == (640, 480)
    export_agreement(saved, tmp_path / "all.csv")
    with (tmp_path / "all.csv").open() as stream:
        assert len(list(csv.DictReader(stream))) == 2


@pytest.mark.parametrize("suffix,options", [
    ("json", {"width": 640}), ("csv", {"pair_index": 0}),
    ("csv", {"height": 480}), ("gif", {}),
    ("png", {"width": True}), ("png", {"height": 479}),
    ("png", {"width": 4097}), ("png", {"width": 640.5}),
    ("png", {"pair_index": True}), ("png", {"pair_index": -1}),
    ("svg", {"pair_index": 1}),
])
def test_options_fail_before_creating_output(report, tmp_path, suffix, options):
    output = tmp_path / "absent" / ("bad." + suffix)
    with pytest.raises(ValueError):
        export_agreement(report, output, **options)
    assert not output.parent.exists()


def test_tampering_and_sidecar_size_fail_before_publication(report, tmp_path, monkeypatch):
    tampered = deepcopy(report)
    tampered["rows"][0]["shape_distance"] += .01
    with pytest.raises(ValueError, match="inconsistent"):
        export_agreement(tampered, tmp_path / "bad.csv")
    monkeypatch.setattr(agreement_export, "MAX_REPORT_BYTES",
                        agreement._bounded_json_size(report, agreement.MAX_REPORT_BYTES))
    with pytest.raises(ValueError, match="sidecar"):
        export_agreement(report, tmp_path / "large.csv")
    assert list(tmp_path.iterdir()) == []


def test_no_clobber_and_controlled_pair_rollback(report, tmp_path, monkeypatch):
    from earth_modes import export_common

    output = tmp_path / "preserved.csv"
    export_agreement(report, output)
    sidecar = Path(str(output) + ".json")
    before = output.read_bytes(), sidecar.read_bytes()
    with pytest.raises(FileExistsError):
        export_agreement(report, output)
    replace = export_common.os.replace

    def fail_sidecar(source, target):
        if Path(target) == sidecar and Path(source).name == sidecar.name:
            raise OSError("injected sidecar commit failure")
        return replace(source, target)

    with monkeypatch.context() as patch:
        patch.setattr(export_common.os, "replace", fail_sidecar)
        with pytest.raises(OSError, match="injected"):
            export_agreement(report, output, overwrite=True)
    assert (output.read_bytes(), sidecar.read_bytes()) == before
    output.unlink()
    with pytest.raises(FileExistsError):
        export_agreement(report, output)  # a surviving sidecar protects the pair
    assert not output.exists() and sidecar.read_bytes() == before[1]
    assert not list(tmp_path.glob(".terra-export-*"))


def test_staged_render_failure_keeps_previous_pair(report, tmp_path, monkeypatch):
    from matplotlib.figure import Figure

    output = tmp_path / "kept.png"
    export_agreement(report, output, width=640, height=480)
    before = output.read_bytes(), Path(str(output) + ".json").read_bytes()

    def fail(*args, **kwargs):
        raise RuntimeError("injected render failure")

    monkeypatch.setattr(Figure, "savefig", fail)
    with pytest.raises(RuntimeError, match="injected"):
        export_agreement(report, output, overwrite=True)
    assert (output.read_bytes(), Path(str(output) + ".json").read_bytes()) == before


def test_cli_compute_then_only_received_sidecar(report, tmp_path):
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    for role, path in (("reference", a), ("candidate", b)):
        save_bundle(report["sources"][role]["bundle"], path)
    output = tmp_path / "pair.svg"
    args = ["agreement", "--reference", str(a), "--candidate", str(b), "--pair", "a", "b",
            "--out", str(output)]
    assert main(args) == 0
    a.unlink()
    b.unlink()
    output.unlink()
    received = str(output) + ".json"
    completed = subprocess.run([sys.executable, "-m", "earth_modes.cli", "agreement",
                                "--report", received, "--out", str(tmp_path / "recovered.csv")],
                               text=True, capture_output=True)
    assert completed.returncode == 0, completed.stderr
    assert load_agreement(str(tmp_path / "recovered.csv") + ".json")["pairs"] == [["a", "b"]]


@pytest.mark.parametrize("options", [
    ["--reference", "missing.json"],
    ["--report", "missing.json", "--pair", "a", "b"],
    ["--report", "missing.json", "--candidate", "missing.json"],
])
def test_cli_partial_routes_fail(options, tmp_path):
    assert main(["agreement", *options, "--out", str(tmp_path / "bad.json")]) == 2
    assert not list(tmp_path.iterdir())


def test_cli_mixed_routes_and_project_input_fail(report, tmp_path):
    with pytest.raises(SystemExit) as error:
        main(["agreement", "--report", "r.json", "--reference", "a.json", "--out", "bad.json"])
    assert error.value.code == 2
    project = tmp_path / "project.json"
    project.write_text(json.dumps({"bundle": report["sources"]["reference"]["bundle"]}))
    assert main(["agreement", "--reference", str(project), "--candidate", str(project),
                 "--pair", "a", "a", "--out", str(tmp_path / "bad.json")]) == 2
    assert not (tmp_path / "bad.json").exists()


def test_zero_residual_and_long_names_have_finite_axes(tmp_path):
    a = bundle()
    a["provenance"]["solver"] = r"User method $\invalid{expression}$ " * 20
    report = compare(a, a)
    fig = agreement_export._figure(report, agreement._checked_evaluation(report), 0, 640, 480)
    try:
        import math
        fig.canvas.draw()
        assert len(fig.axes) == 2
        assert all(math.isfinite(x) for axis in fig.axes for x in axis.get_ylim())
        assert any("Exact zero" in text.get_text() for text in fig.axes[1].texts)
    finally:
        fig.clear()
