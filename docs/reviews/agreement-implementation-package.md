# Package agreement implementation handoff

Task/attempt: PKG-IMPLEMENT/1. Owner: Terra package and production, native task
`01a06fdf-dc87-7ca3-be17-1a6fab217fae`. Accepted implementation input B/I:
`4aa90d93bbce43ac4b22b8b65b648434c56dbbd2`, including numerical H
`fd753c8c6785c406b0329a0a3ee0bb8dd6c054ec`, source/package 0.3.0 and PHASE-3
revision 3. Output H is the containing scoped implementation commit returned
in the native handoff.

## Scope and actual receiving-domain continuation

Read the actual primary CURRENT, WORKFLOW v1.2, PHASE-3 revisions 2/3 and the
numerical implementation handoff before edits. The native checkout
`/Users/veritaswang/.codex/worktrees/6eaa/free-oscillation` was clean and detached
at the archival bootstrap. It switched directly to the accepted public I; no
archival history was merged. Linked Git metadata required an authorized sandbox
escalation. The primary runtime import was explicitly overridden and verified:

```sh
env PYTHONPATH=/Users/veritaswang/.codex/worktrees/6eaa/free-oscillation/packages OPENBLAS_NUM_THREADS=1 /Users/veritaswang/Desktop/code/random-ai-slop/free-oscillation/.venv/bin/python -c 'import earth_modes; print(earth_modes.__file__)'
```

Observed import was this worktree's `packages/earth_modes/__init__.py`.
The current record plus linked accepted design and numerical handoff supplied
the source/API, limits and next consumer work without reconstruction of earlier
scientific chat. `_checked_evaluation(report)` now drives actual checked CSV
and figure output, and received sidecars successfully drive new exports. This
is useful receiving-domain continuation evidence; coordinator acceptance of W4
remains separate from this author's observation.

Changed paths are exactly:

- `packages/earth_modes/agreement_export.py`
- `packages/earth_modes/cli.py`
- `tests/test_agreement_export.py`
- `examples/recipes/agreement.py`
- `examples/recipes/README.md`
- `docs/AGREEMENT.md`
- `docs/reviews/agreement-implementation-package.md`

## Implemented behavior

The lazy `earth_modes.agreement.export_agreement` facade now emits checked JSON,
all-row CSV, native SVG and PNG. It performs one fully checked evaluation per
export. CSV/figure values come from recomputation; original checked report values,
unknown metadata, full sources and historical generator remain intact in JSON
and sidecars. `export_production` records the current renderer/version, English
annotation locale, format and resolved figure options. Full sidecar serialization
is bounded before any output publication. JSON has one file, no redundant sidecar.

Two axes show comparison-normalized W and `reference − aligned candidate` with
separate residual scaling. All material union points are retained; boundaries
are dotted and disconnected material paths are not joined. Small nonzero metrics
use adaptive notation. Exact-zero residuals have finite limits and a zero label.
Minimum/default figures show index/n/l, methods, frequencies, signed relative
change, distance, global sign, applicable mismatch/indeterminate notices and an
agreement-not-accuracy caption. Full source/mesh/quality details remain in the
sidecar. User method/model text is display-shortened without math parsing or
changes to scientific metadata.

The thin CLI enforces the two exclusive input routes, repeated explicit pairs,
bounded strict bundle reads, zero-based figure selection and applicability of
dimensions/index. Bundles are not implicitly extracted from Projects. Existing
general comparison behavior is unchanged. Controlled artifact/sidecar failure
restores the old pair; ordinary no-clobber and surviving-sidecar protection apply.

## Executed checks and observed outputs

Commands below ran from this worktree with:

```sh
export PYTHONPATH=/Users/veritaswang/.codex/worktrees/6eaa/free-oscillation/packages
export OPENBLAS_NUM_THREADS=1
export MPLCONFIGDIR=/tmp/terra-pkg-mpl
```

Interpreter throughout:
`/Users/veritaswang/Desktop/code/random-ai-slop/free-oscillation/.venv/bin/python`.

1. `python -m pytest -q tests/test_agreement_export.py tests/test_cli.py`:
   **29 passed in 112.17 s**. Two existing GLB omission/color warnings are expected.
   This includes the unchanged general CLI comparison journey.
2. After minimum-layout and literal-user-text repairs,
   `python -m pytest -q tests/test_agreement_export.py tests/test_agreement.py`:
   **92 passed in 13.41 s**.
3. After the coordinator's residual-direction caption finding,
   `python -m pytest -q tests/test_agreement_export.py`:
   **22 passed in 9.11 s**. This final annotation-only edit did not trigger another
   numerical matrix or full CLI suite.
4. `git diff --check`: exit 0.

Failure checks include prohibited format/options, Boolean/fractional dimensions
and indices, missing multi-pair selection, altered stored metrics, sidecar size
overflow, mixed/partial CLI routes, Project input, existing artifact/sidecar,
injected staged rendering failure and injected overwrite-sidecar commit failure.
The rollback checks compare actual old artifact/sidecar bytes. A fresh CLI
subprocess reloads a received sidecar after both source files and the original
figure have been removed. CSV numeric readback matches recomputed rows including
a tiny nonzero frequency change; original tolerated report metric variations are
preserved in sidecars. PNGs decode at 1200×800 and 640×480. Parsed SVG contains
native paths and no embedded image.

The copied recipe ran as:

```sh
cp examples/recipes/agreement.py /tmp/terra-pkg-implementation/agreement.py
python /tmp/terra-pkg-implementation/agreement.py /tmp/terra-pkg-implementation/recipe-final
```

It completed four solves and independently computed the l=2 spherical-Bessel
traction reference. Maximum relative frequency error across the four solves was
`5.954120280118016e-8`, below the named 0.005 ceiling. This is a frequency check,
not evidence for all eigenfunctions or a quality promotion. The copied script
uses package/SciPy imports and standard library only; this execution explicitly
binds source packages and is **not** isolated wheel/sdist installation evidence.

The recipe creates 15 files in a new directory:

- Four bundles: `default-20.json`, `default-40.json`, `pilot-20.json`, `pilot-40.json`.
- Four reports: `cross-20.json`, `cross-40.json`, `refinement-default.json`,
  `refinement-pilot.json`.
- Three artifacts and three full-report sidecars: `cross-40.csv`, `cross-40.svg`,
  `cross-40.png` and each path plus `.json`.
- Separate `independent-frequency.json` with Bessel equation/root/frequency,
  four checked errors, ceiling and output policy.

All four reports and three sidecars reloaded. CSV values matched the report and
the final PNG decoded. Reusing the existing directory in a subprocess returned
nonzero with FileExistsError; all 15 file hashes remained unchanged. The final
frequency-evidence file is also staged and exclusively committed. The directory
is not a batch transaction; completed files remain after later failure.

The documented wider-window two-pair example also executed (two small degree-2
solves, window up to 0.006 Hz, mesh target 40). Its selected pair-1 sidecar
regenerated both CSV rows without needing original files. No full scientific
matrix was duplicated.

## Visual inspection and retained local evidence

Actual inspected outputs under `/tmp/terra-pkg-implementation`:

- `recipe-final/cross-40.png`: final 1200×800 sphere figure, including signed
  relative change `+3.8308e-9`, distance `1.07719e-7` and explicit residual direction.
- `minimum-final.svg` / `minimum-final-vector.png`: final 640×480 sphere figure.
- `notices-final.svg` / `notices-final-vector.png`: 640×480 material-interface
  fixture showing different n labels and indeterminate sign notices together.
- `zero.png`: exact-zero finite-axis inspection before the final direction label.
- `two-pair.svg.json` / `received-all.csv`: full two-pair receiving journey.
- `verification.json`: recipe file hashes, producing runtime/recipe source hashes,
  independent frequency evidence and existing-directory preservation result.

The SVGs were independently rasterized and visually inspected with:

```sh
/usr/local/bin/rsvg-convert -w 640 -h 480 /tmp/terra-pkg-implementation/minimum-final.svg -o /tmp/terra-pkg-implementation/minimum-final-vector.png
/usr/local/bin/rsvg-convert -w 640 -h 480 /tmp/terra-pkg-implementation/notices-final.svg -o /tmp/terra-pkg-implementation/notices-final-vector.png
```

Initial minimum-size inspection prompted extra space between the radius label
and footer. Root's pre-integration review found the missing explicit residual
direction; the caption was added and both minimum figures plus default PNG were
inspected again. Final SVG/PNG outputs were regenerated from unchanged reports,
without re-solving for the annotation change. The four-solve recipe was repeated
once during development to verify its final staged independent-evidence write;
this was a changed recipe input, not an unrelated broad rerun.

## Limits and next consumer

No numerical runtime, solver, schema, quality, primary CURRENT, website,
dependency environment, global settings or publication state was changed. No
children or background writers were created. Source and report resource bounds
remain rejection limits, not peak-memory promises. Transactions do not promise
power-loss safety or atomicity across multiple exports.

Root owns integration, independent package/artifact audit (including real PREM),
the distribution checker, frozen wheel/sdist installs and release acceptance.
Use `python agreement.py OUTPUT_DIR` from a copied recipe in each isolated
installation; preserve the above filenames and test new-directory refusal.
The author's passing self-checks do not close those independent audits. After
the scoped commit and native handoff, this domain becomes idle.
