# Autonomous team workflow design

Status: protocol v1 accepted after three sequential design reviews, 2026-09-04. Earlier proposals below retain decision history. Deployment and real-trial verification are tracked separately in CURRENT.

## Objective and completion evidence

Design a long-lived working arrangement grounded in the actual Terra Resonance development history; subject it to distinct brainstorming/adversarial rounds; instantiate its threads, ownership and resumable project records; then run a real scientific/product increment through multiple design and implementation reviews. Evaluate the workflow using observed incidents and outcomes, revise it, and leave an operational handoff. More documents or more agents alone are not success.

## Observed history

| Evidence | Consequence | Candidate repair |
| --- | --- | --- |
| Phase-2 release rebuilt after concurrent documentation and generated-preview changes | Installed artifacts no longer exactly represented the latest maintained source | One explicit release freeze over source, docs and generated resources; reports with archive hashes outside the archive |
| Root issued shell paths relative to the repository while using a web working directory twice | Two writes failed before affecting source | Every task names its repository root and commands use that root consistently |
| File ownership was coordinated successfully but primarily through messages | A resumed worker must reconstruct who may edit shared files | A small coordinator-owned work record, accepted per-task file scopes, explicit ownership transfer |
| The numerical reviewer reproduced far-side cut overdraw; real browser SVG selected a control icon | Unit/build passes did not prove output meaning | Independent physical counterexamples plus decoded/rendered user artifacts |
| Initial source push was blocked until the user explicitly authorized its external destination | Release and scientific completion had different authorization states | Keep local deliverable readiness separate from publication authorization; preserve exact destination/audience evidence |
| A new subagent spawn hit the thread limit in this session, while reactivating existing named agents worked | Counting listed running agents was insufficient to predict spawn availability | Reuse known agents, inspect actual handles, fall back to sequential bounded review; never recreate a task just because observation timed out |

Historical evidence is in `docs/reviews/phase-2-implementation-*`; failed shell/tool calls are recorded in this coordinator conversation. These are qualitative observations, not measured baseline throughput statistics.

## Candidate architecture

The coordinator owns the current goal, priorities, acceptance mapping, cross-domain contracts, integration, website lifecycle and release decision. Two candidate durable specialist tasks cover numerical methods/evidence and the package/research-output interface. Their conversations retain domain context; repository records retain authority. Short-lived reviewers should be independent of the implementation under review, with a bounded question and an explicit stop condition. A permanent review bureaucracy is not proposed.

Persistent roles do not receive an unbounded instruction to keep changing the product. Each execution gets a specific task ID, accepted input revision, paths it may change, dependencies, acceptance artifacts and handoff. A manager stops after that task and is reactivated by the coordinator. The active goal drives this development cycle; there is no implied recurring automation or background watch.

The current scientific package root is not a Git repository, while `apps/web` has its own clean Sites repository. Options to review: retain shared-local disjoint scopes with content fingerprints; or initialize local scientific Git history, preserve the separate Site checkout and use native worktrees for new specialist tasks. A worktree isolates writes but does not solve stale contracts or integration by itself. No remote scientific repository publication is implied.

A candidate minimal durable record consists of a short root AGENTS.md router, one workflow document, one coordinator-owned task ledger, and domain handoff notes. A small read-only checker may detect duplicate owners, unresolved dependencies or missing evidence. It must not treat a claimed status, JSON schema pass or file timestamp as proof of running/completed work. Build a custom scheduler only if native thread tools demonstrably cannot support the concrete task.

## Round structure under review

Workflow round 1 compares architectures and real incidents. Round 2 attacks the selected design using interruption, stale inputs, write collision, empty review and late release-change cases. Round 3 is a cold-start/readiness test and removes machinery that did not prevent a concrete failure. Each round records changed decisions or a supported closure; repeating the same review under a new label is not a round.

The development trial is chosen for real scientific/user value after independent proposals. Tentative criteria: crosses numerical and package boundaries, has independent reference evidence, requires an installed user artifact, is a coherent roadmap increment and does not require a website change solely to exercise every manager. Its design and audit counts will be fixed after scientific risk is understood; failed gates reopen the relevant question rather than mandate a full new ceremony.

## External evidence and limits

- Anthropic's [long-running harness experience](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) motivates explicit resumable artifacts and end-to-end verification. Its web-app experiment does not establish the best scientific-team architecture or justify a large feature checklist here.
- Anthropic's [multi-agent research experience](https://www.anthropic.com/engineering/multi-agent-research-system) motivates bounded delegations and cautions that coordination and resource overhead can exceed the benefit for tightly coupled coding. Its research performance figures are not projected onto this project.
- Official [Codex worktree documentation](https://learn.chatgpt.com/docs/environments/git-worktrees) and [AGENTS.md guidance](https://learn.chatgpt.com/docs/agent-configuration/agents-md) inform native mechanisms; current callable tool schemas and observed project/thread state remain authoritative for this session.

Adopt mechanisms only when they solve an observed project problem. No model switching, additional accounts, cloud service or purchased tooling is required.

## Round 2 selected proposal

The three first-round reviewers agreed on unique operation ownership, independent output evidence and a compact current-work record. Their useful disagreement concerned the trial size and whether two durable domains are warranted. Select two context-holding domains for this sustained scientific roadmap, with no permanent QA thread. Keep small maintenance in the coordinator when delegation adds no independent work.

### Decisions changed by round 1

- Replace the tentative JSON ledger/checker/domain boards with **one CURRENT.md**, owned only by the coordinator. Existing contracts and evidence remain authoritative; CURRENT links rather than duplicates them. No management executable is planned initially.
- Select **science** and **package/production** as durable tasks. The coordinator retains the existing website/Sites ownership. Domain names grant no blanket write permission: each dispatched operation has exact paths, dependencies and acceptance.
- Adopt local Git history for the scientific root to provide actual diffs/checkpoints. Preserve `apps/web` as its separate existing repository, ignored by root Git and recorded by its commit identity; do not move it, commit a gitlink or publish the scientific repository. Ignore caches, outputs, editor/agent configuration and environment files. Review the staged source inventory before the baseline commit.
- Use native worktrees for the two new specialist tasks after the root has a committed baseline. Each worktree is a writable implementation environment; the primary CURRENT record is read-only to specialists and its absolute path is supplied in dispatches. Specialist commits are integrated by the coordinator after changed-path review. New work begins only after inspecting a clean/dirty state and synchronizing the accepted root revision without discarding local work.
- Distinguish **integration readiness**, **review readiness** and **distribution freeze** as actual handoffs, not three synonymous status messages. A final documentation-only rebuild is allowed when installed evidence belongs in the source archive. Archive hashes live outside the archive; compare unchanged runtime bytes rather than rerun unrelated physics.

### Development trial selection

Select the **cross-solver toroidal agreement report** from `workflow-r1-trial.md`. It fills an actual installed-analysis gap and tests both persistent domains. The smaller `terra scene --surface` usability improvement is worthwhile but alone would not test sustained scientific-context retention; record it as a future small-maintenance candidate rather than padding the trial. A new R/gravity solver is deferred because this trial should measure collaboration while delivering one complete current-roadmap task.

The report will compare explicit T-mode pairs for the same model and support using frequency difference and a sign-aligned mass-weighted radial shape measure. It will preserve raw inputs, include provenance, produce machine-readable and native figure outputs, and ship an installed API/CLI journey with two-resolution method comparisons and independent reference evidence kept distinct. Do not label agreement as convergence or independent truth. Exact API/metric/error/resource decisions undergo the separate development design rounds after the team is operational.

### Work ownership and recovery

A dispatch contains a task ID, owner handle, accepted input commit/contract, exact allowed paths, outcome, exclusions, dependency, checks and handoff target. At most two implementation tasks run concurrently, plus one independent reviewer when capacity permits. A specialist may use a temporary subagent only for a concrete independent task and within the coordinator's currently assigned concurrency allowance. Idle specialists do not poll or invent work.

One task has one active attempt. Status is a coordination claim; current thread/process tools establish liveness. Before redispatch after interruption or timeout, inspect the same handle and current worktree changes. Do not expire a claim based only on time. A handoff names the commit, changed files, exact executable API/artifact, checks/results, known limits and next action. The consumer acknowledges the input identity before dependent writes. A rejected input updates the same task; it does not spawn a duplicate assignment.

Reviewers may read any relevant code but cannot repair another owner's files without a transfer. The coordinator alone accepts scope changes and integration. Approvals between agents are technical coordination and do not create new user permission gates. External publication still follows the already applicable authorization rules and actual audience.

### Non-circular evidence and review stopping

Track requirements through plan, implementation, independent evidence and release. A reviewer must return a concrete counterexample, a revised requirement/decision, or a reasoned closure on identified risks. Each additional round has a new question or a changed artifact; test counts, prose length and agent count are not progress measures.

For this user-requested workflow experiment, use three sequential workflow rounds (alternatives; failure scenarios; cold-start readiness), three development design rounds (science/user task; interface adversaries; executable acceptance) and three implementation audits (science; user artifacts/API/CLI; installed release). Repair each finding and recheck its counterexample before the dependent round. Additional rounds occur only for an unresolved/materially changed risk, and terminate once those risks close.

Observe ownership collisions, invalidated handoffs and reasons, unnecessary broad reruns, artifact regeneration/build reasons, reviewer findings by discovery stage, and whether another context can resume using only CURRENT plus linked artifacts. No throughput or token-efficiency claim will be made from one uncontrolled trial.


## Round 2 disposition and round 3 readiness questions

All three reviewers retained the two-domain/local-Git/native-worktree decision. Their new corrections are integrated into the proposed WORKFLOW: attempt-aware idempotent dispatch, unknown-writer isolation/revocation, preservation of dirty work, explicit B→H→I integration and semantic input checks, absolute primary authority, package-only synchronization in specialist worktrees, and render-input identity beyond catalog hashes. Live CURRENT/operational handoffs will be excluded from sdist so routine state updates do not invalidate releases. Owner self-checks and one actually observed receiving-domain continuation are explicit acceptance requirements.

Round 3 reads only CURRENT, WORKFLOW and linked design/acceptance. It is a protocol-readiness review, not yet an observed cold-start claim. The actual fresh-context test is the two new specialist conversations' first bounded assignments after activation. Readiness scenarios:

1. A wait times out while the same writer is confirmed active: identify the existing attempt and next observation, without another implementation.
2. A dirty scientific worktree receives an accepted units/API change: preserve work, identify the changed contract, and choose reacceptance/checks rather than reset.
3. An otherwise passing handoff edits primary CURRENT or arrives from a superseded attempt: refuse integration; retain possible evidence without granting old authority.
4. A renderer changes while catalog bytes stay fixed: invalidate affected image evidence, retain unchanged numerical evidence, and name final generation/freeze order.
5. A scientific worktree lacks apps/web: select package-only synchronization, never create a shadow website.
6. A new specialist receives a role charter but no active task tuple: inspect/read and ask the coordinator for the concrete task internally; do not manufacture backlog work.

Freeze only after a reviewer can identify the next safe action and authoritative input for all six cases, and after remaining material ambiguities are repaired. No scenario simulation is evidence of actual worker liveness, publication or a successful installed artifact.


## Round 3 disposition

[The readiness review](../reviews/workflow-r3-readiness.md) resolved all six protocol cases without additional machinery. Activation uses a read-only initial charter because native thread creation can start before its returned ID is recorded. The real context-continuation requirement remains open until the new specialists acknowledge and execute bounded record-based assignments. The workflow is now activated; no additional planning review is justified before observing the real trial.

## Public-delivery amendment

The user explicitly requested public Sites access, publishing the complete project to `random-ai-slop` using configured GitHub CLI, GitHub Pages, package releases and CI, and reconsideration of website ownership. This supersedes the earlier local-only repository and private Site boundaries. [Publication web review](../reviews/publication-web.md) found a concrete recurring website/delivery responsibility; adopt one third dormant specialist role, not separate development/deployment managers. Canonical website source now belongs to the public monorepo; preserve the old Site history only as a local publishing mirror. Native role activation remains an observed outcome, tracked locally rather than assumed.

[Publication science review](../reviews/publication-science.md) identified live CURRENT in the initial local history. Preserve that checkpoint locally and begin public history from a reviewed source snapshot excluding live coordination. Static protocols and a contributor example remain public. This is a publication-boundary correction, not destruction of worktree history.
