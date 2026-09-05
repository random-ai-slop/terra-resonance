# Phase 2 planning, round 3 — final workflow and delivery review

Status: final planning review only; no implementation changes. Reviewed the round-3 precedence section of `PHASE-2.md`, the ownership manifest, and the actual package/browser entry points. Earlier draft wording is superseded by the round-3 decisions.

## Freeze conclusion

**Ready for implementation after two bookkeeping updates below.** No remaining product or workflow design blocker requires another planning round. The plan now defines a useful package-first outcome, a coherent website language boundary, reproducible surface density, truthful legacy behavior, and bounded scientific work. Additional language selectors, graphics controls, frameworks or feature areas would reduce delivery clarity.

## Final adversarial workflow

| Counterexample | Resolved behavior and necessary implementation evidence |
| --- | --- |
| A fresh wheel installation has no repository, network, preview images or web server | `list_examples()` and fresh `load_example()` use packaged canonical bundle/catalog resources. CLI example → scientific PNG/probe → GLB is possible offline except for explicitly optional encoders. A clean installed run verifies the actual path. |
| A saved GIF project is used to produce a 640×480 scientific SVG, then CSV | Resolved project image defaults precede operation defaults; explicit dimensions win. Movie fields are irrelevant to SVG. CSV ignores inherited image fields and rejects explicit image-only flags. Check actual dimensions/analysis metadata, not just successful exit. |
| The researcher changes material parameters | The documented Model → solve → scene path creates a new validated scientific result. The original PREM bundle and its teaching identity are not reused or edited to disguise recomputation. This requires no additional model-editor UI. |
| A custom project reuses a built-in lesson ID, or adds one teaching metadata key | Bundle hash plus exact canonical teaching-object matching prevents false recognition. Original metadata survives save. An edited scene/probe within a genuine lesson may still display that lesson's translated instructions. |
| Language changes while an error is visible and an export is running | Stored diagnostic identities re-render in the current locale; the operation is neither restarted nor relabeled midway. UI locale is absent from physics, geometry keys and saved production state. English artifacts remain independent of the visible Chinese chart. |
| A phase-1 Chinese teaching project is imported into an English UI | Historical user metadata remains verbatim. It is not mistaken for the regenerated English canonical lesson. Product text remains English; arbitrary user text is not subject to the maintained-copy policy. |
| A Scene 1.0 wireframe project is imported, viewed, saved, then explicitly given 10-degree spacing | Passive round trips retain 1.0 and absent/null spacing exactly. The explicit action upgrades only the scene. The corrected filled cut faces are disclosed by the 0.2.0 renderer and policy metadata; legacy surface triangle wires remain available. |
| A high-degree mode uses a very sparse grid | The chosen spacing is retained with a meaningful sparse-grid notice. Dense scientific samples, source knots, clipping diagnostics, nodes and probes remain independent. Endpoint/morph preflight includes hidden scientific geometry and exported animated primitives. |

The scientific-image and probe option policy is now precise enough to implement without inconsistent browser/CLI defaults. The wire recipe is explicit enough to compare Python, Three.js and GLB. The experimental solver remains a separate API with named evidence gates, rather than silently becoming the default backend.

## Two final bookkeeping updates

1. **Capture the original Chinese lesson copy before canonical regeneration.** Root has now specified this dependency in the handoff: root first saves the current Chinese teaching content into website-only localization resources, then sends “Chinese website catalog captured.” The product owner may translate source/docs and build the examples module independently, but must not run the English generator before that notice. Add this dependency to the frozen plan. It prevents losing the reviewed Chinese wording or reconstructing it from memory. Root remains the only writer to Site destinations.
2. **Make the ownership ledger agree with the plan.** The manifest assigns all 36 existing CJK documentation files exactly once, with no duplicates. However, its accompanying prose says `CONTRACT.md` is explicitly listed although it is absent from the JSON. Add `docs/CONTRACT.md` to `scope_review`; this documents the already agreed sole writer and does not change the division of work. README and generated example documents are already explicitly assigned by the plan.

These are execution-order/ledger corrections, not unresolved design decisions.

## Feasibility and scope discipline

The documentation allocation contains 8 numerical, 11 package and 17 product files before the explicit contract entry. It is substantial but finite. Translation should retain headings, chronology, adverse findings, source references and numeric evidence; it should not become another rewrite of the roadmap. Current guides can be concise while historical reviews remain linked. The English generator and package resources must be synchronized only after the relevant schema defaults and the Chinese-resource capture are ready.

Root's website work is the main integration dependency. Typed catalog completeness must include accessible names, status text, quality explanations, owned validation/render/export messages and chart labels. Test English and Chinese at narrow and wide widths, including dropdowns and presentation mode. Allow wrapping and measured layout adjustments; retain the scientific viewport and avoid introducing a new navigation system merely to accommodate longer English labels.

The minimal release evidence should remain one connected installed-package/browser workflow plus focused counterexamples for diagnostic retranslation, edited lesson recognition, legacy/new scenes, grid geometry/budgets and image option precedence. A language scan should explicitly allow scientific symbols, Unicode user fixtures, authoritative third-party text and authentic website evidence. Translation-only edits do not justify repeating unrelated expensive numerical baselines.

No extra feature is needed for workflow sufficiency. After the two handoff notes are recorded, proceed with the declared owners, dependency notices and independent implementation review.
