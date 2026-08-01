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

Every project-bound lifecycle prompt is invoked against one registered project, named as
`PROJECT=<folder name at the portfolio root>` (e.g. `PROJECT=magento-checkout-automation`). The
README's **project registry** lists the valid values. If an invocation does not name a required
`PROJECT`, the agent must **ask — never guess**, and never infer it from which files happen to be
open.

**Onboarding exception:** `onboard-project.prompt.md` requires `PROJECT=`, but it names a
prospective local folder that must **not** already be a registry row. The prompt verifies that
folder and stages the required project/registry PRs before it becomes a valid lifecycle target.

**Portfolio-scoped exception:** `derive-all-worklists.prompt.md`, `loop-all-worklists.prompt.md`,
`review-all-projects.prompt.md`, and `portfolio-status.prompt.md` take the whole registry as their
target and need no `PROJECT=`. Each sub-agent launched by an orchestration prompt receives one
registered `PROJECT=` and is bound by this contract as normal. The standalone
`github-repo-analysis-prompt.md` is general-purpose and not registry-bound.

## Resolving the library root

The **library root** is the directory containing this `project-layout.md`, `registry.yml`, the
canonical prompt files, and `tools/`. Resolve it from the source file being followed, not from a
product-specific environment variable:

1. When a skill is active, its library root is two directories above that skill's `SKILL.md`.
2. When a canonical prompt is read directly, its library root is the directory containing that
   prompt.

Validate that both `registry.yml` and `project-layout.md` exist there before using the root. Skill
links are deliberately relative so the same wrappers work in Claude Code and Codex, including when
Codex loads an installed copy from its plugin cache. Wherever an operational prompt says
`<LIBRARY_ROOT>`, substitute this resolved **absolute** path; do not pass the placeholder literally.

## Resolving the portfolio root

Every portfolio-relative location in this contract and the prompts — `{PROJECT}/`,
`session-notes/`, `WORKLIST_{PROJECT}.md`, `templates/`, and `portfolio-prompts/` itself —
resolves against a single directory, the **portfolio root**. A directory **qualifies** as the
portfolio root iff it contains `portfolio-prompts/registry.yml` (a workspace checkout of this
library with its registry). Resolve the root once at the start of a session — first hit wins,
skipping any candidate that does not qualify:

1. **Explicit argument** — `PORTFOLIO_ROOT=<absolute path>` in the invocation (every
   portfolio-bound skill accepts it). Use this when the session is rooted anywhere other than
   the portfolio.
2. **Library-parent** — when the resolved library root is the workspace checkout at
   `<portfolio root>/portfolio-prompts`, its parent qualifies. A standalone clone or a Codex plugin
   cache does not qualify here — fall through.
3. **CWD/ancestor fallback** — the current working directory, then each ancestor up to the
   filesystem root; take the nearest candidate that qualifies. This covers sessions launched at
   the portfolio root or inside one of its project checkouts.

If no candidate qualifies, **stop and ask — never guess** a root, and never write
portfolio-relative artefacts against an unvalidated directory. Wherever a prompt says "at the
portfolio root" or "from the portfolio root", it means the root resolved by this section;
orchestrators pass it to sub-agents as the absolute working directory. The bundled tools are
already root-independent — each locates the library from its own file path (and
`workspace_preflight.py` additionally accepts `--workspace`/`--registry` overrides), so invoking
them through the absolute library root works from any CWD.

## Machine-readable registry — `registry.yml`

The README's project-registry table has a structured twin: **`portfolio-prompts/registry.yml`**.
It is the **machine-readable form** that tooling and skills load instead of parsing the README's
prose cells — one `defaults:` block plus one row per project (`github`, `status`, `gates`,
`deviations`, `couples_with`, `orchestration_target`, `presentation_role`, and
`multi_stack`/`sdd`/`live_api`/`product` flags), plus explicit `support_repositories:`
classifications for workspace repositories that are not valid `PROJECT=` values. The README table
is the human-readable view of the project rows.

- **Resolution order is unchanged.** A project's `deviations:` override the `defaults:`, exactly as
  the prose rules in this contract describe.
- **Lifecycle and orchestration are separate.** `active` means the canonical backlog contains open
  work; `resting` means it has zero outstanding items; `meta` identifies control-plane tooling.
  Resting projects remain safe orchestration targets: only `orchestration_target: false` removes a
  project row from the `*-all-*` fan-outs.
- **Presentation is separate from both.** Every project row declares exactly one
  `presentation_role`: `showcase`, `methodology`, or `hidden`. Resting does not imply hidden, and
  presentation role never grants orchestration eligibility. The role semantics and public-copy
  boundary are recorded by the portfolio landing repository's decision 001.
- **Support repositories are classified, not registered projects.** Entries under
  `support_repositories:` describe workspace support/presentation repositories such as
  `portfolio-landing`; they are not valid `PROJECT=` values and must declare
  `orchestration_target: false`.
- **The README table is generated** (PP-23). To change a project's row, edit `registry.yml`, then
  run `python tools/render-registry.py` (from `portfolio-prompts/`); it rewrites the block between
  the README's `<!-- REGISTRY:START -->`/`<!-- REGISTRY:END -->` markers. `--check` exits non-zero
  if the table is stale — usable as a gate. Never hand-edit the table between the markers.
  `registry.yml` is the source tooling trusts; the README table is its generated human view.
- A skill resolves a project by loading its row:
  `backlog = row.deviations.backlog ?? defaults.backlog`,
  `gates = first-hit(defaults.gate_cascade, row.gates)`,
  `targets = projects where orchestration_target`,
  `public_projects = projects grouped by presentation_role`.

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

The **library gates itself** too: `PROJECT=portfolio-prompts` resolves (via its `registry.yml` row)
to `python tools/check-library.py` (PP-15) — it asserts the registry maps to real folders, no
workspace repo is left unclassified, the README table is generated from `registry.yml`, internal
doc links resolve, and the worklist example parses. See [tools/README.md](tools/README.md).

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
  paired Markdown/HTML control records tracked by the portfolio root support repository, not by a
  target project's repository. The filename prefix is the namespace. Version sequences are **per
  project**: "highest version" comparisons are made only among files sharing the `{PROJECT}_`
  prefix, never across the folder. **Compare versions numerically, not lexically** — a plain
  filename sort orders `v9` *after* `v13`; parse `{N}` as a number before deciding which file is
  latest.
- **Handover manifest (PP-14):** `session-notes/manifest.json` indexes every handover; its `latest`
  map gives the newest version per project directly, so readers look "latest" up instead of
  re-deriving it (removing the numeric-sort hazard above). It is regenerated by scanning the folder
  with `tools/build-handover-manifest.py` — `write-handover` runs it after writing; `resume-session`,
  `derive-worklist`, and `loop-worklist` **prefer it and fall back to the numeric-glob rule only when
  it is absent**. Unlike the paired handovers, `manifest.json` is generated, deliberately ignored
  by the root support repository, and never hand-edited or committed.
- **Handover pair integrity (P-09):** a Markdown handover without its HTML companion is a contract
  violation, not a cosmetic gap. It fails hard in two places: `tools/build-handover-manifest.py`
  (both build and `--check` modes exit non-zero listing each unpaired file — so `write-handover`'s
  post-step catches it at the moment of authorship) and the library self-gate
  `tools/check-library.py` (when the sibling `session-notes/` archive is present). The workspace
  preflight additionally surfaces it as a per-target `WARN`.
- **Handover freshness (P-09):** whether the latest handover predates the project's fetched default
  head is **advisory only** — a preflight `WARN`, never a hard failure — because commits
  legitimately land after a handover is written. Refresh policy: for a **resting or closed**
  project, a post-handover commit does not by itself require a terminal refresh; judge currency by
  cross-checking the project's backlog and Git history. Write a fresh handover when closing a
  project (`close-project` writes the terminal one), when resuming work whose scope the latest
  handover no longer describes, or when the handover's public-facing claims have become wrong.
- **Worklists:** `WORKLIST_{PROJECT}.md` at the portfolio root — control records tracked by the root
  support repository, outside every target project's history. One worklist exists per project; a
  `loop-worklist` invocation or scheduled iteration binds to exactly one. A target-project commit
  must never absorb a root worklist change.
- **Shared templates:** `templates/` at the portfolio root — project-agnostic scaffolding
  (backlog, implementation log, code review, ADR, etc.).
- **Prompts:** this folder (`portfolio-prompts/`), its own git repository.

### Worklist file format (canonical)

`WORKLIST_{PROJECT}.md` is the loop's memory: `derive-worklist` writes it, and `loop-worklist`
reads it first and updates it last each iteration. It lives in the tracked portfolio root support
repository, outside the target project repository — one worklist per project; a `loop-worklist`
invocation or scheduled iteration binds to exactly one. Worklist changes therefore use the root
repository's own branch/PR flow and are never included in the target project's commit. Both
prompts use **exactly** this format — cite this
section rather than restating it:

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

### Workspace preflight (portfolio P-06)

Every orchestration fan-out starts by running this command from the portfolio root:

```bash
python <LIBRARY_ROOT>/tools/workspace_preflight.py
```

Pass `--projects=<folder>,<folder>` when the invocation or available worklists restrict the target
set; `--json` provides the same report as structured data. The tool loads only project rows whose
`orchestration_target` is true from `registry.yml` — there is no second hard-coded target list.

The preflight is deliberately **read-only**. It reads local files and already-fetched Git refs with
optional Git locks disabled; it never fetches, pulls, switches, resets, cleans, stages, commits, or
otherwise changes a checkout. Consequently `ahead`/`behind` and freshness describe the local view
of the upstream/default refs from the last fetch, not an implicit network refresh.

For each target it reports folder/Git readability, branch, dirty state, upstream, ahead/behind
counts, authoritative backlog path/presence, resolved gate source and commands/CI steps, latest
handover pair, and whether that handover predates the fetched default head. Results are classified:

- `BLOCKED`: evidence is unsafe or structurally incomplete — for example a missing repository,
  unreadable Git state, dirty tree, or missing authoritative backlog.
- `WARN`: evidence is readable but may be non-current — for example ahead/behind state, a topic or
  detached branch, no upstream/default ref, a missing/incomplete handover, or a stale handover.
- `READY`: no blocker or warning was found.

Exit `0` means every selected target is `READY`/`WARN`; exit `1` means one or more target reports
are `BLOCKED`; exit `2` means the registry/invocation itself (including an invalid selection) could
not be evaluated. A fan-out may
continue with `READY` and `WARN` targets while faithfully reporting warnings, but must exclude and
report every `BLOCKED` target. Exit `2` stops the entire fan-out.

### Orchestration fan-out (shared conventions)

The portfolio-scoped orchestrators (`derive-all-worklists`, `loop-all-worklists`,
`review-all-projects`) all fan out one sub-agent per target project and collate a report. These
conventions are common to all three — each orchestrator cites this section and adds only its
**mode-specific deltas** (no-actioning / mutating / evidence-only):

- **Preflight first.** Run the workspace preflight above before coupling or launching any agent;
  use its registry-derived target set, exclude `BLOCKED` targets, and carry all warnings into the
  final report.
- **No `PROJECT=` for the orchestrator** (it targets the registry); every sub-agent it launches
  receives a single `PROJECT=` and is bound by this contract as normal.
- **Self-contained sub-agent prompts.** Sub-agents start with no conversation context — each
  launch prompt must carry everything the sub-agent needs (working directory, the absolute
  `<LIBRARY_ROOT>` canonical-prompt path, `PROJECT=<folder>`, and the mode-specific rules), not
  rely on context.
- **One sub-agent per project; never two agents on the same project or the same working tree.**
  Coupled projects (per the registry coupling notes) share **one sequential agent** that works
  them in dependency order (provider/library first, consumer second).
- **Launch bounded waves in parallel.** Partition the targets into waves no larger than the
  environment's available child-agent slots, reserving the orchestrator's own slot. Launch every
  agent in a wave in the same turn. Before proceeding, confirm that agents launched for the wave
  equal that wave's targets (including any sequential coupled agent). After collecting the wave,
  launch the next until every target has run — a missing target is a silent gap.
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
