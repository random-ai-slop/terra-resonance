# Numerical backend decision (2026-09-04)

Use the GPL-3.0 Ouroboros **v6.0**, commit `fa63363040a28c08d9fe2bd7d05dcc823d90dd1e`, as an attributed, minimally patched numerical dependency. Its mixed Galerkin Rayleigh–Ritz method covers spherical, nonrotating, isotropic elastic planets with radial, spheroidal and toroidal modes, alternating solid/fluid regions, and gravity off / Cowling / full perturbation. This is the defensible baseline, with convergence metadata rather than a blanket “research accuracy” claim.

Sources: [upstream release tree](https://github.com/harrymd/Ouroboros/tree/v6.0), [method and scope](https://github.com/harrymd/Ouroboros/blob/v6.0/modes/README.md), [normalization derivation](https://github.com/harrymd/Ouroboros/blob/v6.0/docs/Ouroboros_normalisation_notes.pdf), [GPL license](https://github.com/harrymd/Ouroboros/blob/v6.0/LICENSE).

## Why not current master or only MINEOS?

Current master `80cd72784be60d325a0ca5600f06b7f13625c209` is an unfinished anelastic refactor. A real PREM run fails in R with missing `use_attenuation`, then undefined `A_bdr_cond`; S fails unpacking four FEM return values into three. Its documentation describes Maxwell, SLS, Burgers and extended Burgers, but the current parser no longer reads the advertised format, Burgers construction is commented out, empirical extended Burgers references an undefined `py_ebm`, and the top-level pipeline raises `NotImplementedError` after full-attenuation mode calculation. Thus “all advertised master rheologies” is not a functioning upstream scope. Complex rheology is a separately declared experimental extension, not falsely advertised as validated.

[MINEOS](https://github.com/geodynamics/mineos) remains a valuable independent benchmark: Fortran integration solver, radial anisotropy and Q, eigenfunctions through `eigcon`, synthetic seismograms. It needs a Fortran toolchain and uses an Earth-style inner-core/outer-core/mantle model contract rather than Ouroboros' arbitrary alternating regions. Its repository license is GPL-2.0; do not conflate its license with the wrapper. [Mineos.jl](https://github.com/anowacki/Mineos.jl) is an MIT wrapper over `Mineos_jll`, with `SeisModels.LinearLayeredModel` input and frequency/period/Q/group and phase velocity/Rayleigh quotient output. Its public README explicitly says eigenfunction retrieval and seismogram generation are not implemented, so it cannot be the sole visualization backend.

## Verified v6.0 experiment

Temporary isolated environment: Python 3.13, NumPy 2.5.2, SciPy 1.18.1. After mechanical compatibility replacements (`np.int`, `np.row_stack`, `np.trapz`), PREM with 70 elements, R/S/T, n=0..2, l=2..3, gravity=2 completed the full eigenfunction/gradient/potential/kernel pipeline. At 280 elements all three gravity cases completed. A single-thread BLAS avoids excessive startup/thread overhead. This is feasibility evidence, not a convergence certificate.

PREM70 examples: 0R0=0.8136503504302 mHz, 0S2=0.3097900397466 mHz, mantle 0T2=0.3797251436011 mHz. Inner-core 0T2=1.13601539146 mHz. Direct trapezoidal DT mass integrals at this coarse sampling were 0.9962, 0.9913, 0.9994, 0.9990 respectively. The final adapter records quadrature normalization and mesh quality.

## Interface hazards

- Four-column `load_model` input actually uses SI; the upstream README's km/g cm−3/km s−1 wording is incorrect.
- Raw `.npy` radius is km; `load_eigenfunc(... units='SI')` converts it to metres, despite the README saying raw metres.
- Use `norm_func='DT', units='SI', omega=2πf_Hz`. Then the mass integral is `∫rho r²(U²+V²+W²)dr=1`, with **unit vector spherical harmonics** `gradΩY/sqrt(l(l+1))`. Default upstream/MINEOS normalization has an additional frequency and angular-degree factor. Never mix them.
- Toroidal solid regions are independent. Preserve region identity; fluid regions must have zero toroidal displacement. Region indices run from centre outward.
- Preserve duplicate interface radii and interpolate each side separately. A model discontinuity cannot be smoothed into a continuous material profile.
- Upstream radial n=0 is the breathing fundamental and must not be deleted based on a misleading README sentence. l=1 handling needs explicit audit.
- Linear Q correction relies on kernels; upstream documents a roughly 4% kernel discrepancy and limited benchmarking. It remains experimental and provenance must say so.

## Necessary verification

1. Homogeneous no-gravity toroidal frequencies against zeros of `x*j_l'(x)-j_l(x)` and surface traction; radial breathing against the homogeneous elastic traction equation.
2. PREM low-frequency mode frequencies versus independent MINEOS results with the **same isotropic model, reference frequency, and gravity convention**; not generic PREM values from differing conventions.
3. Mesh refinement for representative R/S/T and interface-localized modes, mass normalization, finite outputs, interface sidedness, and absent fluid toroidal fields.
4. Alternating solid/fluid topologies including fluid centre/surface and more than one fluid shell. Reject unsupported/ill-conditioned requests explicitly rather than silently drawing a guessed shape.
5. A finite-difference bulk/shear perturbation check before treating attenuation kernels as quantitatively validated.
