# Phase 2 planning review, round 1: standalone package and presentation contracts

This is a planning review, not an implementation report. It considers the user's four requests: English outside the bilingual website, a useful standalone package, adjustable surface-grid density, and a reasoned future path toward an independently maintained numerical implementation. No implementation files were changed for this review. Existing release evidence was inspected rather than repeating its numerical matrix or clean installations.

## Assessment

The package already performs substantive work without the website. Phase 2 should improve discoverability, close a few configuration gaps, and add one well-defined presentation control. It should not replace a working scientific core or turn a presentation request into a new numerical method. The most consequential design decision is to separate **visible surface-grid density** from **field sampling resolution** and **solver finite-element allocation**.

The plan is ready for a first revision, but not yet ready to freeze: the surface-grid representation, configuration precedence, wire compatibility, and retained English documentation inventory need explicit decisions. Rounds 2 and 3 should challenge those decisions and their acceptance criteria before implementation.

## Evidence from the current package

| Area | Actual state and evidence | Phase 2 implication |
|---|---|---|
| Standalone installation | `pyproject.toml` defines the Python package and `terra` entry point. `docs/reviews/implementation-round-3-release.md` and `docs/validation/release.json` record separate wheel/sdist installations outside the repository, real T-mode solves, fields, PNG, GLB, and media recipes. Package resources include PREM, palettes, coastlines, schemas, and licenses. | Do not claim the package needs to be made independent from scratch. Preserve this path and make its first-run documentation easier to find. |
| Scientific API | `packages/earth_modes/__init__.py` exposes model constructors, `solve`, bundle/project I/O, `default_scene`, field evaluation, and probes. `earth_modes.export` and `earth_modes.analysis` are focused public modules. Importing the numerical API does not initialize a plotting backend. | Keep these module boundaries. A small task-to-API reference is more useful than a new facade, plugin system, or package split. |
| CLI | `packages/earth_modes/cli.py:parser` offers model, solve, inspect, scene, export, probe, and compare. Solve accepts a JSON configuration in SI units with explicit CLI overrides; its frequency flags intentionally use mHz. | Retain the existing commands and document precedence and units together. Avoid a second configuration language. |
| Portable production | `make_project` combines scientific data, a hash-bound scene, and optional ProbeSpec/ExportSpec. CLI `_load` accepts either a project or bundle plus scene. `examples/recipes/render.py` already constructs a self-contained project without a browser. | Use a project as the primary reproducible production example. A browser login, web server, or model download must remain unnecessary. |
| Existing output limits | `export_common.ExportLimits` permits explicit offline Python limits. CLI `_export` constructs default limits internally and has no export-limit option. `docs/CONTRACT.md` currently says these limits can be raised through the offline API/CLI. | Correct the unsupported CLI claim or deliberately add one bounded JSON limits option. Do not list an absent feature as existing capability. |
| Scientific image configuration | `export_plot` and `export_probe` accept width/height, transparency, and annotations. CLI `_export` rejects width/height for every scientific kind; `_probe` does not expose those production controls. Saved project ExportSpec is applied to visual exports, but not to those scientific paths. | Close the small public workflow gap or document the deliberate restriction. Recommended: share relevant option resolution while keeping scientific kind/probe selection explicit. |

A small command confirmed the scientific-image gap:

```sh
.venv/bin/terra export examples/lessons/03-indices.terra.json \
  --kind eigenfunctions --width 640 --height 480 \
  --out /tmp/terra-phase2-plan.svg
```

The CLI refused it with `Scientific plots/tables do not support these options: width, height`; the Python image API supports both. The request failed before writing an output. This is a concrete usability improvement, not a reason to redesign all exporters.

## Recommended bounded package changes

### Keep

- The current Python/SciPy numerical implementation, private pinned Ouroboros source, explicit approximation labels, and existing quality evidence.
- The small dictionary-based, versioned public data interface. Keep an explicit distinction between a numerical bundle, a presentation scene, a probe request, and export production settings.
- Separate scientific plot/table operations and visual movie/mesh operations. A format such as SVG alone cannot identify whether a user wants eigenfunctions, a material profile, or a probe.
- Atomic output protection, explicit overwrite, independent material sides, fixed physical times, and recorded appearance limitations.

### Change

1. Write an English first-run path for an installed wheel, followed by a repository/sdist path. The first path should generate a material model, solve one small mode group, inspect evidence, create/save a project through the public API, and render/read a result. It must not assume an `examples/` directory inside an installed wheel.
2. Add a compact API/CLI capability and configuration table. State the actual import paths and show the portable project path before advanced settings. Clarify that solver mesh size, rendering quality, and the new visible-grid control have different meanings.
3. Resolve the relevant production options consistently for scientific images. A proposed rule is: explicit call/CLI options override saved project options; unspecified values use the operation's documented default. Width, height, transparency, and annotation apply to image operations; fps and playback duration do not alter scientific curves. CSV must reject explicit image-only arguments, while irrelevant inherited image defaults must not make a valid CSV request impossible. The saved scientific operation and ProbeSpec remain explicit rather than inferred from a suffix.
4. Correct stale claims about CLI resource customization. Raising export limits can remain a Python API capability in this phase; adding every limit as a flag is unnecessary. If CLI-only large production is included, accept one validated limits JSON file with unknown keys rejected and record the resolved limits in production diagnostics. This is a scope choice to settle in round 2, not an assumed commitment.

### Add only if it closes an observed task

A small `terra project` assembly command could combine a bundle, scene, and optional probe/export JSON using the existing `make_project` contract. It would let CLI-only users produce a self-contained project without an ad hoc Python one-liner. It is useful but not required to prove package independence: the public Python path already works. Do not add an interactive project wizard, arbitrary nested mutation syntax, or a workflow engine merely to avoid documenting this existing API.

## Surface-grid density: the necessary semantic decision

There are currently three different sampling systems:

| System | Current control | Current behavior |
|---|---|---|
| Numerical discretization | `solve(mesh_size=...)`, CLI `--mesh` | `solver._allocation` distributes elements among material layers, with at least four per layer and thickness/travel-time weighting; provenance records actual counts. This changes the numerical approximation. |
| Field rendering | `Scene.quality = draft/standard/high` | Python `export_render.geometry` and browser `geometry.ts` use a degree-dependent angular floor. True sections add active source knots and each material side through `sampling.layer_radial_nodes`. This controls representation accuracy and cost. |
| Visible surface mesh | `Scene.surface = wireframe` | Browser `Viewport.tsx` uses `MeshStandardMaterial.wireframe`; Python `export_render.py` draws the edges of all generated faces; Python `export_glb.py` turns triangle faces into line indices. Density is therefore tied to actual triangulation. |

The user's request concerns the last row. Relabeling the solver slider or the existing quality presets would not satisfy it. Lowering numerical mesh density to make a sparse illustration would be scientifically inappropriate.

Recommended requirement: **an explicit, reproducible visible-grid density control, independent of the numerical bundle and the sampling needed to evaluate its motion**. A single bounded density parameter with a fixed longitude/latitude ratio is sufficient initially. Do not add separate polar, equatorial, longitudinal, latitudinal, radial, and adaptive sliders without a concrete use case.

Round 2 must settle the representation. A practical option is a coarser surface-edge skeleton whose edges are sampled finely enough to follow the canonical deformed field. This decouples how many edges are visible from how accurately each edge moves. If the chosen design instead changes actual surface tessellation, its density floor must remain explicit and users must be told when high-degree modes prevent further coarsening. A silent clamp would defeat the requested control. A geographic graticule should not be mislabeled as an arbitrary triangulated mesh.

The coordinator's draft proposes `wireframe_spacing_deg` in {5, 10, 15, 30}, absent/null for the legacy triangle mesh and 15 degrees for newly created scenes. This is a bounded, feasible candidate: use explicitly named parametric latitude/longitude surface-grid curves, with degree-aware samples along each curve, while retaining scientific triangulation on section faces. Its spacing is clearer than an abstract density multiplier. Acceptance should include the pole/seam convention and clipping against the removed quadrant; it need not introduce arbitrary mesh editing. The remaining compatibility concern is that a phase-1 viewer could ignore an unknown spacing field, so the migration/version decision must be explicit even if legacy null is retained.

Whatever representation is selected, require these properties:

- Changing visible density does not change frequencies, eigenfunctions, raw probes, normalization, or the bundle hash.
- Edge points move using the same physical field, layer choice, absolute time, and deformation gain as the surface. Do not evaluate just coarse endpoints and stretch straight edges across unresolved structure while claiming accurate high-degree geometry.
- Wire geometry and its cached mode fields count toward existing point/cache/morph budgets before allocation. More controls do not waive the existing limits.
- Browser view, Python PNG/frames/video, and both GLB exporters preserve the chosen grid or explicitly reject an unsupported request. Static lines in an animated GLB would be an incomplete implementation.
- Define whether the control applies only to the curved shell. It should not silently alter source-knot preservation or the material boundaries of a true cut face. There is already a relevant backend difference: browser wireframe is limited to `patch.kind === 'surface'`, whereas offline face-edge rendering and GLB currently start from all faces. Resolve this deliberately as part of the grid contract.
- Record the requested density, actual segment/vertex counts, and sampling policy in the manifest. A sparse visible grid is a presentation choice, not evidence of convergence.

## Schema and compatibility

The new setting belongs in SceneSpec, not SolveSpec or ExportSpec. Every backend must consume the same saved value. Add it to the Python validator/defaults, TypeScript types/validator/defaults, packaged scene schema, geometry cache key, resource preflight, project restoration, and export manifests together.

Do not introduce a new semantic field as arbitrary unknown metadata and assume older viewers will honor it. Current readers intentionally retain unknown keys; an old reader could accept the project while ignoring its new appearance. Prefer an explicit scene-version change with a small, documented legacy path, retaining bundle version 1.0 if its scientific shape is unchanged. Whether the project wrapper also needs a new version should follow its actual semantics rather than changing every version together.

For legacy projects, preserve the old effective mesh interpretation or make migration explicit. Do not silently overwrite a saved scientific bundle merely to adopt new presentation defaults. Locale also must not change scientific identity: translate website labels around canonical values, rather than translating `model.name` inside the hashed model.

## English-only non-website materials

A file scan found no Han text in `packages/earth_modes`, `schema`, or `vendor`. Core CLI messages, Python docstrings, schema descriptions, model labels, and export annotations are already English. The substantial work is authored documentation and generated teaching content: 36 files under `docs/` contain approximately 74,020 Han characters, README approximately 1,350, nine example files contain Chinese text, and `scripts/generate_lessons.py` contains Chinese teaching copy. These are inventory measurements, not quality scores.

The retained first-party non-website surface should be English:

- README, user/data/developer guides, current plan/contract/roadmap, package metadata, source comments, command help/errors, examples and their instructions.
- Canonical teaching projects/catalog text and generation source, figure annotations, manifests, downloadable lesson explanations, and review/release summaries that remain in the distribution.
- Keep raw external source material, proper names, mathematical symbols, existing user-imported strings, and Unicode conformance fixtures unchanged. An English product policy must not become an ASCII-only data restriction or a reason to rewrite upstream evidence.

Avoid maintaining duplicate Chinese/English prose throughout the repository. Put website translations in a website-owned message/catalog layer keyed by stable lesson IDs and message IDs. Generate or retain canonical English teaching metadata in standalone projects; the browser may show its Chinese translation without mutating the underlying bundle or losing provenance. Decide explicitly whether a browser-exported explanatory caption follows the selected website locale; package-generated annotation should remain English.

Documentation volume is a real planning cost. Retained historical reviews must either be translated or replaced by an English evidence-preserving summary/index after removing obsolete duplicate prose from the current distribution. Do not quietly exempt dozens of shipped Chinese files while claiming that only the website remains bilingual. Preserve original external evidence and the distinction between observations, fixes, and unexecuted checks. Deleting valid regression evidence to reduce translation work is not an acceptable simplification.

## Future numerical ownership and language choice

The current source already isolates an attributed numerical core under `earth_modes.vendor.Ouroboros`, with solver adaptation and explicit patch provenance in `solver.py`. ModeBundle provides a useful boundary for a future implementation. Keep improving that boundary and its physical evidence; do not create a plugin registry or introduce Julia/Rust/C++ merely to signal future ownership.

A bounded phase deliverable is an English decision record that identifies the current assembly/eigensolve costs, the independent numerical formulation one would own, and evidence required before replacing each part. Python/SciPy remains the default unless a measured bottleneck or missing solver capability justifies an alternative. Compare real workloads and packaging costs before choosing a compiled numerical kernel. Any implementation derived from Ouroboros must continue honoring its license; changing language does not remove derivation obligations. A detailed solver-method assessment belongs to the parallel numerical review, not to the mesh-density implementation.

The website should continue importing canonical numerical output regardless of the future solver language. A new backend should first reproduce a small existing physical case and emit honest provenance; it should not require a new website or data model just to change the assembly implementation.

## Necessary acceptance and next review gates

1. **English package path:** from an installed wheel outside the repository, follow the English quickstart to a real solve, finite field, saved project, and decoded image. Reuse the existing small case; do not rerun N1–N6 solely because prose changed.
2. **Production options:** exercise one scientific image with explicit dimensions, one inherited project setting overridden at the CLI, and one explicit inapplicable CSV option. Compare actual output/manifest values and confirm failure leaves prior output intact. Do not enumerate every combination.
3. **Grid semantics:** compare sparse and dense versions of one low-degree and one high-degree scene. Verify the visible change, unchanged numerical identity/probe values, correct line motion at a non-key time, and preflight rejection of an over-budget combination. Include a cutaway/material-side case if that representation changes.
4. **Compatibility:** load one phase-1 project and one new-grid project in Python and the browser. Check retained metadata, version handling, bundle identity, and saved effective appearance. A validator-only test is insufficient if an exporter then drops the setting.
5. **Language boundary:** review retained first-party documentation and generated outputs for unintended bilingual leftovers; verify website language switching does not alter scientific hashes or strip arbitrary user text. A script can list suspected strings, but should not reject Unicode data or replace human terminology review.
6. **Release:** after code changes, repeat the existing small clean-wheel smoke and affected media checks. Avoid expanding to a broad platform CI matrix or repeating full independent frequency benchmarks unless numerical code changes justify it.

Round 2 should freeze the visible-grid representation, option precedence, compatibility policy, and exact English document set, then challenge implementation effort across both renderers and GLB. Round 3 should simulate the final user paths and confirm that each promise has an implementation owner and a small meaningful acceptance check. After those three sequential planning iterations, execute the bounded plan rather than reopening general architecture without new evidence.
