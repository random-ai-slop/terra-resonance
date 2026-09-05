# Implementation review log

Planning reviews and development preflights are separate from these sequential post-implementation rounds.

## Round 1 — closed

Three independent adversarial reviews covered numerical interfaces, project contracts, and output reconstruction. Reports: `implementation-round-1-numerics.md`, `implementation-round-1-contract.md`, `implementation-round-1-outputs.md`.

Fixed fluid–fluid gravitational density sheets; made analytic validation gates reject missing modes, wrong identities and frequency errors; rejected noninteger gravity flags at the API boundary. Restored independent probes and exact sampling steps, completed project defaults, preserved metadata, separated toroidal dispersion branches by solid domain, and included actual analysis state in SVG provenance. Explicit mode comparisons now respect user-selected pairs; adaptive GLB animation is no longer constrained by video sampling; weak nonzero components retain their nodes.

Independent numerical re-verification reproduced the original density-jump counterexample and demonstrated convergence to the smooth-interface limit. Fault injection now fails all three analytic-gate corruptions. Python: 53 passed; TypeScript: 13 passed; owned frontend source lint and type checking passed. Browser file import restored a point-independent probe at (12°,34°,0.7R), start 123 s, step 0.1 s and three samples, including omitted defaults. Updated PREM bundle hash: `e26a5121a8ac0f448b81c66d5c0b4fba241116f18bf7de96cd6f758608478ef9`.

The lint command targets maintained application/science source; generated shadcn component catalog is not rewritten to satisfy unrelated lint rules. Test source is checked by TypeScript and the test runner.

## Round 2 — closed

Opened only after Round 1 fixes and independent verification completed. Focus: real user workflows, hostile/edge-case imports, playback state, output specifications and scientific consistency at API boundaries.


Fixed no-clobber output commit races, truthful scientific ExportSpec records, floating-point half-open probe windows and format/suffix mismatches. Browser output recipes now preserve every parameter and independent omission flag, and use the saved project directly; actual seven-format CLI execution passed. Ambiguous model comparisons require explicit IDs. Probe spatial caching reduced a representative 32-term/10,000-sample trace from seconds to milliseconds without changing field values. Numeric drafts support negative/exponent entry, short-window tick labels remain distinct, and browser scientific files and provenance travel in one ZIP.

Independent threaded file/directory races produced exactly one winner without deleting another producer's output. PNG/probe dimensions, transparency, annotations and half-open endpoints were independently read back. Browser file input/save/error recovery and PNG/SVG/GLB ZIP readback passed. Final R2 checks: 60 Python tests; 17 TypeScript tests; type checking and owned source lint. Details in the four Round 2 reports.

## Round 3 — closed

Opened after all Round 2 fixes and independent re-verification. Focus: clean installation, complete case workflows, release evidence and maintainability, production dependencies/build and deployed static application.


Quality records now reject inconsistent model hashes, quantities and frequency errors; Python/TypeScript/Schema agree on safe integer-valued JSON numbers without changing artifact identity. Six teaching scenes use analytically bounded fixed color ranges, visible material sections and contrasting node lines, with zero clipping over the validation sample. Material-side selection and full teaching metadata close the lesson-to-saved-project workflow. Standalone source/test fixtures and sdist contents were repaired. Production dependencies were updated, and a real narrow-screen canvas-layout defect was fixed.

Final checks: 62 Python tests; 19 TypeScript tests; type/lint/static build; independent wheel and sdist installation outside the repository; seven-format media readback; six-case evidence; desktop/narrow production browser operations. Cross-author review independently checked the new material-side tolerance, fixed color envelopes and benchmark consistency. Native Blender remains an explicitly unexecuted optional environment, with tested GLB and an import script supplied. All three sequential implementation rounds are closed; website delivery and final archive bookkeeping follow these verified sources.
