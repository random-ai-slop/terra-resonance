# Planning round 2: interface feasibility and numerical dependencies

Historical record. Reviewed PLAN/CONTRACT v0.3, ACCEPTANCE, and PLAN-REVIEW-LOG. This pass changed perspective to interoperability and execution boundaries, without repeating resolved normalization, amplitude, color, or material-domain principles. No implementation continued.

Verdict at the time: the architecture was feasible, with **five remaining interface ambiguities** before freezing. They allowed compliant implementations to disagree on hashes, normalization, quality, or frame counts. An independently derived regular-center limit also offered a simpler alternative to an artificial central hole.

## A1 — JCS domain and model-hash projection remain incomplete (P1)

Choosing RFC 8785 resolves number serialization, but “scientific model content excluding provenance” could mean either the whole model minus provenance or only radius/layers/Q without id/name. Unknown metadata can also contain invalid Unicode or nonfinite Python numbers, so validating scientific arrays alone is insufficient.

Minimal revision: explicitly list the projection, or simply hash the entire model except its top-level provenance and accept that renaming changes identity. If selecting only radius_m/layers/reference_frequency_hz, specify treatment of layer IDs/names individually. Hash the entire validated canonical bundle without inserting defaults or converting units during hashing. External convention conversion creates a new canonical bundle first. Require every subtree to meet the same JCS/I-JSON domain: finite double-representable numbers, no lone surrogates, consistent large-integer handling, and no silently dropped unknown keys. Longer identifiers may be strings.

[RFC 8785 sections 3.1–3.2](https://www.rfc-editor.org/rfc/rfc8785) requires I-JSON input, IEEE754-compatible numbers, and unchanged strings; lone surrogates and nonfinite values must fail. A JCS library cannot define the application's shared import policy by itself.

Acceptance additions: renamed models, unknown provenance, negative zero, unsafe integers, and invalid surrogates must produce equal hashes or equal rejections across implementations, beyond the successful 1/1.0 example.

## A2 — Density sampling for layer-wise trapezoidal normalization is undefined (P1)

Model and eigenfunction radial grids are independent. “Over exported samples” could mean interpolating density to region.r_m or forming a union grid and resampling everything. Both resemble layer-wise trapezoids but produce different modal factors.

Minimal revision: integrate on each region.r_m, interpolating density linearly inside its named material layer only. Apply trapezoids to rho*r^2*(u^2+v^2+w^2), one scale for the whole mode; reject zero/nonfinite integrals. Require a region to span its entire named layer, with missing layers indicating zero support, instead of leaving partial support/extrapolation ambiguous.

Acceptance addition: a two-layer fixture with different density/eigenfunction sample locations and an independently hand-calculated discrete integral.

## A3 — Quality and failure paths lack a uniformly consumable structure (P1)

The prose did not say whether quality belongs to a bundle, mode, or family/degree/domain group. Spectral completeness lacked a type and basis. A benchmark_checked label could be mistaken for a level above converged, although a frequency comparison alone says nothing about mesh convergence. Significant negative eigenvalues require failure, but the listed status enum had no failure semantics.

Minimal revision: use a small fixed structure, not a complex state machine. Per-mode quality holds independent convergence and benchmark evidence; run groups retain topology/family/degree/domain, finite-spectrum counts, and completeness. Define summary-label conditions. A requested-group failure should raise without a normal saved bundle, or appear in an explicitly incomplete result; silently losing modes with a generic warning is unacceptable. Distinguish all-fluid T being mathematically inapplicable from a solver failure returning nothing.

Acceptance additions: success, unconverged, failed-group, and legitimate-empty cases displayed correctly by CLI/browser. Benchmark evidence includes reference model, frequency convention, and discrepancy, not a boolean.

## A4 — Sampling and working-memory limits are not executable boundaries (P1)

The 512 MiB solver budget was defined, but separate degree and term limits do not bound their product or cutaway sampling. At l=64 the surface alone has about 135,000 points; 32 float64 Cartesian fields approach 100 MiB before sections, graphics buffers, morph targets, or source arrays. A 32 MiB JSON file can encode millions of short numeric values.

Minimal revision: specify total point, spatial-cache, and GLB morph-byte limits with formulas and preallocation checks. Define radial-section and arrow sampling rules. Any reduction in display quality or sequential computation must be explicit; never silently truncate degrees/terms. Solver estimates need a conservative multiplier for simultaneously live matrices and eigensolver workspace, labeled as estimates rather than OS guarantees.

Acceptance additions: requests just below/above aggregate limits; rejection before allocation; a legitimate expensive case either uses an explicit lower display quality or asks for a concrete adjustment.

## A5 — Rounding, GIF defaults, and transaction semantics can differ (P2)

Python round uses ties-to-even, while JavaScript Math.round rounds positive halves upward. A duration*fps ending in .5 therefore differs. The video API default fps=24 conflicts with a GIF policy whose defaults are 20 and whose allowed list excludes 24. Two individually atomic renames are not a media/sidecar transaction: a failed sidecar commit can leave apparently successful untraceable media.

Minimal revision: use floor(duration*fps+0.5) for positive duration, or reject nonintegral products. Prefer fps=None with container defaults, or document explicitly that GIF requires a supplied 20. Generate/validate media and manifest before final placement; failed commits must remove this run's new files and restore previous valid outputs, with an explicit overwrite policy.

Acceptance additions: a shared .5 rounding case; GIF with omitted fps; an injected final-sidecar commit failure preserving the previous complete result.

## Exact-center review: analytic support is justified

Independent substitution confirms the root agent's regular S,l=1 center formula. For A=sqrt(3/(4*pi)), the real basis has Y10=A*z/r, Y11=-A*x/r, and Y1,-1=-A*y/r. With v0=sqrt(2)*u0, the radial and tangential combination is respectively A*u0*ez, -A*u0*ex, and -A*u0*ey, independent of approach direction. Regular R/T and l>1 center displacement is zero.

Remove the artificial center hole and use this analytic branch. The center layer begins at r=0; S1 obeys the ratio, and other applicable coefficients obey regular zero values, within a mode_scale-based tolerance. An adapter may make justified upstream regularity corrections with provenance, but import must not invent values or rewrite hashes. Reject irregular input clearly instead of returning an arbitrary directional center field.

Necessary checks: exact-center values for all three m, multidirectional limits as r approaches zero, regular R/T/l>1 zeros, and one explicitly rejected irregular fixture. This is simpler than maintaining artificial holes and introduces no new physics.

## Recommended closure

Restrict revision to hash projection/domain, density interpolation in discrete normalization, fixed quality/failure structures, aggregate resource budgets, deterministic timing/commit rules, and the justified center limit. No service layer, queue, or extra architecture is needed. The third round can then walk the complete contract end to end.
