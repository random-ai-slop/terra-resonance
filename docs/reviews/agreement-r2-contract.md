# Toroidal agreement: round 2 contract review

Assignment DEV-R2-CONTRACT/1. Reviewed PHASE-3 revision 1, the two round-1
reports, and runtime `03eacc3`. This is a design review; no proposed API has been
implemented. The small arithmetic counterexamples below test the proposed
contract, not an existing implementation.

## Verdict

Keep the dedicated analysis, full embedded sources, computed curves, bounded
multi-pair metrics, and explicitly selected single-pair figures. These choices
are sufficient for the installed scientific journey and simpler than a second
study/scene format. Fix the concrete ambiguities below before round-3 freeze.
No additional solver, website, registry, or background tracking mechanism is
needed.

## 1. Numerical consistency needs quantity-specific rules

The proposed blanket absolute tolerance `1e-14` is inappropriate for frequency
rows. With `fa=1e-3` and `fb=fa+4e-15`, Python computes
`fb-fa=4.00005549516802e-15` Hz. The proposed `isclose` rule accepts a stored zero
instead. That contradicts retaining small representable differences.

**Change:** copy both source frequencies exactly and require exact agreement
for their derived `delta_frequency_hz = fb-fa` and
`relative_frequency_change = (fb-fa)/fa`, with that precise expression order.
The subtraction is not interchangeable with `fb/fa-1` at small differences.
Compare positive continuous norms with relative tolerance only. For overlap
and directly integrated distance, allow a stated machine floor plus a relative
tolerance; the coordinator's proposed `64*eps + 1e-12*abs(expected)` is a
reasonable explicit starting rule. Reject nonfinite data before comparisons.
IDs, counts, hashes, pairs, field names, and categorical values remain exact.

Near-zero alignment also needs an explicit exception. Proposed signed overlaps
`+3*eps` and `-3*eps` pass the float tolerance, and both are indeterminate, but
the original sign rule yields opposite exact `alignment_sign` values. A report
can therefore fail reload solely because the quadrature sum changes sign.

**Adopt the coordinator's minimal correction:** let `delta=64*eps`; use sign
`+1` when `abs(c)<=delta`, otherwise the sign of c. Preserve signed c and the
indeterminate flag. Integrate the residual for that chosen sign directly;
near zero, its distance may exceed sqrt(2) by roundoff allowance. Document that
this deterministic presentation choice differs slightly from strict minimum
distance inside the indeterminate interval. Do not silently take the minimum
again in the plot path.

At exactly the threshold, two floating-point implementations can still disagree
on the flag. Keep one threshold and exact flag validation rather than adding
another hysteresis/state protocol. If recomputation crosses it, report a
specific alignment-threshold consistency error. Do not promise cross-library
bitwise portability for that borderline case. Ordinary exact-zero and near-zero
fixtures must nevertheless load with the new stable sign convention.

## 2. Freeze which values drive the plot after validation

Revision 1 correctly removes stored duplicate plotting curves. It still leaves
two conforming interpretations: use tolerance-accepted stored row norms/signs
to derive curves, or use recomputed row values. They can produce different
plots. `validate_agreement` returning the same mapping does not resolve this.

**Change:** one private deterministic evaluator computes rows and material-sided
curves from embedded sources and explicit pairs. Validation checks stored rows
against that result without modifying the report. `agreement_curves` uses the
evaluator's recomputed norms/sign, never tolerance-accepted stored normalization
values. Numerical CSV/figure labels should use the same recomputed values.
Preserve the validated original report in JSON/sidecars; exporting must not
rewrite its original generator version or source quality. Current rendering
producer/version and resolved figure settings belong in separate export
metadata. Do not expose an unsafe public "already validated" bypass merely to
avoid repeating work; reuse the evaluated result within one export operation.

Freeze curve output as ordered per-material records with `layer_id`, `r_m`,
reference-normalized W, aligned candidate W, and a precisely oriented residual
(recommend reference minus aligned candidate). Sample on the existing union
partition knots, including each material's own endpoints. No hidden plot
decimation and no new interpolation rule. Raw curves remain the original
embedded region arrays and are never overwritten.

## 3. Full sources solve provenance, provided validation covers their whole tree

Keep complete reference/candidate bundles embedded once. Compute both full
bundle hashes, rather than accepting either provenance's asserted hash. The
model hash is independently computed from each embedded model. Validate all
embedded modes, even unselected ones, and preserve their unknown metadata.
Reject a report whose source, pair order, derived support, counts, or numeric
rows no longer agree. A hash is identity, not authentication.

**Clarify:** `metric`, schema, generator identifier, interpretation, required row
keys and scalar/structured types need one exact table in round 3. Unknown JSON
extensions must not replace any required computed field. A known metric with
an unknown schema, or vice versa, is an explicit unsupported-format error, not
best-effort loading. Old generator versions may be retained when the metric
and schema are still supported.

The sidecar shape must also be fixed. Minimal choice: export sidecars are the
same report object plus one reserved `export_production` extension holding current renderer
metadata. Then `load_agreement("figure.png.json")` works directly and remains
self-contained. A wrapped `{report, export}` envelope would require a second
accepted loader shape; either is feasible, but do not leave two authors to make
different choices. JSON alone still needs no `.json.json` companion.

## 4. Resource limits must mean the same thing in API, files, and sidecars

Keep 64 unique ordered pairs, 200,000 total integration intervals, 64 MiB per
bundle file, and 160 MiB per report as bounded rejection limits. They do not
promise a 160 MiB peak process footprint: JSON objects, validation, embedded
copies and quadrature buffers can coexist.

**Add exact counting semantics:** each pair contributes the sum of
`len(layer_partition)-1` across its support; reuse of a mode in several distinct
pairs counts its intervals each time. Duplicate pair tuples fail rather than
being silently deduplicated. Each input and embedded source must satisfy the
same documented byte rule, not only the command-line source filenames. Unknown
metadata counts toward bytes. Report and sidecar size limits apply to the
actual UTF-8 serialization selected by the writer, not a character count or an
estimated compact representation that becomes oversized when indented.

For files, read at most the limit plus one byte before strict parsing; a prior
`stat` check alone races growth. Reuse duplicate-key/nonfinite-number rejection
from `data._read_json`, but its current unbounded `json.load` is not itself the
required bounded loader. For API inputs, cheap structure/pair/array-count checks
precede cloning; a bounded JSON serialization pass can enforce the byte limit.
Check sidecar overhead before publication too. No integration allocation or
filesystem publication should occur after a budget has already failed.

Avoid adding an adjustable resource-policy framework. Fixed documented limits
and precise failures suffice; revisit them only for a measured excluded workload.

## 5. CLI/API option applicability has one concrete default conflict

The proposed signature `width=1200, height=800` cannot tell whether a CSV caller
explicitly supplied those values or omitted them. Therefore "reject inapplicable
options" is not fully implementable with that signature.

**Change:** use `width=None, height=None` at the API/CLI boundary. Resolve omitted
figure dimensions to 1200x800; reject explicit dimensions for JSON/CSV. Likewise
reject `pair_index` for JSON/CSV, use implicit index zero only for a single-pair
figure, and require an explicit valid integer index otherwise. The index is
zero-based and applies to figures computed from bundles as well as re-exported
from a report. It never changes the pairs retained in the report or sidecar.

Freeze the exclusivity table:

| Input route | Required | Forbidden |
| --- | --- | --- |
| Compute | both bundle paths, one or more explicit `--pair` values | `--report` |
| Re-export | `--report` | either bundle path, `--pair` |

Partial bundle routes, unsupported suffixes, mixed routes, and inapplicable
figure options must fail before writing. Source inputs are Bundle files, not
implicitly extracted Projects, unless round 3 explicitly adds that feature.
There is no demonstrated need to add it now.

CSV needs an exact column list, including zero-based `pair_index`, because rows also contain structured `layer_ids`
and per-layer mesh dictionaries. Keep scalar metrics/identities and nullable
selected-domain totals in CSV; keep full regional maps in its JSON sidecar.
Do not emit Python dictionary repr as an undocumented CSV cell format. Preserve
null/unavailable mesh counts rather than guessing them from radial nodes.

## Feasibility and focused acceptance

Existing `_write_json` and `export_common.transaction` cover the publication
mechanics. Validate and enforce budgets before invoking them; use one transaction
per CSV/figure plus its sidecar, and no claim of cross-command atomicity.
One comparison evaluator, one loader, and one lazy rendering module are enough.

Round 3 should require only the meaningful new counterexamples above in addition
to existing scientific fixtures: tiny representable frequency delta, stable
near-zero sign, deliberate row/hash tampering, report-only re-export, exact
interval/byte boundary rejection, multi-pair index selection, and explicit
inapplicable options. Reuse established no-clobber/rollback evidence with one
agreement-specific staged failure. Keep current comparison compatibility and
the installed wheel/sdist journey. Do not add a schema migration engine, report
signing, native SVG project format, or configurable tolerance dashboard.
