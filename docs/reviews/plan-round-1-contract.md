# Planning round 1: adversarial data-contract and scientific-fidelity review

Historical record. Reviewed PLAN v0.2 and CONTRACT v1. The reviewer owned scientific data and fields but reviewed the plan only after receiving the pause instruction. The data.py/fields.py files already on disk were unfinished, untested drafts, not evidence that frozen interfaces had passed acceptance.

Verdict at the time: **do not freeze yet**. The problem was not missing feature categories. Ambiguities between scientific and illustrative quantities, interface boundaries, and acceptance gates could make two individually compliant implementations incompatible.

## Required changes

### P1 — Solver normalization conflicts with canonical unit mass integral

The same contract paragraph required retaining solver normalization and fixing the mass integral to one. Upstream U/V/W, radius units, and potential scaling already used special conventions. One implementation could change only labels while another renormalized, without the user being able to tell.

Choose one conversion path. Prefer an adapter converting u/v/w to the canonical unit-vector spherical-harmonic basis and unit mass integral, applying the same modal factor to potential. Preserve source_normalization, unit conversion, vector-basis conversion, and mass_scale in provenance, together with traceable source artifacts. If unnormalized external input is permitted, give it a different normalization value instead of claiming unit mass. Canonical displacement coefficients have units kg^(-1/2), not metres.

Acceptance: independently integrate a real upstream mode to approximately one; verify source and canonical representations produce the same field after the documented transform; apply one common modal scale to displacement and potential.

### P1 — PLAN promises physical amplitude but SceneSpec contains only illustration coefficients

PLAN separated phase, physical amplitude, geometry gain, and color scale, while the contract defined amplitude solely as a dimensionless illustration coefficient and omitted a saved color range. A researcher could mistake a probe CSV for metres or assume a manually chosen color bar was reproducible.

Limit this release to canonical eigenfunctions and illustrative coefficients, removing the unimplemented physical-amplitude promise. Actual excitation needs its own model and units. Default probes should use the same normalized illustration field, with derivative units s^-1 and s^-2; raw output must state its normalization rather than imply metres. Save a color-range field or define its fully deterministic rule. A configurable color bar cannot lack a corresponding scene setting.

Acceptance: plots, CSV, and manifests distinguish illustration values, mass-normalized coefficients, and calibrated physical displacement; no metre label appears without an excitation definition.

### P1 — An undefined “safe angular bound” prevents matching color scales

The proposed sum(abs(amplitude)) times a safe angular bound did not distinguish radial and tangential harmonics. An arbitrary constant can clip l=64 modes. Signed components need a diverging scale; magnitude is nonnegative; mixed degrees require a shared rule.

Specify a provably conservative bound or deterministic sampling procedure. Suggested per-term bound: sqrt(3*(2*l+1)/(4*pi)), covering the three vector bases, summed with absolute coefficients; l=0 may use a tighter bound. Defaults stay fixed; manual overrides belong in SceneSpec with component, range, and clipping information.

Acceptance: actual samples of supported high degrees and mixtures remain inside the default bound; changing time does not change it; Python and browser use identical scene color ranges.

### P1 — Center, pole, and material-side conventions are incomplete

The outer-side rule was good but lacked a shared geometric tolerance and r=0 behavior. Trigonometric construction can put a surface sample several ulps beyond R, causing random zero-valued points under the outside-model rule. Spherical angles are undefined at the center; regular l=1 modes become finite only after radial and tangential terms combine. At poles, dphiY/sin(theta) needs its limit, not an arbitrary zero.

Specify a common length tolerance and boundary snapping, keeping explicit side selection. Use analytic polar limits and check Cartesian vectors. Reconstruct exact-center values from regularity. If center evaluation were excluded in this release, reject it clearly and omit those sample points rather than returning an arbitrary direction.

Acceptance: the same north/south pole constructed using different longitudes gives the same Cartesian result; rotations/scaling do not lose surface points; exact and near-interface samples follow the declared sides; the center is independently validated or explicitly rejected.

### P1 — Material layers are not independent dynamical domains

A solid material jump can split a model into layers while a T mode spans their shared solid domain. Only a fluid separator creates an independent solid vibrational domain. IDs and layer_id arrays could store the data but did not define how identical n/l labels in different domains were distinguished. Solving T independently per material layer would invent free surfaces.

Treat adjacent same-phase layers as one dynamical domain. Material layers preserve profile boundaries. Put the toroidal supporting-domain ID in provenance or a formal field and include it in unique mode identity. Preserve both material sides, and do not normalize per layer.

Acceptance: artificially splitting a continuous solid model leaves its T spectrum unchanged; a real fluid separator creates independent domains; equal n/l labels from different domains coexist.

### P1 — Arbitrary fluid/solid topology and executable upstream scope need an acceptance matrix

The plan lacked representative models and convergence conditions. Import capability could be mistaken for solving capability; gravity=2 could omit potential without explanation; mesh_size existed without a failure/unconverged policy. All-fluid and surface-ocean boundary conditions needed actual solving evidence.

Fix a matrix: homogeneous solid sphere, all-fluid sphere, no-ocean PREM, two solid regions separated by fluid, and a surface-fluid layer if executable. Record representative applicable R/S/T cases for gravity 0/1/2. Define quality states; returning eigenpairs is not a scientific pass. If full-gravity output lacks potential, explicitly identify the missing observable.

Acceptance: changing real parameters triggers recomputation and changes results; independent frequency evidence and mesh refinement cover representative modes separately; wider import-only support is labeled separately.

### P2 — Frame timing and attenuated-loop semantics are missing

The draft specified physical time but not scene.time_s + frame_index/fps*time_scale, frame rounding, final frames, or a GLB endpoint key. Damped modes are not periodic; wrapping phase while resetting the envelope can look like spontaneous energy recovery.

Define time mapping, counts, and GLB endpoint keys. Replaying an initial condition is a labeled UI action, not continuous evolution. Undamped defaults may support teaching loops; Q-enabled scenes retain absolute time and expose the envelope.

Acceptance: Python, browser, and exports agree at the same physical time; derivatives include the envelope; Q scenes do not silently reset normalization at the end.

### P2 — A candidate independent reference is insufficient for research acceptance

Mineos.jl was listed as a candidate, while upstream examples, invariants, and refinement were the only required checks. Faithfully copying an upstream defect can pass all three.

Make independent frequency comparison an implementation gate. Trusted tables or analytic solutions cover only their supported modes. Paths without independent evidence must be labeled executed/refinement-checked, not independently verified. Retain evidence level for each individual result.

## Minimal revision set

Do not broaden the feature map: unify normalization; remove undefined physical-amplitude claims; fix color/time rules; complete center/pole/interface conventions; distinguish material layers from dynamical domains; make the representative numerical matrix and independent references executable acceptance. Review the resulting v0.3 before resuming implementation rather than inferring semantics while coding.
