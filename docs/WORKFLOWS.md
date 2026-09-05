# Package workflows and CLI

Terra provides one `terra` CLI, a Python API, and a website. The installed package works without the website, a source checkout, or a background service. Each command has `--help`; invalid requests return a nonzero exit code with a reason. Existing outputs require explicit `--overwrite`.

## Start from a maintained example

```sh
terra example --list
terra example 03-indices --out lesson.terra.json
terra inspect lesson.terra.json
terra export lesson.terra.json --out lesson.png
```

The six packaged examples are complete projects containing a shared real PREM bundle, a Scene, and teaching metadata. `terra example --out lesson.terra.json` selects `03-indices`. In Python, `list_examples()` and `load_example("03-indices")` are public APIs; every load returns an independent validated project. No repository-relative example path is required.

## Research model to visualization

```sh
terra model prem --out model.json
terra solve model.json --families R S T --l-max 8 --f-max-mhz 3 --mesh 280 --gravity 2 --out modes.json
terra solve model.json --config solve.json --out recomputed.json
terra inspect modes.json
terra scene modes.json --out scene.json
terra scene modes.json --wireframe-spacing-deg 15 --out grid.json
terra export modes.json scene.json --out mode.png
```

`model prem` records its isotropic, 3 mHz, ocean-free approximation and source. `model homogeneous` accepts explicit radius, density, Vp and Vs; `--vs 0` means a fluid sphere. Arbitrary connected material layers use the documented SI Model JSON rather than a separate model language.

Model properties, gravity, Q and numerical mesh are actual solver inputs. CLI frequency flags use mHz; the API uses Hz. `--n-max` is an explicit optional truncation. Experimental `--linear-q` requires material Q, the model reference frequency and an explicit `--target-mhz`; `--memory-mib` changes the solver budget. General solves do not acquire verified status merely by completing. Inspect the per-mode mesh and independent frequency evidence.

The website imports the resulting bundle. Changes to m, phase or presentation act immediately; material changes require a new solve. A failed solve or import does not replace previously valid data.

## Presentation, grids and saved projects

A Scene records terms, phases, radius, cutaway, arrows, geography, colors, playback time and display gains. Mode changes must keep m within the new degree. Seeking does not change the field normalization or color range. The physical time and playback multiplier remain distinct.

New scenes use Scene 1.1 with a 15-degree surface grid. `--wireframe-spacing-deg` accepts `5`, `10`, `15`, `30` or `legacy`. It changes visible latitude/longitude line spacing only when the saved Scene has `surface="wireframe"` (set through Python, JSON or the website). It does not change the solver mesh or the degree-aware curve sampling. Cutaway material faces stay filled. A coarse visible grid can hide extrema between lines; a warning reports this without silently adding lines. `legacy` preserves triangle-edge shell rendering. Scene 1.0 files remain readable without an implicit version upgrade.

Save a complete project to preserve bundle, Scene and optional ProbeSpec/ExportSpec with a content hash binding. A separate Scene needs its matching bundle. Import errors retain the current valid state and report the affected field. Interface preferences are not a substitute for a saved project.

## Scientific quantities and probes

```sh
terra probe modes.json scene.json --lat 35 --lon 105 --duration 7200 --step 5 --out probe.csv
terra probe modes.json scene.json --lat 35 --lon 105 --duration 7200 --step 5 --raw --derivative 1 --out raw-velocity.csv
terra export modes.json scene.json --kind eigenfunctions --out eigenfunctions.svg
terra export modes.json scene.json --kind model --out model.svg
terra export modes.json scene.json --kind tables --out tables/
terra compare reference.json candidate.json --family S --l 2 --n 0 --out comparison.svg
```

Probes use latitude and east longitude, with an optional radius and explicit material side. Headers describe Cartesian axes. Illustration displacement is dimensionless; its first and second time derivatives have units s^-1 and s^-2. `--raw` retains canonical mass-normalized coefficients in kg^-1/2 and their derivatives, not source-calibrated displacement in metres. It does not mean the unmodified upstream file. The resolved ProbeSpec and normalization are saved in the sidecar.

The default probe start is `scene.time_s`; `--start` overrides it. CLI duration and step define the half-open physical interval `[start,start+duration)`. Samples that round to the endpoint are excluded and the actual count is saved. Unresolvable floating-point steps fail instead of producing duplicate timestamps.

Scientific images default to 800×500 without a saved ExportSpec. If a project has ExportSpec, first resolve its defaults, then inherit width, height, transparency and annotations. Explicit image flags override those four values. Thus a saved partial `{"format":"gif"}` supplies 1200×900 to a scientific image, while its movie timing is irrelevant. CSV and tables ignore inherited image settings but reject explicit image flags, including `--no-annotation`. Explicit movie-only flags on scientific image operations are errors. Python `export_plot` and `export_probe` accept the same four image options directly.

Comparisons use explicit mode identities and solid-domain identity. Frequency differences and each model's normalization are visible; radial plots use each model's r/R. They do not physically superpose different models. Ambiguous or crossing modes require explicit IDs; automatic mode tracking is not claimed.

## Movies and editable 3D

```sh
terra export modes.json scene.json --out mode.gif --duration 8 --fps 20
terra export modes.json scene.json --out mode.mp4 --duration 8 --fps 24 --width 1200 --height 900
terra export modes.json scene.json --kind frames --out frames/ --duration 8 --fps 24
terra export modes.json scene.json --out geometry.glb --duration 8 --omit-arrows --omit-geography --omit-analysis-overlays
```

Duration here is playback duration; Scene controls conversion to physical time. Preflight checks sampling and resources before field allocation or encoding. `ExportLimits` is an offline Python API option, not a CLI flag. Explicit GLB omission options apply to that output only. Surface grid lines and filled sections are essential geometry and animate together. GLB colors are frozen at the export start; metadata records that limitation.

Each output carries a manifest with the Scene, provenance, bundle hash, actual production settings, sampling, software/encoder versions and declared differences. Source-package annotations are English; user-authored model names and metadata are preserved verbatim. A hash alone cannot recover a missing bundle: the complete project remains the reproducibility input.

The supplied Blender script imports GLB and configures timeline/camera. Native `.blend` execution is only claimed when actually run in Blender. Independent GLB readback and vertex reconstruction are separate checks.

## Necessary failure paths

- Unknown versions, invalid indices, nonpositive density or bulk modulus, inconsistent solid/fluid Vs and incomplete Q requests give field errors.
- Insufficient numerical resolution, excessive memory, an uncovered frequency range or an unstable spectrum are solver failures, not successful empty outputs.
- Hard display budgets and requests below temporal Nyquist fail explicitly. Sampling safeguards do not silently discard terms.
- Missing FFmpeg gives an actionable error; PNG, SVG, CSV and GLB remain usable.
- Existing targets are protected unless overwrite is explicit. Export transactions do not mix old frames into a new directory and roll back only outputs created by that transaction.

An experimental linear-Q request can be written as:

```json
{"families":["R","S","T"],"l_min":0,"l_max":3,"frequency_min_hz":0.00005,"frequency_max_hz":0.02,"mesh_size":160,"gravity":0,"n_max":null,"linear_q":true,"target_frequency_hz":0.001,"convergence_check":false,"memory_mib":512}
```

The Model must separately provide `reference_frequency_hz` (for example 0.01) and layer `q_bulk`/`q_shear`; the config cannot invent them. Material-point trajectories use undeformed coordinates and explicit physical intervals. Nodes are restricted to a single nonzero real term and a signed component. The project's sole playback time remains `scene.time_s`; ExportSpec stores production choices, not another scientific clock.
