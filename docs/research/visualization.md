# Visualization and export research

Historical research supplement to `docs/PLAN.md`; the subsequently frozen contract governs implementation. One scientific state should drive browser views, scientific plots and offline output, while display parameters leave mode data unchanged.

## References and scientific scope

[Saviot's Earth page](https://saviot.cnrs.fr/terre/index.en.html) offers S/T, whole/cut spheres, n/l/m and a second degenerate component. Shapes use a homogeneous isotropic elastic model, periods come from observations, amplitudes are greatly enlarged, and gravity/Coriolis terms are omitted. Direct retrieval was unreliable; verification here used the official page's search-index text, not pixel-level visual review. Bind frequencies, eigenfunctions, normalization and model together rather than mixing observed periods with unrelated illustrative shapes.

[Ouroboros](https://github.com/harrymd/Ouroboros) describes spherical models with arbitrary solid/fluid regions, R/S/T and self-gravity including Eulerian perturbations; rotation, nonspherical structure and anisotropy are excluded. Attenuation capability must be established from code and executed evidence, not inferred from the top-level README.

## Field and time conventions

The exchange contract should define the unit-sphere gradient explicitly:

```text
xi = U(r) Y_lm e_r + V(r) grad_Omega(Y_lm)
     + W(r) e_r cross grad_Omega(Y_lm)
u(x,t) = Re[sum_j a_j xi_j(x) exp(-i omega_j t)]
x_draw = x + displayScale * u(x,t)
```

Record any sqrt(l(l+1)) factors, Condon–Shortley phase, harmonic normalization, signed-m real-basis meaning and coordinate axes. Adapters convert upstream conventions; renderers must not guess. These were research notation proposals: where the frozen formula differs, the contract is authoritative.

Physical amplitude, geometric gain, arrow gain and color limits are separate. Without source calibration, use normalized displacement, not metres. Sum modes before a common display gain; per-frame normalization would hide beating and decay. Physical time determines the field, with an explicit playback conversion. Multifrequency sums are not presumed periodic.

Keep both interface samples and region IDs; interpolate within a region. Tangential displacement may jump and must not be smoothed across a fluid-solid interface. Distinguish an inapplicable elastic fluid T field from a numerical zero. Rendering and solver meshes have different roles. A component zero is not necessarily a zero of the entire vector field.

## Minimum state proposed at research time

| Area | Necessary content |
| --- | --- |
| Data binding | Schema version, bundle ID/hash and mode IDs |
| Superposition | m, real/complex convention, coefficients or amplitude/phase and activation |
| Time | Physical time, playback gain, export interval and frame rate |
| Presentation | Geometry/arrow gain, color variable/fixed range, layers and sampling quality |
| Space | Camera/projection, cuts, visible shell and selected receiver |
| Output | Dimensions, background, annotations, format and software version |

Scene data references real modes instead of duplicating frequencies. Camera/color edits do not solve again. Validate finite values, lengths, enums, ranges and bundle identity; unknown versions require actionable errors. The final architecture later separated SceneSpec, ProbeSpec and ExportSpec rather than putting every production field inside SceneSpec.

## Views and hierarchy

Useful views include displaced or neutral surfaces, material grids/wireframes, a reference sphere and optional geography. Radial motion is visible in shape; toroidal motion needs material grids and tangential arrows because a smooth silhouette alone is insufficient. Arrows must distinguish displacement from velocity.

Real radial sections show interior structure with regional sampling. U/V/W curves mark boundaries and may include available potential perturbations. Catalogs, dispersion and receiver traces support quantitative inspection. Material trajectories and model comparisons can reuse the same field/curve abstractions.

Use the plan's dark ink viewport, low-reflectance sphere and fine grid, with readable controls/legends. Light output supports print. Teal/amber encodes signed fields rather than simultaneously indicating layer categories. Diverging maps center on zero, magnitude uses ordered luminance and phase would require a cyclic map. Python and browser share sampled palettes, following [Matplotlib guidance](https://matplotlib.org/stable/users/explain/colors/colormaps.html). Fixed scales and signed contours also help grayscale reading.

Keep mode, true period, normalization and geometric/time gains visible; detailed physics may collapse. Hide meaningless m/tangential controls at l=0. Camera rotation must not be called rotational splitting in a nonrotating model.

## Minimum sufficient export workflow

1. Freeze a bundle/scene and record provenance.
2. Evaluate deterministic physical times instead of integrating a wall clock.
3. Use one time for stills; use `t_k=t_0+k*dt` for animation and avoid a duplicated final frame when looping a single mode.
4. Use PNG frames as an intermediate and FFmpeg for MP4/global-palette GIF, rather than scientific screen recording.
5. Bake real vertex displacement into GLB morph targets and sampled weight animation, with mesh/camera/material metadata for Blender.

| Output | Proposed commitment |
| --- | --- |
| PNG | 3D field, cutaway or scientific plot with explicit size/background/annotations |
| SVG | Scientific curves, section contours or simplified projected wires, not complete textured 3D vectors |
| CSV | Frequencies, eigenfunctions and receiver traces with units/normalization |
| MP4/GIF | Fixed samples, count/time metadata; GIF for short demonstrations, MP4 for longer animation |
| GLB | Editable deformation animation, not only static geometry; arbitrary shaders/dynamic colors are not automatically portable |
| Blender | GLB plus a real import script; native `.blend` generation requires an installed Blender |

[Three.js SVGRenderer](https://threejs.org/docs/pages/SVGRenderer.html) lacks textures, shadows and advanced shading, supporting a clear separation between scientific SVG and complete 3D PNG. [GLTFExporter](https://threejs.org/docs/pages/GLTFExporter.html) supports morph targets, animation and cameras. [Blender glTF documentation](https://docs.blender.org/manual/en/4.4/addons/import_export/scene_gltf2.html) describes shape-key animation import; arbitrary material/light animations do not automatically survive. Shader-only displacement is not automatically editable GLB. [FFmpeg filters](https://ffmpeg.org/ffmpeg-filters.html) document palettegen/paletteuse and frame-rate handling.

Default annotations state model, modes, period and gains. Clean output may hide annotations but preserves metadata. Do not call multifrequency or damped output seamlessly looping.

## Necessary acceptance

- Science: finite poles, known low-order harmonics, spherical l=0, radial-zero T, both interface sides and equal Python/TypeScript fields at equal phase.
- State: save/restore, invalid bundle binding, exact seeking and camera independence.
- Formats: readable PNG, actual SVG vectors, matching CSV, correct frame times/counts and genuine GLB morph animation.
- Interpretation: readable scientific scale, traceable exaggeration, no sampling-induced false nodes and visible T motion.

These cover scientific/format boundaries; small layout/color edits do not require piles of unit tests. At the time of this research, offline implementation was to wait for the lead's frozen data contract.
