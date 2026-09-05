# Implementation round 1: scientific outputs and research workflow

Historical review by numerical_research, 2026-09-04, distinct from `implementation-preflight-science.md`. Report-only review of analysis/CLI, Python output/overlays and browser geometry/GLB. **The following repairs were required before round 2.**

## O1 / P2: explicit comparisons still fail across naming/layer changes

At `packages/earth_modes/analysis.py:53`, compare_bundles required complete `_identity` equality even for explicit IDs, including T solid-domain strings built from layer IDs. Renaming a PREM T mode's domain while preserving model/frequencies/eigenfunctions left both bundles valid but made explicit `(id,id)` fail with `Comparison requires the same family/l/n and solid-domain identity`. Real cases include splitting one solid domain into adjacent material layers or using another solver's domain names. select_pair recommended explicit IDs, then the explicit route failed too.

The contract used domain matching for suggestions, while explicit API pairs did not claim tracking. Keep suggestions conservative; allow researcher-selected explicit pairs and report each side's family/l/n/domain separately. Any retained family/l restriction needs an explicit policy, not a string equality treated as physical proof. Regression: renamed or same-material-split T domains compare explicitly, while ambiguous automatic suggestions remain conservative.

## O2 / P2: CLI rejects fast GLB that the API exports correctly

At `cli.py:329`, GIF/MP4/frames/GLB all called `times(...check_alias=True)`. GLB API correctly used false and independently refined weight keys.

Executed case: true default PREM R0_0, time_scale=10000, duration=1 s, fps=4, draft and no decorative/analysis layers. API `write_glb(...duration_s=1,fps=4)` wrote `/tmp/r1-fast-api.glb`; CLI `terra export /tmp/r1-fast.terra.json --out /tmp/r1-fast-cli.glb --fps 4 --duration 1` failed with `Time aliasing for R0_0: 0.492 frames/period; reduce time_scale`. This was a video-sampling rule incorrectly imposed on adaptive continuous morph output, not a resource limit.

Use check_alias=false in GLB CLI preflight, describe nominal window/adaptive keys, and retain alias rejection for videos. Check CLI/API agreement for this case and continued video failure; no broad extra suite is necessary.

## O3 / P2: browser classifies weak nonzero components as identically zero

At `geometry.ts:216,277`, nodePoints/zeroComponent used an absolute 1e-12 threshold. Scaling the analytic fixture from 1 to 1e-13 changed a maximum of 0.28209479 with zero=false into 2.8209479e-14 with zero=true. Scaling should not change that mathematical conclusion. A physically relevant case is one U/V/W component weak relative to another; whole-mode normalization preserves that ratio but the weak component was misrepresented. Python already used a side-vector-relative machine-precision threshold.

Use Python's per-side `64*eps*vector_scale`, then set intersection tolerances from the nonzero component's own amplitude. Test a weak sign-changing radial component with strong tangent and exact T radial zero. Whole-field scaling alone is not a sufficient component-ratio regression.

## Checked without new defects

- Source-knot union already restored all 60 nodes of real R60; do not count that earlier repair as a new round-1 finding.
- GLB checks real non-keyframe reconstruction; the browser also uses a second-derivative bound.
- Canonical versus illustration units and divisors are explicit, not mislabeled as source-calibrated metres.
- A deliberately nonfinite manifest failure had already demonstrated previous-output-pair restoration; the same rollback was not redundantly rerun.
- Browser GLB orthographic metre-scale frustum is not double scaling: glTF 2.0 §3.10.2 excludes scale from camera view transforms. See the [Khronos specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#view-matrix).

Permitted lighting/antialias differences were not called scientific defects, and no speculative performance rewrite was added.
