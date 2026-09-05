# Phase 2 implementation review 1 — Python grids, scenes and exports

Reviewer: numerical_research. Date: 2026-09-04. Independent read-only review of the other agent's Python scene/schema, geometry, GLB and CLI changes against frozen PHASE-2. No implementation files were changed. **Initial conclusion: two reproducible P2 workflow/rendering defects require repair.** Their narrow scope does not require reopening the phase plan.

## P2 — filled sections render through the opaque near hemisphere

Location: `packages/earth_modes/export_render.py`, render's separate shell/section PolyCollections, approximately lines303–315 at review time.

The phase-2 change partitions globally depth-sorted faces by surface type, draws the shell collection, then draws all filled section faces in another collection. That loses depth ordering across the two types. A cut on the far side consequently displays its internal radial field through the front opaque surface. This changes the scientific appearance rather than merely line density.

Actual reproduction from the installed-style example API:

```python
from copy import deepcopy
from earth_modes import load_example
from earth_modes.export import export_image
p = load_example('03-indices')
b, s = p['bundle'], p['scene']
s.update(deformation=0, reference=False, arrows=False, nodes=False,
         point=None, geography=False, surface='solid')
s['trajectory']['enabled'] = False
s['camera'].update(azimuth_deg=135, elevation_deg=0)
for cut in [False, True]:
    scene = deepcopy(s)
    scene['cutaway'] = cut
    export_image(b, scene, f'back-{cut}.png', width=600, height=600,
                 annotation=False)
```

The removed x>0,y<0 quadrant is behind this camera. With deformation zero and opaque surface, toggling that far cut should not reveal interior radial patterns. Actual outputs `/tmp/terra-phase2-python-review/back-False.png` and `back-True.png` differ by more than five channel levels at **82,994 of 360,000 pixels**, maximum difference **190**. Visual inspection confirms the cut face paints over the near hemisphere.

Minimal repair: for filled rendering, keep all shell/section faces in one globally depth-sorted filled collection. In wireframe rendering retain filled sections while explicitly handling curve/section depth; the present unconditional zorder2 grid lines can similarly overpaint an opaque section. Preserve the documented filled-section correction for both Scene1.0 and1.1. One far-cut visibility regression plus a front-cut view is valuable; do not replace it with an arbitrary full-image screenshot baseline.

## P2 — CLI rejects GLB recipes whose explicitly omitted overlays exceed display limits

Location: `packages/earth_modes/cli.py`, `_export` resource preflight around line348. `export_glb` itself already uses the effective scene with omitted arrows/geography/analysis removed.

The CLI resolves ExportSpec but preflights the original scene before invoking the exporter. A user can explicitly authorize omission of an expensive overlay and still be blocked by the memory/point cost of that omitted overlay. This breaks API/CLI parity and the saved-project production path.

Actual counterexample: `/tmp/terra-phase2-python-review/high-degree.json`, a validated manufactured S l=40 field fixture with surface=wireframe, spacing30, nodes=true, and saved export `{format:'glb', omit_analysis_overlays:true, duration_s:0.1, fps:24}`. This fixture tests legal high-degree output semantics; it does not claim a solved Earth mode.

- Original scene preflight: **273,078 points**, exceeding the default250,000.
- Effective geometry with the explicitly omitted analysis layer: **57,910 points**.
- Public `export_glb(..., duration_s=.1, omit_analysis_overlays=True)` succeeded and wrote `/tmp/terra-phase2-python-review/high-api.glb`.
- `terra export high-degree.json --out high-cli.glb` returned **2**, reporting the original scene's display budget.

Minimal repair: preflight the same effective GLB scene as the exporter after resolving/validating explicit or saved omission authorization. Preserve original scene and omission choices in provenance; do not silently omit a requested overlay when permission is absent. Reuse one helper if it prevents CLI/exporter policy drift. A focused legal-over-budget-overlay/API-CLI parity case is sufficient.

## Positive checks

The affected `tests/test_grid.py` and `tests/test_cli.py` suite passed: **9 tests**, 3 expected GLB static-color warnings, 12.58s in the review environment. Passing tests did not cover the two counterexamples above.

Independent actual file round trips additionally verified Scene1.0 with absent spacing and explicit null: both returned exactly the same parsed project object and did not mutate the input. All five Scene1.1 settings (null,5,10,15,30) validated. Scene1.0 with non-null spacing and Scene1.1 without the required field are rejected by the implementation/tests; no automatic legacy upgrade occurs during validation/load/save.

Code and running tests confirm:

- Graticule sampling retains the full scientific surface mesh and material-side cut nodes. Every curve uses the same time-dependent field. The spacing formula and full endpoint counts agree with the frozen recipe; axes are snapped only for robust undeformed quadrant clipping. Boundary segments remain, removed segments do not reconnect.
- Grid points are included in spatial-cache/morph preflight. Active high-degree grids trigger a sparse notice; filled surface does not allocate inactive graticules. Changing spacing leaves bundle hashes and scientific mesh/bases intact.
- Animated GLB emits line and filled-section primitives with shared attributes/morph targets and one weight animation, avoiding buffer duplication. Existing non-keyframe reconstruction verifies temporal interpolation against the physical field. Original material-side ranges and static color policy remain recorded.
- Scientific images resolve explicit flags over fully resolved saved ExportSpec image keys over800×500 operation defaults. A minimal saved GIF specification therefore supplies1200×900, as frozen. Explicit probe640×480/transparency/no-annotation wins. Inherited movie settings do not leak into scientific plots, and explicit movie-only flags are rejected.
- CSV/table output ignores irrelevant inherited production settings and rejects explicit image-only choices. The overwrite counterexample preserves the existing CSV after rejection. Maintained annotation_language is English, and generator version/filled-section policy are in manifests.

## Limits and disposition

This review did not rerun unrelated solver benchmarks, browser lifecycle tests or external editor installations. Static GLB colors and deliberate unsupported-overlay omissions remain documented limitations, not new defects. Hidden-shell scientific samples intentionally remain allocated for node/picking/clipping diagnostics.

Both findings were sent to the lead and package owner with their actual artifacts. At report creation they were pending repair; this report does not claim their fixes, a closed integration round or release completion.
