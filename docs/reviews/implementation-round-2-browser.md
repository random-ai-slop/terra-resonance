# Implementation round 2 — real browser workflows

Root used the actual local application in the Codex browser and Microsoft Edge, with filesystem readback of Edge downloads.

## Findings and changes

- Numeric controls rejected intermediate keyboard input. Selecting latitude 28 and typing `-35` left 28 unchanged. NumberField now retains a local draft and commits finite in-range values on Enter/blur. Repeating the exact interaction produced -35. Escape discards the draft.
- A three-sample probe starting at 123 s with step 0.1 s produced five identical x-axis labels `2.05`. Tick precision now follows the tick interval; the visible labels distinguish 2.05000 through 2.05333 min.
- Sequential automatic downloads could save the scientific file without its JSON record. Browser PNG/GLB/SVG/CSV now use one ZIP containing both files. The existing dependency-chain ZIP library fflate is an explicit dependency, rather than a new bespoke archive implementation.

## Verified workflows

- Real JSON file input restored an independent ProbeSpec (12°,34°,0.7R; start 123; exact step 0.1; 3 samples), defaults normalized=true/derivative=0, partial ExportSpec defaults and unknown lesson metadata. Saved `terra-project (1).json` was parsed independently from disk and retained those exact values.
- Invalid project version 99 displayed a specific error and preserved the prior PREM 0S2 scene.
- A downloaded SVG ZIP contained actual vector curves and its kind=eigen record with the current bundle hash.
- Downloaded PNG ZIP decoded to 1200×900 RGBA, contained nonempty rendered geometry and readable legend/quality/time annotations, and matched its JSON dimensions and bundle hash.
- Downloaded GLB ZIP had glTF 2.0 header, two meshes, a morph-weight animation and its interpolation/scene/export provenance. Independent numerical reconstruction is covered separately by browser-export tests.
- The six-case beat preset opens the intended probe chart and retains a material point and two independent physical frequencies.

The in-app browser did not expose working file downloads during this local test; standard Edge downloads were exercised and read back. Complete page reload was used after Vite dependency optimization to avoid judging transient hot-reload failures as production behavior. Production and responsive release checks belong to Round 3.
