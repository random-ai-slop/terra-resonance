# Workflow review, round 1: release and handoff counterproposal

Reviewer: scope_review. This is a proposal based on the phase-2 handoffs I performed, not a new operating policy. No runtime, threads or scheduled tasks were changed. The useful outcome is fewer invalidated handoffs while keeping the independent reviews that found real defects.

## What the completed work establishes

The existing team already has strong foundations: bounded assignments, one writer per file, independent counterexamples, explicit scientific contracts and installed release evidence. The [phase-2 ownership map](../phase-2-ownership.json) prevented simultaneous document edits; the [developer guide](../DEVELOPMENT.md) describes these principles. A replacement management framework is not justified.

There were nevertheless concrete coordination costs:

| Observed event | What failed or worked | Smallest response |
|---|---|---|
| The first release archive audit failed on `docs/reviews/phase-2-implementation-r2-scope.md`, changed after the initial build | “Source ready” did not identify which outputs were frozen; runtime readiness and documentation readiness differed | Name the accepted input set for each handoff and identify the sole writer of generated destinations. Freeze the actual distribution inputs before its final build. |
| Previews were regenerated after the depth-order repair, then again after the small-image annotation repair | A decodable image was accepted before inspecting the actual output sizes | Before requesting final preview generation, author and non-author inspect a small representative artifact set. For the observed renderer change: rear/front cut and 320/640/1200 annotation layouts. |
| API GLB succeeded with 57,910 effective points while CLI rejected the original 273,078-point Scene despite saved explicit omissions | File separation left operation semantics duplicated across the boundary | Give one owner responsibility for the entire changed user operation, with explicit file ownership beneath it; ask the reviewer to compare entry points on the same input. The resulting shared `effective_glb_scene` helper is sufficient. |
| An independent numerical reviewer found 82,994 incorrectly different rear-cut pixels despite passing focused tests | Fresh viewpoint and an analytic visual expectation worked | Keep non-author review; rotate by the relevant failure mode rather than create a permanent reviewer who approves every own subsystem change. |
| Final wheel/source installs matched 38 runtime/resource files; the only post-media runtime difference was `export_render.py` annotation layout | Byte comparison made selective revalidation defensible | Retain input identity and executed artifact identity. Repeat changed PNG sizes and imports after rebuilding, not unrelated numerical matrices or all media encoding. |
| Network access could not install setuptools during release; an existing cached wheel completed the source install | Environment preparation arrived during the critical release path | At release-task start, check interpreter, build backend, dependency/cache availability and FFmpeg tools. Do this once per release environment, not before every edit. |
| Package verification completed independently of website publication approval | Separate deliverable status prevented an external permission delay from invalidating local acceptance | Keep package, website build and deployment states separate. No recurring monitor or additional approval process is needed. |

The numerical/API reproductions and fixes are recorded in [implementation review 1](phase-2-implementation-r1-python.md). The layout finding and installed checks are in [release review 3](phase-2-implementation-r3-release.md), with final byte evidence in `dist/python/phase-2-release-verification.json`. The archive mismatch and repeated generation sequence above are firsthand handoff observations; they are not invented timing estimates.

## Minimal team arrangement

Keep one coordinating task accountable for the current user objective, scope decisions and integration. Use short-lived subagents for a bounded implementation, independent review, or release check. A task assignment should contain only:

1. The observable outcome and explicit exclusions.
2. Files the agent may write, and the current owner of each shared/generated destination.
3. Inputs that must be ready, with an executable example or current content identity.
4. The smallest acceptance evidence and the person/agent that consumes the handoff.

This is an assignment format, not a database schema. A single current-work note can summarize live ownership and blocked dependencies when the change actually spans several owners. Do not duplicate every status into a task board, manifest, thread summary and review log. Existing historical reviews remain evidence; the current note links them instead of retelling them.

Long-lived responsibility tasks are useful only when there is a distinct recurring backlog and reusable technical context. A numerical-methods task has evidence for that role: the owned toroidal pilot, default backend and future T→R→S work have their own equations and gates. Package/product delivery can have a separate context if it receives sustained independent work. Neither should be permanently running. Begin with the smallest arrangement the next real change needs; do not create four standing tasks just because four agents were useful during this phase.

A long-lived task is a context holder, not a perpetual file lock or approval authority. The coordinator grants write ownership for the current change and explicitly transfers it. This addresses the observed transfer from implementation/export ownership to release ownership without requiring a distributed lock service. An independent reviewer is selected per change and does not gain runtime write permission merely by identifying a bug.

## Handoffs and release sequence

Use three factual handoff descriptions:

- **Ready for integration:** named API/artifact executes and the focused checks pass; list remaining dependent work. The installed `load_example` readiness message was effective because the CLI owner could immediately call the actual API.
- **Ready for independent review:** identify the changed behavior, one representative successful result and one risk-bearing counterexample. Passing test counts alone did not reveal the rear-cut or small-image defects.
- **Ready for final packaging:** runtime, resources and retained release documents are finished; generation/sync checks pass; no owner has a pending write to those distribution inputs.

These are not permission gates. An owner proceeds through already authorized work and reports readiness when it is true. If a defect appears after a freeze, reopen only the affected inputs, repair it and name which evidence is invalidated.

The practical release order is: representative artifact review → fixes and focused checks → one final preview/resource generation → input freeze → build/install/decode → evidence finalization → final identity check. An initial candidate may be needed to generate installed evidence. If the source archive includes the resulting report, allow one intentional documentation-only final build; compare runtime bytes and repeat installation/import checks. Do not pretend such a build is avoidable, or rerun the numerical matrix merely because the source tarball hash changed. Keep archive hashes beside the archive to avoid self-reference.

The latest release demonstrates this approach: the final artifact contained 182 checked source files and both installations matched all 38 packaged runtime/resource files. Preserve that check rather than add an elaborate provenance service. Record which commands exercised which files; do not label a reused dependency environment as a newly provisioned one.

## Keep, change, remove, add

**Keep** unique writers, executable readiness notices, cross-author counterexamples, content hashes and separate deployment status. Each has direct successful use above.

**Change** responsibility from “own these files and finish them” to “own this observable user operation within these file boundaries.” The CLI/API omission mismatch is the motivating counterexample. Stable contracts still matter, but duplicated semantic decisions need one integration owner.

**Remove** an automatic requirement for every small change to repeat the entire release matrix, for every role to have a permanent active task, or for every handoff to create another planning document. The annotation-only rebuild already showed why input-based revalidation is more informative. Honor explicitly requested review rounds; do not interpret their number as a demand for identical repeated suites.

**Add** early artifact inspection, an explicit distribution-input freeze, a compact evidence-to-input mapping and release-environment preflight. These address the observed late layout discovery, concurrent document update, unnecessary rerun risk and missing setuptools availability respectively.

## One real development experiment

A useful bounded pilot is the missing standalone CLI surface selection: `terra scene --wireframe-spacing-deg 30` currently creates the default solid Scene, so the saved setting remains inactive until the user edits JSON, uses Python or visits the website. This is documented behavior, not a fabricated scientific bug. A small `terra scene --surface solid|wireframe` option would make the already-supported grid directly usable from the CLI without changing Scene semantics or the numerical backend.

The experiment is reproducible with the existing `cli.py` scene branch and `data.default_scene` (`surface="solid"`). Implement the option with one package owner; a second agent independently checks absent-flag compatibility and renders the CLI-created wireframe; documentation can proceed independently after the flag contract is named. The coordinator integrates the result and records actual installed usage. Do not add general Scene editing, more flags, a new schema or full numerical baselines to make this pilot appear substantial. If the lead selects a different user-facing change, retain the same measurable cross-entry-point and artifact check.

Observe only four quantities for this trial: ownership collisions, handoffs invalidated by later writes, final asset generations/builds and the reason for each, and whether a non-author can reproduce the result from the handoff without another context question. Also record elapsed implementation/review/blocking time as observations, not quotas; one trial cannot establish a general speedup. Success is a useful completed change, zero ambiguous concurrent writers, a reproducible independent check, and no unaccounted source change after the accepted identity. A real defect causing another build is healthy review, not a metric failure.

Stop adding workflow machinery if these observations remain manageable in one compact work note. Revisit long-lived task structure only when an actual second backlog or repeated context reconstruction supplies evidence for it.
