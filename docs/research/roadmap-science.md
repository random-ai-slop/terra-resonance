# Scientific capability roadmap: from trustworthy visualization to research

Historical strategic planning material, 2026-09-04. Implementation was paused when this report was written; existing solver drafts/assets were retained. This is not a commitment to implement every future capability. Research was bounded to primary sources that could change architecture or stage order, not an unlimited literature survey. Later scope decisions are in STRATEGY/ROADMAP.

## Assessment and recommendations

The candidate SNREI baseline reasonably answers what a mode looks like, where its frequency comes from, and how to reproduce/display it. It does not fully answer how material changes affect modes or why a real source/instrument observes a spectrum. Calling it a mature general normal-mode research platform would overpromise; leaving only a webpage and probe traces would underserve research.

Position it as a trustworthy numerical and visualization foundation. Keep true solving, complete model/data export, independent comparison, parameter comparison and inspectable quality. Prioritize material-sensitivity workflows and source–receiver response ahead of visually dramatic rotation/3D. Three strategic additions were recommended:

1. A research-question example catalog covering bulk elasticity, core/mantle domains and material/interface changes, with model, request, figure and command; explain where later physics is needed.
2. A minimal explicit parameter perturbation recipe reporting perturbation and Δf/f. Finite differences can precede kernels; unverified upstream kernels are not inversion capability. If deferred, make this the next concrete increment rather than indefinite future consideration.
3. Reusable MINEOS assets: model, controls, raw output, conversion and comparison recipe. A public second driver can follow later without adding a mandatory runtime now.

## Primary-source findings

- [MINEOS official code](https://github.com/geodynamics/mineos) provides modes and modal-sum seismograms for spherical nonrotating models. [eigcon](https://github.com/geodynamics/mineos/blob/master/eigcon.f) converts R/S/T and inner-core T eigenfunctions. Its Fortran method is independent of Ouroboros's matrix method; wrappers must expose normalization differences.
- [Ouroboros](https://github.com/harrymd/Ouroboros) also contains kernels, attenuation corrections and source summation. Inspected summation documentation promised R/S, and kernel documentation described incomplete benchmarks. Reuse saves implementation effort, not units/scope validation.
- [ObsPy response removal](https://docs.obspy.org/packages/autogen/obspy.core.trace.Trace.remove_response.html) exposes response metadata, prefilter/water-level and processing choices. Observed-data comparison therefore needs a recorded pipeline rather than simply overlaying downloaded waveforms and predictions.
- [Nader et al., 2015](https://academic.oup.com/gji/article/201/3/1482/759829) use rotational/elliptical/3D coupling for rotational observations. Preserve pure S/T versus coupled mixed motion: rotating a camera or manually adding two modes is not a Coriolis calculation.
- [Beghein et al. on anisotropic coupling](https://academic.oup.com/gji/article/175/3/1209/636703) motivates separate radial-anisotropy and full 3D tensor stages, not one ambiguous anisotropy switch.
- [NormalModes](https://github.com/js1019/NormalModes) separates model building, parallel mixed-FE eigensolving with spectral slicing/filtering, and postprocessing; rotation branches include gravity. [PlanetaryModels](https://github.com/js1019/PlanetaryModels) uses tetrahedral models, reference gravity and VTK/ParaView. A future 3D path needs mesh fields, not forced radial U/V/W arrays.
- [Shi et al.'s nonperturbative rotating-planet method](https://arxiv.org/abs/1906.11082) uses unstructured fluid/solid meshes, Coriolis terms and fast-multipole gravity; independent rotation references cover the available slow-rotation perturbative regime. This is research infrastructure, not a small website option. The older [1912.00114 preprint](https://arxiv.org/abs/1912.00114) was withdrawn and merged into 1906.11082; do not cite the withdrawn version as the main method.
- [NEP-PACK](https://github.com/nep-pack/NonlinearEigenproblems.jl) supplies nonlinear eigenproblem algorithms/benchmarks, not validated planetary rheology. Materials need causality, physical limits and complex-mode normalization checks separately.

## Capability map and promotion gates

S/M/L/XL are relative effort estimates: focused increment, several cycles, dedicated release, research project. They are not dates. Upstream compatibility, independent data and validation may dominate code size.

| Stage | Scientific/visual value | Prerequisites | Promotion evidence | Effort/risk |
| --- | --- | --- | --- | --- |
| A: trustworthy SNREI | R/S/T, radial fluid/solid regions, gravity comparisons, internal fields and outputs | Current core/contract and source normalization conversion | Topologies, analytic roots, same-model MINEOS, mesh evidence, complete examples | L; existing solver requires real integration repairs |
| A+: material/interface perturbations | Frequency/node/localization response to thickness, density and velocities | A, explicit parameterization and pairing | Central differences converge with step; quality preserved; legal interface geometry | S–M; crossings cannot be tracked by n alone |
| B1: solver interoperability | Existing MINEOS results share a viewport; separate model error from numerical error | Contract and genuine raw examples | Same model/gravity/dispersion frequency and shape checks; phase/norm/label conversion; reproducible install | M; binary layouts, versions, units, licenses |
| B2: bulk/shear/density/interface kernels | Depth sensitivity, frequency budgets and inversion foundation | A+ perturbations, derivatives/potential and pairing | Every kernel checked by finite differences; δln/δ definitions; separate boundary/volume terms | M–L; density/gravity/interface omissions, near-degenerate subspaces |
| B3: source/receiver response | Physical excitation, depth/radiation/station spectra | Canonical modes, derivatives, SourceSpec/ReceiverSpec, concrete B1 reference | Analytic/reciprocity checks, same-source/station MINEOS, separate R/S/T, convolution and units | M–L; plausible wrong traces from phase/tensor coordinates |
| B4: observables/data | Displacement/velocity/acceleration, strain/rotation/gravity | B3, explicit operators, optional ObsPy | Operator limits; recorded response/prefilter/window/spectrum; comparison is assessment, not proof of unique Earth | M–L; low-frequency response, tilt/gravity/site effects |
| C1: mature weak attenuation | Connect material Q, modal Q, frequency dispersion and damping | Required validated B2 bulk/shear weights and reference model | Infinite-Q elastic limit; errors decrease with loss; stated weak-loss range | M; experimental kernel accuracy/near-degeneracy |
| C2: radial anisotropy | Vpv/Vph/Vsv/Vsh/eta while retaining radial separation | B1 and explicit elastic-model schema | Same anisotropic model versus MINEOS; continuous isotropic limit | M; stable elastic tensor, no averaging marketed as anisotropy |
| C3: slow rotation/ellipticity | Splitting, precession, S–T mixing and near degeneracy | Accurate A basis and required matrix elements/selection rules; optional source path | Zero perturbation limit, matrix energy properties, published small cases, basis convergence | L; changing frequencies without mixed vectors misrepresents physics |
| D1: complex rheology | Maxwell/SLS/Burgers, relaxation/oscillatory modes and spatial phase | Validated weak-loss/material operators, complex data, optional NEP | Passivity/causality, elastic/Newtonian limits, roots versus poles, suitable left/right normalization | L–XL; nonlinear/non-Hermitian spectrum and incomplete root searches |
| D2: weak 3D coupling | Lateral structure, topography and tensor mixing | Coupled representation, structural expansions, required kernels | Spherical/selection-rule limits, bandwidth convergence, independent 3D cases, common coordinates | L–XL; truncated/near-degenerate bases, invalid self-coupling approximations |
| D3: direct 3D/strong rotation | Irregular planets and broader non-spherical problems | Mesh backend/environment, 3D adapters, HPC | Constant-sphere/1D and slow-rotation limits; separate mesh/spectral convergence and reproducible resources | XL; mesh, reference gravity, constraints, parallel dependencies |
| E: bounded inversion/uncertainty | Identifiability, resolution/covariance, mode-constraint choices | Required kernels/operators, covariance and parameterization | Synthetic recovery, regularization/prior sensitivity, error propagation, withheld observations | L–XL; good fit does not establish uniqueness |

## Dependencies are not an infinite queue

After A, A+→B2→C1 addresses sensitivity/attenuation while B1→B3→B4 addresses independent origin and observability. These are concrete prerequisites, not requirements to finish every feature in a stage: source excitation does not wait for density/interface kernels, and weak Q only needs the dissipative weights it uses. Radial anisotropy naturally uses B1 and can precede complex Q. Rotation and complex rheology are alternative dedicated research choices, not both mandatory additions to routine visualization maintenance.

Weak-coupling D2 and direct D3 are complementary. Coupling is interpretable and tracks mixing; direct 3D covers more geometry at greater cost. Direct 3D still needs perturbative benchmarks, and a large coupling matrix is not equivalent to every 3D physical effect. Inversion must start from a specific question/data/error model; good sensitivity and comparison are more valuable than an ungrounded general inverse framework.

## Extension boundaries and stop rules

Separate model/request/numerical result from Scene, retain backend/conversion provenance, and remember that SNREI m is a basis label rather than an eternal physical mode identity. Static projects can carry external results without requiring browser solving. Exportable scientific arrays let later solvers/papers reuse the visual layer.

Add `CoupledMode` only when needed: basis modes, complex coefficients, singlet frequencies/attenuation and truncation. Add `MeshMode` for topology/material domains, nodal/element vector fields, true coordinates and complex conventions, compatible with VTK/VTU/ParaView. Neither should masquerade as one family/n/l with radial real arrays.

No plugin registry, cloud scheduling, automatic solver discovery, universal rheology UI or inverse-problem DSL is needed now. Derive abstractions from a second functioning backend or first real complex-data task. Explicit schema migration is preferable to scientifically vague fields.

Every stage needs a concrete question, independent benchmark and reproducible data product. A small eigen-residual proves the discrete algebra, not continuous physics: separate mesh, material and observational error. Visual polish substitutes for none of them. Keep dependency-heavy unbenchmarked capabilities experimental without stopping maintenance of the trustworthy core. Prioritize a complete reliable postprocessing increment when it answers a valuable question without new physics.

The historical recommendation was to retain the true numerical/visual base, strengthen problem-led examples, perturbations and reusable MINEOS evidence, and make kernels/source/observations concrete near-term gated routes. Do not promise mature inversion, full rheology or 3D in v1; do not erase those scientific goals from the long-term vision merely by calling them out of scope.
