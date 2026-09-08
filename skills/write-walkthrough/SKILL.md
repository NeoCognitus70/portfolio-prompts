---
name: write-walkthrough
description: "Record a structured, evidence-grounded WALKTHROUGH of a completed batch of work — changes implemented, verification and test evidence, operational state, and recommended next actions — into docs/walkthroughs/. Takes a project folder name, or PROJECT=root for portfolio-level work spanning several repositories. Use at the end of a discrete batch. NOT the immutable per-task development record (that is write-implementation-log) and NOT the end-of-session handover (that is write-handover)."
---

Write a walkthrough document for a **test-automation-portfolio** project, or for the portfolio itself.

Read and follow the [canonical prompt](../../write-walkthrough.prompt.md), following the body below
its `---` divider exactly.

- `PROJECT` = the project folder name the user supplied — a row in the bundled
  [registry](../../registry.yml) — or the literal `PROJECT=root` for a cross-portfolio batch.
  If none was given, **ask — never guess**.
- Gather ground truth from Git and the run output **before** writing; the prompt forbids guessing or
  inventing evidence, and every claim of a passing gate must cite a real command, run id, or commit.
- Output location follows the target: `PROJECT=root` writes to `docs/walkthroughs/` at the portfolio
  root; a project writes to that repository's own `docs/walkthroughs/`. Walkthroughs are immutable —
  use a new date and slug per batch rather than overwriting an existing file.
- Resolve the **portfolio root** first, per the bundled [project layout](../../project-layout.md)
  §"Resolving the portfolio root" — an explicit `PORTFOLIO_ROOT=<path>` argument wins, else the
  library-parent, else the nearest qualifying CWD/ancestor; all portfolio-relative paths resolve
  against it.
