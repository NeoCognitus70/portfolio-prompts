---
name: close-project
description: "In the FINAL session of a test-automation-portfolio project, close it out — verify every public-facing README claim (fetch live artefacts, CI green), reconcile the backlog one last time, retire WORKLIST_<project>.md, and write a terminal handover marked FINAL. Use for \"close out / archive <project>\". Takes the project folder name. Only when the backlog is complete or every item is explicitly deferred."
argument-hint: "<project-folder>"
---

Close out a **test-automation-portfolio** project (terminal session).

Read and follow the canonical prompt **`${CLAUDE_PLUGIN_ROOT}/close-project.prompt.md`** (bundled at
this plugin's root), following the body below its `---` divider exactly.

- `PROJECT` = the project folder name the user supplied — a row in `${CLAUDE_PLUGIN_ROOT}/registry.yml`.
  If none was given, **ask — never guess**.
- Closure requires every backlog item done/closed/deferred; if any is genuinely open, stop and report.
  Nothing destructive without explicit instruction. Conventions are in `${CLAUDE_PLUGIN_ROOT}/project-layout.md`.
