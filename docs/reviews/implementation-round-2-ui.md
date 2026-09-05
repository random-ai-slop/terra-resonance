# Implementation round 2: user workflows and production state

Historical review by visual_research, sequentially after round 1 closed. Read Workbench, Charts, Viewport, Controls and browser exporters, using deterministic parameter counterexamples. The lead separately performed real pointer/keyboard/download/responsive checks; unexecuted interaction is not claimed here.

## Findings

Display edits during playback now begin from the engine's current physical time, so the previous reset-to-zero defect was not reproduced in the code path. Independent ProbeSpec defaults and exact step were retained. Two production-state blockers, a recomputation mismatch and a necessary input improvement remained.

### U1 / P1: recipe and generated CLI command disagree

Workbench recognized only gif/mp4/png/glb; all other formats fell back to earth.mp4. Selecting lossless frames, scientific SVG or numeric CSV therefore generated a video command. Commands ignored transparency and annotation=false. For legal imported GIF fps=null, the UI used 20 fps but the command used 24, which exact GIF timing rejects.

These followed directly from expressions without network/expensive solves. GLB text also hardcoded eight seconds after duration changed, and described dimensions as below when controls were above.

Extract a pure output-recipe builder with explicit format → CLI kind/path/options. Use the complete project as the request source rather than duplicating scattered fields. Frames need `--kind frames`; SVG needs an explicit scientific kind; CSV needs tables or a named probe operation. Test actual semantics, transparency/annotations and format defaults, not string existence.

### U2 / P1: three independent GLB omission flags collapse on save

This was identified but not marked repaired in round 1 and was explicitly closed here. Importing `{omit_arrows:true, omit_geography:false, omit_analysis_overlays:false}` reduced the flags by AND to one false switch; save rewrote all three false even without user action. A true switch could also contaminate a subsequent PNG request with unsupported GLB options.

Preserve all three values in ExportSpec. Only an explicit user toggle changes all together. Browser GLB must consume independent values rather than interpreting a false aggregate as retain everything. Other formats must not inherit inapplicable preferences. Save, command generation and browser output use the same effective request.

### U3 / P2: recomputation command does not replay the original request

The source/recompute section hardcoded RST/lmax8/mesh280/gravity2. A gravity0, different-window or linear-Q import followed by this command computed different physics.

Download exact `bundle.provenance.request` as solve.json and use `terra solve model.json --config solve.json --out modes.json`. If absent, explicitly state that replayable options are unavailable instead of presenting a demo command as recomputation. Preserve SI units in Model/config.

### U4 / P2: NumberField rejects intermediate edits

A numeric controlled value updated only when finite and in range. Clearing the input or typing a lone minus left state unchanged, causing restoration of the previous value and obstructing normal negative-coordinate/decimal entry.

Keep a local string draft and validate/commit on blur or Enter. Invalid values receive feedback or return to the last valid number; scientific state accepts only validated values. No new control library is needed. The lead owned keyboard reproduction and repair.

## Other checks and scope restraint

Controls had labels/ARIA names, presentation had an exit, and narrow layouts stacked with scrollable scientific labels; actual accessibility/layout required lead screenshots and keyboard use rather than CSS inference. Viewport.configure retained old geometry/state, frame failure restored previousTime, and PNG finally restored renderer size, frustum and alpha. No replacement state framework was warranted.

Quality must retain its actual status, evidence and warnings rather than become universally trusted. Standard Edge successfully downloaded/read a project; the in-app host did not emit a download event, which cannot support a claim that all browsers were tested.

## Minimum repair acceptance

1. Execute frames/SVG/CSV, default-fps GIF, unannotated transparent PNG and partial-omission GLB through the generated project/command.
2. Opening/saving preserves partial omission flags; only the aggregate toggle changes them together.
3. Export a gravity0 or experimental-Q request as the exact Model/config; missing provenance never claims replay.
4. Type negative coordinates/decimals character-by-character and commit/cancel without corrupting scene state.

No additional production format or preset manager was needed.

## Implemented and checked

U1/U2/U3 were repaired through `lib/science/output-recipe.ts` and Workbench. Commands read complete terra-project data; frames/SVG/CSV select the correct kind; SVG explicitly passes scientific transparency/annotation flags; null GIF fps resolves at the proper exporter to 20. Independent omissions persist; hints list actual omissions. Recompute downloads original request or honestly reports absence. GLB duration text follows settings, and browser PNG/GLB buttons explain ZIP media/provenance delivery.

Two focused tests cover seven-format semantics/defaults and partial flags, including safe single-quote escaping of a mode ID in shell commands. TypeScript and relevant oxlint checks passed.

Actual cross-runtime execution constructed seven TypeScript projects/commands, then ran installed Python terra. PNG/GIF/MP4/frames/SVG/CSV/GLB all returned zero with appropriate artifacts. Readback checked transparent unannotated PNG, null-fps GIF with four 50 ms frames over 0.2 playback seconds, unchanged partial omissions, real SVG and material JSON. Evidence: `/tmp/terra-output-recipe-results.json`, beyond string assertions.

The lead's NumberField, short-window probe-axis precision and ZIP interaction verification remain in the integration record. This report did not substitute for round 3.
