# Planning round 2: reproducible research workflows

Historical review of PLAN v0.3, ACCEPTANCE and the round-1 log, with implementation paused. Previously resolved Q fields, diagnostics, topology and coordinate conventions are not repeated.

## Necessary changes

| Priority | Gap and consequence | Minimum correction |
| --- | --- | --- |
| P1 | Unspecified solve options cannot reproduce mode count, Q treatment, target frequency, convergence checks or budgets. | Save a SolveSpec; distinguish requested settings from effective settings, expose config-file CLI replay and reject unknown options. |
| P1 | Reference-frequency material properties and target-frequency effective properties can be confused. | Preserve the reference input model and record effective model/settings separately. A post-solve frequency shift does not imply one effective elastic model describes every mode. Label the reference frequency on plots. |
| P1 | Cross-model comparison has no explicit pairing API. Matching only n/l can select the wrong toroidal domain, mishandle l=1 or hide crossings. | Provide independent bundle/mode pairs, with suggestions keyed by family/l/n/domain; report IDs, quality and frequency differences. Different models must not be physically superposed in one scene. |
| P1 | Probe CSV/SVG is promised without a position/time request. | Define ProbeSpec latitude, longitude, radius, optional layer, start, step, count and derivative; export Cartesian values with units and complete provenance. |
| P1 | “Raw CSV” can mean canonical mass normalization or untouched upstream arrays, although original arrays may not be retained. | Name canonical CSV explicitly; include family/n/l/domain/layer/r/U/V/W and potential where available, preserving duplicate interface samples. Offer original upstream data only when actually retained. |

## Additional consistency requirements

**Artifact identity is not numerical determinism.** Canonical hashes prove saved-artifact integrity. Re-running on another BLAS build may change floating-point values or diagnostics. Record model hash, SolveSpec and upstream patch provenance; compare repeated numerical results with justified tolerances rather than requiring identical bundle hashes. A third identity system is unnecessary.

**Inputs must remain unchanged.** Validation and solving must not mutate user models while filling Q grids, IDs or effective velocities. Return independent results. A normal single solve may remain unverified; convergence checking can be explicit, while published examples should include refinement evidence.

**Quality requires scoped evidence.** A summary status must retain which modes and quantities were checked, reference identities, error values and limitations. A frequency benchmark is not proof of eigenfunction accuracy, and selected-mode agreement is not a whole-bundle accuracy claim.

## Concrete workflow proposed for the next revision

1. Load and modify a model while retaining provenance; changed physical content gets a new content hash.
2. Solve from a saved request, with nonzero CLI failure status and no destruction of an existing valid output.
3. Copy the model, perturb Vs, solve again and compare explicitly selected pairs through frequency CSV and independent radial curves.
4. Sample normalized and canonical probes, including derivatives, and independently recompute a selected CSV sample from its sidecar request.
5. Save and reopen a project with the same bundle hash. Treat a newly computed solution as a numerical comparison, not a requirement for identical artifact bytes.

The command shapes discussed here were planning proposals, not executed acceptance evidence; final flags belong to the frozen CLI contract. Model, SolveSpec, Bundle, Scene, Probe and explicit comparison pairs are enough. No research database or asynchronous task framework is required.
