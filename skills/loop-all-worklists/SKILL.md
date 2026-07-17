---
name: loop-all-worklists
description: "Action ALL prepared worklists across the test-automation-portfolio in one pass — fan out one sub-agent per project with unchecked items, each executing its loop iterations (commit + PR, never merge); coupled projects share one sequential agent. MUTATING and high-impact — invoke EXPLICITLY only, never as an incidental auto-trigger. Use only on a deliberate \"action all worklists\" request. Takes NO project; optionally PROJECTS=<a>,<b> and MAXITEMS=<n>."
argument-hint: "[PROJECTS=<folder>,<folder>,...] [MAXITEMS=<n>] [PORTFOLIO_ROOT=<path>]"
disable-model-invocation: true
---

Orchestrate worklist **execution** across the whole portfolio. **Mutating and high-impact** — only
run this when the user has explicitly asked to action all worklists; do not trigger it incidentally.

Read and follow the canonical prompt **`${CLAUDE_PLUGIN_ROOT}/loop-all-worklists.prompt.md`** (bundled
at this plugin's root), following the body below its `---` divider exactly.

- Takes **no `PROJECT=`** — it targets every `WORKLIST_<project>.md` with unchecked items. Optionally
  restrict with `PROJECTS=...` and cap per project with `MAXITEMS=<n>`.
- The canonical prompt runs the read-only registry-driven workspace preflight before fan-out.
- After preflight, do the coupling check (coupled projects run in one sequential agent). Sub-agents
  commit and open PRs but **never merge**. Shared fan-out conventions are in
  `${CLAUDE_PLUGIN_ROOT}/project-layout.md`.
- Resolve the **portfolio root** first, per `${CLAUDE_PLUGIN_ROOT}/project-layout.md`
  §"Resolving the portfolio root" — an explicit `PORTFOLIO_ROOT=<path>` argument wins, else the
  plugin-parent, else the CWD; all portfolio-relative paths resolve against it.
