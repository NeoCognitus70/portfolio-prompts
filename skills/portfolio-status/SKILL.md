---
name: portfolio-status
description: "REPORT the current status of the WHOLE test-automation-portfolio: local repo state, open backlog counts, latest handovers, open PRs, and default-branch CI. Strictly read-only; takes NO project and changes nothing."
---

Report the current status of the whole portfolio without changing it.

Read and follow the [canonical prompt](../../portfolio-status.prompt.md), following the body below
its `---` divider exactly.

- Takes **no `PROJECT=`** — it reports every project in the bundled
  [registry](../../registry.yml).
- It is strictly read-only: write no files, change no repositories, and do not refresh remote Git
  state.
- Resolve the **portfolio root** first, per the bundled [project layout](../../project-layout.md)
  §"Resolving the portfolio root" — an explicit `PORTFOLIO_ROOT=<path>` argument wins, else the
  library-parent, else the nearest qualifying CWD/ancestor; all portfolio-relative paths resolve
  against it.
