# Planning round 3: pre-freeze contract and delivery review

Historical record. Reviewed PLAN/CONTRACT v0.4, ACCEPTANCE, WORKFLOWS, PLAN-REVIEW-LOG, and read-only README, pyproject, and vendor license records. No feature was run or implemented in this review.

## Verdict

**The plan could be frozen.** Scientific and cross-module blockers from rounds 1 and 2 had explicit feasible resolutions. No new architecture or broad fourth planning round was warranted. Three small interface/text synchronizations belonged in the freeze commit; the remaining work required implementation and actual evidence.

1. ProbeSpec.layer_id selected an interface side, but sample_probe lacked the corresponding argument. Add layer_id=None and pass it to field evaluation so direct Python probes and exported probes agree. No separate API is needed.
2. An introductory quality enum still omitted unconverged although the later normative structure included it. Update/delete the stale enum and assign export_probe and compare_bundles to their documented modules so agents do not choose incompatible locations.
3. README already said “frozen,” inconsistent with the current third-review status. Synchronize v1.0 at the freeze. Before release, connect development setup to the final public WORKFLOWS commands and state FFmpeg/Blender boundaries. The then-placeholder CLI was not evidence of implementation failure during a planning review.

## Simulated installation-to-artifact path

| Step | Planned connection | Review result |
|---|---|---|
| Install core | pyproject package/terra entry point and vendored assets | Sufficient architecture; D1 must install a built wheel outside the repository, not just use editable installation. PREM, JCS, palettes, and coastlines must actually be packaged. |
| Write model | terra model prem/homogeneous → Model JSON | SI, phase, Q, reference frequency, and no-ocean/isotropic/3 mHz limitations are explicit. |
| Modify material and solve | Model + SolveSpec → canonical bundle | Requested/effective settings are separate; linear Q does not mutate the input; failed groups do not become ordinary partial bundles; prior artifacts remain protected. |
| Inspect quality | terra inspect → groups/per-mode evidence | Legitimate empty, unverified, unconverged, and independently checked frequencies are distinguishable without extending claims to eigenfunctions. |
| Build scene | default_scene → bundle hash → SceneSpec | JCS projection and all unknown subtrees are constrained; failed imports retain state; cross-model superposition is not ambiguous. |
| Evaluate field | Canonical U/V/W → real vector harmonics → fixed illustration scale → display gain | Basis, poles, center, interface sides, color, Q, and physical time can be shared; Python/TS fixtures have independent foundations. |
| Probe/compare | ProbeSpec/explicit mode pairs → tables or curves | Scientific and display quantities are separated; add the layer_id parameter above, then implement directly. |
| Static/video export | Preflight → temporary media/manifest → commit | PNG/GIF/MP4 retain agreed effects; dependency checks and paired rollback are feasible without a job database. |
| 3D animation | GLB morphs → independent non-key-time readback | Geometry and frozen scientific-color limitations are explicit; unsupported arrows/coastlines require explicit omissions; unavailable Blender does not imply verified .blend output. |
| Reproduce | Self-contained project or bundle/scene/manifest | Artifact hashes identify saved content; numerical reruns use tolerances rather than cross-platform bitwise identity. |

## Center correction

Exact-center support is correct and simpler. In this real unit-vector harmonic convention, S1 with v0=sqrt(2)*u0 combines to fixed Cartesian directions z/-x/-y for the three m values. Regular R/T/l>1 center values are zero. The 1e-6*mode_scale tolerance checks endpoint consistency; it is not an error promise for the entire near-center field. Implementation still needs multidirectional near-center checks and provenance for upstream corrections. No scientific reason remains for a central hole.

## Hash and failure paths

- Model hash includes id/name and removes only top-level provenance; bundle hash covers the complete validated canonical bundle. External conversion creates a new bundle before binding a scene, without a circular dependency.
- Scientific arrays and unknown provenance share I-JSON/JCS rules and rejection fixtures. Renaming changes identity by explicit choice, not implementation accident.
- Significant retained unstable spectrum stops solving; memory preflight occurs early; all-fluid T is not_applicable. Failed groups cannot masquerade as successful empty results.
- Generate media and manifests together temporarily, then roll back a failed commit; frame directories commit as a unit. Ctrl-C preserves prior outputs. Necessary recovery logic does not require a broader transaction framework.

## Packaging and licensing release gates

pyproject selected GPL-3.0-or-later; vendor retained GPL v3 text, pinned commit, and patches. The plan did not relicense upstream work. Distribution retains upstream copyright/license, the project's own license, and modifications. Natural Earth, palettes, and other assets retain their sources, actual versions, and licenses. These are concrete packaging requirements, not reasons to change the dependency strategy.

D1/D2 must inspect real wheel/sdist contents: repository LICENSE/examples do not imply installed resources. Python JCS must be a declared dependency, its frontend counterpart locked, and no machine paths introduced. Remaining pyproject/README gaps were implementation tasks, not completed planning-stage evidence.

## Execution risks retained without expanding planning

Independent PREM/MINEOS benchmarks, six topologies, mass conversion, executable linear Q, poles/center, and GLB interpolation still required actual results. The acceptance matrix assigned each a path and failure response. If evidence contradicted a core promise, fix or explicitly reopen that specific scope; do not preemptively add abstractions.

After the three small synchronizations, the reviewer supported freezing v1.0 and resuming assigned implementation. Planning reviews and the three later implementation reviews were separate accounting; this verdict certified no unexecuted feature.
