# Phase 2 planning, round 2 — package-to-website workflows

Status: planning only. Reviewed the round-2 revision of `PHASE-2.md` against the existing loaders, CLI parser, website lifecycle, lesson generator and SceneSpec schema. The revised scope is sufficient without new feature areas. Freeze is blocked by the small contract details below, not by a need to redesign the application.

## Adversarial end-to-end walk

| Step | Required result | Review outcome |
| --- | --- | --- |
| Install a wheel outside the repository; list and load a lesson | One canonical PREM bundle, English teaching metadata, a fresh self-contained project, no network or repository paths | Feasible. Freeze `list_examples()` return shape and example ownership; a mutable cached return would contaminate later examples. |
| Export a scientific image and probe | Explicit image flags override saved image settings; inherited movie fields do not cause failure; manifest matches actual dimensions, sampling and normalization | Revised precedence is sufficient. Include an example with inherited GIF settings and explicit SVG dimensions, plus CSV rejection of explicit image-only flags. |
| Construct and solve a custom material model | A new validated bundle and scene; no accidental reuse of PREM hash or teaching identity | Existing model/solve/scene path is sufficient. The guide must edit a Model input and recompute, not demonstrate changing materials inside a solved project. |
| Import it into the website; switch Chinese/English during playback | Camera, physical time, independent probe, comparison, export options and unknown metadata survive; custom projects do not acquire built-in lesson claims | Feasible, with exact lesson recognition and stored-message rules below. |
| Save a project and download PNG/SVG/GLB | Canonical scientific state and original user metadata survive; maintained artifact labels are English regardless of UI language | Requires the planned English SVG renderer boundary. Do not copy the visible Chinese chart, translate researcher names, or temporarily switch the workbench. |
| Import a phase-1 wireframe/cutaway project | Legacy surface triangle-wire interpretation is retained; corrected filled sections are disclosed | The current phrase “1.0 unchanged” overstates compatibility. Amend it before implementation. |

## Necessary revisions before round 3

### W1 — make lesson recognition precise

“Known identity and canonical teaching content match” is not yet a testable predicate. Matching only an ID or title can apply an authoritative built-in translation to a custom-model project that happens to reuse that ID.

Use the existing canonical JSON machinery: recognize a built-in lesson only when the project bundle hash equals the catalog bundle hash, the lesson ID exists, and the entire original `teaching` object equals the catalog's canonical teaching object. Unknown extra teaching keys or modified text make it unrecognized; preserve and display that metadata verbatim. A digest of canonical teaching JSON is an implementation convenience, not a new field required in user projects. Scene/probe edits need not invalidate translated instructions: editing the scientific scene is part of following a lesson. Never write the localized strings back into `teaching`.

Legacy projects containing the old Chinese built-in prose will not match the new canonical English catalog. Keep them verbatim as imported data. The language requirement governs maintained phase-2 assets; it does not authorize silent rewriting of historical user projects. State this explicitly so the English migration test does not reject legitimate imports.

### W2 — locale lifecycle includes existing messages and in-flight work

The plan correctly excludes locale from geometry and scientific state. Add the following execution rule: state stores a diagnostic/message identity and parameters, not the already translated sentence. Otherwise an error already on screen remains Chinese after switching to English, even if all newly generated errors translate correctly. This affects `Workbench.error`, viewport sampling/status callbacks and long-running export errors in particular.

A language switch during an in-flight import or export must change how eventual status is presented, without restarting the operation or changing its English artifact labels. Store the diagnostic at completion and translate on render using the current locale. Canonical English details remain available. Optional WebMCP schemas, machine responses and technical diagnostics can stay English; they are an integration interface, not another localized scientific state.

Use `history.replaceState` for the selector so language changes do not flood history or cause navigation; preserve unrelated query parameters and the fragment. Handle browser back/forward when it changes a recognized language parameter. Local-storage read/write failure must not prevent a session-local switch. Resolve document language before showing localized content; a short neutral loading shell is sufficient. None of these need a router rewrite or server runtime.

### W3 — define legacy semantics honestly and identify the release

SceneSpec 1.0 preserves its surface triangle wires, but fixing previously unfilled Python/GLB sections intentionally changes that old project's appearance. Replace “accept 1.0 unchanged” with “preserve input data and legacy curved-surface wire topology; apply the documented cutaway rendering correction.” The sidecar must identify the new renderer/package version and the correction, so a user can distinguish scientific-state compatibility from pixel-identical replay.

Freeze a compatibility matrix:

- Scene 1.0 with no new field: load/save remains 1.0; never default in a non-null spacing.
- Scene 1.0 with `wireframe_spacing_deg: null`: explicitly decide whether this benign extra field is retained; the draft permits it and both validators should agree.
- Scene 1.0 with non-null spacing: reject rather than ignore.
- Scene 1.1: require null or one of 5/10/15/30; do not confuse a missing field with null.
- Choosing spacing in the UI explicitly upgrades the scene to 1.1, including while solid surface rendering temporarily hides the grid. Merely importing, saving or changing language does not upgrade it.

Bundle and Project remain 1.0 as proposed. Split any shared version constants that would otherwise upgrade them accidentally. Publish phase 2 under a new package release identifier rather than reuse 0.1.0 for a changed schema/rendering implementation. A version bump is essential provenance, not a new feature.

### W4 — finalize package example shape and canonical resource direction

Specify `list_examples() -> list[str]`, returning the six stable IDs in teaching order, and `load_example(id="03-indices") -> dict` returning a newly assembled, validated Project. A second call must be unaffected by mutations to the first result. Unknown IDs produce a canonical English error with the available IDs. `terra example --list` needs no output path; writing a selected/default example does.

Name the single maintained bundle/catalog source and the generated copies in round 3. Either preserve the current validated `examples` sources with synchronized package/web copies, or move the canonical source once and update every generator. Do not have the wheel builder, lesson generator and web synchronizer each infer a different “latest” resource. Installed examples need bundle/catalog JSON, not six duplicate bundles or preview PNGs. Resources and hashes must be verified from an installed wheel, with no source checkout on `sys.path`.

The source example should demonstrate the same API/CLI described above. A package-installed tutorial is needed, but a new tutorial command framework is not.

### W5 — assign files rather than overlapping responsibilities

The proposed ownership gives root “schema/TypeScript parity” and the package reviewer “Python mesh/export/schema contracts”; both could edit the canonical JSON Schema. The CLI is also shared between scientific-image options and `terra example`.

Assign one writer for each: the package reviewer owns canonical JSON Schema and `cli.py`; root owns TypeScript schema consumers, frontend and integration checks. The product reviewer owns an examples/resource module and its public API proposal, with a ready-to-integrate notice for the CLI branch rather than concurrent CLI edits. Root or one named integrator owns the final public `__init__` exports. Adjust names if desired, but freeze a unique file owner before implementation.

For English documentation, create an explicit per-file allocation. Root owns the current phase plan; product owns README/USER-GUIDE/DEVELOPMENT, lesson generator/resources and assigned product reviews; numerical owns its decision/validation documents and assigned historical numerical reviews; package owns the data/contract text tied to its changes. Bulk translation and scientific code work must not race in the same document.

## English migration: bounded but complete

The round-1 scan identified 36 maintained documentation files with CJK text, nine example files, one generator and the root README. This is substantial editing, but it does not require new numerical solves. Translate the generator first, regenerate maintained teaching/project copies, and verify that only teaching text and explicitly planned scene-version/display fields changed. Bundle arrays, quality evidence, units and canonical bundle hash must remain intact unless a separately reviewed numerical correction occurs.

Preserve historical chronology and adverse findings when translating reviews. An old report's “not yet tested” is historically correct; translate it and link to later closure instead of rewriting it as a pass. Update current entry points rather than duplicating the full history in each guide. Do not translate upstream licenses or arbitrary Unicode user content. Authentic screenshots of the Chinese website remain evidence; their maintained captions should be English.

Use a narrow maintained-text scan with explicit path/category exceptions for website localization, authentic website evidence and Unicode preservation fixtures. Avoid a repository-wide ban on non-ASCII: scientific symbols, source attribution and user data are legitimate. No website string should be duplicated in Python solely to satisfy a scan.

## Minimum evidence and conclusion

One combined workflow can cover the package example, custom solve, scientific image/probe options, website switch, English artifact and project round trip. Add focused counterexamples for edited lesson metadata, a visible diagnostic switched between locales, legacy/new scene versions, and a sparse grid at high degree. Pair key completeness checks with actual English/Chinese narrow/wide browser use; a key-count test alone cannot detect clipped labels or untranslated existing errors.

Retain the phase-2 feature set. Remove no scientifically necessary item, add no framework or extra locale/output selector, and do not broaden the pilot during this product review. With W1–W5 incorporated, the plan is suitable for the final adversarial round. It is not yet frozen for implementation.
