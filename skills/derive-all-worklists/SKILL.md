---
name: derive-all-worklists
description: "PREPARE worklists across the WHOLE test-automation-portfolio in one pass — fan out one sub-agent per registry project, each deriving its worklist; collate all breakdowns and user decisions. No actioning, read-only. Use to prepare or derive worklists for all projects. Takes NO project (targets the whole registry); optionally accepts a PROJECTS list."
---

Orchestrate worklist **derivation** across the whole portfolio (no actioning).

Read and follow the [canonical prompt](../../derive-all-worklists.prompt.md), following the body
below its `---` divider exactly.

- Takes **no `PROJECT=`** — it targets every orchestration-enabled row in
  the bundled [registry](../../registry.yml). Optionally restrict with
  `PROJECTS=<folder>,<folder>,...`.
- The canonical prompt runs the read-only registry-driven workspace preflight before fan-out.
- Each sub-agent writes only its own `WORKLIST_<project>.md`; the orchestrator writes nothing.
  Shared fan-out conventions are in the bundled [project layout](../../project-layout.md).
- Resolve the **portfolio root** first, per the bundled [project layout](../../project-layout.md)
  §"Resolving the portfolio root" — an explicit `PORTFOLIO_ROOT=<path>` argument wins, else the
  library-parent, else the nearest qualifying CWD/ancestor; all portfolio-relative paths resolve
  against it.
