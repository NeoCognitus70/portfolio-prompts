---
name: review-all-projects
description: "CODE-REVIEW every test-automation-portfolio project in one pass — fan out one sub-agent per registry project, each writing a review into its own .review/ folder on a branch + PR (never merged), then collate a cross-portfolio synthesis of common themes and top-severity findings. Evidence-only, no implementation changes. Use to review the whole portfolio. Takes NO project; optionally accepts a PROJECTS list."
---

Orchestrate a **code review** across the whole portfolio (evidence-only).

Read and follow the [canonical prompt](../../review-all-projects.prompt.md), following the body
below its `---` divider exactly.

- Takes **no `PROJECT=`** — it targets every orchestration-enabled row in
  the bundled [registry](../../registry.yml). Optionally restrict with
  `PROJECTS=<folder>,<folder>,...`.
- The canonical prompt runs the read-only registry-driven workspace preflight before fan-out.
- Each sub-agent writes only review artefacts into its own project, committed on a branch + PR, never
  merged; no implementation changes. Shared fan-out conventions are in
  the bundled [project layout](../../project-layout.md).
- Resolve the **portfolio root** first, per the bundled [project layout](../../project-layout.md)
  §"Resolving the portfolio root" — an explicit `PORTFOLIO_ROOT=<path>` argument wins, else the
  library-parent, else the nearest qualifying CWD/ancestor; all portfolio-relative paths resolve
  against it.
