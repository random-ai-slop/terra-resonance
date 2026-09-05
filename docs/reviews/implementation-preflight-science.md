# Independent science preflight — 2026-09-04

Scope: `data.py`, `fields.py`, `export_*.py` and exported artifacts, authored by other agents. This is an implementation preflight and **does not count as one of the final three sequential review rounds**. The numerical solver is used only to supply genuine counterexample data. No data/field/export implementation was edited by this reviewer.

Conclusion: one release-blocking scientific-display defect, one material-data export omission, and one accepted-input/runtime mismatch. The first has a shared sampling helper ready for integration; it is not considered closed until both renderers use it and their exports are rechecked.

## P1 — high radial orders alias into the wrong node count

Locations: `export_render.py:109–118`, `export_overlays.py:37–41`.

The surface angular grid grows with l, but the section radius has only `base//2` intervals, irrespective of the active eigenfunction's radial knots or oscillations. This affects the colored section, deformed mesh, node overlay and GLB geometry. Its successful export is therefore not evidence of adequate spatial sampling.

Actual counterexample:

```python
bundle = solve(homogeneous_model(1e6,4000,8000,4000),
    families=['R'], gravity=0, mesh_size=160,
    n_max=60, frequency_max_hz=.3)
mode = next(m for m in bundle['modes'] if m['n']==60)
bundle['modes'] = [mode]
scene = default_scene(bundle)
scene.update(cutaway=True, nodes=True, quality='standard')
```

The genuine R60_0 result has f=0.2443226591 Hz and **60** interior radial sign-crossing nodes in its supplied piecewise-linear U. Sampling the standard section produces only **12** radial nodes. There is no spatial-alias warning. The 25 distinct section radii cannot preserve this field.

A second, deliberately manufactured canonical R field uses 2401 samples of `sin(24*pi*r/R)`, normalized with the contract's mass integral. It passes `validate_bundle`, has **23** interior roots, and lands almost exactly on zero at every old standard section radius. `build_overlays` returns zero segments and:

> sphere: component identically zero / node contour not applicable

That assertion is false: the sparse display grid cannot establish that a material-region field vanishes identically.

Required correction: retain all active source radial knots, independently on each material side, before angular triangulation. Use exact original coefficient data or the resulting complete knot grid when classifying zero regions. If the required vertex/cache product exceeds the budget, reject clearly; reducing fidelity without telling the user is not a valid fallback.

A shared implementation requested by the root agent is now available in `packages/earth_modes/sampling.py` as `layer_radial_nodes(bundle, terms, radius_fraction, base_intervals, max_nodes=...)`. It returns the union of active region knots, material/truncation endpoints and optional presentation-grid nodes. `tests/test_sampling.py` checks that the real R60 retains all 60 roots, the aligned manufactured field retains 23 roots, zero-amplitude terms do not inflate sampling, and a resource limit does not silently decimate.

Discrete justification: on each material side, between adjacent union knots every U/V/W coefficient is linear in r. At fixed angular direction, any component of the full vector sum is therefore linear in r. Keeping those endpoints is sufficient to find every isolated root of this **represented** field. Two extra midpoints per interval do not add mathematical root information; angular-triangle contour error remains a separate issue. This is not a claim that a finite numerical eigenfunction already resolves every continuous physical oscillation.

Integration pending: the export owner must call this helper in `geometry`; the root owner must use the same rule in TypeScript. Recheck actual rendered/GLB artifacts after integration, rather than only the helper test.

## P2 — model CSV discards material Q and reference frequency

Location: `export.py:452–458`, model table manifest construction.

A model with `reference_frequency_hz=.01`, `q_bulk=[1000,1000]`, `q_shear=[300,300]`, solved with `linear_q=False`, exports the header:

```text
layer_id,phase,radius_m,density_kg_m3,vp_m_s,vs_m_s
```

Neither that table nor its sidecar contains `q_bulk`, `q_shear` or `reference_frequency_hz`. This is distinct from modal Q, which is correctly present in the frequency table. A researcher carrying the material table to a Q-enabled calculation loses relevant original material information without an explicit omission.

Suggested small correction: export the two optional Q columns with distinct unspecified/infinite semantics, and put model reference frequency plus parameter semantics in the model-table sidecar. Alternatively make the table explicitly an elastic-profile subset and provide the complete model JSON alongside it. The model hash alone cannot recover missing parameters.

## P2 — accepted MaterialPoint can fail with an internal KeyError

Locations: `data.py:414–434` and `export_overlays.py` point construction.

This scene point passes `validate_scene`:

```python
scene['point'] = {'latitude_deg': 30, 'longitude_deg': 10}
```

`validate_material_point` uses a default radius of one, but returns the dictionary unchanged. `build_overlays` then indexes `spec['radius_fraction']`, giving `KeyError: 'radius_fraction'`. Enforce the SceneSpec point's required radius at validation, or apply one consistent default before downstream access. The ProbeSpec's documented default may remain separate.

A related minor type inconsistency exists for `validate_probe(derivative=1.0)`: validation accepts numeric equality to one while `sample_probe` later requires an integer. Use the shared integer rule so validated inputs can execute.

## Checks that passed

- Raw/illustration normalization: a damped genuine evaluator sample obeyed `raw = illustrated * mode_scale`, with maximum absolute difference 6.62e-24. The divisor is fixed per mode, not dependent on frame or receiver.
- Independent GLB readback: two PREM modes (S0_2 and R1_0), nonzero phases, Q=2, nonzero physical start, cutaway geometry and five non-key times. Maximum reconstructed displacement error was **0.0000621** of the fixed geometric displacement bound, below the required 0.01. This verifies time/morph interpolation at stored material vertices, not radial mesh sufficiency between them.
- Controlled pre-commit failure: existing artifact and sidecar remained byte-for-byte intact when a generated manifest contained a forbidden nonfinite value. The existing export tests also exercise a rename failure between pair commits.
- Existing tests already check raw derivative probe units, explicit GLB omissions, GIF timing, true SVG paths, analytical Y20 surface contours and material side validation. No duplicate implementation-mirroring tests were added for those already covered cases.

The high-n and aligned-grid regressions should remain as meaningful scientific tests. No broad test suite expansion is needed beyond these specific defects and their cross-renderer integration checks.

## Follow-up within this preflight

After the export owner integrated `layer_radial_nodes`, the same actual R60 case now yields **60** section nodes (previously12). The aligned sine case now yields **4512** contour segments, preserves its23 interior roots, and no longer reports the section as identically zero. Both sampling regression tests pass. This closes the reproduced offline radial-alias defect at the data/geometry/overlay level; browser integration and final visual artifacts remain part of subsequent review.

The export owner added material Q columns and model reference frequency metadata. A remaining detail was sent back: blank CSV values must distinguish an absent Q array (unspecified) from a present null entry (infinite Q), using sidecar presence metadata or a complete accompanying model JSON. The point/default mismatch was sent to the data owner for resolution.
