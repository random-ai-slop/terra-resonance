# Agreement audit 3: frozen distribution and installed usability

Assignment AUDIT-RELEASE/1. Preparation reviewed primary `e9e660e5`, PHASE-3
revision 3, AGENTS/WORKFLOW/primary CURRENT, `scripts/check_distribution.py`,
`pyproject.toml`, MANIFEST, the agreement guide and copied recipe. Only this
review file is owned by the reviewer. No build, install, numerical rerun, source
change, or external publication was performed during preparation.

**Status: candidate audit 3 passed on frozen input `4e1d79ad`; final hosted
build/publication remains a separate root-owned boundary.** Preparation findings
and their corrections are retained below. The candidate closure at the end
records actual installed evidence; earlier source tests and 0.2.1 release
evidence were not substituted for it.

Preparation follow-up: independently inspected root's subsequent checker diff.
Both gaps below are addressed in source: the sdist guide receives byte equality
checking, and recipe readback runs in an isolated child through installed public
loaders. It checks all four actual mesh declarations, pair/source directions,
full embedded bundle equality, independent-frequency row/source consistency,
complete sidecars and scalar output consistency. No new material regression was
found in that diff. This closes the preparation design gaps; execution on frozen
archives remains pending and is not inferred from source inspection.

## Preparation findings

### P2 — shipped guide identity is not yet checked

The archive audit requires `docs/AGREEMENT.md` to exist, but compares only the
agreement recipe and runtime tree against current source bytes. An old guide
with outdated commands could therefore pass the frozen archive audit even when
the inspected maintained guide has changed. This is an evidence gap, not an
observed wrong command in the current guide.

Minimal correction: compare the archived agreement guide bytes to the frozen
source, alongside the existing recipe comparison. Root accepted this correction.
Do not rebuild merely to embed the candidate archive's own hash inside itself;
final checksums remain beside the archives.

### P2 — recipe readback does not yet establish the actual-resolution journey

`check_recipe_outputs` currently uses plain JSON parsing, checks one row per
report and a shape ceiling, requires four bundle filenames, and decodes the
PNG/SVG/CSV. It does not load the four reports through the installed public
validator, connect each embedded source to its saved bundle, or verify the
declared actual resolutions and reference/candidate direction. A recipe that
accidentally saved the same coarse output under both mesh labels, or paired the
wrong valid sources, could pass these predicates. The inspected recipe itself
does use the correct 20/40 loop and four explicit comparison directions.

Minimal correction, accepted by root: perform readback inside the same isolated
installation using public `load_bundle`, `bundle_hash`, and `load_agreement`.
No additional solver run is needed. Check:

- All four saved bundles validate. For this fixed one-layer homogeneous sphere,
  the two requests have declared actual `sphere` element counts 20 and 40 and
  matching actual totals, with the fine count greater than the coarse count.
  Check reported radial-sample counts against actual regional array lengths;
  there is no need to freeze a general `nodes=2*elements+1` rule.
- `cross-20` is default-20 → pilot-20; `cross-40` is default-40 → pilot-40;
  each refinement is its named method's 20 → 40 output. Their explicit pair is
  `T0_2:solid:sphere` on both sides. Embedded source hashes must match the saved
  source bundles and row counts must match those sources.
- The independent-frequency evidence names each of those four files once and
  records its actual selected frequency. Its stored reference is positive and
  finite; stored relative errors agree with those frequencies/reference and
  satisfy the named ceiling. This connects the reference evidence to the actual
  outputs without relabeling code agreement as independent truth.
- The scalar figure/report outputs remain loadable and consistent after the
  original bundle files are absent; the existing generic installed sidecar-only
  check already exercises this feature with two pairs. Repeating every scientific
  counterexample in the distribution checker is unnecessary.

These narrow corrections should be verified on the final checker before the
root performs the frozen installation runs. Either a retained independent
readback or the corrected checker can supply evidence; a successful subprocess
exit and filenames alone cannot.

## What the existing release path already establishes

The checker selects exact-version wheel/sdist filenames, checks the common
version and SPDX expression, requires the new packaged agreement schema and
existing examples/licenses, and compares the entire runtime/resource tree to
source bytes. MANIFEST includes the source recipe and guide while excluding
live CURRENT, operational handoffs, artifacts, environments and website source.
The recipe is deliberately obtained from the sdist, not promised as a wheel
resource. Its archived bytes must match the copied accepted source recipe.

Each archive is installed into a separate fresh venv. Numerical/package imports
must resolve inside that installation; `-I`, removed `PYTHONPATH`, and an outside
working directory prevent the source tree from supplying missing modules. The
copied recipe uses installed public APIs and already required SciPy functions,
not repository reference tables. Checking its outputs in that same environment
will complete the remaining authority boundary described above.

The installed feature check computes two explicit pairs through the CLI,
validates the saved report, renders a selected native SVG, removes the original
bundle/report files, and recovers all rows and another PNG from the full sidecar.
It compares CSV frequency differences and complete sources, rejects a tampered
negative distance without publishing an output, and exercises the existing
general comparison API. Existing example loading, small custom default/pilot
solves, PNG/SVG/probe/GLB decode and `pip check` remain useful compatibility
checks. They do not replace the earlier scientific or actual typography audits.

The recipe's existing-directory retry must fail without changing file hashes.
Its documented output policy is honest: each artifact or artifact/sidecar pair
commits separately, and a failure can leave completed outputs in the new
directory. Neither the guide nor the checker claims a transaction over all
four solves and every generated file.

## Guide and scientific claims

The current guide's four-solve positional command matches the recipe parser.
Its wider-window two-pair example explicitly selects both identities; subsequent
sidecar-only commands select a zero-based figure index or export all CSV rows.
The Python and CLI computation blocks are equivalent alternatives, not commands
to run sequentially against the same protected filenames. Existing-output
protection and explicit overwrite are documented.

The scientific descriptions retain the necessary distinctions: continuous
comparison norms versus canonical discrete normalization; material-sided
piecewise-linear curves; one whole-domain sign; direct residual integration;
near-zero +1 alignment; signed reference-denominator frequency changes; and
same canonical model rather than general physical equivalence. The analytic
sphere frequency reference is separate from agreement and refinement. No
arbitrary-input quality promotion, PREM shape-accuracy claim, hidden pairing,
or new solver capability was found in the inspected text.

Package version 0.3.0 is internally prepared, but the guide's installation
instruction must be evaluated as the forthcoming release journey until root
actually publishes it. No PyPI availability is implied or checked here.

## Frozen evidence required to close audit 3

Root should provide the accepted post-layout source commit, clean declared
distribution inputs, final checker identity, and wheel/sdist SHA256 values.
Review the exact runtime/resource, recipe and guide byte comparisons; both
isolated installation reports; copied-recipe readback and protected retry;
and the retained output/sidecar identities. Inspect representative final
agreement PNG and native SVG rendering from the frozen producer, using audit 2's
repaired layout evidence rather than repeating its entire matrix.

If retained audit documentation is included in a final evidence-only rebuild,
compare unchanged runtime/recipe/guide bytes and repeat the final installation
identity checks as WORKFLOW specifies. Do not rerun the 12-solve science matrix
for renderer or review-text changes. Hosted CI/Python-version compatibility and
actual tagged publication remain distinct evidence supplied by root, not
assumptions inferred from these preparation notes.

## Frozen candidate inspection

Independently inspected candidate input
`4e1d79ad9eb7d80c7da9051c29de3a513e6d0fc0` with a clean primary worktree.
Both archives under `dist/phase3-candidate` contain 41 runtime/resource files
matching the frozen source. All 222 tracked files represented in the sdist
match that commit; the three public schema symlinks are correctly represented
by their committed target contents. Generated packaging metadata is distinguished
from tracked source. The package version is 0.3.0 and SPDX is GPL-3.0-only;
live coordination, website, local artifacts and environments remain excluded.

| Candidate | Bytes | SHA-256 |
| --- | ---: | --- |
| Wheel | 678773 | `300597241cf21cbf1c50a059e4cf4ad735eab722aaf12412817ddcd8695511c0` |
| Sdist | 4854565 | `f376f50e42da7fce85ad5040fe0f8f65effb3384a0146ef136e2446e55ff8b90` |

Frozen checker SHA-256 is
`1c0ed80c6ba415f47ada89757e22a60041fc1e7b567b4be0e08d26be0e5956a8`;
recipe is `d1da357ec409ed5d19b6fbc6742ca8291d19908d2eba2ed9911aafa5b9e89e9b`;
guide is `beffe976a8255c270f6af5a0d1cd27ea9266dba240ec4f2f3acaf42a995f5985`.
Each was compared to the actual frozen Git blob, not just its working filename.

Audit 2's independent repair closure identifies exporter
`47ddbb87b3318b08a5999da24c349f8f9c88f398a05ac640e2074efca5be12f8`,
which is exactly the frozen packaged renderer. This review checked all six
repair input identities and 24 PNG/SVG/sidecar hashes against that closure
record and independently viewed the repaired 800×480 native-SVG raster. Both
scientific notices, the residual direction and the accuracy caption remain
legible. No rerender or numerical rerun was needed.

These candidate identities are not the eventual evidence-only public archive
identities. Root will use the actual hosted final-source CI/build/install and
downloaded tagged release checks for that boundary, avoiding a redundant local
rebuild solely for review prose. At this checkpoint the existing root-owned
isolated-install process is still running; no installed pass is inferred.

## Candidate installed closure

Root's single existing installation command completed with exit 0. Independently
inspected `artifacts/public-delivery/release-v0.3.0/candidate-install.json`, SHA-256
`7c9f51d3cf80e43d24a3bfed23df4f0f3296e426656e9739220e7e6cb43d1a6e`.
Its two archive hashes agree with the bytes inspected above. The wheel and sdist
use distinct fresh `env-0` and `env-1` Python 3.13.7 installations; each copied
recipe's readback import path is its own installed package path. The recorded
copied script hash matches the frozen recipe. No source-tree or shared-site
installation was substituted.

Both installations passed six fresh example loads, the example CLI, small
custom default/pilot solves, existing exports/GLB readback, two-pair agreement
computation, sidecar-only recovery, tampered-report rejection, and the existing
general comparison workflow. Each copied recipe produced the four expected
reports, validated exact source directions and actual 20/40 sphere counts, and
checked all 15 output identities. Existing-directory retries failed with every
output hash unchanged. The maximum independent sphere frequency error in both
runs is `5.954120280118016e-8`, against the separately stated 0.5% named-case
ceiling. This does not certify arbitrary-model accuracy or promote quality.

The retained installed-wheel figures under
`artifacts/public-delivery/release-v0.3.0/candidate-installed-figures` are linked
by `identity.json` to the candidate wheel and frozen commit. All five retained
file hashes match the combined installation report. Independently viewed the
actual 1200×800 PNG: `d=1.07719e-7`, signed relative frequency change
`3.83079e-9`, sign -1 and the separate residual scale remain readable and
nonzero. Parsed its native SVG to verify vector paths and absence of embedded
raster imagery. Both computation and rendering producers are 0.3.0. Different
full report/SVG hashes between fresh runs are not treated as a failure: timing
provenance and SVG production metadata are not an asserted byte-deterministic
scientific result.

**No candidate release blocker remains.** This closes the third distinct
implementation audit, including both preparation gaps. No duplicated install,
build, test suite, rendering matrix or scientific solve was run by this reviewer.
The final evidence-only documentation commit will change the sdist input;
therefore these candidate hashes must not be presented as the eventual public
release hashes. Root's final hosted CI must build and check the actual final
source, including supported interpreter jobs and isolated package journeys,
then verify the downloaded tagged archives against that source. This candidate
closure does not claim those later external actions have already happened.
