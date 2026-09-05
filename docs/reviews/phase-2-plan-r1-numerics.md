# Phase 2 planning review, round 1 — numerical ownership

Date: 2026-09-04. Reviewer: numerical_research. This is a planning review, not an implementation or acceptance claim. I inspected the actual solver, vendored operators, validation scripts, `docs/ROADMAP.md`, and the root's round-1 `docs/PHASE-2.md`. No numerical implementation was changed.

## Recommendation

Accept the root's decision to retain Python/SciPy and the current default solver. Make the numerical pilot a concrete, bounded deliverable: **an experimental SI toroidal finite-element solver with its own assembly and independent shape/frequency checks**. Do not replace the full backend, add a plugin registry, or port the package to Rust/C++/Julia in this phase. A roadmap alone would give less useful evidence than this small executable slice; a complete new R/S/T implementation would compete with the package, language, and export work without sufficient benefit.

“Owned core” should mean maintainable source with explicit operators, discretization, diagnostics, and release responsibility. It does not mean a language change, independence from NumPy/LAPACK, independent scientific validation merely because files have been renamed, or removal of upstream attribution.

## What the current code actually does

| Evidence | Consequence for the plan |
| --- | --- |
| `packages/earth_modes/solver.py:18–24` imports the private fork and lists substantive physics patches. The adapter is 447 lines; its four main vendor modules total about 2,100 lines. | This is already a maintained derived numerical implementation, not a thin call into an interchangeable external binary. Wholesale replacement is not needed to start taking ownership. |
| `solver.py:87–145` builds material/domain meshes and dispatches quadratic displacement, cubic pressure, linear fluid tangential displacement, and quadratic potential spaces. Internal radius/density factors are 1e6/1e3; exported values are SI. | A clean SI pilot offers a useful reduction in unit/space complexity. A complete migration must preserve distinct material interfaces and physical domains, not collapse them into one layer abstraction. |
| `vendor/Ouroboros/modes/FEM.py:16–42` adds material density sheets; `compute_modes.py:134–180` assembles phase/surface traction terms. | “Simplify interfaces” is scientifically hazardous. The fluid-fluid density jump discovered during phase 1 is a required regression, not incidental legacy code. |
| `compute_modes.py:196–247` converts sparse inputs to dense, condenses auxiliary variables, identifies potential values, and imposes center regularity. | The existing computation is dense despite some sparse wrappers. Calling `eigsh` on the original singular mixed pencil would not be a drop-in optimization. |
| `solver.py:289–320` performs a dense symmetric solve and, when required, a dense shifted-inverse refinement. `solver.py:322–334,375–377` classifies/excludes the fluid essential subspace. | Partial spectral extraction must address null/essential spaces, branch labels, completeness, and conditioning before being promoted as a performance improvement. |
| `solver.py:365–375` applies the l=1 rigid-translation stiffness correction; `solver.py:430–442` compares refinement by mode ID and frequency. | A future full core needs explicit symmetry/residual evidence and stronger shape/subspace checks, not only matching frequencies. Keep current behavior until a replacement has earned promotion. |
| `solver.py:195–221` postprocesses potential with repeated integrals; `solver.py:248–286` estimates first-order Q from finite-difference strains. | Potential and Q have their own convergence requirements. Ownership alone must not upgrade either quantity's quality label. |
| `scripts/validate_numerics.py:64–84` reads or runs a pinned MINEOS executable with eigenfunction output disabled; its inner-core T check at lines42–61 is a separate traction ODE. | We have real independent frequency evidence, but not a complete MINEOS eigenfunction importer or a broadly validated source-excitation pipeline. |

The recorded baseline remains 47 PREM modes and 36 independent frequency checks, with maximum frequency disagreement about 0.0536%. These are specific saved cases, not a guarantee for arbitrary models. `docs/validation/NUMERICS.md` also explicitly excludes a general calculation of the stratified-fluid continuous gravity-wave spectrum.

A read-only profile supports addressing architecture before language: on this machine, single-thread BLAS, PREM S2/full gravity, 80 elements produced a 309×309 reduced pencil in about 49 ms and solved it in 10 ms; 160 elements produced 597×597, about 116 ms assembly and 36 ms eigensolve. These timings are illustrative, not acceptance thresholds. Python assembly and dense matrix operations both matter; a new language around the same dense algorithm would not remove its scaling limits.

## Requirements to keep, change, remove, and add

| Decision | Recommended requirement |
| --- | --- |
| Keep | The current full R/S/T solver, six topology cases, gravity 0/1/2, explicit experimental linear Q, canonical mass normalization, region sidedness, physical branch labels, and fail-before-allocation budgets remain the default supported path. |
| Change | Replace “eventually write our own numerical library” with an executable toroidal ownership pilot plus a promotion checklist. Replace a language-first discussion with measured workload and operator/constraint requirements. |
| Remove from this phase | Full R/S migration, sparse mixed eigensolvers, automatic mode tracking, rotation/ellipticity/3D coupling, nonlinear rheology, mature inversion kernels, new source-calibrated synthetic seismograms, and a backend registry. These remain possible later stages, not disguised optional tasks that delay release. |
| Add | Pilot-specific matrix diagnostics, a derivative-independent quadrature formulation, a documented material interpolation convention, full radial-shape checks, attribution records, and an installed-package example that genuinely executes the pilot. |
| Add to later full-core requirements | Mesh resolution of material-profile knots, auxiliary-variable recovery, constrained residuals, symmetry defects before/after projection, and eigenspace comparisons near close modes. Sequence these as numerical changes after migration equivalence, rather than mixing every improvement into a port. |

The phase-2 pilot must not replace the default backend or silently fall back to it. Its experimental identity belongs in returned provenance and documentation. It may reuse the canonical model/bundle validators and presentation tools; it must not call vendor FEM/assembly/mesh helpers and then claim independent assembly.

## A useful bounded pilot

### Physics and discretization

Toroidal modes isolate the most manageable part of the existing numerical scope: independent solid domains, with fluids providing traction-free boundaries. Use explicit SI radius, density, and shear modulus; quadratic Lagrange radial elements; ordinary Gauss–Legendre quadrature; and the energy form

`K(W,Z) = integral mu * [(r W' - W)(r Z' - Z) + (l(l+1)-2) W Z] dr`

with

`M(W,Z) = integral rho * r^2 * W Z dr`.

This is the same physical toroidal energy represented in the existing `_attenuate` shear expression, but permits a small independently organized assembly. The natural boundary condition is zero tangential traction, `mu*(W' - W/r)=0`; center regularity is explicit. At l=1, W proportional to r must remain a rigid zero mode rather than becoming an artificial oscillation.

Evaluate rho and vs by their declared layerwise linear interpolation and form mu=rho*vs² at quadrature points. Do not silently use a different interpolation of mu. On intervals bounded by material-profile knots, four-point Gauss quadrature exactly integrates these polynomial mass/stiffness integrands for quadratic basis functions. Thus the pilot should retain all material-profile knots and add requested refinement; `mesh_size` is a target, and actual allocation/budget must be recorded. This is a deliberate discretization difference from legacy element-averaged properties, so heterogeneous-model comparisons require refinement, not bitwise equality.

### Concrete scope

- One internal experimental module, for example `earth_modes/experimental/toroidal.py`, with a real callable producing the existing canonical bundle for T modes. Expose only the small T request it implements; do not advertise R/S, material-Q dispersion, source response, or potential computation here.
- A model may contain multiple solid domains separated by fluid, including an inner-core domain and an outer shell. Adjacent solid material layers remain one physical solid domain. All-fluid input yields an explicit not-applicable result, following existing semantics.
- Preserve n labeling around the l=1 zero motion and explicit solid-domain identity. A finite requested frequency interval filters the computed finite spectrum; there is no hidden overtone cap.
- Use dense NumPy/SciPy linear algebra initially. Keep memory estimates and unsupported-request errors explicit. One implementation, one development validation command, one installed usage example; no second general framework.
- A source-derived implementation carries the actual upstream reference and a pilot method/version label. Matching the old fork is a migration regression, not independent scientific validation.

Exact argument names and the experimental API/export boundary should be frozen in planning round 2/3. The present proposal is bounded enough to assess feasibility without prematurely locking an unreviewed interface.

### Promotion evidence for the pilot

1. **Homogeneous sphere:** analytic spherical-Bessel traction roots and full W(r) shape for at least l=2/3 and several overtones, allowing only a common arbitrary sign/scale. Check the l=1 rigid rotation separately.
2. **Solid shell:** free traction at both boundaries; compare frequencies and radial shape with an independent displacement/traction shooting implementation. This exercises a boundary that a center-only test cannot cover.
3. **Layered PREM solid domains:** retain the saved mantle MINEOS and inner-core shooting references. Test a nonzero material jump and the same material artificially split into adjacent layers. Refinement must reduce the independently measured error; do not rely solely on fork-to-pilot agreement.
4. **Discrete diagnostics:** symmetric matrices, positive-definite mass after center constraints, normalized eigenpair residuals, and mass orthogonality for a bounded set of separated eigenvalues. Define scaled residuals against the actual discrete pencil and avoid demanding identity of eigenvectors within a degenerate subspace.
5. **Canonical/output closure:** one global exported mass normalization, correct supporting regions and missing-region zero field, no change of frequency by display scaling, and successful ordinary bundle validation/export from an installed wheel.

The existing 0.5% frequency gate is an appropriate ceiling for an initial independently benchmarked pilot case; it is not a universal tolerance for shapes, residuals, or all modes. Round 2 should set separate shape and residual tolerances from these bounded test cases, with no timing assertions in unit tests. The default solver can remain unchanged even if a pilot case needs more work; do not label an incomplete pilot complete.

## Language and long-term stack

Python remains the recommended scientific API and orchestration language. SciPy already calls compiled LAPACK; its symmetric generalized solver requires a positive-definite mass matrix and does not check matrix symmetry itself. Those are operator/constraint obligations, not issues a rewrite in Rust or C++ automatically solves. [SciPy eigh documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.eigh.html)

Keep TypeScript for the existing browser field/view layer in this phase. A Rust/C++ kernel becomes justified only after profiling demonstrates a persistent hotspot, the numerical interfaces are stable, and the Python/native/WASM build and precision costs have been measured. Julia remains a useful independent research/reference environment; adding it as a mandatory runtime to this installed Python package would increase deployment work without evidence of benefit here. Fortran MINEOS remains an optional independent reference tool rather than the default package dependency.

A credible sequence after this phase is:

1. Promote the toroidal pilot only after its gates pass; retain an archived, pinned reference implementation for development comparisons rather than permanently shipping two complete solver stacks.
2. Implement an owned radial formulation and verify all-fluid/free-surface, same-phase density jumps, phase interfaces, and gravity variants.
3. Address spheroidal mixed spaces explicitly: auxiliary-variable constraints, center behavior, potential boundary conditions, and the essential subspace. Preserve scope limitations instead of rebranding excluded fluid spectra as complete physics.
4. Add a complete second-solver import and eigenfunction/normalization checks. A shared plotting bundle is useful interoperability; sharing assembly is not an independent benchmark.
5. Mature individual sensitivity/weak-Q quantities with finite-difference and independent checks. Source/receiver excitation can proceed once its normalization, derivatives, units and independent synthesis reference are ready; it need not wait for every kernel.
6. Introduce efficient interval eigensolvers, coupling, anisotropy, or complex rheology only as separate evidence-backed numerical changes. Sparse assembly alone does not make the global Schur complement sparse or prove spectral completeness.

## Attribution, independence, and English policy

`pyproject.toml` currently declares GPL-3.0-or-later; the bundled Ouroboros license and source pin remain part of the delivered artifact. Preserve upstream notices, derivation references, and modification history when source moves. Do not claim that a rewrite based on the existing implementation becomes permissively licensed or clean-room code; any desired licensing change needs its own verified provenance review. Operational ownership and independent physical validation are separate claims.

All new numerical docs, diagnostics, examples, maintained comments and reports should be English. Translate the current Chinese `ROADMAP.md` and maintained historical prose without deleting adverse findings or changing evidence values. Imported researcher metadata and original attribution remain verbatim. Built-in lesson science should have one canonical source; website-only English/Chinese presentation strings can be keyed by stable lesson IDs rather than forcing Chinese prose into installed scientific projects or changing bundle hashes on locale switches.

Sources inspected locally: the pinned Ouroboros fork above, the pinned MINEOS control path and raw files in `docs/validation/mineos`, the phase-1 evidence and interface regression reports. The upstream references remain [Ouroboros v6.0 source pin](https://github.com/harrymd/Ouroboros/tree/fa63363040a28c08d9fe2bd7d05dcc823d90dd1e) and [MINEOS source pin](https://github.com/geodynamics/mineos/tree/26f842dbe95b0c27d5e77146d415268db1239913). No implementation is authorized by this round-1 review alone; consolidate scope, then perform the two further sequential planning iterations requested by the user.
