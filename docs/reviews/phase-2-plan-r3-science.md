# Phase 2 planning review, round 3 — scientific freeze decision

Date: 2026-09-04. Reviewed the round-3 revision of `docs/PHASE-2.md` and its exact pilot API, evidence definitions, graticule contract and ownership. Planning only; no implementation changed.

**Decision: scientifically ready to freeze.** The round-2 blockers are resolved. The bounded experimental T solver provides useful numerical ownership evidence without replacing or weakening the delivered full solver. There is no remaining architectural or scientific blocker requiring another research cycle.

## Adversarial checks

- **Exported versus FE normalization:** the plan now evaluates the 1e-9 residual and 1e-8 orthogonality gates on constrained FE vectors, separately from canonical trapezoid normalization and interpolated output. This avoids an impossible precision claim on reconstructed fields. The sign-aligned mass-weighted shape gate is independent of arbitrary eigenfunction sign and remains meaningful at radial nodes.
- **Spectral identity:** every connected solid domain reserves its own l=1 rigid rotation at n=0; filtering does not renumber positive branches. Adjacent solid material layers do not acquire independent rotations. A core/mantle model exercises both cases. Empty output is explicitly distinguishable from unsupported or failed calculation.
- **Independent evidence:** sphere Bessel frequencies/shapes and shell traction-ODE frequencies/shapes test actual physics, rather than only reproducing the old assembly. Selected PREM references exercise both separated solid domains. The 0.5% frequency and 1% shape gates are feasible for the stated low-order cases with documented refinement. They do not automatically certify arbitrary l<=64 requests.
- **Material discretization:** layerwise linear rho/vs, mu=rho*vs², mandatory profile knots and quadratic FE functions make the quadrature claim well-defined. Actual-knot budgeting prevents a detailed imported profile from bypassing the dense-memory guard. Preserving input Q while explicitly solving an elastic problem is consistent and does not imply an estimated modal Q.
- **Sparse wires:** the revised coverage notice, unchanged scientific clipping samples and independently retained node/picking mesh address the high-m meridian counterexample. Scene identity changes while the ModeBundle hash stays fixed. Filled sections are explicitly documented as a renderer correction, so the plan no longer promises pixel-identical old exports.
- **Package and language:** installed examples remain fresh validated complete projects; canonical scientific content is not duplicated per locale. English export annotations reuse the numeric plot state, and arbitrary imported metadata remains verbatim. These changes do not redefine a probe as a source-calibrated seismogram or promote an experimental quality status.

## Small execution clarifications to record at freeze

These make the prescribed tests reproducible; they do not expand scope or justify delaying implementation:

1. Use valid increasing frequency bounds, `0 <= frequency_min_hz < frequency_max_hz`, with inclusive filtering of positive frequencies. “Empty selection” means no modes in a valid interval; inverted/equal bounds are invalid requests.
2. Fix representative sphere/shell materials in the validation command rather than choosing an easier case after a failure. A practical pair is R=1e6 m, rho=4000 kg/m³, vp=8000 m/s, vs=4000 m/s; a shell occupying 0.3R..R with a fluid interior in the complete Model. Preserve the already specified degree/overtone counts. For PREM, name n=1,l=1 and n=0,l=2/3/4 in each solid domain: eight mode identities with the existing pinned mantle/MINEOS and inner-core references.
3. Verify the known l=1 null vector W proportional to r using the scaled Kx residual and expected null multiplicity, not a universal arbitrary frequency cutoff. Output excludes that rigid motion, while raw diagnostic provenance records it. Check it on both a sphere and a shell.

## Keep / remove / add

- **Keep:** the exact API-only experimental boundary, no vendor assembly dependency or fallback, Python/SciPy, existing ModeBundle, all current default-solver behavior and historical evidence, separate independent and discrete validation, and the provisional unique file ownership.
- **Remove:** nothing further from the revised scope. Retain the already removed whole-solver rewrite, backend framework, sparse mixed solver, and additional physical branches as future work.
- **Add:** only the explicit validation inputs and frequency/nullspace wording above. Do not add another runtime, new schema for the pilot, or a claim of independent physics based on file ownership.

## Long-term sufficiency and limits

The staged T→R→S route is adequate. R promotion must preserve free-fluid surfaces and material density sheets; S promotion must confront mixed pressure/potential spaces, essential-spectrum classification, and l=1 symmetry before claiming equivalent support. Independent eigenfunction import, individual sensitivity/weak-Q validation and source/receiver calibration remain separate evidence-backed increments. Native acceleration follows measured operator/memory bottlenecks, not language preference.

The phase-2 pilot remains elastic, one-dimensional, toroidal and experimental. Its low-order evidence is not a certificate for high overtones, unresolved sharp profiles, every shell thickness, or a general stratified-fluid spectrum. These are appropriate declared limits while the existing full R/S/T workbench remains available. Proceed after the root records freeze; this review does not start implementation by itself.
