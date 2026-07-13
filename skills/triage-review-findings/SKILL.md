---
name: triage-review-findings
description: "TRIAGE one named portfolio code review into a prioritised, deduplicated candidate worklist for user approval. Takes a project and REVIEW=<path>; does not action findings or change the project repo."
argument-hint: "<project-folder> REVIEW=<review-path>"
---

Triage one named code review into an approved worklist without actioning its findings.

Read and follow the canonical prompt
**`${CLAUDE_PLUGIN_ROOT}/triage-review-findings.prompt.md`** (bundled at this plugin's root),
following the body below its `---` divider exactly.

- `PROJECT` = the registered project folder supplied by the user; ask if it is missing.
- `REVIEW` = the named review directory or main index; ask if it is missing and never pick one.
- First present deduplicated candidates and stop. Only after explicit approval may the workflow
  write `WORKLIST_<project>.md`; it never changes or actions the project repository.
