# Implementation review round 1 — numerical solver

Date: 2026-09-04. Reviewer: scope/contract agent, reviewing solver/vendor and
`scripts/validate_numerics.py` implemented by another agent. This is the first
formal post-implementation round, separate from the earlier implementation preflight.
No numerical core files or published evidence were edited during this review.

**Result: changes required.** One P1 scientific defect, one P2 validation-gate defect,
and one P2 accepted-request failure were reproduced. The current PREM frequency
evidence is authentic and consistent with the saved asset; these findings do not
invalidate that specific model's existing benchmarks.

## P1 — same-phase fluid density discontinuities lose an interface gravity term

Locations: `packages/earth_modes/solver.py:98–109`, fluid gravity assembly in
`vendor/Ouroboros/modes/FEM.py`, and phase-only interface loop in `compute_modes.py`.

The model contract accepts adjacent fluid material layers with a density jump.
`_prepare` merges them into one fluid vibrational domain, correctly avoiding an
artificial independent domain. However, `rho_p` contains only each material layer's
interior finite differences. The distributional density derivative at a fluid-fluid
interface is absent. The fluid weak form explicitly contains `-rho_p*g*r²`, while
the interface assembly only visits changes of phase. Consequently gravity=1/2 omit
the density-sheet contribution at these material boundaries.

This is more than an omitted gravity-wave branch: the retained fundamental S2
frequency differs from the thin smooth-transition limit, and both answers are marked
`converged` by mesh refinement.

Minimal reproducible model and request:

```python
from earth_modes.models import homogeneous_model
from earth_modes.solver import solve

def layer(name, r0, r1, rho0, rho1):
    return dict(id=name, name=name, phase="fluid", r_m=[r0, r1],
                rho_kg_m3=[rho0, rho1], vp_m_s=[8000, 8000], vs_m_s=[0, 0])

model = homogeneous_model(1e6, 8000, 8000, 0)
model["layers"] = [layer("inner", 0, 5e5, 8000, 8000),
                   layer("outer", 5e5, 1e6, 4000, 4000)]
bundle = solve(model, families=["R", "S"], l_min=2, l_max=2,
               gravity=1, mesh_size=60, n_max=0,
               frequency_max_hz=.02, convergence_check=True)
```

For the independent consistency check, replace the boundary by three fluid layers:
inner ends at `5e5-width/2`; a transition of width 1000 or 100 m decreases density
linearly from 8000 to 4000; outer begins at `5e5+width/2`. Each transition receives
at least four real elements. All units below are Hz.

| Gravity | Sharp jump S0_2 | 1000 m transition | 100 m transition |
|---|---:|---:|---:|
| 1, Cowling | 0.000249930225467214 | 0.000257293313758008 | 0.000257299534080073 |
| 2, full | 0.000168026361255642 | 0.000175104632893575 | 0.000175112944420222 |

The limiting discrepancies relative to the sharp-jump answer are approximately
2.95% and 4.22%. Sharp-jump 60→120 mesh relative changes are only 0.00591% and
0.03270%; the 100 m transition changes are 8.78e-10 and 1.12e-8. Refinement therefore
does not detect the missing term. R frequencies change less but show the same
nonmatching limit (gravity=1: 0.00446938132310 versus 0.00447047641716 Hz).

Required correction: carry material density jumps into the fluid weak-form interface
contribution while keeping same-phase displacement/pressure continuity and a single
physical domain. Verify the sign and SI/internal-unit conversion against the smooth
thin-layer limit. Do not solve this by inventing independent fluid domains, smoothing
the user's model silently, or claiming additional refinement fixes it. Add one
focused fluid-fluid jump limit regression at gravity 1 and 2. The existing six
topology tests use density 4000 everywhere and cannot exercise this failure.

## P2 — the N1 publication gate records arbitrary errors without failing

Location: `scripts/validate_numerics.py:91–96`.

N1 calculates analytic reference errors using `zip(b['modes'], roots)`, then proceeds
without checking count, identities, or tolerance. A missing mode silently shortens
the evidence; a wrong frequency is still followed by “N1 analytic roots complete”
and can ultimately reach “All N1–N6 gates passed.”

Actual isolated execution of that exact script block, replacing its solve result by
two mode frequencies of 0.04 Hz, accepted relative errors **10.4501743** and
**24.1213600** and printed completion. No full validation matrix was recomputed for
this fault injection. The existing pytest analytic test does assert a tolerance,
but the standalone evidence-generation command does not run that test.

Required correction: validate expected mode identities/count and assert the declared
N1 tolerance before writing evidence. Include the independently tested free-fluid
acoustic case in the N1 evidence if the script continues to claim it in its comment.
Make the null-Q frequency/quality limit an asserted N5 gate too, rather than only
recording those fields. Keep these small assertions local; a second framework is
unnecessary. The current recorded N1 numbers themselves are accurate.

## P2 — gravity=1.0 passes request validation and crashes with an internal TypeError

Locations: `solver.py:56–57` and gravity dispatch in `_assemble`.

```python
solve(homogeneous_model(1e6, 4000, 8000, 4000), families=["R"],
      gravity=1.0, mesh_size=8, n_max=0, frequency_max_hz=.02)
```

Observed: `TypeError: list indices must be integers or slices, not float`, without
structured numerical diagnostics. Membership in `[0,1,2]` accepts the float, then
list indexing fails after preparation. This can arise naturally from JSON `1.0`.
Either normalize an accepted integral numeric enum to int or reject it consistently
at the request boundary with ValueError. It must not enter numerical assembly as an
apparently validated request.

## Checks that passed and bounded interpretations

- The current published PREM file's ordinary file SHA-256 matches
  `docs/validation/numerics.json`; `load_bundle` succeeds. There are 47 modes and
  36 benchmark records. Maximum independent frequency error is
  0.0005356027279050934 (0.0535603%). The saved MINEOS source, input and gravity
  settings are explicitly identified, and its outputs are correctly described as
  frequency-only evidence. Inner-core fundamental T modes use an independent
  displacement/traction shooting equation instead of forcing MINEOS's discrepant
  branch labels into a match.
- Independently compared the whole sampled radial eigenfunction to spherical Bessel
  functions for homogeneous gravity-free modes with 40 elements, fitting only the
  arbitrary common sign/scale. Maximum relative-to-peak errors for R0..R3 were
  2.15e-6, 2.35e-5, 8.14e-5, 1.91e-4; T0..T3,l=2 were 2.46e-5, 1.70e-4,
  3.68e-4, 6.31e-4. These tests compare spatial shape, rather than simply reusing
  the mass normalization or frequency assertion.
- Re-ran three targeted existing tests: null/uniform-Q toroidal limit, R/S modal Q
  against material finite differences with self-gravity, and unchanged T spectrum
  after a homogeneous same-solid-phase layer split. All three passed in 0.58 s.
- Linear Q preserves the reference model and separately records the effective model,
  elastic frequency, corrected frequency, and experimental eigenfunction status.
  It does not claim the unfinished nonlinear Maxwell/Burgers implementation.
- T modes are solved for separate solid domains with domain IDs in mode identity.
  R always uses l=0; S/T include l=1 and retain zero-motion indices instead of
  relabeling every positive fundamental as n=0. Exact rigid translation is projected
  only where its physical symmetry applies, not under Cowling.
- Mixed auxiliary pressure/potential degrees are condensed by explicit indices;
  significant negative retained eigenvalues and ambiguous shifted-inverse window
  counts stop the request. The finite-dimensional essential-space exclusion is
  documented as a scope limit, not a general stratified-fluid gravity-wave solver.

## Small useful improvements beyond defect repairs

1. Preserve one analytic eigenfunction-shape comparison in permanent numerical
   evidence. Visualization is the principal product, so independent shape evidence
   adds substantially more value than another low-degree frequency-only case.
2. Add sign counts or the eigenvalue interval of the **excluded** essential subspace
   to each solver group. In the smooth-transition counterexample 59 raw modes are
   excluded but only 16 are negative and 39 near zero; four positive low-frequency
   modes are excluded too. This is consistent with the documented limited branch
   scope, but the current one-line exclusion label hides the distinction. Report it
   explicitly so researchers cannot read “positive spectrum” as all retained modes.
   No universal mode-tracking framework or expansion into gravity-wave research is
   required for this release.

The next round should independently verify the interface fix and publication-gate
failure path, then sample another material contrast case. Repeating the unchanged
entire 18-case matrix before these targeted fixes would add little evidence.

## R1 repair verification — closed numerical findings

The original reviewer independently re-ran the original counterexamples after the
numerical owner repaired the four fluid weak forms. **All three reported numerical
findings are now verified fixed.** This is repair verification within R1, not the
start of R2; overall round closure remains with the root reviewer.

The new `_fluid_density_interfaces` adds exactly
`-[rho]*g(rb)*rb²` to the radial-displacement interface degree of freedom for R/S,
gravity 1/2. For outward-decreasing density, this is positive stiffness, consistent
with the original volume `-rho'` term. Strict interior-domain bounds exclude the
centre, fluid exterior and solid-fluid domain ends, whose traction contributions
are already assembled elsewhere. The helper is not added to solid weak forms,
where integration by parts already handles material density jumps. Same-phase
materials still share a single physical fluid domain.

Fresh independent runs, with the exact model/request above, gave:

| Gravity | Sharp S0_2, mesh 60 | Sharp S0_2, mesh 120 | 100 m transition, mesh 60 |
|---|---:|---:|---:|
| 1 | 0.000257202005371038 | 0.000257250427658309 | 0.000257299534080073 |
| 2 | 0.000174374535422263 | 0.000174725927881092 | 0.000175112944420222 |

Thus the old persistent 3%–4% discrepancy is removed and the remaining finite-element
error decreases toward the smooth limit. The independent mesh-120 results exactly
match the recorded `density-interfaces.json` values. Its additional mesh-240 results
give sharp-to-thin errors of 0.00947% (Cowling S2) and 0.11287% (full-gravity S2),
within the declared 0.15% gate; they are properly labeled thin-transition consistency,
not an independent solver benchmark. The R results also approach the same limit:
mesh-120 gravity1/2 values are 0.004470440186951988 and 0.004460143849067962 Hz.
The sharp fluid interface retains slower finite-element convergence than a smooth
profile; the fix does not justify claiming exact frequencies from a coarse mesh.

Re-executed only the actual N1 block with three injected faults: missing expected
mode, wrong family/order identity, and frequencies deliberately set to 0.04 Hz.
Each now raises AssertionError before completion. Executing the same block with the
real solver succeeds and produces **five** cases, including the three free-fluid
acoustic roots. The script also now asserts the N5 infinite-Q/null-frequency limit.

`gravity=1.0` now raises the explicit request-boundary ValueError
`gravity must be 0, 1 or 2`; it does not reach matrix assembly. The refreshed PREM
bundle passes semantic validation, its file hash matches the refreshed N1–N6
evidence, and its patch provenance contains `fluid-material-density-sheet`.

No core implementation was edited during this verification, and the full unchanged
18-case matrix was not redundantly recomputed by this reviewer. The numerical
owner's broader 30-test and N1–N6 rerun is separate from the targeted evidence above.
