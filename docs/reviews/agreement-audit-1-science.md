# Agreement implementation audit 1: independent science

Assignment AUDIT-SCI/1. **Preparation only; execution is pending the coordinator's accepted integration I.** No scientific audit pass, numerical integration result or implementation finding is claimed yet. The numerical agreement implementation is being written by the independent native numerical-methods task. This reviewer owns the audit harness and evidence, not the runtime implementation.

## Prepared gate

`scripts/validate_agreement.py` requires an explicit full `--integration` matching current HEAD and refuses dirty tracked runtime sources. Run with the primary environment, `PYTHONPATH=packages` and `OPENBLAS_NUM_THREADS=1`. The artifact directory must be new. Only Python syntax has been inspected so far; neither the harness nor the new API has been executed.

The harness prepares exactly twelve existing-solver calls: sphere/shell targets40/80 and PREM140/280, both default and owned methods, degrees1..4 and frequency window1e-8..0.012Hz. Explicit expected branch lists contain seven sphere, seven shell and eight PREM identities. Missing identities fail. Six cross-method reports contain44 rows; six within-method refinement reports contain44 rows. All named rows require absolute relative frequency change<=1e-4 and shape distance<=0.003, without a monotonic-improvement requirement.

Full bundles and self-contained reports are retained under ignored `artifacts/agreement-science/`. Compact `docs/validation/agreement.json` will record accepted source identity, environment, script hash, every artifact's canonical and serialized hash, each bundle hash, actual domain/layer element and radial-sample counts, requests, measured rows and failures. A failed run records failure instead of a pass. No existing independent reference evidence is rewritten or rerun.

## Independence and counterexamples

The audit's numeric oracle reconstructs the original layer-local linear fields and density, multiplies interval-local polynomials in extended precision and integrates their coefficients analytically. It does not call the production Gaussian quadrature, production evaluator internals or FE mass matrices. Each reported row is checked against this separate oracle, including direct residual integration.

Manufactured fixtures separately use rational expected constants for a density knot absent from both field grids and for a continuous field whose sign reverses across a material interface with density ratio91/11. Other checks cover different valid canonical scalings of the same field, one global sign, incomplete connected support, forged domain labels, explicit differing n labels, tiny nonzero shape/frequency differences, inward/outward tolerated endpoint tails, model identity, zero/nonfinite fields, supported and contradictory effective-model declarations, row types/ranges and altered source hashes. Curves retain separate material paths and the prescribed residual orientation. The fixtures remain labelled manufactured/unverified.

## Pending acceptance

After I is supplied, inspect the actual numerical source before running the harness, record real failures for author repair, and rerun only checks justified by those repairs. The completed audit must identify the accepted source and actual results here. Until then, the scientific audit remains **not run**. Package/CLI/artifact inspection and isolated distribution verification are separate later audits; this document does not close them.
