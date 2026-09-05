# Planning adversarial review 1: numerical scope and acceptance

Date: 2026-09-04. Historical review of PLAN v1.0, CONTRACT v1, research materials and pinned v6.0 source. Implementation was paused; copied vendor code and compatibility patches were unfrozen drafts, not completion evidence.

**Conclusion at the time: the plan could not establish complete numerical coverage.** Pinning v6.0 controlled complexity, but a working PREM run did not establish arbitrary fluid/solid topology or all-fluid support. The P1 items below needed explicit contracts and acceptance gates before freeze, not necessarily implementation during planning.

| Priority | Reproducible risk or gap | Minimal revision |
| --- | --- | --- |
| P1 | Layer lacked Qκ/Qμ and reference frequency despite promised linear Q. A modal envelope cannot replace material dispersion; identical velocities at different references describe different models. v6 create_adjusted_model needs a nine-column model and T_ref. | Optional per-sample q_bulk/q_shear with explicit null/positive semantics and model reference_frequency_hz, or an explicit nine-column adapter. Never silently supply “Earth Q.” |
| P1 | Each solid→fluid interface used block_len[i][0]-1 without preceding global offsets. PREM's first such interface hid the multiple-interface defect. | Require S/F/S/F/S with at least five regions and audit global interface DOFs. Metadata alone is not topology support. |
| P1 | round(num_elmt*sample_fraction) could allocate 0/1 elements to a thin/undersampled fluid, breaking cubic interpolation; redundant profile samples changed mesh. | Total target, at least four elements per phase region, thickness/speed allocation and fixed boundaries. Increase actual counts with provenance or reject. |
| P1 | No running all-fluid/fluid-center/fluid-surface evidence. Essential removal used essen/essen-1 and center phase; fluid exterior also changes gravity boundary location. | S, F, SFS, FS, SF, SFSFS × applicable families × g0/1/2. All-fluid T is empty/not applicable. Repair failures or reopen scope; never replace with cartoons. |
| P1 | v6 S l=1 sliced at essen+1 then skipped n0/1, possibly discarding physical low branches while promising upstream labels. | Retain eigenpair index and label convention; compare S1 to same-model MINEOS. Identify rigid motion from omega²/shape, not labels alone. |
| P1 | sqrt of negative omega² produced NaN; real unstable models and roundoff were conflated. Quality language was vague. | Raw negative/near-zero/positive counts and threshold; explicit instability failure for retained physical negative modes. Require rho>0, mu>=0, kappa=rho(vp²-4vs²/3)>0. Later round 3 clarifies essential-space classification before stability judgment. |
| P1 | Frequency range had no completeness definition; hidden n_max=8 could omit valid branches, and coarse FE cannot certify arbitrary high frequencies. | Entire discrete spectrum then filter, or explicit recorded truncation; completeness and mesh quality. Coarse high modes remain unresolved, not validated. |
| P1 | A continuous normalization label did not survive sampled layer slicing: PREM70 DT conversion gave only 0.991–0.999; naive density interpolation crossed discontinuities. | Record upstream conversion and region integral; one whole-mode rescale on the agreed export quadrature, never each layer independently; verify interface sides. |
| P1 | Raw .npy potential P was a zero placeholder until potential_all_modes. Diagnostic g0/Cowling potential differs from a solved gravity contribution. | Optional actual potential with absent/solved/postprocessed and units/conversion provenance. Zero placeholders cannot claim computed gravity. |
| P2 | Dense eigensolving costs O(N³) time and O(N²) memory per degree; the web l<=64 bound is not an API budget. | Preflight dimension/memory, configurable budget, serial degrees; optional processes without oversubscribed BLAS; actual runtime. |
| P2 | Experimental Q could still fail: create_adjusted_model called unimported write_model; T kernel/source docs were stale. | Runnable Q smoke plus finite-difference reference; expose only tested families/parameters. Do not load optional ObsPy for ordinary solving. |
| P2 | Default PREM was an isotropic average shifted to 3mHz, not generic PREM. | Name the isotropic/no-ocean/3mHz approximation, retain source/commit/content hash/transforms, and use the exact same table in MINEOS. |

## Minimum scientific matrix

- Homogeneous no-gravity T roots `x*j_l'(x)-j_l(x)=0`, frequency/radius/Vs scaling, and independent zero-radial-traction R breathing roots.
- Same-table MINEOS R/S/T including l=1/l=2 and inner-core T, with raw outputs/tool versions and convergence-justified tolerance.
- Six topologies at g0/1/2, especially all-fluid and the second solid→fluid interface. Verify radial continuity, T support and potential boundary behavior, not just finite frequencies.
- Two mesh levels for every default displayed mode; unresolved localized/high-frequency results remain numerically available with pending quality in UI/manifests.
- Whole-mode regional mass and consistent model/frequency/shape identity; do not discard 0R0 or legitimate S1 as rigid motion.

Replace “upstream runnable range” with complete explicit topology coverage, independently benchmarked/refined defaults and inspectable discrete solutions/completeness/pending quality on custom parameters, without claiming a universal error bound. This makes arbitrary-layer support demonstrable rather than reducing it.

The next planning round needed concrete Q fields, matrix budgets, mode quality, l=1 labels and regional mesh decisions. Testing every function was unnecessary; attractive images could not replace these physical gates. This report is historical and does not assert the findings remain unresolved after later implementation.
