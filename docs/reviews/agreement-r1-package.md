# Toroidal agreement: design round 1 package review

Ticket: DEV-R1-PKG/1. Read-only review of public baseline `03eacc3`; no feature
implementation, release change, or native-context completion is claimed.

## Keep the existing comparison; deliver a distinct installed analysis

The selected trial addresses a real gap. `earth_modes.analysis.compare_bundles`
returns explicit frequency pairs and untouched regional U/V/W curves;
`export_comparison` writes SVG/PNG/CSV plus metadata. It deliberately permits
different models and labels. Changing that API into a same-model T metric would
break a useful existing user journey. Keep it unchanged. Add a narrowly named
installed agreement API, not a wrapper around
`scripts/validate_owned_toroidal.py` or a website-only feature.

Recommended minimal public surface, with final naming frozen in round 2:

```python
from earth_modes.agreement import toroidal_agreement, load_agreement, export_agreement

report = toroidal_agreement(reference, candidate,
    pairs=[("T0_2:solid:sphere", "T0_2:solid:sphere")])
export_agreement(report, "agreement.json")
saved = load_agreement("agreement.json")
export_agreement(saved, "agreement.svg", width=1200, height=800)
export_agreement(saved, "agreement.png", width=1200, height=800)
export_agreement(saved, "agreement.csv")
```

The compute function performs no solving, plotting, writing, or mutation. The
exporter consumes an already computed report, so a collaborator can render or
tabulate a received result without rerunning either solver. Plot imports remain
lazy. One CLI command can expose the same two paths: explicit bundle inputs with
repeatable `--pair REFERENCE_ID CANDIDATE_ID`, or an exclusive `--report FILE`
input for re-export. Require pairs when computing; reject pair flags when
re-exporting. Do not infer pairs from nearest frequencies or reuse the broad
comparison's implicit identity shortcut. JSON, CSV, SVG, and PNG must work from
the installed CLI outside the repository. No new Scene/Project type is needed.

## Eligibility and interpretation must be visible before plotting

Require validated bundles, explicit nonempty unique pairs, elastic T modes of
the same degree, the same canonical model hash, and the same complete connected
solid support. Derive support from actual regional layer membership and bounds;
a provenance `solid_domain_id` string alone is not proof. Different radial grids
are expected. Different n labels may be explicitly paired, but remain visible
and carry no tracking claim. Damped/complex modes, missing regions, zero norms,
fluid gaps bridged by interpolation, and mismatched support must fail with a
pair-specific explanation before any output is published.

`data.model_hash` excludes provenance but includes model id, name, and all other
fields. Therefore document the first implementation as **same canonical model**,
not a general physical-equivalence detector. A renamed otherwise identical model
may be conservatively rejected. Do not add fuzzy model matching to this trial.

The numerical reviewer owns the final metric equations and interpolation rules.
Package requirements are independently clear: retain signed frequency difference
and its explicit reference denominator, original canonical W values, the two
comparison norms, one global candidate alignment sign, signed overlap before
alignment, and the normalized shape error. Keep the material-sided integration
partition separate from optional display samples. Never independently align or
normalize layers. At zero overlap, record that alignment is indeterminate and
use a documented deterministic display sign; do not suggest correlation.

Current `data.mass_integral` uses a layer-local trapezoidal discrete norm. If the
new metric integrates the piecewise-linear rho/W reconstruction exactly, its
normalization is a different, legitimate operation. Name it explicitly and
retain its conversion factors. Raw source arrays must not silently become the
aligned plotting arrays, and neither input bundle's hash or quality may change.

## A transferable report, not hashes without recoverable inputs

Prefer a versioned self-contained JSON report containing each complete source
bundle once, its verified existing JCS hash, selected IDs, source/model/mode
provenance and quality, method/algorithm identifier, computed rows, and regional
plotting data. Retain unknown source metadata. This is more useful than a report
that stores selected curves but references an unavailable full-bundle hash.
Do not label a reduced selected-mode bundle with the original full-bundle hash.

If source embedding proves too large, the only acceptable alternative is an
explicit immutable source pairing: save both actual bundle files with the
report, name their relative paths and hashes, and verify those files on load.
A machine-local path or hash by itself is insufficient. Choose one policy in
round 2; avoid offering two storage modes without a demonstrated need. Embedded
sources are the simpler initial choice for bounded analyses.

JSON is the authoritative artifact and needs no redundant `.json.json` sidecar.
CSV has one metric row per pair, scalar units, method identities, and source
hashes; it is not an unlabelled dump of aligned coordinates. CSV and figures can
use the existing `.json` sidecar convention, with the complete report and
resolved rendering settings. Native SVG must contain actual paths/text, not an
embedded raster screenshot. Figures need a W overlay and a signed residual,
material boundaries, reference/candidate identities, norms/sign, frequency and
shape measures, and a concise agreement-not-accuracy caption. The complete
provenance belongs in JSON, not microscopic captions. Keep English-only package
outputs and the existing restrained palette. Default one/few-pair figures should
be legible; reject undersized layouts instead of silently dropping annotations.

## Concrete installed journey and refinement evidence

Use `homogeneous_model(1e6, 4000, 8000, 4000)`, degree 2, and a 0.002 Hz maximum
for the fast quickstart. A read-only local probe of existing APIs on this
baseline produced the following, without automatic convergence checks:

| Method | Requested elements | Actual elements | Exported radial nodes | T0_2 frequency, mHz |
| --- | ---: | ---: | ---: | ---: |
| Default | 20 | 20 | 41 | 1.59227047465 |
| Owned pilot | 20 | 20 | 41 | 1.59227057427 |
| Default | 40 | 40 | 81 | 1.59227047929 |
| Owned pilot | 40 | 40 | 81 | 1.59227048539 |

These values establish that the proposed quickstart is executable and small;
they are not new independent reference or continuum-accuracy evidence. The
shipped copied recipe should call only installed public APIs, save the four
bundles and explicit cross-method pairs at each resolution, and separately
compare each method across resolutions. Its output labels must distinguish
method agreement, mesh change, and existing independent reference evidence.
Do not add a generic experiment scheduler or aggregate study format merely to
combine four calls.

Requested mesh size alone is insufficient: mandatory material knots can change
actual counts. Preserve both methods' full effective settings, regional output
node counts, and the selected domain's actual element counts when available.
An unavailable count is `null` with an explanation, never a guessed conversion
from the other solver. A documented layered case should ensure that refinement
actually changes the relevant domain discretization, not merely a global target.

## Bounds, publication, and necessary acceptance

Bound source bytes before CLI JSON loading, pair count before duplication or
plot construction, union partition size before allocating per-pair quadrature,
and figure pixel area before rendering. A reasonable round-2 starting policy is
16 explicit pairs, 200,000 total selected integration intervals, and 64 MiB per
input file; final limits should be checked against the real sphere/shell/PREM
examples. These are explicit rejection limits, not a peak-RSS guarantee. No
silent truncation, hidden downsampling of scientific integrals, or unsupported
"converged" promotion is acceptable.

Reuse `_write_json`'s completed-file/no-clobber behavior for JSON and
`export_common.transaction` for each figure/CSV plus sidecar. Validate every
pair and the final report before publishing anything. Document the existing
boundary honestly: rollback handles controlled failures, not power loss or an
arbitrary multi-command transaction. A multi-output recipe should stage its
whole result in a new directory and publish that directory only after success,
or clearly identify individually committed outputs; do not claim all-or-nothing
behavior for sequential ordinary exports. Existing outputs remain untouched on
validation failure, and deliberate overwrite remains explicit.

Necessary package acceptance is bounded:

- Global sign reversal leaves normalized agreement unchanged; layer-local sign
  reversal does not. Preserve original bundles byte-for-byte and quality states.
- Reject model/support/degree/Q/pair failures with no partial valid-looking
  result. Include duplicated-boundary and unsupported-domain counterexamples.
- Saved JSON reloads without the original source paths. CSV values and native
  figure labels match that report; inspect one standard and one minimum-size
  PNG/SVG. A tampered source hash must fail on load rather than quietly export.
- Exercise write failure after staging and an existing output, reusing the
  established transaction tests rather than duplicating a filesystem framework.
- Fresh wheel and sdist installations run a small custom-model API/CLI journey
  and copied recipe outside the checkout, with no source-tree imports. Re-run
  the affected existing comparison workflow to demonstrate compatibility.

Keep the proposed trial. Modify its storage and mesh-count requirements as
above. Add standalone report re-export and explicit layout/resource boundaries.
Remove any pressure to introduce website parity, automatic tracking, solver
promotion, a report dashboard, or a generic study engine. The next round should
freeze the exact report keys and metric/load/export contracts; implementation
before that would invite the same cross-module drift this trial aims to test.
