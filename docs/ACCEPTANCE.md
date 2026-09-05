# Acceptance matrix and baseline results

This document preserves the original acceptance criteria and the actual 0.1.0 results below. Unexecuted work is explicit; a script's existence is not validation. Phase-2 additions are governed by [PHASE-2.md](PHASE-2.md) and require their own implementation evidence.

## Phase 2 implementation result

The 0.2.0 additions are implemented: installed English examples and CLI discovery, reproducible Scene 1.1 material grid density with explicit Scene 1.0 compatibility, English maintained documents/artifacts, bilingual state-preserving website, and a separate experimental toroidal core. Source integration passed 83 Python and 25 frontend checks plus TypeScript, lint and static build. All 19 independent pilot comparisons were reproduced. [The integration review](reviews/phase-2-implementation-r2-integration.md) records actual browser downloads and the defects repaired after cross-review. [The release review](reviews/phase-2-implementation-r3-release.md) records the final independent distribution installations and media decoding; the older baseline results below are not borrowed as new release evidence.

Remaining scientific boundaries and the default PREM bundle are unchanged. Native Blender execution is still not claimed. The owned solver is toroidal, elastic and experimental; it does not replace the full default backend.

## Four complete workflows

1. **Explore:** open the real default isotropic PREM approximation, select R/S/T and n/l/m, inspect frequencies, quality and regional eigenfunctions; switch surfaces/grids, color components, vectors, shells and cutaways; pause and seek accurately.
2. **Research:** modify a sourced material Model → solve specified families/degrees/gravity/grid by CLI → inspect discrete-spectrum quality and warnings → import into the website → save a self-contained project → restore the same physical time. Renaming a model in the website is not recomputation.
3. **Compare and superpose:** configure two or more modes with m, real coefficients and phase to inspect standing/traveling patterns and beats. Use a fixed common color scale and scientific comparison curves. Separate-model comparisons must not be treated as one physical linear superposition.
4. **Produce:** save a project → generate PNG, scientific SVG, CSV, PNG frames, GIF, MP4 and animated GLB → independently read outputs → recover scene/data references from sidecars. Without Blender, claim GLB plus an import script, not an already generated native `.blend`.

## Numerical capability

| ID | Deliverable | Independent basis | Gate |
| --- | --- | --- | --- |
| N1 | Gravity-free homogeneous elastic R/T sphere | Analytic traction-free frequency roots; radius/velocity scaling | Fixed equations/parameters; convergent refinement; default low-order relative error <=0.5% |
| N2 | R/S/T of the exact default PREM table, including l=1 and inner-core T | Pinned MINEOS raw output or an equivalent independent solution | Same model/frequency reference; low-order target <=0.5%; larger differences require correction/explanation and reopening the default selection |
| N3 | Solid, fluid, solid-fluid-solid, fluid-solid, solid-fluid and solid-fluid-solid-fluid-solid | Support, interface conditions, finite frequencies and refinement | Every applicable family × gravity 0/1/2; fluid T explicitly empty; no skipped failed topology |
| N4 | Default catalog on two grids | Per-mode frequency changes and association | Default demonstration modes change <=0.5%; unmet modes cannot be labeled verified, though explicitly labeled exploratory results may remain |
| N5 | Material linear-Q frequency shift and modal attenuation | Lossless limit, finite differences/pinned upstream case, correct exponential derivatives | Experimental features must run; unsupported combinations fail; no invented Earth Q |
| N6 | Canonical bundle and quality | Regional mass integral, units and identities | Declared discrete quadrature of ∫rho r²(U²+V²+W²)dr equals 1; preserve relative components, conversion factor and solver labels |

Custom models promise inspectable discrete eigenmodes and quality status, not uniform accuracy over the full parameter space. Coverage of a discrete frequency range is not proof of continuous-spectrum convergence.

## Fields, product and outputs

| ID | Deliverable | Basis |
| --- | --- | --- |
| F1 | Python/TypeScript field at the same point | Shared analytic/core fixtures, poles and both interface sides; spherical R and radial-zero T |
| F2 | Single/summed modes and time derivatives | Analytic cosine plus Q envelope and first/second derivatives; identical absolute-time field |
| F3 | Internal sections | Actual radial interpolation and boundaries; merely cutting away the outer shell is insufficient |
| U1 | Project save/import | Matching canonical data hash and scene; actionable errors preserve the last valid project |
| U2 | Main UI | Real click/drag/import/export, keyboard and narrow-screen use; no blocking console error |
| U3 | Resource extremes | Validate unsupported l/data/output size first; release WebGL resources and preserve previous results on cancellation |
| O1 | PNG | Decode dimensions/content; readable annotations/color scale; phase changes actual displacement |
| O2 | SVG/CSV | Genuine scientific vector curves; numeric readback agrees with data and units |
| O3 | GIF/MP4/frames | Decode count/duration/fixed physical samples; at least two genuinely different frames; no forced seamless nonperiodic animation |
| O4 | GLB | Valid structure, morph targets and weight animation; readback matches scientific displacement; static-color limitation declared |
| O5 | Reproducibility | Sidecar version, scene, bundle hash, production parameters and explicit omissions; no silent downgrade |
| D1 | Installation | Clean API/CLI install, packaged assets, computation/output and frontend production build; installed use can be offline |
| D2 | Maintenance/licensing | Pinned vendor commit/license/patch notes, clear modules and no developer-machine path or secret dependency |

## Resource budget overview

- The Python solver processes degrees serially and estimates dense/workspace memory; default budget is 512 MiB and may be explicitly increased. Over-budget requests fail with an actionable grid suggestion rather than becoming an empty catalog.
- Recommended demonstrations favor l<=8 and at most eight active terms. Rendering separately validates l<=64, at most 32 terms and total samples. Spatial bases are cached; frames combine time coefficients.
- Browser imports default to a 32 MiB file cap. CLI can handle larger inputs; the static website does not promise cloud computation of arbitrary models.
- Export preflight validates dimensions, frame rate/count and memory before production; stream frames/encoding rather than retaining every uncompressed frame.

Exact limits/formulas are in CONTRACT's resource preflight. GLB verification includes non-key times with geometric error <=1% of a fixed displacement bound. Cross-language frame count uses `floor(duration*fps+0.5)`. Shared JCS cases cover renaming, unknown provenance, -0, Unicode and invalid numbers/strings. A numerical recomputation is not required to reproduce an artifact hash.

Verification has two levels: necessary fast regression (analytic fields/hashes/small solves/media) and release evidence (complete topology matrix, default convergence/independent benchmarks, browser workflows and clean installation). Recheck affected behavior and required integration after a repair; do not turn every expensive evidence run into a routine mandatory test.

## Product sufficiency

| ID | Complete value path | Independent basis and limit |
| --- | --- | --- |
| E1 | One material point → 3D marker → analytic trajectory → synchronized probe → save/output | Same undeformed coordinate/field; a single real mode gives a line, quadrature the expected ellipse; Q/multiple frequencies need not close; media retain gain |
| E2 | Component node lines and radial zero crossings | 0S2,m0 latitudes agree with Y20; radial-zero T is inapplicable; global temporal zero is not a spatial node; no fabricated roots across discontinuities |
| E3 | Six problem projects and presentation mode using the same scene | At most three steps, one checkable conclusion and a caution per lesson; independently walked without editing code; no claim of human user research |
| E4 | Publication/classroom/video/3D presets and ExportSpec restoration | One source of dimensions/aspect, explicit transparency/annotation behavior; GLB overlay omissions chosen explicitly while PNG/video retain them |
| E5 | One material-perturbation recipe | Analytic homogeneous/whole-solid-domain Vs scaling for T; local perturbations require h/h2, grid evidence and explicit pairing; not called kernels or inversion |

Multiple points, synchronized dual viewports and a complex node system were not baseline gates. E1–E5 serve existing tasks and include persistence and main media outputs, not website-only demonstrations.

## Sequential implementation review

The three rounds occurred after implementation and were recorded separately from planning and strategy counterreviews: round 1 science/data, round 2 interaction/exports, round 3 independent reproduction/delivery. Each followed the preceding round's fixes and verification. Record genuine defects and justified improvements; do not fabricate tests or changes to fill a round count.

## Actual 0.1.0 baseline results — 2026-09-04

| Gate | Result and evidence |
| --- | --- |
| N1–N6 | Passed. [Numerical evidence](validation/NUMERICS.md), `numerics.json`, raw MINEOS/independent shooting output and density-interface thin-layer-limit evidence. Default PREM: 47 modes, 36 independently checked frequencies, maximum relative frequency difference about 0.0536%, maximum refinement change about 0.0212%. Stated scope limits remain. |
| F1–F3 | Passed. Shared Python/TS field fixture, centers/poles/material sides/Q derivatives, actual sections and high-order node regressions. |
| U1–U3 | Passed. Real import/save/error recovery, physical time, material side, presentation mode, 390 px overflow and desktop checks; budget/rollback regressions. See browser/contract review reports. |
| O1–O5 | Passed. `validation/exports.json` and `validation/release.json` contain actual decoding/readback; all seven formats exercised through CLI, browser ZIPs read back. GLB non-keyframe error meets 1%; static colors/overlay omissions are explicit. |
| D1–D2 | Passed. Independent wheel/sdist installations ran API/CLI/media outside the repository; packaged resources/schema/licenses matched byte-for-byte. Static production build and standalone website test directory ran successfully. Release/dependency evidence is under `validation/`. |
| E1–E5 | Passed. Six self-contained cases and `validation/lessons.json`; nodes/trajectory/probe/export restoration, analytic fixed-color envelopes checked at 65 times; ten perturbation solves in `validation/vs-sensitivity.json`. |
| Three implementation rounds | Passed. Sequential repairs and independent rechecks are recorded in [the implementation log](reviews/IMPLEMENTATION-LOG.md), separately from planning. |

The final baseline regressions were 62 Python and 19 TypeScript tests, type checks, maintained-source lint and static production build. The full scientific matrix is not rerun for every prose change.

Explicit exclusions: no native Blender was available, so `.blend` execution was not verified; the delivered GLB and import script were checked as stated. Probes are traces for specified modal coefficients, not source-calibrated seismograms. Complex rheology, rotation/3D coupling and inversion follow the reviewed longer-term research route. These historical results do not automatically certify phase-2 additions.
