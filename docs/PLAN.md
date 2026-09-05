# Terra Resonance — project plan

The phase-1 design v1.1 was frozen after three technical reviews and a separate product-sufficiency/long-term-roadmap challenge. Its 0.1.0 implementation subsequently completed three sequential implementation reviews; the reports retain their original pending-at-the-time findings. Current 0.2.0 work is governed by [PHASE-2](PHASE-2.md), not by the former statement that all code was an unaccepted draft. See [ROADMAP](ROADMAP.md), [STRATEGY](STRATEGY.md), [CONTRACT](CONTRACT.md) and `reviews/` for decisions, exact interfaces and evidence.

## Purpose and principles

Connect spatial modal structure, material motion and readable signals in one scientific workbench for spherical Earth and planetary models. The main products are an installable Python core, versioned interchange data, interactive 3D exploration and deterministic offline outputs. The website is one entry point. Recommended presentation settings are stored separately from computed physics.

1. Frequencies, eigenfunctions, normalization and physical options must come from the same model calculation. Observed periods must not be attached to unrelated illustrative shapes without disclosure.
2. Arbitrary modal coefficients are not predicted seismic displacement. Record coefficient meaning, deformation gain, physical time, playback speed and phase in UI and artifacts.
3. Reuse established solvers before casually rebuilding self-gravitating fluid/solid coupling. Pin runnable code, retain licenses and isolate adapter patches.
4. Connect Python and TypeScript through a concrete data contract; no browser or cloud solver is required by the scientific core.
5. Necessary tests cover physical invariants, independent references, data boundaries, valid outputs and principal interactions. Coverage percentages are not the objective.

## Research decisions

The [reference Earth page](https://saviot.cnrs.fr/terre/index.en.html) does not derive its illustrative shapes and observed periods from a single realistic Earth model. Terra addresses that teaching risk. [Ouroboros](https://github.com/harrymd/Ouroboros) supplies arbitrary radial fluid/solid regions, R/S/T and no-gravity/Cowling/full-gravity variants. Its moving master contained regressions and unfinished entry points; the runnable v6.0 pin is `fa63363040a28c08d9fe2bd7d05dcc823d90dd1e`. Full viscoelastic entry points raised NotImplementedError and were not counted as working upstream scope. Linear Q remains explicitly experimental.

[Mineos.jl](https://github.com/anowacki/Mineos.jl) was investigated for reference calculations; the delivered independent frequency evidence uses pinned Fortran MINEOS. It is not a mandatory second runtime. Three.js GLTF morph targets serve editable 3D animation; SVG is reserved for supported scientific curves/sections rather than pretending SVGRenderer reproduces all textured materials.

## Organization

| Path | Responsibility |
| --- | --- |
| `packages/earth_modes/` | Models, solver adapter, modal data, fields, analysis, exporters, CLI |
| `packages/earth_modes/vendor/` | Necessary pinned upstream source and license |
| `packages/earth_modes/experimental/` | Explicitly bounded owned numerical pilots; no default replacement |
| `apps/web/` | React/TypeScript workbench and Three.js renderer |
| `schema/` | Versioned scientific and presentation schemas |
| `examples/` | Reproducible inputs, precomputed modes and source recipes |
| `scripts/` | Data generation, validation and release helpers |
| `tests/` | Focused physical and format regressions |
| `docs/` | Conventions, current guides, plans and preserved review evidence |

## Scientific and data boundaries

The baseline is spherically symmetric, nonrotating and isotropic, with radially varying solid/fluid materials. Preserve both sides of every interface; never smooth tangential discontinuities across fluid/solid boundaries. R is the l=0 spheroidal family. Fluids do not support elastic T shear modes. Radial labels and rigid zero modes require explicit solver conventions.

Canonical data uses SI: radius m, density kg/m³, velocity m/s, frequency Hz and physical time s. UI conversions to km/mHz/min are explicit. A bundle carries model/material boundaries, solver/version/request/gravity, mode ID/family/n/l, eigenfunctions, optional actual potential, normalization, provenance and per-mode quality. Imports validate finite values, lengths, ordering, indices and model association.

The angular basis is normalized real spherical harmonics: signed m distinguishes sine/cosine branches, and quadrature-phase pairs express traveling patterns. Displacement is radial plus normalized spherical gradient and rotated gradient. Canonical eigenfunctions are retained independently of illustration coefficients. Phase, amplitude, deformation and fixed color limits are separate. Probe displacement/time derivatives are not automatically meters. Superposition occurs before display transforms.

## Required baseline capabilities

| Area | Delivery depth | Evidence |
| --- | --- | --- |
| Solver | Actual supported R/S/T, arbitrary fluid/solid topology, three gravity treatments, custom models, frequency/degree controls | Six topology matrix, physical invariants, independent references, refinement |
| Attenuation | Experimental linear-Q frequency correction and optional modal-Q envelopes | Runnable cases, finite differences, elastic limit; no full-rheology claim |
| Fields | Single/multiple modes, signed m, phases, radius sampling, real/traveling combinations | Analytic low-degree harmonics, poles, T radial zero, R spherical symmetry |
| 3D | Deformed surface, mesh, reference sphere, arrows, true radial cutaway, arbitrary shell, geography | One shared field; programmatic and manual checks |
| Scientific figures | U/V/W and available potential, frequencies/dispersion, material profiles, modal receiver traces | Source data, explicit units and normalization |
| Workbench | Browsing/import, exact project save/load, recommendations and research settings, camera/time/quality | Principal flows and error recovery |
| Static output | 3D PNG, scientific SVG, frequency/eigenfunction/probe CSV | Readable files and data readback |
| Dynamic output | Deterministic MP4/GIF/frame sequences with generation metadata | Frame count, timestamps and encoder metadata |
| 3D output | GLB meshes and editable morph animation, Blender path | Structure, animation and import/readback |
| Independent use | Installable API/CLI, standalone frontend, examples and theory/limits | Clean install/build and complete workflows |

Source moment-tensor excitation, general 3D, rotation and anisotropic coupling are not implicit capabilities. A modal probe is not renamed a seismogram. Any later upstream source summation reuse must verify excitation and units separately.

## Interpretation and visual design

The baseline includes one linked material point and analytic trajectory, signed single-real-mode component nodes and radial zero crossings, six question-led projects, presentation mode and a compact ExportSpec. Cross-model comparisons use explicit curve/table pairs, not a displacement mixture of different models. Three simultaneously edited points, full vector-node classification/3D nodal isosurfaces, synchronized dual viewports, 3D potential coloring and arbitrary transfer functions are conditional extensions.

The style is a quiet geophysical observatory: dark ink-blue viewport, restrained surfaces and clear thin lines, cool neutral controls, cyan/amber for signed displacement. Decorative glow, star fields and random ornament do not substitute for information. The field dominates the layout; narrow screens prioritize view/playback then collapsible controls. Use consistent numeric typography, units, spacing and line widths; color bars state quantity, range and normalization. The phase-1 Chinese-first interface decision is superseded in phase 2 by coherent English/Chinese website locales with English fresh-visit default. Maintained non-website material is English.

## Development and delegation workflow

Research independently across numerics, visualization/output and scientific acceptance; the lead resolves contradictions. Freeze interfaces, licenses, examples and scaffold before implementation. Build a real model→mode→field→interactive-view→static-output slice, then complete the remaining breadth. Perform three sequential post-implementation reviews covering physics, boundaries/output/state, and complete user/reproduction/visual flows; repair findings before the next round.

Delegated tasks have exclusive file ownership, dependency contracts and runnable completion evidence. Reviewers primarily challenge others' code. Integration reports state actual scope, command and remaining risk. A solver cannot generate its own sole expected physical answer. Small UI or prose changes do not trigger the full expensive numerical matrix.

## Acceptance and sufficiency

[ACCEPTANCE](ACCEPTANCE.md) specifies six topologies, independent analytic/MINEOS evidence, two mesh levels, four complete workflows and output readback. A successful call is not verified physics. Exact-center behavior uses independently derived regular limits, including S l=1. Hash integrity and cross-machine numerical tolerance are distinct.

Six projects address breathing, linear tangential T motion, n/l/m controls, liquid-core sides, standing-to-traveling patterns and local beats. Each has at most three steps, a verifiable conclusion, a caution and real data. Research recipes include model/gravity comparisons, reusable MINEOS evidence and explicit material perturbation. Exact Vs scaling applies only to a homogeneous sphere or an entire independent solid domain; local perturbations require h/h2 finite differences and mesh evidence, not an unsupported kernel/inversion claim.

The interpretation layer is a medium integration task: point/chart links, saved scenes and PNG/movie output must agree; unsupported GLB overlays use visible capability limits and explicit omissions. One linked point closes the space–point–time loop without making three-point editing a release blocker.

Long-term interoperability, sensitivities and source excitation can proceed in parallel once their particular scientific prerequisites exist. Observational operators, radial anisotropy and rotation/ellipticity follow appropriate evidence gates; complex rheology, direct 3D and bounded inversion remain distinct research branches. Teaching, output reliability, performance and compatibility continue throughout. Reopen only decisions invalidated by actual evidence; further planning must not replace runnable products.
