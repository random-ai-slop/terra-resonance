# Agreement implementation audit 2: package and scientific artifacts

Assignment: AUDIT-PKG/1. Reviewed integrated runtime `e9e660e5e45bfd7960bb33abd80abb8b380afef6`, package version `0.3.0`, against the complete round-2 use review and PHASE-3 frozen contract. This is an independent non-author audit. Only this report and `artifacts/agreement-package-audit/` were written; no runtime changes, tests, commits, website work, release builds or solver runs were performed.

## Disposition

**Initial disposition on `e9e660e5`: changes required for two P2 figure-layout defects.** Scientific content, checked report/CSV authority, sidecar-only recovery and the exercised failure protections passed. Neither finding changes the agreement metric or requires broader scope. After an author fixes the two layout cases, independently regenerate and inspect those cases before closing this stage. Clean-installed delivery remains the subsequent release audit.

## Findings

### P2: character-count truncation still clips valid method and model labels

Location: `packages/earth_modes/agreement_export.py`, `_short` and the method/model `fig.text` calls.

A valid source bundle may contain a wide method or model string. Setting both source model names and `provenance.solver` values to 180 `W` characters, then computing a fresh valid report, produces clipped labels in native PNG and rasterized SVG. This is not tampered metadata or an invalid hash. Full input and output sidecars are retained.

At 640×480, the reference/candidate text extends to x=849.356/850.2 on a 640-pixel canvas. The model footer extends to x=880.2: its display ellipsis and the material-boundary explanation disappear. At the default 1200×800, the reference/candidate text extends to x=1424.984/1428.0. The fixed 57/85-character limits do not bound the rendered width.

Evidence: `artifacts/agreement-package-audit/long-labels-report.json`, `long-labels-640x480.{png,svg}`, `long-labels-1200x800.{png,svg}`, their full-report sidecars and `verification.json` figure bounds. Both native PNG and `rsvg-convert` output were visually inspected. Full user metadata, including a Unicode extension, remains preserved in the sidecars; this is a presentation failure only.

Minimal correction: fit the displayed label into an actual pixel budget using measured text width and visible ellipsis, or bounded wrapping with an explicitly reserved layout. Preserve the role prefix, scientific footer and complete original metadata. Do not silently reject valid source metadata or shrink all text indefinitely. Recheck both minimum and default sizes.

### P2: two notices collide with the accuracy caption on short, wide figures

Location: `packages/earth_modes/agreement_export.py`, width-dependent `font` and the fixed y=.105/.04 footer placements.

A report with both explicit different-n pairing and indeterminate alignment is valid and supported. At 800×480 and 1200×480, the font increases from 9 to 11 solely because of width, while the footer remains at the same vertical coordinates. The warning block spans y=15.678..50.4 in Agg display coordinates and the accuracy caption spans y=4.863..19.2, overlapping by 3.522 pixels. Native PNG warning/caption glyphs share raster row 461; SVG rasterization visibly crowds the second warning against the caption. At 640×480, the same content has a positive 3.422-pixel bbox gap and no shared glyph row.

Evidence: `artifacts/agreement-package-audit/both-notices-{640,800,1200}x480` PNG/SVG outputs and full-report sidecars; `verification.json` text bounds. The fixture derives from the retained density-interface/global-sign report, changes the candidate n label explicitly, and recomputes a valid report. Both notices reflect actual computed flags.

Minimal correction: reserve footer space based on font size, line count and available height, maintaining a positive visible gap. Keep both scientific notices and the agreement-not-accuracy statement. No aspect-ratio ban or new page-layout subsystem is necessary. Recheck 640×480, 800×480, 1200×480 and the default size with both notices.

## Executed user and artifact checks

The independent driver used `.venv`, `PYTHONPATH=packages`, `OPENBLAS_NUM_THREADS=1` and an audit-local Matplotlib cache. It reused SCI1 reports rather than solving models. Native SVGs were parsed to exclude embedded raster images, rasterized with `/usr/local/bin/rsvg-convert`, and compared visually with decoded native PNGs.

| Journey or case | Actual result |
| --- | --- |
| PREM inner-core pair 1 and mantle pair 5 of the eight-pair report | Minimum 640×480 and default 1200×800 PNG/SVG preserve pair identity, l/n, both methods/frequencies, signed relative frequency change, d, alignment sign, units, common r/R, separate residual scale and accuracy caution. |
| Material-sided curves | Mantle starts outside the liquid outer core; inner-core ends at its own boundary. Material lines are separately drawn, with dotted boundaries and no bridge through fluid. Dense PREM boundaries are visible without requiring crowded individual labels. |
| Useful aspect ratios | Mantle 1200×480 and 640×960 remain readable; only the distinct two-notice short-height case above failed. Portrait whitespace is not a correctness defect. |
| Explicit different n and indeterminate alignment | Separate and combined fixtures show the appropriate flags. Near-zero overlap uses the actual +1 indeterminate convention, not a fabricated successful alignment. |
| Tiny nonzero residual | d≈4.88474e-10 remains nonzero in figure and report; the residual axis displays its separate scientific scale. |
| Exact zero | Identical-source comparison gives d=0 and a finite residual axis with an explicit exact-zero label. |
| Sidecar-only recipient | A separate `received/` directory contained only an SVG and its full-report sidecar as scientific inputs. CLI regenerated all eight CSV rows and a PNG of another explicit pair using that sidecar. No original bundle paths were used. |
| Invalid or ambiguous export requests | CLI rejects a multi-pair figure without an index, image selection on CSV, and width 639. No requested artifact was created. |
| Tampering and existing output | A changed stored d is rejected even with overwrite requested. Existing CSV and sidecar hashes remain unchanged. A valid report without overwrite also rejects replacement without changing either file. |
| Recomputed authority versus historical report | A tolerance-accepted stored norm 0.7111111111114669 remains in the full report, while CSV correctly emits recomputed 0.7111111111111112. An explicitly historical producer string remains unchanged; `export_production.renderer_version` correctly records current 0.3.0. Unknown Unicode metadata is preserved and inputs are unmodified. |
| Existing general comparison | The existing `analysis.export_comparison` API still produced a one-row CSV independently of the new metric. |

`run_audit.py` generated the initial cases and performed the receipt checks; its first evidence-serialization attempt encountered a NumPy boolean in this audit-only driver after the operations passed. That driver conversion was corrected. `followup.py` independently reloaded retained artifacts, reran the seven CLI operations, checked historical/recomputed authority, added the wide notice cases and wrote the successful `verification.json`. This was an audit-harness issue, not a package failure. `check_default.py` also exercises omitted width/height, rather than only explicitly passing the documented defaults. No existing unit suite was rerun.

## Source review and limits

The implementation validates/recomputes the full report before plotting or writing scalar data. Plot arrays and CSV values come from that recomputation; stored values accepted within validation tolerance do not become the numerical authority. Continuous normalized W and the signed residual use the accepted material-sided curves. The residual direction is explicitly labelled; the previously reported pre-integration omission is fixed and is not a new finding.

The scalar table includes pair index, exact mode IDs, n/l, mismatch/alignment flags, method labels, frequencies, norms, overlap/d, domain counts and canonical source hashes. Image sidecars retain the complete checked report and original computational producer, adding current renderer/index/dimension/language metadata. Source strings are displayed as literal text and are not altered to manufacture normalized provenance.

Report/source byte limits and the pair/interval limits are checked through the common evaluator. Figure dimensions are bounded before publication. Figure selection is explicit for multi-pair reports; scalar formats reject misleading selection/image options. The existing transaction stages artifact and sidecar, rejects no-overwrite conflicts and restores controlled overwrite failures. This audit directly exercised validation failure and no-overwrite preservation; it does not claim to establish crash durability or every operating-system failure branch. No shared-input mutation was observed or introduced by the exporter.

The scientific agreement matrix and independent rational/Bessel references remain SCI1 evidence. These artifact checks establish useful presentation and recovery, not continuum accuracy, convergence, arbitrary-model validation or proof of external provenance. The small copied installed recipe and clean wheel journey belong to the next assigned release stage; this audit used the accepted repository package explicitly.

## Evidence and author retest handoff

Retained directory: `artifacts/agreement-package-audit/`. `verification.json` records accepted source identity, agreement-source file hashes, artifact/sidecar hashes, actual text bounds, seven CLI results and the authority check. Original SCI1 producer/version/hash values remain inside the real PREM and fixture sidecars. Audit-manufactured cases have their actual current producer and newly computed hashes; they are not labelled as original SCI1 outputs.

Author acceptance: use `long-labels-report.json` and `both-notices-640x480.png.json` as checked inputs; generate the listed minimum/default/wide figures with the fixed renderer. Retain before/after evidence, visually inspect PNG and native SVG rasterization, and measure a positive gap/contained text. Keep complete sidecar metadata and all current scientific captions. There are no requested numerical changes or new product features.


## Independent repair closure

**Both P2 findings are closed on integrated runtime `0779d9600f46eef341fad65767d5920d087814cb`** (native author commit `67c91c9235ccebd41ce10d0084b5a2aa999ab9a2`). The historical findings and original failing artifacts above remain intact. This stage now passes; clean-installed/release acceptance remains audit 3.

I inspected the scoped renderer diff and author handoff, then independently regenerated exactly the six affected cases from this audit's retained full reports. The author evidence was contextual comparison only, not substituted for this run. `repair-closure/verify.py` verified the checked-out producing commit and exact committed exporter bytes before rendering. Exporter SHA-256 is `47ddbb87b3318b08a5999da24c349f8f9c88f398a05ac640e2074efca5be12f8`.

For each case, the run exported a native PNG and native SVG, reloaded both complete sidecars, decoded the PNG, excluded embedded raster images from the SVG, and rasterized the SVG at matching pixel dimensions with `rsvg-convert`. I visually inspected all twelve resulting native/vector-raster views. Default-size calls omitted width and height. No solver, test suite, build or runtime edit was performed.

| Independent repaired case | Rightmost figure text (px) | Footer-to-accuracy gap (px) | Axis-to-footer gap (px) |
| --- | ---: | ---: | ---: |
| long-labels-640x480 | 605.200 | 9.000 | 13.850 |
| long-labels-1200x800 | 1139.984 | 11.000 | 36.858 |
| both-notices-640x480 | 580.747 | 9.000 | 9.000 |
| both-notices-800x480 | 719.391 | 11.000 | 11.000 |
| both-notices-1200x480 | 741.391 | 11.000 | 11.000 |
| both-notices-1200x800 | 741.391 | 11.000 | 19.497 |

All figure text lies inside the canvas. Both long method labels and the long model label retain a visible display ellipsis; the full “material boundaries dotted” suffix is visible. At minimum, wide-short and default sizes, both scientific notices have clear separation from the accuracy caption and radius label. The adjustment does not remove the residual direction, separate-scale warning, units, pair identity or agreement-not-accuracy statement. Native vector curves remain legible.

Every output sidecar retained the exact original source bundles, pairs, rows and computational generator version; the 180-character method/model strings and arbitrary user metadata remain complete. Input mappings were unchanged. The new rendering metadata records the resolved dimensions while the scientific source identity remains intact.

Closure evidence: `artifacts/agreement-package-audit/repair-closure/verification.json`, `run.log`, `verify.py`, and six PNG/SVG/full-sidecar sets with `-vector.png` rasterizations. The JSON records producing SHA, exporter identity, source/output/sidecar hashes, text bounds and measured gaps. The independently measured gaps agree with the author handoff. No remaining issue was found in this bounded repair recheck; no new feature or scientific change is requested. The reviewer returns to idle.
