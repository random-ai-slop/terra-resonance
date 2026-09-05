# Workflow planning round 2 — recovery under ambiguous execution and stale inputs

Date: 2026-09-04. Reviewed the selected round-2 proposal in `docs/team/DESIGN.md`: local root Git, preserved independent Site repository, two native worktrees and one coordinator-owned primary CURRENT. No Git/runtime/thread operations were performed.

**Decision: retain the selected architecture, with four small protocol clarifications before deployment.** The proposal says what to inspect, but its ambiguous-attempt and synchronization transitions need enough precision that a resumed coordinator cannot accidentally create a second writer. No scheduler, lock service or additional status database is required.

## 1. Observation times out while the worker is still active

### Counterexample

Task T17 is running in science worktree W1 on accepted base C0. A wait/status operation times out. The coordinator resumes in another context, sees no final answer and dispatches T17 to a new worker. The first worker still has a long-running shell process or delegated child that can write after the replacement starts. Reading “idle” from a conversation alone can miss that process.

### Required transition

- A timeout changes **observation certainty**, not task ownership. Keep the current attempt active and preserve its handle/worktree claim. Query the same handle once; inspect the known command session/child handles if that task delegated or launched a still-running process.
- If it is running, continue waiting with bounded observations or send a status request to that same attempt. Work on nonoverlapping tasks meanwhile. No replacement writer is authorized.
- To interrupt deliberately, address the existing attempt and confirm that its known writers are stopped or have acknowledged quiescence. Do not infer this from elapsed time, a missing reply, an empty `git diff`, or a temporarily unchanged file.
- If liveness remains unavailable, mark the operation **blocked: writer state unknown**. Freeze only its worktree/overlapping integration; keep independent work moving. Do not reuse or reset that checkout. A replacement can begin only after the coordinator has resolved writer ownership, or has explicitly isolated a new checkout and revoked the old attempt's authority to publish/integrate changes.
- Preserve partial work before transfer. Record the replacement attempt and its accepted checkpoint in the same task row; do not create a second task that looks unrelated to T17.

The task needs a small **attempt number** in addition to task ID and actual owner handle. Handoffs identify T17/attempt1 versus T17/attempt2. This is not a distributed fencing implementation: old processes may still modify their own isolated checkout. The coordinator refuses integration from a superseded attempt, and never lets an uncertain old writer share the replacement checkout.

## 2. The worktree is dirty when an upstream contract changes

### Counterexample

The science worker has uncommitted shape-metric changes against C0. Package work changes the accepted comparison contract to C1 while the science task is interrupted. On resume, “synchronize accepted root revision” could be interpreted as reset, pull/rebase onto whatever HEAD exists, or continue under the old contract and claim the result supports C1. All three can lose work or create false evidence.

### Required transition

1. Read primary CURRENT's exact accepted implementation base and contract identity. Compare them with the task's recorded inputs. Do not substitute the coordinator's latest HEAD automatically: it may contain only unrelated docs/ledger updates or unfinished integration.
2. Inspect tracked **and untracked** changes in the task checkout. Record which belong to the task and which are unexpected. Preserve task work with a local WIP commit when its contents are understood, or an explicit patch plus untracked-file copies. Do not automatically commit secrets, unrelated user files or generated environments.
3. Determine the changed contract's effect. If unrelated, the coordinator records that the existing acceptance remains valid; the worker continues without a ceremonial rebase. If it changes the task's metric/units/API or acceptance, pause dependent edits and invalidate the old readiness claim.
4. Coordinator decides the target contract and integration order. Worker updates the **same task** against that explicit target, using a normal merge or a rebase only on its own unpublished branch with preserved work. Never hard-reset/stash-drop to obtain a clean status. Resolve conflicts within the assigned files; overlap with another owner is an ownership amendment, not unilateral conflict repair.
5. Rerun only checks invalidated by the actual contract/code change. The new handoff names the new input revision and output commit. Evidence from C0 remains historical and must not silently be relabeled as evidence for C1.

“Dirty” is a state to inspect, not a reason to abandon a task or discard it. A worker may continue unaffected research/docs while a dependent API decision is blocked. If the contract change invalidates the scientific question itself, cancel or revise the existing task with an explicit reason; creating a new task must not hide the incomplete predecessor.

## 3. Redispatch or duplicated delivery produces duplicate ownership

### Counterexample

A send-message response is uncertain, so the coordinator retries. Two identical start messages arrive; alternatively a resumed coordinator issues a changed request using the old task ID to another handle. Without an attempt identity and acknowledgment rule, “one task has one active attempt” remains an aspiration.

### Required transition

- Primary CURRENT contains one active tuple: **task ID, attempt, owner handle, worktree path, accepted input revision, allowed files**. Coordinator records it before dispatch. It is the only authority for that operation.
- Dispatch and every handoff include that tuple's task/attempt identity. The receiver acknowledges matching primary state **before new writes**. An identical repeated message resumes/observes the existing operation; it does not create another branch, child worker or execution loop.
- A mismatch of owner/attempt/input revision means stop new writes and report the mismatch. Do not “fix” primary CURRENT from a specialist checkout or assume the newer chat message overrides an accepted contract without the coordinator updating the record.
- A deliberate transfer increments attempt only after inventorying the predecessor and recording its stopped/revoked status. Retain its output/WIP commit as recovery material. The new attempt starts from a named checkpoint, not an unspecified dirty directory.
- Coordinator checks task/attempt and allowed changed paths before integrating. A late answer from a superseded attempt is read as possible evidence, never automatically cherry-picked. Concurrent new review messages are harmless if read-only; duplicate implementation claims are not.

An acknowledgment is a technical handoff, not another user-permission request. Two sides do not each keep editable task ledgers. A single primary writer avoids most race conditions; the tuple makes manual resumption auditable.

## 4. Worktree isolation creates a new Site and state-copy hazard

Root Git deliberately ignores `apps/web`, preserving the existing separate Site checkout. A native scientific worktree therefore does **not** contain that Site working tree. The existing default `scripts/sync_web_assets.py` writes all destinations and creates missing directories; running it in the specialist worktree can create a shadow `apps/web/public/data` instead of updating the actual Site. Git's ignored-path policy then hides those writes from the ordinary changed-file handoff.

The same problem applies to a tracked worktree copy of CURRENT: it may look official but is stale. Git isolation does not identify the correct operational authority.

Minimal clarification:

- Dispatch supplies absolute **primary root, primary CURRENT, specialist worktree and actual Site root**. The root router names which is authoritative; it does not rely on the current working directory. A copied CURRENT is explicitly nonauthoritative.
- Specialists run scientific/package checks and package-only synchronization in their own checkout. They do not run default/all/web destination writes there. The existing `--target package` is sufficient; no new runtime mechanism is needed.
- After integration, the coordinator performs website synchronization and tests in the actual primary Site checkout. Record its commit separately from the scientific integration commit. Never claim a root worktree contains or checkpoints the ignored Site.
- Inspect unexpected/untracked/ignored output destinations before handoff where a task used generators; a clean ordinary diff does not prove that no shadow Site was created. Remove only confirmed task-generated shadows after preserving relevant evidence, not arbitrary ignored directories.
- Keep the accepted code/contract commit distinct from CURRENT's current coordination text. Committing a ledger update alone must not invalidate every task or force a rebase. Root source checkpoints and Site checkpoints remain different identities.

This directly preserves the successful phase-2 single-source/separate-destination workflow in the new worktree layout.

## Minimal changes to the selected proposal

Keep local scientific Git, preserved Site, two worktrees and one primary CURRENT. Add only:

1. Task-attempt identity and a precise unknown-liveness/revocation rule, including known child/process writers.
2. Dirty/stale-contract preservation and targeted synchronization steps; separate accepted implementation base from incidental coordinator HEAD.
3. Idempotent redispatch acknowledgment and stale-handoff rejection against primary CURRENT.
4. Absolute environment paths and package-only specialist synchronization, with the coordinator operating the real Site after integration.

Do not add periodic claim expiry, automatic resets/rebases, a duplicate JSON ledger, heartbeat-driven polling or a permanent recovery agent. Time alone must not release ownership. No worker should need to reconstruct these transitions from old chat messages.

## Cold-start test for round 3

Give a reviewer only a sample CURRENT record, the router, the linked accepted contract and worktree status snapshots. Require four correct choices:

- Timed-out but active attempt: retain ownership; no duplicate writer.
- Dirty task plus materially changed contract: preserve work, pause dependent changes, select the explicit target, then rerun affected checks.
- Duplicate dispatch/late predecessor handoff: same attempt resumes idempotently; stale attempt cannot integrate.
- Missing Site under a scientific worktree: package-only operations there; website synchronization at the real primary Site.

Success is a concrete stop/continue/synchronize decision with the right files preserved. A prose promise to “be careful” or another status board is not sufficient. After these cases close, deploy and exercise the workflow instead of expanding recovery theory indefinitely.
