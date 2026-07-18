---
name: write-implementation-log
description: "AFTER a development task, append an immutable implementation log inside a test-automation-portfolio project's repo (docs/implementation-logs/) from the project template — what was built, decided, broke, and learned. Use when recording completed development work for a named project. NOT the end-of-session handover (that is write-handover) and NOT a code review."
---

Write an implementation log for a **test-automation-portfolio** project.

Read and follow the [canonical prompt](../../write-implementation-log.prompt.md), following the
body below its `---` divider exactly.

- `PROJECT` = the project folder name the user supplied — a row in the bundled
  [registry](../../registry.yml).
  If none was given, **ask — never guess**.
- The log is a tracked, append-only file **inside the target project repo**; handovers are tracked
  separately by the portfolio root support repository. Conventions and the template location are
  in the bundled [project layout](../../project-layout.md).
- Resolve the **portfolio root** first, per the bundled [project layout](../../project-layout.md)
  §"Resolving the portfolio root" — an explicit `PORTFOLIO_ROOT=<path>` argument wins, else the
  library-parent, else the nearest qualifying CWD/ancestor; all portfolio-relative paths resolve
  against it.
