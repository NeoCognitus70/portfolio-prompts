---
name: review-all-projects
description: "CODE-REVIEW every test-automation-portfolio project in one pass — fan out one sub-agent per registry project, each writing a review into its own .review/ folder on a branch + PR (never merged), then collate a cross-portfolio synthesis of common themes and top-severity findings. Evidence-only, no implementation changes. Use for \"review the whole portfolio\". Takes NO project; optionally PROJECTS=<a>,<b>."
argument-hint: "[PROJECTS=<folder>,<folder>,...]"
---

Orchestrate a **code review** across the whole portfolio (evidence-only).

Read and follow the canonical prompt **`${CLAUDE_PLUGIN_ROOT}/review-all-projects.prompt.md`** (bundled
at this plugin's root), following the body below its `---` divider exactly.

- Takes **no `PROJECT=`** — it targets every orchestration-enabled row in
  `${CLAUDE_PLUGIN_ROOT}/registry.yml`. Optionally restrict with
  `PROJECTS=<folder>,<folder>,...`.
- The canonical prompt runs the read-only registry-driven workspace preflight before fan-out.
- Each sub-agent writes only review artefacts into its own project, committed on a branch + PR, never
  merged; no implementation changes. Shared fan-out conventions are in
  `${CLAUDE_PLUGIN_ROOT}/project-layout.md`.
