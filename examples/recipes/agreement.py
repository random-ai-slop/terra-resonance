"""Four-solve installed API recipe: python agreement.py OUTPUT_DIR.

Creates a new directory. Files are individually committed; a failure may leave
completed outputs for inspection. Existing directories are never deleted or reused.
"""
import argparse
import json
import math
import os
from pathlib import Path
import tempfile

from scipy.optimize import brentq
from scipy.special import spherical_jn

from earth_modes import homogeneous_model, save_bundle, solve
from earth_modes.agreement import export_agreement, toroidal_agreement
from earth_modes.experimental import solve_toroidal


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=False)
    model = homogeneous_model(1e6, 4000, 8000, 4000)
    selected = "T0_2:solid:sphere"
    pairs = [(selected, selected)]
    bundles = {}
    for mesh in (20, 40):
        settings = dict(l_min=2, l_max=2, frequency_min_hz=1e-8,
                        frequency_max_hz=.002, mesh_size=mesh)
        for method in ("default", "pilot"):
            bundle = (solve(model, families=["T"], gravity=0, **settings)
                      if method == "default" else solve_toroidal(model, **settings))
            # Explicit lookup is required; a missing branch never disappears silently.
            next(m for m in bundle["modes"] if m["id"] == selected)
            name = f"{method}-{mesh}"
            bundles[name] = bundle
            save_bundle(bundle, args.output_dir / f"{name}.json")
    reports = {}
    comparisons = (
        ("cross-20", "default-20", "pilot-20"),
        ("cross-40", "default-40", "pilot-40"),
        ("refinement-default", "default-20", "default-40"),
        ("refinement-pilot", "pilot-20", "pilot-40"),
    )
    for name, reference, candidate in comparisons:
        report = toroidal_agreement(bundles[reference], bundles[candidate], pairs)
        reports[name] = report
        export_agreement(report, args.output_dir / f"{name}.json")
    export_agreement(reports["cross-40"], args.output_dir / "cross-40.csv")
    export_agreement(reports["cross-40"], args.output_dir / "cross-40.svg")
    export_agreement(reports["cross-40"], args.output_dir / "cross-40.png")

    # Independent elastic sphere traction condition: x*j_l'(x) - j_l(x)=0.
    # [2,3] brackets the first positive l=2 root, independent of either solver.
    root = brentq(lambda x: x * spherical_jn(2, x, derivative=True) - spherical_jn(2, x),
                  2., 3., xtol=1e-14)
    reference_hz = 4000 * root / (2 * math.pi * 1e6)
    accuracy = []
    for name, bundle in bundles.items():
        mode = next(m for m in bundle["modes"] if m["id"] == selected)
        error = abs(mode["frequency_hz"] - reference_hz) / reference_hz
        accuracy.append(dict(bundle=name + ".json", mode_id=selected,
                             frequency_hz=mode["frequency_hz"], relative_error=error))
        if error > .005:
            raise ValueError(f"{name}: independent sphere T0_2 frequency error exceeds 0.5%")
    evidence = dict(
        interpretation="Independent named sphere frequency check, separate from agreement and mesh refinement; no bundle quality promotion.",
        reference=dict(equation="x*j_2'(x)-j_2(x)=0", bracket=[2., 3.], root=root,
                       radius_m=1e6, vs_m_s=4000, frequency_hz=reference_hz),
        named_case_relative_error_ceiling=.005, results=accuracy,
        agreement_reports=[name + ".json" for name in reports],
        output_policy="New directory; individually committed files; partial outputs retained on failure.",
    )
    # Commit the independent evidence only after its complete serialization.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=args.output_dir,
                                         prefix=".frequency-", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(evidence, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, args.output_dir / "independent-frequency.json")
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    print(f"Four solves, four reports and independent frequency evidence: {args.output_dir}")


if __name__ == "__main__":
    main()
