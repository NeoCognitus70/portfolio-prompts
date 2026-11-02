---
version: 1
created: 2026-11-02T18:40Z
project: portfolio-prompts
type: implementation-plan
item: PP-42
status: approved
approved: "2026-11-02, owner approved implementation; owner retains merge authority; install only after merge"
delivered: not yet
language: en-GB
---

# Implementation plan: Action 3 — distinguish current CI from retired workflows

**Goal.** Correct portfolio-status aggregation so that historical failures from retired workflows remain visible without making currently successful workflows appear to be failing. Preserve the skill's strictly read-only execution boundary and conservative treatment of incomplete evidence.

## Evidence gathered before planning

Read-only inspection on 2 November 2026 covered the canonical status prompt, its skill wrapper, backlog v31, handover v10, the shared planning template and GitHub workflow inventory/run history. These inspections changed no repository or remote state. Only this proposed plan and its index entry are written in this planning batch.

| Finding | Consequence for the plan |
|---|---|
| `portfolio-status.prompt.md` Step 2 selects the newest run per workflow from recent run history without checking current workflow inventory | Replace that selection rule with inventory-aware classification |
| Loan Origination currently lists only active workflow ID 368592048, `CI`, at `.github/workflows/ci.yml` | Aggregate this workflow's latest default-branch run as current evidence |
| Its latest CI run, [37593097097](https://github.com/GBrooks1970/loan-origination-parity/actions/runs/37593097097), succeeded on 7 October at `59671e5397589f260136078494d562f6f66bbf23` | Show the observed run date and revision; a successful old run does not establish fresh coverage of a different HEAD |
| Failed Pages run [36606222022](https://github.com/GBrooks1970/loan-origination-parity/actions/runs/36606222022) dates from 29 September; its workflow is absent from the current listing | Retain this as historical evidence, outside current CI aggregation, subject to a complete inventory check at implementation time |
| The skill wrapper delegates to the canonical prompt | Keep aggregation rules in the prompt rather than duplicating them in the wrapper |
| PP-41 is the latest backlog identifier; its source changes are now merged in `ef43b0e` | Reserve PP-42 provisionally; recheck before adding it to the backlog after approval |

## Steps

1. After approval, recheck repository state, latest handover, backlog IDs and the live workflow inventory. Create `codex/pp-42-current-workflow-ci` from current main. Preserve unrelated root work.
2. Specify the reporting contract in `portfolio-status.prompt.md` Steps 2 and 3:
   - Discover the repository's default branch and collect the complete paginated workflow inventory, retaining IDs, names, paths and states.
   - Match runs by stable workflow ID, not display name. Query default-branch runs for every inventoried workflow; avoid losing a low-frequency workflow behind a fixed global run limit. Retain run timestamp, revision, event and URL.
   - Aggregate latest runs for active workflows as **current CI** using the existing RED / RUNNING / MIXED / GREEN / NO RUNS / UNAVAILABLE vocabulary. GREEN requires a successful latest run for every active workflow. A successful query with no run for an active workflow prevents GREEN and produces NO RUNS unless a known failure/running condition takes precedence; list missing coverage explicitly.
   - Treat incomplete inventory or failed run queries as UNAVAILABLE rather than classifying missing evidence as retirement. Preserve known failures in Attention needed even when aggregation is unavailable.
   - Report inventoried but disabled workflows separately, including their state and latest known run. Do not call them retired or quietly hide them. If no active workflow exists, use NO RUNS with an explicit explanation, not GREEN.
   - Classify a historical run as belonging to a retired/absent workflow only when a successful complete inventory lacks its ID. Preserve its latest observed conclusion and link in a historical-workflow note; exclude it from current CI totals. Label the inspected history window and do not imply an exhaustive historical audit.
   - Label the table column and portfolio totals as current CI. Keep disabled workflows, incomplete evidence and historical failures in distinct explanatory notes. Historical failure alone must not increment the current RED count.
3. Add `docs/portfolio-status-ci-scenarios.md` with the acceptance cases below and expected report fragments. This is a prompt-contract change, so use scenario-based review and live read-only acceptance rather than introducing a new aggregation service or runtime dependency.
4. Update `docs/backlog.md` with PP-42 and its actual delivery state. Update this plan's outcome and `_index.md` after execution; preserve the approved plan body. Reconcile PP-41's publication wording with its verified merge as necessary to avoid carrying stale pending-publication claims forward.
5. Bump `.claude-plugin/plugin.json` to proposed patch release 0.7.5 and `.codex-plugin/plugin.json` to the same release plus a fresh execution-time cachebuster, subject to rechecking concurrent releases. Run the existing registry/library gates. Publish a draft library PR for owner review.
6. Following owner-approved merge, verify exact-main CI, install via `codex plugin add portfolio-prompts@portfolio-prompts --json`, and check release-bearing source/cache parity. Never edit cache files directly. Exercise the refreshed status skill read-only and capture the actual Loan Origination result.
7. Write `docs/implementation-logs/YYYY-MM-DD_pp-42-current-workflow-ci.md` with measured evidence. Create the next numerical portfolio-prompts handover (expected v11) as Markdown and generated HTML in root `session-notes/`, preserving earlier records. Regenerate/check the ignored manifest. Publish the root records through their own branch and draft PR; record any remaining publication boundary honestly.

## Verification

| Acceptance case | Required result |
|---|---|
| Active CI succeeds; absent Pages workflow has a historical failure | Current GREEN; dated Pages failure retained separately |
| Active workflow fails; another succeeds | Current RED; no suppression of the active failure |
| Workflow remains in inventory but is disabled | Explicit disabled-workflow attention note; never labelled retired |
| Two distinct workflow IDs share a name | Keep them distinct; a failure in one cannot be overwritten by success in the other |
| Active workflow has no runs | Never GREEN; explicit missing run coverage |
| Inventory fails, is truncated, or cannot be completed | UNAVAILABLE; no inferred retirement |
| Active run is queued/in progress, cancelled, skipped or otherwise non-success | Preserve the existing conservative status semantics; explain exceptions |
| A low-frequency active workflow lies beyond the initial global run page | Its latest run still contributes through per-workflow discovery |
| Successful run predates the observed default-branch head | Expose run date/SHA and coverage limitation without claiming exact-head success |

**Required negative check:** replay the Loan Origination case using the old union-of-run-history rule; it must produce the undesired RED and fail the new expected-current-GREEN acceptance assertion. A candidate rule that discards an active failure must also fail acceptance. Record actual outcomes, not merely the existence of examples.

Run `python -B tools/render-registry.py --check`, `python -B tools/check-library.py`, and `git diff --check` in the library. Review all scenario outputs against the table above. After installation, capture a fresh read-only portfolio-status report and confirm current totals exclude retired workflow results while disabled workflows and historical evidence remain visible. For the handover, verify metadata/body parity, relative links and `build-handover-manifest.py --check`.

## Delivery

Owning repository: `portfolio-prompts`. This action changes reporting policy, examples and release/documentation records. It does not change Loan Origination code, GitHub workflow files, enabled/disabled states, dependencies or historical runs. No workflow rerun or application test suite is needed to alter reporting policy.

Implementation branch: `codex/pp-42-current-workflow-ci`; support records branch: `codex/pp-42-ci-reporting-handover`. Owner reviews and merges each PR. Approval to implement does not authorise an automatic merge. If inventory/run semantics or acceptance cases expose a need for executable tooling, return with a revised plan before expanding scope.

## Decisions put to the owner

| Decision | Options | Recommended | Owner's answer |
|---|---|---|---|
| Approve this bounded implementation | Implement reporting correction / revise scope / defer | Implement after approval | Approved by owner, 2026-11-02 |
| Treatment of disabled workflows | Separate visible attention note / conflate with retired history | Separate visible note | Approved by owner, 2026-11-02 |
| Publication and installation | Owner-reviewed merge, then supported install / local pre-merge installation | Merge first, then install and verify | Approved by owner, 2026-11-02 |

## Outcome

Owner approved the plan on 2 November 2026. The canonical prompt, 18-row manual scenario review and 0.7.5 release metadata are implemented in the source branch. Both executed negative checks passed by rejecting their deliberately incorrect results; the Loan Origination source preview is current GREEN with the failed Pages run retained as historical evidence. The initial combined registry/library gate passed in 39.790 s and the final rerun passed in 39.405 s. Handover parity/link checks and the 128-pair manifest check passed. The separate implementation log and v11 Markdown/HTML handover record this review boundary. Owner-approved merge, exact-main CI, installation/parity and refreshed whole-portfolio acceptance remain later gates.
