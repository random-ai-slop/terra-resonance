# Data, fields and reproducible projects

Terra separates scientific `ModeBundle` data from presentation `SceneSpec`. A `terra-project` contains both, with optional `probe` and `export` requests. The Scene binds to the whole bundle's SHA-256: changing material, eigenfunctions or provenance requires a matching Scene. See the [JSON Schema](../schema/README.md) and [exact contract](CONTRACT.md). Schema validation describes structure; Python and TypeScript also check quality evidence, normalization, boundaries and cross-field relationships.

The installed example API avoids depending on a source checkout:

```python
import numpy as np
from earth_modes import load_example
from earth_modes.data import make_project, save_project
from earth_modes.fields import evaluate_field, sample_probe

example = load_example("03-indices")
bundle, scene = example["bundle"], example["scene"]
point = [[bundle["model"]["radius_m"], 0.0, 0.0]]
displacement = evaluate_field(bundle, scene["terms"], point, time_s=100.0)
velocity = sample_probe(bundle, scene, lat_deg=30.0, lon_deg=120.0,
                        radius_fraction=1.0, times_s=np.arange(0, 3600, 10),
                        derivative=1, normalized=True)
project = make_project(bundle, scene, export={"format": "png", "width": 1600})
save_project(project, "session.terra.json")
```

Saving refuses existing targets unless `overwrite=True`. Validators do not mutate caller data; `make_project` deep-copies bundle and Scene, expanding production defaults in a new object. Projects contain neither absolute output paths nor machine memory budgets. Media manifests describe actual time, gains, sampling, software and provenance; complete recovery still requires the project.

Media transactions also protect outputs created by another process while rendering. Files commit through exclusive hard links; directories use OS exclusive rename. If a second member fails to commit, rollback removes only this transaction's own output. macOS uses `renamex_np(RENAME_EXCL)` and Linux `renameat2(RENAME_NOREPLACE)`; unsupported platforms fail explicitly instead of falling back to an overwriting rename. This is not a claim of filesystem-level multi-file atomicity during power loss. See the [Apple exclusive-renaming documentation](https://developer.apple.com/documentation/foundation/urlresourcevalues/volumesupportsexclusiverenaming) and [Linux syscall manual](https://man7.org/linux/man-pages/man2/renameat2.2.html).

Scientific images and probe plots default to 800×500 at 100 dpi. The Python `export_plot` and `export_probe` APIs accept `width`, `height`, `transparent` and `annotation`. For CLI project input, a present ExportSpec is resolved first and contributes those four options; explicit flags override them. CSV/tables ignore inherited image settings but reject explicit image flags. Movie-only flags do not apply to scientific plots. Manifests record actual production options. `export_artifact` requires its format to match the output suffix; CLI resolves the explicit suffix before calling it.

## Units and eigenfunctions

Radii use m, density kg/m³, wave speeds m/s, frequency Hz and physical time s. Models consist of radially connected material layers, including same-phase discontinuities. Radius increases strictly inside each layer; interfaces appear once on each side. Density and bulk modulus are positive; solid Vs is positive and fluid Vs is zero. Missing material Q means unavailable; null means infinite Q. Material Q and a mode's attenuation Q are distinct quantities.

Canonical radial functions use

\[
\mathbf{s}=uY\mathbf e_r+v\nabla_\Omega Y/k+w\mathbf e_r\times\nabla_\Omega Y/k,
\qquad k=\sqrt{l(l+1)}.
\]

R has l=0 and u only; S has l≥1 and u/v; T has l≥1 and w only. Tangential basis terms vanish for l=0. Canonical normalization is the sum of separate layer trapezoidal integrals, `∫ρr²(u²+v²+w²)dr = 1`. Density is linearly interpolated within the corresponding material layer onto each mode-region grid. One factor scales the entire mode; normalization is neither per-layer nor interpolated across a jump. This is a discrete convention on the published sampling. Coefficients have units kg^(-1/2), **not metres**. Potential exists only when actually evaluated and records solved/postprocessed status, units and the gravity approximation.

## Harmonics, axes and time derivatives

Cartesian axes form a right-handed system: z north, x at equatorial longitude 0, y at equatorial east longitude 90°. θ is colatitude and φ east longitude. Complex harmonics are orthonormal with the Condon–Shortley phase. The real basis is `√2 Re(Y_l^m)` for m>0, `√2 Im(Y_l^|m|)` for m<0, and `Y_l^0` for m=0. Thus the l=1,m=1 scalar is proportional to −x/r and m=−1 to −y/r.

Each term has time factor `a exp(-γt) cos(ωt+phase)`, with ω=2πf, γ=πf/Q, γ=0 for null Q and t≥0. `derivative=1/2` differentiates the whole envelope:

\[
T^{(d)}(t)=a\operatorname{Re}\{(-\gamma+i\omega)^d
\exp[(-\gamma+i\omega)t+i\,phase]\},\quad d=0,1,2.
\]

Quadrature phases on ±m can make a travelling pattern. Arbitrary multiple frequencies or finite Q do not automatically form a seamless loop.

ProbeSpec stores a sample count, with times `start_s + k*step_s`. CLI duration uses the same absolute floating-point arithmetic to exclude samples rounding to the half-open interval's endpoint, and saves the actual count. Multi-sample steps must resolve the binary64 spacing at the final time. Unresolvable steps or a duration that cannot advance the start fail instead of writing duplicate timestamps.

## Interfaces, poles and exact centre

Each region interpolates only within its layer and covers both endpoints. Missing regions contribute exactly zero. An interface defaults to its outer side; `layer_id` selects a side explicitly, including for probes. A T mode can occupy one solid domain separated from others by fluid; adjacent solid material layers are not independent domains. Fields outside the model vanish. Boundary roundoff within `64 * float64_eps * radius_m` snaps to the interface; larger offsets use their actual location.

Poles use analytic harmonic derivative limits. Compare Cartesian vectors rather than singular spherical components; displayed θ/φ components at a pole use φ=0. A regular S,l=1 centre satisfies `v(0)=√2 u(0)`. With A=√(3/4π), its m=0,1,−1 fields are respectively `A*u(0)*ez`, `-A*u(0)*ex`, `-A*u(0)*ey`. Other regular modes vanish at the centre. Import regularity tolerance is `1e-6 * mode_scale`; upstream endpoint corrections must be recorded rather than hidden behind an arbitrary centre direction.

## Presentation, grids and scientific quality

Illustration fields divide each mode by its fixed `max_r sqrt(u²+v²+w²)` before applying dimensionless Scene amplitude and phase. `deformation` converts that field to visible displacement as a fraction of model radius (default 0.035); arrows have independent `arrow_scale`. `time_scale` is physical seconds per playback second. `normalized=False` skips the illustration divisor but remains a mass-normalized field without source calibration. Normalized derivatives use s⁻¹/s⁻²; raw derivatives kg⁻¹ᐟ²·s⁻¹/kg⁻¹ᐟ²·s⁻².

The Scene saves a fixed color limit: signed components use a symmetric range and magnitude starts at zero. Defaults use fixed angular bounds; colors never chase instantaneous peaks. Clipping changes appearance only and is reported. Geography follows undeformed material coordinates. Real cut faces sample the radial interior. Nodes remove the time factor and require one nonzero real term and a signed component; identically zero regions are identified separately instead of drawing arbitrary dense lines.

Bundle and Project remain version 1.0. New Scenes are 1.1 and require `wireframe_spacing_deg`, accepting null/5/10/15/30; defaults use 15. Scene 1.0 permits only an absent/null value and is preserved during load/save. Null means legacy shell triangle edges. Non-null spacing is active only for wireframe surfaces; filled surfaces retain the saved setting without allocating lines. Both versions use filled scientific cut faces, correcting the earlier offline all-wire behavior.

Visible lines are material-coordinate parallels and meridians. Their spacing does not change the dense scientific mesh, solver, probes, nodes, harmonics or time sampling. Degree-aware curve sampling is still applied at every spacing; cuts retain boundary segments and omit segments whose undeformed midpoint lies strictly in x>0,y<0. If spacing×maximum degree≥90°, a notice warns that extrema can lie between visible lines. See CONTRACT for exact indexing and memory accounting.

Per-mode `provenance.quality` separates mesh convergence from benchmark evidence. `unverified` is not a pass; `unconverged` needs failed mesh evidence; `converged` needs passed mesh evidence; `benchmark_checked` needs a passed reference check. Frequency agreement does not validate eigenfunction accuracy. `Scene.quality` is solely display sampling quality.

Benchmark quantity is `frequency_hz`; its model hash must match the current canonical model. Stored relative error must agree with `abs(f-reference)/reference` within `64*eps*max(1,error)` rounding. These checks establish internal consistency, not authenticity of a source string or an independent experiment. Provenance retains settings, approximations, excluded discrete subspaces and sampling. `field-reference.json` is an analytic field fixture, not Earth eigenmode data.

## JCS identity and compatibility

Hashes use SHA-256 of RFC 8785 JCS bytes. Key order, whitespace, 1 versus 1.0 and negative zero do not cause false differences; Unicode is not normalized. Bundle identity covers all validated content, including unknown provenance. Model identity omits only top-level model provenance and still includes id/name, so renaming changes identity.

Wire integer fields accept finite safe integer-valued JSON numbers such as 2 and 2.0 without rewriting input. Consumers locally convert array/harmonic indices to native integers. The direct Python solver request has its separate strict-integer API.

JSON must be finite and binary64-compatible. NaN, infinity, duplicate keys, lone Unicode surrogates and integer literals outside ±(2^53−1) are rejected. Large identifiers should be strings; valid large scientific floating quantities can use exponent notation. Shared JCS fixtures check Python/browser agreement. Numerical re-solves across BLAS/OS versions use tolerances, not byte-identical hashes. Unknown wire versions fail explicitly; unknown optional metadata is preserved. Display limits l≤64, 32 terms and resource bounds are independent of solver capability and do not silently truncate numerical results.
