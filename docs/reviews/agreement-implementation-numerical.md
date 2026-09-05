# Numerical agreement implementation handoff

Task/attempt: NUM-IMPLEMENT/1. Owner: Terra numerical methods, native task
`01a06fdf-c9ca-7580-9cd5-1c5c3cd21ac1`. Accepted input B:
`f88431ce62eb0a73b0abd2a162795149eed6f0a1`, PHASE-3 revision 3 including the
three design rounds. Output H is the containing implementation commit reported
in the native handoff; no archival bootstrap history is merged.

## Scope and result

Assigned changes only:

- `packages/earth_modes/agreement.py`: pure explicit-pair evaluator, complete
  source checking, report validation/loading, material-sided comparison curves
  and lazy export facade.
- `packages/earth_modes/data.py`: optional `max_bytes` for the existing strict
  JSON reader; omitted bounds preserve its previous behavior.
- `packages/earth_modes/assets/schema/agreement.schema.json`: structural report
  contract with the existing relative ModeBundle schema reference.
- `tests/test_agreement.py`: independent integral fixtures, invalid-input and
  report/resource boundaries, compatibility and a real two-method smoke case.
- This report.

The evaluator uses three-point Gauss integration on each material's union of
actual layer endpoints, interior density knots and both original W grids.
Interpolation retains original endpoints and clamps only as the existing field
contract does. One sign covers the full connected support. Norms and residuals
use scaled amplitudes, radius and density, `math.fsum`, and exponent-aware
restoration of positive dimensional factors. The distance is integrated from
the normalized residual directly, retaining a nonzero 1e-9 shape perturbation.
No solver, source quality, canonical normalization, source array or model is
modified. Complete bundles are embedded and hashed without mutation.

Bounded encoding uses the exact writer convention: UTF-8, `ensure_ascii=False`,
`indent=2`, and a final newline. Limits are 64 unique pairs, 200,000 total union
intervals counting each explicit pair, 64 MiB per bundle and 160 MiB per report.
Cheap pair/shape/sample checks precede cloning or quadrature; exact bounded
partition counting precedes all quadrature. File input reads at most bound+1
bytes. These rejection limits are not a measured peak-memory promise.

## Consumer boundary

The frozen public functions are available from `earth_modes.agreement`:

- `toroidal_agreement(reference, candidate, pairs) -> dict`: detached report.
- `validate_agreement(report) -> dict`: returns the same mapping unchanged after
  structural, source/hash, eligibility and recomputed-row checks.
- `load_agreement(path) -> dict`: bounded strict JSON parsing plus validation.
- `agreement_curves(report, pair_index) -> list[dict]`: ordered material records
  with `layer_id`, `r_m`, `reference_w`, `candidate_w`, `residual_w` lists.
  Candidate W includes the single selected sign; residual is reference minus
  aligned candidate. Safe integer-valued JSON numbers are accepted as indices;
  booleans, fractional/out-of-range numbers and strings fail.
- `export_agreement(report, path, *, pair_index=None, width=None, height=None,
  overwrite=False)`: lazy facade; actual export implementation is the receiving
  package task's dependency and is not present at this numerical checkpoint.

For one checked export operation, the package implementation can call private
`_checked_evaluation(report)`, which performs full validation and returns
`{model_hash, pairs, rows, curves, bundle_hashes}`. `curves[i]` is the complete
material list for pair i. It is not an unchecked/already-validated bypass.
Use its recomputed rows and curves for CSV/figure numerics, preserving the
original validated report for JSON and sidecars. The bundle hashes are in
reference/candidate order. Private `_bounded_json_size(value, limit, name)` and
`MAX_BUNDLE_BYTES` / `MAX_REPORT_BYTES` share exact serialization checks with
that consumer. Sidecars must include their extra production metadata in the
160 MiB check. The bounded reader is `data._read_json(path, max_bytes=...)`.

Unknown JSON extensions and historical `generator_version` remain intact.
Known request.linear_q/effective_model declarations follow the frozen narrow
rules. Declared mesh counts are checked positive safe integers; absent counts
remain null and are never inferred from radial sample counts. Saved numeric
rows are type/range checked before applying their quantity-specific tolerance;
frequency fields use exact expression equality. A sign/flag disagreement has
an explicit alignment-threshold consistency error.

## Executed self-checks

Interpreter and import binding were verified with:

```sh
env PYTHONPATH=/Users/veritaswang/.codex/worktrees/69a8/free-oscillation/packages OPENBLAS_NUM_THREADS=1 /Users/veritaswang/Desktop/code/random-ai-slop/free-oscillation/.venv/bin/python -c 'import earth_modes; print(earth_modes.__file__)'
```

Observed import:
`/Users/veritaswang/.codex/worktrees/69a8/free-oscillation/packages/earth_modes/__init__.py`.

Final combined check:

```sh
env PYTHONPATH=/Users/veritaswang/.codex/worktrees/69a8/free-oscillation/packages OPENBLAS_NUM_THREADS=1 /Users/veritaswang/Desktop/code/random-ai-slop/free-oscillation/.venv/bin/python -m pytest -q tests/test_agreement.py tests/test_data.py
```

Result: **77 passed in 17.34 s**, exit 0. This covers 70 agreement cases and
7 existing data cases. `git diff --check` also exited 0. Schema JSON was parsed;
its required fields and local embedded schema references were checked against a
real generated report. No separate JSON Schema engine is installed in this
environment; runtime semantic validation does not depend on one.

Meaningful failure cases include matching partial supports and forged matching
domain labels, different domains across a fluid, different canonical model,
modal Q, mismatched degree/family, zero/nonfinite raw fields, malformed/stale
known effective-model declarations, altered metrics and hashes, Boolean numeric
fields, nonfinite rows, duplicate/missing pairs, wrong indices, malformed mesh
counts, duplicate JSON keys, nonfinite JSON literals, and exact byte/interval
budget boundaries. The coordinator's pre-integration malformed `mode.id=[]`
finding was fixed before handoff; lists, objects, booleans, null and empty IDs
now receive clear ValueError messages before set membership.

Independent scientific oracles include the R1 rational density-knot constants
(AA=727/1215, BB=64007/155520, AB=75931/155520), different canonical trapezoid
factors for the same continuous linear field, an equal-mass two-material
opposite-sign fixture, a separately integrated polynomial residual for a 1e-9
perturbation, and analytic inward/outward endpoint-tail norms. The broad
comparison API still retains supplied signs and permits different models.
A fresh-process check confirms importing agreement does not import Matplotlib,
the experimental solver or the future exporter. The existing package initializer
already imports the default solver module; agreement does not call it.

Initial development checks caught a NumPy Boolean leaking into a report flag;
using a native float roundoff constant corrected the flag's JSON type. A test
initially assumed the existing package initializer did not import the default
solver module; the test was narrowed to the actual lazy-plotting/no-new-import
boundary rather than changing unrelated initialization. These failures were
rechecked by the final passing run.

## Actual scientific smoke output

An additional executed API check ran the homogeneous sphere
`homogeneous_model(1e6,4000,8000,4000)`, both methods at requested mesh 20,
degree 2 and frequency window [1e-8,0.002] Hz. The default used gravity=0 and
n_max=0; the pilot received no n_max. Both explicitly selected IDs were
`T0_2:solid:sphere`. Full report validation and curve derivation succeeded.

| Measure | Observed value |
| --- | --- |
| Reference frequency, Hz | 0.001592270474645895 |
| Candidate frequency, Hz | 0.0015922705742718625 |
| Signed frequency difference, Hz | 9.962596741498742e-11 |
| Signed reference-relative change | 6.256849511521793e-8 |
| Continuous reference norm | 0.9987083733268596 |
| Continuous candidate norm | 0.9987083733103839 |
| Signed overlap | -0.9999999999992402 |
| Alignment sign / indeterminate | -1 / false |
| Direct residual distance | 1.2327116895093247e-6 |
| Declared elements, reference/candidate | sphere:20 / sphere:20 |
| Stored samples, reference/candidate | sphere:41 / sphere:41 |
| Material-sided union curve samples | sphere:56 |

Model hash:
`705e9d064115d20d2e9b8b9ea24e3cf5ae80b06f936d482b50f15c721a79dea3`.
This execution's canonical report hash:
`ee1b96bf9674afad48d543404860713681e08b1ede33753b137700b2c95c4258`.
Runtime provenance means a fresh solve can have a different report hash.
These observed scalars are retained evidence; this smoke report was inspected
in memory, not retained as a separately downloadable artifact. The exact same
solve/request and row assertions are reproducible with:

```sh
env PYTHONPATH=/Users/veritaswang/.codex/worktrees/69a8/free-oscillation/packages OPENBLAS_NUM_THREADS=1 /Users/veritaswang/Desktop/code/random-ai-slop/free-oscillation/.venv/bin/python -m pytest -q tests/test_agreement.py::test_real_two_solver_pair_with_actual_counts
```

## Remaining acceptance and next action

Numerical API is ready for coordinator integration, then package-consumer
continuation at the supplied integrated revision. The author has not closed
independent scientific, artifact or release audits. Root owns the full named
12-solve / 44 cross-method / 44 refinement matrix; the 19 existing independent
reference cases were not regenerated. Installed CLI, actual native graphics,
transaction/sidecar behavior, copied recipe and isolated wheel/sdist remain
package/integration acceptance work. No universal accuracy status or solver
promotion follows from this self-check.

No children, background writers, environment installation, source publication,
primary CURRENT changes or website edits were performed. The initial clean
checkout was switched directly from the archived bootstrap to B. That switch
required the authorized sandbox escalation for linked Git metadata; it did not
merge or modify archival history. The scoped commit/status are reported in the
native handoff, after which this specialist becomes idle.
