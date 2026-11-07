---
version: 1
created: 2026-11-07T05:31Z
project: portfolio-prompts
type: implementation-plan
item: loan-origination-parity lifecycle
status: approved
approved: "2026-11-07, owner instruction to investigate and resolve the reported project issues; merge remains with owner"
delivered: not yet
language: en-GB
---

# Implementation plan: reconcile Loan Origination lifecycle

**Goal.** Match the registered lifecycle to the project's zero-open backlog and verified publication while preserving the completed-phase label, showcase role and orchestration eligibility.

## Evidence gathered before planning

A dedicated read-only investigation found clean main \`71089cabb56b527ffaf222dc2fc8af90ec864a97\`, backlog v8 with zero open and four resolved risks, and no open PRs. [PR #21](https://github.com/GBrooks1970/loan-origination-parity/pull/21) merged on 3 November at 23:32:21 UTC. [Main CI 41739941194](https://github.com/GBrooks1970/loan-origination-parity/actions/runs/41739941194) passed 8/8 jobs in a 209-second run span. The published parity page identifies that same commit and run, with PASS and 33/52/21 rows. All four linked Serenity reports returned HTTP 200. The old starter deployment workflow was deliberately removed by PR #14; its historical failure is not active work.

## Steps

1. Set only the Loan Origination registry row's lifecycle to \`resting\`; retain its completed-phase label, presentation role and orchestration flag.
2. Append a concise evidence note describing backlog v8 and the merged maintenance fix. Generate the README registry table mechanically.
3. Verify the generator detects the stale table before regeneration, then passes after regeneration. Run the existing library self-gate and whitespace check.
4. Publish a draft library PR. Shared handover v3 and the cross-project walkthrough belong to the portfolio support repository and its separate draft PR.

## Verification

The negative control is the existing \`render-registry.py --check\` against a changed registry and stale README: it must exit 1. After generation it must exit 0. Run \`python -B tools/check-library.py\` in a scratch workspace with the registered sibling checkouts available. No new tests or application reruns are needed for this record correction.

## Delivery and decisions

Branch \`codex/loan-resting-registry-20261107\`. The user authorised resolution of this reported lifecycle mismatch. The owner retains approval of each merge. Optional future features remain unpromoted. No workflow run, historical result, project source or installed plugin cache is altered.

## Outcome

The Loan Origination lifecycle is now resting in this branch; its phase label, showcase role and orchestration flag are unchanged. The generated README includes the refreshed evidence note. The stale-table negative control exited 1 as required, regeneration and its check exited 0, the full library self-gate passed, and git diff --check passed. No application tests were rerun. Draft PR publication and owner merge are the remaining delivery stages; installed plugin caches remain unchanged.
