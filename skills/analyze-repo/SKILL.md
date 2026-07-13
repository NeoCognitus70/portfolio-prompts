---
name: analyze-repo
description: "Produce a deep, evidence-based, pedagogical technical report on ANY repository (by URL or local path) — purpose, architecture, data flow, SOLID, an ISTQB-aligned test-strategy review, and a dependency/security/licence pass. The zero-config pilot: takes NO project and is not registry-bound. Use to understand, evaluate, audit, or decide whether to adopt an unfamiliar/external codebase. For an onboarded portfolio project reviewed against its own backlog, use write-code-review instead."
argument-hint: "<repo-url-or-path> [summary|standard|deep-dive]"
---

Analyse an arbitrary repository and produce a standalone technical report. This is the **zero-config**
skill — no `PROJECT`, no registry, no contract.

Read and follow the canonical prompt **`${CLAUDE_PLUGIN_ROOT}/github-repo-analysis-prompt.md`** (bundled
at this plugin's root), following the body below its `---` divider exactly.

- Supply the **repository** the user named (a Git URL or a local path). If none was given, ask for it.
- Optional **depth**: `summary` | `standard` | `deep-dive` (default `standard`).
- Acquire the code before writing any finding; if you cannot access it, stop and say so. Write the
  report to `REPO_ANALYSIS_<repo-name>_<YYYYMMDD>.md` unless the user asks for a chat report.
