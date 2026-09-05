# Phase 2 planning, round 2: contract cross-review

Reviewed `docs/PHASE-2.md` after its round-1 revision, against `data.py`, `export_common.py`, `export_glb.py`, `cli.py`, the browser renderer, and the installed-example proposal. This is planning only. The revised scope is sufficient and broadly feasible; the following small decisions are needed before round 3 freezes it.

## 1. Clarify legacy compatibility versus the cut-face correction

The plan says both “accept SceneSpec 1.0 unchanged” and “section faces remain filled in all renderers.” These cannot mean pixel-identical legacy output: existing Python wire export turns all faces into edges, while the browser already keeps section faces filled. There is no single old appearance to preserve.

**Minimal revision:** say that 1.0 remains readable without rewriting the input scene or its bundle identity; absent/null spacing retains legacy **curved-surface** triangle edges. Filled sections are a documented renderer bug fix that also applies to 1.0. Record this correction in release notes/export presentation metadata, without changing numerical quality evidence. The preserved boundary is scientific state and the old surface-grid interpretation, not erroneous old section rendering.

Keep Bundle and Project at 1.0 and Scene at 1.1 as proposed. Validators must use separate version constants: the existing Python `SCHEMA_VERSION` currently serves all three. Freeze a small version table: 1.0 permits absent/null spacing; 1.0 plus non-null spacing fails; 1.1 requires the field and permits null or the four choices. Validation/import must not silently upgrade. New scene construction and an explicit spacing selection may create 1.1; an unrelated time, locale, or camera edit must not upgrade an imported 1.0 scene. This avoids both data mutation and hidden defaults.

## 2. Freeze curve construction and the complete export budget

“Sample finely enough” is not yet an interoperable rule. A compliant Python implementation could connect sparse endpoints while a compliant browser samples hundreds of points, producing visibly different motion at high degree. Existing GLB budgets use `mesh_count * 2 * term_count`; line points added outside mesh_count could bypass that check.

**Minimal revision:** specify a shared deterministic curve recipe, not a new adaptive geometry framework:

- Grid spacing determines which material parallels/meridians exist; sampling along those curves uses a separate degree/quality bound. State its formula, seam duplication, pole treatment, and whether cut-boundary meridians are retained.
- Clip line segments against the same fixed removed quadrant as the surface. Do not connect surviving endpoints across the removed region. Curves on an internal selected shell use that shell's radius and the existing outer-side default.
- Dense scientific triangulation remains available when needed for filled sections and node extraction. Sparse display lines must not become the sampling input for scientific nodes.
- Include every allocated line vertex, filled-face vertex, hidden scientific sample retained for nodes, and overlay in preflight/cache counts. GLB morph/key budgets count all exported animated vertices and all animated mesh weights, including separate line and triangle primitives. Reuse the existing limits and rejection policy; do not silently drop lines or reduce modes.
- Both GLB exporters retain parametric lines **and** filled section triangles with the same temporal morph coefficients. Existing frozen-color and explicit overlay-omission limitations remain; the surface grid itself is essential geometry, not a newly omitted decorative layer.

Only one new spacing control is needed. Do not add solver mesh sliders, radial-density controls, arbitrary mesh editing, or a second “wire quality” parameter. Its label should say surface grid/spacing; it does not display a finite-element mesh. One sparse/dense comparison, a high-degree non-key-time line check, and a cutaway budget counterexample are enough acceptance evidence.

## 3. Make scientific-image precedence executable, including partial projects

The explicit > saved > operation-default rule is sound, but “saved project image options” still has two meanings. Python `validate_project` retains a partial ExportSpec, while browser parsing expands defaults. For a raw `{export:{format:"gif"}}`, should an eigenfunction SVG use its 800×500 operation default, or the portable ExportSpec's 1200×900 defaults?

**Minimal revision:** choose one rule and give that exact example. Recommended: resolve a present ExportSpec with its documented defaults, then project only width/height/transparent/annotation into image production; with no ExportSpec, retain the scientific operation default. This matches a browser round trip. Format comes from the requested output/operation; inherited fps, duration, and omissions have no effect. Explicit irrelevant options still fail. For CSV/tables, discard inherited image options but reject explicit image requests, including `--no-annotation` if the table has no annotation concept.

Add width/height/transparency/annotation to the probe command as planned. Keep probe times in physical seconds and independent of production duration. Manifests must contain the actual resolved settings; neither CLI nor Python should silently pretend a CSV has a visual size. No generic exporter facade or resource-flag expansion is needed.

## 4. Fix the small installed-example API boundary

The package-first example closes a real usability gap. Freeze only what consumers need: `list_examples()` returns stable IDs in catalog order; `load_example(id)` returns an independent, validated self-contained project with English canonical teaching metadata, scene, probe, and export settings. Unknown IDs fail clearly. State whether the six distributed cases migrate to Scene 1.1 and their intended spacing, instead of letting whichever generator runs last decide.

Ship one scientific bundle and one lesson catalog, as proposed. Do not add resource downloaders, a project wizard, or six duplicated bundle assets. Preserve arbitrary imported text; the English requirement applies to maintained example copy and annotation labels, not to user model names.

## Product sufficiency and acceptance

The revised plan now covers independent package use, scientific-image configuration, bilingual website presentation, reproducible grid spacing, and a bounded numerical-ownership experiment. Removing the immediate backend rewrite, plugin registry, and many resource flags is appropriate. Keep the experimental solver separate so that its research gates cannot silently change the established default or delay otherwise complete language/grid work.

Round 3 should check four concrete paths: a legacy project with wire cutaway; a new sparse-grid project exported through Python and browser GLB; a partial saved ExportSpec used for a scientific image and probe; and an installed example loaded twice, with one copy edited without affecting the other. Reuse existing normalization, hash, and numerical benchmark evidence unless the corresponding numerical behavior changes. Resolve the four decisions above in the plan; no additional feature category or extensive testing layer is required.
