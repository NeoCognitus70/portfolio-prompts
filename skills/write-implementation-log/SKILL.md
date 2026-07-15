---
name: write-implementation-log
description: "AFTER a development task, append an immutable implementation log inside a test-automation-portfolio project's repo (docs/implementation-logs/) from the project template — what was built, decided, broke, and learned. Use when recording completed dev work (\"log what I just built for <project>\"). NOT the end-of-session handover (that is write-handover) and NOT a code review."
argument-hint: "<project-folder> [PORTFOLIO_ROOT=<path>]"
---

Write an implementation log for a **test-automation-portfolio** project.

Read and follow the canonical prompt **`${CLAUDE_PLUGIN_ROOT}/write-implementation-log.prompt.md`**
(bundled at this plugin's root), following the body below its `---` divider exactly.

- `PROJECT` = the project folder name the user supplied — a row in `${CLAUDE_PLUGIN_ROOT}/registry.yml`.
  If none was given, **ask — never guess**.
- The log is a tracked, append-only file **inside the target project repo**; handovers are tracked
  separately by the portfolio root support repository. Conventions and the template location are
  in `${CLAUDE_PLUGIN_ROOT}/project-layout.md`.
- Resolve the **portfolio root** first, per `${CLAUDE_PLUGIN_ROOT}/project-layout.md`
  §"Resolving the portfolio root" — an explicit `PORTFOLIO_ROOT=<path>` argument wins, else the
  plugin-parent, else the CWD; all portfolio-relative paths resolve against it.
