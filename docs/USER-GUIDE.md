# User guide

Install the Python package as described in the root README. Commands below use `terra` from that environment and work outside the repository. The browser and offline renderers share scientific fields, orthographic camera conventions and fixed color limits; antialiasing and text layout can differ.

## Choose a scientific question

```sh
terra example --list
terra example 03-indices --out lesson.json
terra export lesson.json --out lesson.png
```

The six examples cover a breathing sphere, tangential motion, n/l/m, both sides of the liquid-core boundary, traveling patterns and beats at a fixed point. Each is a complete editable project. Pause and compare two physical times before changing a parameter; lesson animation is not separate from its scientific scene.

The solver's n labels radial branches, while l controls angular degree. In a spherical model, m selects a degenerate real cosine/sine basis without changing frequency. Changing n or l selects another eigenmode. The branch label n is not necessarily the zero count of every radial component in a layered model.

A material trajectory is the undeformed position plus the analytic displacement at that fixed material coordinate. It is not a numerical integration of velocity and does not follow a moving wave crest. Its physical window is saved independently of the current marker time.

Component node lines are available for one active real basis with a signed component. The global time factor is removed before extracting spatial zeros. An instant of zero displacement does not make the whole sphere a node. Identically zero components receive an explanation; magnitude has no signed node lines. Sections preserve active eigenfunction source knots and both material sides, including at high radial order.

## Research: material, solution and evidence

Start with a sourced Model, change its material profiles, then solve it:

```sh
terra model prem --out prem-model.json
terra solve prem-model.json --families R S T --l-max 4 --f-max-mhz 3 --mesh 140 --gravity 2 --convergence-check --out recomputed.json
terra inspect recomputed.json
terra inspect recomputed.json --details
```

For an inexpensive first calculation, use `model homogeneous` and `--families T --l-min 2 --l-max 2 --gravity 0 --mesh 24`. Installed PREM lessons require no recomputation. Mesh convergence approximately doubles the grid and records frequency changes; it also increases cost.

Quality states `unverified`, `unconverged`, `converged` and `benchmark_checked` describe different evidence. Mesh convergence does not substitute for an independent benchmark, and frequency agreement does not establish equal accuracy for every observable. Default `inspect` retains important warnings; `--details` and `--json` expose full provenance. Custom models do not inherit the default PREM benchmark status.

A solve config uses Python/SI units. Explicit CLI flags override its values:

```json
{"families":["T"],"l_min":2,"l_max":2,"gravity":0,"mesh_size":48,"frequency_min_hz":0.00005,"frequency_max_hz":0.003,"convergence_check":true}
```

```sh
terra solve prem-model.json --config solve.json --out toroidal.json
```

Gravity 0 is purely elastic; 1 retains background gravity; 2 includes its perturbation. Experimental `--linear-q --target-mhz 1` requires material Q and `reference_frequency_hz`. Omitted Q means unspecified, whereas an array entry of null means infinite Q. No Earth attenuation profile is guessed. Fluids have zero shear speed and no elastic T modes; nonapplicable groups are explicit.

Changing labels or material arrays in a solved bundle is not a valid model update. Recompute from the Model input and create a scene bound to the new result.

## Compare separate models

```sh
terra compare reference.json candidate.json --family S --l 2 --n 0 --out comparison.svg
```

Automatic suggestions require matching family/l/n and solid-domain identity. Explicit `--reference-mode ID --candidate-mode ID` permits a researcher-selected pair with different labels; do not combine those flags with family/l/n. The report preserves both identities and does not claim physical mode tracking. Near crossings or degeneracy, identical labels do not prove continuity.

Comparison curves retain each model's own r/R, canonical mass normalization and original sign. Frequency difference means candidate minus reference. An overall eigenvector sign is arbitrary. Separate-model comparison never enters a single physical scene superposition.

The source recipe `examples/perturb_model.py` compares h, h/2 and two grids against the analytic T-mode frequency scaling with shear speed. See the [recipes](../examples/recipes/README.md). It is a bounded research example, not a verified general inversion kernel.

## Save and restore a teaching scene

A project contains its bundle and scene and may include independent probe/export settings and teaching metadata. Hash validation binds the scene to the entire scientific bundle. Invalid imports preserve the current valid project.

```sh
terra scene recomputed.json --mode-id S0_2 --m 0 --out scene.json
terra export recomputed.json scene.json --out earth.png
```

Edit the SceneSpec JSON to change display settings. Invalid values fail explicitly. `radius_fraction` selects an r/R shell; disable geography before entering an internal shell because coastlines are material surface references. Cutaway removes the fixed x>0, y<0 quadrant and creates two actual radial sections. Choose a camera on the cut side to see them.

The camera looks at the center, with z north. Azimuth increases from +x toward +y; elevation is measured above the equator. `camera.distance` is the visible vertical span in planetary radii, not a perspective focal length. Dark ink blue supports screen presentation; `background="light"` supports light publication layouts.

`deformation` is geometric gain, `arrow_scale` controls arrows independently, `color_limit` is fixed throughout the animation, and `time_scale` converts playback seconds to physical seconds. These settings do not change eigenfrequencies. T displacement is orthogonal to the radius at first order, but exaggerated Cartesian addition can create a second-order apparent radius change.

### Surface grids and compatibility

New SceneSpec 1.1 scenes contain `wireframe_spacing_deg`, set to 15 by default. Values 5/10/15/30 select a material latitude/longitude grid; null selects legacy triangle wires. The field-sampling quality remains independent. A sparse visual grid cannot display every extremum between its lines; use a filled surface or smaller spacing when needed. Grid curves are sampled from the same field, not coarse chords used as a substitute for scientific sampling.

The setting persists while the surface is solid and activates only for wireframe rendering. Cut faces remain filled in every renderer, retaining source knots and interfaces. Changing grid density does not alter probes, nodes, normalization or the bundle hash. Display geometry and morph targets remain subject to resource preflight.

SceneSpec 1.0 accepts absent/null spacing and preserves that input on passive load/save. A non-null spacing requires an explicit upgrade to 1.1. Changing website language does not upgrade a scene. The new renderer corrects filled cut faces even for 1.0 scenes; preservation of scientific input is not a pixel-identical replay promise. Bundle and Project versions remain 1.0.

## Fixed-point time series

```sh
terra probe lesson.json --out displacement.csv
terra probe lesson.json --lat 35 --lon 105 --start 100 --duration 7200 --step 5 --raw --derivative 1 --out velocity.svg --width 1000 --height 600
```

Latitude is geographic, longitude is east-positive, and `--radius` is r/R with default 1. At an interface, `--layer-id` selects the material side; the default is the outer side. Cartesian x points to equatorial longitude 0, y to 90° east, z north.

A saved ProbeSpec is independent of the 3D material point unless explicit UI linking is enabled. Reusing a project preserves its exact step, start, count, derivative and normalization. If creating a new time window, samples occupy `[start,start+duration)` and do not add a duplicate endpoint. Supply duration when changing a step to state the intended window.

Default illustration displacement is dimensionless; its derivatives have units s^-1 and s^-2. `--raw` uses kg^(-1/2) and its derivatives, not metres. Derivatives include the Q-envelope derivative. CSV, SVG and PNG sample the same physical field. Tiny steps that cannot advance the chosen floating-point time are rejected.

## Scientific images and production options

```sh
terra export lesson.json --kind eigenfunctions --out eigenfunctions.svg --width 1000 --height 600
terra export lesson.json --kind model --out material.svg
terra export lesson.json --kind frequencies --out frequencies.svg
terra export lesson.json --kind tables --out tables
terra export lesson.json --out earth.png --width 1600 --height 1200 --transparent
terra export lesson.json --out earth.gif --duration 8
terra export lesson.json --out earth.mp4 --duration 8 --fps 24
terra export lesson.json --kind frames --out frames --duration 8 --fps 24
terra export lesson.json --out earth.glb --duration 8 --omit-arrows --omit-geography --omit-analysis-overlays
```

For scientific images and probe plots, explicit width/height/transparency/annotation flags override resolved saved image settings, which override operation defaults. Without a project ExportSpec, scientific plots default to 800×500. If an ExportSpec exists, resolve its documented defaults first: even `{format:"gif"}` implies its 1200×900 image defaults. Inherited movie settings do not invalidate a scientific image, but explicit movie-only flags do. Tables/CSV ignore inherited image settings and reject explicit image-only flags.

GIF defaults to 20 fps and MP4 to 24 fps. GIF supports 1/2/4/5/10/20/25/50 fps, whose delays are exact multiples of 10 ms. Duration is playback time. Frame count is `floor(duration*fps+0.5)`, at least two, without an extra final frame. Multi-frequency or damped motion generally does not form a seamless loop.

GLB uses real morph targets and paired nonnegative weights with a recorded interpolation error limit, including its interval endpoint. Initial vertex colors are static. Dynamic geography, arrows, nodes and trajectories require explicit omission; the essential surface grid does not. Omissions affect the artifact, not the original project. The [Blender import recipe](../examples/recipes/README.md) needs a native Blender environment; independent GLB readback is not a substitute for that application test.

Browser PNG/SVG/GLB downloads use a ZIP containing media and provenance together. CLI outputs remain a media file and adjacent sidecar. English and Chinese website UI use English maintained artifact labels; imported model names and researcher metadata remain verbatim. SVG export uses the same numeric series as the visible chart without changing the UI language.

Use `--no-annotation` for a clean image while retaining scientific metadata. Transparency is supported only where the format permits it. Material tables include original `model.json` so absent and infinite Q remain distinguishable. Resource limits can be configured through the explicit Python API; there is no general CLI flag collection for every exporter limit.

## Website language

English is the initial default. The language selector updates the session, saved preference and `?lang=en|zh-CN` without navigation. A valid URL choice takes precedence over the saved preference; invalid values fall back safely. Storage failure must not prevent a session switch.

Locale affects interface text, accessibility, quality summaries and owned messages. It does not reload scientific data, reset playback/camera/probe settings or modify hashes. The six canonical English lessons have website-only Chinese translations. Recognition requires the matching catalog bundle hash, ID and complete teaching object; edited or historical imported teaching remains verbatim and is preserved on save.

## Failure recovery

| Message | Next action |
| --- | --- |
| Output exists | Choose another path or explicitly use `--overwrite`; controlled failure preserves the previous result. |
| Bundle hash mismatch | Load the matching bundle/project or create a new scene for changed data. |
| Invalid mode, m or material side | Check the identity, `-l <= m <= l` and the selected layer at that radius. |
| Missing Q/reference frequency | Supply physical inputs explicitly or disable experimental linear Q. |
| Temporal aliasing | Reduce playback gain or use an allowed higher frame rate; do not alter physical frequencies to hide it. |
| Vertex/cache budget exceeded | Reduce active terms or field-sampling quality. Source radial knots are not silently removed. |
| Solver memory limit | Reduce the grid or explicitly increase `--memory-mib` after checking available resources. |
| FFmpeg unavailable | Install it and check PATH; other output formats remain independent. |
| No matching mode | Check frequency units, n limits, family and solid domain; an empty catalog is not a successful image. |

Time, geometry and encoder preflight runs before expensive production. Media and sidecars are staged and verified before commit; controlled interruption removes temporary output. Multiple calls are not one global transaction, and power-loss recovery is not promised.
