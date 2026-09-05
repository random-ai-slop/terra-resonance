# Vendored numerical dependency

Actual package source: `packages/earth_modes/vendor/Ouroboros`.

Upstream: https://github.com/harrymd/Ouroboros
Version: v6.0, commit fa63363040a28c08d9fe2bd7d05dcc823d90dd1e
License: GPL-3.0 (full license retained alongside the source).
Only core FEM mode calculation, setup, required helpers and constants are included.

Local compatibility patches:
- Private import namespace `earth_modes.vendor.Ouroboros`.
- Removed obsolete NumPy aliases (`int`, `row_stack`, `trapz`).
- Symmetric Jacobi quadrature uses `eigh` and sorted real nodes, avoiding LAPACK-dependent eigenvalue order and unnecessary complex casts.
- Single-row eigenvalue files use `atleast_2d`.
- Requested radial-order range is clipped to available eigensolutions.
- Missing optional ObsPy does not print during normal imports.

See `docs/research/numerics.md` and adapter provenance for scientific limits.

Scientific adapter changes (all recorded in bundle patch identifiers):

- Retained only the local FEM forms, quadrature/setup, assembly and required helpers. The old file pipeline, unused kernel placeholders and optional ObsPy path are excluded from the installed dependency.
- Replaced four inconsistent mixed-variable reductions with one indexed reduction: duplicate interface gravitational potentials are identified by a congruence, then massless pressure/potential variables are condensed. Material-domain offsets are based on original block sizes.
- Corrected solid→fluid interface offsets after the first solid region, and the exterior gravitational-potential boundary index for fluid exteriors and radial modes.
- Added the missing fluid free-surface boundary terms. A homogeneous fluid sphere now has radial acoustic frequencies n*vp/(2R), instead of rigid-wall roots.
- Enforced central regularity. S l=1 has finite even U and V=sqrt(2)U; its massless centre uses fourth-order even extrapolation from the first two displacement nodes. Other central displacements vanish. Toroidal centre recovery is no longer obtained by a spurious massless Schur solve.
- In isolated gravity-off/full-gravity S l=1 problems, a symmetric rank-one stiffness projection restores the exact rigid-translation nullspace. Cowling's fixed gravity field is deliberately not projected. This removes a quadrature artifact, not a physical oscillation or physical negative root.
- Background gravity integrates each linear density interval exactly, retaining jump sides; no staircase-density approximation is imposed.
- Dense whole-spectrum solves can lose the small eigenvalues of thin-layer problems. The adapter refines the low-frequency window through a diagonally equilibrated shifted inverse when the estimated roundoff scale reaches the requested window. It checks window eigenpair counts; unclassifiable spectra fail explicitly.
- Eigenfunctions receive one layerwise discrete mass normalization, with explicit SI factors. Potential uses an independently evaluated Poisson integral. Linear Q uses explicit material Q, stiffness dispersion to the requested target, and bulk/shear strain energy; it remains a first-order elastic-eigenfunction approximation.

Validation and exact numerical evidence: `docs/validation/NUMERICS.md`,
`docs/validation/numerics.json`, `scripts/validate_numerics.py` and
`tests/test_solver.py`. The benchmark validates frequencies; it does not promote
all observables or all custom models to a blanket accuracy class.

Implementation review R1: fluid gravity forms now include internal same-phase material density sheets `-[rho]*g*r²` in radial-displacement stiffness. Layer derivatives alone omit these delta terms. Domain-end traction terms remain separate. Solid forms already eliminate density derivatives by integration by parts and receive no duplicate term. Jump-to-thin-transition R/S regressions cover fluid/solid at gravity 1 and 2.

Publication clarification (2026-09-04): the combined distribution declares GPL-3.0-only because the retained upstream grant is GPLv3; no additional later-version grant is assumed. Local modifications listed above were present by 2026-09-04. Original upstream license and provenance remain unchanged.
