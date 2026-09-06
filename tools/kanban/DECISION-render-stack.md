# Decision D6 — Kanban board render stack

**Status:** Decided (recorded before any board shipped, per D6).
**Decision:** A single self-contained HTML file with a **vanilla-JS renderer**
reading two embedded JSON payloads. No framework, no build step, no CDN, no
vendored files.
**Rejected:** Keeping the auth-separation exemplar's vendored
React 18 + ReactDOM + babel-standalone stack.

## Why the choice was open

The exemplar board (`auth-separation_implementation-kanban_v1.html`) renders with
three vendored scripts loaded from a sibling `vendor/` directory:

| File | Purpose | Size |
|---|---|---|
| `react-18.2.0.production.min.js` | UI runtime | ~10 KB |
| `react-dom-18.2.0.production.min.js` | DOM renderer | ~130 KB |
| `babel-standalone-7.23.9.min.js` | in-browser JSX transpiler | **~2.8 MB** |

That is a defensible choice for one hand-authored board in one repo. It stops being
defensible for a **shared generator that commits a board into every project repo and
publishes it to every project's Pages site** — the axis this build sits on.

## Measurement

The OUTPUT contract for this build requires "one self-contained board". The exemplar
is not self-contained: strip the `vendor/` directory and it renders nothing. Making
the React stack self-contained means **inlining ~2.94 MB** (dominated by
babel-standalone) into every committed board.

| | Vendored React + babel (self-contained) | Vanilla single-file |
|---|---|---|
| Bytes added to each board | ~2.94 MB inlined | ~8 KB template + CSS + JS |
| Files per board | HTML + 3 vendored scripts (or one giant inlined HTML) | 1 HTML file |
| Network needed to render | none (once inlined) | none |
| Runtime cost | in-browser JSX transpile on every open | none |
| Determinism (drift-gate) | fine | trivially byte-identical |
| Cost across ~14 repos | ~2.94 MB × N committed **and** published | negligible |

At portfolio scale that is roughly **40 MB** of committed-and-published transpiler
whose only job is to convert JSX that a generator can just as easily emit as plain
DOM calls. The board's interactivity — column layout, three filters, a search box,
and a detail modal — is about 150 lines of vanilla JS.

## Portability check

The status-derivation logic carried over from the exemplar
(`scripts/sync-kanban-status.mjs`) is already framework-agnostic plain JavaScript;
moving off React required **no rewrite** of it. Only the view layer changed, and the
exemplar's React component (cards, tags, dependency pills, modal) maps one-to-one onto
DOM-building helpers in `lib/render.mjs`.

## Consequences

- Boards are a single `{project}_implementation-kanban_v1.html` with two
  `<script type="application/json">` payloads (`payload-tickets`, `payload-stats`) —
  the same ids the exemplar used, so the drift-gate reads them back unchanged.
- No `vendor/` directory ships with a board; migrated repos can delete theirs (that
  removal is T4's job, not this build's).
- Because there is no transpile step and payload serialisation has a fixed field
  order, a board is byte-identical on unchanged inputs — which is exactly what the
  `--check` drift-gate (T5) needs.
