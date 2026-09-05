# Phase 2 planning, round 3: final contract readiness

Reviewed the overriding round-3 revision in `PHASE-2.md`, the root's round-2 integration review, and `phase-2-ownership.json`. This review changes no implementation. **Verdict: ready to freeze and implement.** The substantive round-2 blockers have been resolved; two small wording/ownership clarifications below should be incorporated during the freeze, without another planning cycle.

## Counterexample checks

**Version and legacy appearance.** The explicit table distinguishes unchanged 1.0 data from the intentional filled-section renderer correction. A 1.0 scene with non-null spacing fails; a 1.1 scene without spacing fails; ordinary edits do not upgrade old scenes. Project 1.0 containing Scene 1.1 is coherent because the wrapper and scientific bundle shapes are unchanged. The implementation must separate their version constants, but this is an assigned task rather than an unresolved design choice. Old readers reject the new scene instead of accepting an ignored appearance field.

**Grid alignment and sparse high-degree motion.** Every allowed spacing divides 90 degrees. The sampling count `n=max(32/48/96,4*(l_max+1))` is divisible by four, so the parallel longitude samples also include the removed quadrant's boundaries. Midpoint-based segment removal is consequently well defined for this specific fixed quadrant; it would not automatically generalize to arbitrary cut planes. Curves must be clipped in undeformed material coordinates once, not according to their deformed positions every frame. Retaining boundary curves, suppressing polar parallels, and avoiding the duplicate 360-degree meridian give a deterministic recipe. The sparse-grid warning honestly distinguishes missing extrema between curves from inaccurate field evaluation along a curve; no extra density control is needed.

**Resource feasibility.** At l=64, n=260, the unclipped recipe allocates `(180/d−1)*(2n+1)+(360/d)*(n+1)` curve points: 37,027 / 18,253 / 11,995 / 5,737 for 5 / 10 / 15 / 30 degrees. At 32 terms these alone use approximately 27.12 / 13.37 / 8.79 / 4.20 MiB of float64 spatial cache. This is bounded but material when added to scientific triangulation and overlays. The plan correctly requires aggregate preflight and permits rejection of combinations that exceed existing limits. A valid spacing is not a promise that every degree/term/overlay combination fits. Both GLB exporters must count every animated primitive's vertices and weight tracks; validating only the original triangle mesh would violate the frozen contract.

**Scientific-image precedence.** The explicit partial-ExportSpec example now removes the Python/browser ambiguity: a present `{format:"gif"}` resolves to 1200×900 before selecting image keys, while no saved ExportSpec retains the operation's 800×500 default. Explicit dimensions win; inherited movie settings are discarded, explicit inapplicable settings fail. Probe physical sampling remains independent. This is executable without a new configuration language or facade.

**Installed examples.** Ordered IDs, fresh validated projects, one bundle/catalog resource pair, and clear unknown-ID errors close the standalone path. New assets deliberately use Scene 1.1; arbitrary imported teaching remains verbatim. The generator/resource/API/CLI dependencies have unique owners and readiness handoffs, so the package can be integrated before its final wheel smoke.

## Two minimal freeze clarifications

1. State explicitly that cut-segment classification uses **undeformed material coordinates**, and that the grid is active only when `surface='wireframe'`. Its saved spacing may remain present while a filled surface is selected, but it must not allocate a hidden grid or generate sparse-grid notices in that mode. This is the natural reading of the plan; writing it down prevents an avoidable interpretation difference.
2. The numerical pilot says “package-installed Python example,” but its assigned example file is `examples/own_toroidal.py`, a source-distribution file rather than an installed wheel module. Define acceptance as an English documented snippet importing the installed experimental API from any working directory, or place the runnable example in the package deliberately. The documented snippet is sufficient; no additional CLI/backend selector is needed. Assign any shared example recipe/readback adjustments to the package reviewer if the new multi-primitive GLB representation affects them. Root still owns release version integration and final asset synchronization.

The ownership JSON contains 36 existing documentation paths, each exactly once, with no missing file. `CONTRACT.md` is explicitly assigned outside that translated-file list. CLI has one writer; the example API and lesson resources have another with a clear handoff. This avoids the previous shared-file ambiguity. Translation effort is substantial but acknowledged; it should be completed in the assigned files, preserving adverse findings and their historical status, rather than replaced by another scope expansion.

## Keep / change / remove / add

- **Keep:** the numerical baseline, separate scene version, four spacing choices, scientific cut-face triangulation, English canonical artifacts, package example API, and isolated experimental numerical slice.
- **Change:** only the two clarifications above and the implementations already assigned by the revised plan.
- **Remove:** nothing further. The rejected project wizard, backend registry, wholesale solver rewrite, and extra resource flags should remain outside this phase.
- **Add:** no new feature category or test framework. Use the planned legacy/new-scene checks, one sparse high-degree non-key GLB reconstruction including a filled cut face, one aggregate-budget failure, image-precedence checks, and one clean installed-package workflow.

The three planning rounds have made substantive sequential revisions. There is no remaining contract blocker that justifies delaying implementation or reopening general product strategy.
