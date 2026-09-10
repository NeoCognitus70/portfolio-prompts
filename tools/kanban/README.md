# tools/kanban — shared per-project Kanban generator + drift-gate

One generator, run inside each project repo, that builds a single **self-contained**
implementation-Kanban board from the project's backlog and an optional content
override, and a `--check` mode that fails CI if a committed board drifts from a fresh
generation. This is the shared implementation of portfolio design **Option B+** (one
generator; boards committed into each repo and published to each repo's own Pages,
with a per-repo drift-gate), decision **D5** (generator + optional per-project
content override), and decision **D6** (render stack — see
[DECISION-render-stack.md](DECISION-render-stack.md)).

Published to the public npm registry as
**[`portfolio-kanban-generator`](https://www.npmjs.com/package/portfolio-kanban-generator)**
so any project repo can run the drift-gate in CI via `npx` without vendoring the tool.
The npm package has **zero runtime dependencies** (vanilla Node). The prompt-library
source repo that hosts this directory stays private; only the npm package is public.

## Usage

```bash
# run straight from npm — no install, pinned to an exact version (for CI)
npx portfolio-kanban-generator@1.1.0 --check --dialect auth-table --project my-project

# write / refresh the board (run from the project repo root)
npx portfolio-kanban-generator@1.1.0 --project my-project
```

Or, from a checkout of this repo (development / the library's own gate):

```bash
# write / refresh the board (run from the project repo root)
node path/to/tools/kanban/generate-kanban.mjs --project my-project

# drift-gate: exit 1 if the committed board is stale or missing (for CI)
node path/to/tools/kanban/generate-kanban.mjs --check --project my-project
```

### Options

| Option | Default | Meaning |
|---|---|---|
| `--project <name>` | basename of `--cwd` | project id, used in the heading and board filename |
| `--backlog <path>` | `docs/backlog.md` | the backlog file |
| `--override <path>` | `docs/kanban-content.json` | optional ticket-body override |
| `--adr <dir>` | `docs/adr` | ADR directory, for citation resolution |
| `--dialect <name>` | `auth-table` | backlog adapter: `auth-table` or `risk-block` |
| `--board <path>` | `{project}_implementation-kanban_v1.html` | output board |
| `--title <text>` | `{project} — Implementation Kanban v1` | board heading |
| `--cwd <dir>` | `process.cwd()` | base directory for all relative paths |

`override_path` and `backlog_dialect` are also recorded per project in the library
`registry.yml` `defaults:` block, so the per-repo gate can be wired consistently.

## Where authority lives

The board never authors its own truth. Status is **derived**, never transcribed:

- the **backlog** owns which tickets are Done and which are Parked (human decisions);
- the ticket **dependency graph** (`blockedBy`) owns readiness;
- **Ready vs Backlog is authored by neither** — it is computed from the two above.

Parked is scope, not progress: a parked ticket never becomes Ready however its
blockers resolve (**scope beats dependency-readiness**). Readiness is never derived
from `blocks`. This rule is carried over verbatim from the auth-separation exemplar's
`scripts/sync-kanban-status.mjs`; see [lib/derive-status.mjs](lib/derive-status.mjs).

## Input contract

A **canonical ticket** has a header (from the backlog) and an optional body (from the
override):

- Header: `id`, `title`, `type?`, `priority?`, `score?` (0–30), `phase?`,
  `blockedBy[]`, `blocks?[]`, `backlogStatus` (Done | Parked | Ready | Backlog),
  `status` (derived).
- Body (override only): `description?`, `acceptance[]?`, `spec?`, `adr[]?`
  (each `ADR-nnnn`), `assignee?`.

### Backlog adapters

- **auth-table** (default, the shipping path): 7-column Markdown rows
  `| ID | Ticket | Type | Priority | Tier | Blocked by | Status |`. A row is a
  ticket iff its first cell is a backticked id and it has exactly seven cells.
  Status is keyword-classified — **Parked** (tested first) > **Done** > **Ready** >
  else **Backlog** — and `blockedBy` is read from the "Blocked by" cell. Ready/Backlog
  are recomputed from the graph.
- **risk-block** (shipping, pre-classified): the portfolio's shared risk-scored
  backlog template. Item headings are `#### Risk #N: title — Score: N` plus the
  variants `Risk #N (qualifier): …` and `Risk <ID>: …`; inside a `Resolved Risks`
  section a scoreless `#### Title ✅ Resolved <date>` heading is also an item. Every
  form requires a `Score:` or the resolved section, so prose `####` headings such as
  "Out of scope" never become cards. `**Status:**` maps COMPLETE → Done,
  IN PROGRESS → In Progress, READY TO START (or READY START) → Ready,
  BLOCKED → Backlog, RECORDED → Parked (the accepted-risk terminal state — asserted
  and consciously not accommodated, so closed to work but not a delivery);
  risks have no dependency edges, so the authored status passes
  through unchanged. Priority band comes from the enclosing
  `### HIGH|MEDIUM|LOW Priority` heading, falling back to the score, and drives
  grouping and the card badge in place of auth-table's phase filter. Card body is
  read from the backlog itself — `**Problem:**` (plus `**Impact Analysis:**`) becomes
  the description and `**Success Criteria:**` checkboxes become acceptance — so a
  risk-scored project needs **no content override**.

An adapter **fails loudly** on a backlog it cannot parse: parsing zero tickets is an
error, never an empty success.

### Content override (`docs/kanban-content.json`)

Optional. Required only where the backlog does not itself carry card body — the
`auth-table` dialect. A `risk-block` project's body comes from its own backlog, and an
override, if supplied, still takes precedence over it.

A JSON object keyed by ticket id whose values carry **only** body fields. Rules,
enforced (not merely documented):

- an override id absent from the backlog is a **hard error**;
- a backlog id with no override entry is fine (a header-only card);
- an override entry carrying any header field (`status`, `backlogStatus`,
  `blockedBy`, `title`, `type`, `priority`, `score`, …) is a **hard error**.

## What fails a run or the gate

Both modes fail (exit 1) on: an unparseable backlog, an override id absent from the
backlog, an override carrying header fields, an unresolved ADR citation, or a
non-deterministic render. `--check` additionally fails on a missing or stale board.

## Layout

```
tools/kanban/
  generate-kanban.mjs        CLI: default writes/refreshes; --check is the drift-gate
  lib/derive-status.mjs      status derivation (verbatim rule) + stats recompute
  lib/adapters.mjs           auth-table (graph-derived) + risk-block (pre-classified)
  lib/override.mjs           override load/validation, content merge, ADR resolution
  lib/render.mjs             self-contained vanilla-JS board renderer + payload I/O
  test/                      node:test suites + fixtures (auth-table, risk-block, risk-template)
  DECISION-render-stack.md   D6 measurement and decision
```

## Tests

```bash
cd tools/kanban && node --test
```

The suite covers the derive-status rule against its truth table, both adapters,
override validation, ADR resolution, and end-to-end generation / drift / determinism
over the fixtures. It also runs inside `python tools/check-library.py`
(check `check_kanban`) and is guarded across the language boundary by
`tools/tests/test_kanban_generator.py`.

## Publishing (maintainers)

This directory is its own npm package (`portfolio-kanban-generator`), independent of
the private prompt-library root (which is `"private": true` and cannot publish). The
published tarball is whitelisted to `generate-kanban.mjs`, `lib/`, `README.md`, and
`LICENSE` — `test/` and its fixtures are excluded. Confirm the contents before a
release with `npm pack --dry-run`.

A release is cut by pushing a tag `kanban-v<version>` that matches the `version` in
[package.json](package.json); the [`publish-kanban`](../../.github/workflows/publish-kanban.yml)
workflow then runs the test suite and `npm publish --access public`. It needs a
repository secret **`NPM_TOKEN`** (an npm automation token for an account that owns the
package name).

```bash
# 1. bump tools/kanban/package.json "version", commit, merge to main
# 2. cut the release
git tag kanban-v1.1.0
git push origin kanban-v1.1.0
```

To publish manually instead (from this directory, logged in to npm):

```bash
npm test
npm pack --dry-run          # verify the file list
npm publish --access public
```
