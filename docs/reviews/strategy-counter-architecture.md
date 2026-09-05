# Product-sufficiency counter-review: architecture, scope, and leaving planning

Historical record. Inputs: STRATEGY, ROADMAP, strategy-decisions, and the science/product/architecture roadmap studies. This review challenged necessity and hidden engineering cost rather than repeating settled scientific-field questions. Implementation remained paused.

## Verdict at the time

**The sufficiency work was adequate to enter implementation validation.** Material point → trajectory → nodes → explanatory cases offered more coherent value than a solver library loosely attached to an animated sphere. No long-term compatibility concern justified rebuilding the scientific foundation.

These additions were not all “cheap code.” Physics evaluation was inexpensive, but picking, persistence, interface-side semantics, multiple outputs, and readable presentation formed a medium-size product task. Accept the direction with four minimal adjustments, then stop planning after synchronizing the documents rather than ordering another generic review without new evidence.

## Adjustment 1: one complete explanatory work package

| Addition | Actual loss if removed | Recommendation |
|---|---|---|
| Material point linked to a time series | Hard to distinguish pattern propagation from material motion; a CLI probe does not identify a position in the scene | Retain for the initial release |
| At most three trajectories | One establishes the relation; more compare regions/interfaces without new physics | The proposal allowed a maximum of three, default one, without a particle system |
| Component nodes and radial roots | Learning n/l/m relies on interpreting colors and can confuse instantaneous zero with spatial nodes | Retain only defined, explainable zero sets |
| Six question presets | Animation alone supplies no checkable question or evidence of understanding | Retain as acceptance cases, not a teaching platform |
| Presentation mode | Workbench controls crowd projection/teaching space | Retain a simple layout switch |
| ExportSpec | Production settings are scattered and a saved project cannot reproduce output | Retain a small object, not a second scene model |
| Material perturbation recipe | Comparisons show differences without a controlled reproducible experiment | Retain one case, not a research framework |

Underestimated work:

1. Picking a deformed surface must recover material position x0, not use the displayed displaced point as input. Preserve layer_id at interfaces and point identity after resampling.
2. A trajectory needs a window, current marker, gain, closure semantics, applicability, persistence, seeking, and export—not merely field samples.
3. Mesh contours depend on seams, polar tangential conventions, zero plateaus, and discontinuous material sides. They cannot connect across discontinuities.
4. Three buttons are cheap; defining consistent PNG/video/GLB behavior is not. Explanatory layers cannot disappear silently during export.

Minimal implementation: a medium-size explanatory workflow using ordinary MaterialPoint, trajectory interval, selected component, and preset text objects. Share state/data without a layer-plugin framework. Each exporter retains or explicitly omits the layer; GLB need not promise editable semantics it cannot support. Extend the existing capability table.

## Adjustment 2: make new promises decidable

Nodes: support one real-basis mode's signed spatial-component contours with time factored out, plus U/V/W radial zero crossings. For mixtures, complex traveling combinations, or identically zero components, explain why the operation is inapplicable instead of changing node definitions. Separate zero plateaus from isolated roots. Sampled node markers do not relabel upstream n. Keep polar conventions and avoid seam-crossing artifacts. Do not add arbitrary isosurfaces, vector-zero taxonomy, or permanent-node solving. Refine only when a real six-case failure shows existing contours are inadequate.

Perturbation recipe: exact toroidal proportionality under a Vs change applies to a uniform sphere or uniform scaling of an entire independent solid domain, not an arbitrary layer-only change in a stratified model. The first analytic recipe should scale all Vs in a uniform solid sphere, holding density and radius fixed. General layer perturbations report actual recomputation and two-step results without assuming proportional frequency change. One ordinary script and explicit model/solve/compare commands suffice; no recipe engine or parameter DSL.

ExportSpec: width/height are the canonical dimensions, with derived aspect or an explicit consistency check if all three are accepted. Time originates only in scene.time_s. Transparency has a defined format scope; annotation affects layout, never removes provenance. Paths, overwrite, and budgets remain execution options. Update three small objects and the capability table with focused acceptance. At that pre-release point, no generic migration framework was needed.

## Adjustment 3: dependencies, not an alphabetic serial chain

The roadmap called work parallel but “C depends on A/B” and “D depends on material/interface sensitivity” could still be read as whole-stage prerequisites. Use actual dependencies:

    A: trustworthy SNREI fields and reproducible tasks
      B1: second-source import/verification → source excitation → observations/event comparisons
      Local perturbations → B2: individual kernels/sensitivities → mature weak-Q treatment
      B1 or another trusted backend → radial anisotropy
      Reliable basis + required angular matrix elements → slow rotation/ellipticity coupling
      Independently benchmarked rheology backend + complex-mode contract → complex-mode research
    Teaching, production, performance, and maintenance proceed across branches.

Source work needs physically meaningful normalization/derivatives and independent synthesis, not every density/interface kernel or large-catalog storage. A first controlled rotation problem needs its own matrix elements and basis convergence, not the full source/observation chain. Complex rheology need not wait for all of D; weak Q is useful experience but not a mathematical prerequisite for every independent complex-mode method. High entry gates still keep it outside initial delivery. Direct 3D import may be a separate research prototype, but formal support needs applicable 1D/slow-rotation limits and contract acceptance; it is not native 3D solving.

This changes roadmap expression, not current workload. Every long-term branch needs a scientific validation owner, reproducible case, and independent basis. Limited maintenance capacity should pursue one expensive new-physics branch at a time.

## Adjustment 4: executable criteria for leaving planning

Another architecture document now offered less value than a real vertical slice. Earlier rounds settled scientific/data/export conventions and this work added purposes and long-term gates. Clarity, explanatory value, and reproducibility still needed actual use.

Resume implementation after:

1. Synchronizing the main plan, contract, acceptance, and one entry document, distinguishing initial delivery from later branches.
2. Assigning explanatory-layer files, parallel work, and cross-export responsibilities rather than letting agents infer their own schemas.
3. Running one real R/T mode through solve → material point → field/trajectory/series → project → PNG/short video, then an analytic l2m0 node case. These engineering milestones do not replace final six-case/all-format acceptance.
4. Fixing actual failures locally. Reopen planning only when evidence changes scientific assumptions, core scope, or data meaning. Ordinary bugs/layout issues belong to iteration, not a project-wide pause.

Do not add “another generic review” as a gate. Independent numerical checks, browser tasks, media readback, and three post-implementation reviews own the remaining risks. Completed planning is not passed functionality; unknown functionality does not automatically require more planning prose.

## Meaning of a complete initial release

With these additions, the release supports a bounded research task (material edit → recomputation → evidence-backed comparison), an explanatory task (field → point → trajectory/nodes → questions), and a production task (one project across formats). Call it a trustworthy SNREI numerical/visualization foundation, not the entire free-oscillation research ecosystem.

The user emphasized visualization and executable scope comparable to Ouroboros. Deferring real sources/observations, mature kernels, rotation, and complex rheology did not block that task; their independent physical chains and validation costs justified explicit later gates. Editable GLB and an importer define 3D delivery; native project claims require actual execution.

The data model does not lock out future work: real r-only modes are an explicit v1 assumption, and future representations can use concrete migrations. No empty CoupledMode/MeshMode placeholders, generic plugin protocol, or WASM rewrite are needed now. Extract abstractions from a second real implementation or scientific object when it exists.

Recommendation: accept the explanatory and small production/perturbation additions, budget them honestly as medium product work, synchronize their state/output rules, and express roadmap dependencies directly. After those four changes, planning is sufficient; obtain real artifacts through sustained implementation.
