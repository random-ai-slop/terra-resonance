# Product sufficiency and long-term strategy — historical v1.1 rationale

This records the design-sufficiency decision, not an implemented-feature checklist. After three technical planning rounds, three roadmap studies, lead synthesis and independent counter-review revised the scope. [PLAN](PLAN.md) is the current project entry; [ROADMAP](ROADMAP.md) gives dependencies/gates. The original review asked whether the project was worthwhile and sufficiently planned, not merely free of known bugs. Phase-2 changes are tracked separately in [PHASE-2](PHASE-2.md).

## Continuing problem

Starting from an Earth/planet model, users should understand and verify modal structure, turn a phenomenon into a reproducible scientific scene and take it into research, explanation or production. Keep computation, physical interpretation and visual evidence together. An unsourced animation, invisible solver or nonportable website solves only part of that task.

| User task | Useful outcome | Sufficiency question |
| --- | --- | --- |
| Researcher changes core/mantle structure | Clear models, mode identities/errors/support, independent recomputation | Can curves reveal localized/mixed behavior? Are boundary sides and domain identity visible? |
| Informed learner studies R/S/T, n/l/m, nodes and degeneracy | Understand relations between quantities rather than memorizing labels | Are nodes, trajectories and counterexamples needed to reduce reliance on mathematical intuition? |
| Teacher reveals structure and one or two conclusions | Controllable, replayable parameters with conclusions independent of irrelevant appearance | Does the same scene need a presentation layout instead of another website? |
| Producer prepares paper/slides/animation | Consistent composition, stable outputs, provenance/units/rights, editable deformation | Do aspect ratio, transparency, framing and annotation controls cover real production? |

## Sufficient planning criteria

Every required feature maps to a task and closes a workflow through public API/CLI/UI without editing source. Scientific quantities, display choices and explanations are mutually inspectable; likely confusion receives concrete counterexamples. The first delivery must offer more than a loose combination of a solver and a sphere animation. Long-term approximations, evidence gates and data changes must be explicit without implementing all future physics now. Control maintenance: a feature that cannot close a small loop with existing model/field/scene/output needs stronger justification. Deferring promised core tasks is insufficient; promising all future research in one release is also irresponsible.

## Tradeoffs reopened by the sufficiency review

- Nodes were previously postponed without enough value analysis. Component zeros can explain n/l/m, but are distinct from vector zeros; T's identically zero radial component is not a useful node network.
- One/few material trajectories distinguish standing straight-line motion, quadrature ellipses and traveling patterns. Not every mode produces an ellipse. Reuse field evaluation and avoid inventing new physics.
- Cross-model curves are the necessary minimum. Dual 3D comparison should be justified by actual localized/mixed-mode questions rather than dismissed merely because it adds a viewport.
- Presets need questions, steps, conclusions, cautions and provenance, with full editable parameters; defaults alone are not lessons.
- Probes are not seismograms. Whether source coupling belongs in the first delivery depends on reuse and validation costs, not the phrase “easy extra.”
- Still images, movies and 3D projects are primary outputs. A shared compact ExportSpec can prevent scattered aspect/transparency/annotation/time-window settings, but must earn its maintenance cost.

## Parallel improvement tracks

| Track | First complete delivery | Evidence for expansion |
| --- | --- | --- |
| Scientific trust | Real SNREI solutions, normalization/provenance, independent references, inspectable fields | Independent evidence for each new approximation or external solver |
| Understanding/research efficiency | Question-led exploration, comparison and explanation without source reading | Repeated user obstacles, data scale and measured workflow delays |
| Production/reproduction | The same scene leaves as data, image, movie and editable deformation | Actual editor/format/batch/narrative requirements |

Do not split user tasks into “website now, science later” or “solver now, understanding later.” Subsequent versions widen scope/scale rather than complete basic uses already promised. Advanced physics never excuses poor maintainability, defaults or output reliability.

## Small extension boundaries to preserve

Model/request→canonical results is the solver boundary. Add a second concrete adapter before a plugin abstraction. Treat radial real functions and spherical degeneracy as v1 assumptions, not universal modes; new assumptions receive explicit new types/versions and readable migration errors. Separate field evaluation from rendering: Python is the scientific reference, and the limited TS angular/interpolation/time mirror has shared fixtures, not a second eigensolver.

Separate raw scientific results from Scene/Probe/Export usage. Camera changes do not invalidate a model result. Synchronous local API/CLI, atomic outputs and explicit batches precede caches, concurrency and services. Preserve standalone numeric arrays so future solvers or published data can reuse the visual layer.

Do not prebuild a plugin market, arbitrary PDE framework, database orchestration, collaborative editing, accounts, cloud compute platform, universal metadata model or unvalidated rheology UI. Each stage instead states the new task, evidence, concrete prerequisites, schema impact, must/non-goals, owner and exit conditions.

## Candidate route and final decisions

The historical candidate tracks were a complete SNREI workbench; external solver/data interoperability and comparisons; physically dimensioned source/receiver synthesis and observation; rotation/ellipticity/aspherical coupling; and independent complex-rheology/non-Hermitian/3D research. They are not an obligatory serial release list. Teaching and production continue in parallel around stable versioned data boundaries.

Three research reports are retained under `research/roadmap-science.md`, `roadmap-product.md`, `roadmap-architecture.md`; synthesis and counter-review under `reviews/strategy-*.md`. No real-user interviews established the product hypotheses: independent task walkthroughs and actual artifacts were the next evidence, not proof of market/user value.

The final first-delivery additions were one linked material point/trajectory, signed single-real-mode component nodes, six question projects, presentation mode, compact ExportSpec and an explicit perturbation recipe. Counter-review reduced three mandatory points to one because picking/material sides/exports carry real complexity. The whole interpretation layer is M-scale work, not free buttons. PNG/movies preserve it; unsupported GLB analysis overlays require explicit omission.

Keep curve/frequency-table comparisons and rapid switching at the same camera; dual viewports wait for concrete demand. Mature kernels and real source/observation workflows are near-term gated routes. Rotation, complex rheology, 3D and inversion enter separate evidence-driven branches. Source excitation need not wait for all kernels, weak Q need not wait for density/interface kernels, and rheology need not wait for rotation.

Preserve scientific semantics, portable projects and primary APIs. Add CoupledMode/MeshMode or binary arrays only with concrete demand and explicit versioning, avoiding vague universal fields. All three counter-reviews accepted the synchronized scope for real vertical-slice implementation. That established resolved value/scope/dependency/acceptance decisions, not demonstrated product value. The next evidence had to come from running results and user tasks, not a longer feature list.
