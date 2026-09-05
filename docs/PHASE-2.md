# Phase 2 — package usability, language, and an owned numerical core

Status: **implemented for 0.2.0 after three sequential planning rounds, 2026-09-04**. The proposal and successive revisions below preserve the decision history. Source validation and independent first/second implementation reviews are complete; the final distribution-installation gate is recorded separately in [the release review](reviews/phase-2-implementation-r3-release.md). The original 0.1.0 scientific baseline remains unchanged.

## Outcome

An installed Python package must support useful scientific and production work without the repository or website. The web workbench must present one coherent language at a time. Surface wire density must be an explicit, reproducible display choice. A future in-house numerical implementation must have an evidence-based migration route rather than a language rewrite justified by preference.

## Round 1 proposal

| Area | Keep | Change or remove | Add and acceptance |
| --- | --- | --- | --- |
| Language | Stable scientific symbols, units, IDs and user-provided text | Replace Chinese maintained documentation and shipped teaching copy with English; remove duplicated bilingual headings and competing lesson narratives | A typed English/Chinese website message catalog, persistent local preference, accessible language selector; translation does not modify scientific state or bundle hashes |
| Package | Python API, CLI and deterministic exporters | Replace repository-dependent first-use examples; distinguish optional external media encoders from Python requirements | A compact installed example entry point and runnable package-first guide, verified from an independent wheel installation outside the repository |
| Surface grid | Scientific samples, interface knots and quality safeguards | Decouple visible wire density from numerical mesh and field sampling; avoid a low-density setting erasing high-order structure | One bounded scene setting implemented consistently in Python, website, saved projects and relevant media/GLB outputs, with backward-compatible semantics |
| Numerical ownership | Validated Ouroboros adapter and independent MINEOS/analytic evidence | Reject an immediate whole-solver rewrite or speculative multi-language framework | A written language/architecture decision, staged migration gates and a small independently validated numerical slice only if it provides concrete evidence without replacing the default backend |
| Information architecture | Accurate historical evidence and scientific limits | Correct stale plan status; translate rather than discard adverse review findings | Concise current user/developer entry points, linked archival reviews, accurate next-stage roadmap |

Website locale is a presentation preference, not a physics parameter. Exported machine data remains stable and package-generated annotations are English. Imported researcher-authored metadata must remain verbatim; the language policy applies to maintained product copy, not censorship of user data. Built-in lesson translations should be keyed by stable lesson IDs and must never overwrite an imported project's teaching metadata.

## Three sequential planning rounds

1. Audit current implementation and proposed requirements independently from scientific, package and product perspectives. Consolidate concrete evidence and remove speculative additions.
2. Review the consolidated proposal across ownership boundaries. Resolve schema/default/export, locale/lifecycle, installation and numerical evidence contradictions. Record changes before starting round 3.
3. Adversarially check whether the revised scope is sufficient, feasible and testable; freeze exact interfaces, implementation ownership, release evidence and long-term gates. Begin implementation immediately after blockers are resolved.

Each round produces its own reports under `docs/reviews/phase-2-plan-r*-*.md`. Running three reviews of an unchanged draft does not count as three iterations. Implementation checks are recorded separately and selected by changed behavior, not coverage targets.

## Round 2 revision: concrete contracts

All three round-1 reports were read before this revision. Their concrete additions are scientific-image CLI parity, a package example, explicit scene versioning, the existing cutaway mismatch, English artifact captions, and an executable numerical pilot. A broad rewrite, desktop wrapper, multilingual Python, resource-flag proliferation and plugin registry are removed from this phase.

### Surface grids and compatibility

New scenes use SceneSpec **1.1** with `wireframe_spacing_deg: 15`. Allowed values are 5, 10, 15, 30, or null. Null preserves legacy triangle wires on the curved surface. Non-null values specify a material latitude/longitude display grid, not the solver's mesh. Curve segments are sampled finely enough for the active degree and quality; they use the same field, absolute time and gain. Density only changes visible shell lines. Section faces remain filled in all renderers and retain all source knots and material boundaries; this intentionally fixes an existing cross-export bug.

Readers accept SceneSpec 1.0 unchanged; it has legacy surface wires. Selecting a new spacing explicitly upgrades only the scene to 1.1. Version 1.1 requires the spacing field, and version 1.0 rejects a non-null new spacing. Bundle and Project remain 1.0. Old readers reject 1.1 rather than silently ignoring its appearance. Schemas, validators, defaults, cache keys, budgets, project saving, CLI scene creation and both GLB renderers must agree. Reports preserve requested spacing and actual sampled line counts; density does not modify scientific hashes, probes or node extraction.

### Language and website lifecycle

English is the fresh-visit default. One typed message catalog and React provider supply English/Chinese labels, descriptions, accessibility, status, quality and owned diagnostics. Explicit `?lang=en|zh-CN` overrides a versioned local preference; an invalid value falls back to the saved choice or English. The language selector updates the preference and URL parameter without navigation. Language never enters Scene/Probe/Export or the geometry cache, and never remounts the viewport, reloads data or resets live time.

Website-owned errors use stable diagnostic identities with parameters and canonical English details, translated at the presentation boundary. Unknown external exceptions retain diagnostic details under a localized explanation. No substring translation of arbitrary researcher data. Scientific identifiers, units and field paths are canonical.

Remove `presetInfo`. Use the canonical lesson catalog for lesson selection and guidance. Translate only catalog entries whose known built-in identity and canonical teaching content match; edited/imported metadata remains verbatim and is preserved on save. Chinese lesson prose lives only in website-owned resources. All maintained downloaded annotations, including SVG from a Chinese chart, are English. The export and visible chart reuse one numeric plot description; exporting cannot temporarily change the UI locale. Artifact metadata states `annotation_language: en` for maintained labels.

Use a single localized heading per section and an accessible text language selector. Allow action/label wrapping and move advanced field-sampling explanation out of the primary controls. Preserve the established palette, scientific semantics and viewport emphasis.

### Installed package and output options

Add `list_examples()` and `load_example(id="03-indices")` returning a fresh, validated self-contained project. `terra example --list` lists IDs; `terra example [id] --out project.json` writes the same project with existing overwrite protection. Ship one canonical PREM bundle and one English lesson catalog, not six duplicated bundles. Generate package and web copies from the existing validated sources; install-time access uses package resources and requires neither repository nor network.

Scientific-image CLI options follow explicit flags > saved project image options > documented operation defaults. Apply only width, height, transparency and annotation; inherited movie settings must not poison scientific images. Explicit movie options on scientific commands still fail. CSV/table outputs reject explicit image-only options and ignore irrelevant inherited production settings. Apply the same image controls to `terra probe`. Export resource limits remain an explicit Python API capability; correct the unsupported CLI claim instead of adding many flags.

### Numerical pilot and long-term route

Add experimental `earth_modes.experimental.solve_toroidal` with explicit model, degree bounds, mesh target, frequency bounds and memory budget. Return the existing validated ModeBundle with experimental method provenance. It uses its own SI quadratic finite-element energy assembly, preserves profile knots and solid-domain boundaries, and uses SciPy dense symmetric generalized eigensolving. It does not call vendor assembly/mesh helpers. Keep it separate from the default `solve` dispatch; a package-installed Python example is sufficient. No new backend registry or mandatory runtime.

Acceptance separates homogeneous Bessel-root/shape checks, hollow-shell independent traction-ODE checks, layered/adjacent-solid domain checks, center/rigid l=1 behavior, mass normalization, symmetry, SPD mass, scaled residuals and source support. Tentative gates for review: low-order frequency error <=0.5%; sign-aligned mass-weighted shape error <=1%; discrete scaled residual <=1e-9 and mass orthogonality defect <=1e-8. Benchmark evidence does not certify arbitrary models or promote the pilot to the default solver. Record a concrete Python-first numerical ownership decision and staged T→R→S migration with physical and performance gates before native-language acceleration.

### Documentation and execution ownership

Translate all retained first-party non-website documentation, historical research/reviews and maintained generator/example text to English, preserving adverse findings, dates, evidence values and pending-at-the-time status. Consolidate current usage around README, USER-GUIDE, CONTRACT, DEVELOPMENT and ROADMAP; link historical reviews instead of copying their narrative into every guide. Do not delete valid evidence to avoid translation. Preserve original third-party sources and arbitrary Unicode user data.

Root owns site code, localization integration, schema/TypeScript parity, release integration and current phase plan. The package reviewer owns Python mesh/export/schema contracts and focused regression. The numerical researcher owns the experimental numerical module, independent validation, decision record and assigned English historical documents. The product reviewer owns English user/developer documentation, lesson generation/resources and installed-example API/CLI; CLI file editing is sequenced with the package reviewer. Exact file ownership and ready-to-integrate notices are frozen in round 3.

## Questions for round 2 adversarial review

- Are explicit scene versioning and filled cut faces sufficient to avoid silently changing old projects?
- Can curve sampling and morph budgets honor sparse wires even at high degree without losing scientific nodes?
- Do installed examples, scientific-image precedence and English exports close the actual user paths?
- Are the pilot evidence gates and workload feasible without quietly broadening the solver scope?
- Is the locale boundary complete without duplicating numerical data, user metadata or chart calculations?

## Round 3 revision and proposed freeze

All round-2 reports, including the root integration challenge, were read before this revision. Release identifier: **0.2.0**. The following decisions resolve their blockers and take precedence over the earlier draft wording.

### Exact grid recipe and legacy behavior

- Let `n = max(quality_base, 4*(l_max+1))`, where quality_base is 32/48/96. This remains the scientific angular sampling floor.
- For spacing `d`, parallels occur at colatitude `j*d`, `j=1..180/d-1`; each parallel uses `2*n` segments around longitude, including a closing endpoint. Meridians occur at longitude `k*d`, `k=0..360/d-1`; each uses `n` segments from north to south. Do not duplicate the 360-degree meridian or draw degenerate polar parallels. Shared pole endpoints are permitted and counted.
- Material line points lie on the selected radius with the existing outer-material-side convention. The removed quadrant is the existing x>0, y<0 region; discard segments whose midpoint lies strictly inside it. Sampling aligns with its boundaries; keep boundary curves and do not reconnect across the removed region.
- Preflight all curve endpoints before allocating modal caches, including hidden scientific triangulation retained for node extraction/picking. Export morph budgets include every exported animated line/triangle vertex and all mesh-weight tracks. Curves are essential geometry, never an optional GLB omission.
- Sparse wires do not guarantee that every extremum between curves is visible. For `d*l_max >= 90`, show a localized sparse-grid notice recommending filled surface or smaller spacing. Preserve the chosen spacing without silent extra lines. Scientific field/probe/node data and the ModeBundle hash remain unchanged; the saved scene/project intentionally changes. Color clipping diagnostics continue to sample the scientific surface, not only sparse wires.
- Scene 1.0 accepts absent/null spacing and preserves that exact input on load/save. Non-null spacing fails. Scene 1.1 requires the field and allows null/5/10/15/30. Only new scene construction or an explicit grid-setting action upgrades to 1.1. Bundle and Project versions remain 1.0.
- Legacy curved-shell triangle wires are retained. Filled cut faces are a documented cross-export correction, including for 1.0 scenes, not a promise of pixel-identical replay. New six-case assets use 1.1 and 15 degrees. Record the renderer version and filled-section policy in export metadata.

### Precise language and package behavior

- Recognize built-in teaching only if the bundle hash matches the catalog, the ID exists, and the complete canonical teaching object matches the catalog object. Additional/changed teaching keys invalidate recognition. Scene/probe changes do not. Old imported Chinese teaching remains verbatim user data; it is not silently migrated.
- Store diagnostic identities and parameters through renderer callbacks, React state and asynchronous work. Render using the current locale. Optional WebMCP machine schemas/responses may remain English. Preserve URL parameters/fragments on language changes; handle popstate, blocked local storage and in-flight operations without resetting science or restarting work.
- `list_examples() -> list[str]` returns stable six-case IDs in catalog order. `load_example(id="03-indices") -> dict` returns a fresh validated complete Project; mutations cannot affect subsequent loads. Unknown IDs give an English error listing available IDs.
- Maintained sources remain `examples/prem-modes.json` and generated `examples/lessons/catalog.json`, produced from the English lesson generator. Package copies live under `earth_modes/assets/examples/`; website copies remain generated assets. One synchronization command validates hashes and checks all destinations. Preview PNGs and six duplicated bundles are not installed as package examples.
- If a project has ExportSpec, resolve its defaults first, then select image keys; if absent, use scientific operation defaults (currently 800x500). Thus `{export:{format:"gif"}}` implies 1200x900 scientific image defaults, matching a browser round trip, while explicit `--width 640 --height 480` wins. CSV/tables ignore inherited image settings and reject explicit image-only flags. Scientific plot/probe media record actual dimensions and `annotation_language: en`.

### Exact experimental scope and evidence

API: `solve_toroidal(model, *, l_min=1, l_max=4, mesh_size=80, frequency_min_hz=0.0, frequency_max_hz=0.01, memory_mib=512)`. Degree range is 1..64 for this pilot. Actual mandatory profile knots take priority over the mesh target and are budgeted before dense allocation. Adjacent solid layers share a domain; fluids separate domains. Each domain's l=1 rigid rotation reserves n=0 but is excluded from positive oscillatory output; first positive l=1 is n=1, and l>=2 starts at n=0. Frequency filtering never renumbers branches. All-fluid/empty ranges return a truthful empty bundle with explicit not-applicable/empty-selection provenance. Invalid requests raise.

Keep the original model, layer sides and single canonical mass factor. U/V=0, no fluid W regions, no potential placeholders and q=null. Model Q may be preserved as input but is not applied. The pilot imports no vendor assembly or mesh helper and has no silent fallback.

Independent evidence matrix: homogeneous sphere l=2/3, n=0..3; traction-free hollow shell l=2, first three positive branches; selected low-order modes of both PREM solid domains, l=1..4; separate l=1 rigid rotations and an artificial same-material layer split. Compare positive frequencies <=0.5% and sign-aligned physical mass-weighted shape error <=1% for the named sphere/shell cases. Evaluate on a common resolved grid with material sides. Cases may use a documented refinement sufficient for the stated gate; do not remove failed IDs silently.

FE residual is `||Kx-lambda Mx||2 / ((||K||F+abs(lambda)||M||F)*||x||2) <=1e-9`, evaluated on constrained FE eigenvectors. Orthogonality is `max(abs(X.T M X-I)) <=1e-8` within a degree/domain FE group. Record symmetry and SPD checks. These discrete diagnostics do not claim independent physical accuracy. Canonical exported trapezoid normalization/interpolated fields follow the existing separate contract; no 1e-8 orthogonality claim is imposed on exported samples. The default solver and its scientific dataset remain unchanged.

### Unique implementation ownership

- **Root:** all Site checkout edits; i18n, TypeScript scene/geometry/export parity, UI/layout, frontend tests, source synchronization integration, version integration, final package build and release checks; `docs/PHASE-2.md` and phase acceptance/log.
- **scope_review:** Python `data.py`, `export*.py`, `cli.py`; canonical and packaged JSON schemas; associated existing Python tests plus new grid/option tests; `docs/CONTRACT.md`; English files assigned in `phase-2-ownership.json`. Sole CLI writer implements the example command against the agreed API after readiness notice. Do not edit Site checkout.
- **numerical_research:** `packages/earth_modes/experimental/`, its focused tests, `scripts/validate_owned_toroidal.py`, `examples/own_toroidal.py`, numerical decision/validation documents and assigned English files. Do not edit default solver or Site checkout.
- **visual_research:** new `packages/earth_modes/examples.py`, public exports in `__init__.py` (including version 0.2.0), English `scripts/generate_lessons.py`, `scripts/sync_web_assets.py` extended to package destinations, generated canonical lessons/resources, example API tests; README, user/developer/acceptance guides and English documents assigned in `phase-2-ownership.json`. Do not edit CLI/schema/Site files; notify root before synchronizing into Site destinations so root can own that operation.

The ownership JSON lists every existing Chinese documentation file once. `CONTRACT.md` is assigned explicitly even though already English. Existing text-only fixture cases may preserve Unicode data; no ASCII-only restriction is introduced. New docs and reports are English.

### Final review and execution gates

Round 3 must challenge these resolved interfaces and sufficiency, using counterexamples instead of proposing an unbounded next feature list. Correct any remaining blockers in this document, then start implementation immediately without another permission gate. Implement independently owned areas in parallel, integrate dependencies sequentially, and independently cross-review the finished changes. Run the affected physical, schema, output and lifecycle checks plus one clean release workflow; do not repeat unrelated expensive baselines for translated prose.

## Freeze clarifications and execution start

The three final reviews (`phase-2-plan-r3-contract`, `-science`, `-workflows`) found no remaining substantive blocker. Their final clarifications are adopted:

- Grid allocation, rendering and sparse-grid notices are active only for `surface=wireframe`. The setting persists while filled rendering is selected. Clip once in undeformed material coordinates. Use indexed vertices shared within each curve (a closing parallel endpoint is explicit); retain/count the full curve vertex set even when clipping removes some edges. The unclipped point count is `(180/d-1)*(2*n+1)+(360/d)*(n+1)`.
- Pilot bounds require `0 <= frequency_min_hz < frequency_max_hz`; positive-frequency filtering is inclusive. Fixed sphere/shell evidence materials: R=1e6 m, rho=4000 kg/m³, vp=8000 m/s, vs=4000 m/s; shell inner radius 0.3R with fluid inside the complete model. PREM checks name n=1,l=1 and n=0,l=2/3/4 in each solid domain. Verify W proportional to r and its null multiplicity using scaled stiffness residuals, not a universal frequency threshold. An installed API snippet run outside the repository satisfies the pilot installation example; the source recipe remains useful but is not described as an installed wheel file.
- Root captures the existing canonical Chinese teaching prose into website-only localization resources **before** product ownership regenerates English lessons. The product agent waits for that readiness message; it may work independently on English source/docs/API meanwhile.
- `CONTRACT.md` is included in the ownership manifest. The package reviewer also owns any existing source media recipe/readback adjustments required by the new multi-primitive GLB, coordinating with the product documentation writer.

Implementation now proceeds under these contracts. Reviews remain separate from implementation evidence. A new counterexample can reopen only the affected decision; absent such evidence, do not restart broad planning.


## Implementation acceptance

The frozen package APIs, Scene 1.1 grid controls and legacy compatibility, English maintained resources, bilingual website and experimental toroidal core are implemented. The actual first-round review found and repaired offline cut-face overdraw and an inconsistent CLI GLB preflight. A subsequent real browser review found and repaired SVG control-icon capture. Independent rechecks, language/state evidence and remaining limitations are recorded in [the integration review](reviews/phase-2-implementation-r2-integration.md), [scope review](reviews/phase-2-implementation-r2-scope.md) and [pilot review](reviews/phase-2-implementation-r1-pilot.md).

Validation before distribution: 83 Python checks and 25 frontend checks passed; TypeScript, lint and static production build passed. The toroidal matrix contains 19 independently reproduced comparisons; these are named-case evidence, not a universal accuracy guarantee. The final release review records wheel/source installations and decoded production artifacts. Publication of the static website is independent of package acceptance.

No default numerical backend promotion occurred. The next numerical stages remain radial elasticity/gravity, followed by spheroidal solid-fluid self-gravity under the independent gates in [NUMERICAL-OWNERSHIP.md](NUMERICAL-OWNERSHIP.md). A compiled implementation requires measured performance evidence and preserved conventions; it is not a prerequisite for useful package workflows.
