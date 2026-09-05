# Product positioning, scientific experience and longer-term route

Historical strategy research written while implementation remained paused. Three technical reviews had made formats, numerical/display conventions and acceptance implementable, but mainly answered whether outputs were correct, not what people could understand or accomplish. This report reopened priorities; earlier drafts, sunk effort and an alleged v1 freeze were not reasons to retain a design.

The user tasks and obstacles below are **design hypotheses** drawn from the project goals and public examples, not findings from interviews or usability studies.

## Core value

Position the product as a scientific workbench connecting modal spatial structure, material motion and measurable signals. A solver supplies credible modes; the workbench makes them inspectable, explainable and reusable. Neither an attractive moving Earth nor an input box for every parameter is sufficient.

Users should progressively answer: where and in which direction does the mode move; why do model/mode/superposition changes alter space and time signals; and which physical quantity and display transformations are being shown, with what route to papers, lessons, videos or other software?

Two failure modes matter. A technically real vector field can remain impossible to interpret if users can only admire colors and silhouettes. Conversely, exposing every research detail immediately can force learners to understand internal data formats before observing a mode.

## Four task chains

| Context | Task chain | Main obstacles | Valuable result |
| --- | --- | --- | --- |
| Research | Choose/edit model → solve/check quality → identify mode → inspect support/interfaces → compare → reproduce | Unstable identities, normalization/sign differences, hidden localization, frequency agreement mistaken for shape accuracy | Raw curves/tables, explicit pairing, probes, radial structure tied to evidence and reproducible inputs |
| Informed outreach | Start with a question → watch motion → distinguish mode/wave/node → vary one parameter → retain explanation | Harmonic patterns mistaken for purely radial motion, pattern travel confused with particle motion, m mistaken for frequency, exaggerated geometry treated as literal | Verified question presets, simultaneous material/pattern views, spatial/time linkage and concise explanations |
| Teaching | Choose concept → prepare states → pause/replay/mark → predict → control one variable → export | Searching controls during teaching, unexplainable frames, simultaneous parameter changes, unreadable projection text | Saved states, deterministic phase seeking, one material trajectory, printable images and bounded questions |
| Production | Define shot → choose science → compose/color/annotate → preview → batch output → edit elsewhere | Coupled science/camera state, broken size changes, missing GLB layers, manually repeated state drift | Reproducible scenes, clean/annotated variants, frame sequences, stable 3D assets and explicit format differences |

Research values justified decisions; outreach values correct relationships; teaching values predictable control; production values reliable reuse. One successful PNG export cannot validate all four.

## Evidence informing the design

[Saviot](https://saviot.cnrs.fr/terre/index.en.html) gives quick mode/cutaway access, although model approximations and periods are not a unified source. Improve scientific binding while retaining immediate access.

The [IRIS ground-motion tutorial](https://web-archive-2022.iris.edu/hq/programs/epo/visualizations/tutorial) connects maps, sections and synchronized traces, using horizontal-motion trails to complement vertical-component colors and placing predictions beside observations. This supports linking space and signal, not assuming its exact layout suits this workbench.

[Russell and Eddy's normal-mode demonstration](https://jbrussell.github.io/outreach/normal_modes/) organizes accumulating modes, their sum and attenuation into a narrative. Reproducible explanatory states therefore precede a general video timeline. [IRIS educational resources](https://www.iris.edu/hq/timeless/story/iris_animations_webinars_and_videos) combine animation with activities/sequences; presets should pose checkable questions, not only attractive names.

## Five depths within one project

### 1. Question presets

Open directly into an editable scene with a compact example/question selector, not a marketing page or mandatory tutorial. Each preset binds real data, scene, question, camera, interpretation and evidence.

| Question | Starting view and action | Minimum understanding target |
| --- | --- | --- |
| How does a planet breathe? | Regular radial mode, reference sphere and selected point; inspect quarter/half periods | Same behavior in all directions and explicit exaggeration |
| Can it oscillate without changing silhouette? | T mode, material grid and tangential arrows; toggle aids | Material positions move without first-order radial bulges |
| What do n/l/m change? | Controlled mode pairs, radial curves and surface pattern; vary one index | Separate radial branches, angular pattern and degeneracy; do not universally name complex branches by zero counts |
| How do both liquid-core sides move? | Real layered cutaway and side-specific probes | Normal coupling, possible tangential difference and absent elastic T support in fluid |
| How do standing waves form a traveling pattern? | Same-degree ±m in quadrature and a material point | Distinguish pattern propagation from material trajectories |
| Why does a nearby-mode sum grow and fade? | Beats, fixed color scale and synchronized probe; disable one term | Envelope arises from superposition, not frame normalization or artificial amplitude animation |

These are scientific examples and acceptance cases, not a new narrative engine. Projects plus short Markdown can implement them.

### 2. Guided explanation without loss of control

Use a few named complete-state bookmarks: observe, change one condition, compare. Users can leave guidance at any time. Do not initially add automatic camera flights, scroll-driven animation or locked parameters. Pause, exact time, period fractions, reset and state copying are the high-value tools. Separate projects can represent bookmarks before repeated use justifies an in-project story sequence.

### 3. Free exploration linking space, points and time

The viewport answers where; radial/time curves answer how; the selected point identifies the material object. A selected coordinate should drive the marker, vector and trace without duplicate coordinate entry. Group parameters by model/solve, modes/superposition, display, probe and output. Collapse advanced settings instead of creating a divergent application behind an ambiguous professional-mode switch.

### 4. Quantitative analysis

Expose U/V/W, frequencies, quality, interfaces and probes from the same mode, with explicit raw-mass versus illustration normalization. Comparisons need a pair, radius convention and normalization. Eigenvector sign is arbitrary; a recorded display sign-alignment option could help without changing raw data. Quality must expose quantity, reference, error and grid rather than a universal green badge. Strong defaults do not establish uniform custom-model accuracy.

### 5. Reusable output

Offer a few purpose presets—publication, classroom, video, 3D and scientific data—over the existing pipeline. Prefill dimensions/background/annotations/fps but retain exact settings. Preview framing, legends, interval and omitted layers before export. Keep source projects/sidecars even when media annotations are hidden. Quantitative plots and production shots may have different layouts while sharing scientific state and color meaning.

## Reconsidering baseline priorities

| Capability | Value and minimum scope | Expansion deferred |
| --- | --- | --- |
| Real sections/shells | Baseline requirement for support, nodes and fluid-solid behavior; same r and regional interpolation as curves | Arbitrary boolean cuts and multi-plane editors |
| Linked point | Baseline core interaction: one marker and trace; CLI probes alone do not establish the relationship | Large particle seeding or integrators |
| Point trajectory | High-priority direct sampling of `u(x0,t)` with phase marker, explaining S/T and traveling patterns | Thousands of trails, flow art or displacement streamlines miscalled trajectories |
| Nodes/zero structure | At least trustworthy radial/component zeros; clear surface/section contours prioritized | General vector-zero classification, permanent multimode nodes and arbitrary 3D isosurfaces |
| Comparison | Baseline explicit curve/frequency pairs; synchronized viewports later if they reveal otherwise hidden structure | Automatic near-degenerate tracking or unconditional n pairing |
| Source excitation | High-value separate stage: moment tensor, source function, units and pre-instrument synthetics, independently checked | Manual coefficients presented as event predictions; immediate full-waveform inversion |
| Observational comparison | Traceable processed event package after sufficient source/receiver capability | A platform searching every earthquake or automatically explaining anomalies |
| Sensitivity kernels | Quantitative link between material location and frequency change after mature comparisons; separate validation | Attractive unverified kernels or automatic inversion advice |
| Sonification | Experimental relative-frequency/decay explanation with explicit frequency shift | Claiming inaudible modes are literal audible Earth sound or encoding physics by musical effects |
| Rotation/ellipticity/nonspherical structure | Long-term new physics and benchmarks needed for splitting/coupling | Artificial splitting or rotating textures passed off as Coriolis effects |

The proposed addition was a linked point/analytic trajectory/radial-zero explanatory loop, not a general particle/node system. It serves all four tasks using existing fields and probes. If scope must shrink, decorative geography or redundant plots should be reduced before this relationship.

## Design semantics

Keep an ink-blue stage, low-reflectance sphere, clear fine lines and light scientific output. Stable meanings matter more than particular hexadecimal colors:

- Physical objects: reference geometry, material grid, interfaces and point use distinct line styles rather than color alone.
- Fields: diverging signed components, sequential magnitude, cyclic phase only if introduced; selection/warnings must not impersonate displacement sign.
- State: distinguish original data, display edits, numerical evidence and output limits; a mode is not the same object as a shot.
- Text: the historical proposal used Chinese explanations with standard n/l/m notation; labels/units remain visible and numeric typography consistent. Phase-2 language rules later superseded this language choice.
- Interaction: sliders have precise entry; reset/undo meaning is clear; phase/time work with keyboards; reduced-motion preferences do not change science.
- Documentation: one question, observable explanation and limitation per preset; papers retain units/sources, while short-video captions avoid internal schema jargon.

No enormous component library is needed. Approximately 20 tokens for color/type/spacing/line widths, five control types and shared legend/caption components were sufficient initial structure.

## Staged route by benefit and evidence

**P0: scientific/product vertical slice.** One real mode can be selected, explained, measured and reproduced. Deliver credible R/S/T, fields, one point/trace, sections, at least three of six initial question loops, PNG/CSV/project save and basic CLI. This is an internal milestone, not the requested complete release. Exit requires independent physics/coordinate/time evidence and mode → point → curve → image without reading source. Agent walkthroughs cannot be called human usability research.

**P1: complete baseline package.** Each user class completes a real task; all promised numerical/formats work. Include raw/normalized analysis, superposition/comparison, point trajectory/node explanation, six questions, media/GLB, clean installation, docs and three implementation reviews. Exit requires reproducible projects, genuine format readback and clear default frequency/shape evidence without ad hoc code or animation repair.

**P2: deeper explanation/comparison.** Add useful component contours, synchronized comparison, bookmark sequences, consistent figure batches and initial quantitative kernels according to actual use. Each needs a concrete question the previous version cannot answer. Shared points/radii/times, independent finite-difference kernel checks and manageable control cost are gates. Avoid building a general timeline first.

**P3: source to station to observation.** Define source functions/excitation, station components, response/sampling and one reproducible event comparison before connectors. Units, normalization, time zero, directions, filtering and responses must be traceable; independent synthetics must agree. Do not hide mismatch by automatic amplitude adjustment. The [ObsPy response tutorial](https://docs.obspy.org/tutorial/code_snippets/seismometer_correction_simulation.html) illustrates Inventory/StationXML, prefilter and response-removal contracts: overlaying miniSEED on a normalized probe is insufficient.

**P4: richer Earth research.** Rotation, ellipticity, nonspherical coupling and validated backends may begin with trusted external result import. Each new physical term needs a scope, benchmark and observable benefit. Change schema only when existing structure is insufficient. Design plugin/distributed/inversion frameworks only when at least two real implementations need them.

## When planning is sufficient

At this research point, numerical/export contracts were mostly ready, but the space–point–time explanatory loop and the value of postponed capabilities still needed a decision. Counting planning rounds was not the criterion. Each user class needed a concrete improved task; each baseline feature needed a task/fidelity/reproducibility reason; all six questions needed a representation; postponed work needed dependencies, benefit and entry/evidence gates. Remaining physical interaction questions should then be answered by a real vertical slice rather than endlessly revised prose.

## Explicit pre-merge recommendations at the time

1. Include signed single-real-term spatial/component nodes, excluding the global time factor. Explain identically zero radial T; omit permanent multimode nodes and full-vector classification. Instantaneous contours, if ever added, need that distinct name. Include radial zero markers.
2. Include a few fixed material trajectories, originally proposed as at most three with one selected by default. Use `x0 + u(x0,t)`, explicit windows and no forced multifrequency/Q closure; reuse Probe. The later counterreview reduced the mandatory count to one.
3. Include all six questions, each with at most three steps, editable parameters and a caution. No grading/accounts/progress/tutorial engine.
4. Include a presentation layout using the same scene, enlarged labels/legend, pause/phase/preset controls and Escape exit. Keep it out of scientific bundle state; do not create another website/player.
5. Defer dual viewports. For spherical models with common l/m, curves and rapid same-camera switching cover many comparisons. Two WebGL contexts, synchronized picking/time/scales, mobile fallback and export composition cost more than their demonstrated benefit at baseline. Add them only when a real localization/mixed-shape case proves the need.
6. Include a small ExportSpec for reusable production settings: format, dimensions, duration/fps, transparency/annotations and explicit omissions. The historical suggestion also included aspect and a possible quality override; later counterreview removed those duplicates. Time starts at scene time; path/overwrite/resource budgets remain execution parameters. Record effective values in manifests without an export-job database or media language.

Thus the proposal added explanatory value and portable production choices while retaining explicit gates for dual views, sources/observations and advanced physics. The lead was asked to challenge each addition using the six cases, not accept expansion simply because this report proposed it.
