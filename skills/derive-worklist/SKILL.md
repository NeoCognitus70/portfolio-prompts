---
name: derive-worklist
description: "PREPARE (without actioning) a worklist for one test-automation-portfolio project — orient from handover + backlog, derive and cross-check the items, write the project worklist, and report a per-item breakdown for review. Use when preparing or planning a worklist for a named project. Read-only in the project repo. NOT for executing the work (that is loop-worklist) or reviewing code (that is write-code-review)."
---

Derive-a-worklist (no actioning) for a **test-automation-portfolio** project.

Read and follow the [canonical prompt](../../derive-worklist.prompt.md), following the body below
its `---` divider exactly.

- `PROJECT` = the project folder name the user supplied — a row in the bundled
  [registry](../../registry.yml).
  If none was given, **ask — never guess**.
- Optionally pass `WORKLIST=<path-or-description>` to name the source instead of deriving one.
- This session writes **only** `WORKLIST_<project>.md` at the portfolio root and a chat breakdown;
  it makes no project changes. Conventions are in the bundled
  [project layout](../../project-layout.md).
- Resolve the **portfolio root** first, per the bundled [project layout](../../project-layout.md)
  §"Resolving the portfolio root" — an explicit `PORTFOLIO_ROOT=<path>` argument wins, else the
  library-parent, else the nearest qualifying CWD/ancestor; all portfolio-relative paths resolve
  against it.
