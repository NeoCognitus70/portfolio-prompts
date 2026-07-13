# portfolio-prompts — Library Review

**Date:** 2026-07-13
**Reviewer:** AI assistant (Claude Opus 4.8)
**Scope:** All 12 prompts + `project-layout.md` (contract) + `README.md` (registry) + `docs/backlog.md`.
**Style:** en-GB.

> This is a review of the **prompt library itself**, not of any test-automation project it
> serves. Its actionable outcomes are recorded as `PP-13..PP-24` in
> [`docs/backlog.md`](backlog.md) so a future session can pick them up. A prototype of the two
> highest-value items (a structured registry and the first skill) already exists under
> [`../proposals/`](../proposals/).

---

## 1. What the collection is

A self-contained, git-tracked library of **12 reusable session prompts** plus a shared
**contract** (`project-layout.md`) and a **registry** (the README table). It industrialises the
lifecycle of a multi-project test-automation portfolio: every prompt is invoked against one
`PROJECT=<folder>`, resolves its paths and gates through the contract, and writes to conventional
locations. The library has even onboarded *itself* as a "meta" registry member with its own
backlog.

The lifecycle:

```
resume-session -> derive-worklist -> loop-worklist -> write-implementation-log
              -> write-code-review -> write-handover -> close-project
```

with three portfolio-scoped **fan-out orchestrators** (`derive-all-worklists`,
`loop-all-worklists`, `review-all-projects`) that parallelise the single-project step across the
whole registry, and one **outlier** (`github-repo-analysis-prompt`) that is registry-free and
works on any repo.

---

## 2. Per-prompt notes

| Prompt | Verdict | Notes |
|---|---|---|
| `resume-session` | Strong | Three-source reconciliation (handover / backlog / live repo) with "don't trust, check". The stray-file guard and numeric-vs-lexical version rule are battle-scars turned into instructions. |
| `derive-worklist` | Strong | Clean separation of *planning* from *doing* ("You are NOT actioning"). Anti-padding rule ("a short worklist honestly derived beats a long one") is excellent. |
| `loop-worklist` | Strongest | The heart of the system. One item per iteration, gate-before-commit, never-commit-on-red, branch-from-fresh-main, honest stop conditions. The "session-boundary test" (re-orient if you don't remember orienting) guards against stale loop memory. |
| `write-handover` | Strong | `.md`-as-source, `.html`-generated-not-authored is the right call. Fixed section shape with `N/A - reason` escape hatch avoids padding. The repeated "put it in the folder, not root" warning is earned but symptomatic (see weakness #2). |
| `write-implementation-log` | Strong | Append-only / immutable discipline; promotes structural decisions to ADRs rather than burying them. |
| `write-code-review` | Strong | Rich, template-driven, evidence-ruled ("never fabricate a CVE", "label inferences"). Most likely to over-produce (7+ mandated files even for a single-repo project) - mitigated by the `N/A` valve. |
| `close-project` | Strong | Verification sweep *fetches* published URLs for real content, not just HTTP 200 ("an empty shell has shipped before"). Refuses to close over a red state. |
| `derive-all-worklists` | Good | Safe-by-design (disjoint writes). Launch-count self-check added after a real miss. |
| `loop-all-worklists` | Good | The only *mutating* fan-out; the coupling check (calculator -> hand-baked) is handled explicitly. Highest-risk prompt in the set. |
| `review-all-projects` | Good | Evidence-only fan-out with the cross-tree-build caveat. Cross-portfolio synthesis (common themes, outliers) is the genuine payoff. |
| `github-repo-analysis` | Strong / most reusable | Depth-controlled (`summary`/`standard`/`deep-dive`), acquire-before-analysing gate, SOLID + ISTQB + security passes. Already project-agnostic - the natural first skill. |

---

## 3. Strengths

1. **A real contract, not copy-paste.** `project-layout.md` is a genuine abstraction layer: paths,
   the first-hit-wins gate cascade, the canonical worklist format, and the shared orchestrator
   scaffold live in one place and are cited, not restated. The PP-03/04/05 refactors show the
   library applies its own DRY discipline.
2. **Source-of-truth discipline.** The backlog wins over the handover, which wins over memory;
   every prompt flags discrepancies rather than silently choosing "the nicer story". The single
   most valuable design decision.
3. **Evidence over assumption, everywhere.** "Don't trust, check"; cite commits/URLs/line numbers;
   "never round up"; label inferences; fetch artefacts for *content*.
4. **Guards born from real failures.** The v11-at-root stray, numeric-vs-lexical versioning, the
   forgotten sequential agent, the "empty shell" report - each bug became an explicit instruction.
5. **Correct planning/execution split.** `derive` (no actioning) vs `loop` (one item, gated) vs the
   orchestrators is a clean, reviewable pipeline with human approval at the right seams (PRs never
   auto-merged).
6. **Consistent house style.** en-GB, ASCII, fixed document shapes, versioned + timestamped
   artefacts - the whole portfolio reads as one system.

---

## 4. Weaknesses and risks

1. **The registry is prose, not data.** The most drift-prone thing in the library is the README
   table - deviations (e.g. sudoku's `DOCS/.planning/backlog.md`), coupling notes, and gate rules
   are embedded in free-text cells. Every prompt must *parse English* to resolve a path. This is
   also the chief blocker to "any project" skill reuse. -> **PP-13**.
2. **Filename-encoded version numbers invite the bug they keep warning about.** Handover version
   lives in the filename (`_v13_`), so every prompt repeats "parse `{N}` numerically" and "glob for
   strays at root". The design causes the recurring hazard; a manifest/index would remove the class
   of bug. -> **PP-14**.
3. **Windows-only invocation paths.** Every example uses backslashes (`portfolio-prompts\name...`).
   A friction for cross-platform reuse or skill packaging. -> **PP-18**.
4. **No validation of the prompts themselves.** Gates for the library are "docs-only". Nothing
   checks that a cited path exists, that registry names match real folders, or that the worklist
   example parses. The library under-gates itself. -> **PP-15**.
5. **Verbosity / density.** High cognitive load; slow human onboarding; `write-code-review` and
   `github-repo-analysis` can over-produce on small repos despite the `N/A` valve. -> partially
   addressed by **PP-19** and by centralisation (**PP-13/PP-17**).
6. **Residual duplication.** The "all changes via branch + PR (harness blocks direct pushes,
   2026-06-10)" norm is restated in resume, loop, handover, close, and the contract. -> **PP-17**.
7. **Coupling is hand-maintained.** The calculator -> hand-baked dependency is prose, re-explained
   in two orchestrators. One structured `couples_with` field makes the check mechanical. -> **PP-13**.
8. **Registry accuracy drifts from reality.** The README lists five test projects; the workspace
   also holds `markdown-renderer` and `orangehrm-pim-automation`, which are not registry members -
   so the fan-outs silently skip them. -> **PP-16**.

---

## 5. Suggested improvements (now tracked in the backlog)

**Near-term (low risk, high leverage)**
- Extract the registry into a structured file (`registry.yml`) - kills #1, #7, #8; unlocks skills. **PP-13** *(prototype in `proposals/registry.yml`)*.
- Add a handover manifest/index to remove the numeric-parsing and stray-file hazards. **PP-14**.
- Add real self-gates: a check script proving cited paths and registry names resolve. **PP-15**.
- Reconcile the registry with the two missing projects (or record why they are excluded). **PP-16**.

**Medium-term**
- Centralise the branch + PR universal norm into the contract and cite it. **PP-17**.
- Make invocation paths OS-neutral. **PP-18**.
- Add a one-paragraph "reader's map" to the README for humans. **PP-19**.

**Future additions (new prompts / skills)**
- `onboard-project` - scaffold backlog/templates/registry-row for a new project. **PP-20**.
- `portfolio-status` - read-only cross-registry dashboard. **PP-21**.
- `triage-review-findings` - explicit bridge from a code review to a derived worklist. **PP-22**.
- `refresh-registry` - regenerate the README table from `registry.yml`. **PP-23** *(depends on PP-13)*.
- Package the collection as a portable **skill/plugin pack** with `project` as an argument. **PP-24** *(shipped in `skills/` + `.claude-plugin/`)*.

---

## 6. Skills potential (summary)

The collection is unusually well-positioned to become portable Claude Code **skills**: the
`PROJECT` parameter and the `project-layout.md` contract already provide the two things skills
need - a single input variable and an externalised configuration surface. Each `*.prompt.md` maps
almost 1:1 to a `SKILL.md`, with `project` becoming a skill argument and the three fan-outs taking
none (they read the registry).

The one structural change standing between "this portfolio" and "any project" is externalising the
registry + contract into machine-readable config the skill *loads* rather than prose the model
*re-reads*. That is exactly **PP-13**, which is why it is the linchpin.

`github-repo-analysis` is the right pilot: it takes no `PROJECT=`, reads no registry, and needs no
contract, so it isolates the prompt -> skill mechanics. It shipped as
[`../skills/analyze-repo/SKILL.md`](../skills/analyze-repo/SKILL.md) (PP-24); the full plugin and the
remaining skills are in [`../skills/README.md`](../skills/README.md).

---

## 7. Bottom line

A mature, self-improving library whose core designs - source-of-truth discipline, evidence-based
checks, planning/execution split, a real contract - are excellent. Its main structural weakness (a
prose registry every prompt must parse) is also the exact thing to fix first to turn the collection
into a portable, config-driven skill pack. `PP-13` is the keystone item; `PP-14/15/16` are the
cheap high-value follow-ons; `PP-24` is the strategic direction, already de-risked by the POC.
