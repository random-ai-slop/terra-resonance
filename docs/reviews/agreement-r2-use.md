# Toroidal agreement: design round 2 user and artifact review

Assignment DEV-R2-USE/1. Read AGENTS, WORKFLOW, primary CURRENT, PHASE-3 revision 1 and both round-1 reports; inspected the accepted `03eacc3` comparison, plotting, CLI and transaction APIs. Only this report was written. No implementation, commit, solver run or website work was performed.

## Decision

**Keep the proposed outcome and one-pair figure rule.** It is a useful installed analysis rather than another developer benchmark. Embedded complete sources, explicit pair selection, recomputation on load and separate method/refinement/reference evidence address the important round-1 gaps.

Before round-3 freeze, resolve three user-facing ambiguities: how a recipient reloads a figure's sidecar; the exact minimum figure content and signed-residual direction; and which small recipe works with installed APIs alone while the larger independent validation remains a developer gate. These are narrow contract changes, not reasons to add a study framework or website.

## Necessary revisions

### P1: make the received-artifact recovery path executable

The proposed `load_agreement(path)` accepts an authoritative report, while figures/CSV receive “a sidecar containing the full report and resolved export settings.” That does not yet specify whether `terra agreement --report pair.svg.json --out recovered.csv` works. A researcher receiving only a figure and its self-contained sidecar should not have to discover an undocumented nested field or reconstruct the original source files.

Choose one exact layout before implementation. The simplest option is for the sidecar to remain a valid report at its top level, with a reserved export-production extension holding pair index, dimensions, current renderer/version and annotation language. The report's original computational generator/version stays unchanged. `load_agreement` can then validate the same report format with or without that extension; no second loader or archive format is needed. If the package owner instead chooses an envelope, define its one recognized extraction path explicitly in the loader/CLI and test it.

Required evidence: export a multi-pair report's second pair to SVG, retain only the SVG and its sidecar, then produce all-pair CSV and a PNG of another explicitly selected pair using the installed CLI. Tampering with one stored metric still fails; full original bundle hashes and user metadata remain intact. This establishes transferability without promising authenticity of external provenance.

### P1: freeze a meaningful minimum scientific figure

“Figures show one pair” prevents overcrowded multipanels but does not by itself define what a scientific figure explains. Carry the round-1 requirements into the frozen contract:

- Upper axis: reference `W/sqrt(A)` and globally aligned candidate `s W/sqrt(B)`, distinguished by both line style and color. Use the common physical radius fraction `r/R`; both share one accepted canonical model.
- Lower axis: signed residual **reference minus aligned candidate**, using the same x coordinate. State this direction in its label; the scalar distance alone cannot establish the plotted sign.
- Label the curves as comparison-normalized radial shapes, with `kg^(-1/2)` units where shown. Their continuous norms A/B and dimensionless distance d are different quantities. Do not label the residual as a pointwise physical displacement error in metres or imply that its maximum equals d.
- Mark material boundaries, keep material-side segments separate and show the selected domain's extent. Do not connect through fluids or turn a material-side jump into a diagonal line. Dense PREM boundaries need not each carry a full text label.
- Include compact pair identity/index, both n labels, common l, reference/candidate method labels, the frequency values and reference-relative difference, d, alignment sign and any label-mismatch/indeterminate-alignment notice. Include a short agreement-not-accuracy caption. Full names, norms, exact IDs, detailed mesh counts and provenance can remain in the sidecar when space is limited, but the figure must clearly identify where they are retained.

Keep 640×480 as the supported minimum and 1200×800 as default. They are design targets pending actual inspection, not pre-proven layout guarantees. Long PREM domain IDs and arbitrary user names can overflow even a large canvas. Define compact labels, bounded wrapping or clearly marked display ellipsis while preserving complete text in the report. Do not shrink every caption indefinitely to fit or silently remove scientific cautions.

Required evidence: inspect both PNG and native SVG at 640×480 and default size, using a real mantle pair with its long domain identity, a different-n pair, and an indeterminate-alignment fixture. Confirm no clipping/overlap, legible identity/caution, separate material paths and an actual signed residual. SVG must contain vector curves rather than a rasterized plot. Matplotlib may encode text as vector glyph paths; selectable SVG text is optional unless deliberately made a requirement.

### P2: keep small differences visible without making every near-match look bad

The explored d values are small, and a manufactured 1e-9 perturbation is an explicit scientific gate. Fixed decimal output can round a real difference to zero. Independently autoscaling the residual can also make an excellent match look as large as the primary shapes unless the scale is prominent.

Use scientific/adaptive notation for nonzero small values and visible residual tick scales. State that the residual axis is separately scaled. For exact zero residual, use a deterministic finite axis and label zero; do not create NaN limits or fabricate a tolerance band. Report the near-zero-overlap alignment warning independently from tiny residual magnitude.

Required evidence: a nonzero tiny residual remains nonzero in JSON/CSV and readable scientific notation in the figure; the identical-field case produces a finite, correctly labelled plot. This can share the science fixtures rather than add a second numerical test system.

## Installed researcher journey

The frozen quickstart should supply actual inputs, not begin with unexplained A.json and B.json. A small script can create the documented homogeneous model, call the default and owned APIs at mesh targets 20 and 40, save the four complete bundles and generate four agreement reports: cross-method at each resolution and within-method refinement for each solver. Keep the positive lower frequency bound explicit and do not pass the default solver's `n_max` option to the pilot.

Then document the CLI as a distinct useful consumer:

1. Compute a report from the two saved bundles and an explicit T0_2 pair.
2. Re-export a saved report after moving it away from the bundle files.
3. Demonstrate two explicit pairs, all-row CSV and `--pair-index 1` for a single figure.
4. Show the applicable failure: omit pair index for a multi-pair figure, or use a different canonical model. Preserve existing outputs on failure.

Pair indices must be explicitly **zero-based**, with report-order stability. Put `pair_index` in scalar CSV and/or print a short ordered pair summary so users need not infer an index from spreadsheet row numbers. A new interactive selector or generic inspect command is unnecessary. Supplying `pair_index` for JSON/CSV should be rejected if those formats always export all pairs, rather than silently suggesting filtering occurred.

For 64-pair reports, the single-pair plot rule is enough. Do not automatically create dozens of figures or invent a batch-output transaction. A documented loop can export selected pairs. Clearly distinguish an authoritative all-pair report from one selected visual view; the figure sidecar must retain the selected index as well as complete report data.

## A manageable recipe and independent evidence

Keep two levels of evidence:

- **Copied installed recipe:** four small homogeneous solves, four labelled reports, a genuine figure and scalar CSV, plus a Bessel-root frequency check computed independently with installed SciPy. It needs no repository-relative reference files or imports from `scripts/`. It is a complete user example, not a re-execution of the whole physical matrix. Mark the independent check's quantity/reference separately from agreement and refinement.
- **Developer/release scientific gate:** the named sphere, shell and two-domain PREM matrix and the five adversarial fixture families, with the existing independent references where applicable. Expected rows must be enumerated. The report may link their maintained evidence, but the small recipe must not imply it reran those references or certify an arbitrary user model.

Do not copy the full 19-case validation script into every quickstart or install a benchmark framework solely to fetch its reference tables. Likewise, merely attaching an old evidence link is not an independently executed check for the new small example. One analytic frequency reference is sufficient for that example; shape accuracy beyond its actual checks remains unclaimed.

The recipe should create a new output directory and clearly identify individually completed artifacts, or stage the directory using the existing transaction helper if it claims all-or-nothing publication. It should not delete a user's directory on restart. Documentation needs the expected files, meanings and an explicit overwrite/retry policy; not a long shell transcript.

## Reuse and complexity decisions

| Keep/change/remove/add | Decision | Feasible reuse and acceptance |
| --- | --- | --- |
| Keep | Separate same-model T agreement from broad raw comparison | Leave `analysis.compare_bundles` and its interpretation intact; rerun one existing comparison workflow |
| Keep | Pure computation and lazy plotting imports | `export.py` already constructs Figure/FigureCanvasAgg lazily; installed compute/load works without initializing a plotting backend |
| Change | New agreement figures need their own small two-axis layout | Existing comparison renderer retains arbitrary signs, plots U/V/W and auto-stacks pairs; reusing that layout unchanged would violate this report's semantics |
| Add | Exact sidecar reload and pair-index semantics | Reuse strict JSON/hash validation and the existing transactional artifact-plus-sidecar writer; add one end-to-end received-sidecar test |
| Add | Compact labels and explicit residual scale | Inspect real long-ID and minimum-size outputs; decoding alone is insufficient |
| Remove | Automatic multiple figures, general experiment aggregation and website parity | Neither is needed for the installed report/figure journey |
| Keep | Full sources once per report and full report in each output sidecar | Storage cost is explicit and bounded; no source-path dependency or misleading partial-bundle hash |

## Freeze disposition

Revision 1 is sufficiently complete to advance to round 3 after the sidecar layout/reload path, figure semantics and small-versus-full evidence recipe are recorded. These changes make existing promises executable; they do not widen the physical scope. Final round 3 should freeze example commands, expected report/CSV keys and representative visual cases. Actual legibility and installed behavior remain implementation acceptance, not facts established by this design report.
