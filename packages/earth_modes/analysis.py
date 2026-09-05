"""Explicit mode comparisons; never create a mixed-model physical scene."""

from __future__ import annotations

import csv
from pathlib import Path

from .data import bundle_hash, validate_bundle
from .export_common import transaction


def _identity(mode):
    domain = mode["provenance"].get("solid_domain_id")
    if mode["family"] == "T" and domain is None:
        domain = "solid:" + ",".join(r["layer_id"] for r in mode["regions"])
    return mode["family"], mode["l"], mode["n"], domain


def select_pair(a, b, family, l, n):
    """Suggest a unique identity match; ambiguous crossings require explicit IDs."""
    left = [m for m in a["modes"] if (m["family"], m["l"], m["n"]) == (family, l, n)]
    right = [m for m in b["modes"] if (m["family"], m["l"], m["n"]) == (family, l, n)]
    pairs = [(x["id"], y["id"]) for x in left for y in right if _identity(x) == _identity(y)]
    if len(pairs) != 1:
        raise ValueError(
            f"Expected one matching {n}{family}{l} identity/domain, found {len(pairs)}; "
            "provide --reference-mode and --candidate-mode explicitly."
        )
    return pairs[0]


def compare_bundles(a, b, pairs):
    """Return frequency rows and independent, unresampled canonical radial curves.

    ``pairs`` is a nonempty sequence of (reference_mode_id, candidate_mode_id).
    Explicit choices may differ in labels or material-domain naming. No automatic
    identity or physical mode tracking is inferred through a crossing.
    Eigenfunction signs are retained as supplied; they are arbitrary up to sign.
    """
    validate_bundle(a)
    validate_bundle(b)
    if not pairs:
        raise ValueError("pairs must contain at least one explicit mode-ID pair.")
    lookups = [{m["id"]: m for m in bundle["modes"]} for bundle in (a, b)]
    rows, curves = [], []
    for pair in pairs:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError("Each comparison pair must contain two mode IDs.")
        try:
            modes = [lookup[identity] for lookup, identity in zip(lookups, pair)]
        except (KeyError, TypeError) as error:
            raise ValueError(f"Unknown comparison mode ID in {pair!r}.") from error
        f0, f1 = [m["frequency_hz"] for m in modes]
        identity_a, identity_b = _identity(modes[0]), _identity(modes[1])
        rows.append(
            dict(
                reference_mode_id=pair[0],
                candidate_mode_id=pair[1],
                reference_family=identity_a[0],
                reference_l=identity_a[1],
                reference_n=identity_a[2],
                reference_solid_domain_id=identity_a[3],
                candidate_family=identity_b[0],
                candidate_l=identity_b[1],
                candidate_n=identity_b[2],
                candidate_solid_domain_id=identity_b[3],
                pairing="explicit_mode_ids",
                reference_frequency_hz=f0,
                candidate_frequency_hz=f1,
                delta_frequency_hz=f1 - f0,
                relative_frequency_change=(f1 - f0) / f0,
            )
        )
        for role, bundle, mode in zip(("reference", "candidate"), (a, b), modes):
            curves.append(
                dict(
                    role=role,
                    mode_id=mode["id"],
                    model_id=bundle["model"]["id"],
                    model_name=bundle["model"]["name"],
                    normalization=mode["normalization"],
                    regions=[
                        dict(
                            layer_id=r["layer_id"],
                            radius_fraction=[x / bundle["model"]["radius_m"] for x in r["r_m"]],
                            **{key: list(r[key]) for key in ("u", "v", "w")},
                        )
                        for r in mode["regions"]
                    ],
                )
            )
    return dict(
        schema_version="1.0",
        rows=rows,
        curves=curves,
        reference_bundle_hash=bundle_hash(a),
        candidate_bundle_hash=bundle_hash(b),
        interpretation="Analysis of separate models, not a physical superposition. Identity matching is not mode tracking.",
        eigenfunction_units="kg^(-1/2)",
        sign_convention="As supplied; eigenfunction global sign is arbitrary.",
    )


def export_comparison(a, b, pairs, path, *, overwrite=False):
    """Write a native SVG/PNG comparison or a frequency CSV with a complete sidecar."""
    from . import __version__

    result = compare_bundles(a, b, pairs)
    path = Path(path)
    if path.suffix.lower() not in (".svg", ".png", ".csv"):
        raise ValueError("Comparison output must be .svg, .png or .csv.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with transaction(path, overwrite) as (staged, info):
        if path.suffix.lower() == ".csv":
            with staged.open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(result["rows"][0]))
                writer.writeheader()
                writer.writerows(result["rows"])
        else:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_agg import FigureCanvasAgg

            fig = Figure(figsize=(10, max(4, 3.5 * len(pairs))), layout="constrained")
            FigureCanvasAgg(fig)
            axes = fig.subplots(len(pairs), 1, squeeze=False)[:, 0]
            for index, (axis, row) in enumerate(zip(axes, result["rows"])):
                for curve in result["curves"][index * 2 : index * 2 + 2]:
                    for key, color in zip(("u", "v", "w"), ("#286a8f", "#b57b27", "#527c55")):
                        label = f"{curve['role']}: {curve['model_name']} · {key.upper()}"
                        for region in curve["regions"]:
                            axis.plot(
                                region["radius_fraction"],
                                region[key],
                                color=color,
                                linestyle="-" if curve["role"] == "reference" else "--",
                                label=label,
                                linewidth=1.4,
                            )
                            label = "_nolegend_"
                axis.set(
                    xlabel="Each model’s r/R",
                    ylabel="Canonical U, V, W [kg$^{-1/2}$]",
                    title=f"{row['reference_n']}{row['reference_family']}{row['reference_l']} → "
                    f"{row['candidate_n']}{row['candidate_family']}{row['candidate_l']}  ·  "
                    f"{row['reference_frequency_hz']*1000:.7g} → {row['candidate_frequency_hz']*1000:.7g} mHz  ·  "
                    f"Δf/f = {row['relative_frequency_change']:+.5g}",
                )
                axis.grid(alpha=0.16)
                axis.legend(fontsize=7, ncols=2)
            fig.suptitle(
                "Independent model comparison · mass integral = 1 · supplied signs retained",
                fontsize=11,
            )
            fig.savefig(staged, dpi=140)
            fig.clear()
        info.update(
            result,
            generator="earth_modes.analysis",
            generator_version=__version__,
            reference_provenance=a["provenance"],
            candidate_provenance=b["provenance"],
            reference_mode_provenance={m["id"]: m["provenance"] for m in a["modes"]},
            candidate_mode_provenance={m["id"]: m["provenance"] for m in b["modes"]},
            reproduction="Retain both original bundles; hashes alone cannot restore them.",
        )
    return path
