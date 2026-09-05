# Browser scientific/export preflight

Reviewed `geometry.ts` and `Viewport.tsx` independently while root implemented fixes.
The findings below distinguish already fixed export issues from remaining renderer work.

## Established strengths

- Cutaway creates both true radial faces, subdivided per material layer with explicit
  side IDs. Updated `radialSamples` includes every selected eigenfunction knot and
  layer endpoint, so thin layers and radial sign changes survive the display mesh.
- Cartesian cached bases use the same field implementation and fixtures as Python;
  colors use undeformed coordinates, fixed limits and shared palettes.
- Root already changed frame buffers to reusable `work` arrays, precomputed palette
  conversion, removed time/amplitude/color/time-scale changes from the spatial cache
  key, and added an empty-term baseline. These close the initial avoidable hot-path
  allocations and reset errors.

## Remaining focused checks for root

**Implementation follow-up:** these five findings were subsequently addressed in
the owned renderer. `validateRenderBudget` includes all overlay caches and a stated
conservative node-segment bound; configuration stages resources and rolls back both
bundle and scene on failure, with an `onReject` callback for UI restoration. Centre
picking is finite, singular node endpoints and all-zero triangles are excluded,
per-region zero-component notes and live clipping/refresh warnings use `onStatus`.
The normal computation remains intentional for lit deformation. The checklist below
records the original rationale, not an assertion that these fixes are still absent.

1. **Resource preflight must include overlays.** `buildPatches` counts surface and
   sections, but coastlines, node segment endpoints and arrows create additional
   per-term spatial caches. At the 128 MiB threshold, enabling these can exceed the
   advertised bound even though the primary mesh passes. Include every planned seed
   count before evaluating fields; node contours can be checked after topology is
   known and before caching their vectors. Do not merely reduce the mesh silently.
2. **Centre picking must not divide by zero.** A selected exact centre on a section
   gives r=0, so `asin(z/r)` produces NaN. Give the material centre a conventional
   latitude/longitude (0/0 suffices), keeping radius_fraction=0 and the layer ID.
3. **Coordinate-singular nodes need exclusion and an explanation.** `component`
   returns 0 at r=0 and a conventional polar component; `nodePoints` can therefore
   promote these endpoint conventions to lines. Exclude centre/pole endpoints from
   theta/phi physical-node classification. An identically zero component currently
   returns no lines but needs a visible “component identically zero / contour not
   applicable” message, with per-region support considered.
4. **Renderer warnings are part of scientific interpretation.** Confirm an on-screen
   clipping indicator and measured playback undersampling warning. The PNG now
   records clipping, but this does not establish the browser view has the same warning.
5. `computeVertexNormals()` remains O(triangles) per animated frame. This is necessary
   for the current lit material; measure high-degree performance before considering
   an unlit scientific view or analytic normal strategy. No extra architecture is
   justified unless measurement shows a problem. Rebuilding the full geometry when
   enabling reference/geography/point is an optimization opportunity, not a blocker.

## Export fixes implemented separately

`browser-export.ts` now supplies the requested PNG and GLB methods, without editing
Viewport. PNG has fixed palette labels, normalized units, physical time/gains,
quality states, clipping counts and per-mode illustration divisors in the manifest.
Optional ExportSpec controls exact dimensions with renderer/camera restoration.

GLB retains true section geometry, reference lines, orthographic camera, actual
wireframe edge topology and static scientific vertex colors. Geometry is in metres
through the root scale, with explicit z-up to glTF y-up rotation. Enabled unsupported
overlays require explicit omission. Duration/aspect come from ExportSpec. Sampling
uses at least 24 intervals per apparent cycle, a conservative C2 interpolation
error bound including Q curvature, and three actual non-key checks per interval.
The manifest records measured/guaranteed/tolerance errors in metres and all omissions.
Three r185's exporter writes orthographic magnitudes as full spans; a narrow
`writeNode` correction restores glTF half-span semantics, verified in serialized GLB.

Necessary tests reconstruct morph displacement independently at three non-key times,
then inspect real binary GLB headers, camera spans, line topology, target counts,
accessor ranges and empty scenes. They also verify explicit omission and restored
duration/aspect settings. PNG visual appearance still requires a real browser capture;
the Node checks deliberately make no claim to validate raster appearance.
