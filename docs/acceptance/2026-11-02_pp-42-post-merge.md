# PP-42 post-merge installation and acceptance — 2 November 2026

Merge and cleanup completed for library PR #131 (`d8b906671ca5111ead9b490cb559912c0ccf0b15`) and support PR #345 (`824a9296e70247dcb1da86cb675667c3e4161774`). Both primary repositories are clean on main and match origin/main. Both PP-42 branches are absent locally and remotely. The support review worktree is retained, clean and detached at merged origin/main.

Exact library merge CI [41510446495](https://github.com/NeoCognitus70/portfolio-prompts/actions/runs/41510446495) passed. Supported installation produced `0.7.5+codex.20261102190301`. All **103 checked release-bearing files**, the linked scenario document and **18 registry rows** match merged source. Installed prompt SHA-256: `7fbcf090924d600ed61e46841f3a3292745416a88043693fb7c00e35a367c1e6`.

The installed prompt was applied to a fresh read-only whole-registry inspection starting **2026-11-02 22:18:07 UTC**. This report was saved after evidence collection, outside the repositories. The status inspection changed no files, ran no tests and refreshed no remote Git state. Earlier authorised cleanup, installation and manifest regeneration are separate operations.

## Portfolio status

| Project | Registry | Repo | Open H/M/L | Latest handover | Open PRs | Current CI |
|---|---|---|---|---|---|---|
| magento-checkout-automation | resting | main · dfa7086 · clean | 0/0/0 | v22 · 2026-08-03 12:15Z | 0 | GREEN |
| hand-baked-screenplay-pattern | resting | main · 75eb4d7 · clean | 0/0/0 | v7 · 2026-08-20 22:40Z | 0 | NO RUNS |
| calculator-screenplay-bdd | resting | main · beca7dd · clean | 0/0/0 | v5 · 2026-08-19 14:45Z | 0 | GREEN |
| gb.automation.smoketests.sudoku.poc | active | main · f3408bf · clean | 0/0/0 | v7 · 2026-10-07 19:55Z | [#97](https://github.com/GBrooks1970/gb.automation.smoketests.sudoku.poc/pull/97), [#96](https://github.com/GBrooks1970/gb.automation.smoketests.sudoku.poc/pull/96), [#95](https://github.com/GBrooks1970/gb.automation.smoketests.sudoku.poc/pull/95) | GREEN |
| bfx-ws-screenplay | active | main · b90dba4 · clean | 0/1/1 | v6 · 2026-09-12 19:51Z | 0 | RED |
| orangehrm-pim-automation | resting | main · 4a5534a · clean | 0/0/0 | v3 · 2026-07-30 20:12Z | [#48](https://github.com/GBrooks1970/orangehrm-pim-automation/pull/48), [#47](https://github.com/GBrooks1970/orangehrm-pim-automation/pull/47), [#44](https://github.com/GBrooks1970/orangehrm-pim-automation/pull/44) | RED |
| markdown-renderer | resting | main · fb4e419 · clean | 0/0/0 | v5 · 2026-07-20 16:34Z | 0 | GREEN |
| mobile-forex-automation | resting | main · 4baf43c · clean | 0/0/0 | v3 · 2026-07-27 16:15Z | 0 | GREEN |
| parabank-bank-automation | resting | main · bbca594 · clean | 0/0/0 | v5 · 2026-09-02 05:30Z | 0 | GREEN |
| juice-shop-dast-automation | resting | main · 6939644 · clean | 0/0/0 | v4 · 2026-09-10 22:00Z | 0 | GREEN |
| auth-separation | resting | main · 066e883 · clean | 0/0/0 | v7 · 2026-08-17 18:17Z | 0 | GREEN |
| auth-separation-screenplay-poc | resting | main · 0534cfb · clean | 0/0/0 | v5 · 2026-09-10 17:52Z | 0 | GREEN |
| saleor-graphql-automation | active | main · 2449d7d · clean | 1/0/0 | v7 · 2026-11-01 11:58Z | 0 | GREEN |
| tradeblotter-wpf-screenplay | active | main · 656620d · clean | 0/1/0 | v2 · 2026-09-27 23:14Z | 0 | GREEN |
| loan-origination-parity | active | main · 59671e5 · clean | 0/0/1 | v1 · 2026-09-30 13:14Z | 0 | GREEN |
| credit-dashboard-sut | resting | main · 563977e · clean | 0/0/0 | v22 · 2026-10-23 20:20Z | 0 | GREEN |
| azure-dotnet-platform | active | main · 5387b41 · clean | 0/1/1 | NONE | 0 | NO RUNS |
| portfolio-prompts | meta | main · d8b9066 · clean | 0/1/0 | v11 · 2026-11-02 19:05Z | 0 | NO RUNS |

**Totals:** 18 registered projects, all present and clean; no missing checkouts. Seventeen have complete handover pairs; Azure has no handover. Recorded open backlog: HIGH 1 / MEDIUM 4 / LOW 3, total 8. Six open PRs. Current CI: **13 GREEN / 2 RED / 3 NO RUNS**; RUNNING, MIXED and UNAVAILABLE zero. These are observed-run colours, not universal exact-head test coverage.

## Attention needed

- Bitfinex: [current CI failed](https://github.com/GBrooks1970/bfx-ws-screenplay/actions/runs/41421251424) on 2 November. Canonical backlog retains MEDIUM LIVE-01 and one LOW dependency/runtime decision.
- OrangeHRM: [current E2E run failed](https://github.com/GBrooks1970/orangehrm-pim-automation/actions/runs/35924973904) on 23 September. Local HEAD `4a5534a` differs from remote main `44c3907`; the report did not change that checkout. Three open dependency PRs remain.
- Magento: current GREEN reflects the active image-build workflow only. `e2e` is **disabled_inactivity**, with a [failed latest run](https://github.com/GBrooks1970/magento-checkout-automation/actions/runs/40277606923) on 26 October. It is an inventoried inactive workflow, not retired history. The active image-build success is from June and does not cover current main.
- Hand-baked Screenplay: CI and Pages succeeded, but active `Release` has no default-branch run. Aggregate NO RUNS means incomplete default-branch run coverage, not a failed CI job.
- Portfolio prompts: exact-merge integrity CI passed, but active `Publish kanban generator` has no default-branch run; aggregate NO RUNS. The report does not reinterpret tag-oriented release activity as main-branch execution. Canonical backlog still records PP-42 as one open MEDIUM item; this acceptance report proves the post-merge technical checks, while its backlog/log closure remains a separate documentation update.
- Azure .NET Platform: active registry member, no workflows/runs and no handover yet; NO RUNS. Backlog records one MEDIUM and one LOW item.
- Saleor: one HIGH compatibility-review item remains. Its current schema-monitor run predates the new main revision; CI itself covers the merged head. Historical SGR-MAINT-01 publication wording still predates its verified merge; that wording is not a new dependency risk.
- TradeBlotter: MEDIUM TB-08B remains blocked. Loan Origination retains one LOW Windows tooling item.
- Sudoku: canonical backlog has zero open items but registry remains active; separately tracked root work is excluded from the canonical count. Three dependency PRs remain open.
- ParaBank: local HEAD `bbca594` differs from remote main `37fc86a`; observed CI/performance/pin-drift runs succeed but do not all cover that remote head. No fetch or update was performed as part of this report.

## Freshness limitations

The following active latest runs do not match the observed remote default-branch head; their successes do not establish exact-head coverage:

- magento-checkout-automation: bake-store-images, [run 27131449803](https://github.com/GBrooks1970/magento-checkout-automation/actions/runs/27131449803), 2026-06-08T10:26:03Z, run `a4eaf02` versus head `dfa7086`.
- gb.automation.smoketests.sudoku.poc: Dependency Graph, [run 30366340145](https://github.com/GBrooks1970/gb.automation.smoketests.sudoku.poc/actions/runs/30366340145), 2026-07-28T14:01:49Z, run `f514b1d` versus head `f3408bf`.
- parabank-bank-automation: ci, [run 39810241279](https://github.com/GBrooks1970/parabank-bank-automation/actions/runs/39810241279), 2026-10-22T16:01:05Z, run `bbca594` versus head `37fc86a`.
- parabank-bank-automation: perf, [run 41435603939](https://github.com/GBrooks1970/parabank-bank-automation/actions/runs/41435603939), 2026-11-02T11:17:15Z, run `f43ad4d` versus head `37fc86a`.
- parabank-bank-automation: pin-drift, [run 41399728346](https://github.com/GBrooks1970/parabank-bank-automation/actions/runs/41399728346), 2026-11-02T06:24:42Z, run `f43ad4d` versus head `37fc86a`.
- juice-shop-dast-automation: DAST repeatability probe, [run 34200784522](https://github.com/GBrooks1970/juice-shop-dast-automation/actions/runs/34200784522), 2026-09-08T07:43:43Z, run `1fc6706` versus head `6939644`.
- saleor-graphql-automation: Upstream schema monitor, [run 41487708843](https://github.com/GBrooks1970/saleor-graphql-automation/actions/runs/41487708843), 2026-11-02T17:05:05Z, run `abd506e` versus head `2449d7d`.
- credit-dashboard-sut: Pages, [run 39386930250](https://github.com/GBrooks1970/credit-dashboard-sut/actions/runs/39386930250), 2026-10-20T07:30:14Z, run `3860187` versus head `563977e`.
- credit-dashboard-sut: Visual baselines, [run 39238484690](https://github.com/GBrooks1970/credit-dashboard-sut/actions/runs/39238484690), 2026-10-19T10:35:01Z, run `1999d2e` versus head `563977e`.
- credit-dashboard-sut: Visual, [run 39998962157](https://github.com/GBrooks1970/credit-dashboard-sut/actions/runs/39998962157), 2026-10-23T17:54:45Z, run `eb6562e` versus head `563977e`.

## Historical workflows

Only runs whose workflow IDs were absent from a complete current inventory appear here. Reasons for removal were not inferred.

- gb.automation.smoketests.sudoku.poc: Pages (workflow 327141965), latest observed **success**, 2026-09-30T22:30:19Z; [run 36785950531](https://github.com/GBrooks1970/gb.automation.smoketests.sudoku.poc/actions/runs/36785950531). Excluded from current CI totals.
- mobile-forex-automation: Pages (workflow 312587270), latest observed **success**, 2026-07-27T07:22:31Z; [run 30245917916](https://github.com/GBrooks1970/mobile-forex-automation/actions/runs/30245917916). Excluded from current CI totals.
- loan-origination-parity: Deploy Next.js site to Pages (workflow 370356556), latest observed **failure**, 2026-09-29T17:37:09Z; [run 36606222022](https://github.com/GBrooks1970/loan-origination-parity/actions/runs/36606222022). Excluded from current CI totals.

Loan Origination acceptance passed: current CI is GREEN at matching main SHA, while the absent Pages workflow's 29 September failure remains visible above. Historical failures are preserved rather than erased.

## History windows inspected

Each query requested at most 100 newest default-branch runs. No exhaustive historical-retention claim is made.

| Project | Retrieved runs | Oldest observed | Newest observed |
|---|---:|---|---|
| magento-checkout-automation | 100 | 2026-06-06T15:13:23Z | 2026-10-26T06:03:17Z |
| hand-baked-screenplay-pattern | 68 | 2026-06-11T17:41:48Z | 2026-09-03T14:35:18Z |
| calculator-screenplay-bdd | 51 | 2026-06-13T10:40:25Z | 2026-08-19T14:37:20Z |
| gb.automation.smoketests.sudoku.poc | 100 | 2026-07-27T20:52:09Z | 2026-11-01T12:32:23Z |
| bfx-ws-screenplay | 100 | 2026-08-07T13:46:01Z | 2026-11-02T09:30:42Z |
| orangehrm-pim-automation | 89 | 2026-06-23T17:46:39Z | 2026-10-27T21:43:34Z |
| markdown-renderer | 37 | 2026-07-05T15:43:46Z | 2026-08-08T16:18:42Z |
| mobile-forex-automation | 54 | 2026-07-08T22:03:03Z | 2026-08-19T14:10:44Z |
| parabank-bank-automation | 100 | 2026-08-24T03:36:57Z | 2026-11-02T11:17:15Z |
| juice-shop-dast-automation | 23 | 2026-08-06T12:49:07Z | 2026-10-07T13:28:51Z |
| auth-separation | 23 | 2026-08-15T07:04:42Z | 2026-09-07T16:33:42Z |
| auth-separation-screenplay-poc | 8 | 2026-09-07T18:09:05Z | 2026-09-10T17:51:46Z |
| saleor-graphql-automation | 44 | 2026-09-05T01:02:30Z | 2026-11-02T18:27:44Z |
| tradeblotter-wpf-screenplay | 8 | 2026-09-19T19:38:01Z | 2026-09-30T05:33:47Z |
| loan-origination-parity | 31 | 2026-09-27T23:10:16Z | 2026-10-07T08:20:20Z |
| credit-dashboard-sut | 100 | 2026-10-14T09:16:11Z | 2026-10-23T20:00:58Z |
| azure-dotnet-platform | 0 | none | none |
| portfolio-prompts | 100 | 2026-07-14T13:54:45Z | 2026-11-02T19:29:44Z |

**Registry-drift watchlist:** None declared.

**Read-only confirmation:** The portfolio inspection made no repository changes, ran no tests, and refreshed no remote Git state. This acceptance artifact is outside the repositories. It records the merged source and installed behaviour without creating a new branch or changing backlog state.
