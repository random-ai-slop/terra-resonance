"""Shared export contracts: resource preflight, time sampling and safe commits."""

from __future__ import annotations
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import json
import math
import os
import shutil
import tempfile
import warnings
import ctypes
import sys

import numpy as np

from .data import validate_bundle, validate_scene
from .fields import mode_scale


@dataclass(frozen=True)
class ExportLimits:
    max_dimension: int = 4096
    max_frames: int = 14400
    max_pixels: int = 2_000_000_000
    max_points: int = 250000
    max_cache_bytes: int = 128 * 1024**2
    max_morph_values: int = 8_000_000
    max_glb_bytes: int = 512 * 1024**2
    max_key_weights: int = 1_000_000


def bundle_hash(bundle):
    from .data import bundle_hash as canonical_hash

    return canonical_hash(bundle)


def manifest(bundle, scene=None, **details):
    import matplotlib
    from . import __version__
    from .data import validate_export_spec

    media_format = details.get("format")
    if media_format in ("png", "svg", "csv", "frames", "gif", "mp4", "glb"):
        details["export_spec"] = validate_export_spec(
            details.get("export_spec", {"format": media_format})
        )
    return {
        "schema_version": "1.0",
        "generator": "earth_modes.export",
        "generator_version": __version__,
        "annotation_language": "en",
        "section_surface_policy": "filled scientific sections; legacy shell triangle edges preserved",
        "numpy_version": np.__version__,
        "matplotlib_version": matplotlib.__version__,
        "bundle_hash": bundle_hash(bundle),
        "model_id": bundle["model"]["id"],
        "model_reference_frequency_hz": bundle["model"].get("reference_frequency_hz"),
        "model_provenance": bundle["model"].get("provenance", {}),
        "bundle_provenance": bundle["provenance"],
        "scene": scene,
        "mode_provenance": {m["id"]: m["provenance"] for m in bundle["modes"]},
        "illustration_divisors": {m["id"]: mode_scale(m) for m in bundle["modes"]},
        "amplitude_meaning": "dimensionless illustration coefficient; not earthquake excitation",
        "reproduction": "Use the matching saved project/bundle; this hash alone cannot restore input data.",
        **details,
    }


def prepare(bundle, scene, path, suffixes):
    validate_bundle(bundle)
    if scene is not None:
        validate_scene(scene, bundle)
    path = Path(path)
    if suffixes and path.suffix.lower() not in suffixes:
        raise ValueError(f"Expected output suffix in {suffixes}.")
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _rename_directory_exclusive(source, target):
    """Atomically publish a directory without replacing even an empty target.

    Standard POSIX rename replaces empty directories. Use the OS's exclusive
    variant rather than weakening the default no-overwrite contract.
    """
    if os.name == "nt":
        os.rename(source, target)  # Windows rename already refuses existing targets.
        return
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform == "darwin":
        rename = libc.renamex_np
        rename.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        arguments = (os.fsencode(source), os.fsencode(target), 4)  # RENAME_EXCL
    elif sys.platform.startswith("linux") and hasattr(libc, "renameat2"):
        rename = libc.renameat2
        rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        arguments = (-100, os.fsencode(source), -100, os.fsencode(target), 1)  # AT_FDCWD / RENAME_NOREPLACE
    else:
        raise OSError("This platform lacks atomic no-overwrite directory publication")
    rename.restype = ctypes.c_int
    if rename(*arguments):
        code = ctypes.get_errno()
        raise OSError(code, os.strerror(code), str(target))


def _identity(path):
    stat = Path(path).lstat()
    return stat.st_dev, stat.st_ino


def _remove_owned(path, identity):
    """Do not remove a replacement installed by another writer after publication."""
    try:
        if _identity(path) != identity:
            return
    except FileNotFoundError:
        return
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink()


@contextmanager
def transaction(path, overwrite=False, directory=False):
    """Prepare the artifact and sidecar together; roll back controlled commit failures.

    This is not a filesystem-wide transaction against power failure. It prevents
    overwrites by default and restores the previous pair on a failed rename.
    """
    path = Path(path)
    sidecar = Path(str(path) + ".json")
    if not overwrite and (os.path.lexists(path) or os.path.lexists(sidecar)):
        raise FileExistsError(f"Output exists: {path}; use overwrite=True to replace it.")
    with tempfile.TemporaryDirectory(prefix=".terra-export-", dir=path.parent) as tmp:
        staging = Path(tmp) / path.name
        if directory:
            staging.mkdir()
        info = {}
        yield staging, info
        if not staging.exists() or (not directory and staging.stat().st_size == 0):
            raise RuntimeError("Export did not produce a nonempty artifact.")
        staged_manifest = Path(str(staging) + ".json")
        staged_manifest.write_text(
            json.dumps(info, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        )
        # Validate the sidecar before replacing either final file.
        json.loads(staged_manifest.read_text())
        moved = []
        backups = []
        if not overwrite:
            try:
                for source, target in ((staging, path), (staged_manifest, sidecar)):
                    identity = _identity(source)
                    if source.is_dir():
                        _rename_directory_exclusive(source, target)
                    else:
                        os.link(source, target)
                    moved.append((target, identity))
            except BaseException:
                for target, identity in reversed(moved):
                    _remove_owned(target, identity)
                raise
            return
        try:
            for index, target in enumerate((path, sidecar)):
                if os.path.lexists(target):
                    backup = Path(tmp) / f"previous-{index}"
                    os.replace(target, backup)
                    backups.append((backup, target))
            for source, target in ((staging, path), (staged_manifest, sidecar)):
                os.replace(source, target)
                moved.append(target)
        except BaseException:
            for target in reversed(moved):
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink(missing_ok=True)
            for backup, target in reversed(backups):
                os.replace(backup, target)
            raise


def size(width, height, limits):
    if any(
        isinstance(x, bool)
        or not isinstance(x, (int, np.integer))
        or not 64 <= x <= limits.max_dimension
        for x in (width, height)
    ):
        raise ValueError(f"Image dimensions must be integers in [64, {limits.max_dimension}].")


def default_bound(bundle, scene):
    lookup = {m["id"]: m for m in bundle["modes"]}
    return max(
        1e-12,
        sum(
            abs(t["amplitude"]) * math.sqrt(3 * (2 * lookup[t["mode_id"]]["l"] + 1) / (4 * math.pi))
            for t in scene["terms"]
        ),
    )


def times(bundle, scene, duration_s, fps, limits, check_alias=True):
    if (
        isinstance(duration_s, bool)
        or not isinstance(duration_s, (int, float))
        or not math.isfinite(duration_s)
        or duration_s <= 0
    ):
        raise ValueError("duration_s must be finite and positive playback seconds.")
    if isinstance(fps, bool) or not isinstance(fps, (int, np.integer)) or not 1 <= fps <= 120:
        raise ValueError("fps must be an integer in [1,120].")
    count = math.floor(duration_s * fps + 0.5)
    if not 2 <= count <= limits.max_frames:
        raise ValueError(f"Export must have 2..{limits.max_frames} frames.")
    notes = []
    if check_alias:
        lookup = {m["id"]: m for m in bundle["modes"]}
        for term in scene["terms"]:
            if not term["amplitude"]:
                continue
            per_period = fps / (lookup[term["mode_id"]]["frequency_hz"] * scene["time_scale"])
            if per_period < 2:
                raise ValueError(
                    f"Time aliasing for {term['mode_id']}: {per_period:.3g} frames/period; reduce time_scale."
                )
            if per_period < 12:
                notes.append(
                    f"{term['mode_id']}: only {per_period:.3g} frames per apparent period."
                )
    for note in notes:
        warnings.warn(note, UserWarning, stacklevel=2)
    playback = np.arange(count) / fps
    return playback, scene["time_s"] + playback * scene["time_scale"], notes


def media_budget(width, height, count, path, limits):
    size(width, height, limits)
    if width * height * count > limits.max_pixels:
        raise ValueError(
            f"Rendered pixel budget exceeds {limits.max_pixels}; reduce size/duration."
        )
    disk = 4 * width * height * count
    available = shutil.disk_usage(Path(path).parent).free
    if disk > available:
        raise ValueError(
            f"Temporary frame estimate {disk} bytes exceeds available disk space {available}."
        )
    return {"rendered_pixels": width * height * count, "temporary_disk_estimate_bytes": disk}
