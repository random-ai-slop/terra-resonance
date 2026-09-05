# Planning round 1 — integrator self-review

Historical record. Baseline: PLAN v0.2 / CONTRACT v1 draft. Author: root agent. This self-review did not replace independent review; the recommendations below describe the state at that time.

| Severity | Scenario / defect | Consequence | Minimal revision |
|---|---|---|---|
| P1 | A saved SceneSpec uses only model_id and is imported with another model of the same name | Old scenes could be reconstructed with the wrong modes | Bind the bundle using canonical model/data content hashes; package bundle and scene together and check consistency before loading |
| P1 | Browser and offline Matplotlib have no shared definitions for camera, cutaway, and color in the same scene | A reproducible image could still show a different physical view | Define parameters all renderers must honor and explicitly identified renderer-specific differences; never ignore unsupported settings |
| P1 | “Arrows and cutaway” do not specify sampled shells versus actual filled sections | Removing a shell could be presented as internal eigenstructure | Define sections sampled at their actual radii and selectable internal shells; retain separate fluid/solid grids and radius-dependent interpolation |
| P1 | “Includes Ouroboros” does not distinguish the eigenproblem from auxiliary kernels and seismic synthesis | Acceptance could be mistaken for delivery of unsupported research capabilities | Define the eigenproblem as the numerical baseline; label reused kernels experimental where applicable; explain source synthesis separately and never rename a probe trace a synthetic seismogram |
| P1 | Custom models depend on the Python CLI but the website has no complete import/error workflow | The demonstration works while the research workflow is broken | Include model input → CLI solve → bundle import → scene setup → offline export, with contract examples and matching commands |
| P2 | Default visualization permits l<=64 but sampling versus degree is undefined | False nodes or uncontrolled cost | Configure angular sampling sufficiency separately from viewport quality; specify minimum sampling and actual limits; reject requests beyond the budget |
| P2 | Maps require real geographical assets without attribution or an offline policy | License, network, or projection failures | Prefer low-resolution public-domain outlines as static assets, with source and projection conventions; anchor geography to material coordinates |
| P2 | “3D animation projects” means only GLB and a Blender importer | Native .blend acceptance could be claimed incorrectly | Deliver editable GLB shape animation and project/script; do not claim generated or verified .blend files when Blender is unavailable |
| P2 | UI calls controls research parameters although the browser does not solve | Users misunderstand what actually changes | Separate computed-mode selection and display controls from model/physics inputs requiring recomputation; supply real CLI parameters rather than changing labels |

Retain four entry workflows: preset exploration, research import, comparison/superposition, and reproducible export. Optional features must serve one of these. Implement specific verifiable commitments before adding more tabs.
