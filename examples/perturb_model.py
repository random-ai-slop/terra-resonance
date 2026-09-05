"""A bounded material-sensitivity recipe with two step sizes and two meshes.

Run: terra's Python environment examples/perturb_model.py --out artifacts/vs-sensitivity
This is homogeneous toroidal shear-speed sensitivity, not a general inversion or
PREM sensitivity kernel. Hold density, radius and Vp fixed; Vs -> Vs*(1+epsilon).
For this problem f is proportional to Vs, providing an independent exact check.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path
import sys

from earth_modes.analysis import export_comparison
from earth_modes.data import save_bundle, _write_json, bundle_hash
from earth_modes.export_common import transaction
from earth_modes.models import homogeneous_model
from earth_modes.solver import solve


def study(output, h=0.01, mesh=24, overwrite=False):
    if not 0 < h <= 0.05:
        raise ValueError("h must be in (0, .05]; it is a fractional Vs change.")
    if type(mesh) is not int or mesh < 8:
        raise ValueError("mesh must be an integer >= 8.")
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    baseline = homogeneous_model()
    # The domain/l/n label is explicit. No interpolation or automatic tracking.
    mode_id = "T0_2:solid:sphere"
    steps = [
        ("baseline", 0),
        ("plus_h", h),
        ("minus_h", -h),
        ("plus_h2", h / 2),
        ("minus_h2", -h / 2),
    ]
    with transaction(output, overwrite, directory=True) as (staged, manifest):
        records, bundles = {}, {}
        for count in (mesh, 2 * mesh):
            for label, epsilon in steps:
                model = deepcopy(baseline)
                model["id"] = f"homogeneous-vs-{epsilon:+.8g}"
                model["name"] = f"Homogeneous solid · Vs × {1+epsilon:.8g}"
                for layer in model["layers"]:
                    layer["vs_m_s"] = [value * (1 + epsilon) for value in layer["vs_m_s"]]
                model["provenance"]["perturbation"] = dict(
                    parameter="vs_m_s",
                    fraction=epsilon,
                    fixed=["radius_m", "rho_kg_m3", "vp_m_s"],
                    kind="uniform multiplicative scaling",
                )
                print(
                    f"Solving {label}: mesh={count}, ΔVs/Vs={epsilon:+.5g}",
                    file=sys.stderr,
                    flush=True,
                )
                bundle = solve(
                    model,
                    families=["T"],
                    l_min=2,
                    l_max=2,
                    mesh_size=count,
                    gravity=0,
                    frequency_min_hz=0.0001,
                    frequency_max_hz=0.002,
                    n_max=0,
                )
                modes = [mode for mode in bundle["modes"] if mode["id"] == mode_id]
                if len(modes) != 1:
                    raise ValueError(
                        f"Expected explicit {mode_id}; frequency window did not contain it."
                    )
                key = f"{label}-mesh-{count}"
                save_bundle(bundle, staged / (key + ".json"))
                records[key] = dict(
                    frequency_hz=modes[0]["frequency_hz"],
                    bundle_hash=bundle_hash(bundle),
                    mode_id=mode_id,
                    epsilon=epsilon,
                    mesh=count,
                )
                bundles[key] = bundle
        derivatives = {}
        for count in (mesh, 2 * mesh):
            f0 = records[f"baseline-mesh-{count}"]["frequency_hz"]
            for label, step in [("h", h), ("h2", h / 2)]:
                fp = records[f"plus_{label}-mesh-{count}"]["frequency_hz"]
                fm = records[f"minus_{label}-mesh-{count}"]["frequency_hz"]
                sensitivity = (fp - fm) / (2 * step * f0)
                derivatives[f"{label}-mesh-{count}"] = dict(
                    d_log_f_d_log_vs=sensitivity,
                    exact_reference=1.0,
                    absolute_error=abs(sensitivity - 1),
                )
        coarse = records[f"baseline-mesh-{mesh}"]["frequency_hz"]
        fine = records[f"baseline-mesh-{2*mesh}"]["frequency_hz"]
        report = dict(
            schema_version="1.0",
            scope="Homogeneous T0_2 only; not an Earth sensitivity kernel.",
            independent_reference="At fixed density and radius, toroidal elastic eigenfrequencies scale exactly with uniform Vs.",
            h=h,
            meshes=[mesh, 2 * mesh],
            records=records,
            derivatives=derivatives,
            relative_mesh_frequency_change=abs(coarse - fine) / fine,
            relative_step_sensitivity_change=abs(
                derivatives[f"h-mesh-{2*mesh}"]["d_log_f_d_log_vs"]
                - derivatives[f"h2-mesh-{2*mesh}"]["d_log_f_d_log_vs"]
            ),
            caution="Small material steps do not establish a general mode-tracking or perturbation-theory method.",
        )
        _write_json(report, staged / "study.json")
        export_comparison(
            bundles[f"baseline-mesh-{2*mesh}"],
            bundles[f"plus_h-mesh-{2*mesh}"],
            [(mode_id, mode_id)],
            staged / "comparison.svg",
        )
        manifest.update(
            generator="examples.perturb_model",
            report=report,
            reproduction="All ten input/output bundles and solver requests are retained in this directory.",
        )
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--h", type=float, default=0.01)
    parser.add_argument("--mesh", type=int, default=24)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        print(study(args.out, args.h, args.mesh, args.overwrite))
    except (ValueError, OSError, RuntimeError) as error:
        parser.exit(2, f"perturb_model: {error}\n")
