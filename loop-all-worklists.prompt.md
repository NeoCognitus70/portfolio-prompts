# Prompt — Work all worklists in parallel (loop fan-out)

Paste the text below to the agent when you want **every prepared worklist actioned in one pass** —
or invoke it without pasting:
`Read and follow portfolio-prompts\loop-all-worklists.prompt.md`.
It launches one sub-agent per project that has a worklist with unchecked items; each sub-agent
executes `loop-worklist.prompt.md` iterations for its project. Unlike `derive-all-worklists`,
this fan-out **mutates**: agents implement, commit, push, and open PRs (never merge them).

To restrict the fan-out, append `PROJECTS=<folder>,<folder>,...`. To cap how much any one agent
does in this pass, append `MAXITEMS=<n>` (per project).

**When to prefer this over a single `/loop`:** worklists are short, decisions are pre-recorded,
and the projects are independent. Prefer one project at a time when a worklist is long or risky
(quality and reviewability beat wall-clock time), or when you want to review PRs incrementally.

---

You are **orchestrating worklist execution across the portfolio**. You implement nothing
yourself and write no files — your sub-agents do the per-project work; your job is target
selection, the coupling check, the fan-out, and the collated report. (Portfolio-scoped
orchestration: no `PROJECT=` is needed; every sub-agent receives its own — see the exception in
`portfolio-prompts/project-layout.md`.)

## Step 1 — Establish the targets

1. Glob the portfolio root for `WORKLIST_*.md`. A project is a target if its worklist has at
   least one unchecked `- [ ]` item (honour `PROJECTS=` if given; validate names against the
   README registry).
2. Read each target worklist in full. Note per project: unchecked item count, recorded
   `**DECISION**` blocks (these prevent stops), and any items already marked `BLOCKED`.
3. Skip — and report as skipped — any target whose repo working tree is dirty with
   unrecognised changes, or that the registry marks not onboarded.

## Step 2 — Coupling check (do this before any fan-out)

Two projects must **never run concurrently** if one's build or test touches the other's working
tree. Consult the registry rows for recorded couplings — e.g. `calculator-screenplay-bdd`'s
`prepare:screenplay` installs and builds **inside** the sibling `hand-baked-screenplay-pattern`
checkout, so a concurrent hand-baked agent would race a build in its own tree.

Partition the targets: independent projects each get their own parallel agent; coupled projects
are assigned to **one sequential agent** that works them one after the other (library/provider
project first, consumer second). State the partition in the report before launching.

## Step 3 — Fan out

Launch the agents for one wave **in the same turn** (parallel). **Launch-count check:** agents
launched this wave must equal the wave's targets, **including the one sequential agent for any
coupled pair** (the count that has been missed before) — confirm explicitly before proceeding.
Each sub-agent's prompt must be self-contained:

```text
Working directory: <absolute path of the portfolio root>
Read and follow portfolio-prompts\loop-worklist.prompt.md using PROJECT=<project folder name>
You cannot schedule wake-ups, so execute iterations CONSECUTIVELY in this
run: complete one item fully (implement -> validate -> verify -> commit ->
record in WORKLIST_<project>.md), then proceed to the next unchecked item,
until all items are done or blocked<, or you have completed <MAXITEMS> items>.
Every per-item rule applies unreduced: gates must pass before every commit;
never commit on red; all changes via branch + PR; create the worklist branch
from an up-to-date default branch (git fetch; switch main; pull --ff-only);
open the PR when the first item is ready and push subsequent items to the
same branch; your OWN open worklist PR is not a stop condition; NEVER merge
a PR.
You are running unattended: wherever the prompt says to ask the user, do NOT
wait - mark the item BLOCKED (reason) in the worklist, record the question,
and move to the next item. Honour every stop condition; if one ends the run
early, say so. Stay strictly inside your own project's repo and your own
WORKLIST file - other agents are working sibling projects concurrently.
Your final message must be the loop's closing report: items completed (with
commit hashes and gate evidence), items blocked (with their questions), PRs
opened (URLs), worklist state, and follow-on items you added - in full; it
is the only thing returned to the orchestrator.
```

For a sequential agent covering coupled projects, list both projects in dependency order and
instruct it to finish (or block) every item of the first before touching the second.

If the environment cannot launch sub-agents, fall back to working the projects **sequentially
yourself** in the same dependency-respecting order — the per-project rules then apply to you,
including the writes.

## Step 4 — Collate the report

When all agents return, report per project, in registry order:

- **Completed items** — id, commit hash(es), gate evidence as the agent cited it.
- **Blocked items** — the recorded question or failing gate, verbatim.
- **PRs opened** — URL + one-line contents; all await the user's review and merge.
- **Worklist state** — checked/unchecked/blocked counts after the run.
- **Follow-on items** the agent added while staying on-scope.

Close with the cross-portfolio view:

- Every PR awaiting merge, as one list in suggested review order (independent/docs-only first).
- Every blocked question needing a user answer.
- Whether any project now warrants `write-handover.prompt.md` or an implementation log (per its
  own conventions), as recommendations only.
- Anything that went wrong, faithfully: an agent that died mid-item, a gate skipped, a tree left
  dirty — never round up.

## Rules

- Follow the **shared orchestration conventions** in `portfolio-prompts/project-layout.md`
  §"Orchestration fan-out" (no `PROJECT=` for the orchestrator; one agent per project, coupled
  projects share one sequential agent, never two on the same tree; launch-count check; unattended;
  sequential fallback; re-run a failed agent at most once; relay faithfully).
- **Mode-specific (mutating):** in fan-out mode you write **no files** and make **no repo
  changes** — only sub-agents write, each inside its own project repo and its own
  `WORKLIST_{PROJECT}.md` (in the sequential fallback those writes are yours, project by project).
  Sub-agents never merge PRs, never push to `main`, never delete branches.
- en-GB spelling.
