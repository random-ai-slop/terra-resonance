# Checked toroidal agreement

`earth_modes.agreement` compares explicit elastic T-mode pairs from two complete
bundles of the same canonical model. It saves a self-contained report that can
be checked and exported later without the original files. Neither agreement nor
mesh refinement certifies continuum accuracy or changes either solver's quality
status. The experimental solver remains experimental.

## Start with four solves and an independent reference

Install Terra Resonance 0.3.0, copy
[`examples/recipes/agreement.py`](../examples/recipes/agreement.py) from the source
distribution, and run it outside the checkout:

```sh
OPENBLAS_NUM_THREADS=1 python agreement.py my-agreement
```

`my-agreement` must be a new directory. The recipe solves a homogeneous solid
sphere (radius 1,000,000 m, density 4000 kg/m³, Vp 8000 m/s, Vs 4000 m/s), degree
2, frequency window [1e-8, 0.002] Hz, at requested meshes 20 and 40 with each
method. The explicit selected ID is `T0_2:solid:sphere`.

It writes four bundles (`default-20.json`, `default-40.json`, `pilot-20.json`,
`pilot-40.json`) and four full reports (`cross-20.json`, `cross-40.json`,
`refinement-default.json`, `refinement-pilot.json`). `cross-40.csv`,
`cross-40.svg`, and `cross-40.png` each have an adjacent `.json` sidecar.
`independent-frequency.json` separately records the spherical-Bessel traction
root, the analytic frequency and all four frequency errors against a named-case
0.5% ceiling. This independent reference is computed with SciPy; no repository
reference data is needed. The checks do not promote bundle quality.

Each bundle/report or artifact/sidecar pair is committed individually. The recipe
does not provide a transaction across the output directory: failure retains
completed files for inspection. It never deletes or reuses an existing directory.

## Two pairs, one selected figure, then a received sidecar

This wider window includes two radial labels. Explicit selection does not imply
automatic mode tracking:

```python
from earth_modes import homogeneous_model, solve, save_bundle
from earth_modes.experimental import solve_toroidal
from earth_modes.agreement import toroidal_agreement, export_agreement

model = homogeneous_model(1e6, 4000, 8000, 4000)
settings = dict(l_min=2, l_max=2, frequency_min_hz=1e-8,
                frequency_max_hz=.006, mesh_size=40)
a = solve(model, families=["T"], gravity=0, **settings)
b = solve_toroidal(model, **settings)
pairs = [("T0_2:solid:sphere", "T0_2:solid:sphere"),
         ("T1_2:solid:sphere", "T1_2:solid:sphere")]
report = toroidal_agreement(a, b, pairs)
save_bundle(a, "reference.json")
save_bundle(b, "candidate.json")
export_agreement(report, "agreement.json")
export_agreement(report, "pair-1.svg", pair_index=1, width=640, height=480)
```

The equivalent CLI computation is:

```sh
terra agreement --reference reference.json --candidate candidate.json \
  --pair T0_2:solid:sphere T0_2:solid:sphere \
  --pair T1_2:solid:sphere T1_2:solid:sphere --out agreement.json
terra agreement --report agreement.json --pair-index 1 --out pair-1.svg
```

Send `pair-1.svg.json` to a recipient. That file contains **both pairs and both
complete source bundles**, not just the illustrated pair. In a directory with
only that received sidecar, the recipient can run:

```sh
terra agreement --report pair-1.svg.json --out received-all.csv
terra agreement --report pair-1.svg.json --pair-index 0 --out received-pair-0.png
```

`load_agreement("pair-1.svg.json")` provides the same checked Python entry point.
Report-input and bundle-input routes are exclusive. Bundle inputs must be actual
Bundles, not Projects. Unknown IDs, partial routes, or mixed `--report`/`--pair`
options fail. Existing outputs are protected; replacement requires explicit
`--overwrite` or `overwrite=True`.

## Reading the result

The two axes show continuously mass-normalized W and the signed residual
`reference - aligned candidate`, each in kg^(-1/2), on common radius r/R.
Their vertical scales are separate so tiny nonzero residuals remain visible.
The figure retains all union-partition points and draws each material separately,
with dotted boundary marks. A zero residual has finite limits and a zero label.
The caption shows the zero-based pair index, degree/radial labels, methods,
frequencies, signed reference-relative difference, shape distance and alignment
sign. Different n labels and indeterminate alignment receive explicit notices.
Long method/model names may be ellipsized in the figure; complete source names,
IDs, norms, mesh counts, quality and provenance remain in the sidecar.

The reference is the denominator, not physical truth. For fa and fb, the reported
frequency difference is `fb-fa` and relative change is `(fb-fa)/fa`. Both remain
signed. Unknown method identity displays as `unknown`; unknown mesh counts remain
null, never inferred from stored sample counts. The CSV has one row per explicit
pair, scalar columns and source/model hashes. Its domain element total is blank
unless every selected layer has a declared count. The regional maps remain in
JSON. Requested meshes can differ from actual per-layer counts, and the methods
approximate heterogeneous materials differently.

On each material separately, the evaluator unions endpoints, density knots and
both W grids. Three-point Gauss integration evaluates the degree-five products
of their stored linear reconstructions. With mass inner product
`<u,v> = integral rho*r²*u*v dr`, A=`<Wa,Wa>`, B=`<Wb,Wb>` and
c=`<Wa,Wb>/sqrt(A*B)`, the overlap is `abs(c)`. A single sign s is applied across
the entire solid domain. The distance is evaluated directly as
`sqrt(integral rho*r²*(Wa/sqrt(A)-s*Wb/sqrt(B))² dr)` to retain tiny differences.
If `abs(c) <= 64*float64_epsilon`, s is deterministically +1 and alignment is
marked indeterminate; otherwise s is the sign of c. Continuous A/B are distinct
from the bundle's discrete normalization. No source arrays or hashes are changed.

Eligible pairs have equal positive degree, q=null, and the same complete maximal
connected solid support. Canonical model equality is conservative and includes
non-provenance names and IDs. Known conflicting linear-Q/effective-model
declarations fail; absent external provenance stays unknown. Different models,
partial supports, zero norms and unsupported metrics fail explicitly. Use the
existing `earth_modes.analysis.compare_bundles` / `terra compare` for general
side-by-side comparisons with raw supplied signs; its semantics are unchanged.

## Checks, formats and limits

`validate_agreement(report)` returns the original valid mapping unchanged after
checking complete sources, hashes, eligibility and recomputed rows without
solving. `agreement_curves(report, pair_index)` returns separate material records
with `r_m`, `reference_w`, aligned `candidate_w` and `residual_w`. Optional JSON
metadata and historical computation producer remain intact. Validation checks
internal consistency, not authenticity. CSV and figure numerics are recomputed;
JSON and sidecars retain the original checked values within the contract's
arithmetic tolerances. `export_production` in sidecars records the current
renderer/version and resolved options separately from the historical generator.

JSON saves one full report, with no `.json.json`. CSV always exports all pairs.
SVG/PNG show one pair; multi-pair reports require an explicit zero-based index.
Figure dimensions default to 1200×800, support 640..4096 by 480..4096, and accept
safe integer-valued numbers, excluding booleans. Explicit dimensions or a pair
index on JSON/CSV fail rather than being ignored. SVG uses native vector curves.

Limits are 64 unique explicit pairs, 200,000 total material intervals counting
each pair, 64 MiB per complete bundle and 160 MiB per report or export sidecar.
Byte limits use UTF-8 JSON with `ensure_ascii=False`, indent 2 and a final newline;
unknown metadata counts. Readers are bounded and reject duplicate keys and
nonfinite literals. These are rejection limits, not peak-memory guarantees.
Exports validate and bound the sidecar before publication. Artifact/sidecar
transactions restore the previous pair on controlled commit failure; this is
not a filesystem power-loss guarantee.
