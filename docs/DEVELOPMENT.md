Public source, Pages and release operations are documented in [PUBLISHING](PUBLISHING.md). The live coordination record is local; public contributors can use [CURRENT.example](team/CURRENT.example.md).

# Development and maintenance

Active agent coordination follows [WORKFLOW](team/WORKFLOW.md), routed by root AGENTS.md. [CURRENT](team/CURRENT.md) is the sole live task record and is excluded from source distributions; worktree copies are historical. Earlier phase-specific ownership below remains historical context.

The first release completed three sequential implementation reviews; see [the log](reviews/IMPLEMENTATION-LOG.md). Development checks, independent numerical evidence, planning reviews and implementation reviews remain separate records. Phase 2 has its own [scope and ownership](PHASE-2.md). Successful commands alone do not establish scientific correctness.

## Module boundaries

| Path | Responsibility |
| --- | --- |
| `packages/earth_modes/models.py` | SI material models and source attribution |
| `solver.py`, `vendor/Ouroboros/` | Default numerical adapter, spectra, quality and pinned upstream |
| `experimental/` | Independently assembled experimental solver; no automatic fallback or default promotion |
| `data.py`, `assets/schema/` | Semantic validation, JCS hashes, defaults and portable projects |
| `fields.py`, `sampling.py` | Vector spherical harmonics, derivatives, material sides and faithful radial sampling |
| `export*.py` | Export API, budgets/transactions, geometry/overlays and GLB |
| `analysis.py`, `cli.py` | Separate-model comparisons and a thin command layer |
| `examples.py` | Fresh installed projects from one bundle and one English catalog |
| `apps/web/lib/science/` | TypeScript contracts, matching fields/geometry and browser artifacts |
| `apps/web/components/observatory/`, website i18n | UI, locale presentation and controls |
| `assets/`, `examples/`, `scripts/` | Canonical/generated resources and reproducible research/production recipes |

Importing the numerical API does not create a plotting window or browser. Solvers return data; writing belongs to data/CLI/export boundaries. The website does not run a hidden Python service. Scene time, probe sampling and production settings are distinct. Locale is website presentation state, not a scientific field.

Change CONTRACT before changing scientific conventions, then update Python, TypeScript, JSON Schema, parity fixtures and guides together. Structural schemas do not replace semantic checks. No renderer may independently repair an eigenfunction or normalize each frame for appearance.

## Setup and resource synchronization

For development in the full repository:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test,build]'
.venv/bin/terra --help
.venv/bin/python scripts/sync_web_assets.py --check
cd apps/web
npm ci
npm run dev
```

The maintained default bundle is `examples/prem-modes.json`; the English generator writes `examples/lessons/catalog.json`. The package installs one generated bundle/catalog pair under `assets/examples/`, not six duplicate bundles or preview images. Coastlines, palettes and the PREM material source are maintained under `packages/earth_modes/assets/`.

Refresh scientific source data only when the numerical change requires it:

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/validate_numerics.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python scripts/generate_lessons.py
.venv/bin/python scripts/sync_web_assets.py
.venv/bin/python scripts/sync_web_assets.py --check
```

`validate_numerics.py` recomputes cases and evidence; ordinary copy/style changes do not need it. The lesson generator retains the scientific bundle and validates its teaching constructions. `--no-previews` skips media production only.

The sync command validates the catalog's bundle hash and project settings, atomically copies five website resources (including the local parity fixture) and two installed-example resources, then reads back SHA-256. `--check` is read-only and fails on a mismatch. `--target package` or `--target web` supports separately owned destinations; release checks use the default `all`. Never hand-edit generated copies. When the Site checkout has a single owner, that owner performs website writes.

## Meaningful validation

```sh
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m pytest -q
cd apps/web
node --import tsx --test tests/*.test.ts
npx tsc --noEmit
npm run build
```

Physics checks use independent spectra, scaling, regular centers, interfaces, normalization and Q behavior. Cross-language cases compare actual fields. Export checks decode media and CSV, reconstruct non-keyframe GLB displacement and exercise controlled rollback. High-radial-order counterexamples prevent display sampling from deleting nodes. CLI tests use small real solves and necessary failure paths.

Select checks by the change. Translation needs maintained-text and actual locale/layout checks, not an unrelated spectral recomputation. A field/schema change needs Python/TypeScript parity; an exporter change needs the affected output decoded; numerical patches need independent physical and topology evidence. Broaden only for a new change, failure or unresolved concern.

Locale coverage includes existing diagnostics, asynchronous errors, accessibility, quality descriptions and English artifacts from Chinese charts. A message-key count does not prove a usable layout. Test preserved physical time/camera/probe/export state and edited user metadata. Legacy Scene 1.0 and new 1.1 need explicit round trips. Grid density must preserve scientific samples and participate in vertex/morph budgets.

Single-thread BLAS is an optional performance choice for small matrices, not a different model. A restricted environment can set `MPLCONFIGDIR=/tmp/terra-mpl`; the library does not rewrite HOME. GIF/MP4 validation needs FFmpeg/ffprobe. Native Blender is a separate optional environment check.

## Reproducibility boundaries

- Versioned input, complete models/requests, pinned upstream and mode-quality evidence are scientific provenance.
- `bundle_hash` is RFC 8785 JCS; file-byte SHA-256 checks distribution copies. They are different claims.
- Animation uses specified physical times, not render duration. GLB records adaptive interpolation, static initial colors and omissions.
- GLB positions use float32. An independent readback restores declared shell/interface radii before evaluating the strict float64 scientific field; do not widen every API boundary tolerance to accommodate file quantization.
- Media and sidecars are staged, verified and committed as a pair with controlled rollback. This is not a power-loss guarantee or a global transaction over an entire batch.
- Original `model.json` accompanies material CSV because an empty cell cannot distinguish unspecified Q from infinite Q.
- Maintained artifacts and documentation are English. Website translations do not replace user metadata, source citations or authoritative licenses. Historical reports retain findings and the verification status at the time they were written.

## Small-team and agent workflow

The lead owns scope, shared interfaces and final integration. Each agent receives a bounded task, explicit file ownership and expected evidence. Numerical research, product review, fields, exports and UI can run in parallel when their inputs are stable; two owners do not edit the same file concurrently. Send readiness notices when dependencies are executable, not merely drafted.

The frozen phase-2 ownership manifest assigns English documents and shared files. The package owner is the sole CLI/schema writer; the product owner supplies the examples API and generator; root integrates website translations and destinations. Preserve the reviewed Chinese lesson resource before regenerating canonical English lessons. Changes to scientific interfaces require a coordinated handoff.

Independent review changes viewpoint: numerical correctness, cross-output consistency and actual research/teaching/production workflows. Reports need reproducible counterexamples and the smallest adequate repair. Recheck serious defects after repair. The baseline's three sequential implementation reviews are distinct from planning or preimplementation review; later work records its own changed behavior and evidence rather than borrowing historical passes.

Reject unbounded feature competition. Before adding a display layer or output, identify the user task, whether existing state is sufficient, and how every relevant exporter preserves meaning. Unsupported behavior fails explicitly or requires an explicit omission; silent downgrade is not acceptance.

## Release checks

1. Run relevant regressions, complete integration/build checks and all resource hashes; inspect licenses and source attribution.
2. Install the wheel and source distribution into independent environments without editable paths or repository PYTHONPATH. Run installed examples, a small custom solve, scientific image/probe and media outputs from outside the repository.
3. Execute the source media recipe and retain project/manifest/decode evidence. Claim native `.blend` support as tested only after actually running Blender.
4. Review English/Chinese website flows and English artifact labels; confirm schema/version compatibility and source-copy freshness.
5. Update version, acceptance and limitations only after evidence is complete. Website deployment is a separate action and does not determine package usability.

```sh
.venv/bin/python -m build --outdir dist/python
python3 -m venv /tmp/terra-release-check
/tmp/terra-release-check/bin/python -m pip install dist/python/terra_resonance-0.2.0-py3-none-any.whl
/tmp/terra-release-check/bin/terra example --list
```

Use the actual release version in filenames. The Python source distribution contains its docs/examples/evidence; build the website from the complete repository. Dependency installation requires a network or prepared wheel cache. Perform a clean install for a release rather than repeatedly rebuilding environments for ordinary edits. Keep final archive hashes in an adjacent `SHA256SUMS`, avoiding a self-referential checksum inside the archive.
