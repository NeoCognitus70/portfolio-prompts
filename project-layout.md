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

## Machine-readable registry — `registry.yml`

The README's project-registry table has a structured twin: **`portfolio-prompts/registry.yml`**.
It is the **machine-readable form** that tooling and skills load instead of parsing the README's
prose cells — one `defaults:` block plus one row per project (`github`, `status`, `gates`,
`deviations`, `couples_with`, `orchestration_target`, and `multi_stack`/`sdd`/`live_api`/`product`
flags). The README table is the human-readable view of the same data.

- **Resolution order is unchanged.** A project's `deviations:` override the `defaults:`, exactly as
  the prose rules in this contract describe; `orchestration_target: false` marks a row (currently
  only the meta `portfolio-prompts`) out of the `*-all-*` fan-outs.
- **Two views, kept in lockstep.** Until PP-23 automates generating the README table from
  `registry.yml`, **edit both together** whenever a project's row changes — the same discipline the
  handovers' `.md`/`.html` pair uses. `registry.yml` is the source tooling trusts; the README table
  is the source humans read.
- A skill resolves a project by loading its row:
  `backlog = row.deviations.backlog ?? defaults.backlog`,
  `gates = first-hit(defaults.gate_cascade, row.gates)`,
  `targets = projects where orchestration_target`.

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

### Project contract (optional) — `docs/project-contract.md`

A project may pin its gates and norms in `docs/project-contract.md`. When present it is the
**first-checked gate source** (above the registry row) and the home of project-specific working
norms a successor must respect. Minimal skeleton:

```text
# Project Contract — <project name>

## Gates
npm run verify        # one command per line; all must pass before a commit is gated green
npx tsc --noEmit

## Working norms
- <project-specific norm or gotcha, e.g. "explicit waits on JS-framework renders">
```

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

### Worklist file format (canonical)

`WORKLIST_{PROJECT}.md` is the loop's memory: `derive-worklist` writes it, and `loop-worklist`
reads it first and updates it last each iteration. It lives at the portfolio root (untracked,
outside the repos) — one worklist per project; a `/loop` binds to exactly one. Both prompts use
**exactly** this format — cite this section rather than restating it:

- A short **header** naming the project, the derivation source(s) (review version, backlog
  version, or a given `WORKLIST`), and the date — so a later session can judge staleness.
- **One line per item**, in execution order (severity/priority first, then dependency ordering —
  an item that unblocks another precedes it):
  `- [ ] <id> — <one-line description> — <source ref>`
- Beneath each item line: its **acceptance criteria** (what "verified" means) and whether it is
  **docs-only** or **code**.
- The loop checks an item off as `- [x]` with its commit hash and a one-line outcome; an item it
  cannot complete is marked `BLOCKED (reason)`.

Minimal example:

```text
# Worklist — example-project
**Project:** example-project  **Derived:** 2026-06-17  **Source:** code review v2 (HIGH -> LOW)

- [ ] EX-01 — Scope the decline-message selector to the checkout messages region — review R-05 (HIGH)
  - Acceptance: the selector matches only within the messages region; targeted run green. **Code.**
- [ ] EX-02 — Correct the README smoke-count claim to match the dry-run — review R-07 (LOW)
  - Acceptance: README count equals `--profile smoke --dry-run`; no other doc states the old count. **Docs-only.**
```

### Orchestration fan-out (shared conventions)

The portfolio-scoped orchestrators (`derive-all-worklists`, `loop-all-worklists`,
`review-all-projects`) all fan out one sub-agent per target project and collate a report. These
conventions are common to all three — each orchestrator cites this section and adds only its
**mode-specific deltas** (no-actioning / mutating / evidence-only):

- **No `PROJECT=` for the orchestrator** (it targets the registry); every sub-agent it launches
  receives a single `PROJECT=` and is bound by this contract as normal.
- **Self-contained sub-agent prompts.** Sub-agents start with no conversation context — each
  launch prompt must carry everything the sub-agent needs (working directory, the `Read and
  follow ... using PROJECT=<folder>` line, and the mode-specific rules), not rely on context.
- **One sub-agent per project; never two agents on the same project or the same working tree.**
  Coupled projects (per the registry coupling notes) share **one sequential agent** that works
  them in dependency order (provider/library first, consumer second).
- **Launch a wave's agents in the same turn** (parallel). After partitioning, confirm the count:
  the number of agents launched must equal the number of targets (including any sequential
  coupled agent) — a missing agent is a silent gap.
- **Unattended:** wherever a sub-prompt says to ask the user, the sub-agent must **not wait** —
  record the question and proceed or stop per its own mode, carrying the question into its report.
- **The sub-agent's final message is the only thing returned to the orchestrator** — it must be
  the sub-prompt's reporting block (or stop report) in full.
- **Sequential fallback:** if the environment cannot launch sub-agents, run the sub-prompt for each
  project **sequentially yourself**, in registry/dependency order — the per-project writes then
  become yours. Do not silently skip projects.
- **Re-run a failed agent at most once**, and never re-launch one that may have left a dirty tree
  without reporting the state first. **Relay findings faithfully** — never round up a reported
  problem, skipped validation, or failure to "all fine".

## Working norms (universal)

- **All changes to a project's `main` go via branch + PR** — the harness blocks direct pushes,
  including docs-only ones (confirmed 2026-06-10). The user authorises each merge.
- Project-specific norms and gotchas live in the project's latest handover ("Durable lessons")
  and its `docs/project-contract.md` if present — prompts read them there, never hardcode them.
- en-GB spelling in all written artefacts.
