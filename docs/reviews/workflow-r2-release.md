# Workflow review, round 2: frozen inputs and worktree integration

Reviewer: scope_review. Scope: the selected round-2 proposal in [DESIGN.md](../team/DESIGN.md). This adds conclusions from three concrete handoff walkthroughs; it does not repeat round 1 or change Git/runtime state.

**Verdict:** support local scientific Git and isolated specialist worktrees, with the small operational clarifications below before use. Git supplies recoverable changes and accepted revision identities. It does not make a copied CURRENT authoritative, synchronize the separate Site repository, or prove generated artifacts are fresh.

## 1. Documentation changes after distribution freeze

Walkthrough: the coordinator freezes source F, builds and tests a candidate, then a reviewer edits a retained report. `MANIFEST.in` includes `docs/*.md`, JSON, text and SVG recursively. The source distribution no longer matches the current maintained distribution inputs even if the wheel's runtime is unchanged.

The proposed documentation-only rebuild is correct, but the decision must use the **actual diff and affected claim**, not a filename extension:

- Evidence/status prose changes: incorporate the final report, create F2, rebuild the source archive and final wheel as appropriate, compare installed runtime/resources, and repeat import/install checks. Preserve the already valid numerical/media evidence.
- A documented command, unit, normalization, metric or contract changes: review that claim and rerun its affected command/invariant. A `.md` suffix does not establish semantic irrelevance.
- An unrelated live coordination status changes: it should not invalidate distribution inputs at all.

The last case needs an explicit decision now. If CURRENT is placed under `docs/team/`, the present MANIFEST automatically distributes it. That would put stale task handles/status into the package and make ordinary coordination updates invalidate the source archive. Keep `docs/team/CURRENT.md` tracked for recovery but explicitly exclude it from the archive in MANIFEST. I support excluding pure operational handoffs as well, provided they occupy explicitly named files or a dedicated operational directory; do not use a broad filename-pattern exclusion that could remove scientific evidence. Those handoffs contain handles, absolute worktree paths and next-action routing, and should link substantive results into the retained review/validation records. Static WORKFLOW/DESIGN documents and substantive audit reports remain distributable. If a dedicated `docs/team/handoffs/` directory is actually adopted, `prune docs/team/handoffs` plus `exclude docs/team/CURRENT.md` is sufficient. Do not create that directory solely to justify another mechanism. No generic manifest service is needed.

The freeze should name the accepted commit and **distribution input scope**. The final check compares that scope with the built/installed files. A later CURRENT-only commit does not require pretending the runtime changed; a changed retained scientific report cannot be dismissed as merely a ledger update. This directly resolves the phase-2 archive mismatch without freezing the coordinator's ability to report progress.

## 2. Renderer changes while the catalog hash stays constant

Walkthrough: the saved catalog, bundle and ExportSpec are identical, but `export_render.py` changes depth ordering or text layout. `scripts/sync_web_assets.py --check` can still pass: it hashes the five JSON sources and two package copies, not the renderer or preview PNGs. This is exactly the class of phase-2 change that required new images despite an unchanged scientific catalog.

Add one explicit dependency to the handoff: a rendered artifact is evidence for its **Scene/production inputs plus renderer/assets/environment**, not for a catalog hash alone. In the work note or existing release report, name the source revision used for rendering and the relevant artifact paths/hashes. Existing manifests already record production and library versions; there is no need to change their schema solely for this workflow.

For this case, invalidate the affected preview/PNG evidence, run the narrow visibility/layout counterexample, regenerate the owned previews, and inspect the actual outputs. Leave unchanged scientific frequency/shape evidence valid. If a shared rendering path changes, inspect at least one affected encoded frame; a pure encoder change instead requires actual decoding/timing checks. Record the reason for reuse or rerun. Neither “JSON copies identical” nor “same package version” is enough to claim fresh rendered evidence.

The proposed freeze wording should therefore say **generated artifacts checked against their producing inputs**, not merely “resource hashes pass.” An adversarial dry run can leave the catalog untouched while changing a renderer parameter: a correct handoff must identify the old preview as stale even though JSON sync succeeds.

## 3. Child-worktree handoff and root integration

The selected Git plan is preferable to directory-copy integration, provided the following procedure is explicit:

1. Dispatch names the primary root path, the absolute primary CURRENT path, accepted base commit B, relevant contract/API identity, task ID and allowed changed paths. A specialist's checkout contains a historical CURRENT snapshot; its first line/router must say where the primary record is located and that the copy grants no current assignment or write permission.
2. The specialist inspects its actual branch/status, preserves unrelated unfinished work and starts from B. It returns completed task commit(s) H, the changed-path list, commands/results, executable artifacts and limitations. Required source/resource changes must be committed; ignored temporary outputs may be handed off separately with paths/hashes. “Clean worktree” alone does not prove ignored deliverables were included.
3. The coordinator checks the named commits and their ancestry/diff, rather than copying the child directory or trusting CURRENT's `done` label. Useful checks are `git log B..H`, `git diff --name-status B H`, the child's actual status and the expected artifact files. Reject out-of-scope changes or an unrecorded input dependency before integration.
4. Compare the current root's changes since B in the task's relevant inputs. If a numerical API/contract changed, technical reacceptance is required even when Git predicts a clean merge. If only unrelated documentation changed, do not force a numerical rerun merely because HEAD differs.
5. Integrate the explicit task commits by the coordinator's chosen normal Git operation; record the resulting root revision I. Run the focused integration check on I. Commit H's successful tests are evidence for H, not automatic proof of the combined tree I. Consumers receive I as their accepted input before dependent writes. A conflict returns to the same task/attempt and ownership, not a duplicate assignment.

These steps do not require a lock server or checker. They require precise messages and ordinary diffs. Do not require a worker to rebase automatically over dirty work, reset a checkout, or infer acceptance from elapsed time. A timeout means inspect the existing handle and changes, as the proposal already states.

### Concrete boundary exposed by the separate Site repository

Ignoring `apps/web` at the scientific root is sound: preserve its own history, avoid a gitlink and record its independent commit/status when relevant. However, scientific worktrees will not contain that nested checkout. The current sync script computes its web destination relative to its own ROOT and creates missing directories. Running its default write mode in a specialist worktree would create a **different ignored `apps/web/public/data` tree**, not update the real Site. Running default `--check` there fails for missing Site resources.

Make the executable routing unambiguous: package specialists use `--target package` in their own worktree. The coordinator performs `--target web` or `--target all` only from the primary scientific root containing the actual Site checkout. Website checks/builds use that actual Site root and identity. Do not solve this by silently copying or symlinking the Site checkout into every worktree.

The baseline inventory also needs two explicit distinctions: ignore `.codex/`, `.agents/`, credentials and environment/cache files, but **track the intended root AGENTS.md router**; exclude disposable outputs, but retain package-required generated data, maintained examples and independent evidence. Otherwise fresh worktrees can appear clean while missing their instructions or installed resources. This is a staged-inventory review item, not a reason for a broad new ignore convention.

## Minimum amendments and readiness

Before round-3 cold start, add only:

- The precise CURRENT location, its primary-versus-snapshot rule and exclusion from distribution if needed.
- The five-step commit handoff above, including checks on root integration I and semantic input drift.
- Explicit package-only sync in child worktrees and coordinator-only sync to the real Site.
- Distribution freeze/revalidation based on changed input scope; rendered-artifact identity includes its producer, not just catalog JSON.
- An inventory rule retaining AGENTS, required generated resources and scientific evidence while excluding private/disposable state.

The cross-solver report remains a suitable trial. Its numerical output should be integrated and named before the package task consumes it; independent drafting against an agreed interface may proceed meanwhile. CURRENT links that accepted revision and evidence but never substitutes for reading the actual source or verifying the running task. With these amendments, there is no release/worktree reason to add another board, permanent reviewer, automatic scheduler or repeated global validation round.
