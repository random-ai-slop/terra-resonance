# Agreement implementation audit 1: independent science

Assignment AUDIT-SCI/1. **Passed on accepted integration `4aa90d93bbce43ac4b22b8b65b648434c56dbbd2`.** No runtime defect was found in this audit. The numerical implementation was authored by the independent native numerical-methods task; this reviewer wrote and ran the audit harness, not the agreement runtime.

Preparation was checkpointed before the accepted implementation arrived. Execution began only after the coordinator supplied I. The source review covered `agreement.py`, its structural schema, the bounded change to `data._read_json`, and `agreement-implementation-numerical.md`. No solver, schema, loader, evaluator or scientific reference source was edited during this audit. The only harness amendment before execution verified primary import binding and recorded runtime byte identities.

## Reproduction and source identity

Executed once:

```sh
PYTHONPATH=packages OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/validate_agreement.py \
  --integration 4aa90d93bbce43ac4b22b8b65b648434c56dbbd2 \
  --artifacts artifacts/agreement-science/audit-1
```

Exit0; runtime16.893s. Environment: Python3.13.7, NumPy2.5.2, SciPy1.18.1, macOS x86_64, one BLAS thread. The harness checked the full HEAD against I and refused dirty tracked runtime sources. Both imported `earth_modes.__file__` and `agreement.__file__` resolved inside the primary `packages/earth_modes` directory. Their exact paths, the harness SHA256 and seven runtime/schema byte hashes are recorded in [the compact evidence](../validation/agreement.json).

Agreement source SHA256 was `4a7e284a5a54b8105da5abbaccc3f629449136ae148ab00c6a9397de31ba6afb`. Runtime identity is separate from report identity: generator versions and original source provenance remain inside every complete report, while a fresh solve may have different runtime metadata and therefore a different bundle hash.

## Actual matrix

Exactly12 solves completed. Explicit expected labels produced44 cross-method rows and44 within-method refinement rows; none was absent or skipped. Sphere/shell each contain seven named identities, including degree-one positive n=1 and degree-two n=0..3. PREM contains four identities on each of the inner-core and mantle/crust solid domains.

The actual common window was1e-8..0.012Hz and degrees1..4. Sphere/shell requested targets were40/80; PREM140/280. The default solver used T only, gravity0 and n_max3. The owned pilot received no n_max. Every named row passed absolute relative frequency change<=1e-4 and shape distance<=0.003.

| Report | Rows | Maximum absolute relative frequency change | Maximum shape distance |
| --- | ---: | ---: | ---: |
| Sphere cross /40 | 7 | 8.0479e-7 | 9.5718e-6 |
| Sphere cross /80 | 7 | 5.6240e-7 | 1.2772e-5 |
| Sphere default refinement | 7 | 5.5739e-6 | 1.0369e-3 |
| Sphere owned refinement | 7 | 4.8199e-6 | 1.0367e-3 |
| Shell cross /40 | 7 | 1.0386e-5 | 1.4749e-3 |
| Shell cross /80 | 7 | 1.2440e-6 | 3.4362e-4 |
| Shell default refinement | 7 | 1.1781e-5 | 1.4578e-3 |
| Shell owned refinement | 7 | 1.9393e-6 | 5.8405e-4 |
| PREM cross /140 | 8 | 4.3279e-5 | 8.8483e-4 |
| PREM cross /280 | 8 | 1.6039e-5 | 1.6310e-4 |
| PREM default refinement | 8 | 3.4310e-5 | 8.2788e-4 |
| PREM owned refinement | 8 | 1.2002e-8 | 6.8415e-5 |

Column maxima can belong to different modes. No monotonic-improvement gate was imposed: the observed small degree-one changes need not be monotonic.

Actual solid elements confirm the distinct allocation semantics: sphere40/80 for both methods; shell default26/54 versus owned40/80; PREM default101/186 versus owned241/357. PREM inner/mantle totals were default20/81 and owned64/177 at140, then default45/141 and owned96/261 at280. Full per-material counts and actual radial sample counts are recorded for every solve and row, not inferred from requested target or from each other.

## Independent arithmetic and adversarial evidence

The independent oracle reconstructs each original layer's linear W and density, multiplies interval-local polynomials in extended precision and integrates coefficients analytically. It does not call production Gaussian quadrature, evaluator internals or FE mass matrices. All88 physical rows and11 manufactured comparison reports were checked against it.

Maximum absolute disagreement between production and the separate polynomial oracle was4.44e-16 for continuous norms,2.22e-16 for overlap, and3.06e-17 for shape distance. These measure implementation agreement on stored reconstructions, not continuum error.

The manufactured comparisons and22 logged counterexample outcomes established:

- The same linear field sampled on different grids, with different valid canonical discrete scaling factors, has zero normalized shape distance; a whole-field sign reversal retains zero distance and reports−1.
- A density knot absent from either W grid is retained. Independent rational integrals AA=727/1215, BB=64007/155520 and AB=75931/155520 yield the expected distance approximately0.179667758143.
- Two continuous material-side fields with opposite outer-layer signs and density ratio91/11 give zero overlap and distance sqrt(2). Alignment is indeterminate with fixed+1; separate material paths and reference-minus-candidate residual orientation remain intact.
- Matching incomplete supports and forged domain labels across a fluid gap fail. Explicit different-n pairs remain accepted and labelled as mismatched.
- A1e-9 shape perturbation and a representable approximately4e-15Hz frequency difference remain nonzero. Erasing the stored frequency difference fails validation.
- Tolerated inward and outward endpoint offsets preserve the original interpolated/clamped tails, use declared integration boundaries and leave input identities unchanged. Beyond-tolerance offsets fail.
- Different canonical models, zero/nonfinite fields, known linear-Q conflicts, malformed declarations, stale effective-model hashes and different embedded effective models fail. The existing elastic reference and embedded-model declarations are accepted; genuinely absent declarations remain allowed.
- Negative stored distance, out-of-range overlap, Boolean numeric values, a changed norm and an altered source hash fail rather than passing arithmetic tolerance.

All reports were reloaded and revalidated, with canonical report identities unchanged. Complete source bundles, explicit pair order, source quality/provenance, material support and mesh/sample metadata were checked against the inputs. The audit used explicit assertion functions, so its gates remain active under Python optimization.

## Evidence retained and limits

Ignored `artifacts/agreement-science/audit-1/` retains12 complete solver bundles,23 self-contained comparison reports and the audit summary. Bundle/report artifact bytes total28,189,058, excluding the compact summary. Every artifact has a serialized SHA256 and canonical hash in the compact evidence; each report records both full source bundle hashes. Public evidence contains metrics, identities, requests and mesh maps rather than embedding the large source arrays again.

The existing nineteen-case independent reference evidence was identified by file SHA256 and **not rerun or modified**. Its original frequency/shape scope remains separate. This audit does not certify arbitrary PREM shapes, demonstrate continuum convergence or promote the owned pilot. The default and owned methods still approximate variable material profiles differently.

Source inspection found no additional scientific contract discrepancy requiring author repair. The only pre-execution harness change added the requested import/runtime identity checks; no failed runtime result was hidden or converted into a pass. There was no solver rerun after the successful full audit.

Scientific audit1 is complete for I. Actual CLI/export/sidecar recovery, inspected minimum-size SVG/PNG, the copied independent Bessel recipe, and isolated wheel/sdist/source-release checks remain the distinct later audits. They are not closed by these numerical results.
