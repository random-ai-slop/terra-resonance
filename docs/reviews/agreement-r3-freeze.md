# Toroidal agreement: round 3 freeze review

Assignment DEV-R3-FREEZE/1. Reviewed the **revision-2 superseding section** of PHASE-3, both round-2 reports, the round-1 scientific experiment and accepted runtime03eacc3. Only this report was written. No solver execution, implementation, commit or reference regeneration was required for this review.

## Disposition

**Ready to freeze after two narrow contract corrections below.** The selected scientific scope and installed journey are sufficient. Neither another design round nor additional physical capabilities are justified by this review. Integrate the corrections into the frozen document, then assign isolated implementation ownership separately.

Keep the dedicated elastic-T API, complete embedded bundles, one recomputing evaluator, material-sided curves, explicit pair selection, two-axis figures and the small installed recipe. Keep the existing general comparison untouched. Remove no scientific acceptance case; add no general provenance framework, automatic tracking or new solver work.

## 1. Resolve the declared-effective-model rule precisely

This remains less exact than the rest of revision2. Generic `data.validate_bundle` validates the bundle model and scientific fields but does not interpret `bundle.provenance.request` or `effective_model`. The default elastic adapter writes `{reference:'bundle.model'}`; its linear-Q path writes `{model:<full effective Model>,model_hash:<hash>,method:...}` while restoring the original reference model at `bundle.model`. The experimental adapter has no effective-model object and explicitly declares elastic attenuation semantics.

Consequently, equal bundle model hashes and null selected modal Q do not by themselves implement the promised rejection of **known declared** effective-model conflicts. A copied otherwise valid bundle can contain a contradictory effective model without generic validation rejecting it. Conversely, requiring every input to carry the default adapter's declaration would incorrectly reject the experimental output.

**Minimal frozen rule:** inspect only the existing known paths; preserve all other metadata without trying to understand arbitrary solver prose.

- An absent `provenance.request.linear_q` is unknown; a present value must be Boolean. True is ineligible even when selected modes have q=null. False does not establish independent validation.
- An absent `provenance.effective_model` is unknown and allowed. A present known declaration must be an object.
- If `reference` is present, require exactly `'bundle.model'`. Do not silently accept a different reference path as an unspecified external format.
- If `model` is present, validate that full Model and recompute its canonical model hash. Require equality with the common bundle-model hash. If `model_hash` is also present, require it to equal the computed value; do not trust the asserted hash instead of inspecting the model. A reference plus model is allowed only when both checks agree.
- A present `model_hash` without `model` or the recognized reference is not a complete supported declaration: fail with a specific message rather than interpreting it as proof of the effective model. A present object with neither recognized model nor reference likewise fails. Unknown additional fields inside a recognized declaration remain intact.

This is a bounded interpretation of existing reserved fields, not source authentication. A third-party bundle with these fields absent is still measurable under its declared canonical model, with unknown method provenance. No agreement score certifies that an external solver actually used that model. Add one focused test covering the two existing accepted shapes, absence, a contradictory effective model and a stale asserted hash; it can reuse an existing valid fixture without solving again.

## 2. Validate numeric types and physical ranges before arithmetic closeness

Revision2 correctly uses exact source frequencies and subtraction order, relative-only tolerance for positive norms, and a machine floor for overlap/distance. Make explicit that closeness is the **last** check, after type and range validation. Otherwise literal application of its tolerance accepts internally impossible saved values.

A direct float64 calculation gives:

- Expected distance0 and stored distance−1e-15 pass `64*eps + 1e-12*abs(expected)`.
- Expected overlap1 and stored overlap`1+1e-13` pass that rule as well.
- Python `False == 0.0` is true; equality alone does not enforce the table's distinct Boolean and numeric types.

**Minimal correction:** numeric row fields reject booleans and nonfinite values; norms must be strictly positive; stored absolute overlap must lie in[0,1], signed overlap in[−1,1], and distance must be nonnegative and at most`sqrt(2)+64*eps`. These stored overlap ranges are compatible with the specified roundoff-clipped evaluator output. The evaluator may clip a raw Cauchy violation only within its stated roundoff allowance; a larger violation fails. Then apply the quantity-specific recomputation tolerances. Flags must be actual booleans; signs must be integer±1 excluding booleans.

Use the existing JSON wire integer convention for report labels/counts/indices: integer-valued finite safe numbers such as1.0 are valid, booleans are not. Public `pair_index` arguments should follow the same unambiguous index rule or explicitly require native integers; choose and state one before separate compute/export implementations start. Do not silently coerce strings or fractional values. Add tampered-negative-distance and Boolean-as-number variants to the existing tampered-row test rather than creating a separate test framework.

## Resolved scientific issues: retain as written

**Alignment and small residuals.** Fixed+1 inside`abs(c)<=64*eps` is consistent with an indeterminate presentation choice; outside it, sign(c) minimizes the residual. The distance must use that chosen sign, and the plot must not realign independently. At c=−64*eps, the ideal fixed-sign distance exceeds sqrt(2) by approximately1.0e-14, below the proposed64*eps allowance. A specific threshold-consistency failure on reload is preferable to hidden hysteresis. Direct residual quadrature preserves small differences; do not replace it with subtraction of nearly equal overlap values.

**Norm and curve authority.** Per-layer partitioning includes density and both W grids, giving exact degree-five quadrature for the canonical linear reconstructions. The evaluator's recomputed A/B/sign drive curves, CSV and plot annotations. Saved JSON and sidecars retain the validated historical report and generator version. This permits documented arithmetic tolerance without making tolerance-accepted stored norm values a second plotting authority. Raw input arrays and hashes remain unchanged. Comparison normalization is distinct from the existing discrete canonical norm and from quadratic FE mass.

**Support.** Same full canonical model plus an identical complete maximal connected solid component is the correct bounded eligibility rule. The same incomplete subset on both sides must fail. Fluid-separated domains cannot be merged through a provenance label. Different explicit n labels remain measurable and visibly flagged; degree must match. Missing expected trial identities must fail rather than reduce the matrix.

**Report/CSV/limits.** The row table, ordered explicit pairs, per-layer nullable mesh counts, scalar CSV totals, top-level reloadable sidecar and single-pair figure rule are sufficient. Figures cannot filter saved source/report content. Full provenance is already embedded, so no additional registry or duplicated normalized curves are needed. Fixed byte/interval limits have clear counting semantics and apply to API inputs and sidecars; they are rejection bounds, not memory guarantees. Reject unsupported export options before publication and retain the existing artifact-plus-sidecar transaction behavior.

**Interpretation.** Default element-averaged nodal moduli and pilot quadrature of separately interpolated rho/vs differ for variable material profiles. This caveat is retained through the incorporated round-1 contract. Same canonical input and small code differences do not prove equal finite-mesh operators or continuum accuracy. Neither small refinement change nor agreement promotes the input mode's quality status.

## Acceptance sufficiency and exact counting

The full experiment has22 identities: seven sphere, seven shell, and four on each of PREM's two solid domains. Two methods at two requested meshes across three models give exactly12 solves. Cross-method comparison at both meshes gives44 rows. One coarse-to-fine comparison for each method gives44 additional refinement rows. These totals are consistent; do not count solver-returned extra modes as additional named evidence or discard an expected pair when a window changes.

The R1 observed maxima support the proposed **named regression** ceilings of1e-4 absolute relative frequency change and0.003 shape distance for both sets of rows. These ceilings are intentionally looser than the observed maxima and are not public default accuracy tolerances. Retain exact source requests, per-layer/domain actual counts and full output identities. Do not require monotonic improvement: actual degree-one cases already contradict such a gate at small differences.

The existing nineteen independent-reference cases remain valid evidence under their own original quantities and interpolation rules. The copied four-solve recipe independently evaluates its Bessel frequency reference and distinguishes its four agreement/refinement reports from that separate scalar accuracy result. This provides an installed independent check without requiring repository data or repeating expensive unrelated physics.

The adversarial coverage is sufficient when it actually includes: different valid canonical scalings of the same linear field; a density knot missing from both W grids; a material-side density jump with a single global-sign counterexample; matching incomplete supports; tiny nonzero shape and frequency differences; tolerated endpoint tails without input mutation; and invalid/zero/nonfinite data. The R1 rational integral constants give a genuinely separate arithmetic oracle. The two small additions above fit within these fixtures and the existing tampered-report checks.

Keep the three proposed implementation audits distinct and sequential after repairs: scientific counterexamples/full matrix; actual installed API/CLI and inspected artifacts; frozen wheel/sdist and source identity. Artifact legibility and actual packaging behavior remain things to demonstrate after implementation, not claims made by this freeze review.
