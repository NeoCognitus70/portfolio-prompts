# Skills — the portfolio-prompts plugin

This repo is a **Claude Code plugin** (`.claude-plugin/plugin.json`). Each skill here is a
description-triggered entry point that **delegates to the canonical `*.prompt.md`** at the repo root —
so the prompt is the single source of truth and the skill just adds triggering + argument handling
(PP-24). `project` is an argument to the single-project skills; `onboard-project` instead takes the
prospective folder that is not registered yet.

## Skills

| Skill | Delegates to | Arg | Notes |
|---|---|---|---|
| `onboard-project` | `onboard-project.prompt.md` | `<project> [GITHUB=<owner/repo>]` | Explicit-only; staged scaffold + registry draft PRs |
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

## Scope and portfolio-root resolution (PP-28)

- Skills load the registry and contract from the plugin (`${CLAUDE_PLUGIN_ROOT}/registry.yml`,
  `project-layout.md`), so the **project is genuinely an argument**.
- Every portfolio-bound skill resolves the **portfolio root** per `project-layout.md`
  §"Resolving the portfolio root" before following its prompt: an explicit
  `PORTFOLIO_ROOT=<path>` argument wins, else the parent of `${CLAUDE_PLUGIN_ROOT}` when it
  qualifies (a workspace checkout — the plugin root *is* `<portfolio root>/portfolio-prompts`),
  else the CWD as the documented fallback. A directory qualifies iff it contains
  `portfolio-prompts/registry.yml`; if nothing qualifies the skill **stops and asks** rather than
  guessing. All portfolio-relative paths (`session-notes/`, `{PROJECT}/docs/backlog.md`,
  `WORKLIST_{PROJECT}.md`, `templates/`) resolve against that root, so the session no longer has
  to be rooted at the portfolio. `analyze-repo` needs none of this (zero-config, any repo).
- The bundled tools are root-independent — each locates the library from its own file path, and
  `workspace_preflight.py` accepts `--workspace`/`--registry` overrides — so prompts invoke them
  by absolute plugin path from any CWD.
- Verified 2026-07-15 from a session rooted **outside** the portfolio (see PP-28 in
  [`../docs/backlog.md`](../docs/backlog.md)): plugin-parent resolution located the root, and the
  `resume-session` orientation reads (manifest `latest` → handover pair → project backlog) plus
  the workspace preflight all resolved correctly. Live auto-trigger of the *installed* plugin
  remains the separate PP-27 check.
- `onboard-project` is the prospective-project exception: it inspects an existing local checkout,
  stops for approval, and stages target-scaffold then registry PRs. Registry regeneration remains
  the responsibility of `tools/render-registry.py` (PP-23), which the canonical prompt invokes.
