# Phase 2 planning round 2 — integration challenge

This reviews the revised `PHASE-2.md` before implementation. It preserves the scientific baseline and checks whether the new promises can remain one coherent product.

## Necessary refinements

1. **Preserve diagnostics before formatting.** `Viewport.tsx` currently converts caught errors to strings, and status messages are assembled inside the renderer. Merely adding a localized error class to validators would lose its identity at these callbacks. Pass structured diagnostics through callbacks/state and format at the UI boundary. Locale changes must rerender existing messages without rebuilding geometry or restarting the playback effect.
2. **Export text needs explicit ownership.** `Charts.saveSvg` currently clones visible SVG. Reuse the same plot description with canonical English annotation fields for download. Do not maintain two numerical calculations or run broad string replacement on arbitrary series names. User model names remain user data even if they contain Chinese.
3. **Version numbers have separate responsibilities.** Bundle scientific data and Project wrapper remain 1.0; Scene moves to 1.1 only for the new display contract. Keep old 1.0 projects readable and allow a deliberate appearance update. Website tools and output recipes must forward the scene version and spacing rather than reconstructing partial scenes.
4. **Known filled-section inconsistency is a bug fix.** Record the old offline all-wire behavior and the new filled scientific section explicitly. Legacy means preserving shell triangle wires, not preserving a cross-export bug that obscures material sections. A cutaway GLB needs separate line and triangle primitives with aligned animation targets.
5. **Examples require reproducible packaging.** One 1.8 MB PREM bundle plus the small catalog is reasonable; six duplicated self-contained bundles are unnecessary inside the wheel. Keep only one maintained source, validate generated copies, and return a fresh validated project per load. Loading examples cannot trigger a solver or require network access.
6. **Documentation is current guidance plus preserved evidence.** Correct current PLAN/WORKFLOWS claims that implementation is still pending. Historical review reports retain their at-the-time pending statements with an archival context sentence. Translate findings faithfully rather than converting all reports into acceptance summaries.

## Scope and workflow decisions

Remove the proposed extra `terra project` command from the phase scope: `terra example` and the existing public `make_project` API close the demonstrated installed-package path. No general nested scene-edit command or new GUI is needed. A simple `terra scene --wireframe-spacing-deg` may expose the specific new control without a new configuration language.

The experimental solver should be callable through a focused API and executable installed example; adding a backend registry or changing the default `terra solve` behavior would broaden compatibility obligations without improving the stated pilot evidence. Its new numerical tests must have independent expectations and avoid rerunning unrelated full-gravity benchmarks solely because new files exist.

Freeze concrete file ownership after round 3. Keep shared `cli.py` edits sequential. Root alone edits the Site checkout; researchers can produce English documentation, numerical modules and canonical assets outside it. Generated asset synchronization and final web schema changes happen after their source owners report ready.

## Acceptance emphasis

- Validate locale completeness, parameter use and state preservation, including already-visible errors and Chinese UI exporting English charts.
- Compare physical data and effective wire geometry across scene versions and renderers, including an interior cutaway and a non-key GLB time.
- Install the finished wheel outside the repository, load an example, independently solve a small model, create a project, render a scientific image with explicit sizing and execute the pilot.
- Verify retained authored text and generated lesson copy in the release, while permitting Unicode researcher data and original third-party evidence.

The revised scope is useful and bounded provided these integration details survive round 3. No implementation or verification success is claimed by this review.
