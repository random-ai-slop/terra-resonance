# Counterreview of product additions and the longer-term route

Historical review of STRATEGY, ROADMAP and `reviews/strategy-decisions`, assuming few maintainers. Every addition carries browser, offline, storage and scientific-explanation costs. This review challenged the author's own earlier proposals rather than accepting them because they appeared in research.

## Conclusion at the time

Retain six questions, presentation mode, a linked material point, one trajectory and narrowly defined component nodes. The claim that these are all tiny uses of evaluate_field underestimated state/output work. **Reduce the mandatory count from three points to one; three becomes optional rather than an acceptance blocker.** Keep a small ExportSpec but remove duplicated aspect and a second time interval. Retain the material perturbation as a script/data/report, not a special UI.

After the output boundaries and state below are fixed, planning is sufficient for a real vertical slice. Educational benefit remains a hypothesis to inspect in use, not a fact established by more planning rounds.

## 1. Three material points and all-output trajectories hide costs

One point explains a real mode's line, a suitable quadrature ellipse and pattern versus material motion. Additional points bring management, selection, colors, legends, output collisions, material-side controls and occlusion; they are not merely two more field calls.

Require one selectable/locatable point, marker, three-component trace and trajectory. Extend later if copying points within a project proves useful. Existing side-specific probes and regional curves can compare interface sides sequentially; the six lessons should not require multipoint UI. If section picking is difficult, shell picking plus numeric section positioning is acceptable provided both drive the same marker. CLI probes alone are not the linked experience.

A trajectory is `x0 + deformation*u(x0,t)`, never feedback of the displaced coordinate into the field or integration of displacement. An independently magnified local plot must label displacement coordinates. Save a fixed trajectory window; rolling it every video frame would show a different curve while incorrectly calling it one-period motion.

## 2. Keep node semantics narrow

A component zero line of one real basis is useful; general vector zeros are more complicated. A selected shell can itself lie on a radial component node, making the entire shell zero. T radial zero is only one example. Near-zero mesh values can also generate false marching-triangle networks.

Require exactly one active nonzero real term and a signed radial/theta/phi component. Remove time and overall coefficient factors. Magnitude has no signed node line. Detect effectively zero/unresolvable domains using a mode-scale-related threshold and explain them rather than drawing a network. Radial curve zero crossings must not bridge discontinuities.

Captions/manifests must retain component, domain, term identity, threshold/sampling and spatial-eigenfield meaning. Do not rely on a UI disclaimer that disappears in export. Omit multimode instantaneous contours from baseline to avoid introducing permanent-node and dynamic-cancellation semantics simultaneously.

## 3. State the new output boundary explicitly

| Output | Required | Allowed limit |
| --- | --- | --- |
| Browser and PNG/GIF/MP4 | Same material point, fixed-window trajectory, nodes, meaning, position and gains | Antialias/line-width differences; not pixel identity |
| Scientific SVG/CSV | Probe/trajectory samples and radial zeros with window/units/regions | Not a complete 3D projected scene |
| GLB | Core deformation remains complete; unsupported enabled nodes/trajectory must be explicitly omitted before export | One `omit_analysis_overlays` flag covers point/trajectory/nodes with itemized metadata, not three extra flags |

Moving material nodes require their own morph bases; a fixed-window trajectory and moving marker require different animation treatment. Baking all these into baseline GLB solely for format completeness is not justified. Explicit limits preserve production value because image/video retain explanation while GLB carries editable core motion and reproducible inputs.

Budget overlays too: one trajectory, at most 2048 samples, and node geometry bounded by the display mesh. A bounded sphere with unbounded overlays is not a bounded renderer.

## 4. Keep state responsibilities small

- MaterialPoint stores the material position and optional layer side. Boundary side is coordinate semantics, not only a probe-export flag.
- Scene stores the selected point and visibility. Nodes need enable/component; identity follows the single active term rather than duplicating mode/m/phase.
- Probe/trajectory sampling can share a compact time-window shape and the same position definition. Resolve complete positions/windows in outputs rather than requiring many tiny referenced files.
- Trajectory has a fixed sampling window; its current marker uses scene time. It is not a second playback clock. A marker outside the saved window needs clear behavior rather than a silently rolling window.
- ExportSpec stores format, width/height, duration/fps, transparency/annotations and omissions. Start time stays in Scene; probe windows stay in Probe. Actual keys/divisors belong in manifests, not duplicated user state.

Remove aspect: width/height already determine image and GLB camera ratio. Derived rates, intervals, refinement and budgets belong in effective metadata without overwriting original user choices. Remove ambiguous quality overrides; use scene.quality and let a user copy a scene for high-quality output rather than create hidden precedence.

## 5. Keep questions and presentation compact

Six questions are useful and maintainable as regression cases, not six pages/components. Each has one project, at most three steps, a caution and scientific evidence. Multiple n/l/m states can be complete bookmarks, not an implicit-patch narrative machine.

Presentation mode hides editors but retains scientific legends, controls and keyboard use. It needs no second theme system and is not ModeBundle data. Scale captions with output size so readable presentation does not coexist with tiny PNG text.

Without human research, do not claim measured understanding gains. The gate is an independent reviewer completing actions and checking statements from the correct field without the implementer explaining everything live.

## 6. Preserve a small material-perturbation research entry

The recipe answers what to inspect after changing a model. Its minimum is baseline/±perturbations, two step sizes, explicit pairs, Δf/f and curves. Uniform shear-speed T scaling has an independent relation and is a suitable first case.

Do not add a sweep UI, database, automatic tracking or sensitivity map. If complex Earth pairing is ambiguous, use a clearly interpretable example instead of silently matching by n to keep a demonstration smooth. The recipe is baseline research evidence; a mature sensitivity platform is later work.

## 7. Four user tasks are complete

Research has material changes, solves, quality, fields, interfaces/radial analysis, comparisons, perturbations and raw outputs, while remaining a mode-structure tool rather than a full earthquake-analysis platform. Informed outreach gains pattern/material/signal relationships through six questions, a point, trajectory and nodes. Teaching has controllable state, phase/bookmarks/presentation and portable projects without a long-story editor. Production has composition, transparent/annotated stills, deterministic media, data and editable core GLB.

Therefore deferring dual viewports, event excitation, observations and advanced physics does not empty the current positioning. Research cannot be stretched to mean every possible seismology workflow.

## 8. Remove an unnecessary long dependency

ROADMAP C's dependency on “A/B reliable normalized eigenfunctions, spatial derivatives, raw adapters and identity” could be read as requiring all of B—external MINEOS adaptation, radial anisotropy and mature material kernels—before any source/station example.

Use capability dependencies instead: validated canonical eigenfunctions, needed derivatives/source coupling, receivers and units/response chain. **C does not require all of B, mature kernels or anisotropy.** A traceable processed observational spectrum can also enter teaching as observation material before a complete source pipeline, provided no quantitative match to hand-tuned coefficients is claimed.

External catalogs/sensitivity and a bounded independently referenced source/station case can progress in parallel. Useful teaching/production changes need not wait for frontier numerical stages D/E.

## Sufficiency

The route has sufficient product value and implementation bounds after these reductions. One point rather than mandatory three, single-term component nodes and an ExportSpec without duplicate time/aspect/quality genuinely control maintenance cost without postponing the core task.

The next useful evidence is a real R/S/T slice: select point → inspect trajectory/trace → explain zeros → save → read PNG/short media. If that is unclear, improve the actual interface; another ideal-feature list will not fix it.
