# Phase 3: explicit toroidal agreement

Status: design revision 1, not implementation approval. Accepted runtime baseline: public commit 03eacc3 (0.2.1). This bounded scientific iteration also exercises the operating protocol in docs/team/WORKFLOW.md. The experimental T solver remains experimental; no physical solver behavior changes.

## Outcome and boundaries

An installed Python or CLI user can compare explicitly selected elastic T modes from two complete bundles of the same canonical model, save a self-contained checked report, and later export native SVG, PNG or CSV without the original files. A copied recipe runs both methods at two actual resolutions and distinguishes cross-method agreement from within-method refinement and independent accuracy evidence. The existing general comparison API retains its broader, raw signed-curve semantics.

Keep: explicit mode IDs, canonical SI conventions, unchanged input data and quality, native scientific graphics. Add: material-sided continuous comparison normalization, whole-domain sign alignment, complete connected-support validation, actual mesh metadata and report re-export. Remove: automatic pairing/tracking, universal pass status, new solver physics, browser parity, a generic study engine and mandatory monotonic improvement. Website work is an independent delivery responsibility; no website feature is invented for this package trial.

## Scientific contract

Use the eligibility and exact metric in [science round 1](reviews/agreement-r1-science.md): complete bundle validation, equal computed canonical model hashes, equal positive degree, real elastic T modes with q=null, and exactly the same maximal connected solid component derived from model layers. Known linear-Q/effective-model conflicts fail. Unknown external provenance stays unknown. Differing explicit n labels remain visible and permitted.

On each material separately, partition at declared layer endpoints, all interior model density knots and both mode's interior radial knots. Reconstruct density and W linearly with existing endpoint clamping. Three-point Gauss quadrature integrates the degree-five mass-weighted product exactly for these stored reconstructions, up to arithmetic. Do not merge material sides or move source nodes. Continuous norms A and B are separate from the canonical discrete normalization. One sign aligns the entire candidate domain. Compute distance from the normalized residual directly to preserve tiny differences. Report signed overlap, absolute overlap, sign, near-zero alignment flag, both norms, normalized distance and signed frequency difference/reference-relative change. No input mutation or quality promotion.

Canonical-model equality is conservative, including non-provenance names and IDs. The two solvers approximate variable material operators differently; requested mesh targets are not equal actual resolutions. Neither agreement nor refinement alone is an accuracy certificate.

## Proposed API and data contract for round 2

A small `earth_modes.agreement` module owns pure computation and checked report loading; `earth_modes.agreement_export` owns I/O and figures. Public functions:

- `toroidal_agreement(reference, candidate, pairs)` returns a detached JSON-compatible report; no solver calls, file writes or plotting imports.
- `validate_agreement(report)` checks schema, embedded complete bundle hashes, eligibility and recomputed scientific/derived rows without re-solving, returning the same valid mapping. It rejects altered metrics, not just altered source hashes.
- `load_agreement(path)` uses strict bounded JSON parsing, then validation.
- `agreement_curves(report, pair_index)` returns separate material-sided arrays of radius, comparison-normalized reference/candidate W and signed residual. These are derived, not duplicated as another scientific authority in saved JSON.
- `export_agreement(report, path, *, pair_index=None, width=1200, height=800, overwrite=False)` is exposed from agreement via a lazy import and implemented in agreement_export. JSON saves the authoritative report alone. CSV exports all scalar pair rows. Figures show one pair: omit index only for a single-pair report; a multi-pair report requires an explicit index. No silent row omission or unreadable automatic 64-panel page.

CLI: `terra agreement --reference A.json --candidate B.json --pair A_ID B_ID [--pair ...] --out report.json`, or `terra agreement --report report.json --pair-index 0 --out pair.svg`. Compute and report-input modes are exclusive. Width/height affect figures only; reject inapplicable options rather than silently ignoring them.

Proposed report structure: `schema_version="1.0"`, `metric="toroidal-linear-mass-v1"`, `generator`, `generator_version`, `model_hash`, `sources={reference:{bundle_hash,bundle},candidate:{bundle_hash,bundle}}`, explicit `pairs`, computed `rows`, fixed `interpretation`. Sources embed full, unchanged bundles exactly once, including all original quality/provenance. Unknown metadata may be preserved as JSON extensions; required computed fields cannot be overwritten. Row fields use existing comparison frequency names and add `l`, both n/ID labels, `radial_label_mismatch`, ordered `layer_ids`, continuous norms, `signed_overlap`, `overlap`, `alignment_sign`, `alignment_indeterminate`, `shape_distance`, actual source per-layer mesh counts (null if unavailable) and exported sample counts. Full provenance remains in sources. Recomputed known floats compare with explicit arithmetic tolerance (proposal relative 1e-12, absolute 1e-14); structures, hashes, IDs and flags compare exactly. Loading verifies internal consistency, not authorship or provenance authenticity.

Resource proposal: at most 64 explicit unique pairs and 200,000 total integration intervals per analysis; at most 64 MiB per bundle file and 160 MiB per saved report. Check cheap pair/array budgets before deep copying or quadrature allocation; serialized size bounds are rejection limits, not peak-RSS guarantees. Figure dimensions 640..4096 by 480..4096; inspect actual normal and minimum outputs. Use existing transaction/no-clobber utilities, with full validation before publication. CSV and figures receive a sidecar containing the full report and resolved export settings/current rendering producer. Report JSON has no redundant `.json.json`. Individually committed exports are not a multi-output transaction.

## Evidence and workflow

Round 1 combined [science](reviews/agreement-r1-science.md) and [package](reviews/agreement-r1-package.md) findings. Twelve exploratory solves covered 44 explicit pairs on sphere, shell and both PREM solid domains, at two mesh requests per model. Degree-one differences can be nonmonotone; remove that proposed gate. Actual default/pilot per-domain element counts differ substantially and must stay visible.

Round 2 attacks report authority, eligibility, numeric/resource edge cases and the installed user journey. Round 3 freezes exact callable/data contracts, named case matrix, independent fixtures, ownership and acceptance after those corrections. Implementation starts only after that freeze. Postimplementation audits are distinct: independent scientific counterexamples; package/CLI/native artifacts; isolated wheel/sdist and source/release identity. Add rounds only for an unresolved concrete risk.

The implementation acceptance matrix includes the five adversarial fixture families in the science report; existing comparison compatibility; no-clobber/controlled rollback; self-contained reload and tampered metric/hash rejection; actual SVG/PNG/CSV inspection; and copied installed recipe. Named sphere/shell/PREM exploratory ceilings (absolute relative frequency <=1e-4, distance <=0.003) are provisional case regression bounds, not API pass thresholds. Independent reference checks retain their original meaning and are not relabeled as the new exact-interpolant measure.

Native specialist task creation remains unresolved (client handles only). It does not authorize duplicate creation or writes in unknown worktrees. Useful design proceeds with explicit transient assignments and primary CURRENT. The coordinator must resolve or explicitly transfer implementation attempts with accepted source and evidence; pending native setup cannot be claimed as successful durable-team adoption.

## Revision 2: resolved contracts for final freeze review

The following supersedes the revision-1 proposals above. Round-2 [contract](reviews/agreement-r2-contract.md) and [user/artifact](reviews/agreement-r2-use.md) findings are accepted. The implemented release will be 0.3.0; Bundle, Scene and Project versions remain unchanged.

### Exact public representation

Required top-level fields: `schema_version="1.0"`, `metric="toroidal-linear-mass-v1"`, `generator="earth_modes.agreement"`, nonempty historical `generator_version`, computed `model_hash`, `sources`, `pairs`, `rows`, and `interpretation="Same-canonical-model elastic T agreement; reference is a denominator, not physical truth. Agreement and mesh change do not certify continuum accuracy."`. Each source has `bundle_hash` and its full unchanged `bundle`. Pairs are nonempty unique two-string lists in explicit order, at most64. Optional JSON extensions survive; required fields retain their exact semantics. No report signing or authentication is implied.

Each row has these required fields:

| Fields | Type / meaning |
| --- | --- |
| `pair_index` | zero-based integer, equals report order |
| `reference_mode_id`, `candidate_mode_id` | selected source IDs |
| `l`, `reference_n`, `candidate_n` | integers copied from the selected modes |
| `radial_label_mismatch` | Boolean, the n values differ |
| `layer_ids` | ordered complete connected solid support, derived from the model |
| `reference_frequency_hz`, `candidate_frequency_hz` | exact source frequencies |
| `delta_frequency_hz`, `relative_frequency_change` | exactly `fb-fa` and `(fb-fa)/fa` |
| `reference_continuous_norm`, `candidate_continuous_norm` | positive continuous A, B, computed without changing canonical normalization |
| `signed_overlap`, `overlap` | signed c and abs(c), roundoff-only Cauchy clipping |
| `alignment_sign`, `alignment_indeterminate` | integer +/-1 and Boolean under the rule below |
| `shape_distance` | mass norm of reference-normalized minus aligned-candidate W |
| `reference_mesh_elements`, `candidate_mesh_elements` | per-support-layer integer counts or null per unavailable layer, never inferred from samples |
| `reference_radial_samples`, `candidate_radial_samples` | per-support-layer actual stored array lengths; material endpoints counted on both sides |

Known declared mesh counts must be positive integers; malformed supplied counts fail rather than being guessed. Unknown method strings/settings remain in complete source provenance and are shown as unknown when absent. No new source evidence is manufactured.

One private evaluator drives rows and curves. `validate_agreement` recomputes and checks, returning the original mapping unchanged. Curves and CSV/figure numeric annotations use recomputed values; authoritative JSON and sidecars preserve original report values and producer. Frequency fields, identities, counts and categories match exactly. Positive continuous norms use relative tolerance1e-12 with no absolute floor. Overlap and distance use `64*eps + 1e-12*abs(expected)`; reject nonfinite values first. This is arithmetic consistency checking, not bytewise cross-library portability. Sign/flag threshold mismatches produce a specific error.

With delta=64*float64 epsilon, alignment is +1 if abs(c)<=delta and otherwise sign(c). Preserve signed c and mark the near-zero case indeterminate. Direct residual distance may exceed sqrt(2) only within roundoff allowance. This deliberate deterministic sign exception avoids arbitrary whole-curve flips near orthogonality. Do not silently minimize it again during plotting.

`agreement_curves(report, pair_index)` returns a list in layer order, each containing `layer_id`, `r_m`, `reference_w`, `candidate_w`, `residual_w`; arrays are ordinary JSON-compatible lists on that layer's union partition. Candidate includes the one alignment sign. Residual is reference minus candidate. Source arrays remain unchanged; no display decimation. The exporter divides r_m by the common model radius for axis r/R.

`export_agreement(..., pair_index=None, width=None, height=None, overwrite=False)` resolves omitted figure dimensions to1200x800. Explicit dimensions or pair_index for JSON/CSV fail. Figures accept640..4096 width and480..4096 height, strict integer values excluding booleans. A multi-pair report requires a valid zero-based index; one-pair omission resolves to0. CSV and figures retain the entire report at the sidecar top level, adding/replacing only reserved `export_production` with renderer, renderer_version, annotation_language=en, format and resolved options. Sidecars therefore load directly through the same loader/CLI. Saved report computation identity is distinct from current rendering identity. JSON output remains one file.

CSV column order: `pair_index`, `reference_mode_id`, `candidate_mode_id`, `l`, `reference_n`, `candidate_n`, `radial_label_mismatch`, `reference_solver`, `candidate_solver`, `reference_frequency_hz`, `candidate_frequency_hz`, `delta_frequency_hz`, `relative_frequency_change`, `reference_continuous_norm`, `candidate_continuous_norm`, `signed_overlap`, `overlap`, `alignment_sign`, `alignment_indeterminate`, `shape_distance`, `reference_domain_elements`, `candidate_domain_elements`, `reference_domain_samples`, `candidate_domain_samples`, `model_hash`, `reference_bundle_hash`, `candidate_bundle_hash`. Nullable domain element totals require every selected layer count, otherwise blank. Regional maps and all full names remain in JSON; CSV has no Python dictionary representations.

CLI input routes are exactly the two in revision1; partial/mixed routes fail. Bundle inputs are Bundles, not implicit Projects. Figure index applies to either input route. `--pair` is forbidden with `--report`. Unsupported suffix/options/IDs fail before creating output. CLI help states zero-based selection.

### Bounded serialization and plots

Both API and embedded inputs obey the64MiB UTF-8 bound under the writer's actual JSON serialization (ensure_ascii=False, indent=2 plus final newline). Read files at most bound+1 bytes before strict duplicate-key/nonfinite parsing. Full reports and export sidecars must fit160MiB in that same emitted form. Cheap shape/pair/array-count preflight precedes cloning or quadrature allocation; bounded encoding includes unknown metadata and occurs before publication. These are fixed rejection limits, not peak-RSS promises. For each pair count sum(len(material_partition)-1), counting repeated mode use in distinct pairs each time, with total<=200000. Do not silently deduplicate or truncate. Existing strict reader may gain an optional byte bound without changing its default behavior.

Figures use two axes: normalized W overlay (color plus line style), then reference-minus-aligned-candidate residual, explicitly separately scaled. Units kg^(-1/2), common r/R, selected domain extent, separate material paths and boundary marks. Show compact pair/index/n/l and method identities, both frequencies, signed relative difference, shape distance, sign and applicable mismatch/indeterminate notices. Nonzero small measures use adaptive scientific notation. Exact-zero residual has finite limits and an explicit zero indication. Include agreement-not-accuracy caption and point to sidecar for complete IDs/norms/mesh/quality. Long user names may be visibly ellipsized in display only; do not shrink away important warnings. SVG is native vector geometry; selectable text is desirable but not a requirement.

### Executable examples and final acceptance

Copied `examples/recipes/agreement.py` uses only installed APIs/SciPy: sphere(1e6,4000,8000,4000), l=2, f in[1e-8,.002]Hz, mesh targets20/40 for both methods, four bundles and four reports (two cross-method; one refinement per method), CSV and figure, and an independently computed spherical-Bessel T0_2 frequency reference with0.5% named-case ceiling. It creates a new output directory, never deletes it, and describes individually committed files/partial failure honestly. Independent frequency results are separate from agreement and refinement. No repository reference file is needed. Documentation also shows a two-pair received-sidecar journey using a wider frequency window.

Full developer matrix: exactly12 solves,44 cross-method rows and44 within-method refinement rows (sphere/shell7identities, PREM4identities on2domains; degrees/targets/window exactly R1 science). Missing identities fail. Every named row has abs(relative_frequency_change)<=1e-4 and shape_distance<=.003. Retain complete output report hashes and actual per-domain counts. This is a regression gate for named cases, not API status. Reuse existing independent19-case evidence with its original scope; do not rerun it merely for the new report. The copied recipe independently evaluates its own Bessel frequency reference.

Three implementation audits: (1) independent rational/physical fixtures and real12-solve matrix, including density knots, layer-global sign, partial support,1e-9 shape residual, representable tiny frequency delta and boundary tolerance; (2) actual API/CLI and sidecar-only recovery, malformed/tampered inputs, no-clobber/staged failure, inspected real-PREM/label-mismatch/indeterminate figures at minimum/default size, parsedCSV/nativeSVG; (3) frozen source wheel/sdist installs outside checkout running copied recipe and affected existing comparison workflow, actual source/artifact identity and release CI. These audits may produce fixes with selective rechecks; the author does not close their own audit.

## Revision 3: accepted implementation freeze

The final [freeze review](reviews/agreement-r3-freeze.md) found the scope sufficient and requires no further design round. Its two corrections are normative: recognize only the existing reserved `request.linear_q` Boolean and `effective_model` model/reference/hash shapes exactly as enumerated in that review; reject conflicting/malformed known declarations, while absence remains unknown. Validate row types and physical ranges before applying arithmetic tolerance (no Boolean-as-number; positive norms; signed overlap[-1,1], absolute overlap[0,1], distance[0,sqrt(2)+64eps]). Report integer fields and public pair_index/dimensions follow the existing finite, safe, integer-valued JSON number convention, excluding booleans. A stale model_hash in an otherwise supported reference declaration must also fail against the computed common hash.

Implementation ownership is instantiated through actual native domain tasks, with exact base/attempt/path recorded in primary CURRENT. Numerical methods owns the evaluator/loader/bounded JSON reader and scientific tests/schema. Package/production receives its accepted commit before implementing CLI/export/recipe and user guide. Website/delivery owns the independent mechanical release-version preparation, using a lighter transient model with parent verification. Root owns integration, independent audits, distribution checks, maintained overview/contract/roadmap, workflow retrospective and publication. No transient reviewer is simultaneously the native numerical or export author.

The user supplied actual task IDs after list discovery omitted completed native tasks; direct reads verified all three clean read-only bootstraps. Preserve known IDs for direct reads/waits and do not use list omission as a liveness judgment. This real recovery replaces the earlier fallback proposal; no extra worktree or duplicate task is needed. Model tiers are now explicitly authorized and recorded in WORKFLOW.

## Candidate implementation acceptance

The frozen candidate4e1d79ad9eb7d80c7da9051c29de3a513e6d0fc0 implements this increment without expanding the numerical solver scope. Numerical and package native tasks returned scoped commits; the package task accepted the integrated numerical API before dependent implementation. The website/delivery domain prepared synchronized0.3.0 metadata with one lighter-model child and independent parent verification.

Three postimplementation reviews cover distinct risks:

1. [Scientific audit](reviews/agreement-audit-1-science.md): independent polynomial integration and rational counterexamples, one12-solve matrix with44 cross-method and44 refinement rows. Existing reference evidence and quality labels remain unchanged.
2. [Package and artifact audit](reviews/agreement-audit-2-package.md): actual PREM and receiving-sidecar journeys. Two typography defects were repaired and independently closed on0779d960 with six regenerated PNG/native-SVG cases; complete metadata and scientific captions were preserved.
3. [Distribution audit](reviews/agreement-audit-3-release.md): exact frozen runtime/source/guide/recipe bytes, separate wheel/sdist installations outside the checkout, copied four-solve recipe and actual output readback. Two preflight evidence gaps were corrected before execution.

Root integration passed182 Python tests,25 website tests, type/lint and seven resource comparisons. Both candidate installations passed their independent sphere reference, explicit source/direction/20-to-40 resolution checks, sidecar-only recovery, existing comparison and artifact decode. The scientific evaluator's seven audited source identities did not change during rendering repairs. No new schema migration, website metric, automatic mode tracking, PyPI publisher or default-backend promotion was introduced.

Final review/retrospective prose is an evidence-only source change. Hosted CI rebuilds and rechecks that final input; tagged package attachments and Pages remain separate publication checks, visible in the repository's Actions and release records. Candidate-local evidence is not presented as proof of a later public artifact. See the [workflow retrospective](team/RETROSPECTIVE.md) for observed team behavior and the limited protocol improvements.
