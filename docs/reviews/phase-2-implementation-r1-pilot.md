# Phase 2 implementation review 1: independent toroidal pilot

Reviewed 2026-09-04 by the product/export reviewer, who did not implement this numerical module. Scope: experimental API, weak-form assembly, branch identity, numerical evidence and publicly stated boundaries. No implementation files were changed during review.

## Result

**No release-blocking defect found within the frozen pilot scope.** The module is independently assembled and remains an explicit experimental API. Its outputs correctly retain `unverified` physical quality despite strong fixture evidence. This is not approval to replace the default solver or extend the measured error bounds to arbitrary profiles/high branches.

## Code and contract checks

- The weak form uses SI density and shear speed, with `mu=rho*vs²` at quadrature points. Four-point Gauss quadrature integrates the resulting degree-seven material/basis products on each profile interval. Original knots become element boundaries rather than being silently resampled away.
- Adjacent solid layers share degrees of freedom and one domain identity; fluid layers separate domains. Natural shell endpoints have free traction, and a solid center imposes W(0)=0. Only solid W regions are emitted; U/V are zero and no potential or fluid displacement placeholders are fabricated.
- For l=1, the code verifies the scaled stiffness residual of W proportional to r and removes that single null coordinate in mass-whitened space using a Householder complement. It checks the remaining relative gap rather than applying a universal frequency cutoff. Positive branches begin at n=1; l>=2 begins at n=0. Inclusive frequency selection follows branch numbering and does not renumber a restricted window.
- Cholesky verifies mass SPD; symmetry, scaled residual and mass orthogonality gates are enforced before results are returned. FE diagnostics use the quadratic basis. Exported piecewise-linear samples receive one global, layerwise-trapezoid mass factor and one sign, with that distinction recorded in provenance.
- Input models are copied, Q is retained but explicitly not applied, empty/all-fluid cases carry truthful group status, and invalid requests fail. The memory estimate includes mandatory-knot dimensions and conservative accumulated output before dense assembly. No vendor assembly/mesh helper or fallback dispatch is called.

## Independently repeated evidence

Ran `OPENBLAS_NUM_THREADS=1 .venv/bin/python -m pytest -q tests/test_owned_toroidal.py tests/test_examples.py`: **15 passed**, comprising 13 pilot cases and two installed-example cases.

Re-executed `scripts/validate_owned_toroidal.py` with its evidence destination redirected to a temporary tree containing copies of the checked-in MINEOS references, leaving the submitted evidence unchanged. All **19 required comparisons** were present, in the same mode identity order as the recorded report. Maximum computed-frequency difference from the submitted JSON was **0 Hz** in this environment.

| Check | Repeated result | Required gate |
| --- | ---: | ---: |
| Largest relative frequency error | 7.2764291561e-6 | 0.005 |
| Largest sign-aligned mass shape error | 0.00021958396054 | 0.01 |
| Named comparisons | 19 | exactly 19 |

The reference paths are meaningfully independent: sphere Bessel roots/shapes; hollow-shell first-order traction ODE; saved MINEOS values for mantle and inner l=1; knot-resolved strong-form traction ODE for inner l=2/3/4. PREM shape agreement is not claimed. Artificially splitting identical material preserves frequencies and interface W. Full group diagnostics include both PREM solid domains and their rigid rotations. Lookups and the explicit case-count assertion prevent silently dropping a missing named branch.

Temporary recomputation evidence was written under `terra-pilot-review-e86gfc5u` in the system temporary directory. Runtime was about 1.96 seconds with one BLAS thread; runtime is not an accuracy gate.

## Boundaries to preserve at release

1. These are named-fixture frequency/shape checks, not a convergence certificate for all emitted high discrete branches, large contrasts or arbitrary user models. The existing warnings and unverified status are appropriate.
2. The pilot supports elastic isotropic toroidal modes only. Q dispersion, R/S families, source excitation, anisotropy and rotation remain outside this API.
3. The source recipe and in-repository tests are not proof of wheel packaging. The separate clean-wheel release workflow must import and call the experimental API from outside the checkout, with no repository PYTHONPATH.
4. Keep the canonical exported mass interpretation separate from constrained FE orthogonality. Neither normalized scene coefficients nor an unforced eigenfunction constitutes a source-calibrated displacement in metres.

No additional framework, backend registry or general benchmark machinery is needed for this bounded pilot. The next ownership decision should follow the documented physical/performance gates, rather than interpreting this successful experiment as an automatic backend migration.
