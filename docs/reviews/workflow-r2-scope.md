# Workflow round 2: requirements, review value and trial scope

Reviewed the round-2 selected proposal in `docs/team/DESIGN.md`. This review asks whether the workflow preserves the user's whole request and whether the selected development trial produces useful evidence without a permanent review department or endless review rounds. No implementation or task creation was performed.

## Conclusion

**The selected trial is sufficient and appropriately bounded.** A reusable installed cross-solver T agreement report is a real advance over the current frequency rows and arbitrarily signed plots. It can exercise scientific analysis, package/CLI contracts, understandable figures, provenance and distribution without inventing website work or new physics.

Before workflow freeze, make two narrow requirements explicit: CURRENT must link the full acceptance mapping, including an actually observed continuation by a receiving domain; and each readiness handoff must include the owner's own check before the independent review. The design already rejects a permanent QA department, but self-check responsibility is presently implied rather than assigned.

The scientific metric can remain undecided until the separate development-design rounds. That is an intentional dependency, not a reason to begin implementing a convenient metric now.

## Decisions to delete, modify or add

| Action | Decision | Reason | Reviewable acceptance evidence |
| --- | --- | --- | --- |
| Delete | Do not recreate the discarded JSON ledger, checker, separate domain boards or permanent QA task under new names | CURRENT plus authoritative links already meets the coordination need; extra state creates reconciliation work | A cold reader finds exactly one current work record; no competing task-status store or independent polling manager is needed to continue |
| Delete | Do not require a website feature merely to make all roles participate | Package reports and scientific figures are genuine product work; a duplicate browser metric would create an unnecessary numerical consistency burden | Trial acceptance is satisfiable through installed API/CLI and inspected exports; any website increment needs its own user benefit |
| Modify | Define each domain's readiness as **implementation plus self-check**, followed by independent review | A domain must own its quality; forwarding unchecked code to a permanent testing department is neither autonomous development nor independence | Handoff identifies changed behavior, focused checks actually run, one relevant failure case, known limitations and requested downstream action |
| Modify | Require one reviewer independent of the implementation for each material risk; rotate by task rather than maintaining a review role | A domain's own helper can inspect work, but that does not alone provide independent acceptance if it merely repeats the author's assumptions | Audit report names reviewed changes and author/ reviewer responsibility; disputed findings have a reproduction and a recorded disposition |
| Add | Link a short acceptance map from CURRENT, covering both the team workflow and the scientific increment | A successful report release would not itself prove durable handoffs, and a clean management setup would not deliver the requested real development trial | Each user-level requirement points to implementation, observed evidence and final acceptance or an explicit unresolved condition; no requirement is silently dropped during delegation |
| Add | Require one **real receiving-domain continuation** from the durable record | “Resumable” cannot be accepted solely because notes exist | A recipient records the accepted commit/contract and continues a real dependent task using CURRENT and linked artifacts, without a sender's reconstructed conversation; record any missing information and resulting repair |
| Modify | Bound additional reviews by identified unresolved risks or invalidated evidence | The present “new question” condition could otherwise justify an unlimited supply of new questions | Every extra review names the risk/finding it closes or changed artifact that invalidated prior evidence; no open relevant blocker and no stale evidence means closure |
| Modify | Distinguish a late corrective patch from restarting all rounds | A caption or metadata repair can invalidate an output check without changing numerical physics | Affected-check record explains what was repeated and what remained valid; repaired counterexample passes against the final source/ artifact identity |

These changes need a few explicit lines or links, not another management schema.

## Keep three different scientific claims separate

The selected proposal correctly says not to call agreement convergence. Preserve that separation in the later API, table headings, figures, CLI text and evidence status:

1. **Method agreement:** two solvers, explicitly paired modes, a stated common model/support and radial measure. Similar answers can share an error. Frequency agreement and shape agreement are different quantities.
2. **Mesh-refinement evidence:** one method evaluated at two requested resolutions, with actual meshes recorded. A small two-resolution change is measured refinement behavior; it is not a proof of continuum convergence or a universal high-order accuracy guarantee. Report the default and owned method separately, including mandatory knots that may make requested meshes less different than expected.
3. **Independent physical reference:** the named Bessel, traction-ODE or MINEOS quantity, its source and its scope. Reusing an existing verified reference is sensible; it must remain distinct from the pair being compared. A frequency-only reference does not certify eigenfunction shape.

Do not collapse these into one traffic-light “validated” status. The existing pilot's `unverified` mode labels should not be promoted merely because a report was generated or two methods agreed. A report can contain successful measured checks without mutating source quality or source hashes.

An executable negative case should demonstrate why the separation matters: two identical deliberately perturbed shapes agree perfectly with each other while disagreeing with an independent shape reference. This is a small scientific counterexample, not a request for more solver machinery.

## Scope sufficiency and minimum boundaries

The proposed report includes enough user value only if installed users can run it on a documented custom same-model pair, save machine-readable results, and inspect a genuine figure. A source-only benchmark summary or wrapper around the current frequency CSV would be too narrow.

Conversely, the first increment does not need automatic tracking, general degeneracy/subspace matching, cross-model density/radius transport, kernels, MINEOS binary parsing, source excitation or a new backend dispatch. Explicit T pairs with supported same-model/domain eligibility are sufficient. Unsupported comparisons should yield a clear inapplicable-metric result or rejection defined by the contract; the existing independent-curve comparison should remain available.

Exact equations, material eligibility, interface quadrature, norm/sign behavior, numerical thresholds and output schema belong in development design round 1/2. Development round 3 must include concrete example requests and expected report fields so package work can proceed from a stable contract. Do not defer these decisions until the two owners have already implemented different interpretations.

One small provenance observation reinforces this need: the current comparison exporter hardcodes generator version `0.1.0` despite package version `0.2.0`. Fixing it alone is not the trial, but the new report's source/version assertions should prevent repeating that drift.

## What each review round must earn

| Stage | Distinct question | Required output and stop condition |
| --- | --- | --- |
| Workflow 1 | Which durable structure fits actual incidents and the roadmap? | Selected alternatives and rejected machinery; complete |
| Workflow 2 | Can interruptions, ownership ambiguity or review delegation lose requirements? | Minimal repairs and acceptance mapping; this report contributes |
| Workflow 3 | Can a different context locate authority, inputs, next action and remaining gates? | Readiness/cold-read result; close when the concrete omissions are repaired |
| Development design 1 | What scientific/user question is the report allowed to answer? | Equations, scope and worked examples |
| Development design 2 | Can interfaces, signs, domain identity or requested meshes mislead? | Counterexamples and revised API/evidence contract |
| Development design 3 | Can both owners implement and release it from the contract without guessing? | Exact dispatch scopes, dependencies and executable acceptance |
| Implementation audit 1 | Does the numerical report measure what it claims? | Independent reference and adversarial evidence, with repaired findings |
| Implementation audit 2 | Can an installed-facing user understand and reproduce the result? | Actual API/CLI and native artifact checks, with truthful labels/provenance |
| Implementation audit 3 | Do the final archives reproduce the accepted source and workflow? | Clean installation, final identities and an operational handoff |

A round may close with a reasoned pass; it need not invent a bug or demand an improvement quota. Tests are selected for the changed behavior and known failure modes, rather than growing because another reviewer exists. Three implementation audits are three different sources of evidence, not three repetitions of one test command.

## Final acceptance of the workflow experiment

The coordinator should be able to show: a complete released scientific increment; at least one actual acknowledged cross-domain continuation; no conflicting writes or silently discarded work; no lost requirement; and no stale released artifact or unperformed check marked passed. Record real rework, late findings and reopened handoffs as observations. A collision count of zero is useful evidence, but one successful trial cannot establish general throughput or cost superiority.

After the trial, revise only the mechanisms implicated by those observations, leave a clear next task and stop the active dispatches. Durable context is available for future work; it is not permission for an idle domain to continue generating features or reviews.
