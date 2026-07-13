---
name: derive-all-worklists
description: "PREPARE worklists across the WHOLE test-automation-portfolio in one pass — fan out one sub-agent per registry project, each deriving its worklist; collate all breakdowns and user decisions. No actioning, read-only. Use for \"prepare/derive worklists for all projects\". Takes NO project (targets the whole registry); optionally PROJECTS=<a>,<b>."
argument-hint: "[PROJECTS=<folder>,<folder>,...]"
---

Orchestrate worklist **derivation** across the whole portfolio (no actioning).

Read and follow the canonical prompt **`${CLAUDE_PLUGIN_ROOT}/derive-all-worklists.prompt.md`** (bundled
at this plugin's root), following the body below its `---` divider exactly.

- Takes **no `PROJECT=`** — it targets every row in `${CLAUDE_PLUGIN_ROOT}/registry.yml`. Optionally
  restrict with `PROJECTS=<folder>,<folder>,...`.
- Each sub-agent writes only its own `WORKLIST_<project>.md`; the orchestrator writes nothing.
  Shared fan-out conventions are in `${CLAUDE_PLUGIN_ROOT}/project-layout.md`.
