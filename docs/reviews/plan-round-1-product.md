# Planning round 1: workflows and output fidelity

Historical review of PLAN v0.2 and the draft v1 CONTRACT. Implementation was paused; the export module was an untested feasibility draft. This review sought verifiable promises across renderers and formats, rather than additional features.

## Required before freeze

### P1: “The same scene” lacks a rendering contract

Camera azimuth, elevation and distance do not specify projection, target, units or axis conversion. A renderer could interpret distance as perspective distance while another uses orthographic zoom. GLB support for geography, arrows, reference geometry and cutaways is also undefined.

Define an origin target, z-up, azimuth from +x toward +y, elevation from the equator and one orthographic scale formula. Publish a capability table for browser rendering, offline images/video, scientific SVG, GLB and CSV. Promise matching physical fields/times and comparable composition, without claiming pixel identity. Unsupported layers must be rejected before export or explicitly omitted by the request, rather than disclosed only afterward. Browser automation need not become an export dependency. GLB can promise geometry, static colors, reference geometry and deformation without animated color support.

### P1: Colors, arrows and sampling are not reproducible

A “safe angular bound” is not an algorithm. A descriptive palette and unspecified arrow scale permit inconsistent visual intensity across Python and TypeScript. The plan promises quality controls without a contract field.

Specify a shared color-limit formula, fixed RGB tables and indexing, magnitude limits starting at zero, and symmetric signed limits. Define arrows as displacement multiplied by a fixed documented display gain. Separate display quality from solver accuracy, using a few presets and a degree-dependent sampling floor. Two palettes and explicit limits are sufficient; a transfer-function editor is unnecessary.

### P1: Saved scenes cannot identify their data reliably

A model ID is insufficient: different bundles can reuse model and mode IDs. A provenance sidecar records an export but cannot prevent a later scene from loading the wrong data.

Bind scenes to a bundle content hash and verify it on loading. Prefer one self-contained project containing bundle and scene. Define canonical hashing precisely across Python and JavaScript, and record input hashes and solver settings in export provenance. No database or resource-discovery service is needed.

### P1: Raw fields and normalized illustrations can be confused

Dividing every mode by its own display scale changes relative weights. Scene amplitudes therefore represent mode-shape illustration coefficients, rather than original orthogonal expansion coefficients.

State that the UI and default scene probes use illustration units. Provide an explicit `normalized=False` scientific API/CLI route, report normalization and divisors, and avoid labelling arbitrary CSV values as metres. This does not require a moment-tensor excitation model.

### P1: Animation timing lacks endpoint and aliasing rules

Frame-count rounding, physical time mapping, GIF quantization and GLB interpolation accuracy are unspecified. An eight-second period selected from the first mode can alias faster superposed modes.

Define playback duration and frame times `t_k=t0+k*time_scale/fps` on a half-open interval. GLB includes an endpoint keyframe and declares linear interpolation accuracy. Check the fastest active frequency; a possible policy is warning below 12 frames per period and rejection below two unless a documented explicit override exists. Do not promise seamless loops for damping or incommensurate frequencies. Specify GIF-compatible frame rates; 20 fps is a useful default, with MP4 for longer sequences. No common-period solver is needed.

### P1: Editable GLB animation needs independent evidence

Morph-target presence does not verify indices, target order, topology, timing or weights. Shader displacement does not automatically become glTF geometry.

Independently reconstruct exported vertices at at least three nontrivial non-keyframe times and compare them with the field evaluator. Check indices, target and weight counts, and units. Run Blender only if available; otherwise distinguish standard GLB validation from unperformed native Blender testing. Paired positive/negative targets can improve weight compatibility, but 32 terms imply up to 64 targets and require a resource limit.

## Workflow and scope changes

- **P2, geography:** choose a specific offline, licensed resource and verify longitude/latitude mapping. Keep geographic reference independent from a reliable grid. Document any backend differences before export.
- **P2, executable journeys:** provide commands/examples for teaching (real S/T/R example, scales, phase/cutaway, saved project, GIF), research (custom layered model, solve quality, eigenfunctions, raw CSV and scientific SVG), and production (saved scene, MP4/GLB, recovery of physical time and scale). Do not add inactive website solve controls if solving is an API/CLI capability.
- **P2, bounded richness:** retain surface/wire/reference/arrows/cutaway/shell views, superposition, U/V/W curves, frequency lists, probes, density/Vp/Vs profiles and exports. At this review stage, nodes, trajectories, parallel views and 3D potential coloring were proposed for later work. Subsequent strategy review reconsidered nodes and trajectories; this is a historical recommendation, not the final scope.
- **P2, resource preflight:** estimate vertices × targets, frames × pixels and frame-directory storage before allocation. Set explicit limits, write temporary artifacts, publish only after success, and prevent mixing old and new frame sequences. A background-job framework is unnecessary.

## Conclusion

Keep the overall architecture, but resolve the six P1 findings before freeze. Most fixes define existing fields and evidence rather than introduce subsystems. The next round should challenge the revisions and their state/compatibility cost instead of repeating these findings.
