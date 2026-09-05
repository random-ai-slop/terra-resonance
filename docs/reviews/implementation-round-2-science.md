# Implementation review 2: browser science, probes and research outputs

Reviewer: numerical_research. Date: 2026-09-04. Historical review after R1 repairs, initially read-only across `data.ts`, `field.ts`, `Charts.tsx`, `Workbench.tsx` and the Python contract. **Initial conclusion: two necessary repairs and one useful small improvement before sequential R3.** Later repair evidence is retained below.

## S1 — P2: comparison silently chose the first same-label candidate

Historical location: `apps/web/components/observatory/Charts.tsx:460`, `comparison?.modes.find(...)`.

Reproduction: copy real PREM S0_4 to a new ID with identical family/l/n/domain, multiply its frequency by 1.02, mark quality unverified and prepend it. Both entries passed validateBundle; candidates were `[user-selected-crossing-branch, S0_4]`. The first-entry search selected the modified record despite the original exact-ID match also existing, displaying +2%. File order alone changed the apparent scientific comparison.

This differed from repaired R1 Python explicit-ID rejection: the browser never requested disambiguation and SVG metadata omitted the actual candidate ID. Proposed repair: suppress comparison for nonunique candidates until explicit ID selection; allow explicit pairing across custom domain names like Python. Preserve both IDs/hashes and normalization in SVG provenance. A unique-label suggestion remains useful but is not physical branch tracking. Necessary regression: reorder candidates without changing an explicit pair; ambiguous unselected state must not fabricate Δf.

## S2 — P2: project round trips destroyed independent omission choices

Historical locations: Workbench lines157–160,235–237,1099–1101.

Reproduction: lesson6 with format glb, omit_arrows=true, omit_geography=false, omit_analysis_overlays=true passed parseProject. Geography was disabled, so this was an executable explicit recipe. loadProject reduced three flags through AND to one false flag; saving or exporting rewrote all three to false. A load/save therefore lost chosen omissions and made the next export reject the previously approved capability handling. Setting the single switch true instead omitted a previously unapproved layer.

Keep the three imported ExportSpec fields independently. A user-triggered “allow all omissions” shortcut may update them together, but loading/saving must not collapse state. Preflight each overlay against its own flag. Verify an untouched mixed true/false recipe survives round trip and export without a larger settings system.

## S3 — useful improvement: cache each probe term's spatial field

Historical Charts lines270–287 repeatedly called evaluate per timestamp, recomputing modeScale, interpolation and harmonics. Real PREM at one surface point with 10000 samples and 32 legal alternating-mode terms, independent phases and amplitude1/32 took 1.68–1.80 seconds synchronously. Hoisting time-independent spatial work reduced an exploratory equivalent temporal loop to 29–32ms. Derivative/coefficient/point edits invalidate the trace memo, making this a visible stall. Python already separated space/time.

Add one small sampleProbe helper: compute each nonzero term's material-side spatial vector once, then reuse analytic temporal values/derivatives. No worker/cache framework/dependency is needed. Skipping zero-amplitude terms also avoids irrelevant sampling warnings. Verify numeric equivalence and side choice, not fragile millisecond assertions.

## Positive checks and limits

- True 0S2, Q37, amplitude .7, phase .43, t523/3421s and central difference h=.01s verified temporal derivatives: maximum first-order error 8.29e-14, second-order 5.97e-17. Damping derivatives and cosine phase signs were correct.
- Samples use explicit start_s+i*step_s, separate from playback cursor. ProbeSpec accommodates inclusive teaching endpoints and CLI-generated half-open sampling without hidden time replacement.
- Normalized/raw choice reaches field evaluation. CSV provenance records normalization, derivative and units without calling mass-normalized coefficients calibrated meters.
- Imports above 10000 probe samples fail before updating the current project; it remains intact. This is an explicit browser resource limit, not license to truncate.
- Quality labels explicitly concern the first mode, and validators require actual mesh/benchmark evidence rather than trusting a status string. Earlier T-domain catalog repairs were not counted again.

## Repair recheck: S1 and S3

S1 was implemented in comparison.ts: only a unique identity match is automatic, ambiguity returns null, Charts exposes a candidate-ID selector and permits different custom domain names. Explicit selection binds to the comparison bundle object and current reference ID, so a new import cannot reuse stale pairing. SVG provenance stores both IDs, hashes, selection method and normalization.

S3 was implemented in field.sampleProbe, calculating one spatial vector per nonzero term on the selected material side and reusing analytic temporal derivatives. The same 32×10000 case measured about 10.7ms. Raw second derivatives at indices0/131/7823/9999 matched the original evaluate path with maximum difference0. Timing is local evidence, not an automated threshold.

Two focused chart-science regressions cover ambiguous/reordered/cross-domain pairing and cached probes against the Python fixture across Q derivatives, center/poles, both interface sides and raw normalization. Together with science-parity, 7 tests passed; TypeScript check and affected lint passed.

Following the lead review's browser multi-download blockage, Charts SVG/CSV switched to one downloadArtifact ZIP containing image/data and provenance together. Actual pair identities remain in that archive. The lead owned the helper and browser download verification.

The visual agent repaired S2's independent Workbench omission fields; this report does not claim that agent's verification. This repair section alone did not close the whole R2 round or assert three implementation rounds were complete.
