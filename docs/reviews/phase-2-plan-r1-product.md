# Phase 2 planning, round 1 — product and language contract

Status: independent planning review only. No implementation changes. Reviewed the current frontend, Python renderers, lesson generator, maintained documentation, and the initial `PHASE-2.md` proposal. The proposal is feasible, but the boundaries below must be resolved before implementation. This is not an approval to start work before planning rounds 2 and 3.

## Findings from the actual implementation

1. **The website is currently Chinese with scattered English, not bilingual.** `apps/web/app/layout.tsx` fixes `lang="zh-CN"`, title and description. `Workbench.tsx`, `Charts.tsx`, `Viewport.tsx`, `Controls.tsx` and science helpers contain visible text, accessible names, errors, loading states and quality labels. Translating only JSX headings would leave import errors, render-budget failures, chart axes, tool descriptions and status callbacks in the wrong language. In particular, `lib/science/data.ts` mixes Chinese prose with machine field paths; `qualityLabel` embeds Chinese in the scientific data module.
2. **Built-in teaching copy has two competing sources.** `Workbench.tsx:42` defines `presetInfo`, while `scripts/generate_lessons.py` generates titles, steps, conclusions and cautions independently. The beat lesson already has differently worded titles. The catalogue, six standalone projects and their saved `teaching` metadata must remain one scientific lesson definition; translations must not become alternate scene definitions.
3. **Changing a locale cannot safely mean changing every displayed string in place.** `Charts.tsx:316` exports SVG by cloning the visible DOM, including Chinese axis labels. In contrast, `browser-export.ts` constructs English PNG annotations, and Python exporters already generate English labels. A translated browser could therefore produce different-language artifacts depending on the selected format. This must be an explicit language rule, not an accidental consequence of the renderer.
4. **Grid appearance is coupled to field sampling.** `geometry.ts:87` and `export_render.py:101` use quality bases 32/48/96 and an angular floor `4*(l+1)`. `Viewport.tsx:335` renders every surface triangle edge through the Three.js material. Thus the existing quality selector is not an independent visible-wire-density control, and high-degree modes can defeat attempts to make a less cluttered grid by reducing quality.
5. **There is a relevant existing cross-export inconsistency.** The browser applies wireframe only to patches whose kind is `surface`, leaving section faces filled. Python's `export_render.py:259` applies wireframe to the combined face collection; `export_glb.py:182` converts all faces to lines. Wireframe plus cutaway therefore differs across outputs. Resolve this while introducing density, rather than preserving three incompatible interpretations.
6. **The English migration extends beyond README.** A source inventory found maintained CJK text in 36 files under `docs`, 9 under `examples`, and `scripts/generate_lessons.py`, in addition to the root README. No CJK text was found in the Python package source/assets in that scan. Translating generated JSON alone is insufficient because rerunning the generator restores the old copy. Historical adverse reviews must be translated, not removed or rewritten as success claims.

## Language boundaries to freeze

Adopt English as the canonical maintained language outside the website. This is compatible with a Chinese website and does not require a bilingual Python package.

| Surface | Proposed behavior |
| --- | --- |
| Python/CLI help, diagnostics, docs, comments, examples, generated lesson projects | English maintained copy |
| Website controls, descriptions, quality summaries, accessibility text, loading/error/status UI | One selected locale, `en` or `zh-CN` |
| IDs, JSON keys/enums, units, mode symbols, hashes and CLI commands | Stable canonical values; never translated |
| PNG/SVG/GIF/MP4 annotations and machine sidecars downloaded from either renderer | English maintained copy, independent of website locale |
| Researcher-authored model names, citations, arbitrary metadata or imported teaching text | Preserve verbatim; do not translate, censor or rewrite scientific inputs |
| Upstream licenses and original third-party notices | Preserve the authoritative original; add an English explanation only where necessary |
| Screenshots used as evidence of the Chinese website | Remain authentic evidence; captions and surrounding documentation become English |

The exception for Chinese strings should be narrow: website localization resources and authentic website evidence. Do not add translated Python error strings, Chinese lesson prose in the canonical package, or bilingual generated reports.

**Do not add a locale field to SceneSpec or ExportSpec in this phase.** Scene is scientific/display state; website locale is a user preference. The requirement makes maintained artifact copy English, so an export-language selector would add an unsupported choice and duplicate a constant. Record `annotation_language: "en"` in artifact metadata where text is rendered. Do not claim that arbitrary imported user text is English merely because maintained labels are.

### Website state and persistence

Use a small typed message catalog and one React locale provider, not duplicate pages or a new application framework. Keep an English catalog as the key/type reference and require complete Chinese key coverage. Components request semantic messages with parameters; do not concatenate fragments whose word order differs by language. Keep units and scientific number formatting deliberate: decimal points and SI symbols remain stable; surrounding count/time prose may be localized.

Choose English on a fresh installation. An explicit language selection persists under a versioned website preference key. An optional explicit `?lang=` takes precedence for shared website links; project import does not change the reader's language. Unsupported saved values fall back safely. If browser-language detection is added, it must rank below an explicit saved choice and cannot create a hydration mismatch; it is not necessary for this phase.

Update document language, title and description alongside visible text. A neutral loading shell until the locale is resolved is preferable to mounting the whole Chinese workbench and immediately replacing it. Locale switching must preserve the live physical time, playing/paused state, camera, terms, independent probe, export settings, comparison bundle, and open panels. It must not remount the WebGL engine or rebuild its field bases. Never include locale in the geometry cache key.

### Diagnostics and imported metadata

Keep scientific validation errors canonical English in the package and science layer. Where website-owned validators generate errors, use a small typed error with a stable code, field path, parameters and English diagnostic. The website renders the code through its catalog. Ordinary unexpected exceptions remain available as original diagnostic details under a localized explanation; do not translate messages by substring matching or swallow details to claim a clean locale.

Cover the entire owned error surface, including import, schema/semantic validation, render/time/resource limits, empty mode selection, unsupported outputs, failed fetch/encoding/download, and tool API responses. English quality status codes remain unchanged; localized quality explanations belong in the presentation layer.

Canonical lesson prose should be English in the generator and its outputs. Delete `presetInfo` and use the actual catalogue for the six entry points. Website translations are keyed by stable lesson identity and version, with corresponding step identities/ordering validated. Only a recognized built-in lesson may receive translated presentation text. A project with edited or unfamiliar `teaching` metadata is displayed verbatim; matching a familiar `id` alone is insufficient to overwrite it. Saving a project preserves its original metadata and canonical English built-in copy, regardless of the current UI locale.

### Artifact rendering

Keep browser PNG's independently rendered annotation model, but centralize its English labels rather than leaking UI messages into it. Change SVG export to render the same numeric series and analysis state with English artifact labels; do not clone a Chinese chart and hope its labels are appropriate. Do not temporarily switch the whole app to English for export. The visible chart can remain Chinese throughout the download.

A small shared plot description—series, label identities/parameters, units and analysis state—is sufficient. The interactive chart and artifact renderer consume the same numbers. Avoid a second chart-computation implementation. Keep ZIP media-plus-sidecar delivery, independent probe semantics, raw normalization, comparison identity and provenance already fixed in phase 1.

## Surface density: minimum sufficient product design

The root proposal correctly separates visible wires from scientific samples. Preserve `quality` as the existing scientific tessellation policy and preserve every active radial source knot. Add **one** bounded, reproducible density setting for the displayed surface grid; do not add independent latitude, longitude, diagonal, line-width and section-grid controls in this phase.

A useful candidate is an integer count of latitude intervals, with twice that many meridians. The exact name/range/default belongs in round 2's shared contract. Grid curves must be evaluated/subdivided using the retained scientific field sampling, not straight coarse chords between a few grid intersections. Low visible density must not change frequencies, material-point motion, node extraction, radial resolution or color limits. Higher density increases visible geometry and must participate in preflight memory/vertex and GLB morph budgets.

Label the control **Surface grid density**, not numerical mesh resolution. Show it only when a surface grid is relevant; retain the setting across a switch to solid rendering. In advanced settings, call the existing control **Field sampling** to distinguish its purpose. If the new grid uses latitude/longitude curves instead of triangle edges, state this honestly: it is a display grid, not the solver's finite-element mesh.

For cutaway scenes, retain filled scientific section faces while applying the density choice to the outer/internal shell grid. Python PNG/video and both GLB implementations must follow that same rule. GLB can use line primitives for the grid and triangle primitives for sections, with the existing morph-weight model. Unsupported density must not be silently ignored in an exporter.

Old SceneSpec files need an explicit compatibility rule. Either absence preserves legacy triangle-wire appearance, or a versioned/defaulted migration selects the new documented grid and records that migration. A silent change to all existing saved wireframe projects is not acceptable. Round 2 must choose the default and test one legacy project before freezing implementation.

## Restrained layout changes

Retain the ink-blue viewport, pale analysis panels, restrained scientific typography and current task hierarchy. Remove decorative English eyebrow subtitles when they merely repeat a localized heading. Use one language per label; keep symbols such as n/l/m and U/V/W as scientific notation.

Add one accessible, plainly labeled language selector in the header; do not use national flags to represent languages. Allow header actions to wrap and use a compact overflow treatment only if required by the measured narrow layout. The current 270 px sidebars, fixed small typography and long choice labels need English-width checks. Increase available label space or wrap help text before shrinking fonts. Do not redesign the entire workbench solely because English strings are longer.

Preserve the existing mode → field → analysis → output flow and presentation mode. Keep frequently used controls visible, put field sampling and explanatory detail in advanced sections, and keep scientific warnings readable in either language. Test translated dialogs, dropdowns, tooltips, screen-reader names and presentation mode as part of the same layout, not only a static landing screenshot.

## Package-first completion gate

The phase is not complete when the website switches languages. A freshly installed wheel, from outside the repository, must offer a documented English example entry point that produces a real bundle/project and useful PNG/GLB output. A concrete small interface is `load_example("prem")` plus `terra example --out project.json`, returning/writing a fresh self-contained project; round 2 must freeze the return type and default name. It should reuse one canonical compact example and explicit model/solve APIs, not ship another divergent teaching implementation. A package guide must explain CLI, API, scientific limits, optional FFmpeg/Blender and output provenance before linking to the website.

English migration must update generators before regenerating examples and teaching artifacts. Preserve numerical arrays, provenance evidence, physical scene/probe/export values and bundle hashes where only teaching prose changes. Rebuild wheel/sdist and verify that their included README and examples match the new policy.

## Necessary validation and round-1 decision

- Catalog key/parameter completeness for both website locales; a maintained-text inventory gate permits CJK only in declared website resources/evidence and user-data fixtures.
- One real locale switch while playing, with a nondefault camera, independent boundary-side probe, imported metadata and export settings: exact scientific state and input hashes remain unchanged.
- One built-in lesson and one edited imported lesson: localization works for the former; the latter survives import/save without replacement.
- Actual English and Chinese narrow/wide browser flows, including errors, selectors, keyboard names and presentation mode; no horizontal overflow or inaccessible controls.
- Chinese UI → English SVG/PNG/GLB-sidecar exports: decode/parse the output, verify the same numeric data and required analysis metadata, and confirm the visible UI never changes language during export.
- Low/high surface density across browser, Python still/video, and GLB: same field/trajectory/node data, expected line-density change, correct cutaway fill, preserved source knots, explicit preflight failure for a bounded expensive case.
- One old scene import and one new scene round trip in both languages/runtimes; no silent loss of the new setting.
- Clean wheel/sdist package example and generated-English-text checks. Do not rerun the entire spectral benchmark suite for translation-only edits.

**Round-1 conclusion:** retain the scope in `PHASE-2.md`, delete duplicated lesson/UI prose, add a presentation-only locale boundary and one grid-density parameter, and repair the related wireframe/cutaway mismatch. Do not add multilingual Python outputs, automatic translation of research metadata, a replacement UI framework, or a broad visual redesign. Round 2 must settle legacy-grid migration, built-in lesson translation identity, and English SVG rendering before the plan is ready to freeze.
