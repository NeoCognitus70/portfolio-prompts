---
name: loop-worklist
description: "EXECUTE a prepared worklist for one test-automation-portfolio project, one item per iteration (implement, validate, verify, commit, record). MUTATING — it changes the repo and opens a PR. Normally driven by the /loop command. Use when actioning WORKLIST_<project>.md (\"work through the worklist for <project>\"). NOT for preparing the list (that is derive-worklist)."
argument-hint: "<project-folder> [WORKLIST=<path-or-description>]"
---

Execute one iteration of a work loop against a **test-automation-portfolio** project. **Mutating:**
it implements, validates, verifies, commits, and opens a PR (never merges).

Read and follow the canonical prompt **`${CLAUDE_PLUGIN_ROOT}/loop-worklist.prompt.md`** (bundled at
this plugin's root), following the body below its `---` divider exactly.

- `PROJECT` = the project folder name the user supplied — a row in `${CLAUDE_PLUGIN_ROOT}/registry.yml`.
  A loop binds to exactly one project. If none was given, **ask — never guess**.
- Prefer driving this via `/loop` (self-pacing, one item per wake-up). Gates must pass before every
  commit; apply the universal working norms in `${CLAUDE_PLUGIN_ROOT}/project-layout.md`.
