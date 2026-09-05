# Phase 2 implementation review 2 — maintained language and frozen scope

Reviewer: numerical_research. Date: 2026-09-04. **No remaining English-policy or scoped implementation blocker was found in the audited Python/document/example paths.** The two Python R1 defects were independently rechecked after repair. This is not the final clean-release or browser-lifecycle acceptance claim.

## English-only audit

Scanned README, docs, examples, scripts, Python package source/assets, schemas and first-party vendor notes. Excluded website UI/i18n, authoritative third-party source, virtual environments, dependency trees, caches, old build/dist/egg-info products and intentionally multilingual user-data fixtures.

The first scan found one maintained Chinese file, `docs/reviews/PLAN-REVIEW-LOG.md`; its assigned owner translated it while preserving the original premature-freeze correction, three-round chronology, reopened sufficiency review, adverse findings and superseded proposals. The final source-text scan is clear except `tests/test_data.py`'s intentional Unicode hash fixture. The reviewer's eight assigned documents were already clear and needed no further edits.

Parsed **45 JSON files**, rather than relying only on literal-character grep, so escaped Unicode strings were checked too. The only CJK JSON value is the intended `examples/field-reference.json` hash-case value `\u5730\u7403\ud83d\ude42`; removing it would damage cross-language data verification. Maintained teaching titles/steps/conclusions/cautions, six self-contained projects, catalog/package examples, output sidecars and scientific metadata contain English text. Original mathematical symbols, names and units remain intact.

Checked metadata for all **7 generated lesson PNGs**. Visually inspected the lesson03 field image and lesson06 probe plot, covering the shared 3D annotation and scientific-plot caption paths; both use English. Generator/exporter annotation source and all corresponding sidecars are English. This is not a claim of OCR over arbitrary third-party images.

`PYTHONPATH=packages python scripts/sync_web_assets.py --check` passed for all **7 generated destinations**, including website fixtures and installed package examples. Canonical PREM file SHA-256 remains `cb9567887738a8d24794c2170b80f314ab29b364b79fdcf1aa78777616e02443`; locale/example changes did not alter the scientific bundle.

## Frozen-scope cross-check

| Frozen requirement | Current evidence and boundary |
| --- | --- |
| English maintained artifacts, coherent website locales | Non-website audit above passes. Website strings/lifecycle are owned and independently tested by the lead; this audit does not duplicate live-browser acceptance. |
| Installed examples and package-first path | examples API, CLI example command, one bundle/catalog resource pair, English recipes and synchronized assets exist. Fresh wheel use remains a release gate, not inferred from editable imports. |
| Scene1.0/1.1 and reproducible grids | Previous R1 checks verified unchanged absent/null legacy round trips, mandatory1.1 field, fixed curve formula, actual field/material sampling, clipping, high-degree notice and budgets. Filled-section/GLB CLI regressions are closed below. |
| Scientific-image and CSV production options | Actual CLI tests cover resolved saved defaults, explicit overrides and CSV rejection/preservation. No missing new resource CLI flags: the frozen decision intentionally keeps budgets in Python API. |
| Owned numerical pilot | Exact experimental API, independent SI T assembly, mandatory knots/domains/null labels, explicit quality/provenance, 19 expected benchmark rows, focused tests, executable source recipe and ownership route exist. Independent pilot review and installed proof remain separate integration responsibilities. No default-backend promotion or full rewrite was added. |
| Documentation and long-term gates | Current PLAN distinguishes delivered phase1 from active phase2; numerical ownership and ROADMAP retain T→R→S, independent evidence and conditional acceleration. Historical adverse reviews remain available in English. |

No additional features or architecture were proposed. Full source synthesis, R/S ownership migration, mature kernels, native runtimes and advanced coupled physics remain outside this phase exactly as frozen.

## Independent recheck of the two R1 repairs

The package owner now uses one depth order for filled polygons and grid segments, and shares effective_glb_scene between CLI preflight and the GLB writer.

1. Repeated the exact real lesson03 counterexample at azimuth135°, elevation0°, deformation0, solid surface, no overlays,600×600. Fixed far-cut/uncut outputs have **zero differing pixels; maximum channel difference0**. Files: `/tmp/terra-phase2-python-review/fixed-back-False.png` and `fixed-back-True.png`.
2. Repeated the exact saved legal l40/node-overlay GLB recipe. CLI now preflights **57,910 effective points**, returns **0**, and writes `/tmp/terra-phase2-python-review/fixed-high-cli.glb`; the previous **273,078-point** rejection counted an explicitly omitted overlay. The original requested scene and omission are retained rather than rewriting the project.

Ran the two necessary added regressions: offline face/line physical depth order, and actual CLI saved GLB omissions. **2 passed**, one expected static-color/explicit-omission warning,1.13s. The depth test includes rear-line occlusion and front-line visibility. These checks close the two findings from `phase-2-implementation-r1-python.md`; they do not claim the whole phase or release is complete.
