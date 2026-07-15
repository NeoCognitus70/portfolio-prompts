---
name: write-code-review
description: "Write a comprehensive, evidence-backed CODE REVIEW of one onboarded test-automation-portfolio project against its own backlog, into the repo's .review/ folder (architecture, SOLID, ISTQB test strategy, CI, dependency/security/licence). Use for \"review the <project> project\". Takes the project folder name. For an EXTERNAL/unfamiliar repo with no PROJECT, use analyze-repo instead."
argument-hint: "<project-folder> [PORTFOLIO_ROOT=<path>]"
---

Write a comprehensive code review of a **test-automation-portfolio** project.

Read and follow the canonical prompt **`${CLAUDE_PLUGIN_ROOT}/write-code-review.prompt.md`** (bundled
at this plugin's root), following the body below its `---` divider exactly.

- `PROJECT` = the project folder name the user supplied — a row in `${CLAUDE_PLUGIN_ROOT}/registry.yml`.
  If none was given, **ask — never guess**.
- The review is written into the project's `.review/` folder (or its registry-recorded deviation) and
  makes no implementation changes. Conventions are in `${CLAUDE_PLUGIN_ROOT}/project-layout.md`.
- Resolve the **portfolio root** first, per `${CLAUDE_PLUGIN_ROOT}/project-layout.md`
  §"Resolving the portfolio root" — an explicit `PORTFOLIO_ROOT=<path>` argument wins, else the
  plugin-parent, else the CWD; all portfolio-relative paths resolve against it.
