# Phase 2 implementation review 2: localization lifecycle and exports

Read-only source review on 2026-09-04 of `apps/web/lib/i18n/` and `apps/web/components/observatory/`. No Site files were edited and no browser automation was performed by this reviewer. The lead's real browser observations are separate evidence.

## Finding

**P2 — An owned fallback phrase bypasses localization.** In `Viewport.tsx`, zero-component detection inserts `patch.layerId ?? 'current shell'` into a set, then joins that set into the raw `regions` parameter of the localized diagnostic. For an identically zero shell component without a layer ID, a Chinese diagnostic therefore ends with the English product phrase `current shell`. Actual user layer IDs must remain unchanged, but this synthetic fallback is maintained interface prose.

Minimum fix: retain layer IDs as raw values, while representing the current-shell fallback with a nested message token, or use a separate localized shell diagnostic. Keep status as tokens until rendering so an already-visible notice changes language without recomputing geometry. Do not translate arbitrary layer IDs or use string substitution over completed diagnostics.

This is a narrow language-completeness issue, not a physical-state or export-data defect. No new feature is required.

## Verified source behavior

**Locale lifecycle.** The provider resolves a valid URL language before a saved preference and otherwise chooses English. Both storage reads and writes tolerate access failure. Locale changes update the existing URL using `replaceState(history.state, ...)`, preserving unrelated query parameters and the fragment, and `popstate` restores the preference. The provider withholds initial children until initial resolution, then keeps the same subtree mounted. Locale is not a Workbench/Charts key, does not enter data-fetch dependencies and does not enter Viewport construction/configuration/animation dependencies. The document language, title and description follow the selected locale.

**Scientific state.** Viewport engine construction runs once; callbacks are refreshed through refs. Scene/bundle changes and playback changes have separate effects. A translation render does not configure geometry, restart playback or reload scientific data. Charts is keyed only by an explicit project revision, while probe controls store numerical values and retain their sampling dependencies independently of locale. These source properties agree with, but do not replace, the lead's reported browser switching checks.

**Diagnostics.** DiagnosticError retains a canonical English Error message plus a key/parameter token. ContextualError retains its cause rather than flattening it. Workbench initial loading, imports and export operations store the original error object. Charts forwards the original exception. Viewport retains typed status tokens and forwards original errors through current callback refs. Consequently in-flight failures and previously visible owned diagnostics can be formatted in the current locale. Unknown technical exceptions retain their original detail within a localized context. No asynchronous pretranslation or identity-losing callback was found in the reviewed paths.

**SVG export selection and labels.** `Charts.saveSvg()` now resolves the selected tab's `aria-controls` and queries `.plot-wrap svg` within that panel. It therefore selects the scientific plot rather than the Select-control icon. ScientificPlot produces English title, axis, legend and accessibility equivalents through explicit export attributes from the same series/label inputs; its displayed labels use the UI locale. The export call passes the selected SVG to the English artifact builder and records `annotation_language: en`, scene, normalization, derivative, probe/comparison request and provenance. This review covers those callers and label generation; the lead separately reported an actual Chinese-interface probe SVG download containing three curves with English labels and no Han text.

**Teaching metadata.** Built-in recognition checks the exact bundle hash, existing lesson ID and canonical equality of the complete teaching metadata with the catalog entry excluding scene/probe/export. Added or edited metadata prevents recognition; scene/probe edits do not. Localization returns a display copy for recognized lessons. Loading preserves project extras, and saving spreads those original extras rather than localized text. Unrecognized teaching notes are displayed verbatim as imported JSON. There is no ID-only translation of user or legacy text.

**Controls.** Localized labels retain stable generated accessibility IDs. Select item keys use stable values, and number-input drafts are not keyed by translated labels. A language switch does not intentionally commit/reset a draft. The preset buttons do use translated titles as keys, but remounting those stateless buttons does not reset scientific state.

## Conclusion

The locale/state and canonical-English artifact boundaries are coherent and narrowly implemented. Resolve the small current-shell diagnostic phrase before claiming complete owned-message translation. No additional localization framework or scientific-state redesign is warranted by this review. Browser layout, download decoding and clean package installation remain the separately assigned integration gates.
