# Planning review log

This is a historical record. The three planning rounds below are separate from the three later implementation review rounds. Planning approval was never treated as evidence that code or numerical results had passed.

## Review method

Each round used a named plan version, independent adversarial reports, lead-agent resolutions and revised plan/contract/acceptance documents. Reports recorded severity, trigger, impact, minimum correction and disposition. The next round examined the revision rather than merely repeating earlier findings.

Freeze required resolved scientific and architectural blockers and an executable complete scope, rather than stubs. Infeasible proposals had to move explicitly to a bounded future stage. Initial upstream research, v6 feasibility work and scaffolding had already occurred; a premature freeze was withdrawn and implementation paused. Existing drafts were retained as drafts, without treating them as accepted features or forcing their technology choices.

| Round | Input | Result |
| --- | --- | --- |
| 1 | v0.2 | Findings resolved in v0.3 |
| 2 | v0.3 | New workflow/delivery findings resolved in v0.4 |
| 3 | v0.4 | Final conditions resolved; technical plan v1.0 frozen |

## Round 1: numerical scope, contracts and product fidelity

Independent numerical, contract and product reports were integrated by the lead. Accepted changes included:

- Pin upstream v6, preserve Q reference-frequency semantics and canonical normalization, inspect actual matrix/grid budgets, and distinguish negative spectra, incomplete mode extraction and mode identity. Solid-domain and potential provenance became explicit. Six topology cases, analytical checks, MINEOS references and two-grid evidence were planned, not claimed executed.
- Keep canonical mass normalization separate from mixed upstream units. Define scene amplitudes as illustration weights, with explicit raw sampling, harmonic conventions, colors, timing and layer/domain distinctions.
- Define boundary snapping, poles and center behavior. The initial center exclusion/rejection proposal was explicit and did not reduce numerical solver scope; round 2 subsequently replaced that proposal with a regular center limit.
- Introduce self-contained projects with canonical JSON hashes, an orthographic camera, actual cuts, shared palettes, fixed arrow scale, display quality, offline Natural Earth data, a backend capability table, GIF timing rules, independent GLB reconstruction, transactional output and resource estimates.
- Preserve a small architecture without cloud services, databases or automatic resource discovery. At this point, trajectories, nodes, dual views, 3D potential coloring and source excitation were outside v1; later strategy review reconsidered the first two. Comparison curves and a GLB import script remained required; native `.blend` claims required an actual Blender run.

ACCEPTANCE acquired four executable user journeys and separate evidence gates rather than one global accuracy label.

## Round 2: research replay, recovery and delivery budgets

Workflow, architecture and delivery reviews examined v0.3. The v0.4 revision added:

- SolveSpec, ProbeSpec, explicit comparison pairs, canonical CSV and WORKFLOWS. Requested input and effective models/settings remained distinct, and validation/solving were required to preserve inputs.
- A precise canonical hash projection, domain identity, saved-artifact integrity versus numerical reproducibility, and density-weighted mass integration by region.
- Structured quality/groups and legal empty toroidal results, separated from failed or incomplete solves. A failed solve must not publish an ordinary-looking partial bundle.
- An l=1 center regularity formula and approach-direction checks, replacing the artificial central hole.
- GIF default 20 fps, MP4 default 24 fps, `floor(x+0.5)` frame rounding, a fixed-bound 1% GLB non-keyframe gate with damping curvature checks and key budgets, two-pass GIF palette generation and paired-output rollback.
- Independent surface/geography settings, outer-surface geography, a fixed material cut quadrant and explicit GLB omission choices without repeated approval prompts.
- Concrete matrix, cache, GLB, pixel and disk budgets; focused functions and a two-tier verification strategy.

These were contract revisions, not runtime proof.

## Round 3: freeze acceptance

Science, contract and product reviewers walked the revised plan. The final v1.0 conditions were:

- Separate essential-constraint extraction from physical stability in mixed raw spectra; do not classify every raw negative generalized eigenvalue as a planetary instability before appropriate extraction.
- Require an explicit target for linear-Q corrections; otherwise record a null target. Preserve the complete SolveSpec.
- Retain probe layer identity, nonzero start time, half-open windows and synchronized quality semantics.
- Provide explicit GLB omission examples, leave saved projects unchanged, retain the agreed 4:3 export convention and canonical CSV definitions.
- Verify a wheel from outside the repository with packaged assets and licenses; an editable installation is insufficient.

The three technical planning rounds were complete and implementation could resume. The three implementation review rounds had not yet begun.

## Reopened strategy review: correctness was not sufficient

The user reopened planning to examine product sufficiency and a credible long-term route. Implementation paused again. Separate scientific, product and architecture studies examined benefits, dependencies and completion criteria rather than moving necessary capabilities into an undefined future. The lead synthesized STRATEGY, ROADMAP and strategy-decisions, followed by three independent counter-reviews and integration.

The resulting v1.1 scope retained a bounded vertical slice:

- Component nodes, one linked material point with an analytical trajectory, six question-led presets, presentation mode, ExportSpec and a parameter-perturbation recipe. The initial three-point proposal was reduced to one.
- Material-reference coordinates and an explicit interface side; trajectories sample the existing analytical field rather than numerically integrating velocity.
- Nodes limited to a selected signed real component. Constant-zero regions, material jumps and zero-time factors require separate treatment. A toroidal radial component that is zero everywhere is not a meaningful nodal network. Finite display gain does not change the physical field definition.
- Beat examples must demonstrate a nonzero local signal and cancellation rather than merely changing global colors.
- Scene overlays persist through PNG/video; GLB can explicitly omit analysis overlays. No claim that every format supports every layer at no cost.
- Exact Vs scaling is an analytical check for a wholly homogeneous body/domain; localized perturbations require h/h2 and mesh evidence. The recipe must not be called a sensitivity kernel.
- ExportSpec contains output parameters, without duplicating scene quality, aspect state or a second physical clock. Image dimensions determine aspect; execution policy stays outside scientific state.
- The roadmap is a dependency graph: source excitation need not wait for every kernel, weak-Q studies can connect to kernels, and radial anisotropy can precede general 3D structure. Rheology and rotation have independent prerequisites. Teaching, production, performance and compatibility continue throughout.

The counter-review approved this vertical slice as sufficiently specified for implementation, not as an already mature research ecosystem. Later stages have bounded hypotheses, gates and stop rules. Full implementation and three postimplementation review rounds were still required.
