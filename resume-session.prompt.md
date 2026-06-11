# Prompt — Resume from the latest handover

Paste the text below to the agent at the **start** of a new session. It picks up the most recent
handover, cross-checks it against the source of truth and the live repo, and proposes where to start.

---

You are resuming work on the **magento-checkout-automation** portfolio project in a fresh session with
no prior context. Orient yourself from the handover trail before doing anything else — do not start
changing code until you have reconciled the three sources below and confirmed the plan.

## Step 1 — Load the latest handover
In the **`session-notes/`** folder at the portfolio root (`test-automation-portfolio/session-notes/`),
find the **highest-numbered** `magento-checkout-automation_session-notes_v{N}_*.md` and read it in full.
That is your primary
briefing.

**Guard against strays:** also glob the portfolio root itself for misplaced
`*session-notes_v*` files (a v11 was once written to the root and silently missed by the next
session). If any exist, flag them in your orientation summary, treat whichever file carries the
highest version *and* latest timestamp as the true latest, and recommend moving the stray into
`session-notes/`. If its "Read first" section names one or two earlier handovers as still-relevant, read those
too — but treat the highest version as authoritative where they disagree.

## Step 2 — Load the source of truth
Read `magento-checkout-automation/docs/backlog.md`. This is the authoritative record of item status,
priorities, and the credibility checklist. Where the handover narrative and the backlog disagree, the
**backlog wins** — but flag the discrepancy.

## Step 3 — Verify against the live repo (don't trust, check)
Run and read the actual state; the handover may be stale:
- `git -C magento-checkout-automation status --porcelain` — is the tree clean or mid-change?
- `git -C magento-checkout-automation branch -vv` — what branch are we on; is it the one the handover left?
- `git -C magento-checkout-automation log --oneline -15` — does HEAD match the "Repository state" commit
  the handover claimed?
- `gh pr list` (from inside the repo) — any PRs open that the handover expected merged, or vice versa?

Reconcile: confirm the latest commit named in the handover's "Repository state" section is present, and
note anything that has moved since (new commits, merged/closed PRs, a dirty tree).

## Step 4 — Confirm the resume point
Produce a short orientation summary, then propose the next move:
- **Where things stand:** project status (1–2 lines) + which handover version you loaded.
- **Open work:** the outstanding backlog item(s), taken from `docs/backlog.md` (the source of truth)
  and cross-checked against the latest handover — list what is actually open now; do not assume or
  carry forward a remembered snapshot.
- **Repo reality check:** branch, HEAD commit, tree clean/dirty, open PRs — and any mismatch vs the handover.
- **Working norms to respect** — the **single source** for these is the "Durable lessons" and
  working-norms sections of the latest handover you loaded in Step 1; restate them from there
  rather than from memory. Two that always apply: **all** changes to `main` go via branch + PR —
  as of 2026-06-10 the harness blocks even docs-only direct pushes — and don't
  `docker compose down -v` locally if you want to keep the seeded store.
- **Proposed next action:** the single most sensible thing to do next, with the concrete first steps.

Then **stop and wait** for the user to confirm or redirect before making changes. Don't begin
implementation off the back of your own summary unless the user says go.

## Task-completion reporting (apply to every finished task)

At the end of **each finished task** in the session — not only at session close — report back with:

- **Remaining tasks** — the still-open / uncompleted items (open questions, held
  branches, carry-forward lint/structural findings), grouped as **actionable-now / blocked /
  monitor-only** so the operator can see what is left.
- **Recap of session work completed** *(optional)* — a short summary of what this task changed (files,
  commits, validations), included when it aids continuity.
- **Recommended next steps for approval** — a short ranked list of candidate next actions, drawn from
  the backlog tiers (HIGH → MEDIUM → LOW), presented for the operator to choose from. **Stop for
  approval before starting the next task** — do not chain into new project work unprompted.

## Rules
- en-GB spelling. Today's date is the real current date — use it when reasoning about staleness.
- Cite what you read (handover version, backlog item numbers, commit hashes) so the user can trust the
  reconciliation.
- If the three sources are mutually consistent, say so explicitly — that's a useful signal too.
