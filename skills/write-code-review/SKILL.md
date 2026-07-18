---
name: write-code-review
description: "Write a comprehensive, evidence-backed CODE REVIEW of one onboarded test-automation-portfolio project against its own backlog, into the repo's .review/ folder (architecture, SOLID, ISTQB test strategy, CI, dependency/security/licence). Use to review a named portfolio project. Takes the project folder name. For an EXTERNAL or unfamiliar repo with no PROJECT, use analyze-repo instead."
---

Write a comprehensive code review of a **test-automation-portfolio** project.

Read and follow the [canonical prompt](../../write-code-review.prompt.md), following the body below
its `---` divider exactly.

- `PROJECT` = the project folder name the user supplied — a row in the bundled
  [registry](../../registry.yml).
  If none was given, **ask — never guess**.
- The review is written into the project's `.review/` folder (or its registry-recorded deviation) and
  makes no implementation changes. Conventions are in the bundled
  [project layout](../../project-layout.md).
- Resolve the **portfolio root** first, per the bundled [project layout](../../project-layout.md)
  §"Resolving the portfolio root" — an explicit `PORTFOLIO_ROOT=<path>` argument wins, else the
  library-parent, else the nearest qualifying CWD/ancestor; all portfolio-relative paths resolve
  against it.
