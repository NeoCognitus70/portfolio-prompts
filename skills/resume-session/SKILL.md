---
name: resume-session
description: "Resume work on a test-automation-portfolio project at the START of a session — loads the project's latest session-notes handover, cross-checks it against the backlog and the live repo, and proposes where to pick up. Use when reopening, resuming, or picking up work on a named portfolio project. Takes the project folder name. NOT for writing a handover (that is write-handover) or starting fresh work planning (that is derive-worklist)."
---

Resume-from-handover for a **test-automation-portfolio** project.

Read and follow the [canonical prompt](../../resume-session.prompt.md), following the body below its
`---` divider exactly.

- `PROJECT` = the project folder name the user supplied — a row in the bundled
  [registry](../../registry.yml)
  (the README registry). If none was given, **ask — never guess**.
- All paths, gates, and conventions the prompt relies on are defined in
  the bundled [project layout](../../project-layout.md), which the prompt already cites.
- Resolve the **portfolio root** first, per the bundled [project layout](../../project-layout.md)
  §"Resolving the portfolio root" — an explicit `PORTFOLIO_ROOT=<path>` argument wins, else the
  library-parent, else the nearest qualifying CWD/ancestor; all portfolio-relative paths resolve
  against it.
