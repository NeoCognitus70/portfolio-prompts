# Portfolio status: current CI classification scenarios

The [canonical status prompt](../portfolio-status.prompt.md) owns the reporting rules. This document supplies review cases and captured acceptance evidence for PP-42; it is not an executable classifier or a replacement for the prompt. IDs identify workflows; display names do not.

## Scenario review

Reviewed against the candidate prompt on 2 November 2026. Each row records the expected result and the result obtained by applying the written decision order. These are **18 manually reviewed scenario rows**, not 18 automated tests or 18 independent agent executions. Unless specified otherwise, inventory and per-workflow queries are complete and successful.

| Case | Input | Expected current result and required note | Reviewed result |
|---|---|---|---|
| C01 | Active CI succeeds; failed Pages run has an ID absent from complete inventory | GREEN; dated historical Pages failure retained separately | GREEN + historical note; pass |
| C02 | Active ID 1 fails; active ID 2 succeeds | RED; ID 1 failure linked in Attention needed | RED; pass |
| C03 | Active ID 1 succeeds; inventoried ID 2 is disabled_inactivity with a failed latest run | GREEN; ID 2 state/failure visible in Attention needed, not called retired | GREEN + disabled note; pass |
| C04 | Two active IDs have the same display name; one fails | RED; preserve both IDs | RED; pass |
| C05 | Inventory contains only disabled workflows, or is successfully empty | NO RUNS; explain no active workflows and list inactive states where present | NO RUNS; pass |
| C06 | One active workflow has no runs; another succeeds | NO RUNS; name missing coverage | NO RUNS; pass |
| C07 | An active workflow fails; another has no runs | RED; both failure and missing coverage retained | RED + missing coverage; pass |
| C08 | An active workflow is running; another has no runs | RUNNING; missing coverage retained | RUNNING + missing coverage; pass |
| C09 | Inventory fails or pagination is incomplete | UNAVAILABLE; no inferred retirement | UNAVAILABLE; pass |
| C10 | An inventoried workflow's run query fails; a known active failure is available | UNAVAILABLE; known failure remains in Attention needed | UNAVAILABLE + failure note; pass |
| C11 | Inventory contains an unrecognised workflow state | UNAVAILABLE; retain raw state | UNAVAILABLE; pass |
| C12 | Latest active run is queued, requested, waiting, pending or in_progress; none is red | RUNNING for each listed status | RUNNING; pass |
| C13 | Active latest runs include cancelled, skipped, neutral, stale, null or unrecognised conclusions; none is red/running/missing | MIXED for each non-success variant, even if all conclusions agree | MIXED; pass |
| C14 | Global history's first page omits a low-frequency active workflow whose latest run failed | Per-workflow query discovers it; RED | RED; pass |
| C15 | Every active latest run succeeds but one SHA differs from current default-branch head | GREEN as observed-run status; explicit lack of exact-head coverage | GREEN + freshness limitation; pass |
| C16 | Inventory and active runs succeed; optional history query fails | GREEN; historical evidence UNAVAILABLE, no claim of no historical failures | GREEN + history limitation; pass |
| C17 | One workflow ID has a new display name; its older name appears in history | Use newest run for the same ID; do not create a second retired workflow | One current workflow; pass |
| C18 | All active latest runs succeed; default-branch head SHA cannot be queried | GREEN as observed-run status; freshness unverified, no invented SHA match | GREEN + freshness limitation; pass |

Inactive state coverage includes `disabled_manually`, `disabled_inactivity`, `disabled_fork` and an inventoried `deleted` state. These are visible inactive inventory entries; absence is established only by a complete inventory. A failed latest-run query for an inactive entry is also UNAVAILABLE under the conservative query rule.

## Captured Loan Origination source-preview acceptance

Read-only GitHub API queries on **2 November 2026**, captured before the checks at **19:03:00 UTC**, returned:

- Default branch `main`, head `59671e5397589f260136078494d562f6f66bbf23`.
- Complete paginated inventory: one workflow, active `CI`, ID `368592048`, path `.github/workflows/ci.yml`.
- Its newest main run: [37593097097](https://github.com/GBrooks1970/loan-origination-parity/actions/runs/37593097097), completed/success, event `push`, created `2026-10-07T08:20:20Z`, with a SHA equal to the observed main head.
- Bounded history query: requested newest 100 main runs; received 31, matching the API total for that query. Observed timestamps span `2026-09-27T23:10:16Z` to `2026-10-07T08:20:20Z`. This is an observation of returned run history, not a guarantee of historical retention completeness.
- Newest observed run for absent workflow ID `370356556`, `Deploy Next.js site to Pages`: [36606222022](https://github.com/GBrooks1970/loan-origination-parity/actions/runs/36606222022), completed/failure, created `2026-09-29T17:37:09Z`.

Applying the candidate source prompt yields this CI-only report fragment:

| Project | Current CI |
|---|---|
| loan-origination-parity | GREEN — latest active CI succeeded on 7 October; run SHA matches observed main |

**Historical workflows:** Pages workflow ID 370356556 is absent from the complete current inventory. Its newest observed run failed on 29 September; retain the run link above. It does not contribute to the current RED count. No inactive workflows were returned for this repository.

This is a source-preview acceptance check for one repository. The installed 0.7.4 skill was not updated or credited with this behaviour. Fresh whole-portfolio acceptance using the installed 0.7.5 package remains pending owner-approved merge and supported installation.

## Negative acceptance checks actually executed

At `2026-11-02T19:03:00.943144+00:00`, a temporary validation script replayed the captured history and ran two rejection assertions. It did not become library/runtime tooling or modify any repository under inspection.

1. **Legacy history union:** newest observed run per historical workflow ID includes successful CI and failed Pages. The old aggregation returns RED. The assertion that this equals the required current GREEN failed as expected; the negative check passed. Restricting the replay to the completely inventoried active workflow returned GREEN.
2. **Hidden active failure:** a fixture with active ID 1 failed and active ID 2 successful was passed through deliberately incorrect success-only filtering. That candidate returns GREEN. The assertion that it equals the required RED failed as expected; the negative check passed.

Captured output:

```text
PASS negative 1: legacy history union gives RED and is rejected by expected-current-GREEN assertion
PASS negative 2: success-only filtering hides an active failure and is rejected by expected-RED assertion
```

These checks demonstrate the two failure modes and their acceptance criteria. They do not constitute automated testing of an LLM's future prompt adherence. The existing library gate separately validates packaging, references and established library invariants.
