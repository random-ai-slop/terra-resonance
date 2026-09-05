# Agreement audit 3: frozen distribution and installed usability

Assignment AUDIT-RELEASE/1. Preparation reviewed primary `e9e660e5`, PHASE-3
revision 3, AGENTS/WORKFLOW/primary CURRENT, `scripts/check_distribution.py`,
`pyproject.toml`, MANIFEST, the agreement guide and copied recipe. Only this
review file is owned by the reviewer. No build, install, numerical rerun, source
change, or external publication was performed during preparation.

**Status: preparation complete; installed acceptance pending.** The package
author is repairing the two renderer-only findings from audit 2. Root must
supply the accepted frozen input and actual archive/install evidence before
this audit can close. Earlier source tests and 0.2.1 release evidence do not
establish 0.3.0 installed acceptance.

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
