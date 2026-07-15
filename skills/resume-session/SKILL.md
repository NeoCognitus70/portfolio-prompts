---
name: resume-session
description: "Resume work on a test-automation-portfolio project at the START of a session — loads the project's latest session-notes handover, cross-checks it against the backlog and the live repo, and proposes where to pick up. Use when reopening an existing portfolio project (\"resume/pick up work on <project>\"). Takes the project folder name. NOT for writing a handover (that is write-handover) or starting fresh work planning (that is derive-worklist)."
argument-hint: "<project-folder> [PORTFOLIO_ROOT=<path>]"
---

Resume-from-handover for a **test-automation-portfolio** project.

Read and follow the canonical prompt **`${CLAUDE_PLUGIN_ROOT}/resume-session.prompt.md`** (bundled at
this plugin's root), following the body below its `---` divider exactly.

- `PROJECT` = the project folder name the user supplied — a row in `${CLAUDE_PLUGIN_ROOT}/registry.yml`
  (the README registry). If none was given, **ask — never guess**.
- All paths, gates, and conventions the prompt relies on are defined in
  `${CLAUDE_PLUGIN_ROOT}/project-layout.md`, which the prompt already cites.
- Resolve the **portfolio root** first, per `${CLAUDE_PLUGIN_ROOT}/project-layout.md`
  §"Resolving the portfolio root" — an explicit `PORTFOLIO_ROOT=<path>` argument wins, else the
  plugin-parent, else the CWD; all portfolio-relative paths resolve against it.
