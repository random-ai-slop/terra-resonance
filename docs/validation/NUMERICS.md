# Numerical evidence

The published bundle is a real solution of the bundled isotropic, no-ocean PREM table. It contains 47 modes, with R and S/T degrees 1–4 in 0.05–3 mHz, using 140 finite elements and an independent 280-element refinement. There is no hidden radial-order cap. Quality belongs to each mode and quantity.

`numerics.json` records N1–N6 inputs, tested mode identities and measured errors. The current run has 36 independently checked frequencies: maximum relative discrepancy 0.0536%; maximum PREM mesh-refinement change 0.0212%. All six requested topologies at gravity 0, 1 and 2 passed their 80→160-element comparisons (maximum change 0.00177%). These are frequency and discrete-normalization results, not a claim that every derived observable is equally accurate.

Run the evidence generation from the repository root:

```sh
PYTHONPATH=packages OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/validate_numerics.py
PYTHONPATH=packages OPENBLAS_NUM_THREADS=1 .venv/bin/python -m pytest tests/test_solver.py -q
```

The script writes `examples/prem-modes.json` and `docs/validation/numerics.json`. It intentionally recomputes the scientific cases; ordinary unit-test runs need not regenerate large assets. Single-thread BLAS is an optional performance choice, not a different numerical model.

## Independent references

MINEOS source is pinned to [`26f842dbe95b0c27d5e77146d415268db1239913`](https://github.com/geodynamics/mineos/tree/26f842dbe95b0c27d5e77146d415268db1239913). Its original Fortran `minos_bran.f` compiled with:

```sh
gfortran -std=legacy -fallow-argument-mismatch -O2 minos_bran.f -o minos_bran
```

The exact 185-row `examples/prem-isotropic-3mhz.txt` was passed unchanged; its header disables further Q/dispersion correction. Integration/root accuracy is 1e-9, gravity cutoff 100 mHz, frequency bounds 0.1–4 mHz, n=0–4, l=1–4. `jcom=1,2,3,4` gave the saved original output files in `docs/validation/mineos`. Eigenfunction output was disabled (`none`), so these are frequency benchmarks only. To compile and rerun from the pinned public checkout, add `--mineos-root /absolute/path/to/mineos` to the validation command.

MINEOS jcom4's branch counter does not return the inner-core T fundamental under the expected n label: for example its n=0,l=2 output is 3.265081 mHz. This output is preserved rather than relabeled as 0T2. The first nonzero l=1 result does agree with our 1T1. For inner-core 0T2/3/4 the validation script independently integrates the displacement/traction ODE, with a regular centre and zero outer traction. It shares only the material table, not FEM assembly or eigenvectors. Frequencies are 1.135932, 1.751565 and 2.305452 mHz. A truncated-inner-core attempt using the mantle MINEOS branch did not terminate and is not counted as evidence.

## Physical checks beyond running successfully

- Homogeneous elastic R roots use `vp²*x*j0(x)-4*vs²*j1(x)=0`; T roots use `x*jl'(x)-jl(x)=0`. Radius scaling is also checked.
- Homogeneous fluid R modes obey free-surface acoustic roots `f_n=(n+1)*vp/(2R)`. This check caught and fixed a real upstream rigid-wall error.
- Six topologies are S, F, SFS, FS, SF and SFSFS. All R/S and applicable T families run at every gravity setting. Tests include l=1, phase-support identity, multiple interfaces and duplicate material boundaries. All-fluid T is explicitly not applicable.
- PREM l=1 frequencies and labels are checked against MINEOS (2S1≈0.4044 mHz). Exact translation is excluded as a null motion by its physical symmetry; Cowling is not given that symmetry.
- A one-metre fluid surface layer on a 1000-km sphere is an explicit conditioning regression. It must retain the low R spectrum, rather than discard it under a global high-frequency numerical-zero threshold.
- Each mode has a single discrete integral `sum_layer trapz(rho*r²*(U²+V²+W²),r)=1`. Density uses the named layer's own interpolation. The conversion metadata records source units and scale factors.
- The potential is postprocessed from a Poisson integral of the canonical displacement, including interface density sheets by integration by parts. For gravity 0/1 it is labeled diagnostic-only, not gravity that affected the frequency.
- Linear Q has an exact null-Q limit, no implicit Earth Q, and a finite-difference shear-stiffness check. A uniform toroidal Q=300 gives 300.01745; the independent finite-difference estimate gives 300.00000 (relative discrepancy 0.00582%). The output explicitly retains the reference model, effective target-frequency model, elastic frequency, corrected frequency and elastic eigenfunction approximation.

## Remaining scientific limits

The finite-dimensional fluid essential subspace is removed using the mixed-element dimension stated by Ouroboros, with raw counts and retained identities preserved. This selects the advertised oscillatory spectrum; it is not a general calculation of the continuous stratified-fluid gravity-wave spectrum. Negative retained eigenvalues or inconsistent inverse-refinement counts fail the request, rather than turning into NaNs or successful partial bundles.

Linear Q is a first-order constant-Q approximation. It is not the unfinished upstream nonlinear Maxwell/Burgers pipeline. The Q test establishes the implemented loss and frequency-shift convention; a full inversion-quality sensitivity-kernel API is a later roadmap item. Fine-scale custom structures require their own mesh convergence and independent validation, even though the topology is supported.

## Formal implementation review R1 corrections

Fluid material regions with a density jump can share one fluid vibrational domain. Their weak form now includes the distributional contribution `-[rho]*g*r²` at each internal material interface, in addition to the ordinary within-layer density derivative. Domain-end traction terms remain separate. The solid weak forms already remove this derivative by integration by parts and must not receive the same correction again.

Run `PYTHONPATH=packages OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/validate_density_interfaces.py` for the separate, saved `density-interfaces.json` evidence. A 1000-km sphere with density 8000→4000 kg/m³ at 500 km, vp=8000 m/s and vs=0 or 4000 m/s is compared with a 100-m linear transition, for both Cowling and full gravity. At 240 elements, the largest sharp/thin frequency discrepancy is 0.1129% (fluid S2, full gravity); the Cowling discrepancy is 0.00948%, and both solid cases are below 0.0004%. The fluid S discrepancy decreases by more than 40% from 120 to 240 elements. These are thin-transition consistency checks, not additional independent-solver benchmarks. Strong jumps need their own mesh study: the sharp fluid full-gravity S2 frequency progresses 0.1743745, 0.1747259, 0.1749153, 0.1750134 mHz at 60,120,240,480 elements, approaching the thin-transition value 0.17511294 mHz.

The standalone N1 gate now asserts identities, count and its 0.5% tolerance, and records the three free-fluid acoustic roots. N5 now asserts both the null material-Q frequency limit (1e-10 relative tolerance) and null modal Q. The regenerated default retains 47 modes and 36 independent frequency checks. `gravity=1.0` is rejected at the request boundary with a field-specific error, rather than failing after matrix preparation.
