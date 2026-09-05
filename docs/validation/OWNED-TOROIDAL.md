# Independent toroidal pilot evidence

Recorded 2026-09-04. All 19 frozen physical cases passed. This is fixture evidence, not a universal error bound or promotion to the default solver.

Reproduce from the source tree:

```sh
PYTHONPATH=packages OPENBLAS_NUM_THREADS=1 python scripts/validate_owned_toroidal.py
python -m pytest tests/test_owned_toroidal.py -q
```

The JSON companion preserves every group, named mode, profile knot, actual mesh count, reference identity, residual and normalization diagnostic. No expected row is silently removed: the script requires exactly 19 comparisons and explicit lookups fail if a named branch is absent.

Sphere/shell materials are R=1e6 m, rho=4000 kg/m³, vp=8000 m/s and vs=4000 m/s. The shell occupies 0.3R..R, with a fluid interior. The sphere uses spherical-Bessel traction roots and shapes; the shell uses an independent first-order traction/displacement ODE with free inner/outer boundaries. Shapes are compared on 4001 common physical radial points, normalized in the same physical mass measure with one arbitrary sign.

PREM uses the original isotropic/no-ocean/3mHz table. Inner-domain l=2/3/4 fundamental references use an independent knot-resolved traction ODE. Inner l=1 and all mantle references use saved MINEOS outputs at the pinned source revision recorded per row. The inner MINEOS raw n=0 l=1 label is explicitly matched to the first positive branch, n=1 here.

| Case | Mode ID | Computed mHz | Reference mHz | Relative frequency error | Mass shape error |
| --- | --- | ---: | ---: | ---: | ---: |
| sphere | `T0_2:solid:sphere` | 1.592270480 | 1.592270479 | 9.582823e-11 | 3.582958e-06 |
| sphere | `T1_2:solid:sphere` | 4.542924313 | 4.542924293 | 4.516787e-09 | 4.456764e-05 |
| sphere | `T2_2:solid:sphere` | 6.693803170 | 6.693802930 | 3.578375e-08 | 0.0001079146 |
| sphere | `T3_2:solid:sphere` | 8.767323665 | 8.767322505 | 1.323122e-07 | 0.0001906891 |
| sphere | `T0_3:solid:sphere` | 2.460344294 | 2.460344293 | 2.43775e-10 | 7.517469e-06 |
| sphere | `T1_3:solid:sphere` | 5.376204371 | 5.376204334 | 6.952523e-09 | 5.595009e-05 |
| sphere | `T2_3:solid:sphere` | 7.564155198 | 7.564154837 | 4.771613e-08 | 0.0001279789 |
| sphere | `T3_3:solid:sphere` | 9.660982334 | 9.660980736 | 1.654432e-07 | 0.000219584 |
| shell | `T0_2:solid:shell` | 1.587650271 | 1.587650271 | 5.885781e-11 | 2.07024e-06 |
| shell | `T1_2:solid:shell` | 4.519726849 | 4.519726844 | 1.018574e-09 | 2.145707e-05 |
| shell | `T2_2:solid:shell` | 6.833667022 | 6.833666950 | 1.059279e-08 | 5.480193e-05 |
| PREM | `T1_1:solid:prem-00` | 2.637325810 | 2.637345000 | 7.276429e-06 | not claimed |
| PREM | `T0_2:solid:prem-00` | 1.135930927 | 1.135930927 | 1.427927e-10 | not claimed |
| PREM | `T0_3:solid:prem-00` | 1.751563350 | 1.751563350 | 3.59031e-10 | not claimed |
| PREM | `T0_4:solid:prem-00` | 2.305449721 | 2.305449720 | 6.675063e-10 | not claimed |
| PREM | `T1_1:solid:prem-02,prem-03,prem-04,prem-05,prem-06,prem-07,prem-08,prem-09,prem-10,prem-11,prem-12` | 1.236227555 | 1.236232000 | 3.595684e-06 | not claimed |
| PREM | `T0_2:solid:prem-02,prem-03,prem-04,prem-05,prem-06,prem-07,prem-08,prem-09,prem-10,prem-11,prem-12` | 0.379706124 | 0.379707000 | 2.30789e-06 | not claimed |
| PREM | `T0_3:solid:prem-02,prem-03,prem-04,prem-05,prem-06,prem-07,prem-08,prem-09,prem-10,prem-11,prem-12` | 0.586582139 | 0.586583700 | 2.661349e-06 | not claimed |
| PREM | `T0_4:solid:prem-02,prem-03,prem-04,prem-05,prem-06,prem-07,prem-08,prem-09,prem-10,prem-11,prem-12` | 0.765791077 | 0.765793200 | 2.771989e-06 | not claimed |

Frequency gate: 0.005; maximum observed 7.27642916e-06. Shape gate: 0.01; maximum observed 0.000219583961.

Every FE group passed symmetry and SPD checks. Maximum scaled FE residual was 1.25606924e-15 (gate 1e-9); maximum FE mass-orthogonality defect was 3.33066907e-15 (gate 1e-8). Sphere, shell and both PREM domains each passed the l=1 rigid W proportional to r null-space test. These FE diagnostics use quadratic basis mass, separately from exported trapezoid mass normalization.

Artificially splitting the homogeneous sphere at 0.5R changed the 4 compared frequencies by at most 0 relative (gate 1e-9); shared-interface W jump was 0.

Mesh targets were 100 for sphere/shell and 240 for PREM. Mandatory PREM knots yielded 348 actual solid elements; per-layer counts and all preserved knots are in the JSON. Runtime was 1.839 s on the recorded NumPy 2.5.2/SciPy 1.18.1 environment with one BLAS thread. Runtime is informational, not a test threshold.

The 13 focused pytest cases separately cover analytic physics, l=1 indexing, exact inclusive frequency filtering without renumbering, all-fluid/empty selections, multi-domain profile/Q preservation, preflight rejection before dense allocation and invalid requests. The source API recipe generated a validated bundle/project and 800×600 PNG under `/tmp/terra-owned-example-final`; clean wheel installation is assigned to the phase release workflow and is not claimed complete by this report. The recipe uses a fixed analytic T(l=2,m=1) phi color envelope with a 5% margin and arrows; neither setting changes the canonical mode.

Remaining limits: no R/S, Q dispersion, source excitation, rotation, anisotropy or general fluid spectrum in this pilot. High-order/high-radial-index modes and extreme material contrasts require case-specific convergence. The existing default solver and default PREM scientific bundle were not changed by this implementation.
