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
| `gb.automation.smoketests.sudoku.poc` | GBrooks1970/gb.automation.smoketests.sudoku.poc | Active | Multi-stack POC with its own doc system. **Deviations:** backlog = `DOCS/.planning/backlog.md`; implementation logs = `DOCS/.implementation-logs/`; reviews = `DOCS/.review/`; in-repo templates = `DOCS/.templates/` (use these, not the portfolio `templates/`). Gates: no root `package.json` — per `ci.yml` (demoapp001: `npm run build` + `lint` + `test:api` + `test` in `demo-apps/demoapp001-typescript-cypress/`, plus the `.batch/*.ps1` parity scripts) |

## Prompts

| Prompt | When to use | What it does |
|---|---|---|
| [write-handover.prompt.md](write-handover.prompt.md) | End of a session | Reconciles the project's `docs/backlog.md` (source of truth), then writes the next `{PROJECT}_session-notes` handover (`.md` + generated `.html`) into `session-notes/`, superseding the previous version. |
| [resume-session.prompt.md](resume-session.prompt.md) | Start of a session | Loads the project's latest handover from `session-notes/` (or bootstraps from the backlog if none exists), cross-checks it against the backlog and the live repo, and proposes the resume point — then waits for confirmation. |
| [write-implementation-log.prompt.md](write-implementation-log.prompt.md) | After a dev task | Writes a new immutable implementation log into `{PROJECT}/docs/implementation-logs/` from the project's template. |
| [write-code-review.prompt.md](write-code-review.prompt.md) | Code review | Uses `templates/code-review.template.md` and the project's `docs/backlog.md` to write a comprehensive review into the repo's `.review/` folder. |
| [loop-worklist.prompt.md](loop-worklist.prompt.md) | Working through an ordered list of steps | Driven via the `/loop` command (not pasted). Completes one worklist item per iteration — implement → validate → verify → commit → record — tracked in `WORKLIST_{PROJECT}.md` (portfolio root), with stop conditions and a closing report. |
| [close-project.prompt.md](close-project.prompt.md) | Final session of a project | Verifies every public-facing claim the README makes, reconciles the backlog one last time, retires `WORKLIST_{PROJECT}.md`, and writes a terminal handover marked FINAL. |

**Conventions the prompts rely on** (full detail in [project-layout.md](project-layout.md)):
- Source of truth: `{PROJECT}/docs/backlog.md`.
- Handovers live in `../session-notes/` (outside the repos, untracked), named
  `{PROJECT}_session-notes_v{N}_{YYYYMMDD}T{HHMM}Z.{md,html}` —
  versioned per project, UTC-timestamped, en-GB.
- Implementation logs live **inside each repo** at
  `{PROJECT}/docs/implementation-logs/YYYY-MM-DD_short-slug.md` (tracked, append-only).
- Validation gates resolve: project contract → `npm run verify` → stack defaults → ask.

Usage: open the relevant `.prompt.md`, copy the text below its `---` divider, prepend
`PROJECT=<folder>`, and paste it to the agent.
**Exception:** `loop-worklist.prompt.md` is invoked via the `/loop` command (see the invocation
examples in its header), not pasted.
