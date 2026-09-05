# Executable research and production recipes

Run these source recipes from a repository or extracted Python source distribution, using an environment with the package installed. An installed wheel can supply the scientific API; source recipe files themselves are not wheel resources. Output paths are replaceable and existing files are protected unless `--overwrite` is explicit. Installed users can start directly with `terra example` or `load_example()` as described in the [user guide](../../docs/USER-GUIDE.md).

## PREM project to artifacts

```sh
.venv/bin/python examples/recipes/render.py --out artifacts/demo
.venv/bin/python examples/recipes/render.py --out artifacts/demo-media --media --duration 8
```

The first command produces a self-contained project, PNG, vector eigenfunction/material/probe SVGs, probe CSV and scientific tables with original material JSON. The second adds GIF, MP4, animated GLB and independent readback evidence. Video requires FFmpeg; verification uses ffprobe. The PNG uses 640×480, draft angular quality and shared palettes. The saved project can be imported into the website or exported at larger dimensions.

The recipe uses PREM S0_2 with geography, arrows, nodes and one fixed material-point trajectory. GLB explicitly omits its three unsupported dynamic overlay categories while retaining deformation, reference geometry, camera and static initial colors. Every output has a manifest. `verification.json` records decoded timing, GLB structure and three non-keyframe displacement errors.

The 0.1.0 baseline actually executed the one-second media recipe; its historical evidence is in [exports.json](../../docs/validation/exports.json):

- 640×480 GIF: 20 frames, 50 ms each.
- H.264 MP4: 24 frames, 24 fps, 1.000000 s.
- GLB: two morph targets and 25 key times. At playback seconds 0.137/0.413/0.819, maximum error was approximately 3.40×10^-5 of the fixed geometric displacement bound, below 1%.
- PNG was decoded and visually inspected; SVG contains genuine vector curves. Standard-format verification is not native Blender execution.

These are observations for the specified bundle/request, not evidence for every complex scene. The same recipe can produce the default eight seconds and other scenes; multifrequency or attenuated motion does not automatically loop seamlessly. Changes to geometry, including phase-2 grids, require their own readback evidence rather than inheriting these historical numbers.

From a saved project:

```sh
.venv/bin/terra export artifacts/demo/project.json --out artifacts/publication.png --width 1600 --height 1200
.venv/bin/terra probe artifacts/demo/project.json --out artifacts/probe-again.csv
.venv/bin/terra export artifacts/demo/project.json --kind frames --out artifacts/frames --duration 8 --fps 24
```

Frames are written with a physical-time manifest, without mixing old files into the new directory. [Lesson projects](../lessons/) provide cutaway cases. High radial orders retain source knots and can be more expensive.

## Blender import

In the Blender environment used for production:

```sh
blender --background --python examples/blender_import.py -- artifacts/demo-media/earth.glb artifacts/earth.blend --fps 24
```

The script reads the adjacent `.glb.json` manifest, imports actual shape keys and animation, sets timeline/camera and saves `.blend`. Native Blender was not available in the baseline environment. Do not replace a failed import with an empty file or static sphere. Existing `.blend` output needs `--overwrite`. The root node handles z-up to glTF y-up; manually rotating the scientific vertices again would double-transform them.

## Same-model toroidal agreement

```sh
OPENBLAS_NUM_THREADS=1 python examples/recipes/agreement.py artifacts/agreement-new
```

The output directory must not exist. This copied recipe also runs outside the
checkout using only the installed package and SciPy. Four solves cover a
homogeneous sphere at mesh targets 20/40 with the default and experimental T
methods. Four self-contained reports separate cross-method agreement from each
method's refinement. A CSV, native SVG and PNG illustrate `cross-40`; their
sidecars retain the complete report. Separate `independent-frequency.json`
checks the T0_2 spherical-Bessel frequency against a named 0.5% ceiling without
promoting solver quality. Files are individually committed; a later failure
retains completed outputs. No directory deletion or implicit overwrite occurs.
See the [agreement guide](../../docs/AGREEMENT.md) for exact filenames, the
two-pair API/CLI example, sidecar-only recovery and scientific limits.

## Vs sensitivity with step-size and grid evidence

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python examples/perturb_model.py --out artifacts/vs-sensitivity --h 0.01 --mesh 24
```

For homogeneous-solid T0_2, hold radius, density and Vp fixed while using `Vs*(1+epsilon)`. Compute 0, ±h and ±h/2 at both 24 and 48 elements, retaining ten bundles, requests, hashes and comparison curves.

The independent analytic reference is that elastic toroidal frequency is proportional to Vs, so `d log(f)/d log(Vs)=1`. The executed [baseline evidence](../../docs/validation/vs-sensitivity.json) has maximum sensitivity error about 1.39×10^-11, baseline 24→48 frequency change about 1.21×10^-9 and h/h2 sensitivity difference about 1.26×10^-11.

This validates that parameter path, not general 3D PREM kernels, source inversion or tracking through mode crossings. A different model requires its own assumptions, identities, step-size and grid evidence.
