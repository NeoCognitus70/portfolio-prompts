---
name: write-handover
description: "At the END of a session, write the next versioned session-notes handover (.md + generated .html) for a test-automation-portfolio project into session-notes/, reconciling the backlog first so any agent can resume cold. Use for \"write the handover / wrap up <project>\". Takes the project folder name. NOT for resuming (that is resume-session) or the final close-out (that is close-project)."
argument-hint: "<project-folder>"
---

Write the end-of-session handover for a **test-automation-portfolio** project.

Read and follow the canonical prompt **`${CLAUDE_PLUGIN_ROOT}/write-handover.prompt.md`** (bundled at
this plugin's root), following the body below its `---` divider exactly.

- `PROJECT` = the project folder name the user supplied — a row in `${CLAUDE_PLUGIN_ROOT}/registry.yml`.
  If none was given, **ask — never guess**.
- Reconcile `docs/backlog.md` first, then write both files into `session-notes/` (never at the root)
  and regenerate the handover manifest. Conventions are in `${CLAUDE_PLUGIN_ROOT}/project-layout.md`.
