# Sufficiency roadmap — root agent's counterargument

Historical planning record. In addition to the independent reports, the root agent documented the cost and boundaries of proposed additions. This draft did not automatically accept every suggestion for delivery.

## New features are not free

Nodes, material-point trajectories, and presentation layouts need no new solver, but they affect saved scenes, legends, cutaways, PNG/video, and format differences. Website-only buttons would recreate delivery gaps that earlier reviews removed. Including them in the current release must also include persistence, exports, and necessary independent checks.

The proposed minimal boundaries were:

- Nodes are the spatial zero set of one signed component of one real-basis mode. Support lines on the surface and the two existing radial sections, plus radial-function zero crossings. Do not add vector-zero classification, permanent multimode nodes, or arbitrary 3D isosurfaces.
- Trajectories are x0+u(x0,t) at a few fixed material locations over an explicit physical interval. The proposal allowed one default point and at most three. They are not velocity integration or Eulerian streamlines and need no new particle backend.
- If GLB cannot retain the same node/trajectory animation, disclose that before export and require an explicit geometry-output choice; never silently discard it. PNG/video should retain it.
- Presentation mode changes layout only, never scientific data or SceneSpec; no extra schema field is necessary.
- Presets are static questions plus genuine project assets, without completion tracking, narrative interpreters, or teaching scores.

## Keep clocks and state simple

A trajectory window must not create a second player. SceneSpec retains one current physical time; the trajectory interval is saved as a static visible object, and the current marker uses the same time_s. ProbeSpec describes an exported time series. Share MaterialPoint coordinates and interface-side rules rather than creating another latitude/longitude convention.

ExportSpec contains reproducible production settings only. Do not add ExportPreset inheritance, JobSpec, or ProfileRegistry simultaneously. Paths, overwrite, process priority, and machine resources belong to execution. Existing focused functions can accept and resolve this small object without a dependency-injection framework.

## Describe initial sensitivity work accurately

One finite-difference recipe can demonstrate research use; it is not a sensitivity-kernel system or automatic inversion. First verify the uniform solid sphere's shear-speed scaling through delta f/f, then offer a reproducible layered-parameter experiment. Mode pairing must be explicit, and comparison plots must not hide quality or whole-mode sign conventions. A batch-experiment database is unnecessary.

## Avoid unnecessary sequential dependencies

- Sonification, batches of figures, scene bookmarks, and external data import can proceed independently on a trustworthy baseline, without waiting for source or rotation physics.
- A formal MINEOS adapter need not wait for sensitivity kernels; the two can proceed in parallel.
- Radial anisotropy need not wait for 3D anisotropy; a selected reliable backend can first support a more complete 1D model.
- New physics can initially arrive through independently validated external results rather than a native solver, but import support and package solving capability must be labeled separately.

## When planning should end

Once each addition has clear value, scope, and an existing contract connection; the four task types have complete cases; the roadmap has dependencies and evidence gates; and independent counter-review finds no strategic blocker, produce a readable plan summary. Next validate these assumptions with vertical implementation slices rather than endlessly adding features or documents. If implementation disproves a mathematical or product assumption, reopen that specific decision with a record; a frozen plan is not a reason to reject improvements.
