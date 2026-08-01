# Portfolio Prompts

Reusable session prompts for the **test-automation-portfolio** projects.

This folder lives at the portfolio root, **outside** the individual project repos, and is tracked
as its **own git repository** (`portfolio-prompts`) — the prompt library has history without
polluting any project's history.

## Start here

As a human reader, start with the [prompt lifecycle and table](#prompts), choose the workflow that
matches your job, then use its example under [Invocation](#invocation); if you installed the plugin,
use the [skills entry points](#use-as-plugin-skills-claude-code-and-codex) instead. The machine and maintainer
contract is separate: [project-layout.md](project-layout.md) defines paths, gates, worklists, and
working norms, while [`registry.yml`](registry.yml) is the source tooling loads — you do not need to
absorb either before choosing and running a prompt.

## The `PROJECT` parameter

Every project-bound lifecycle prompt is invoked against **one registered project**, named as
`PROJECT=<folder name>` from the [registry below](#project-registry) (state it in the first line you
paste, e.g. `PROJECT=calculator-screenplay-bdd`). `onboard-project` is the setup exception: its
`PROJECT` names an existing local folder that is not registered yet. The full rule — including
portfolio-scoped prompts that need no `PROJECT=` — and all paths, globs, and conventions are
defined once in [project-layout.md](project-layout.md). If no `PROJECT` is given where one is
required, the agent must ask, never guess.

## Project registry

<!-- REGISTRY:START (generated from registry.yml by tools/render-registry.py — do not edit between the markers) -->
| `PROJECT` | GitHub | Status | Notes |
|---|---|---|---|
| `magento-checkout-automation` | GBrooks1970/magento-checkout-automation | Resting | Reference project, resting with zero required backlog items after Items #1..#15 were delivered. Chromium remains the required CI gate; Firefox and WebKit stay non-blocking until each records three consecutive eligible 12/12 runs with zero recovery telemetry (v20 snapshot: Firefox 1/3, WebKit 0/3). Latest handover v20 in `session-notes/`; optional proposals live in `docs/planning/`. Gates: `npm run verify`. |
| `hand-baked-screenplay-pattern` | NeoCognitus70/hand-baked-screenplay-pattern | Resting | Stable teaching library with zero required backlog items. Material in `planning/` remains optional until promoted into the backlog. Gates: `npm run verify`. |
| `calculator-screenplay-bdd` | NeoCognitus70/calculator-screenplay-bdd | Resting | Stable consumer example with zero required backlog items. Gates: `npm run verify`. Depends on `hand-baked-screenplay-pattern` — prepare:screenplay installs and builds inside the sibling checkout (provider-first). |
| `gb.automation.smoketests.sudoku.poc` | GBrooks1970/gb.automation.smoketests.sudoku.poc | Active | Multi-stack POC with its own doc system; run stack defaults inside the touched stack's directory, never at the repo root. Gates: per `ci.yml` — stack jobs (demoapp001 cypress/typescript; demoapp002 pytest/python; demoapp003 specflow/csharp) + `.batch/*.ps1` parity; run the job(s) for the stack(s) touched. Deviations: backlog `DOCS/.planning/backlog.md`, implementation-logs `DOCS/.implementation-logs/`, reviews `DOCS/.review/`, templates `DOCS/.templates/`. |
| `bfx-ws-screenplay` | GBrooks1970/bfx-ws-screenplay | Active | In-repo `SPECIFICATION.md` is normative (SDD) — one SPEC unit at a time; feature file reviewed before framework code; deviations need an ADR change note. `test:smoke` hits the live public API; `environment-blocked` outcomes are platform maintenance, not failures; `@extended` runs nightly only. Gates: `npm run typecheck`, `npm run lint`, `npm run test:smoke`. |
| `orangehrm-pim-automation` | GBrooks1970/orangehrm-pim-automation | Resting | OrangeHRM PIM add-employee E2E (Serenity/JS + Playwright + Cucumber). Backlog is a simple table (not the scored template). All six backlog items are closed; Item #4 retains an accepted demo-fixture caveat but no required follow-up. Live docs: gbrooks1970.github.io/orangehrm-pim-automation. Gates: per `ci.yml` — static `npx tsc --noEmit`; E2E `docker compose up -d --wait` then `npm test`. CI (Node 20) also builds Serenity living docs and deploys Pages. |
| `markdown-renderer` | GBrooks1970/markdown-renderer | Resting (product) | A shipped product, not a Screenplay test suite: a static, offline, browser-based Markdown viewer with its own suite. Currently 0 outstanding (FR-1..FR-11 shipped and live), so a derive honestly returns nothing actionable. Treat its tests as the product's own suite, not portfolio Screenplay conventions. Live demo: gbrooks1970.github.io/markdown-renderer/. Gates: `npm run verify`. |
| `mobile-forex-automation` | GBrooks1970/mobile-forex-automation | Resting | Mobile-web test-automation showcase: a deterministic forex demo SUT with Playwright Pixel and iPhone emulation, Screenplay journeys, and a Vitest-tested P&L core. The MF-01..MF-14 roadmap is complete with zero required backlog items. Live demo: gbrooks1970.github.io/mobile-forex-automation/. Gates: `npm run verify`. |
| `parabank-bank-automation` | GBrooks1970/parabank-bank-automation | Active | Ninth portfolio project. ParaBank (Parasoft, Apache-2.0) as a pinned, Docker-backed banking SUT (never committed here; fetched at build). Two lanes: Serenity/JS + Playwright + Cucumber UI journeys (A1-A5) and API-first stateful BDD with a portfolio-first REST-SOAP parity check (B1-B4); the current baseline is 14 API and 8 UI scenarios plus 17 SUT-independent unit tests. Phased delivery PB-P0..P5 and PB-CODEX-01..10 review remediation are complete; the project remains active for LOW risk maintenance in docs/backlog.md v19. PBR-03 is immediately actionable; PBR-01, PBR-02, PBR-04, and PBR-05 are trigger-gated. Decisions are in docs/decision-register.md (DR-PB-01..10); latest handover is v4 in session-notes/. Gates: per `ci.yml` — static `npm run typecheck`; E2E `pwsh ./scripts/build-sut.ps1; docker compose up -d; pwsh ./scripts/gate.ps1` then `npm run verify`. docs/project-contract.md is the first-hit gate source. npm run verify runs both lanes + smoke-safety + the Serenity report content check (needs Playwright Chromium and a JDK, both installed in CI); the boot gate precedes verify.. |
| `portfolio-prompts` | NeoCognitus70/portfolio-prompts | Meta (self-onboarded) | The prompt library itself. Single-project prompts (`resume-session`, `derive-worklist`, `loop-worklist`, `write-implementation-log`, `write-code-review`) may target `PROJECT=portfolio-prompts`. Not a target of the orchestration fan-outs. Gates: `python tools/check-library.py`. Deviations: backlog `portfolio-prompts/docs/backlog.md`. |
<!-- REGISTRY:END -->

> **Generated table — do not hand-edit.** The rows between the markers above are generated from
> [`registry.yml`](registry.yml) (the source of truth that tooling and skills load) by
> [`tools/render-registry.py`](tools/render-registry.py). To change a row, edit `registry.yml` and
> run `python tools/render-registry.py`; `--check` exits non-zero if the table is stale. See
> [project-layout.md](project-layout.md) §"Machine-readable registry".

**Lifecycle labels:** `Active` means the canonical backlog contains open work; `Resting` means it
has zero outstanding items; `Meta` identifies control-plane tooling. Lifecycle does not decide
fan-out eligibility: resting projects remain orchestration targets, while the separate
`orchestration_target` field is authoritative.

### Classified support repositories

`registry.yml` classifies `portfolio-landing`
([`GBrooks1970/portfolio`](https://github.com/GBrooks1970/portfolio)) as the active public
presentation surface. It is a support repository, not a registered test-automation `PROJECT=`,
and is explicitly excluded from orchestration fan-outs.

## Prompts

**Typical lifecycle** (single project):
`resume-session` -> `derive-worklist` -> `loop-worklist` -> `write-implementation-log` ->
`write-code-review` -> `write-handover` -> `close-project`.
The `run-project-cycle` **conductor** sequences a review-driven cycle of these steps end to end for
one project (`review -> triage -> loop -> log -> handover -> optional close`), with entry/exit gates
and owner checkpoints between stages; it delegates each stage to that stage's prompt and never
re-implements one.
Before a project's first lifecycle, `onboard-project` establishes its backlog/scaffold and registry
entry through staged PRs.
The three `*-all-*` orchestrators (`derive-all-worklists`, `loop-all-worklists`,
`review-all-projects`) fan the corresponding single-project step across the whole registry in one
pass. Each starts with the registry-driven read-only
[`workspace_preflight.py`](tools/workspace_preflight.py) safety report before launching any agent.
`portfolio-status` is a read-only portfolio snapshot outside the lifecycle, while
`github-repo-analysis-prompt.md` is general-purpose and not registry-bound (see below). After a
code review, `triage-review-findings` is the optional explicit route from one named review to the
next approved worklist.

| Prompt | When to use | What it does |
|---|---|---|
| [onboard-project.prompt.md](onboard-project.prompt.md) | Adding an existing local repository to the portfolio | Discovers and proposes the project's registry metadata, gates, backlog, and recommended scaffold; after explicit approval, publishes a target scaffold PR when needed, waits for it to merge, then publishes the generated registry-row PR — never merges either. |
| [write-handover.prompt.md](write-handover.prompt.md) | End of a session | Reconciles the project's `docs/backlog.md` (source of truth), then writes the next root-tracked `{PROJECT}_session-notes` handover pair (`.md` + generated `.html`) into `session-notes/`, superseding the previous version. |
| [resume-session.prompt.md](resume-session.prompt.md) | Start of a session | Loads the project's latest handover from `session-notes/` (or bootstraps from the backlog if none exists), cross-checks it against the backlog and the live repo, and proposes the resume point — then waits for confirmation. |
| [write-implementation-log.prompt.md](write-implementation-log.prompt.md) | After a dev task | Writes a new immutable implementation log into `{PROJECT}/docs/implementation-logs/` from the project's template. |
| [write-code-review.prompt.md](write-code-review.prompt.md) | Code review | Uses `templates/code-review.template.md` and the project's `docs/backlog.md` to write a comprehensive review into the repo's `.review/` folder. |
| [triage-review-findings.prompt.md](triage-review-findings.prompt.md) | Turning one named review into planned work | Reads the named review, deduplicates and backlog-checks its findings, presents prioritised candidates for explicit user approval, then writes the canonical root-tracked portfolio worklist without actioning the project. |
| [review-all-projects.prompt.md](review-all-projects.prompt.md) | Reviewing the whole portfolio | Orchestration fan-out, **evidence-only**: one parallel sub-agent per registry project, each following write-code-review for its project (review artefacts committed on a branch + PR, never merged); collates top findings into a cross-portfolio synthesis of common themes and highest-severity issues. |
| [derive-worklist.prompt.md](derive-worklist.prompt.md) | Preparing work before a loop | Derivation only, **no actioning**: orients from handover + backlog, derives and cross-checks the items, writes root-tracked `WORKLIST_{PROJECT}.md` in exactly the format the loop consumes, and reports a detailed per-item breakdown in chat for review. |
| [derive-all-worklists.prompt.md](derive-all-worklists.prompt.md) | Preparing work portfolio-wide | Orchestration fan-out, **no actioning**: one parallel sub-agent per registry project, each following derive-worklist for its project; collates all breakdowns, guard-stops, and user decisions into a single report. |
| [loop-worklist.prompt.md](loop-worklist.prompt.md) | Working through an ordered list of steps | Completes one worklist item per invocation or scheduled iteration — implement → validate → verify → commit → record — with root-tracked `WORKLIST_{PROJECT}.md` as its control record, stop conditions, and a closing report. Claude Code may repeat it with `/loop`; Codex uses an explicit skill invocation or a separately requested automation. |
| [run-project-cycle.prompt.md](run-project-cycle.prompt.md) | Running one project through a full improvement cycle | Single-project **conductor**, **mutating but checkpointed**: sequences `write-code-review → triage-review-findings → loop-worklist → write-implementation-log → write-handover → optional close-project` with entry/exit gates, a reconcile-before-starting preflight, and owner stops (triage candidate list, each merge, close). Delegates each stage to its canonical prompt; never re-implements a step and never a portfolio fan-out. |
| [loop-all-worklists.prompt.md](loop-all-worklists.prompt.md) | Actioning all prepared worklists at once | Orchestration fan-out that **mutates**: one sub-agent per project with unchecked worklist items, each executing loop-worklist iterations consecutively (commit + PR per its rules, never merging); coupled projects (e.g. calculator → hand-baked sibling build) share one sequential agent; collated report of commits, PRs, and blocked questions. |
| [portfolio-status.prompt.md](portfolio-status.prompt.md) | Checking the whole portfolio without changing it | Read-only aggregation across every registry project: local repo state, open backlog counts, latest handover, open PRs, and default-branch CI; reports unavailable evidence and registry-drift candidates instead of mutating or guessing. |
| [close-project.prompt.md](close-project.prompt.md) | Final session of a project | Verifies every public-facing claim the README makes, reconciles the backlog one last time, retires `WORKLIST_{PROJECT}.md`, and writes a terminal handover marked FINAL. |

### General-purpose (not registry-bound)

| Prompt | When to use | What it does |
|---|---|---|
| [github-repo-analysis-prompt.md](github-repo-analysis-prompt.md) | Understanding or evaluating **any** repository (typically one outside this portfolio) | Standalone, evidence-based, pedagogical technical report on a repo by URL or path: purpose, architecture, data flow, SOLID, an ISTQB-aligned test-strategy review, a dependency/security/licence pass, risks, and an improvement roadmap. Takes **no `PROJECT=`** and is not bound to the registry. Depth-controlled (`summary`/`standard`/`deep-dive`). For an *onboarded* portfolio project reviewed against its own backlog into `.review/`, use `write-code-review.prompt.md` instead. |

**Conventions the prompts rely on** (full detail in [project-layout.md](project-layout.md)):
- Every orchestration fan-out first runs `python <LIBRARY_ROOT>/tools/workspace_preflight.py` after
  resolving the absolute library root per [project-layout.md](project-layout.md);
  blocked targets are excluded/reported and warnings qualify the local evidence.
- Source of truth: `{PROJECT}/docs/backlog.md`.
- Handovers live in the root support repository's `../session-notes/`, named
  `{PROJECT}_session-notes_v{N}_{YYYYMMDD}T{HHMM}Z.{md,html}`. The Markdown/HTML pairs are tracked
  there; only generated `session-notes/manifest.json` remains untracked.
- Worklists live at the portfolio root as root-tracked `WORKLIST_{PROJECT}.md` control records;
  they never enter a target project's history.
- Implementation logs live **inside each repo** at
  `{PROJECT}/docs/implementation-logs/YYYY-MM-DD_short-slug.md` (tracked, append-only).
- Validation gates resolve: project contract → registry-row gates → `npm run verify` → stack
  defaults (run inside the touched stack's directory in multi-stack repos) → ask.

## Invocation

Two equivalent forms (both require `PROJECT=` — without it the agent stops and asks):

1. **Paste:** open the `.prompt.md`, copy the text below its `---` divider, prepend
   `PROJECT=<folder>`, and paste it to the agent.
2. **Read and follow:** point the agent at the file in a single chat message —
   `Read and follow portfolio-prompts/<name>.prompt.md using PROJECT=<folder>`.
   The agent reads the file and follows the body below the `---` divider; the header above the
   divider is guidance for humans, not part of the instructions.

**Exceptions:** one `loop-worklist.prompt.md` invocation completes one item. Claude Code may repeat
it via `/loop`; Codex may invoke its skill again or use a separately requested automation.
`onboard-project` requires a prospective local `PROJECT` that is **not yet** a registry row and may
take `GITHUB=<owner/repo>` when the checkout remote is not sufficient.
The portfolio-scoped orchestrators (`derive-all-worklists`, `loop-all-worklists`,
`review-all-projects`), the read-only `portfolio-status`, and the general-purpose
`github-repo-analysis-prompt.md` take **no `PROJECT=`** — the orchestrators and status prompt target
the whole registry, while the analysis prompt targets an arbitrary repo supplied by URL or path.

One example per prompt:

```text
Read and follow portfolio-prompts/onboard-project.prompt.md using PROJECT=mobile-forex-automation GITHUB=GBrooks1970/mobile-forex-automation

Read and follow portfolio-prompts/resume-session.prompt.md using PROJECT=calculator-screenplay-bdd

Read and follow portfolio-prompts/write-handover.prompt.md using PROJECT=hand-baked-screenplay-pattern

Read and follow portfolio-prompts/write-implementation-log.prompt.md using PROJECT=magento-checkout-automation

Read and follow portfolio-prompts/write-code-review.prompt.md using PROJECT=gb.automation.smoketests.sudoku.poc

Read and follow portfolio-prompts/triage-review-findings.prompt.md using PROJECT=calculator-screenplay-bdd REVIEW=.review/CODE_REVIEW_<agent>_v<N>_<timestamp>

Read and follow portfolio-prompts/derive-worklist.prompt.md using PROJECT=calculator-screenplay-bdd

Read and follow portfolio-prompts/derive-all-worklists.prompt.md

Read and follow portfolio-prompts/loop-all-worklists.prompt.md

Read and follow portfolio-prompts/review-all-projects.prompt.md

Read and follow portfolio-prompts/portfolio-status.prompt.md

Read and follow portfolio-prompts/loop-worklist.prompt.md using PROJECT=calculator-screenplay-bdd

/loop Read and follow portfolio-prompts/loop-worklist.prompt.md using PROJECT=calculator-screenplay-bdd

Read and follow portfolio-prompts/close-project.prompt.md using PROJECT=magento-checkout-automation

Read and follow portfolio-prompts/github-repo-analysis-prompt.md
```

(Optional parameters ride the same line, e.g.
`... derive-worklist.prompt.md using PROJECT=<folder> WORKLIST=<path-or-description>`.)

## Use as plugin skills (Claude Code and Codex)

This repo is a dual-platform plugin with Claude Code metadata in
`.claude-plugin/plugin.json`, Codex metadata in `.codex-plugin/plugin.json`, and a repo-scoped Codex
marketplace in `.agents/plugins/marketplace.json`. Every prompt has a
matching **skill** in [`skills/`](skills/README.md) that takes the project (or, for `analyze-repo`,
the repository) as user input. Each skill is a thin wrapper around its canonical `*.prompt.md`, so
the prompts remain the single source of truth.

Claude Code uses slash-style namespaced invocations such as
`/portfolio-prompts:resume-session calculator-screenplay-bdd`. Codex uses `$` skill mentions:

```text
Use $portfolio-prompts:resume-session for calculator-screenplay-bdd.
Use $portfolio-prompts:triage-review-findings for calculator-screenplay-bdd with REVIEW=<path>.
Use $portfolio-prompts:analyze-repo to analyse <repo-url-or-path> at standard depth.
```

`onboard-project` takes a prospective, unregistered project; `analyze-repo` is the zero-config
pilot (any repo, no registry). High-impact skills use platform-specific invocation policy plus
workflow confirmation gates. See [`skills/README.md`](skills/README.md) for installation,
invocation policy, and path-resolution details.
