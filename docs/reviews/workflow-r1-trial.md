# Workflow design round 1: a real development trial

Reviewed the current ROADMAP, NUMERICAL-OWNERSHIP, public package API, comparison module, perturbation recipe and phase-2 evidence. This is a proposal for the next development trial, not authorization to implement any candidate or a claim that the team workflow is already validated.

## Recommendation

Build a **reproducible cross-solver toroidal agreement report** using the existing default solver and the independently owned T pilot. A researcher should be able to answer: “For this same material model and these explicitly selected modes, do the two methods agree in frequency and radial shape, and what does refinement change?”

This is a real gap. `compare_bundles` currently supplies frequency differences and untouched U/V/W curves with arbitrary signs. The pilot validation script computes selected shape errors internally, but installed users cannot obtain a reusable, traceable shape-agreement report. An agreement report supports the numerical-ownership promotion gate without pretending agreement between two codes establishes physical truth.

The trial is large enough to exercise numerical design, an independently reviewed analysis contract, package/CLI integration, scientific figures, documentation and clean installation. It is smaller and safer than introducing another physical family or a full external-file adapter at the same time.

## Candidate comparison

| Candidate | Real user result | Scope and risk | Disposition |
| --- | --- | --- | --- |
| Cross-solver T agreement report | Quantified, sign-independent shape and frequency comparison for explicitly paired modes on the same physical model, with refinement and independent-reference evidence | Medium. Radial quadrature, interfaces, support and arbitrary signs require real design; existing solvers and exports provide the rest | **Recommended** |
| Installed finite-difference material study | Select a solid layer's fractional Vs perturbation and obtain h/h2, mesh/refined-mesh frequency sensitivities with all underlying requests/results | Medium to large. Existing homogeneous recipe is useful groundwork, but arbitrary layered studies expose branch loss, near crossings and derivative cancellation | Strong alternative if an immediate sensitivity question is prioritized |
| Owned radial elastic/acoustic pilot at g=0 | A second independently assembled family with canonical bundles and analytical/reference checks | Large for a workflow trial. Solid/fluid interfaces, radial weak form, labels and independent shapes are substantial; adding gravity makes it larger still | Defer until the workflow has survived a complete smaller research release |

A MINEOS adapter is valuable but is not the cheapest substitute for the first candidate: checked-in text references are frequency tables, not a complete verified eigenfunction interchange specification. Importing frequencies alone cannot exercise the intended visualization/normalization journey; silently inventing missing eigenfunctions would be unacceptable.

## Recommended trial boundary

### Required user journey

1. Load one documented homogeneous or layered model and solve its T modes through both existing APIs, keeping complete requests and provenance.
2. Choose explicit mode pairs and create a report with frequency differences, sign-aligned mass-weighted shape error/overlap, material support and method identity.
3. Repeat the requested modes on a refined mesh. Separate mesh changes, code-to-code agreement and independent reference errors in the output.
4. Export a native scientific SVG/PNG plus machine-readable JSON/CSV and provenance. The plot retains interfaces, shows which sign was used for display and never changes either input bundle.
5. Reproduce the shipped example and a small custom model from an installed wheel outside the repository.

The report needs an installed API and a CLI path, rather than just another source-tree script. The existing source example remains an entry point for reproducible scientific evidence.

### Minimum contract decisions before coding

- Start with T modes and identical physical model data/domain support. Explicitly reject an inapplicable metric while retaining the existing general side-by-side comparison function. Do not quietly apply a common metric across different radii, density profiles or disconnected supports.
- Specify exactly how model eligibility is checked; do not treat equal display names as proof. Prefer the existing model identity when sufficient. Do not create a new general model-matching system for this trial.
- Define the radial measure, common integration partition and endpoint/interface rules from the canonical piecewise-linear field contract. Keep both material sides. One global sign is free; separate sign choices per layer are not.
- Publish the metric equations, units, returned alignment sign and behavior near zero norm. Separate raw canonical curves from optional aligned plotting curves; neither changes stored scientific inputs or their hashes.
- Explicit pairs are selections, not automatic tracking. A changed branch count, missing pair or disjoint toroidal domain must be visible. Do not choose the nearest frequency behind the user's back.
- Keep report data small and versioned, with source bundle hashes, selected mode IDs, method/request provenance and scoped evidence. Do not add a second scene format or alter the physical Project contract merely to store analysis results.

A browser feature is not necessary to prove a package-first workflow. Product/visualization ownership has substantial work in report semantics, usable figures, examples and documentation. If a web comparison view is included, it should be a separately justified small consumer of the same report; do not require a duplicate scientific implementation solely to involve every team member.

### Acceptance

- Meaningful analytic cases: a global sign flip and rescaling preserve a normalized agreement measure; a changed radial shape does not. At least one layered/interface counterexample must fail if either side is accidentally smoothed or normalized independently.
- Real method comparison: sphere, shell and PREM domain cases with named pairs at two meshes. Retain the pilot's independent Bessel/traction/MINEOS evidence separately. Freeze physical thresholds after inspecting existing fixture behavior and the chosen quadrature, rather than inventing an unexplained universal tolerance.
- Eligibility failures: mismatched physical model, missing region/support, absent mode and zero-norm data produce clear outcomes without mutation or partial valid-looking reports.
- Artifact readback: decoded PNG, parsed native SVG, CSV/JSON values checked against the returned report, complete source identities and an explicitly recorded global alignment sign. Include a small image size so a decodable file cannot conceal unusable captions.
- Release: fresh wheel installation, no repository PYTHONPATH, installed API/CLI custom-model journey and executable example. Preserve current default solver behavior and previous projects; do not promote the pilot automatically.

This is neither a generic modal assurance framework nor an inversion package. Defer automatic tracking, general near-degenerate subspace matching, arbitrary cross-model maps, batch schedulers, kernel families and a new plugin architecture.

## Alternative acceptance if the sensitivity study is selected

Promote the existing homogeneous recipe into a narrow installed study API, adding one explicit layer-wise Vs scaling request. Require positive/negative h and h/2, two meshes, saved effective requests, immutable models, explicit pairs and refusal/flagging of missing or ambiguous branches. A homogeneous whole-domain case must recover the exact logarithmic sensitivity of one. A localized layered case needs step and mesh convergence; it must not be advertised as an exact analytical kernel. Its figures and machine-readable report need the same package/release journey above.

Do not expose every material parameter, moving interface and automatic branch tracker in its first increment. Conversely, merely moving the current homogeneous script into a package module is too narrow: the new user-configured layered task and its failure/evidence semantics are what make this a real trial.

## Design and audit rounds

Use **three sequential design rounds** before implementation, with each round reading the previous revision:

1. User task, current gap, scientific measure, exclusions and concrete end-to-end example.
2. Cross-domain contracts and adversarial fixtures: interfaces, branch identity, normalization, state preservation, output provenance and installation.
3. Executable acceptance and ownership readiness: exact input/output examples, targeted checks, dependency order, resource bounds and release gate.

Then implement the agreed vertical slice and use **three distinct postimplementation reviews**: independent scientific counterexamples; package/product/export workflow review; clean release and evidence-to-source audit. Repair findings before the next dependent review. Parallel independent work inside a round is useful; three reports about one unchanged draft are not three iterations. No fixed line-count, test-count or elapsed-time target is useful.

## Phase-2 lessons to test in the team workflow

The observations below are recorded events, not a controlled productivity study.

| Phase-2 observation | Workflow implication | Measure in the trial |
| --- | --- | --- |
| Final integration recorded 83 Python checks, 25 frontend checks and 19 independently repeated pilot comparisons, yet browser review found SVG icon capture and release inspection found unusable small-image annotations | Automated success and user-facing artifact validity are separate gates | Count defects first found by numerical checks, integration and actual artifact inspection separately; require at least one inspected released artifact |
| API readiness, canonical Chinese text capture, Scene 1.1 availability and renderer readiness were separate dependencies communicated as messages | A single “ready” flag is too vague across durable domains | Every dependent handoff names contract/source identity, completed evidence, permitted downstream action and remaining caveat |
| Lesson images were regenerated after depth-order repairs and again after final annotation repairs | Derived assets must be invalidated by renderer changes, not only by catalog changes | Record regeneration count/reason and the source identity used for final assets; final release has zero stale derived artifacts |
| Catalog SHA stayed `6b9b8d35…ab173` while preview bytes changed | Scientific identity and rendering identity are different | Independently verify input/catalog hashes and renderer/artifact identities; never infer final image freshness from a stable catalog hash |
| An independent 19-case pilot rerun reproduced every computed frequency with zero delta in the same environment while retaining unverified labels on arbitrary outputs | Reproducibility evidence can be concrete without becoming a global accuracy promise | Report actual numerical deltas, environment and evidence scope; count unsupported status promotions as acceptance failures |
| Package APIs/examples could progress while Site writes remained under one owner | Useful parallelism does not require concurrent writes to the same files | Zero unauthorized same-file writes; track blocked handoffs and whether the recipient had independent work available |

For the trial, keep a short handoff log with domain, incoming contract/version, completed artifact/evidence, receiving acknowledgement and any rework cause. Measure owner collisions, reopening after a premature readiness claim, avoidable full-suite reruns and stale-artifact catches. Initially record actual observations rather than inventing thresholds such as “handoff within five minutes.” The hard gates are no silent lost requirement, no conflicting write, no stale released artifact and no unperformed test marked passed.

The persistent-domain experiment should include a real recipient continuation: a domain receiving a handoff must be able to continue from the current contract, source and evidence without requiring the sender to reconstruct the whole conversation. Use normal work boundaries, not deliberate memory erasure or an artificial failure exercise. Do not build a management dashboard before the handoff record demonstrates a need.
