# Public delivery round 3: actual platform and portability evidence

The public source at 6396efa passed hosted CI33946450579 on Ubuntu with Python3.11/3.13, installed wheel/sdist checks and the website job. Pages33946583655 successfully deployed that run's static artifact. These are actual hosted results, distinct from prior local checks.

## Reproduced portability defect

A separate source copy omitted `.openai/hosting.json` and reused installed npm dependencies. Its Pages build failed before compilation: Vite's configuration bundler resolves a literal dynamic JSON import even when the runtime Pages branch returns first. Conditional control flow alone therefore did not satisfy the documented no-Sites-metadata promise. The earlier green CI had kept that file and could not expose this failure.

The fix reads hosting JSON through Node's filesystem only inside the Sites runtime branch. CI now moves hosting metadata outside its temporary website checkout before the existing Pages build. This strengthens the same build gate instead of adding a redundant second frontend build or a mock test. Sites root-path compatibility is checked separately because it uses that runtime read.

This invalidates earlier website build acceptance for the final source revision, not the numerical/data evidence. The affected build checks and final hosted CI must run again before tagging0.2.1. The installed scientific package implementation is unchanged by this correction; its current-version artifacts are still built and verified by the release gate.

## Distinct outcomes from three reviews

The initial science/package/path review corrected combined-license metadata and public live-state treatment. The implementation review exposed the pending-deployment displacement race and required retained queuing. Actual clean-environment execution exposed eager configuration loading after source review and ordinary CI had passed. A separate CLI artifact journey verified the corrected generator-version provenance. Each change has a specific failing input or artifact boundary; no numerical campaign was rerun for a website configuration change.

Final source/release/deployment IDs and artifact checks are observable in GitHub Actions/Releases and the website deployment manifest; live task IDs stay in local coordination rather than a mutable packaged task ledger.
