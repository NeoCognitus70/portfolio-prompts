---
name: derive-worklist
description: "PREPARE (without actioning) a worklist for one test-automation-portfolio project — orient from handover + backlog, derive and cross-check the items, write WORKLIST_<project>.md, and report a per-item breakdown for review. Use when planning work before a loop (\"prepare/plan a worklist for <project>\"). Read-only in the repo. NOT for executing the work (that is loop-worklist) or reviewing code (that is write-code-review)."
argument-hint: "<project-folder> [WORKLIST=<path-or-description>]"
---

Derive-a-worklist (no actioning) for a **test-automation-portfolio** project.

Read and follow the canonical prompt **`${CLAUDE_PLUGIN_ROOT}/derive-worklist.prompt.md`** (bundled at
this plugin's root), following the body below its `---` divider exactly.

- `PROJECT` = the project folder name the user supplied — a row in `${CLAUDE_PLUGIN_ROOT}/registry.yml`.
  If none was given, **ask — never guess**.
- Optionally pass `WORKLIST=<path-or-description>` to name the source instead of deriving one.
- This session writes **only** `WORKLIST_<project>.md` at the portfolio root and a chat breakdown;
  it makes no project changes. Conventions are in `${CLAUDE_PLUGIN_ROOT}/project-layout.md`.
