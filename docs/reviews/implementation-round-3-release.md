# Implementation round 3: independent Python release and tutorial acceptance

Historical 0.1.0 review. This item checked distribution, real installation and tutorials. It did not replace the round's scientific/frontend reviews or independently close the overall round.

## Method and necessary findings

Wheel and source distribution were installed into two independent Python 3.13 environments outside the repository, without editable installation, system-site-packages or repository PYTHONPATH. Public PyPI dependency resolution tested assumptions hidden by the development environment. API/CLI execution, decoded media and archive inspection supplied evidence beyond a successful build command.

**R3-R1 / P2: source distribution omitted tutorial and test inputs.** The initial sdist automatically included tests but omitted `examples/prem-modes.json`, production recipes, research scripts and documentation referenced by README/USER-GUIDE. Extracted tutorials and relevant tests therefore lacked their inputs. `MANIFEST.in` now includes Python documentation, examples, evidence and scripts while excluding caches/build artifacts. The frontend remains a repository distribution; Python packages do not include node_modules or pretend to contain the entire web build. README states this boundary.

**R3-R2 / P2: root vendor adaptation notes lagged behind the package.** Root `vendor/README.md` omitted recent density-jump surface-term changes already documented correctly inside the package. The root and packaged provenance notes were synchronized. Original upstream GPL licensing and local adaptation records remain intact.

A `.[build]` extra and standard `python -m build` instructions now produce both archives. Tutorials distinguish a full checkout, an extracted Python sdist and an installed wheel.

## Executed verification

- Archive members are relative, with no `..`, bytecode or `__pycache__`; the wheel has no hardcoded developer `/Users/...` or temporary build paths.
- Three JSON Schemas, PREM material input, shared 256-entry palettes/coastlines, asset licensing, upstream GPL and adaptation notes are packaged.
- Outside the repository: `terra --help`, homogeneous/PREM models, a real T/l=2/24-element solve, inspect, scene, PNG and GLB.
- The README API example actually evaluates a field and exports PNG/GLB with geography resources; GLB omission is explicit.
- The extracted sdist recipe creates PNG/SVG/CSV/GIF/MP4/GLB and reads frame timing, video streams and three non-keyframe morph errors.
- Both environments pass `pip check` and import from their own site-packages.

Native Blender was not executed. This item did not create separate Python 3.11/3.12 or Linux/Windows environments; their existing scientific/transaction evidence remains in the relevant reports.

## Recheck result: passed

Both installations passed. The final runtime files matched source byte-for-byte. The wheel had 39 files; the completed sdist was approximately 4.2 MB. Resource, license and archive-path checks passed. Exact post-build comparison caught a concurrently landed `fields._integer` correction; the archives were rebuilt/reinstalled rather than falsely treating the stale package as final.

All eight outside-repository CLI commands succeeded. The API returned six T modes and a finite 3D vector, and PNGs decoded. The environments used NumPy 2.5.2, SciPy 1.18.1, Matplotlib 3.11.1, Pillow 12.3.0 and rfc8785 0.1.4 without dependency conflicts.

The extracted recipe `examples/recipes/render.py --media --duration 1` produced 640×480 PNG, SVG, CSV, 20-frame/50 ms GIF and 24-frame/24 fps H.264. GLB contained two morph targets and 25 key times. Independent interpolation at 0.137/0.413/0.819 playback seconds had maximum error 3.398×10^-5 of the fixed bound, below 1%. The latest PNG was visually inspected; node lines remained visible against zero-value fill.

Machine evidence: [release.json](../validation/release.json). The lead subsequently closed the other third-round reviews and finalized README/acceptance. Distribution artifacts were placed under `dist/python/`; adjacent SHA256SUMS and release-verification.json avoided embedding an archive's own checksum recursively. The documentation-finalized build retained the same verified runtime files. No blocker remained in this review item.
