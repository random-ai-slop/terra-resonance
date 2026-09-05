# Toroidal agreement: scientific design round 1

Assignment DEV-R1-SCI/1. Reviewed public source `03eacc363749a0ae8d47f3dd9d7298fae678628a`, `CONTRACT.md`, `analysis.py`, both T implementations, `validation/OWNED-TOROIDAL.md` and `workflow-r1-trial.md`. This is a bounded design recommendation supported by exploratory runs, not implementation approval or a new accuracy certification. No solver, bundle, reference evidence or runtime file was changed.

## Decision

**Keep the selected trial.** It fills a useful installed-analysis gap without expanding the physical solver. Add a dedicated elastic T agreement function/report; retain the existing `compare_bundles` semantics for general, explicitly selected, potentially different-model comparisons. Do not require a browser metric implementation, automatic tracking, subspace matching or solver promotion.

The following distinctions are necessary, not optional refinements:

- Same canonical input model is a conservative eligibility condition; it does not prove identical discretized material operators.
- Canonical trapezoid normalization and continuous interpolated-shape normalization are different quantities.
- Code agreement, each method's mesh change and independent reference accuracy need separately identified rows. None implies either of the others.

## Eligibility and pairing contract

Validate both complete ModeBundles without modification before producing any result. Require nonempty explicit `(reference_mode_id, candidate_mode_id)` pairs; unknown IDs or one invalid pair fail the request before artifact creation. Do not skip missing expected modes or choose nearest frequencies.

For every pair:

1. Both families are T, both degrees are the same positive integer, both frequencies are positive, and modal `q` is null. This increment concerns elastic real radial eigenfunctions. Reject a known `linear_q=True` request or an explicitly different effective material model. Material Q stored but not applied by the experimental solver is allowed. An absent third-party method declaration is **unknown**, not evidence of independent elastic computation; the report measures declared canonical data and cannot authenticate its provenance.
2. Require equality of the existing `data.model_hash` computed from `bundle.model`, not names or a supplied provenance hash. That hash includes every non-provenance model key, including IDs, names, material sample positions, Q and reference frequency. Renaming otherwise equal data can conservatively fail eligibility. Explain this rather than adding a physical-model matching system in this trial.
3. Derive maximal connected solid domains from model layer order and phase. Each mode must contain **exactly all material regions of one such domain**, and both must select the same domain. Sort only local lookup views by model order; do not alter stored arrays. Matching incomplete supports, subsets spanning a fluid gap, or two different solid domains are ineligible even if their `solid_domain_id` strings match. A mode may have zero values inside one included region; zeros are not a reason to remove it. Treat provenance domain labels as reported metadata, not proof of support.
4. Explicit pairs may have different IDs and radial labels `n`; record both and a visible label-mismatch flag. Equal `n` is the normal trial selection, not a mathematical prerequisite for comparing two radial shapes. Requiring identical `n` would prevent an explicit wrong-branch diagnostic or a future documented external-label mapping. Equal degree is required because the canonical angular bases depend on degree. No azimuthal `m` selection is needed for this radial T metric: compare the same normalized angular basis, not arbitrary rotated three-dimensional fields.

For the two current methods, positive degree-one modes retain the rigid-rotation slot: first positive T is `n=1`; for degrees two and above it is `n=0`. Preserve these labels. MINEOS inner-core `I` labels require the existing explicit mapping; they are not interchangeable with a guessed T label.

## Exact measure for the stored fields

On material layer j, let `a_j(r)` and `b_j(r)` be **the canonical piecewise-linear reconstructions of stored W**, and let `rho_j(r)` be the model's independently piecewise-linear density. Define

\[
\langle a,b\rangle_\rho=\sum_j\int_{r_j^-}^{r_j^+}\rho_j(r)r^2a_j(r)b_j(r)\,dr,
\quad A=\langle a,a\rangle_\rho,\ B=\langle b,b\rangle_\rho,
\quad c=\langle a,b\rangle_\rho/\sqrt{AB}.
\]

Use **one whole-domain** sign `s=-1` when `c<0`, otherwise `s=+1`, and report

\[
\operatorname{overlap}=|c|,\qquad
 d=\left[\sum_j\int\rho_jr^2\left(a_j/\sqrt A-sb_j/\sqrt B\right)^2dr\right]^{1/2}.
\]

Also retain signed `c`, alignment sign, A and B. The ideal ranges are overlap in [0,1], and d in [0,sqrt(2)]. These are dimensionless; W retains kg^(-1/2). Frequency fields are `f_a`, `f_b`, `delta_hz=f_b-f_a` and signed `relative_delta=(f_b-f_a)/f_a`. The designation “reference” here means the denominator, not physical truth.

Calculate d by integrating the normalized difference directly. Do **not** implement it solely as `sqrt(2-2*abs(c))`: cancellation would erase the small errors observed in real sphere cases. A separate squared-overlap/MAC column adds no independent information and is unnecessary initially.

The norm A or B is generally not exactly one. `CONTRACT.md:19–21` and `data.mass_integral` deliberately define exported normalization by the layer-wise trapezoid on **each mode's own sample grid**. Do not change that convention, substitute this comparison norm into validation, or silently rescale either input bundle. Report separate comparison scaling factors; plots may display these normalized, globally aligned curves while keeping raw arrays available with an explicit label.

### Quadrature and material sides

For each named material layer separately, construct the sorted union of:

- that layer's two declared endpoints and all its interior density/profile knots;
- every strictly interior radial sample of the reference region;
- every strictly interior radial sample of the candidate region.

Do not concatenate materials into one interpolation table. At a material interface, integrate each side with its own density and W arrays. Equal physical radii on two sides must survive in plotted/raw regional data; interpolation must never bridge the interface.

On each union interval, density is linear, each W is linear, and r² is quadratic. Every norm, cross product and squared normalized residual is therefore a polynomial of degree at most **five**. Three-point Gauss–Legendre quadrature is exact for these reconstructions up to floating-point arithmetic. It does not claim exactness for the original quadratic FE fields or the continuous physical eigenproblem. Retaining both W grids without density knots is insufficient.

Endpoint rule: existing validation permits region endpoints within `64*eps*R` of a model boundary. Integrate on the model layer's actual declared bounds; clip the partition to those bounds, retain all strictly interior original knots, and evaluate the **original** arrays with the field path's linear interpolation/endpoint-clamping semantics. Thus a tolerated short uncovered tail is constant, while an endpoint just outside a boundary is interpolated at the boundary. Do not move stored endpoint coordinates or linearly stretch the region. Outside the existing tolerance the bundle is invalid. Layer boundaries themselves remain the model's separate declared sides; do not average adjacent radii or density values.

Reject zero, negative or nonfinite comparison norms and any nonfinite result; do not replace them with an arbitrary floor. Canonical validation already rejects a raw all-zero or arbitrarily rescaled input. For numerical stability, locally scale W by a positive amplitude before integration, restoring A/B where representable, and use stable summation. Do not identify “zero norm” with a dimensional fixed threshold. If calculations remain unrepresentable, raise a clear numerical-range error.

Use a small roundoff allowance, provisionally `64*eps`, for overlap clipping and `alignment_indeterminate = abs(c)<=64*eps`. A near-zero signed overlap can change sign across machines; preserve the actual deterministic sign rule while marking its interpretation as indeterminate. A substantial Cauchy–Schwarz violation is an error, not a value to hide by clipping. Review the allowance against the bounded implementation's summation in round 2.

## Reproducibility and the material-operator caveat

The report must preserve computed hashes of **both unchanged input bundles** and the common canonical model hash, all explicit pairs, source solver identities/requests, original quality evidence, actual per-layer mesh counts and radial sample counts. For a self-contained report, retain the selected raw region arrays and density profiles, or an equally complete checked input attachment. Report schema/metric version, interpolation/quadrature rule and one alignment factor per pair. Fresh solver runs contain runtime provenance, so full bundle hashes need not repeat even when physical results repeat.

`solver.py:_prepare` interpolates nodal `rho*vs²`, samples uniformly per material and assigns element averages. The experimental `_assemble` interpolates rho and vs separately at quadrature points and multiplies `rho*vs²`; `_plan` preserves every original profile knot. These are **not identical material approximations** for a variable profile. PREM agreement is between methods receiving the same canonical profile, not proof that their finite-mesh operators are identical. Do not silently rewrite either solver to improve agreement in this trial. Preserve this difference in provenance and in the discussion of any residual plateau.

Likewise, equal requested mesh sizes are not equal actual resolutions. Report domain/per-layer elements and samples, not a single misleading “same mesh” badge. Mesh refinement evidence is a comparison of two outputs from one named method, not a Richardson accuracy estimate. Do not promote `mode.provenance.quality`, attach new frequency benchmarks to input modes, or label arbitrary reports “validated.”

## Actual bounded feasibility experiment

Ran both existing APIs in memory at the reviewed source, with one BLAS thread and the local package environment. A short independent exploratory calculation used the three-point, per-layer union quadrature above; it is not an implemented/public analysis API. The first request with `frequency_min_hz=0` failed because the default solver requires a positive lower bound. The common executable request is **1e-8 through 0.012 Hz**, degrees 1..4, default gravity 0 and `n_max=3`; the pilot receives no `n_max` option. Twelve solves and 44 explicitly looked-up cross-method pairs completed; no expected pair was omitted.

Models and named pairs:

- Sphere: `homogeneous_model(1e6,4000,8000,4000)`; domain `solid:sphere`; `T1_1`, `T0_2`, `T1_2`, `T2_2`, `T3_2`, `T0_3`, `T0_4` at requested 40 and 80. Model hash `705e9d064115d20d2e9b8b9ea24e3cf5ae80b06f936d482b50f15c721a79dea3`.
- Shell: same properties, fluid interior 0..0.3R, solid 0.3R..R, model ID `pilot-shell`, layer IDs `fluid` and `shell`, as `validate_owned_toroidal.shell_model`; same seven labels on `solid:shell`, requested 40 and 80. Hash `cd5801948b7204833815f95b09a517400a6a6831d323423717b99ff1b4434636`.
- PREM: `prem_model()`; `T1_1`, `T0_2`, `T0_3`, `T0_4` on **each** of `solid:prem-00` and `solid:prem-02,...,prem-12`, requested 140 and 280. Hash `0481d664b43d0243bdcbb009e99f532fffecf70b121dce5369e8bec417702052`.

| Case / target | Default actual solid elements | Pilot actual solid elements | Maximum absolute relative frequency difference | Maximum shape distance d |
| --- | ---: | ---: | ---: | ---: |
| Sphere / 40 | 40 | 40 | 8.0479e-7 | 9.5718e-6 |
| Sphere / 80 | 80 | 80 | 5.6240e-7 | 1.2772e-5 |
| Shell / 40 | 26 | 40 | 1.0386e-5 | 1.4749e-3 |
| Shell / 80 | 54 | 80 | 1.2440e-6 | 3.4362e-4 |
| PREM / 140 | 101 | 241 | 4.3279e-5 | 8.8483e-4 |
| PREM / 280 | 186 | 357 | 1.6039e-5 | 1.6310e-4 |

Default shell fluid elements are 14/26; PREM fluid elements are 39/94. Pilot allocates none in fluids. PREM inner/mantle totals are respectively default20/81 versus pilot64/177 at140, and default45/141 versus pilot96/261 at280. These differences explain why nominal mesh targets must not substitute for actual metadata.

| Refinement | Default max absolute relative frequency change / d | Pilot max absolute relative frequency change / d |
| --- | ---: | ---: |
| Sphere 40→80 | 5.5739e-6 / 1.0369e-3 | 4.8199e-6 / 1.0367e-3 |
| Shell 40→80 | 1.1781e-5 / 1.4578e-3 | 1.9393e-6 / 5.8405e-4 |
| PREM 140→280 | 3.4310e-5 / 8.2788e-4 | 1.2002e-8 / 6.8415e-5 |

These are separate column maxima, not necessarily the same mode. Sphere T1_1 shape agreement changes from9.57e-6 to1.28e-5; shell T1_1 frequency agreement also grows slightly under refinement. **Do not require every error to decrease monotonically.** Small null-space/numerical effects make that an unsound gate even in simple real fixtures.

For these named regression cases only, proposed initial ceilings are `abs(relative_delta)<=1e-4` and `d<=0.003`, covering both resolutions and each method's refinement with explicit headroom. These are starting acceptance proposals for round 2/3, not universal package defaults or achieved physical accuracy. The API should report measurements without inventing a universal pass threshold. Manufactured exact-metric checks should instead use float64-scale tolerances, provisionally1e-12 on well-conditioned dimensionless results. Independent references retain their separately scoped gates: the existing nineteen-case evidence uses0.5% frequency and1% shape ceilings, and does not claim PREM shape accuracy. Reuse/recompute those named references separately; do not replace them with code agreement or relabel old4001-point reference-shape values as this new exact-interpolant metric.

## Necessary independent adversarial fixtures

Each manufactured mode must be made a valid canonical bundle using the existing **discrete** normalization first. Its manufactured/unverified provenance must remain explicit. The expected integrals below can be evaluated by rational polynomial antiderivatives independently of the implementation's Gaussian rule.

1. **Same field, different canonical factors.** Uniform-density sphere with W=r, sampled on `[0,R]` versus `[0,R/2,R]`. Before scaling, the discrete integrals differ (for R=rho=1, 1/2 versus9/32), while the exact continuous integral is1/5. After separate canonical normalization, overlap must be1 and d0. A whole-mode sign reversal must return sign−1 with the same distance. Arbitrary unnormalized input rescaling must fail validation rather than be a public invariance test.
2. **Density knot absent from either mode grid.** In dimensionless radius x, density samples `[0,1/3,1] -> [1,9,1]`; A(x)=x, B has samples `[0,1/2,1] -> [0,1/4,1]`. Before canonical scaling, exact weighted integrals are AA=727/1215, BB=64007/155520, AB=75931/155520. The normalized distance is approximately0.17966775814299688. SI scales cancel. This fails if density is interpolated only on eigenfunction knots or if B is treated as a quadratic rather than the stored linear reconstruction.
3. **One sign across a material interface.** Two adjacent solid layers split atR/2. A is the continuous triangular function with values `[0,1,0,1,0]` at x=`[0,1/4,1/2,3/4,1]`; B equals A in the inner layer and −A outside. Set constant densities in ratio inner/outer=91/11. The unweighted r² shape integrals are11/960 and91/960, giving equal mass contributions. Both fields vanish at the interface and are continuous. Expected signed overlap0, d=sqrt(2), indeterminate alignment. Per-layer sign choice would incorrectly report perfect agreement. Keep separate density sides; flattening the density jump changes the expected metric.
4. **Eligibility cannot trust labels.** In a two-solid-domain model, forge equal provenance domain strings for modes on different domains: reject. Omit the same layer from both sides of a connected multi-material domain, renormalize the surviving regions, and reject even though generic bundle validation permits them. An explicit equal-degree/different-n pair should produce a poor agreement measurement and a label-mismatch flag, not silently change its pair.
5. **Small residual and boundaries.** Add a1e-9 independent shape perturbation, canonically normalize and verify a nonzero d against an independently integrated residual. Exercise tolerated inward and outward region endpoint offsets against explicit clamped/linear tails; hashes must remain unchanged. Offsets beyond tolerance, zero/nonfinite norms, different model hashes and a known linear-Q effective model must fail clearly.

## Required changes before freeze

Keep the limited T scope, explicit pair selection and existing independent references. Change “same physical model” wording to the precise conservative canonical-model condition; change “same mesh” to actual allocation metadata; remove raw-rescaling-as-valid-input and monotonic-refinement requirements. Add exact density/field union quadrature, full connected support, endpoint behavior, the near-zero alignment flag and the material-operator caveat. In round 2, agree the small public schema and how refinement/reference rows attach without implying unperformed evidence. In round 3, freeze named case counts, error ceilings and complete source/hash artifacts before implementation. No new physical solver capability is needed to make this trial scientifically useful.
