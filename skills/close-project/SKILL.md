---
name: close-project
description: "In the FINAL session of a test-automation-portfolio project, close it out — verify every public-facing README claim (fetch live artefacts, CI green), reconcile the backlog one last time, retire the project worklist, and write a terminal handover marked FINAL. Use to close out or archive a named project. Takes the project folder name. Only when the backlog is complete or every item is explicitly deferred."
---

Close out a **test-automation-portfolio** project (terminal session).

Read and follow the [canonical prompt](../../close-project.prompt.md), following the body below its
`---` divider exactly.

- `PROJECT` = the project folder name the user supplied — a row in the bundled
  [registry](../../registry.yml).
  If none was given, **ask — never guess**.
- Closure requires every backlog item done/closed/deferred; if any is genuinely open, stop and report.
  Nothing destructive without explicit instruction. Conventions are in the bundled
  [project layout](../../project-layout.md).
- Resolve the **portfolio root** first, per the bundled [project layout](../../project-layout.md)
  §"Resolving the portfolio root" — an explicit `PORTFOLIO_ROOT=<path>` argument wins, else the
  library-parent, else the nearest qualifying CWD/ancestor; all portfolio-relative paths resolve
  against it.
