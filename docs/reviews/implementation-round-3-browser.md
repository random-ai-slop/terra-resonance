# Implementation round 3 — production browser and dependencies

The final static output was served by `npm start` at 127.0.0.1:4180, without the development server or a Worker. Both the embedded browser and Edge loaded the actual static bundle.

## Release improvements

- Updated compatible frontend/build dependencies after inspecting npm advisories. The final audit reports zero currently known advisories; exact versions and the prior result are recorded in `docs/validation/frontend-dependencies.json`. This is not a guarantee against unknown vulnerabilities.
- `npm start` now previews the real static directory through a small dedicated Vite configuration; it no longer assumes a Worker output exists.
- Initial loading and the third teaching preset use the same validated scene. All teaching metadata, including verification and variants, survives saved projects.
- Added explicit material-side selection at a fixed radius. Only layers containing the radius within the same 64εR tolerance as the scientific evaluator appear.
- A real resize to 390×844 exposed canvas intrinsic height feeding back into CSS grid sizing, making the globe crop horizontally. Absolutely positioning the canvas within its controlled viewport fixes the layout without changing camera semantics. Recheck: document/client widths both 390, viewport 390×436.69, entire globe visible.
- Radial l=0 displays its only valid m=0 instead of a misleading movable slider.
- The standalone website source includes its license, instructions and synchronized scientific test fixture.

## Actual checks

Desktop and narrow layouts were visually inspected. The liquid-core lesson exposed the liquid and solid CMB sides at exactly r/R=0.5462250824046461. Selecting the solid side and downloading a project produced scene.point.layer_id=probe.layer_id=prem-02, the unchanged radius, and complete teaching verification/variants; these were independently read from disk. Playback advanced physical time and continued across a reference-sphere toggle; pause and presentation enter/exit worked. The final static origin produced no captured application console errors. Temporary viewport overrides were reset.

The final code passed 19 TypeScript tests, type checking, owned source lint and production static build. Python release checks and six-case evidence are recorded in the other Round 3 reports. The build retains a large-chunk advisory for the 3D/science viewer; performance and correctness were checked on the actual default workload. No server-rendered public runtime is deployed.
