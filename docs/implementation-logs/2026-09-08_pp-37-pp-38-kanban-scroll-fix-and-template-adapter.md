<!--
  AUDIENCE: Engineers and AI agents reviewing development session history.
  PURPOSE:  Record what was built, what was decided, what broke, and what was learned
            during a development session. Immutable once written — append only.
  LOCATION: docs/implementation-logs/2026-09-08_pp-37-pp-38-kanban-scroll-fix-and-template-adapter.md
  TEMPLATE: docs/templates/implementation-log.template.md
-->

# Kanban renderer scroll fix and shipping template adapter (PP-37, PP-38) — 2026-09-08

## Session Summary

Delivered the two library-owned sub-items of portfolio backlog item **P-13** (per-project Kanban
rollout), opened after decision **D9 — Option A, scoped** was accepted. **PP-37** fixed the generated
board's horizontal-scroll defect, whose root cause was an unbounded board height rather than the
missing `overflow-x` it appeared to be. **PP-38** promoted the `risk-block` dialect from a scaffold
that parsed essentially none of the portfolio's real backlogs into a shipping template adapter that
reads card body straight out of the backlog. Together they unblock P-13 Phases 2–3; the combined
`kanban-v1.1.0` release is deliberately not cut, because publishing needs the owner's npm
credentials.

---

## Objectives

1. **Register PP-37 and PP-38 in `docs/backlog.md`** so the source of truth reflects the work P-13
   opened (the backlog still read "no outstanding items" at v24). — **Complete** (`e5152a5`, PR #89).
2. **PP-37 — make every board column reachable.** — **Complete** (`9812cc5`, PR #90).
3. **PP-38 — promote `risk-block` to a shipping template adapter.** — **Complete** (`7477055`,
   PR #91, open at time of writing).
4. **Cut `kanban-v1.1.0`.** — **Deferred by design.** Publishing is an owner-credential gate; the
   loop prepares the change and stops there.

---

## Test Results

| Suite | Before this session | After |
|---|---:|---:|
| `cd tools/kanban && node --test` | 49 pass | **58 pass** (0 fail) |
| `python tools/check-library.py` | PASS | **PASS** |

Nine tests were added: one CSS-contract regression check for PP-37, six adapter tests and one
end-to-end generator test for PP-38, and one merge-precedence test for the body-fallback change.

---

## Changes Implemented

### Change 1 — PP-37: bound the board to the viewport (`tools/kanban/lib/render.mjs`)

The board already declared `overflow-x:auto` and *was* internally scrollable
(`scrollWidth` 1548 vs `clientWidth` 564). It also carried `min-height:calc(100vh - 200px)` with no
bounded height, so it grew to its tallest column — measured `offsetHeight` **6378px** against the
51-ticket `auth-separation` backlog, whose Parked column holds 46 cards. A block renders its
`overflow-x` scrollbar at its **own bottom edge**, which therefore sat roughly **5845px below the
fold**, while `body`/`html` stayed `overflow-x:visible` and never scrolled horizontally because the
board clipped its own overflow.

The page became a full-height flex shell, which removes the `200px` magic number rather than
re-tuning it — the chrome wraps on narrow viewports, so any fixed constant is wrong somewhere:

- `body` → `height:100vh; display:flex; flex-direction:column; overflow:hidden`
- `header` / `.stats` / `.filters` → `flex:none`
- `.board` → `flex:1; min-height:0` (was `min-height:calc(100vh - 200px)`)
- `.column`, `.column-body` → `min-height:0`

The `min-height:0` additions are the non-obvious part: a flex item's `min-height` defaults to `auto`,
which prevents it shrinking below its content. Without them the column body's existing
`overflow-y:auto` never engages and the column stretches the board again, reproducing the defect by
another route.

### Change 2 — PP-38: shipping template adapter (`tools/kanban/lib/adapters.mjs`)

`riskBlock` was replaced. Item detection now covers the canonical
`#### Risk #N: <title> — Score: <n>` plus the two variants the portfolio actually contains — a
review-qualified number (`Risk #2 (review #1):`, bfx) and an explicit id (`Risk PBR-07:`, parabank) —
and a scoreless closure heading inside a `Resolved Risks` section. Every form requires either a
`Score:` or the resolved section, so prose `####` headings ("Out of scope", "Implementation
acceptance criteria", "Validation and closure criteria" — all real parabank headings) can never
become phantom cards. Duplicate ids now throw instead of silently emitting two cards for one risk.

Card body is read from the backlog itself: `**Problem:**` (plus `**Impact Analysis:**`) becomes the
description and `**Success Criteria:**` checkboxes become acceptance, so a risk-scored project needs
no per-project content override. Priority band comes from the enclosing
`### HIGH|MEDIUM|LOW Priority` heading, falling back to the score. Status maps as a pre-classified
pass-through and `graphDerived` stays `false` — a risk carries no dependency edges.

### Change 3 — body precedence (`tools/kanban/lib/override.mjs`)

`mergeContent` previously took body fields only from the override file. It now resolves each body
field as **override → adapter-supplied backlog body → absent**, via a small `pickBody` helper. The
`auth-table` dialect supplies no body, so its override-driven cards are unchanged.

### Change 4 — band styling (`tools/kanban/lib/render.mjs`)

The renderer only styled `P0`–`P3`, so `priClass('HIGH')` produced `tag-high` with no CSS and
`PRIORITY_ORDER` treated every band as equal. Added `.tag-high/.tag-medium/.tag-low`,
`.border-high/.border-medium/.border-low`, and `HIGH/MEDIUM/LOW` sort keys. This was not anticipated
when PP-38 was written — the plan assumed band and score alone were enough.

### Change 5 — fixtures and guards

A new `tools/kanban/test/fixtures/risk-template/` carries the canonical heading, both variants, body
extraction, the resolved section, and three prose-heading traps in one file, and is registered in the
cross-language guard `tools/tests/test_kanban_generator.py`. The `auth-table` and `risk-block`
fixture boards were regenerated: auth-table's diff is CSS only, while risk-block's tickets gain the
derived `priority` band and `byPriority` stats with ids and statuses unchanged.

---

## Technical Decisions

- **Fix the shell, not the constant.** `height:calc(100vh - 200px)` would have worked at one viewport
  and failed wherever the header/stats/filters wrap. A flex shell makes the board's height a
  consequence of the chrome's actual height.
- **Reject by grammar, not by blocklist.** Phantom-card prevention relies on requiring a `Score:` (or
  the resolved section) rather than listing known prose headings, so an unforeseen heading is
  rejected by default.
- **Override still wins.** Adapter-supplied body is a fallback, never an override, so a project that
  wants richer cards than its backlog carries can still supply one.
- **One combined release.** PP-37 and PP-38 both touch `tools/kanban`; consumers pin exact versions,
  so shipping them as a single `kanban-v1.1.0` avoids making every downstream repo upgrade twice.
- **Resolved entries get a slug id.** A resolved-section entry carries no risk number, so its id is a
  deterministic six-word slug of its title (`RES-…`) — stable across regeneration, which the
  drift-gate requires.

---

## Documentation Updates

- `docs/backlog.md` — v24 → v25, opening PP-37 and PP-38 with scores, problems and success criteria;
  risk summary and suggested order updated. The v24 note's now-false "there are no outstanding items"
  claim was trimmed while its record was kept.
- This implementation log.
- A portfolio-level walkthrough of the wider D9 → P-13 arc is recorded at the portfolio root in
  `docs/walkthroughs/2026-09-08_kanban-d9-decision-and-p13-delivery.md`.

---

## Lessons Learned

- **"No scrollbar" did not mean "no `overflow-x`".** The property was already present; the bug was
  height. Reading the computed layout (`scrollWidth` vs `clientWidth`, element `offsetHeight`, and
  where the element's bottom sat relative to the fold) found in minutes what inspecting the CSS
  declaration alone would have missed.
- **Prove a regression test fails first.** The PP-37 check was run against the previous rule and
  observed to fail before being committed. A regression test that cannot fail is worthless, and this
  costs one command.
- **The drift-gate will flag committed fixture boards on any render change.** Twice this session it
  failed with "Regenerate and commit" — working exactly as designed. Expect to regenerate fixtures
  whenever `render.mjs` changes, and check the diff is presentational before accepting it.
- **A dialect is more than a parser.** PP-38 was scoped as adapter work, but the renderer's priority
  palette only covered `P0`–`P3`; shipping a band-based dialect required render support too. Check
  the whole path from backlog to pixel before sizing an adapter.
- **Backlog heading level is load-bearing.** The self-gate parses Outstanding items as `### PP-NN:`
  and Resolved as `#### PP-NN:`. Writing a new outstanding item at the wrong level produced
  "Total Outstanding is 2; found 0", which is the gate correctly refusing an inconsistent backlog.

---

## Recommendations / Next Steps

1. **Merge PR #91** (PP-38) and the root worklist tick, then **reconcile `docs/backlog.md`**: PP-37
   and PP-38 are still recorded `READY TO START` and should move to resolved. This is the
   `write-handover` stage's reconcile step.
2. **Cut `kanban-v1.1.0`** — owner npm gate. Nothing downstream sees either fix until it ships,
   because consumers pin exact versions.
3. **PP-39** — package `write-walkthrough.prompt.md` as a skill and add a prompt→skill coverage check
   to `check-library.py`; it is currently the only prompt with no skill wrapper, which is why the
   lifecycle's walkthrough stage was missed in this session.
4. **P-13 Phases 2–3** are unblocked once the release lands: standardise the parabank, bfx and saleor
   backlogs to the template shape, then generate and gate their boards.

---

*Session logged: 2026-09-08. Author: Claude Code (Opus 5).*
