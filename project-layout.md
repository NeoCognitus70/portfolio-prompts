# Project Layout Contract

What a project must provide to participate in the `portfolio-prompts` library, and the
portfolio-level conventions the prompts rely on. Prompts cite this contract instead of repeating
paths; if a project deviates, fix the project or record the deviation in the README registry —
do not fork the prompts.

**Before applying any default path below, read the project's registry row in the README.**
Recorded deviations override the defaults (e.g. a project whose backlog lives at
`DOCS/.planning/backlog.md` is fully onboarded — the "stop, not onboarded" rule applies only
when neither the default path nor a registry-recorded alternative exists).

## The `PROJECT` parameter

Every prompt is invoked against one project, named as `PROJECT=<folder name at the portfolio
root>` (e.g. `PROJECT=magento-checkout-automation`). The README's **project registry** lists the
valid values. If an invocation does not name a `PROJECT`, the agent must **ask — never guess**,
and never infer it from which files happen to be open.

**Exception — portfolio-scoped orchestration prompts** (`derive-all-worklists.prompt.md`,
`loop-all-worklists.prompt.md`, `review-all-projects.prompt.md`): these take the whole registry as
their target and need no `PROJECT=`; each sub-agent they launch receives a single `PROJECT=` and
is bound by this contract as normal.

## Required in-repo structure

A participating project (`test-automation-portfolio/{PROJECT}/`) must have:

- Its **own git repository** (the prompts run `git -C {PROJECT} ...` and `gh` from inside it).
- **`docs/backlog.md`** — the project's **source of truth** for item status and priorities.
  Scaffold from `templates/backlog.template.md` if missing; a project without a backlog is not
  onboarded, and prompts must stop and say so rather than improvise.

## Recommended in-repo structure

Created on first need if absent (scaffold from `templates/` where a template exists):

- `docs/implementation-logs/` + `docs/templates/implementation-log.template.md` — append-only
  session history (used by write-implementation-log).
- `docs/adr/` — architecture decision records.
- `CHANGELOG.md` — user-visible changes.
- `.review/` — created by write-code-review on first review.

## Validation gates

Prompts that gate commits (loop-worklist, write-code-review) resolve a project's gates in this
order — first hit wins:

1. A **`Gates`** section in the project's `docs/project-contract.md`, if that file exists
   (one command per line, all must pass).
2. **Gates recorded in the project's README registry row** (e.g. "per `ci.yml`" for a
   multi-stack repo with no root `package.json` — run the CI job steps for the stack(s) touched).
3. **`npm run verify`** in the project's **root** `package.json`, if defined.
4. Stack defaults, stated explicitly in the report: `npx tsc --noEmit` for TypeScript projects,
   plus `npx cucumber-js --profile default --dry-run` where the project uses the **cucumber-js
   runner** (a `cucumber.js`/`cucumber.{json,yaml}` config exists). A `features/` folder of
   Gherkin alone does not imply cucumber-js — **playwright-bdd** projects validate step binding
   via their `bddgen` script instead (generation fails on undefined steps).
   In a **multi-stack repo** (no root toolchain config), run the stack defaults **inside the
   touched stack's directory**, never at the repo root — a root `npx tsc --noEmit` with no root
   `tsconfig.json` fails spuriously.
5. Otherwise: **ask the user** what "validated" means for this project.

## Portfolio-level conventions (outside the repos)

- **Handovers:** `session-notes/{PROJECT}_session-notes_v{N}_{YYYYMMDD}T{HHMM}Z.{md,html}` —
  the filename prefix is the namespace. Version sequences are **per project**: "highest version"
  comparisons are made only among files sharing the `{PROJECT}_` prefix, never across the folder.
  **Compare versions numerically, not lexically** — a plain filename sort orders `v9` *after*
  `v13`; parse `{N}` as a number before deciding which file is latest.
- **Worklists:** `WORKLIST_{PROJECT}.md` at the portfolio root — one worklist per project; a
  `/loop` binds to exactly one.
- **Shared templates:** `templates/` at the portfolio root — project-agnostic scaffolding
  (backlog, implementation log, code review, ADR, etc.).
- **Prompts:** this folder (`portfolio-prompts/`), its own git repository.

## Working norms (universal)

- **All changes to a project's `main` go via branch + PR** — the harness blocks direct pushes,
  including docs-only ones (confirmed 2026-06-10). The user authorises each merge.
- Project-specific norms and gotchas live in the project's latest handover ("Durable lessons")
  and its `docs/project-contract.md` if present — prompts read them there, never hardcode them.
- en-GB spelling in all written artefacts.
