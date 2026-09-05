# Numerical ownership decision

Decision: Python and SciPy remain the scientific stack. The experimental toroidal implementation is the first executable migration slice; the attributed Ouroboros adapter remains the default. This is a method and maintenance decision, not a new licensing claim.

## What is independently implemented

`packages/earth_modes/experimental/toroidal.py` owns mesh planning, SI material evaluation, quadratic basis assembly, physical constraints, spectral identity, normalization and provenance. It imports no vendor or default-solver helper. Its toroidal energy is

```
K(W,Z) = integral mu*((r W'-W)*(r Z'-Z) + (l(l+1)-2)*W*Z) dr
M(W,Z) = integral rho*r^2*W*Z dr
```

Every material profile knot is an element boundary. Adjacent solid materials share displacement degrees of freedom; a fluid separates traction-free solid domains. At quadrature points, rho and vs are each linearly interpolated on their own material side, then mu=rho*vs². Four Gauss points integrate the resulting degree-seven stiffness/mass products exactly within each profile interval. This differs deliberately from the default adapter's element-averaged materials; heterogeneous outputs require refinement comparisons rather than bitwise equality.

W(0)=0 is an essential center constraint. Each l=1 solid domain has one exact rigid rotation W proportional to r. A Householder complement in mass-whitened coordinates removes that known null coordinate without an arbitrary frequency cutoff. The positive subspace must pass a scale-aware gap check; unidentified null or nonpositive modes fail explicitly. l=1 positive branches start at n=1, other degrees at n=0. Frequency filtering never renumbers modes.

SciPy uses compiled LAPACK already. Its generalized symmetric solver requires a symmetric stiffness matrix and positive-definite mass matrix; the implementation checks symmetry, Cholesky factorization, scaled residual and FE mass orthogonality explicitly. Passing those tests establishes a solved discrete problem, not continuum accuracy. See [SciPy's documented eigh requirements](https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.eigh.html).

## Public boundary and limitations

```python
from earth_modes.experimental import solve_toroidal
bundle = solve_toroidal(model, l_min=1, l_max=4, mesh_size=80,
                        frequency_min_hz=0.0, frequency_max_hz=0.01,
                        memory_mib=512)
```

Degrees are 1..64. Bounds satisfy 0 <= minimum < maximum and filtering is inclusive for positive modes. All-fluid input returns not-applicable groups; a valid empty selection remains an empty bundle. There is no n cap or fallback backend. The mesh target covers all solid domains combined; mandatory knots and rounding can increase actual element counts. A conservative matrix/workspace/output estimate is checked before mesh or dense allocation. The estimate is a guard, not a measured peak-memory promise.

The original model, including any material Q, is preserved. Output modes are elastic with q=null, no fluid W regions and no potential placeholder. The complete finite-dimensional spectrum is solved, but the accuracy of high branches still requires mesh refinement. Each mode remains `unverified` on arbitrary input; named fixture evidence does not silently certify new models.

FE eigenvectors have exact quadrature mass normalization for algebra diagnostics. Exported quadratic nodes use the existing piecewise-linear field contract and one separate layerwise trapezoid mass factor, recorded in provenance. No per-layer normalization or 1e-8 exported orthogonality claim is made.

## Evidence and promotion

[Owned toroidal evidence](validation/OWNED-TOROIDAL.md) records 19 named independent comparisons, full group diagnostics, profile knots, actual counts and the reproduction command. The source recipe `examples/own_toroidal.py` uses only installed APIs when copied outside the repository; it is not itself an installed package resource.

The current pilot is a useful independent implementation, not a default replacement. Promotion requires retained public contracts, all relevant domain/interface tests, independent physics evidence, representative resource measurements and migration parity for actual user workloads. Do not maintain two complete production stacks indefinitely: retire a replaced runtime path only after its supported scope is covered, retaining pinned development references and provenance.

## Staged numerical route

1. **T:** current independent SI slice. Expand demanding radial profiles/high branches only with explicit convergence and resource evidence. Add interval eigensolving only when dense workloads justify it; verify missing-mode counts and null handling.
2. **R:** own radial energy and gravity formulation. Gates include solid/fluid centers and surfaces, adjacent density jumps, multiple interfaces, g=0/1/2, acoustic and elastic analytic roots, same-table MINEOS and canonical output.
3. **S:** own mixed spaces and constraints. Document auxiliary fields, center regularity, gravitational boundary terms and the physical/essential subspace before replacing assembly. Verify all six phase topologies, l=1 translation, fluid density sheets, thin layers, spectrum completeness and independent eigenfunction shapes. A sparse assembly does not imply a sparse Schur complement or validated fluid spectrum.
4. **Interoperability and research:** a concrete second-solver import with normalization and shape comparisons; then separately validated material kernels, weak attenuation and source/receiver excitation. Source synthesis needs its own spatial derivatives, units and independent source/station reference, not every density/interface kernel first.
5. **Advanced methods:** radial anisotropy, weak rotation/ellipticity coupling, complex rheology and direct 3D each receive a distinct data type, benchmark and resource gate. See [ROADMAP](ROADMAP.md) for scientific dependencies.

Rust/C++/WASM is conditional on measured hotspots, stable numerical interfaces and demonstrated packaging/precision benefits. Julia is an optional independent research environment; Fortran MINEOS is an optional reference tool. Neither becomes a mandatory runtime without a concrete benefit. No plugin registry, generic PDE engine or cloud scheduler is needed for this route.

## Attribution and licensing

The package remains GPL-3.0-only, with all Ouroboros notices and pin `fa63363040a28c08d9fe2bd7d05dcc823d90dd1e` retained. The new formulation is independently organized after studying existing methods; it is not represented as clean-room or permissively relicensed code. Operational ownership, source provenance and independent physical validation are three different claims. A future license change would require its own verified provenance review.
