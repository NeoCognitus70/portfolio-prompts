# Portfolio Prompts

Reusable session prompts for the **test-automation-portfolio** projects.

This folder lives at the portfolio root, **outside** the individual project repos, and is tracked
as its **own git repository** (`portfolio-prompts`) — the prompt library has history without
polluting any project's history.

## The `PROJECT` parameter

Every prompt is invoked against **one project**, named as `PROJECT=<folder name>` from the
registry below (state it in the first line you paste, e.g. `PROJECT=calculator-screenplay-bdd`).
If no `PROJECT` is given, the agent must ask, never guess. Paths, globs, and conventions the
prompts rely on are defined once in [project-layout.md](project-layout.md).

## Project registry

| `PROJECT` | GitHub | Status | Notes |
|---|---|---|---|
| `magento-checkout-automation` | GBrooks1970/magento-checkout-automation | Complete (2026-06-11) | Reference project; handovers at v13 |
| `hand-baked-screenplay-pattern` | NeoCognitus70/hand-baked-screenplay-pattern | Active | Gates: `npm run verify`; open work in `planning/` |
| `calculator-screenplay-bdd` | NeoCognitus70/calculator-screenplay-bdd | Active | Gates: `npm run verify`; **depends on the sibling `hand-baked-screenplay-pattern` checkout** (`prepare:screenplay`) |
| `gb.automation.smoketests.sudoku.poc` | GBrooks1970/gb.automation.smoketests.sudoku.poc | Active | Multi-stack POC with its own doc system. **Deviations:** backlog = `DOCS/.planning/backlog.md`; implementation logs = `DOCS/.implementation-logs/`; reviews = `DOCS/.review/`; in-repo templates = `DOCS/.templates/` (use these, not the portfolio `templates/`). Gates: no root `package.json` — per `ci.yml`, **three stack jobs** (demoapp001 TypeScript Cypress, demoapp002 Python Pytest, demoapp003 C# SpecFlow) plus the `.batch/*.ps1` parity scripts; run the job(s) for the stack(s) touched |
| `portfolio-prompts` | NeoCognitus70/portfolio-prompts | Meta (self-onboarded) | The prompt library itself. **Backlog:** `portfolio-prompts/docs/backlog.md`; gates: docs-only (link/grep checks — no build). Single-project prompts (`resume-session`, `derive-worklist`, `loop-worklist`, `write-implementation-log`, `write-code-review`) may target `PROJECT=portfolio-prompts`. **Not a target of the orchestration fan-outs** (`derive-all-worklists`, `loop-all-worklists`, `review-all-projects`) — those operate on the test-automation projects, not the library. |

## Prompts

| Prompt | When to use | What it does |
|---|---|---|
| [write-handover.prompt.md](write-handover.prompt.md) | End of a session | Reconciles the project's `docs/backlog.md` (source of truth), then writes the next `{PROJECT}_session-notes` handover (`.md` + generated `.html`) into `session-notes/`, superseding the previous version. |
| [resume-session.prompt.md](resume-session.prompt.md) | Start of a session | Loads the project's latest handover from `session-notes/` (or bootstraps from the backlog if none exists), cross-checks it against the backlog and the live repo, and proposes the resume point — then waits for confirmation. |
| [write-implementation-log.prompt.md](write-implementation-log.prompt.md) | After a dev task | Writes a new immutable implementation log into `{PROJECT}/docs/implementation-logs/` from the project's template. |
| [write-code-review.prompt.md](write-code-review.prompt.md) | Code review | Uses `templates/code-review.template.md` and the project's `docs/backlog.md` to write a comprehensive review into the repo's `.review/` folder. |
| [review-all-projects.prompt.md](review-all-projects.prompt.md) | Reviewing the whole portfolio | Orchestration fan-out, **evidence-only**: one parallel sub-agent per registry project, each following write-code-review for its project (review artefacts committed on a branch + PR, never merged); collates top findings into a cross-portfolio synthesis of common themes and highest-severity issues. |
| [derive-worklist.prompt.md](derive-worklist.prompt.md) | Preparing work before a loop | Derivation only, **no actioning**: orients from handover + backlog, derives and cross-checks the items, writes `WORKLIST_{PROJECT}.md` (portfolio root) in exactly the format the loop consumes, and reports a detailed per-item breakdown in chat for review. |
| [derive-all-worklists.prompt.md](derive-all-worklists.prompt.md) | Preparing work portfolio-wide | Orchestration fan-out, **no actioning**: one parallel sub-agent per registry project, each following derive-worklist for its project; collates all breakdowns, guard-stops, and user decisions into a single report. |
| [loop-worklist.prompt.md](loop-worklist.prompt.md) | Working through an ordered list of steps | Driven via the `/loop` command (not pasted). Completes one worklist item per iteration — implement → validate → verify → commit → record — tracked in `WORKLIST_{PROJECT}.md` (portfolio root), with stop conditions and a closing report. |
| [loop-all-worklists.prompt.md](loop-all-worklists.prompt.md) | Actioning all prepared worklists at once | Orchestration fan-out that **mutates**: one sub-agent per project with unchecked worklist items, each executing loop-worklist iterations consecutively (commit + PR per its rules, never merging); coupled projects (e.g. calculator → hand-baked sibling build) share one sequential agent; collated report of commits, PRs, and blocked questions. |
| [close-project.prompt.md](close-project.prompt.md) | Final session of a project | Verifies every public-facing claim the README makes, reconciles the backlog one last time, retires `WORKLIST_{PROJECT}.md`, and writes a terminal handover marked FINAL. |

### General-purpose (not registry-bound)

| Prompt | When to use | What it does |
|---|---|---|
| [github-repo-analysis-prompt.md](github-repo-analysis-prompt.md) | Understanding or evaluating **any** repository (typically one outside this portfolio) | Standalone, evidence-based, pedagogical technical report on a repo by URL or path: purpose, architecture, data flow, SOLID, an ISTQB-aligned test-strategy review, a dependency/security/licence pass, risks, and an improvement roadmap. Takes **no `PROJECT=`** and is not bound to the registry. Depth-controlled (`summary`/`standard`/`deep-dive`). For an *onboarded* portfolio project reviewed against its own backlog into `.review/`, use `write-code-review.prompt.md` instead. |

**Conventions the prompts rely on** (full detail in [project-layout.md](project-layout.md)):
- Source of truth: `{PROJECT}/docs/backlog.md`.
- Handovers live in `../session-notes/` (outside the repos, untracked), named
  `{PROJECT}_session-notes_v{N}_{YYYYMMDD}T{HHMM}Z.{md,html}` —
  versioned per project, UTC-timestamped, en-GB.
- Implementation logs live **inside each repo** at
  `{PROJECT}/docs/implementation-logs/YYYY-MM-DD_short-slug.md` (tracked, append-only).
- Validation gates resolve: project contract → registry-row gates → `npm run verify` → stack
  defaults (run inside the touched stack's directory in multi-stack repos) → ask.

## Invocation

Two equivalent forms (both require `PROJECT=` — without it the agent stops and asks):

1. **Paste:** open the `.prompt.md`, copy the text below its `---` divider, prepend
   `PROJECT=<folder>`, and paste it to the agent.
2. **Read and follow:** point the agent at the file in a single chat message —
   `Read and follow portfolio-prompts\<name>.prompt.md using PROJECT=<folder>`.
   The agent reads the file and follows the body below the `---` divider; the header above the
   divider is guidance for humans, not part of the instructions.

**Exceptions:** `loop-worklist.prompt.md` is driven via the `/loop` command, not a plain message.
The portfolio-scoped orchestrators (`derive-all-worklists`, `loop-all-worklists`,
`review-all-projects`) and the general-purpose `github-repo-analysis-prompt.md` take **no
`PROJECT=`** — the orchestrators target the whole registry, and the analysis prompt targets an
arbitrary repo supplied by URL or path.

One example per prompt:

```text
Read and follow portfolio-prompts\resume-session.prompt.md using PROJECT=calculator-screenplay-bdd

Read and follow portfolio-prompts\write-handover.prompt.md using PROJECT=hand-baked-screenplay-pattern

Read and follow portfolio-prompts\write-implementation-log.prompt.md using PROJECT=magento-checkout-automation

Read and follow portfolio-prompts\write-code-review.prompt.md using PROJECT=gb.automation.smoketests.sudoku.poc

Read and follow portfolio-prompts\derive-worklist.prompt.md using PROJECT=calculator-screenplay-bdd

Read and follow portfolio-prompts\derive-all-worklists.prompt.md

Read and follow portfolio-prompts\loop-all-worklists.prompt.md

Read and follow portfolio-prompts\review-all-projects.prompt.md

/loop Read and follow portfolio-prompts\loop-worklist.prompt.md using PROJECT=calculator-screenplay-bdd

Read and follow portfolio-prompts\close-project.prompt.md using PROJECT=magento-checkout-automation

Read and follow portfolio-prompts\github-repo-analysis-prompt.md
```

(Optional parameters ride the same line, e.g.
`... derive-worklist.prompt.md using PROJECT=<folder> WORKLIST=<path-or-description>`.)
