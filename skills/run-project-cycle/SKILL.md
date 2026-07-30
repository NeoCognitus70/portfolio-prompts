---
name: run-project-cycle
description: "CONDUCT one test-automation-portfolio project through a full improvement cycle end to end: review, then triage, then loop, then implementation-log, then handover, then optional close. A conductor that SEQUENCES the existing single-project skills with entry/exit gates and owner checkpoints; it delegates each stage and never re-implements one. MUTATING and multi-stage, but human-in-the-loop (stops for approval at triage, each merge, and close). Binds to exactly one PROJECT. NOT a portfolio fan-out for one step across every project (use the all-worklists orchestrators for that)."
---

Conduct a full improvement cycle for a single **test-automation-portfolio** project. This is a
**conductor**: it sequences the canonical single-project skills (`write-code-review` ->
`triage-review-findings` -> `loop-worklist` -> `write-implementation-log` -> `write-handover` ->
optional `close-project`) with the entry/exit gates and owner checkpoints that chain them safely. It
**delegates** each stage to that stage's skill and never re-implements one.

Read and follow the [canonical prompt](../../run-project-cycle.prompt.md), following the body below
its `---` divider exactly.

- `PROJECT` = the project folder name the user supplied — a row in the bundled
  [registry](../../registry.yml). The cycle binds to exactly one project. If none was given,
  **ask — never guess**.
- **Mutating and multi-stage, but checkpointed:** it opens commits/PRs across the stages, yet stops
  for explicit owner approval at the triage candidate list, at each merge, and before close-project.
  It is not a portfolio fan-out — for one step across every registry project use the `*-all-*`
  orchestrators (`review-all-projects`, `derive-all-worklists`, `loop-all-worklists`).
- Gates must pass before every commit; apply the universal working norms and the validation-gates
  cascade in the bundled [project layout](../../project-layout.md) — this skill references them, it
  does not restate them.
- Resolve the **portfolio root** first, per the bundled [project layout](../../project-layout.md)
  §"Resolving the portfolio root" — an explicit `PORTFOLIO_ROOT=<path>` argument wins, else the
  library-parent, else the nearest qualifying CWD/ancestor; all portfolio-relative paths resolve
  against it.
