---
name: loop-worklist
description: "EXECUTE a prepared worklist for one test-automation-portfolio project, one item per invocation or scheduled iteration (implement, validate, verify, commit, record). MUTATING — it changes the repo and opens a PR. Use when working through the prepared worklist for a named project. NOT for preparing the list (that is derive-worklist)."
---

Execute one iteration of a work loop against a **test-automation-portfolio** project. **Mutating:**
it implements, validates, verifies, commits, and opens a PR (never merges).

Read and follow the [canonical prompt](../../loop-worklist.prompt.md), following the body below its
`---` divider exactly.

- `PROJECT` = the project folder name the user supplied — a row in the bundled
  [registry](../../registry.yml).
  A loop binds to exactly one project. If none was given, **ask — never guess**.
- Complete one item per explicit skill invocation. Claude Code may instead drive repeated
  invocations with `/loop`; Codex may use a separately requested automation. Gates must pass before
  every commit; apply the universal working norms in the bundled
  [project layout](../../project-layout.md).
- Resolve the **portfolio root** first, per the bundled [project layout](../../project-layout.md)
  §"Resolving the portfolio root" — an explicit `PORTFOLIO_ROOT=<path>` argument wins, else the
  library-parent, else the nearest qualifying CWD/ancestor; all portfolio-relative paths resolve
  against it.
