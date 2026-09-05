# Implementation review, round 3: scientific/API/release contract

Historical record. Reviewer: scope_review. Date: 2026-09-04. Following closed R2 (60 Python / 17 TypeScript tests), this round began with independent read-only review and small counterexamples. It did not rerun N1–N6. Other reviewers owned clean-wheel checks, six teaching workflows and production deployment.

## C1 · P1 · Contradictory frequency evidence could retain passed status

Python `data._validate_quality` and TypeScript `validateQuality` checked relative_error≤tolerance without recomputing error from the current frequency or checking evidence model identity.

Actual counterexample: published PREM R0_0 had frequency_hz=0.0008136079958129652. Independently changing benchmark.model_hash to 64 zeros, reference_frequency_hz to 0.0016272159916259305 (an actual 50% error), or quantity to `unrelated quantity` still passed Python validation and retained benchmark_checked. The old relative_error=0.0005356027279050934 and tolerance=0.005 remained. Browser logic had the same omission. Stale evidence could therefore survive a model/frequency edit while the interface said its frequency benchmark was checked.

Minimal fix: restrict wire-1.0 quantity to frequency_hz, compare model_hash with the current canonical model hash, and recompute `abs(f-reference)/reference` with explicit rounding tolerance. Keep mesh and benchmark evidence independent. A source string is not a signature, and no new trust system is needed. Three counterexamples plus unchanged real PREM validation suffice.

## C2 · P2 · Integer-valued JSON spelling differed across languages

Python `_integer` accepted only int objects, while TypeScript used Number.isSafeInteger and JSON Schema used integer. Changing the first published mode.n from JSON 0 to 0.0 made Python reject it and the browser accept it, despite identical JCS identity. Degree, m, trajectory/probe counts and ExportSpec integers had the same issue.

Minimal fix: wire validation accepts finite safe integer-valued floats without changing input or identity. Consumers locally convert harmonic/array/sample indices; resolved ExportSpec may return native integers in its new object. Continue rejecting booleans, fractional values and unsafe integers. The direct solver's strict Python gravity API is a separate request contract and retains its R1 fix. Regressions must evaluate fields and export, not merely pass validation.

## Checked scientific scope and maintenance boundaries

- Production uses private vendored Ouroboros v6.0 commit `fa63363040a28c08d9fe2bd7d05dcc823d90dd1e`, without install-time retrieval of master. README/NUMERICS restrict claims to executable isotropic, spherically symmetric, nonrotating elastic R/S/T and three gravity levels. Experimental linear Q is not full Maxwell/Burgers support.
- Solid/fluid topology and the discrete fluid constraint space are explicit. NUMERICS does not claim a general continuously stratified fluid gravity-wave spectrum. N3 six-topology evidence, independent N2 raw outputs and R1 density-jump evidence remain available. General solves default to unverified; missing refined counterparts warn rather than establish convergence.
- The 47-mode catalog has per-mode frequency evidence from MINEOS frequencies and independent inner-core T shooting. These checks do not imply equal accuracy for eigenfunctions, potentials or source amplitudes.
- Scanning packages, vendor and scripts found no default `/Users`, `/home` or `/opt` paths. Materials, palettes, geography and schemas are packaged resources; source scripts resolve ROOT from __file__. MINEOS is an explicit optional recalculation path. Clean-wheel evidence is tracked separately.
- Three schemas have one package source with root-directory links. Probe/Export reject unknown parameters; other metadata survives. Schema does not replace normalization, hash, cross-field or resource checks. C2 records the discovered integer mismatch.

## Minimal release cleanup

1. ACCEPTANCE still described a planning draft rather than a passed report. After actual R3 closure, add gate→command/report/artifact evidence and final status. A table's existence is not a pass. Keep unexecuted native Blender use explicitly outside local verification claims.
2. vendor/README described kernel/old-pipeline patches while later saying that subset was not distributed. Align it with the actual subset and record the R1 fluid-material-density-sheet correction. Runtime PATCHES already recorded it; this was stale maintenance prose, not a numerical recurrence.

At initial review, C1/C2 blocked closure. No new architecture or release feature expansion was needed.

## Fix verification

C1/C2 were fixed. Python and TS both check frequency_hz quantity, current-model JCS hash and recomputed relative frequency error within `64*binary64_eps*max(1,error)`. TS uses explicit dependency @noble/hashes 2.4.0 rather than handwritten SHA. Integer-valued floats preserve input/identity and convert locally in indexing, fields, trajectories and probes. The separate strict solver API remains. Schema quantity and DATA documentation were updated.

Thirty affected Python data/field/export/CLI tests passed, including a real trajectory PNG and integer-valued-float Probe CSV. All 19 TS tests, tsc and scientific/UI lint passed. A comparison test that changed frequency but retained benchmark evidence is now correctly rejected; its synthetic candidate was changed to explicitly unverified. Real PREM, all modes and six self-contained lessons still validate. PREM file SHA matches numerics.json; scientific assets and project hashes were not rewritten. C1/C2 had no remaining blocker.

## Cross-author closing review

- Workbench material-side choices use r∈[r0−64epsR,r1+64epsR], matching validation/evaluation. Automatic choice means outer side. Explicit side selection preserves other point fields; changing radius removes stale layer_id.
- Initial lesson 3 uses the same catalog scene/probe/export through parseProject after bundle-hash validation. It is not a separately handwritten initial field. Initial/preset code copied only five teaching strings and omitted verification (including color formulas) and variants; this was sent to root for minimal metadata preservation and subsequent integration verification.
- Selected color bounds match real harmonics: R uses Y00, S uses l=2 radial displacement, T uses the phi gradient/√6. Cutaways examine radial extrema on all sides. Equal-amplitude quadrature ±m=2 travelling terms can use one-term bounds; ordinary sums use the sum, then a fixed 1.05 margin. Additional 17×32 angular samples, seven times, layer endpoints/midpoints and explicit sides produced peak/color_limit ratios 0.952381, 0.952381, 0.952136, 0.952231, 0.952381 and 0.826494. Sampling is supplementary; analytic formulas supply the all-time bound.
- Dark teal offline nodes contrast with the light signed-zero background. They use unchanged time coefficients, gains, root locations and material-side connectivity. A fragile pixel test was unnecessary for this color-only change.
