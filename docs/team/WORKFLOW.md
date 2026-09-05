# Terra Resonance operating workflow

Status: active operating protocol v1.2, 2026-09-04, incorporating the explicitly requested public delivery domain after three workflow design reviews. Actual adoption and development-trial outcomes remain tracked in CURRENT.

## Start and authority

For coordinated work read the primary local `docs/team/CURRENT.md` (independent public contributors use their own user assignment and `CURRENT.example.md`), the assigned task's accepted design and its linked handoff. Confirm your actual checkout and Git state before editing. A worktree copy of CURRENT is a historical snapshot; the coordinator supplies the absolute primary path in each dispatch. Scientific CONTRACT, model/bundle provenance, actual source and executed evidence retain their separate meanings.

The coordinator owns the goal, current record, scope decisions, integrations, website/Sites lifecycle and final acceptance. Three bounded specialist roles retain numerical-method, package/production and website/delivery context. Their actual native task readiness is recorded locally; a proposed role is not proof of an active task. They execute bounded assignments and then become idle. Transient subagents handle independent bounded investigation, implementation or adversarial review. An author does not close their own scientific or release review.

Do not infer a task from a role title or old backlog item. Never start a recurring monitor, loop or new conversation solely because a role is durable. Use native tools and known handles; create no orchestration service or duplicated dashboard.

## A task is an observable operation

CURRENT records the task ID and attempt, role/thread, accepted input revision, exact allowed paths, dependencies, acceptance artifacts, current coordination status and next action. Statuses are planned, active, review, accepted, blocked and cancelled. Blocked means a concrete dependency or environment condition; it does not release file ownership automatically.

Before writing, acknowledge task ID/attempt, owner handle, accepted implementation base and scope against primary CURRENT. An identical repeated dispatch resumes that attempt; a mismatched or superseded attempt stops new writes and cannot be integrated. The latest incidental coordinator commit is not automatically a new accepted implementation base. Raise a concrete path amendment with the coordinator when necessary; this is internal coordination, not a user approval gate. Include known child and command-session handles in a running-task handoff when they can continue writing. No overlapping live write claims are allowed, even across worktrees: isolation prevents physical overwrite but not competing implementations. Read-only reviewers may overlap. The coordinator permits at most two implementations and one independent reviewer concurrently, adjusted downward when tools or dependencies limit useful work.

A temporary agent gets a concrete independent question, output and file scope. The dispatch specifies its concurrency allowance. Do not delegate only to forward status or multiply identical opinions. Prefer reusing an available agent to creating a duplicate task after an ambiguous tool result.

## Source isolation and integration

The public monorepo includes scientific source and `apps/web`. The original Sites history is preserved locally as a publication mirror, not a second development authority; only its assigned owner updates it from a tested canonical revision. The pre-publication scientific checkpoint remains in a local archival branch and is not pushed. Public history starts with the reviewed complete source and excludes live CURRENT/handoffs. Dependency environments, credentials, agent settings, caches, local artifacts and distributions are excluded from Git; necessary evidence belongs in maintained docs/examples.

Each specialist uses its native worktree. Before beginning a new assignment, inspect tracked/untracked changes and integrate the coordinator's accepted revision without discarding work. If the worktree is dirty or a merge conflicts, report the concrete conflict and preserve changes; do not hard-reset, force-checkout, delete untracked work or silently switch to editing the primary checkout.

Scientific/package specialists run `scripts/sync_web_assets.py --target package`; web/all writes belong to the currently assigned website owner. Public worktrees now contain website source. Older pre-publication worktrees lack it and must integrate an explicitly accepted public baseline before web work. Inspect generator destinations before handoff.

Return a commit containing only permitted changes and evidence, with a clean declared task scope. The handoff names accepted base B and completed commits H. The coordinator inspects `git log B..H`, `git diff --name-status B H`, actual worktree status and artifacts, plus semantic input changes on the primary since B. Clean Git merging does not prove an unchanged scientific contract. Integrate explicit commits, record primary revision I and run the affected integration check on I; consumers receive I before dependent writes. The coordinator updates CURRENT with accepted identities and informs consumers. A worktree or source commit is a checkpoint, not a correctness certificate.

## Handoff and resume

A ready handoff contains: task/attempt; input and output commit; changed paths; implemented API or artifact; owner's self-check (including a relevant failure case), exact reproduction command and actual result; known limits; remaining dependency; next consumer/action. Link existing reports instead of copying their contents. The consumer acknowledges the input before dependent changes.

On timeout, poll the same thread/process handle or inspect its current authoritative status. Native list discovery can omit a completed task: a user-supplied actual ID successfully recovered all three bootstrap reports in this trial. Preserve actual IDs and use direct reads/waits; list omission does not mean absence. Ask for an ID only when native discovery cannot resolve the client handle; never duplicate creation merely because a list omits it. Do not equate an observation timeout with failure, and do not restart an encoding/build/worker from a lock file or old note. If liveness is uncertain, keep the affected writer claim paused and inspect known process/child handles. A replacement requires confirmed quiescence or a separate checkout with explicit revocation of the old attempt’s integration authority. If a worker is truly terminal or unavailable, inspect partial work, preserve its checkpoint and explicitly transfer the same task to a new attempt. Record which prior evidence is invalidated. A resumed worker rechecks current files and accepted inputs rather than trusting remembered success.

Keep a short domain handoff only at task completion, interruption or transfer. Do not maintain parallel domain task boards. Closed tasks retain the decisive evidence and rationale; CURRENT keeps the active milestone and a compact completed summary.

## Evidence and review

CURRENT links acceptance for both the scientific feature and this workflow. Map every accepted requirement to source behavior and evidence of the appropriate scope. At least one real receiving-domain continuation must use the current record and linked artifacts, acknowledge the accepted input and perform useful dependent work; the existence of a handoff note is insufficient. Check command exit/output, not a claimed status alone. Numerical validity requires independent physical identities and material/interface counterexamples. User usability requires the actual API/CLI/browser operation and decoded or inspected artifact. A valid SVG, successful build or high test count alone proves neither.

Planning reviews examine what to keep/change/remove/add and whether the proposed outcome is sufficient. Implementation reviews attack actual code and artifacts. Each sequential round names a different question or changed input and records its decision delta. Stop after required rounds and closure of their material findings. Add a round only for a named unresolved risk or changed artifact invalidating earlier evidence; a review with no findings still needs concrete covered risks and evidence.

For this workflow trial use three design rounds and three postimplementation audits: scientific counterexamples, user-facing package/artifacts, then isolated installation/release. Ordinary future small maintenance uses the affected independent review and recheck; it does not inherit a ceremonial three-round minimum. User-requested counts take precedence.

## Release freeze and selective revalidation

Inspect representative artifacts before final generation, including a small supported image when typography changes. Freeze runtime, maintained documentation and generated resources before the release candidate. The coordinator records the exact distribution input set and sole generator owner. CURRENT and operational handoffs remain local and are excluded from public Git and source distributions; static workflow/design/review and scientific evidence remain included. Documentation changing a command or scientific claim invalidates that check even if runtime files are unchanged; stable model/catalog hashes alone do not certify images generated by changed rendering code. Render evidence names Scene/production inputs, producing code/assets/environment and artifact identity. Retain AGENTS and required generated resources in baseline history while ignoring private agent settings and disposable output.

When figure width and height are independently configurable, typography changes need the affected short-wide cases as well as the minimum/default canvas, with long valid metadata and combined notices. Measure containment and spacing, then inspect native output; a character limit is not a pixel-width guarantee.

Build/install from the frozen candidate in an independent environment outside the checkout. Record real import paths and actual dependency isolation. Decode and inspect affected outputs. If installed evidence is retained inside the source distribution, allow one documented final evidence-only build, then compare runtime/resource bytes and repeat final installation/import checks. The existing hosted CI can perform that final build/check after evidence text is committed; an extra identical local build is unnecessary. Keep final archive hashes beside the archives to avoid self-reference.

A post-freeze defect reopens affected inputs. State which evidence remains valid and which must be repeated. Do not rerun a numerical matrix for annotation-only changes; do not reuse render evidence after the renderer changes. Package acceptance, website build and external publication are distinct states. External writes use the user's actual authorization and current destination/audience; an automated rejection is not a reason to bypass controls.

## Evaluate the workflow

For each trial, record observed owner collisions, invalidated handoffs and causes, artifact regeneration/build reasons, broad reruns with no changed inputs, reviewer findings by discovery stage, and cold-start continuation outcome. Do not invent timing/token baselines. Hard outcomes are no lost accepted requirement, no competing writer, reproducible non-author evidence, and no stale released artifact.

Retrospective changes must remove friction or prevent a concrete failure. Keep the current protocol when it works. The user-requested public GitHub/Pages delivery, alongside Sites and bilingual frontend maintenance, justifies one combined website/delivery domain. Do not split development and deployment into competing owners. Add further domains, automation or machine checkers only for demonstrated recurring need.

## Model selection by task

The user explicitly permits model tiers. Keep high-capability models for scientific derivation, ambiguous design, semantic integration and adversarial numerical/release review. Use a lighter available model for a bounded mechanical task whose input, allowed edit and acceptance command are already settled: deterministic text/version updates, file inventories, or an established command run with evidence collection. Start with `gpt-5.6-luna` for those tasks, escalating to a stronger model only for a concrete unresolved interpretation or failure. Do not call a task mechanical merely because its output is short; scientific signs, units, provenance and release destination decisions retain capable review.

Each dispatch names the selected model when overridden, the reason, exact inputs and a checkable result. The receiving owner inspects the actual diff/artifact. A cheaper author does not remove independent review; model diversity alone is not evidence of correctness. Existing running tasks retain their settings unless an explicit new bounded assignment justifies a change. Prefer native model options over editing global configuration or creating duplicate conversations solely to change a model.

Initial native bootstrap should return one compact message to the supplied coordinator task using `send_message_to_thread`, then become idle. The transport's source task ID establishes the real handle even when list discovery omits the task; include actual cwd, HEAD/status, role boundary and missing assignment. This avoids requiring the user to relay links. The trial verified that direct task reads and a numerical specialist's incoming native message expose the actual ID. After registration, normal bounded completion uses the known-ID wait/handoff path; do not duplicate every progress update across tasks.

A model tier is an option, not a reason to delegate. For a lone literal change, prefer local execution or include it in an already useful bounded domain operation. The version-preparation trial established reviewed correctness with a lighter child, not an efficiency or cost advantage; no controlled comparison was made.
