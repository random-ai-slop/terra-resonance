# Planning adversarial review 3: scientific acceptance and freeze

Historical baseline: PLAN/CONTRACT v0.4, ACCEPTANCE, WORKFLOWS and round-2 dispositions. Date: 2026-09-04. Only plans and existing research logs were reviewed; implementation had not resumed.

**Conclusion at the time: ready to freeze after two small scientific wording/default decisions below.** No fourth round of architectural expansion was needed. These decisions could close in this round; later physical failures still required real repairs. This was not numerical acceptance evidence.

## Earlier findings rechecked

| Requirement | v0.4 disposition | Judgment |
| --- | --- | --- |
| Recomputable solve input | Complete SolveSpec, config precedence, request/effective_settings, immutable input | Closed; reproduce exact saved config at release |
| Q/reference/effective models | Material Q/reference frequency, original reference model retained, effective model and modal shift metadata | Closed except null target below |
| Arbitrary solid/fluid domains | Explicit groups/domain IDs, six topologies × families × gravity, failures not normal partial bundles | Implementable gate; unrun rows do not count as passed |
| Quality/independent evidence | Per-mode quality; N1 analytic, N2 same-table MINEOS, N4 refinement; quantity/scope | Closed except negative-spectrum stage below |
| Comparison/probe/CSV | Explicit compare_bundles pair, ProbeSpec/export_probe, canonical CSV naming | Closed; no database or coupled Scene needed |
| Identity/reproduction | Separate JCS integrity from cross-machine numerical tolerance | Closed; eigenfunctions have arbitrary global sign |
| Maintenance/testing | Python/CLI alignment, private vendor, quick regressions separate from full release evidence | Reasonable; avoid full topology runs for every small change |

## Two required pre-freeze decisions

### P1: classify the physical subspace before judging negative spectra

The phrase “Spectra significantly violating stability stop the affected run” could incorrectly mean rejecting every negative raw eigenvalue. Ouroboros's mixed Ritz form includes fluid pressure/essential-spectrum degrees of freedom. Existing PREM280 g0/1/2 logs warned at sqrt(eigvals), then emitted S modes after essential removal. This proved neither that every negative value was physical instability nor that all were harmless.

Record raw spectrum counts separately from excluded constraints/essential modes, including count, basis and threshold. Judge stability after justified physical-subspace extraction: significantly negative retained omega² fails. Never silently discard unclassified negatives or take their square roots. Rigid/essential identification precedes sqrt. A clear “physical subspace could not be extracted” error is acceptable; raw signs alone do not establish planetary instability.

This came from actual logs, not a new hypothetical requirement. It preserves the stable-oscillation goal while avoiding an implementation that rejects every fluid model.

### P1: make linear_q=true with null target_frequency_hz unambiguous

SolveSpec defaulted target_frequency_hz to null; WORKFLOWS required material Q/reference but left the effective-matrix frequency unresolved. Using the reference, band midpoint or an error would produce different physical behavior.

Require an explicit positive target when linear_q is enabled; expose `--target-mhz` and return a field error if missing. Without linear Q, target must be null or reject non-null. Include one complete Q+target SolveSpec. Never silently choose a typical Earth frequency.

## Concrete release fixtures proposed at the time

Store versioned generated inputs, hashes, commands and outputs. Small topology models use R=1,000,000 m, all-region rho=4000 kg/m³ and vp=8000 m/s, solid vs=4000 and fluid vs=0. Positive bulk modulus and weak gravity relative to elasticity avoid accidentally using unstable physics as a solver test.

| Gate | Exact input/action | Required evidence |
| --- | --- | --- |
| N1 | Homogeneous solid, g0, R and T l2/3, mesh80/160 | Analytic equations/roots/error, doubled-radius and proportional-speed scaling |
| N2 | Original `examples/prem-isotropic-3mhz.txt`, pinned MINEOS and corresponding gravity; R0..2, S1/S2, inner/mantle T2 | Raw controls/output, tool version, same model hash, explicit mode pairs/errors |
| N3 | S/F/SFS/FS/SF/SFSFS with relative boundaries [0,1], [0,1], [0,.3,.65,1], [0,.45,1], [0,.55,1], [0,.15,.35,.6,.8,1]; g0/1/2, R/S l1/2, T l2 | Per-group success/not-applicable, extraction counts, support/continuity, mesh80/160 changes; exit0 alone insufficient |
| N4 | Default PREM mesh140/280 or additional refinement as required | Every displayed ID's two frequencies, difference and quality; no bundle-wide validated flag |
| N5 | Solid sphere q_bulk1000/q_shear300, reference .01Hz/target .001Hz, then both Q null | Reference/effective model, R/S/T support, finite modal Q, elastic limit, shift/damping derivative error, experimental label |
| N6 | Representative bundles integrated on contract region grids | Pre-normalization integral/global factor/canonical norm, interface IDs/duplicate radii, center records |
| Recompute | Saved request/reference model for PREM and sphere | Pairing/frequency tolerance/software version; hashes establish original integrity only |
| Compare | Solid-sphere Vs +1%, positive bulk retained, explicit T2 pair | Relative frequency shift and r/R shape/CSV; approximately +1% T frequency, not merely a drawn curve |

These parameters do not restrict user input or claim every combination already passed. All-fluid S1 or multiple-interface defects must be repaired and attributed, not skipped while claiming Ouroboros coverage.

## Nonblocking notes

A cross-run comparison may align one global sign and record it without changing canonical source arrays. Near-degenerate modes should not be forced into automated curve-similarity tracking; explicit pairs keep scope controlled. Update WORKFLOWS's stale “planning round 2” heading and “Original eigenfunctions” CSV wording to v1/canonical at freeze; no new architecture is needed.

After the two required decisions, freeze and implement, followed by at least three sequential implementation reviews. Infinite planning refinement cannot substitute for numerical execution and deliverable artifacts.
