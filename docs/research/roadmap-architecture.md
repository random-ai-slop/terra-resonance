# Long-term architecture and maintenance roadmap

Historical planning research for the candidate v1 contract. This is not an additional delivery promise or evidence of implemented capability. It considers research and communication together, with maintenance affordable to a small team. No feature implementation continued during this review.

## Main assessment

Python science, a TypeScript viewer, JSON exchange and independent media outputs do not inherently lock the project into a dead end. The real risks are treating a presentation format as the permanent container for every future scientific representation, letting renderers reinterpret physics independently, and promising a general solver/plugin/workflow platform before real users and data sizes justify it.

Stabilize scientific meanings, provenance, a few user APIs and reproducibility workflows. Internal layout, caches, graphics libraries, geometry generation and encoders should remain replaceable. Candidate v1 should complete one trustworthy chain; later stages should expand capabilities with independent evidence rather than grow every direction at once.

## Dependency map and responsibilities

```text
Models / external results / solve requests
                  |
       solver adapter + source provenance
                  |
      canonical scientific bundle
        +---------+----------------+
        |         |                |
 Python analysis  field contract   exchange / validation / hashes
        |         |
 curves/tables    +-- Python reference evaluator
                  +-- TS interactive evaluator
                           |
                 Scene transforms / sampling
                           |
                 renderer / raster / video / GLB
                           |
                  project / output provenance
```

The solver does not depend on cameras, frontend or encoders. Adapters own source-to-canonical physical conversions. Canonical data does not store displacement normalized for the current screenshot; moving a slider does not change it. Python and TS share a bounded reconstruction contract rather than independently computing Earth eigenmodes. Exporters accept validated data and presentation settings; they cannot silently change models, frequencies or terms. Projects preserve inputs, while manifests explain individual outputs. A hash is neither storage nor a substitute for the original data.

Ordinary module dependencies suffice. No service locator, plugin discovery, remote job system or database is required.

## Sustainable Python/TypeScript duplication

Two evaluators are a reasonable tradeoff: Python supports scientific computing and batch output; the browser needs responsive interaction. Keep duplicated logic limited to harmonics/vector bases, regional interpolation, time coefficients and fixed illustration normalization. Solving and source adaptation remain Python responsibilities.

Necessary now:

1. A mathematical contract and small shared fixtures covering analytic low degrees, poles, centre, interface sides, Q derivatives and real-mode samples. Record independent fixture derivations; Python-generated values alone do not prove TS correct.
2. Independent physical invariants on both sides. Parity plus external mathematical reasoning avoids copying the same mistake twice.
3. Explicit distinction between the Python scientific reference, the bounded interactive evaluator and the broader storable numerical range.
4. Static assets, schemas and fixtures shared without a complex code-generation framework. Shared palettes and coastlines are not shared physics code.

Move TS computation to a worker, use transferable arrays or add further spatial caching only when measured interaction latency or main-thread blocking justifies it.

Exit the dual-implementation arrangement if conventions repeatedly drift across releases, or complex/coupled fields make reliable duplicate maintenance costlier than its benefits. Then prototype a small native/WASM kernel with Python bindings against real workloads. Porting the whole Python solver to WASM now would add build and dependency maintenance without automatically establishing scientific trust.

## Versions, migration and reproduction

JSON arrays suit a small default catalog, inspection and simple deployment. First make identity and read/write semantics clear; do not start with a general binary container.

Keep package and schema versions separate. Unknown wire versions fail; extensible metadata survives. Changes to normalization, axes or field representation require explicit semantic versioning. When a second schema actually exists, an explicit migration creates a new artifact/hash and retains source identity and migration version. Loading old data must not rewrite user files in place.

Self-contained projects are the teaching/sharing default. Large projects may reference external data only through an explicitly portable packaging path, without creator-specific absolute paths. Replaying a saved Scene uses the same artifact. Re-solving uses the same model/settings and scientific tolerances, not guaranteed byte identity across BLAS implementations.

If real data outgrows JSON, separate scientific objects from storage: a small manifest plus typed blocks with dtype, shape, units and content hashes. Choose NPY/archive or chunked storage according to actual access patterns—whole modes, individual regions, time slices or remote access—rather than supporting all formats.

Entry gate: a real catalog exceeds import budgets while common work needs only a subset, or parsing/copying is a measured bottleneck. Exit gate: mode/region access works on that catalog, migration preserves fields, missing/corrupt blocks fail clearly, and small projects stay simple.

## External solvers, caching and expensive work

One pinned production solver and an independent reference path are sufficient for v1. The reference must not become a production installation requirement.

An adapter can remain a normal function: validate request → run/read source → convert units, normalization and identities → record quality → return a canonical bundle. Different solvers need not claim identical capabilities. Unsupported physics is rejected rather than zero-filled or ignored.

Pin upstream commits, document patches and dependency ranges, and retain licenses. Separate compatibility patches from mathematical changes; the latter require derivation, benchmarks and affected-mode records. Add a second adapter when a concrete dataset or research task needs it, such as an existing MINEOS catalog. Consider a capability registry only after at least three independent adapters and actual external installation needs. A generic plugin manager is premature.

Cache recomputable objects first: parsed bundles, spatial bases and completed numerical results. Numerical keys include model content, the resolved request, solver/adapter versions and patches—not just model name and n/l. Store quality with results; an upgraded solver does not inherit old verification by name. Failures are not normal cache hits.

Defer global cache managers, automatic eviction, distributed caches and queues. Avoid duplicate work within a process first; add an explicit file cache and cleanup command only when repeated real work warrants them.

## Higher degrees, complex modes and broken spherical symmetry

The v1 l≤64 limit is a visualization resource bound, not a general numerical storage limit. Higher-degree work must address spatial/temporal aliasing and memory before simply raising a constant. Keep frequency/eigenfunction analysis available for modes unsuitable for real-time 3D.

Complex modes require a new physical contract: complex-frequency time sign, growth/decay, phase and normalization of complex eigenfunctions, left/right vectors and nonorthogonality, and the rule reconstructing a real field. Adding imaginary u/v/w arrays alone does not establish general viscoelastic support. Preserve the real SNREI path while introducing an explicitly versioned new representation when needed; do not add unimplemented complex placeholders now.

Rotation and nonspherical structure also break a single separable l/m representation. Future modes may use harmonic expansions or vector fields rather than being forced into n/l/m. Identity, frequency, provenance and quality remain useful concepts, but field representation must change explicitly. The interface must explain mixed degrees and coupling rather than reuse an insufficient m slider.

Entry gate: runnable solver, reproducible public examples, independent evidence and a concrete scientific task. Exit gate: a complete real-result-to-display/export path, preserved old projects, and honest color/amplitude/time semantics. Without that evidence, keep the work a research branch outside default promises.

## Output backends and API stability

Do not invent an all-purpose scene graph for every output. Stabilize bundle+Scene and geometry/time/color rules; WebGL, offline raster, scientific SVG and GLB may use suitable implementations with declared capabilities.

Standardize preflight, manifests and scientific versus illustration naming. Every backend samples the same field. Unsupported effects are concrete format choices, not repeated permission requests or silent degradation. Validate editable GLB deformation and scientific movies separately; a format need not carry semantics it lacks.

Keep a small public API for models, solving, loading/saving, sampling, projects and core outputs. Internal cache objects, graphics-library nodes and temporary paths should not become permanent APIs. Prefer keyword-only additions. Breaking scientific changes need explicit migration; compatibility cannot justify misleading behavior. Document 0.x changes and demonstrate actual external use before declaring stability.

## Stages and gates

| Stage | Goal and evidence | Entry / exit | Deferred |
|---|---|---|---|
| A: trustworthy baseline | Executable SNREI scope, canonical data, workbench, scientific plots/probes, projects/media, three implementation reviews | Agreed scope → complete acceptance evidence, clean install, truthful docs, independently checked/converged defaults | General solver platform, complex modes, cloud queues |
| B: use and performance | Real research/teaching tasks, reproducible pain points, necessary workers/caches and batch/import improvements | Actual use → measured latency/memory improvement and focused regressions without expanded physics claims | Speculative format/plugin generalization |
| C: interoperability and scale | Second adapter, appropriate array storage, migration, higher-degree analysis | Concrete external data/scale/task → independent sources within one contract and real large-data workflows | Every geophysical format at once |
| D: new physics | Complex/attenuating modes or rotation, one supported path at a time | Reliable source/reference and task → validated new field/export semantics with old-project continuity | All frontier physics in one release |
| E: sustainable collaboration | External contribution, stable APIs, justified plugins/remote batch work | Actual maintainers/integrations → independently reproducible contributions and clear release responsibilities | Governance infrastructure without a team |

These are not fixed dates or unlimited commitments. A is the current acceptance object in this historical proposal; B–E are evidence-triggered directions. They need not form an unnecessary serial dependency chain. A research branch may stop for lack of evidence while the reliable baseline continues to improve.

## Resource and maintenance reality

Radial matrix methods grow rapidly with dimension; current conservative working memory is quadratic. High-order spectra require radial resolution, which browser fps cannot replace. Start with serial degrees and record time/memory before adding parallelism.

A 1200×900, 24 fps, 8-second movie contains 192 frames—about 0.83 GB of raw RGBA. Streaming, temporary disk and encoder preflight are necessary; remote batch services can wait until local batches are sound. Thirty-two spatial fields at high resolution can consume hundreds of MiB; caches have real costs and must invalidate/release by Scene rather than accumulate invisibly.

Duplicated physics, multiple output backends and multiple solvers multiply maintenance. Add each capability with an owner and independent acceptance evidence, or defer its promise.

## Packaging, CI and contribution

A short contributor guide should state module ownership, conventions, necessary checks, how to add a scientific case and how to record upstream patches. Scientific PRs explain changed equations/conventions, independent evidence and affected outputs. Pure interface changes should not force every expensive numerical matrix.

Three check levels suffice:

1. Routine changes: small invariants, data/schema/hash, type/build checks and a short end-to-end output.
2. Affected numerical/output changes: relevant real modes, interfaces and media readback; select by risk rather than coverage percentage.
3. Release: independent references/topologies, default refinement, wheel installation outside the checkout, production frontend, assets/licenses, four user workflows and backend comparisons.

Pin scientific upstream and patches; preserve a reference environment and tested dependency ranges. Avoid permanently freezing every dependency or adopting latest numerical dependencies without verification. Migration, failure protection, licenses and quality are ordinary maintenance, not a reason to introduce telemetry, accounts, a database or a large CI matrix.

## Candidate-v1 decision

Keep separation of science/presentation, canonical semantics, the small dual-language evaluator, self-contained projects, explicit output capabilities and real numerical/release evidence. Defer a universal plugin platform, generic large-data format, full-solver WASM port, cross-machine queues/caches, complex placeholders and every native DCC project format.

Confirm alignment with the user's research priorities and the ability of a small team to validate the feature surface. The architecture already leaves enough extension space. Stage gates improve autonomous development more than additional speculative abstractions.
