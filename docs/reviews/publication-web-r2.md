# Public website implementation review, round 2

PUB-WEB-R2/1, 2026-09-04. Read-only review of implemented `build-pages.mjs`, Next/Vite configuration, Workbench asset URLs, and Pages/CI workflows. No Site files, builds, browser sessions, external state or child tasks were changed by this reviewer. The user renamed the repository during review: the final target is `/terra-resonance/`; the initial inspected code still used `/free-oscillation/` and the coordinator is updating that configuration and its links.

## Blocking finding: a stale completion can cancel the current pending deployment

**P1 — Workflow-level concurrency currently permits one pending run.** `cancel-in-progress: false` preserves the running deployment but does not preserve every pending workflow. The stale-SHA guard runs only after a Pages workflow obtains its concurrency slot.

Concrete sequence:

1. Pages A is running, for example waiting for its deployment job/environment.
2. Successful CI for the latest main commit B starts Pages B, which waits in the pending slot.
3. A previously successful push workflow C for an older commit is rerun and completes late. Pages C enters the same group and cancels/replaces pending B.
4. A finishes; C acquires the slot, correctly detects that its SHA is old and skips. B has already been canceled, so the latest tested site is never deployed without another trigger.

The existing head comparison prevents an old late run from overwriting the new site; it does not prevent the old run from displacing a pending new run before that comparison.

Minimum correction supported by current GitHub documentation: retain serialization and `cancel-in-progress: false`, add `queue: max`, and retain the current-head check after acquiring the workflow slot. This prevents ordinary out-of-order completions from canceling the latest pending workflow. The documented queue is bounded at 100; do not describe it as an unbounded delivery guarantee. [GitHub concurrency documentation](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)

Acceptance: inspect the amended queue policy and walk the sequence above; both B and C remain queued, and whichever is evaluated as stale skips without canceling the other. The first real Actions deployment still needs to confirm platform workflow acceptance and the public URL. This report records the finding before the coordinator's repair; no repaired remote run is claimed here.

## Paths and build staging: the implemented design addresses the earlier failures

- All four scientific data requests—two initial resources, lesson reload and default PREM restoration—use `assetUrl`. The helper strips leading slashes and prefixes the build-time public base. This fixes origin-root `/data` requests while leaving imported files and Blob downloads unchanged.
- Next configuration is the base-path authority and supplies the same value through `NEXT_PUBLIC_BASE_PATH`; trailingSlash is enabled. The Pages builder validates the path and supplies it consistently to the child build. The final rename must update the default, workflow assertion and documentation together to `/terra-resonance`.
- The Pages Vite branch returns before importing Cloudflare, Sites or hosting JSON. The default branch retains the existing Sites integration. A same-code root-path build remains available.
- `build-pages.mjs` removes prior dist output before invoking vinext and exits if the build fails. It selects the physical `dist/client/<base>` subtree, copies that subtree to `dist/pages`, verifies entry/data files and checks absolute HTML asset URLs against both the base and staged files. This avoids double nesting and stale successful output after a failed build.
- The source/base/version manifest is generated in the staged artifact. In CI, GITHUB_SHA identifies the commit whose code and checks produced that artifact. Local builds truthfully record a null SHA when the environment does not supply one.

The coordinator reported successful Pages and Sites builds plus 25 tests, type checking and lint. This source review did not repeat those builds. The current CI verifies HTML-linked resources and compilation; it is not an HTTP/browser exercise of lazy requests, locale behavior or downloads. Those remain the explicitly assigned live integration checks, rather than evidence inferred from a green build.

## Event trust and exact source artifact

The Pages prepare job requires successful CI, originating event `push`, branch `main` and the same head repository. A pull-request workflow—even one named CI and successful—cannot satisfy those conditions. The current-main API lookup then compares its SHA with `workflow_run.head_sha`.

Artifact download names `pages-static` from the exact triggering run ID using the current repository token. The downloaded `deployment.json` must match the triggering source SHA and intended deployment base, and required staged files must exist. The workflow does not check out and execute code from a pull-request artifact, and the privileged deploy job does not rebuild from whatever main contains later.

The CI upload occurs after tests, type checks, lint and the Pages build. The subsequent Pages workflow is triggered only when the complete CI workflow succeeds, including Python jobs. Therefore it reuses the output from that accepted CI run, rather than building a second untested website during deployment. A new source commit while an already accepted deployment is running can temporarily leave the prior accepted revision live; that is different from stale-run overwrite or silently deploying new untested bytes.

## Hidden marker and artifact wording

`include-hidden-files: true` correctly preserves `.nojekyll` in the first `pages-static` artifact, so the prepare-job staging assertion can pass. However the pinned `actions/upload-pages-artifact` implementation subsequently excludes dotfiles while creating its tar, including `.nojekyll`. Its source contains that exclusion explicitly. [Pinned upload-pages-artifact implementation](https://raw.githubusercontent.com/actions/upload-pages-artifact/7b1f4a764d45c48632c6b24a0339c27f5614fb0b/action.yml)

This is **not a runtime blocker**: the custom Actions path deploys an already-built static artifact, rather than asking Jekyll to process a source branch. `_next` begins with an underscore, not a dot, so its assets are not affected by this exclusion. The marker can remain a staging invariant. Describe reuse as the same tested website assets and manifest, not literal byte identity of every wrapper/hidden marker after packaging. There is no need to replace the official Pages upload action solely to preserve an unnecessary marker.

## Final acceptance conditions

1. Repair the pending-run race and verify the renamed base consistently in builder, workflow assertion and published links.
2. Run CI/Pages on the final public source; retain the originating run ID, head SHA and final deployment URL.
3. Read the deployed `deployment.json` and verify source/base/version; load the default data, switch lessons and restore PREM from the actual `/terra-resonance/` URL.
4. Confirm locale switching preserves the path/state and a downloaded scientific artifact contains its English labels and provenance.
5. Preserve root-path Sites behavior. A Pages publish is not evidence that the separate Sites destination was updated, or vice versa.

No other code-level blocker was found in the reviewed path/artifact/event boundaries. The queue repair is narrow and should precede publication; no new deployment framework is warranted.

## Coordinator disposition

The pending-run race is repaired with `queue: max`, retaining `cancel-in-progress: false` and the current-main guard. This setting was verified against current official GitHub concurrency documentation. The final `/terra-resonance` build succeeded after the user rename, including prefixed emitted assets and required data. Sites root-path build and web25 tests/type/lint also passed during this change. Actual hosted CI, public HTTP checks and package publication remain separate gates, recorded in the delivery evidence.
