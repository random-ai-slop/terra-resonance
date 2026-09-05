# Terra Resonance

[Interactive observatory](https://random-ai-slop.github.io/terra-resonance/) · [Release downloads](https://github.com/random-ai-slop/terra-resonance/releases) · [CI](https://github.com/random-ai-slop/terra-resonance/actions/workflows/ci.yml)

Normal-mode calculations and scientific visualization for spherically symmetric planets. The Python package computes modes, samples fields and exports reproducible artifacts. The optional English/Chinese website explores the same versioned data without a hidden Python service.

The 0.1.0 baseline completed three sequential implementation reviews. The 0.2.0 changes are tracked in [Phase 2](docs/PHASE-2.md); [Phase 3](docs/PHASE-3.md) tracks explicit toroidal agreement and its implementation audits. A plan is not an acceptance result. Scientific claims are bounded by the [numerical evidence](docs/validation/NUMERICS.md) and each mode's provenance.

## Start with the installed package

Python 3.11+ is required. From a source checkout or extracted source distribution:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install .
```

Alternatively download the wheel and `SHA256SUMS` from the GitHub release, verify its checksum and install the wheel with `python -m pip install path/to/terra_resonance-0.3.0-py3-none-any.whl`. The package is not currently published on PyPI. Activate that environment, then run these commands from any working directory:

```sh
terra example --list
terra example --out project.json
terra inspect project.json
terra export project.json --out earth.png
terra probe project.json --out probe.svg
```

The installed package contains one validated PREM bundle and six English lesson definitions. The default `03-indices` example includes its scientific data, SceneSpec, ProbeSpec, ExportSpec and teaching notes. No repository paths, browser or network are needed after installation. Existing outputs are protected; use a new path or explicit `--overwrite`.

```python
from earth_modes import list_examples, load_example, save_project
from earth_modes.export import export_image, export_probe

project = load_example("04-liquid-core")
export_image(project["bundle"], project["scene"], "core.png", width=960, height=720)
export_probe(project["bundle"], project["scene"], project["probe"], "core-probe.svg")
save_project(project, "core-project.json")
```

Each call to `load_example()` returns fresh editable data. The example frequencies and eigenfunctions come from a **PREM isotropic, no-ocean, 3 mHz approximation** with mesh and independent frequency evidence. They are not arbitrary shapes placed on an Earth texture.

## Compute a custom model

```sh
terra model homogeneous --radius 6371000 --rho 5515 --vp 10000 --vs 5500 --out model.json
terra solve model.json --families T --l-min 2 --l-max 2 --gravity 0 --mesh 48 --convergence-check --f-max-mhz 3 --out modes.json
terra inspect modes.json
terra scene modes.json --out scene.json
terra export modes.json scene.json --out toroidal.png
```

`model prem` writes the sourced PREM material profile; `homogeneous --vs 0` creates a fluid sphere. Modify a Model JSON and solve again to study different materials. Editing a solved bundle's labels or material arrays does not recompute its eigenmodes. Python frequencies use Hz; CLI frequency flags use mHz. There is no hidden mode-count limit when `--n-max` is omitted.

```python
from earth_modes import homogeneous_model, solve, default_scene, evaluate_field
from earth_modes.export import export_image

model = homogeneous_model()
bundle = solve(model, families=["T"], l_min=2, l_max=2,
               gravity=0, mesh_size=24, frequency_max_hz=0.003)
scene = default_scene(bundle)
scene["color"] = "magnitude"
point = [[0, 0.6 * model["radius_m"], 0.8 * model["radius_m"]]]
vector = evaluate_field(bundle, scene["terms"], point, time_s=100)
export_image(bundle, scene, "toroidal.png")
```

This uses fixed illustration normalization by default, not an earthquake-source-calibrated displacement in metres. A separate experimental `earth_modes.experimental.solve_toroidal` studies an independently assembled toroidal solver; it does not replace the default backend. See the [phase scope](docs/PHASE-2.md).

## Compare two toroidal computations

`earth_modes.agreement.toroidal_agreement` measures explicitly paired elastic T modes from two complete bundles of the same canonical model. It reports signed frequency change and a mass-weighted, globally sign-aligned radial-shape distance. JSON embeds both complete inputs; native SVG/PNG and scalar CSV retain a reloadable report sidecar. Code agreement and mesh refinement remain separate from independent accuracy evidence.

See the [agreement guide](docs/AGREEMENT.md) and [copied two-resolution recipe](examples/recipes/agreement.py) for standalone API/CLI use, independent Bessel frequency checks and received-sidecar re-export. The existing general comparison still supports separate models and unchanged raw curves.

## Artifacts and reproducibility

| Output | Meaning and boundary |
| --- | --- |
| PNG | Orthographic scientific field, cutaway or scientific plot; fixed color limits, dark/light or transparent output |
| SVG | Genuine vector scientific curves: eigenfunctions, material/frequency profiles, probes and comparisons |
| CSV | Frequencies, canonical U/V/W, available potential, material profiles and probes; original material JSON preserves omitted versus infinite Q |
| GIF / MP4 / PNG frames | Fixed physical sampling with explicit playback gain; no automatic seamless-loop claim |
| GLB | Editable morph targets, animated weights, static initial colors and an orthographic camera; unsupported dynamic overlays require explicit omission |
| Project JSON | Self-contained bundle + scene, with optional probe/export settings and preserved user metadata |
| Blender | A real GLB import script; native `.blend` execution requires Blender and was not verified in the baseline environment |

```sh
terra export project.json --kind eigenfunctions --out eigenfunctions.svg --width 1000 --height 600
terra export project.json --kind tables --out tables
terra export project.json --out earth.gif --duration 8
terra export project.json --out earth.mp4 --duration 8 --fps 24
terra export project.json --out earth.glb --duration 8 --omit-arrows --omit-geography --omit-analysis-overlays
```

GIF/MP4 require `ffmpeg` on PATH; the verification recipe also uses `ffprobe`. PNG, SVG, CSV and GLB do not require FFmpeg. Artifacts include sidecars with scientific hashes, inputs, actual production settings, display gains, versions and declared omissions. Save the project as well: a hash cannot reconstruct missing input data.

New SceneSpec 1.1 projects distinguish visible surface-grid spacing from field sampling. Spacing is 5/10/15/30 degrees or null for legacy triangle wires. Sparse grid lines do not change the field, probes or node extraction. Legacy SceneSpec 1.0 inputs retain their surface-wire interpretation; filled cut faces are a documented renderer correction. See the [contract](docs/CONTRACT.md).

## Optional website

Use the complete repository for the website; the Python source distribution is not a frontend distribution. Node.js 22.13+ is required. The public website can be built without a Sites account:

```sh
.venv/bin/python scripts/sync_web_assets.py
cd apps/web
npm ci
npm run build:pages
npx vite preview --outDir dist/client --base /terra-resonance/
```

Open the server address at `/terra-resonance/`. For the existing Sites development target, run `npm run dev`; it uses the retained hosting configuration. Import a project or bundle, explore modes, interfaces and material-point motion, then save the complete project. The website offers English and Chinese as presentation preferences. Switching language does not change scientific state or user metadata. Maintained downloaded annotations are English in either UI language. No online model/map downloads are needed after the bundled data have loaded.

## Scientific limits

The default solver supports spherical, nonrotating, isotropic elastic models with arbitrary solid/fluid regions, R/S/T families and three gravity levels. It preserves both material sides of interfaces and does not smooth tangential displacement across fluid-solid boundaries. Custom models produce inspectable discrete eigenmodes and quality evidence, not a uniform accuracy guarantee over every parameter range.

Linear Q is an experimental elastic-eigenfunction approximation requiring explicit material Q, reference frequency and target frequency. Full Maxwell/Burgers rheology, rotation splitting, lateral heterogeneity, anisotropy, moment-tensor excitation and instrument response are outside the current default capability. Probe traces are not claimed to be source-calibrated seismograms.

Illustration normalization uses each mode's fixed radial maximum norm. Geometric gain, arrow gain, color limits and playback speed are separate and saved; none is normalized again each frame. `probe --raw` uses the mass-integral-one canonical field in kg^(-1/2) and its derivatives, not metres and not an unconverted upstream file.

## Guides and sources

- [User guide](docs/USER-GUIDE.md): research, teaching and production workflows.
- [Publishing](docs/PUBLISHING.md): CI, static targets, package releases and ownership.
- [Development](docs/DEVELOPMENT.md): module ownership, meaningful validation and release steps.
- [Data](docs/DATA.md), [contract](docs/CONTRACT.md), [schemas](schema/README.md).
- [Output recipes](examples/recipes/README.md), [lessons](examples/lessons/README.md), [acceptance](docs/ACCEPTANCE.md).
- [Current phase](docs/PHASE-3.md), [roadmap](docs/ROADMAP.md), [historical reviews](docs/reviews/).

The default numerical core adapts fixed [Ouroboros v6.0](https://github.com/harrymd/Ouroboros/tree/fa63363040a28c08d9fe2bd7d05dcc823d90dd1e); [vendor notes](vendor/README.md) and bundle provenance record local corrections. Independent frequency references use fixed [MINEOS](https://github.com/geodynamics/mineos/tree/26f842dbe95b0c27d5e77146d415268db1239913). Visualization was inspired by [Saviot's Earth demonstration](https://saviot.cnrs.fr/terre/index.en.html). Coastlines are Natural Earth 110m public-domain data; palettes and licensing are documented in [assets](packages/earth_modes/assets/README.md). The package is GPL-3.0-only; retain upstream licenses and attribution when distributing it.
