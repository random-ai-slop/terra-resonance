# Workflow planning round 1 — durable coordination without a management platform

Date: 2026-09-04. Architecture brainstorming against DEVELOPMENT and the completed phase-2 planning/implementation/release reports. No threads were created; no runtime, Site, source or release settings changed. This is a proposal for subsequent adversarial refinement, not a claim that the workflow already exists.

## Recommendation

Use one coordinating conversation plus **two durable domain conversations when a new phase contains sustained parallel domain work**, with temporary bounded subagents for independent investigation and review. Keep a zero-domain-thread mode for small maintenance tasks. Do not add a third permanent domain by default. A durable conversation preserves context; it is neither a file lock nor the source of project truth.

Two domains should be broad enough to own complete work:

- **Science and data:** default/experimental numerics, material/field conventions, scientific validators and reference evidence. It owns the physical meaning of interfaces.
- **Experience and delivery:** website presentation, offline/browser output, CLI/package user journeys, installed examples and delivery documentation. It owns preserving those meanings through actual user outputs.

The coordinator owns accepted scope, cross-domain decisions, current claims and integration/release status. Exact file ownership is assigned per task, not inferred forever from a domain name. In particular, data/schema changes need both viewpoints, while CLI must still have one writer. Site operations have one explicitly assigned owner. A temporary reviewer can inspect either domain without acquiring write ownership.

## Why the existing evidence points here

| Phase-2 event | What failed or worked | Workflow consequence |
| --- | --- | --- |
| Python filled sections overpainted the foreground; 82,994 pixels differed in the far-cut counterexample | Field/schema/unit tests passed, but cross-output appearance was wrong | Keep independent output review and an actual artifact; a permanent graphics thread alone would not prove correctness |
| CLI counted273,078 points even after explicit GLB omissions, while API needed57,910 | Two layers independently interpreted the same production decision | Assign one implementation owner for the shared policy and require CLI/API closure; do not split API and CLI between autonomous domain rules |
| Chinese-chart download selected a chevron SVG instead of the plot | Correct numerical paths and a valid SVG were insufficient | Preserve real user download/decode evidence; a test-count dashboard cannot replace the final artifact |
| The last review log stayed Chinese despite broad translation work | Historical-document ownership existed, but completion still needed an end-to-end audit | One finite owned-file list plus one final scan is useful; a permanent documentation department is not |
| Chinese lesson text had to be captured before English source regeneration | Producer/consumer mutations had a real sequence dependency | Record an explicit readiness handoff before running a generator that replaces canonical content |
| Package and website copies stayed synchronized through one command with seven hash checks | Canonical source and generated destinations were distinguished | Keep generated copies single-source; website owner executes the destination mutation when another owner controls the generator |
| Pilot review independently reran all19 rows without replacing submitted evidence | Bounded independent verification produced strong evidence in about2s | Temporary specialist reviewers are appropriate; do not make every review a new permanent workstream |
| Installed release found annotation overlap after ordinary image decode passed | Actual isolated installation and image inspection added information | Release is an integration checkpoint, not an inference from editable tests or each domain saying done |

These are concrete process lessons, not proof that more conversations improve results. Phase2 succeeded with one lead and bounded agents; its defects primarily arose at interfaces and interpretation, not from missing organizational titles.

## Compare zero, two and three durable domains

The coordinator is additional to the domain count below. Permanent conversations need not run continuously.

| Organization | Suitable work | Advantages | Costs and risks | Decision |
| --- | --- | --- | --- | --- |
| **0 durable domains + temporary agents** | One-file fixes, release patches, a small bounded phase | Lowest coordination cost; one current context; straightforward ownership | Repeated large-phase restarts re-read scientific and product history; lead accumulates too much detailed context | Retain as maintenance/default fallback; not inadequate merely because fewer conversations exist |
| **2 durable domains + temporary agents** | Continuing numerical development alongside user/output work | Retains both deep contexts; only one main science↔delivery interface; temporary reviewers change viewpoint | Broad delivery domain can bottleneck; schemas and shared files still need explicit claims | Recommended for sustained next-phase work, subject to a real trial |
| **3 durable domains + temporary agents** | Three independently sustained backlogs: numerics, scientific data/production, website/product | More specialized retained context; potential parallel work when three seams are stable | Data/production becomes a bridge owning nearly every shared contract; more handoffs, stale statuses and idle “departments”; risk of self-review by specialty | Add only after measured repeated contention; not justified solely by three agent slots or three research reports |

A plausible three-domain alternative is numerics / scientific data-and-production / website-and-product. It must not turn the middle domain into an obligatory approval queue for every change. Adding a domain is justified when it has both recurring independent tasks and a clear durable knowledge burden, and the existing domain repeatedly waits on unrelated work. No calendar-only or thread-count target is proposed.

## One current state record, several kinds of evidence

Maintain **one small root-owned current-work file**, for example `docs/workflow/CURRENT.md`. It points to authoritative artifacts instead of copying their contents. It contains:

1. Active objective, accepted scope revision and the next integration milestone.
2. A bounded table of active task IDs: owner conversation, exact allowed files, status, dependency/next action, checkpoint identity, evidence link and reviewer/disposition.
3. Explicit unresolved interface decisions or blockers, plus the last integration result and next required check.

Do not duplicate the live table in separate domain boards, a machine JSON ledger and a hand-written dashboard. If automation later needs a machine representation, make it the single source and generate the human view. Historical reports remain immutable findings/dispositions; they are not the current queue. ModelBundle provenance is scientific truth, accepted CONTRACT is interface truth, actual files are implementation truth, and the current-work file is coordination truth. A conversation summary is an index into them, not a competing source.

Domain conversations can keep a brief durable handoff note **only when idle/interrupted or transferring work**, linked from CURRENT. Avoid permanent per-message memory files. Store the actual artifact/reference, numerical counterexample and command when they matter; do not reproduce entire chat histories or dump every tool response.

## Claim, work and handoff protocol

Use a small state set: **active → ready for review → accepted**, with **blocked** and **cancelled** when real. “Planned” work remains in the accepted milestone list until claimed. “Accepted” means its defined evidence and review are complete; it does not mean the entire release is complete.

1. Coordinator records a claim and its exact files before dispatch. Worker acknowledges the task ID, input checkpoint and dependency readiness before writing. Two claims cannot overlap mutable files. Read-only reviewers may overlap.
2. Worker updates source within the claim. New interface/files outside it require a short concrete claim amendment, not another strategic planning cycle. This is coordination among authorized agents, not a new user permission gate.
3. Producer reports readiness with paths, exact implemented API, checks, current defects and what the consumer may now do. “Draft exists” is insufficient for a runnable dependency.
4. Consumer acknowledges the dependency checkpoint before the dependent mutation. Example: website locale capture precedes English lesson regeneration; generator readiness precedes website-copy synchronization.
5. Worker hands off a compact record: changed files, request/model/schema assumptions, evidence command/result, known limits and the next owner. Reviewer reports counterexamples/minimal fixes or acceptance; coordinator records disposition and integration state.

Short-term agents receive the same bounded claim. Use them for genuinely parallel research, a narrowly owned implementation slice or independent review. Do not spawn an extra agent merely to forward another agent's status. Domain persistence must not grant automatic rights to edit every file in that directory.

## Shared local files and the non-Git root

The current project root has **no `.git` repository**, while `apps/web` has its own Git checkout and Site configuration. A task claiming to have created a root worktree would therefore be false. Website commits do not checkpoint Python, docs, examples or release state. This is a recovery risk that conversation persistence does not solve.

For the present layout:

- Treat one-writer claims as cooperative coordination, not enforced filesystem locks. Existing agents and user edits can still change files.
- At claim start and handoff, record hashes of the small claimed-file set; include an absent-file marker for new files. Before resuming or transferring, compare against those values. If another writer changed a claimed file, stop that file's write path, inspect the difference and reconcile through the coordinator. Continue independent files where safe.
- Keep a bounded baseline copy of claimed files before nontrivial edits, and a milestone checkpoint covering maintained root source/docs/assets. Exclude dependencies, caches and regenerated build trees. Do not rely on `/tmp` screenshots or agent memory for long-term evidence; promote a necessary reproducer/report before closing its task.
- Never restore a whole baseline over unrelated current work. Recovery compares and reapplies only the intended change; a changed external/user file is not presumed disposable.
- Root Git adoption is a separate concrete migration decision: inspect the nested Site checkout, ignore/generated policy and what belongs in history before initializing anything. Do not silently nest, move or rewrite repositories as a workflow convenience.

Hashes detect unexpected changes; they do not serialize writers or prove semantic correctness. Manual claims are reasonable for this small team. A lock daemon, transaction service or full orchestration platform is unnecessary unless real collisions repeatedly defeat the simpler protocol.

## Resume and interruption

On restart, read CURRENT, the linked accepted contract and the task handoff; inspect actual file hashes and evidence existence. Distinguish “last check passed on these bytes” from “current bytes are checked.” If a producer changed since the consumer's checkpoint, rerun the affected interface check rather than assuming the old ready message still applies.

A stopped conversation does not automatically release its mutable claim. The coordinator first determines that its worker is idle/interrupted, inventories partial files and transfers or cancels the claim explicitly. A missing message/elapsed timeout is not proof that no writer is running. If state is ambiguous, keep the overlapping file paused and work elsewhere; do not let two agents “finish” the same patch concurrently.

Recovery notes should say what exists, what is valid, what is partial, the next executable action and the actual blocker. Avoid “continue where I left off” without artifact identities. On completion, link accepted evidence and close the claim; do not keep a permanent thread manufacturing follow-up work to justify its existence.

## Reviews, stopping and overhead limits

Planning and implementation review remain separate. If the user explicitly requires three sequential rounds, each reviews the previous round's revised artifact; parallel reviews of one unchanged draft count as one round. Otherwise the default is one independent affected-scope review, repair of findings and independent recheck, plus the release check appropriate to the milestone.

Reopen only an affected decision when new evidence reveals a missing requirement or contradiction. Do not repeatedly brainstorm after acceptance because future advanced physics is possible. Numerical changes require independent physical evidence; field/schema changes require parity; exporter changes require meaningful readback/appearance; language changes require maintained-text and actual locale behavior. Do not rerun unrelated matrices to create an impression of activity.

Stop a review loop when defined gates pass, high-impact defects are resolved/rechecked, remaining limitations are recorded and no new counterexample justifies more work. A reviewer must be able to say ready. A blocked dependency needs one actionable owner/next step, not repeated unchanged status reports. No recurring heartbeat or scheduled check is implied by a persistent conversation.

Keep management updates at claim, dependency readiness, material blocker, handoff, review disposition and integration checkpoint. No mandatory minute-by-minute log, per-file ticket, duplicate status board or exhaustive tool transcript. If management writing starts to dominate a small task, use the zero-domain mode.

## Proposed next planning iteration

Challenge this recommendation against three real scenarios: a cross-language Scene change, an independent radial-solver increment, and a package-only release repair. For each, allocate exact writers/reviewers, simulate interruption while a file is partly edited, and demonstrate recovery without relying on chat memory or a nonexistent root Git revision. Decide whether the proposed CURRENT record and checkpoint are enough before adding fields or permanent conversations.

Success is a recoverable scientific artifact with fewer ambiguous handoffs, not more threads, longer plans or a new management subsystem.
