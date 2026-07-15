# portfolio-prompts — Library Review (Update)

**Date:** 2026-07-15
**Reviewer:** AI assistant (Claude Fable 5)
**Scope:** Update to the second review ([`library-review_2026-07-13.md`](library-review_2026-07-13.md)),
verifying its outcomes now that `docs/backlog.md` v7 reports **zero outstanding items**
(PP-00..PP-26 all resolved). Covers all 14 prompts, `project-layout.md`, `registry.yml`,
`tools/`, `skills/` + `.claude-plugin/`, and the backlog.
**Style:** en-GB.

> This is a review of the **prompt library itself**, not of any project it serves. It is an
> *update* review: rather than re-assessing every prompt, it verifies the disposition of the
> 2026-07-13 review's eight weaknesses against the live repository, records what the library has
> become since, and derives the next actionable items (`PP-27..PP-29` in
> [`docs/backlog.md`](backlog.md)).

---

## 1. What changed since 2026-07-13

The previous review produced PP-13..PP-24; **all twelve were resolved within two days** (PRs
#19-#31, 2026-07-13), followed by two portfolio-driven items: **PP-25** (the read-only workspace
preflight, portfolio P-06, PR #34) and **PP-26** (handover pair integrity, portfolio P-09,
PR #35). `main` is at `19ec0f6` with a clean tree.

Structurally, the library crossed a line: it is no longer only prose conventions. It now has a
**control plane**:

- **`registry.yml`** at the root is the machine-readable source of truth (PP-13): 9 members —
  8 projects (including `mobile-forex-automation`, registered via MF-14 after the review) plus the
  meta row — with `defaults:`, per-project `deviations:`, structured `gates:`, a `couples_with:`
  field for the calculator -> hand-baked dependency, and a `support_repositories:` section that
  classifies `portfolio-landing` without making it an orchestration target.
- **`tools/`** holds four scripts: `check-library.py` (the self-gate), `render-registry.py`
  (README table generator, PP-23), `build-handover-manifest.py` (PP-14/PP-26), and
  `workspace_preflight.py` (PP-25) — with deterministic tests under `tools/tests/`.
- **`skills/` + `.claude-plugin/plugin.json`** package the library as a Claude Code plugin
  (PP-24): 14 thin-wrapper skills, one per prompt, each delegating to its canonical
  `*.prompt.md`.
- **Three new prompts** shipped from the review's "future additions" list: `onboard-project`
  (PP-20), `portfolio-status` (PP-21), and `triage-review-findings` (PP-22), bringing the prompt
  count from 12 to 14.

## 2. Verification evidence (run 2026-07-15)

Claims below were checked against the live workspace, not the backlog's own account:

- `python tools/check-library.py` — **PASS**, covering: registry classification and lifecycle
  semantics, README-generated check, least-privilege CI, internal links, skills frontmatter,
  working-norms non-duplication, OS-neutral invocation paths, the worklist example, workspace
  preflight scenarios, and handover pairs.
- `python tools/workspace_preflight.py` — **WARN, exit 0**: 8 targets, **0 blockers**,
  12 advisory warnings (see §4.3). Every target resolved its folder, backlog (including sudoku's
  `DOCS/.planning/backlog.md` deviation), gate source, and a **paired** latest handover.
- `registry.yml` parses; every non-meta `project` maps to a real workspace folder; the README
  registry table regenerates with no diff (enforced by the self-gate).
- 13 `*.prompt.md` files + `github-repo-analysis-prompt.md` = 14 prompts; 14 skills;
  `proposals/` correctly reduced to a pointer README (the prototype registry was promoted, not
  duplicated).

## 3. Disposition of the 2026-07-13 weaknesses

| # | Weakness (2026-07-13) | Disposition |
|---|---|---|
| 1 | Registry is prose, not data | **Resolved** (PP-13/PP-23). `registry.yml` is the source; the README table is generated and the self-gate fails on hand-edits. |
| 2 | Filename-encoded handover versions | **Resolved** (PP-14/PP-26). `session-notes/manifest.json` resolves "latest"; unpaired Markdown handovers now *fail* the manifest build and the self-gate. |
| 3 | Windows-only invocation paths | **Resolved** (PP-18). Forward slashes throughout; the self-gate blocks regressions in operational docs. |
| 4 | No validation of the prompts themselves | **Resolved** (PP-15, extended by PP-25/PP-26). The library has a real `verify` gate, run in CI, with deterministic test fixtures. |
| 5 | Verbosity / density | **Partially resolved** (PP-19 reader's map). Density is inherent to the design; acceptable residual. |
| 6 | Duplicated branch + PR norm | **Resolved** (PP-17). Single copy in `project-layout.md`; the self-gate rejects restatements. |
| 7 | Hand-maintained coupling | **Resolved** (PP-13). `couples_with:` is structured data with an `order: provider-first` field. |
| 8 | Registry drift from reality | **Resolved** (PP-16 + drift check). All workspace repos are classified (project, meta, or support); an unclassified repo fails the gate — this check caught `portfolio-landing` and `mobile-forex-automation` on first run, and both are now recorded. |

The pattern worth naming: five of the eight fixes came with **enforcement**, not just a corrected
document. The library moved from "conventions the model must remember" to "conventions a script
rejects violations of", which is the same maturity step the test projects themselves were asked to
make (gates before commits).

## 4. Residual weaknesses and observations

1. **PP-24 residuals are still open.** (a) The plugin's skill auto-triggering has never had a
   live smoke test — it needs the plugin installed in an interactive session, explicitly deferred
   at resolution time and still not done. (b) The lifecycle skills resolve portfolio-relative
   paths against the CWD, so the plugin only works from a portfolio-root session; "any-workspace"
   portability — the review's stated strategic direction — remains the one unbuilt piece.
   -> **PP-27**, **PP-28**.
2. **The backlog's structure has drifted from its content.** `docs/backlog.md` v7 lists eleven
   fully-resolved items (PP-25, PP-13..16, PP-03/04/05, PP-00, PP-10, and the LOW block) under
   "## Outstanding Items", while its own risk summary says zero outstanding. Every reader must
   check each item's `Status:` line to learn the section heading is wrong. A structural tidy
   (resolved items move to Resolved; Outstanding holds only open items) makes the file honest at
   a glance. -> **PP-29**.
3. **The preflight's 12 warnings are workspace hygiene, not library defects — but they are real.**
   Four checkouts sit on topic branches (`magento-checkout-automation` on
   `codex/p04-magento-mit` with **no upstream**, `hand-baked-screenplay-pattern`,
   `orangehrm-pim-automation`, `mobile-forex-automation`), and `bfx-ws-screenplay` is 2 commits
   behind its fetched upstream. A fan-out launched today would carry five WARN targets. The
   loop prompts branch from fresh `main` so this is survivable, but the preflight exists
   precisely to surface it: a pre-fan-out hygiene sweep (checkout `main`, fast-forward) is due.
   Recorded as a portfolio-level action, not a `PP-` item (it changes checkouts, not the library).
4. **Handover freshness warnings are policy-compliant.** Seven of eight targets report
   "latest handover predates fetched default head"; PP-26 deliberately made freshness advisory,
   and the refresh policy (terminal refresh at close, on scope-changing resume, or when public
   claims become wrong) covers these. No action beyond the policy.
5. **Observation, no action:** the registry records two owning GitHub accounts (`GBrooks1970` and
   `NeoCognitus70`) across members. The registry treats `github:` as plain data, so nothing
   breaks; noted only so a future consolidation, if ever wanted, starts from an accurate list.

## 5. Recommended next steps

**Library (now in the backlog):**
- **PP-28** — make the lifecycle skills workspace-portable (resolve `portfolio_root` from
  configuration rather than assuming the CWD). The highest-leverage open item: it completes the
  prompt -> skill arc that PP-13 and PP-24 built towards.
- **PP-29** — restructure `docs/backlog.md` so "Outstanding" contains only open items. Cheap,
  removes a standing source-of-truth ambiguity in the library's most-read file.
- **PP-27** — live auto-trigger smoke test of the installed plugin (needs an interactive
  session; five minutes of human time, closes the last `[~]` in PP-24).

**Portfolio (outside this backlog):**
- **Workspace hygiene sweep** before the next fan-out: return the four topic-branch checkouts to
  `main` and fast-forward `bfx-ws-screenplay`, then re-run `tools/workspace_preflight.py` to
  confirm 0 warnings of the branch/behind class.
- **Fourth review cycle is now materially different from the third:** the registry has 8
  orchestration targets, three of which (`markdown-renderer`, `orangehrm-pim-automation`,
  `mobile-forex-automation`) have **never been through a `review-all-projects` fan-out**. When
  the next cycle runs, it exercises the PP-25 preflight and the enlarged registry end-to-end for
  the first time.

## 6. Bottom line

The 2026-07-13 review's thesis — "the prose registry is the keystone; fix it and the library
becomes a portable, self-validating skill pack" — has been executed almost in full, and faster
than the review anticipated: registry as data, generated README, handover manifest with pair
enforcement, a real self-gate in CI, a workspace preflight guarding the fan-outs, and a packaged
plugin. All eight identified weaknesses are resolved or acceptably residual, and every claim
checked in this update held against the live repository. What remains is small and specific:
finish the plugin's portability (PP-28) and its live trigger test (PP-27), tidy the backlog's
structure (PP-29), and sweep the workspace before the next fan-out. The library's next
structural test is not another self-review — it is the first full orchestration cycle over the
enlarged, preflight-gated registry.
