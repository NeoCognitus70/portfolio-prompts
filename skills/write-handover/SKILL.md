---
name: write-handover
description: "At the END of a session, write the next versioned session-notes handover (.md + generated .html) for a test-automation-portfolio project into session-notes/, reconciling the backlog first so any agent can resume cold. Use to write the handover or wrap up a named project. Takes the project folder name. NOT for resuming (that is resume-session) or the final close-out (that is close-project)."
---

Write the end-of-session handover for a **test-automation-portfolio** project.

Read and follow the [canonical prompt](../../write-handover.prompt.md), following the body below its
`---` divider exactly.

- `PROJECT` = the project folder name the user supplied — a row in the bundled
  [registry](../../registry.yml).
  If none was given, **ask — never guess**.
- Reconcile `docs/backlog.md` first, then write both files into `session-notes/` (never at the root)
  and regenerate the handover manifest. Conventions are in the bundled
  [project layout](../../project-layout.md).
- Resolve the **portfolio root** first, per the bundled [project layout](../../project-layout.md)
  §"Resolving the portfolio root" — an explicit `PORTFOLIO_ROOT=<path>` argument wins, else the
  library-parent, else the nearest qualifying CWD/ancestor; all portfolio-relative paths resolve
  against it.
