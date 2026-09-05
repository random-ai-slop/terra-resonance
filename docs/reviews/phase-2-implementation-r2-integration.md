# Phase 2 implementation review — integration and real browser artifacts

Date: 2026-09-04. This follows the independent first-round Python, pilot and TypeScript reviews. It records actual changed behavior, not additional planning approval.

## Findings and repairs

1. **Scientific SVG selected a control icon (P1).** Downloading the point-time-series plot from the Chinese UI produced a valid SVG containing the derivative selector's chevron, with one path and no axes. The active tab lookup had selected its first SVG. The repair selects `.plot-wrap svg` within the active tab and reports an unavailable plot instead of silently doing nothing. A new real download decoded to three numerical paths, English `Normalized displacement` and `Physical time / min` axes and x/y/z legends, with no Han annotations. The downloaded figure is retained at `docs/validation/phase-2-browser-probe.svg`. The visible UI remained Chinese during download.
2. **Browser grid/resource metadata incomplete (P2).** The independent TypeScript review found the actual clipped segment count and animation-resource report absent. PNG/GLB metadata now reports actual grid index pairs; GLB also reports counted/visible points, cache bytes, conservative morph allocation and actual scalar weight/track counts. These reuse existing geometry and do not resample fields.
3. **Synthetic shell diagnostic remained English (P3).** The zero-component diagnostic previously placed `current shell` into a raw joined ID string. It now preserves real layer IDs and carries the owned fallback and list punctuation as nested message tokens, so existing diagnostics retranslate on locale changes.
4. **Website checkout documentation remained Chinese (P3).** The independent package text audit intentionally excluded the whole website directory. Root separately translated the web README; only website translation resources and intentional Unicode fixtures retain Chinese text.

## Browser evidence

- Current website tested in the existing in-app narrow viewport (464 px) and existing Edge desktop viewport (1466 px). English and Chinese had no horizontal document overflow; headings, controls, lessons and chart captions remained readable. The established blue/ochre scientific palette and restrained controls were retained.
- During playback, switching English to Chinese kept the player running: the displayed physical time progressed from 67.08 to 68.48 minutes, without returning to zero. Point parameters remained unchanged.
- Two real saved project downloads, one per locale with playback paused, were structurally identical. Scene version was 1.1, time 6229.431870990296 s, camera (-45 degrees, 20 degrees, distance 2.9) and teaching ID `03-indices`. Locale was absent from the scientific record.
- Surface controls exposed legacy triangle wires and 30/15/10/5 degree spacing. Switching to the 30-degree grid produced distinct curved material lines around filled scientific cut sections. Presentation mode remained functional.
- Twenty-five frontend checks cover scientific parity, budgets, binary GLB readback, complete message parameter parity, canonical teaching recognition, identical plot paths across locales and Scene 1.0/1.1 rules. The browser download counterexample was essential: parameter/unit checks alone did not find the icon-selection bug.

## Independent closure

The numerical reviewer independently confirmed both Python first-round findings fixed: the far-side cut comparison now has zero differing pixels, and the saved high-degree GLB recipe succeeds with authorized omissions and 57,910 effective points. The independent UI source review found no lifecycle/async-diagnostic/teaching-identity blocker. Clean installed distributions and final production publication are separate release gates, recorded in the release report.
