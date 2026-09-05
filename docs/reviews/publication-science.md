# Public delivery review — science, provenance and Python distributions

Task: PUB-SCI/1. Reviewed 2026-09-04 against the scientific0.2.0 baseline and the coordinator's authorized public-delivery plan. Scope was read-only scientific source, licenses, resources, packaging and existing validation evidence. This report is the only file written; no external publication, runtime edits, Site operations or new agents were performed.

## Result and required corrections

The scientific implementation and offline resources have a concrete source/provenance path suitable for public distribution. No bundled MINEOS executable/source or missing required scientific resource was found in the inspected wheel. The public release should retain the existing bounded claims and make the following small corrections/checks before publishing its newly built packages.

### 1. Resolve the combined package's GPL version claim

`pyproject.toml` and the current wheel METADATA declare `GPL-3.0-or-later`. The pinned Ouroboros checkout supplies the GPLv3 text; its inspected README/mode documentation did not contain a project-specific later-version grant. The generic sample notice near the end of the license document is not itself evidence that the author applied that sample notice to this code. The local vendor notes and model provenance currently say GPL-3.0, which is less specific than the package claim.

Recommended minimal action: conservatively identify the **combined distributed package** as `GPL-3.0-only` unless an explicit upstream later-version grant is located. Synchronize current README/package metadata and clearly explain the third-party boundary; original first-party work can retain separately stated broader permissions if desired. Preserve historical reports as historical statements rather than silently rewriting their evidence. This is a precision correction, not a reason to withhold public GPLv3 source or seek new permission for an already licensed release. Do not relicense the studied/modified numerical code as permissive or claim clean-room independence.

The distinction follows [GNU's explanation of version-specific grants](https://www.gnu.org/licenses/gpl-faq.html.en) and [SPDX's explicit only/or-later distinction](https://spdx.github.io/license-list-data/GPL-3.0-or-later.html). The inspected primary source is the local pinned Ouroboros tree at `fa63363040a28c08d9fe2bd7d05dcc823d90dd1e`, matching the retained LICENSE. The online pinned GitHub LICENSE fetch was unavailable during this review; that does not invalidate the available local source evidence.

Add a dated local-modification line to the shipped vendor notice while touching attribution: the notice already lists substantive patches and points to dated research/review records, but an explicit date at the modification list makes the redistributed fork easier to identify. Keep the package-internal notice and root vendor note consistent.

### 2. Publish newly verified artifacts, not whatever an old glob finds

`dist/python` currently contains both0.1.0 and0.2.0 wheel/sdist files. The existing0.2.0 artifacts are real tested historical release inputs, but their metadata still carries the license expression above, and publication adds CI/documentation/source-layout changes. Rebuild into a clean staging directory and attach only the intended tag/version pair plus checksums. Check that the tag, pyproject version, installed `earth_modes.__version__` and archive metadata agree. Do not advertise these attachments as a PyPI upload unless that separate operation actually occurred; the current README correctly supports source/wheel installation without asserting PyPI availability.

### 3. Apply the existing live-state exclusion to public source deliberately

The Python MANIFEST already excludes `docs/team/CURRENT.md` and handoffs. `git ls-files` confirms CURRENT is nevertheless tracked in the scientific repository; it contains local absolute paths, live/pending task handles and mutable coordination state. It is not scientific provenance or an installed-user requirement. The coordinator should exclude it from the canonical public source publication or replace it there with a non-live example/pointer while preserving the actual primary local authority. Inspect the chosen publication history as well as its final tree. This is an identified operational-state difference between sdist and Git publication, not a claim that a secret credential was found.

## Licensing and resource evidence

| Component | Actual retained source/use | Publication assessment |
| --- | --- | --- |
| Ouroboros | Necessary Python FEM/setup/helper files, full GPLv3 LICENSE, private namespace, upstream pin, detailed local patch notices | Source and notices are present. The v3/“or later” package-expression issue above needs clarification. No claim that the fork is unchanged. |
| MINEOS | Pinned Fortran tool used externally for independent frequency evidence; checked-in R/S/T/I text outputs and controls/reproduction code | No MINEOS Fortran or binary is included in the inspected wheel/sdist. Do not describe it as an installed backend or apply Mineos.jl's MIT license to MINEOS itself. Its GPLv2 repository license is accurately distinguished in research notes. |
| Mineos.jl | Investigated MIT wrapper, not a dependency or shipped implementation | No extra runtime or wrapper distribution claim is needed. |
| PREM profile/default modes | Exact isotropic/no-ocean/3mHz table from pinned Ouroboros, source hash/path and transformations retained; canonical modes keep normalization and per-mode evidence | Keep the approximation name. Default mode data are computed from that model, not a generic observed-Earth catalog or unrestricted accuracy claim. |
| Coastlines | Natural Earth110m v4.1.0, original source URL/archive SHA, public-domain notice | Offline coordinates and attribution are present. [Natural Earth's primary terms](https://www.naturalearthdata.com/about/terms-of-use/) expressly place these raster/vector data in the public domain. |
| Palette | Original signed palette plus sampled Matplotlib cividis, source explanation and full Matplotlib license | Required notice is included in the wheel. Do not remove it merely because the dependency also installs Matplotlib. |
| Experimental T solver | Independent SI assembly, no vendor mesh/assembly calls, documented derivation and GPL package boundary | Operational implementation independence and independent physical validation are separate claims; the ownership document states this accurately. |
| Six lessons | One canonical scientific bundle plus English lesson catalog, complete project generation and scientific cautions | Installed examples are actual package resources, not links to unshipped checkout files. |

The retained MINEOS numerical tables are reference results, not copied solver implementation. No GPLv2/v3 combined-runtime issue is introduced by the present arrangement; do not broaden it to bundled MINEOS code without revisiting that actual change.

## Package contents and usability inspected

The existing0.2.0 wheel contains **44 entries**, approximately **2.57MB uncompressed**, including experimental/toroidal.py, both installed-example resources, schemas, PREM material data, coastlines, palettes, Ouroboros LICENSE/notice and Matplotlib license. METADATA declares Python>=3.11 and NumPy>=2.0, SciPy>=1.15, Matplotlib>=3.9, Pillow>=11 and rfc8785>=0.1.4. There is no bundled native extension, MINEOS executable or local CURRENT record.

The existing sdist contains **216 entries**, including source recipes, tests, scientific validation scripts, independent MINEOS reference outputs and licenses. It deliberately excludes apps/web: the **complete GitHub source tree** supplies the website, while the Python sdist is a scientific-package distribution. README already explains this distinction. Preserve both products rather than making the wheel carry a frontend toolchain.

Existing installed evidence in `docs/validation/phase-2-package.json` and the phase2 release review covers isolated Python3.13 wheel/sdist environments, no editable path/PYTHONPATH, `python -I` outside the checkout, examples/custom solves/experimental API, PNG/SVG/CSV/GIF/MP4/GLB and resource/license access. Native Blender remains explicitly unexecuted. This audit inspected that evidence and archive inventory; it does not relabel those macOS runs as new Ubuntu/Python3.11 CI passes. The new CI must actually establish its own platform coverage.

## Lean CI with meaningful science

Coordinate the following with PUB-CI; do not create a second testing framework:

1. **Ordinary scientific/package CI:** run the existing focused pytest suite on one supported Ubuntu/Python environment. It already checks independent analytic scaling, six topology combinations, center/interface/Q behavior, canonical data/field parity, high-radial sampling, grid/GLB readback, CLI failure preservation and installed-example behavior. These are regression tests, not the expensive full refinement campaign. Install FFmpeg/ffprobe in one job so the real media test is not silently skipped.
2. **Supported-version check:** include Python3.11 because `requires-python` promises it, plus the current tested3.13 line. A second environment can use the core tests and actual installed smoke rather than duplicate every media encode. Assert effective imports/dependencies rather than relying on a matrix label. Avoid claiming every allowed future NumPy/SciPy version is certified.
3. **Resource/build gate:** run the single read-only synchronization check, build wheel/sdist, inspect required notices/assets and forbidden runtime state, then install each from a clean output directory outside the checkout. Exercise one small solve, `load_example`, CLI save/probe and a decoded scientific artifact without repository PYTHONPATH. A source pytest pass cannot replace this gate.
4. **Independent numerical evidence:** the owned T19-row reference matrix is cheap (about2s in the previous environment) and useful for numerical changes. Full N1–N6/two-level PREM/topology recomputation belongs to an explicit numerical-change or manual verification job, not every translation push. MINEOS raw references already exist; compiling Fortran is an optional regeneration check, not a package-CI dependency.

A concrete hazard: `scripts/validate_numerics.py` rewrites canonical `examples/prem-modes.json` and evidence. Running it and then building release packages in the same dirty checkout can silently package newly generated scientific inputs rather than the tagged baseline. Run reference regeneration in an isolated temporary source/output tree and upload its results as evidence; never auto-commit or silently substitute them into a release. Frequency/shape gates and named-case counts determine success, not equality of runtime metadata or an arbitrary image hash.

Website tests/build and Pages subpath checks belong to the separate web/CI owners. Reuse the canonical field fixture and existing tests rather than duplicating numerical solving in JavaScript.

## Claims to retain and one small wording correction

Retain the explicit limitations: general custom models are not uniformly certified; linear Q is experimental; the owned T API is not the default replacement; probe traces are not source-calibrated seismograms; GLB colors are static at the starting time; native Blender is not claimed tested. Agreement with the fork, mesh refinement and independent reference error are different evidence.

README's sentence after its evaluate_field example calls the selected coefficients “canonical mode coefficients,” while that example uses normalized illustration evaluation. Prefer “illustration coefficients applied to canonical eigenfunctions” to align with the accurate normalization explanation later in the same README. This is a small explanatory correction, not a numerical defect.

Subject to the targeted metadata/publication-input corrections and actual CI/distribution results, no further scientific feature work is required for the authorized public release. Do not delay publication infrastructure by reopening advanced physics or the separate planned agreement trial.

## Coordinator release correction

Final source inspection also found `export_comparison` recording a hardcoded generator version0.1.0. It now records the actual package version, and the existing end-to-end CLI comparison journey asserts the saved metadata. The correction changes provenance only; frequency and eigenfunction algorithms/data are unchanged. This explicitly invalidates the prior package candidate bytes and requires fresh CI/release builds.
