# Phase 2 implementation review, round 3: installed release

Reviewer: scope_review. Release: 0.2.0. The wheel and source distribution independently passed installed API/CLI and media workflows outside the checkout. Historical 0.1 archives remain separate and are not evidence for this release. Detailed results are in [phase-2-package.json](../validation/phase-2-package.json); final archive identities are stored in `dist/python/SHA256SUMS` and `dist/python/phase-2-release-verification.json`, outside the sdist to avoid self-referential hashes.

## Installation and actual workflows

Two separate, isolated Python 3.13 environments retained their independently installed scientific dependencies after uninstalling Terra 0.1. Neither used editable installs, system site-packages or PYTHONPATH. Checks ran with `python -I` from temporary directories and confirmed imports from each environment's site-packages. Both `pip check` results reported no broken requirements. The sdist was built through PEP 517 with installed setuptools 84; restricted networking was handled with an existing cached setuptools wheel, not an undeclared source-tree import.

Both installations verified:

- All six stable installed example IDs; independent fresh project objects; preserved content hash; Scene 1.1 and 15-degree defaults. CLI list/save works without a source checkout.
- An explicit custom homogeneous model (radius 1,000,000 m, density 5,000 kg/m³, Vp 8,000 m/s, Vs 4,000 m/s), a T,l=2,mesh20 Cowling solve with four selected positive modes, a new Scene with a saved 30-degree grid setting, and finite field sampling.
- The installed experimental toroidal API on that custom model, producing four explicitly unverified modes. Its first frequency was 0.0015922705742720579 Hz. This is a package smoke result, not another independent numerical benchmark. Its grid/cutaway PNG and GLB were produced from installed code.
- The source distribution's archived recipe driving installed APIs: decoded PNG, parsed scientific SVG XML, 360 numerical probe rows, all 20 GIF frames, and a complete FFmpeg decode of the 24-frame, one-second, 640×480 H.264 MP4. The recipe independently parsed GLB buffers and reconstructed three non-key animation times within its fixed-bound tolerance.
- Installed example/model/palette/coastline/schema/license resources. No source-package directory was inserted into the import path.

## Release finding and fix: small-image annotations

Actual image inspection found fixed annotation fonts overlapping in a 320×240 image and a colorbar label reaching the edge at 640×480. This was treated as a usability defect rather than dismissing a successfully decoded image as sufficient.

The offline renderer now scales annotation fonts with `min(1,width/640,height/480)`, reserves more right margin and scales tick/label padding. It keeps the requested annotations and scientific content. Actual 320×240, 640×480 and 1200×900 images were inspected. A focused bounding-box regression checks note/title separation and complete colorbar-label containment at all three sizes. Final installed checks repeat those PNG sizes after the annotation-only rebuild; the unchanged scientific and encoding mechanisms do not justify repeating unrelated numerical matrices or the entire media run.

## Earlier independent fixes retained

The R1 far-side-cut counterexample is closed: global face/line painter ordering makes the specified undeformed 600×600 rear cut pixel-identical to the uncut foreground view (zero differing pixels, previously 82,994 above five channel levels). A focused rear-line/foreground-cap test also requires a front line to remain visible.

CLI GLB preflight now shares explicit omission resolution with the writer. A legal l=40 Scene with nodes and saved `omit_analysis_overlays=true` passes using the effective geometry budget while retaining the requested nodes and omission provenance. Tests protect against the former CLI/API disagreement.

## Scope and final identity

This gate verifies packaging and usable installed workflows; it does not replace the numerical review. Native Blender execution remains unperformed. Small thumbnails necessarily contain smaller type; no annotation is silently omitted. The website is independently built and its remote publishing approval is outside this Python release gate.

Final archives are rebuilt after documentation/resource freeze. Their runtime and resource bytes must match source and the executed installed packages; the sdist also includes the retained English documentation, source recipe and browser SVG evidence. Generated setuptools caches are removed before rebuilding. Final installation/import checks and identities are recorded alongside the archives rather than asserted from filenames alone.
