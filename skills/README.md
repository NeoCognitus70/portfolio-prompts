# Skills — the portfolio-prompts plugin

This repo is a **Claude Code plugin** (`.claude-plugin/plugin.json`). Each skill here is a
description-triggered entry point that **delegates to the canonical `*.prompt.md`** at the repo root —
so the prompt is the single source of truth and the skill just adds triggering + argument handling
(PP-24). `project` is an argument to the single-project skills.

## Skills

| Skill | Delegates to | Arg | Notes |
|---|---|---|---|
| `resume-session` | `resume-session.prompt.md` | `<project>` | Start of a session |
| `derive-worklist` | `derive-worklist.prompt.md` | `<project>` | Plan a worklist (no actioning) |
| `loop-worklist` | `loop-worklist.prompt.md` | `<project>` | Execute a worklist (mutating; `/loop`) |
| `write-implementation-log` | `write-implementation-log.prompt.md` | `<project>` | After a dev task |
| `write-code-review` | `write-code-review.prompt.md` | `<project>` | Review an onboarded project |
| `triage-review-findings` | `triage-review-findings.prompt.md` | `<project> REVIEW=<path>` | Review findings → approved worklist; no actioning |
| `write-handover` | `write-handover.prompt.md` | `<project>` | End of a session |
| `close-project` | `close-project.prompt.md` | `<project>` | Final session |
| `derive-all-worklists` | `derive-all-worklists.prompt.md` | — | Fan-out, no actioning |
| `review-all-projects` | `review-all-projects.prompt.md` | — | Fan-out, evidence-only |
| `loop-all-worklists` | `loop-all-worklists.prompt.md` | — | Fan-out, **mutating — explicit only** |
| `portfolio-status` | `portfolio-status.prompt.md` | — | Whole-portfolio status, strictly read-only |
| `analyze-repo` | `github-repo-analysis-prompt.md` | `<repo> [depth]` | Zero-config; any repo, no registry |

`analyze-repo` is the **zero-config pilot** — it needs no `project`, registry, or contract, so it is
the one skill that already runs against any repository unchanged.

## Install

```bash
# from an interactive Claude Code session, add this repo as a plugin marketplace/source, e.g.
/plugin marketplace add NeoCognitus70/portfolio-prompts
/plugin install portfolio-prompts
```

Or point Claude Code at a local checkout of this repo as a plugin. Once installed, the skills appear
by name (e.g. `/resume-session calculator-screenplay-bdd`) and auto-trigger on their descriptions.

## Scope and current portability caveat

- Skills load the registry and contract from the plugin (`${CLAUDE_PLUGIN_ROOT}/registry.yml`,
  `project-layout.md`), so the **project is genuinely an argument**.
- The delegated lifecycle prompts still resolve **portfolio-relative paths** (`session-notes/`,
  `{PROJECT}/docs/backlog.md`, `WORKLIST_{PROJECT}.md`) against the **current working directory**, so
  the single-project and fan-out skills are built for a session whose CWD is the
  **test-automation-portfolio root**. Making those paths fully project-agnostic (run the lifecycle on
  any workspace) is follow-on work; `analyze-repo` already has no such dependency.
- `onboard-project` (scaffold a new registry row + backlog) is **not** shipped here — it is tracked
  separately as backlog item **PP-20**; registry regeneration is `tools/render-registry.py` (PP-23),
  not a skill.
