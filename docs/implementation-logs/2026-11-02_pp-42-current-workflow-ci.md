# PP-42: distinguish current CI from historical workflows — 2026-11-02

## Session Summary

Action 3 changes the portfolio-status reporting contract to aggregate currently active workflows by stable ID and retain inactive and historical evidence separately. Source-preview acceptance classifies Loan Origination's current CI as GREEN while preserving its absent Pages workflow's failed run. Release 0.7.5 is prepared for review; the installed package remains 0.7.4 until owner-approved merge. PP-42 remains open because installation and fresh installed whole-portfolio acceptance are still required.

## Objectives

1. ✅ Implement the approved inventory-aware reporting rules without changing application repositories or GitHub workflows.
2. ✅ Review the classification scenarios, execute the required negative checks and run the existing library gates.
3. ✅ Prepare the implementation log and separate portfolio-prompts v11 handover pair.
4. ⏸️ Owner-approved merge, exact-main CI, supported installation, source/cache parity and fresh installed portfolio-status report.

## Test Results

| Check | Before | After | Result |
|---|---|---|---|
| Loan Origination source-preview classification | Legacy union of latest historical workflow runs produces RED | Active inventory selects successful CI; current GREEN and historical Pages failure both visible | PASS |
| Negative: legacy rule against required current GREEN | Defect reproduced | Assertion rejects RED as expected | PASS, expected assertion failure |
| Negative: hide an active failed run | Deliberately incorrect success-only filtering produces GREEN | Assertion rejects GREEN against required RED | PASS, expected assertion failure |
| Scenario review | No recorded scenario matrix | 18 manually reviewed rows in the scenario document | Reviewed; not automated LLM tests |
| Registry renderer and complete library gate | Not rerun before edits | Exit 0 in 39.790 s for the first combined run | PASS |

The negative checks executed at `2026-11-02T19:03:00.943144+00:00`. Their captured outputs and inputs are preserved in [CI classification scenarios](../portfolio-status-ci-scenarios.md). The temporary validation replay is not shipped aggregation tooling. The final document/packaging gate and PR checks are recorded in handover v11; no test count is inferred from the gate's summary.

The final combined registry/library rerun passed in **39.405 s**. The v11 pair passed metadata/body parity, eight-section, preserved-CSS and local-link checks; the manifest reports **128 handovers across 19 subjects, all pairs complete**.

Read-only API evidence: active workflow `368592048`; successful main run [37593097097](https://github.com/GBrooks1970/loan-origination-parity/actions/runs/37593097097), created 7 October, matching observed main SHA `59671e5397589f260136078494d562f6f66bbf23`. The newest observed failed Pages run [36606222022](https://github.com/GBrooks1970/loan-origination-parity/actions/runs/36606222022), created 29 September, belongs to workflow ID `370356556`, absent from the complete current inventory. The bounded history query returned 31 runs spanning 27 September to 7 October. No workflow was changed or rerun.

## Changes Implemented

### Current, inactive and historical evidence

`portfolio-status.prompt.md` now discovers complete workflow inventory, joins runs by ID, and queries each inventoried workflow's latest default-branch run. Current aggregation uses active workflows, with explicit precedence for unavailable evidence, failures, running work, missing runs and other non-success conclusions. It exposes run/head freshness limits. Inactive workflows stay in Attention needed; absent-workflow history remains separately dated and linked.

Before: a failed retired Pages run made Loan Origination RED. After: its successful active CI is GREEN; the Pages failure remains a historical observation outside current totals. An active failure cannot be discarded to obtain GREEN.

### Release and backlog records

The two plugin manifests identify 0.7.5 and `0.7.5+codex.20261102190301`. Backlog v32 records PP-42 as the sole open MEDIUM item and reconciles PP-41 with its verified source merge `ef43b0edf59a29e1553f19490513c4baf900ef59` and support merge `8387bcbb7412a6fcf8f12088d3067b14404683c5`. No installed cache or historical log was edited.

## Technical Decisions

| Decision | Rationale | Alternative rejected |
|---|---|---|
| Keep policy in the canonical prompt | The existing skill wrapper already delegates there | Duplicate rules or introduce a new aggregation service |
| Join by workflow ID and query each inventoried workflow | Names can collide/change and global history can omit low-frequency runs | Group by display name or infer current membership from run history |
| Keep inactive workflows visible | A disabled workflow is materially different from an absent one | Hide disabled workflows as retired history |
| Preserve incomplete evidence and freshness limits | GREEN is a claim about observed successful active runs | Infer current health from missing queries or old runs |
| Install only after owner-approved merge | Follows the approved plan's publication boundary | Refresh the installed package before review |

This is a bounded reporting-contract change; no structural architecture decision or new ADR was required. Source base: `ef43b0edf59a29e1553f19490513c4baf900ef59`; support base: `8387bcbb7412a6fcf8f12088d3067b14404683c5`.

## Documentation Updates

- `portfolio-status.prompt.md` — inventory-aware classification, current totals and separate history.
- `docs/portfolio-status-ci-scenarios.md` — scenario review and actual acceptance evidence.
- `docs/backlog.md` v32 — PP-42 state and PP-41 merge reconciliation.
- `docs/implementation-plans/2026-11-02_pp-42-current-workflow-ci-aggregation.md` and `_index.md` — approval and outcome boundary.
- This append-only implementation log.
- Root `session-notes/portfolio-prompts_session-notes_v11_20261102T1905Z.md` and `.html` — separate resumable handover.
- Root ignored `session-notes/manifest.json` — regenerated discovery only.

## Lessons Learned

- A run-history API answers a different question from the current workflow inventory. Keep both to avoid erasing evidence while correcting present status.
- Unknown workflow membership prevents a retirement claim. Disabled membership is evidence that deserves a visible note.
- Manual prompt review, a validation replay, library integrity checks and installed-agent acceptance are different evidence stages.

## Recommendations / Next Steps

- [ ] Owner: review and merge the source PR, then the corresponding root handover PR.
- [ ] Agent after merge: verify exact-main CI, install 0.7.5 through the supported command, compare release-bearing source/cache files and run the refreshed status skill across the whole registry.
- [ ] Close [PP-42](../backlog.md#outstanding-items) only after installed acceptance, with a new immutable completion log/handover recording the actual outcome.

*Session logged: 2026-11-02. Author: Codex.*
