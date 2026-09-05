# Independent scientific scope and acceptance audit

Historical review of `docs/PLAN.md` v0.1, 2026-09-04. Responsibility: scientific fidelity, upstream scope and testability; the report did not edit the plan.

The draft's layering, separation of numerical results from display transforms, real-mode vertical workflow and sequential review principle were sound. Scope and data conventions still needed tightening before freeze, especially avoiding a claim that the documented full Ouroboros rheology was executable.

## Upstream evidence and actual scope

1. The [main Ouroboros README](https://github.com/harrymd/Ouroboros) supports arbitrary solid/fluid regions, R/S/T, background self-gravity and Eulerian perturbations for spherical nonrotating isotropic elastic models. Rotation, lateral heterogeneity and anisotropy are outside that baseline.
2. [Mode documentation](https://github.com/harrymd/Ouroboros/blob/master/modes/README.md) defines gravity 0 as absent, 1 as Cowling and 2 as full gravity. Separated solid regions have separate T spectra; a fluid model has no T modes. Preserve documented n labels and exclusions rather than inventing another ordering.
3. Although the mode documentation describes Maxwell, SLS, Burgers and Extended Burgers rheology, [calculate_modes.py](https://github.com/harrymd/Ouroboros/blob/master/modes/calculate_modes.py) raises `NotImplementedError` for `attenuation == 'full'`; frequency loading in [common.py](https://github.com/harrymd/Ouroboros/blob/master/common.py) does likewise. Full rheology therefore was not required to match the inspected executable scope. Linear Q could remain experimental after validating applicable families.
4. [Summation documentation](https://github.com/harrymd/Ouroboros/blob/master/summation/README.md) supplies R/S source summation but not T. It includes source/receiver geometry, displacement/velocity/acceleration and a source pulse. A probe trace is not an equivalent substitute. Kernel and source-coupling claims need their own acceptance and cannot follow indirectly from visualization.
5. Units required care: documentation describes raw eigenfunction radii in metres, but `common.load_eigenfunc_Ouroboros` multiplies loaded radii by 1e3. Pin and inspect actual files with a real fixture instead of trusting prose. That function also sets R-mode `U[0]=0` with an upstream-center-bug comment; any inherited repair requires a reason and provenance.

These observations came from readable master documentation/code, not completed numerical execution. A release still needed a pinned commit, real cases and capability evidence. This reviewer could not retrieve Saviot; specific claims about that page required another reviewer's evidence.

## Required pre-freeze changes

| Priority | Area | Requirement and reason |
| --- | --- | --- |
| P1 | Attenuation | Remove unresolved full-rheology delivery: inspected core paths are unimplemented. Mark linear Q experimental; retain convergence status and never disguise failure as a valid result. |
| P1 | ModeBundle | Add solid-domain identity so inner-core/mantle T with the same n/l cannot overwrite each other. Bind model/modes to unambiguous IDs/hashes. |
| P1 | Angular convention | Freeze harmonic normalization, Condon–Shortley phase, signed-m branches, colatitude/longitude and sqrt(l(l+1)) factors for V/W. A promise to define them later is insufficient for parity. |
| P1 | Radial convention | Define dual interface samples/regions and side selection. Equal radii on distinct sides are valid; global interpolation destroys tangential jumps. |
| P1 | Units/amplitude | Arbitrary eigenfunction normalization is not metres. Define normalization, coefficients/units and display gain separately; without excitation label normalized displacement. |
| P1 | Numerical quality | Record grids, physics options, versions, original labels, residual/convergence evidence and corrections. No uniform full-domain accuracy claim; recommended defaults require actual validation. |
| P1 | Time/export | Frames derive from absolute physical time; retain duration/fps/time mapping. Every output needs the shared scene/manifest; GLB needs genuine deformation animation. |
| P2 | Display defaults | Fixed color limits instead of per-frame normalization, which hides decay and zero crossings; identify any automatic range. |
| P2 | Numerical acceptance | Fix representative solid/fluid/PREM-like/multiple-solid-domain models and applicable R/S/T × gravity 0/1/2. |
| P2 | Order controls | Grid resolution and n/l limits are independent, with preflight and quality notices. High-order controls cannot merely play a few premade shapes. |

These changes refine existing abstractions into a small complete contract; they do not require broad architecture expansion.

## Scientific fidelity requirements

- Express displacement equivalently to `U Y e_r + V ∇ₛY + W(e_r × ∇ₛY)` with explicit V/W scaling. T must not become radial bulging.
- Eigenfunctions, frequencies, model and gravity choices belong to the same computation. Precomputed defaults are valid; handmade shapes are not research solutions.
- Apply common display gain after linear reconstruction. If components ever receive different exaggeration, save and label it explicitly.
- Do not force tangential continuity across fluid-solid interfaces. T is zero in fluid and inactive solid domains. Preserve original interface samples in export.
- Camera/global rotation is not rotation splitting. Rigid translation/rotation zero modes are not ordinary oscillatory modes.
- Geography follows material coordinates rather than scrolling independently to imitate motion.
- Trace every illustrative modification: gain, playback, phase, normalization, clipping, interpolation and any downsampling.
- Without real source excitation, call receiver curves modal probe traces. Metres require a physical amplitude definition; derivatives must be computed rather than relabeled.

## Small independent validation set

1. Known low-order harmonics, symmetry, finite poles and integrated normalization.
2. Family invariants: spherical R, radial-zero T and S tangent aligned with the surface gradient.
3. Homogeneous T analytic roots/shapes, including radius/velocity scaling.
4. Representative R/S/T mesh refinement and independent low-order full-gravity frequencies.
5. Gravity switches actually affect R/S while T remains unchanged.
6. Fluid/multiple-solid topologies, dual interface samples and interpolation.
7. Real adapter unit/normalization fixture, identities and metadata round trip.
8. Analytic single-mode derivatives/Q envelope and consistent superposition/probes.
9. Absolute-time determinism, saved scenes and same-point Python/TypeScript parity.
10. A few real outputs in every promised format, read back for dimensions/count/duration/deformation/manifest.

Tolerances should follow reference accuracy, convergence and mode properties, not use the implementation's own output as the only correct answer. Without an independent benchmark, state the evidence level; a plausible picture is not physical verification. Wrapper/getter/style tests are not required merely for coverage.

## What three review rounds mean

1. **Science/data:** a nonauthor checks units, harmonics, interfaces, zero modes, gravity, normalization and benchmarks; records reproducible defects, necessary regression and an improvement to misleading display/metadata.
2. **State/input/export:** extremes, invalid inputs, switching, seeking, restoration and batch output; actual media/GLB decoding rather than existence checks; improve recovery or reproducibility.
3. **Independent product reproduction:** start with README installation, compute a custom layered model and import/display/export it; check licenses, cache/network assumptions, documentation and readability; recheck earlier repairs in the complete version.

Each records scope, findings, impact, repair, evidence and limits. Three agents reading the same unfixed version do not constitute three sequential rounds. If no severe bug is found, report real coverage and justified improvement rather than manufacture changes.

## Historical environment observation

Detected Python `/usr/local/bin/python3`, Node `/usr/local/bin/node`, Julia `/Users/veritaswang/.juliaup/bin/julia` and FFmpeg `/usr/local/bin/ffmpeg`. Blender, magick and uv were not found. Default Python lacked numpy, matplotlib, Pillow, obspy and trimesh; scipy had a module spec but successful import was not verified. No software was installed during this audit. A controlled environment or bundled runtime was needed rather than assuming a complete system Python.
