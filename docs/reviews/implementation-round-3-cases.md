# Implementation round 3: six scientific lessons and final presentation

2026-09-04, numerical_research. Historical review of the implementation after R2 closed. All six self-contained projects, catalog, ProbeSpec/SceneSpec and conclusions were checked; six 960×720 PNGs and the beat probe chart were regenerated and visually inspected. The reviewer did not compete for the lead's CUA browser session. **Necessary improvements in this scope were completed; cases and presentation sources were ready to freeze. Overall closure remained with the lead's UI/package integration review.**

## Findings and repairs

1. **General conservative color bounds weakened curated patterns.** Lesson 5 previously used 2.185 versus a true traveling radial peak around 0.2945; lesson 6 used 1.629 versus a surface-component envelope bound of 0.2777. Numeric amplitudes and per-frame normalization were not changed. The lessons now use 1.05 times their selected component's analytic all-time envelope, disclosed in teaching cautions and `verification.color_policy`. General `default_color_limit` remains unchanged.
2. **Lesson 3 obscured sections and node lines.** The original +25° camera viewed the shell rather than the intended cut faces. It changed to −45° azimuth, 20° elevation, 2.9R span. Nearly white node lines disappeared into pale zero-value fill; both renderers now use `#193e49` for node annotations only, leaving arrows, trajectories and physical fields unchanged. The resulting PNG shows surface and full section nodes. Analytic Y20 and field-invariance regressions still pass.
3. **Lesson 4 lacked a material-side UI action.** Instructions required changing layer_id, but the UI exposed only latitude/longitude/radius. The lead added a Choice of valid sides at the same radius; teaching now calls it Material side. Original exact fluid/solid boundary coordinates and linked Scene/Probe behavior remain. The lead owned real browser click acceptance.
4. **Website tests depended on the parent repository.** Synchronization now copies central `examples/field-reference.json` to the web test fixture directory with byte/hash verification. Tests use that local fixture; PREM evidence tests use synchronized public data. Copying only lib/tests/public/package/tsconfig to an independent temporary directory and reusing installed dependencies passed all 19 TypeScript tests. An initial x64-Python launcher caused a local esbuild architecture mismatch; launching from the native shell resolved that environment issue, which was not attributed to website source.

## Fixed color bounds

Piecewise-linear radial absolute extrema occur at source knots. Section cases inspect both sides of every layer; other cases use the surface. For m=0 the harmonic bound is `sqrt((2l+1)/(4π))`; selected l=2, |m|=1/2 radial harmonics use `sqrt(15/(16π))`; the T2,m1 phi derivative uses `sqrt(15/(4π))/sqrt(6)`. Distinct-frequency terms sum absolute envelopes. Equal-amplitude quadrature ±m2 of the same S02 uses the exact `cos(2φ+ωt)` envelope instead of adding peaks that cannot coincide. A fixed 5% margin applies throughout the playback window; legends show the saved range.

| Lesson | Fixed limit | Verified pattern/conclusion |
| --- | ---: | --- |
| 01 Breathing | 0.289917 | R0_0 is direction-independent and reverses at half period; geometric gain does not change frequency; radial arrows are readable. |
| 02 Tangential | 0.468333 | Real surface-solid-domain 0T2,m1; zero radial projection and rank-one point trajectory; not rotation; clear phi pattern. |
| 03 n/l/m | 0.418013 | m selects a degenerate real basis; n/l select another true solution; n is not forced to equal component zero counts; clear sections/nodes. |
| 04 Liquid core | 0.362010 | Original CMB U is continuous while V can jump; no cross-interface smoothing; liquid participation in R/S is explicit. |
| 05 Traveling | 0.309202 | Same 0S2 ±m2 with π/2 phase; at T/8 the pattern shifts 22.5° toward negative longitude; material does not circle with peaks. |
| 06 Beats | 0.291621 | 0S4/1S2, non-node x component at equator/zero longitude; explicitly balanced local amplitudes; 4097 samples span two envelopes. |

Each lesson has three steps. Catalog and project scene/probe/export match field-by-field and use the same real 47-mode bundle. Beat difference is 3.2813595e-5 Hz, envelope period 30475.1731 s and window 60950.3463 s. Maximum analytic trace error is 5.72e-15; selected cancellation error is 5e-16. No seamless-loop claim is made.

`python scripts/validate_lessons.py` with the repository's stated import setup checked all six lessons at 65 deterministic times without color clipping. Lesson 3 had 2892 true node segments, including 2354 in internal sections. Sampling supplements the analytic continuous-time envelope proof; it does not replace it. Evidence is in `docs/validation/lessons.json`. All six PNGs, beat PNG/CSV and JSON sidecars were regenerated. Five synchronized resources passed `--check`; TypeScript checks and Viewport lint passed.

## Retained limits

- Six examples do not certify every high-n/high-l or custom-model visualization. Their analytic color policy is case-specific. Changing modes, components, materials or observed radii requires a suitable general bound and clipping checks.
- Nodes are zeros of the selected real component on the shell and actual radial sections, not surfaces where every vector component vanishes and not the whole standing wave's instantaneous T/4 zero.
- In lesson 4, one m1 cut plane has a nearly identically zero radial component due to an angular node; the fluid is not missing. The other section and U/V curves reveal interface behavior. Display gain, triangles and projection are disclosed rather than confused with earthquake amplitude calibration.
- Frequency/eigenfunction quality still comes from each mode's numerical evidence. Color/annotation improvements do not upgrade scientific status. Source excitation, rotation/ellipticity and 3D coupling remain on the frozen research route rather than being implied by these lessons.
