# Implementation round 1 — scientific state and reproducible contracts

Historical record. Reviewer: visual_research. Scope: other implementers' Python data/fields, TypeScript data/field, Charts/Workbench project state, and scientific figures. This was a formal post-implementation review; planning and pre-implementation checks were not counted. Findings were sent to the lead maintainer, and subsequent verification is recorded separately below.

## Conclusion at initial review

Independent analytic tests supported the main field conventions: canonical mass normalization, material-side selection, regular center, Q-envelope derivatives, and fixed modal scales. No blocking formula change was identified. Four groups of import/scientific-output problems meant that successful loading alone could not certify project save/restore acceptance.

## R1-C1 — P1 — Linked point overwrites independent ProbeSpec and reverses a legal default

Reproduction: make_project(bundle, default_scene(bundle), probe={latitude_deg:35, longitude_deg:105, start_s:0, step_s:5, sample_count:20}). This is valid: Scene.point is null and the independent probe omits normalized/radius_fraction/derivative to use their defaults.

TypeScript parseProject returned successfully, but Charts' probe memo read only scene.point, produced an empty series, and an effect called onProbeChange(null), erasing the independent request. A different scene point silently moved the probe. The expression initialProbe ? !initialProbe.normalized : false also interpreted absent normalized as raw=true, although its default is normalized=true.

Required fix: preserve independent coordinates, side, start, step, count, and normalization. Synchronize position only when the user explicitly links it to the visible point. Import cannot change a valid scientific request. Consumers should receive new objects with resolved defaults. Root took ownership of the Charts change.

Acceptance counterexamples: import/save the null-scene-point project with probe retained and raw=false; also test differing coordinates/material sides. The final half-open sample remains start+(count−1)*step.

## R1-C2 — P1/P2 — TypeScript default expansion and required Scene.point fields disagree

The reproduction returned export:{format:'png'} unchanged even though validateExportSpec had computed defaults. Workbench therefore received undefined width/height/annotation instead of 1200×900 and enabled annotation. Valid probe defaults were likewise validated without being supplied to UI consumers needing full fields.

Another case gave Scene.point only latitude/longitude. Python rejected it with “scene.point.radius_fraction is required”; TypeScript's generic validatePoint accepted it. Rendering then multiplied position by undefined, so this was not a valid reproducible scene.

Required fix: explicit radius_fraction for Scene.point, while ProbeSpec retains its documented defaults. parseProject returns a new project with resolved probe/export objects, preserving unknown top-level, scene, and provenance metadata without modifying input. Add shared rejection cases.

Workbench also reduced three independent omission flags to their AND, then saved all three as the same value. An otherwise valid omit_arrows-only request became three false flags. Preserve independent values unless the user explicitly operates a master control. Root owned that correction.

## R1-C3 — P1 — Dispersion connects fluid-separated solid domains into one branch

Default PREM reproduced the problem. Charts grouped by family+n although equal n/l T modes can occupy different solid domains. The plotted 0T data included:

| l | Inner-core frequency, mHz | Mantle/crust frequency, mHz |
|---|---:|---:|
| 2 | 1.135957083 | 0.379715373 |
| 3 | 1.751621999 | 0.586601119 |
| 4 | 2.305549509 | 0.765822800 |

Connecting both columns at each l and then across degrees created a zigzag that represented no physical branch. Correct numbers in the catalog did not excuse the misleading curve.

Required fix: include solid_domain_id in the branch key and label inner/outer solid domains, or use discrete points without claiming tracking. Comparisons also retain domain identity and never superpose different models physically. Root owned the Charts correction.

## R1-C4 — P1 — Scientific SVG lacks independent analysis state

Charts.saveSvg recorded only scene, bundle_hash, tab, and bundle provenance. It omitted raw/illustration eigenfunction selection; independent probe coordinates/start/step/count/derivative/normalized; and the comparison's second bundle hash, mode identities, frequency difference, and normalization. SceneSpec cannot reconstruct these independent inputs.

Required fix: preserve the actual plot state and units in the SVG sidecar. Use complete ProbeSpec; comparison records both hashes, model names, mode IDs, and canonical/illustrative scaling; eigenfunctions identify their fixed divisor or mass normalization. Axis labels alone do not replace sampling inputs. Root owned the change.

## Checked without expanding scope

- Python harmonic combination, zero radial T, spherical R, S1 center, default/explicit interface sides, and damping derivatives already had independent cases; no new formula error was found.
- Both importers rejected nonfinite JSON, duplicate keys, invalid quality evidence, and invalid materials. Unknown project metadata already had a preservation mechanism; no new metadata store was needed.
- Using each model's r/R in comparisons was correct. Automatic mode tracking, dual viewports, and more points were not required.
- The Node reproduction used node --import tsx /tmp/terra-contract-review.mts. The tsx CLI could not create IPC under the sandbox, so the loader performed the same read-only check without broader permissions.

## Minimum post-fix checks

1. Independent probe round trips: defaults, differing points/sides, one sample, and nonintegral time steps.
2. Consistent Python/TS rejection of a missing scene-point radius and equivalent expansion of valid probe defaults.
3. Separate PREM solid-domain dispersion branches, including exported SVG legend/metadata.
4. Reconstructible state in all three scientific SVG sidecars, without pixel/font identity requirements.

These genuine counterexamples bounded the work; no unrelated features or implementation-mirroring test suite was added.

## Round-1 verification record

- TS parseProject now returns new resolved probe objects with radius=1, derivative=0, normalized=true and complete ExportSpec. Explicit null is not an omitted default and fails. Scene.point requires radius_fraction. Unknown top-level metadata and caller input are preserved.
- Added necessary cross-language cases for independent points, one sample, nonintegral times, defaults, and null. Five science-parity tests passed; related browser export tests brought the total to 12. Type checking and data.ts lint passed. A locally explained dynamic-JSON any assertion remained; global lint was not weakened.
- Source review confirmed independent probe coordinates with an explicit link switch, SVG probe/normalization/comparison inputs, and family/n/solid_domain_id branches. This was code/data verification, not a claim of completed browser interaction regression.
- Two remaining root-owned edges were noted: imports above 10,000 samples must fail explicitly instead of clearing probes through empty displayed arrays; preserve the original step until a user changes the window/count rather than round-tripping it through duration/count and changing its last floating-point bit.

Closure: root added preflight rejection above 10,000 browser samples and retained independent probeStep until window/count changes. The updated default bundle and six-case catalog were synchronized; four resource byte hashes passed, recorded in docs/validation/assets.json. The then-current canonical bundle hash was e26a5121a8ac0f448b81c66d5c0b4fba241116f18bf7de96cd6f758608478ef9. The media recipe was rerun and docs/validation/exports.json updated. Contract findings in this report were implemented; root verified browser behavior during integration. This round did not replace the following two reviews.
