# Phase 2 planning review, round 2 — scientific contracts

Date: 2026-09-04. Reviewed the revised `docs/PHASE-2.md` against the actual canonical normalization, field evaluation, mixed solver, and bundle validators. Planning only; no implementation changed.

**Recommendation: accept the bounded phase with three small contract clarifications before freeze.** The executable T pilot is useful and feasible alongside the package/render work. The numerical scope and proposed language stack need no expansion.

## 1. Change: define the four pilot errors on the correct representations

The proposed frequency 0.5%, shape 1%, residual 1e-9 and mass-orthogonality 1e-8 thresholds are credible for selected low-order, resolved test problems. They are not meaningful until the comparison norms and test modes are specified.

- Frequency: `abs(f_test/f_reference - 1)` on explicitly paired positive oscillatory modes. Exclude rigid rotations from this percentage test and verify their expected nullspace separately. Name the Bessel and shell cases and overtone ranges before implementation.
- Shape: normalize both fields in the same physical domain, align only their common arbitrary sign, and measure `sqrt(integral rho*r²*(W_test-sign*W_ref)² dr / integral rho*r²*W_ref² dr)`. Use a sufficiently resolved common evaluation grid retaining material sides. Do not use pointwise relative errors near nodes, or fit arbitrary depth-dependent rescaling. Compare each independent solid domain separately.
- Residual: use the original constrained **discrete FE eigenvector** and pencil, before exported-data interpolation, with `||Kx-lambda Mx||₂ / ((||K||F+abs(lambda)||M||F)*||x||₂)`. Record that norm definition, matrix size and positive mode IDs. This is a solver consistency test, not independent physics accuracy.
- Orthogonality: compute `max(abs(X.T @ M @ X - I))` for FE mass-normalized eigenvectors in one degree/domain group. Never apply it to modes from different material models or spaces.

This distinction is necessary because `solver.py:170–191` currently normalizes exported regions with a layerwise trapezoid, whereas the pilot eigenvectors use quadrature-based FE mass. Canonical piecewise-linear reconstruction generally does not retain discrete mass orthogonality to 1e-8. Keep canonical validation separately at its existing contract tolerance; do not loosen the FE tests or falsely claim that exported samples meet them. Matrix symmetry/SPD and residual gates should be diagnostic provenance, while benchmark labels require the independent reference evidence.

**Minimal blocker:** freeze these definitions and a short explicit case matrix, such as homogeneous ball l=2/3 with n=0..3, a traction-free shell l=2 with its first three modes, both PREM solid domains at selected l=1..4, and separately the l=1 null modes. A failed mode cannot disappear from the tested set silently. No need to add an extensive framework or a new quality-status vocabulary.

## 2. Add: a small, exact pilot output/mesh contract

The API-only experimental boundary is appropriate. Returning the existing ModeBundle is feasible, but round 3 should explicitly retain these facts:

- The input model is preserved; density and shear speed are linearly interpolated within each named material layer, and `mu(r)=rho(r)*vs(r)²` is evaluated at quadrature points. Four Gauss points are sufficient for the proposed quadratic basis on each interval bounded by original profile knots. Treat material jumps as separate sides, not as ordinary knots in one smoothed profile.
- Keep every profile knot. Refinement adds nodes; the target mesh size cannot remove mandatory source knots. Preflight the **actual** domain dimensions and report actual allocation before dense matrices are allocated. A source profile that exceeds the budget fails explicitly.
- Adjacent solid material layers share one displacement domain. Fluids separate traction-free T domains. Each connected solid domain has its own l=1 rigid rotation. Reserve n=0 for that zero motion and retain n=1 for the first positive l=1 branch, matching the current identities. For l>=2, the first positive mode has n=0. The user frequency filter does not renumber modes.
- Region U/V are exactly zero; W retains each source layer's boundary samples; fluid regions are absent; there is one global canonical mass factor per mode. q=null means this pilot performs an elastic calculation even if the preserved reference model contains material Q. Do not imply that Q was estimated. Do not add placeholder potential arrays.
- Provenance identifies the experimental method/version, interpolation/quadrature, actual mesh and memory estimates, spectrum exclusions and diagnostics. It must not incorrectly say that eigenvectors originated from the old Ouroboros mass matrix. Reuse canonical data utilities without importing vendor assembly through an indirect helper.
- Invalid/all-fluid/empty-frequency outcomes follow documented existing semantics: invalid requests raise; no solid domains are explicitly not applicable; a valid empty frequency selection returns an empty bundle, with no fabricated demonstration mode.

**Minimal blocker:** choose the exact keyword/default set and this identity policy in round 3. Keep `solve_toroidal` separate from default dispatch and CLI. Do not add a generic backend option or pilot-to-default fallback.

## 3. Change: make the sparse wire promise scientifically achievable

Filled cut faces, preserved source knots, independent node extraction and explicit SceneSpec 1.1 are sound. One sentence in the new plan is too strong if interpreted visually: an arbitrarily sparse graticule cannot guarantee that every high-degree feature remains visible simply because each line is finely segmented.

For example, the real m=-12 harmonic has its sine factor zero on meridians spaced 30 degrees; a radial-component plot on those meridians misses the intervening azimuthal extrema regardless of along-line sampling. Parallels provide additional information but do not make the sparse display equivalent to a resolved surface mesh.

**Change the acceptance claim:** spacing never discards the scientific field, section samples, probes or node extraction; it does choose a sparse material display grid that may omit extrema between lines. Label it as a display graticule, record the requested spacing, and give an explanatory warning for under-resolved high-degree displays. Do not silently insert extra meridians contrary to the saved spacing. Null retains legacy triangle-wire behavior. Keep color extrema/clipping diagnostics based on the underlying scientific sample set rather than only the visible wires, otherwise a sparse grid could falsely report no clipping.

Clarify that “density does not modify scientific hashes” means the **ModeBundle** hash. A Scene/project artifact intentionally changes when its saved appearance changes. This avoids an impossible promise of unchanged project identity while modifying SceneSpec.

## Accepted cross-cutting choices

- Installed examples use one canonical bundle plus a catalog and return fresh validated projects. This avoids duplicated data maintenance without weakening the self-contained returned project.
- English maintained artifacts and website locale as presentation state preserve scientific IDs, units and hashes. Immutable user-authored text remains verbatim. English chart export must reuse the actual numeric plot/explicit comparison pair; re-evaluating a different scene or time would break the promise.
- Retaining old 1.0 scenes and explicitly upgrading appearance to 1.1 is adequate if Python/TS, GLB, cache keys and package examples share the same version decision. Keep the independent bundle version unchanged.
- The T→R→S route is scientifically adequate and the limited pilot delivers evidence now. Later R/S promotion must keep the fluid density-sheet, free-surface, l=1 regularity/translation and essential-subspace regressions. More physics and sparse solvers do not belong in this release.
- Preserve GPL attribution and distinguish independent assembly from independent benchmarking. No native-language dependency is justified by the current profile.

## Remove/change/add summary

Remove a blanket promise that sparse visible wires preserve every high-degree visual feature. Change the pilot tolerance statement to named quantities on FE versus exported representations. Add exact T domain/zero-mode identity, mandatory-knot budgeting, and an explicit bounded reference matrix. Everything else can proceed to final planning review without further broad research.
