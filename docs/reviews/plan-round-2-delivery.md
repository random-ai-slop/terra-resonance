# Planning round 2: delivery and acceptance

Historical review of v0.3 with implementation paused. The revised camera, hashing, normalized/raw scale, timing and GLB capability boundaries from round 1 were accepted. The following findings concern new contradictions or missing executable gates.

## Freeze blockers

**P1 — GIF defaults conflict.** A shared `fps=24` export default violates the proposed allowed GIF rates, while the documentation recommends 20 fps. Resolve an omitted rate by format: GIF 20, MP4 24. Do not silently rewrite an explicitly requested 24-fps GIF. Test default success, explicit incompatibility and actual MP4 frame counts through the public API.

**P1 — Frame rounding differs across languages.** Python `round(2.5)` is 2; JavaScript rounding gives 3. Define `floor(x+0.5)`, record the resulting duration and check half-integer boundaries such as 2.5 and 3.5.

**P1 — GLB accuracy has no achievable threshold.** With 24 linear segments per sinusoidal period, midpoint peak error is `1-cos(pi/24) ≈ 0.00856`, so a 0.1% promise is false. Specify a fixed-field-bound relative error, sample both interval midpoints and unrelated non-keyframe times, and account for Q curvature. A 1% gate or sufficiently finer adaptive keys is enough; reject requests that exceed key budgets. Relative error against an instantaneous zero is unsuitable. No general animation compressor is needed.

**P1 — Scientific probe and comparison exits remain missing.** Add explicit normalization to probe sampling, a focused probe exporter for CSV/SVG/PNG, and request provenance. Comparisons need explicit `(bundle, mode_id)` pairs for the same physical quantity, not cross-model scene superposition.

## Small necessary corrections

- **P2, geometry:** use `surface=solid|wireframe` plus an independent geography flag. State that geography applies to the outer surface and how cuts clip it.
- **P2, cutaway wording:** a fixed `x>0, y<0` quadrant is not always the near quadrant. Remove camera-relative wording rather than changing geometry when the camera rotates.
- **P2, encoder memory:** a single ffmpeg split/palettegen/paletteuse graph can buffer a complete sequence. Use two passes over a frame directory and check `libx264` availability, not merely the ffmpeg executable.
- **P2, real budgets:** l=64 can require roughly 136,000 surface vertices; 64 morph targets already consume around 100 MiB for position arrays before cuts, caches and serialization. Input size does not bound output memory. Suggested limits included maximum image dimensions, 14,400 frames, two billion frame pixels and eight million vertex-target pairs. Final constants need conservative allocation/disk estimates, a successful small case and a rejection test that allocates no large arrays. Do not guarantee a compressed size.
- **P2, explicit omission:** expose unsupported GLB layers before execution and require the corresponding omission option. Avoid both silent omission and an approval dialogue on every export; no generic capability-negotiation framework is needed.

## Validation cost

Use two levels. Fast checks cover analytical fields, hashes, frame endpoints, a small solve, actual format decoding and independent GLB reconstruction. Release checks cover representative topology cases, default benchmarks/refinement, four real user journeys, full media output and clean installation. Re-run affected expensive checks when changes justify them; do not repeatedly run everything or call an unexecuted check passed. One evidence report with commands, environment and hashes is sufficient.

The JCS dependency and shared assets are justified. A broader framework is not. Resolve the four P1 findings before freeze; the P2 items can be addressed with narrow contract and implementation changes.
