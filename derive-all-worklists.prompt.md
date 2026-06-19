# Prompt — Derive worklists for all projects (parallel fan-out)

Paste the text below to the agent when you want **worklists prepared across the portfolio in one
pass** — or invoke it without pasting:
`Read and follow portfolio-prompts\derive-all-worklists.prompt.md`.
It launches one sub-agent per project, each following `derive-worklist.prompt.md` for its project
in parallel, then collates every detailed breakdown into a single report. **Nothing is actioned**
— the same no-actioning rule applies as in the single-project prompt.

No `PROJECT=` is needed (the target is the whole registry). To restrict the fan-out, append
`PROJECTS=<folder>,<folder>,...` — e.g.
`... using PROJECTS=hand-baked-screenplay-pattern,gb.automation.smoketests.sudoku.poc`.

---

You are **orchestrating worklist derivation across the portfolio**. You do not derive any
worklist yourself and you write no files — your sub-agents do the per-project work; your job is
the fan-out and the collated report. (This is the portfolio-scoped exception to the `PROJECT=`
rule in `portfolio-prompts/project-layout.md`: the orchestration needs no `PROJECT=`; every
sub-agent receives its own.)

## Step 1 — Establish the project list

Read the **project registry** table in `portfolio-prompts/README.md`:

- If the invocation names `PROJECTS=`, use exactly that subset (validate each name against the
  registry — an unknown name is reported, not guessed at).
- Otherwise take **every registry row**, including projects marked Complete (their derivation
  honestly returning "nothing actionable" is a useful confirmation, and a stale "Complete" claim
  would surface here). Skip only rows whose status says **not onboarded**.

Note for the report which projects already have a `WORKLIST_{PROJECT}.md` at the portfolio root —
expect their agents to stop at the guard rather than derive.

## Step 2 — Fan out (one sub-agent per project, all in the same turn)

Launch **one sub-agent per project**, all in a single turn so they run in parallel. This is safe
by design: each agent writes at most one file (`WORKLIST_{PROJECT}.md`, names disjoint per
project) and is otherwise read-only.

**Launch-count check:** the number of agents you launch this turn must equal the number of projects
in scope from Step 1 — count them off explicitly before moving on; a forgotten agent is a silent
gap.

Each sub-agent's prompt must be **self-contained** (sub-agents start with no conversation
context). Use this template, filling both placeholders:

```text
Working directory: <absolute path of the portfolio root>
Read and follow portfolio-prompts\derive-worklist.prompt.md using PROJECT=<project folder name>
Follow it exactly, including the Step 0 guard (never overwrite an existing
WORKLIST_{PROJECT}.md) and the no-actioning rule (read-only in the project
repo; the only file you may write is WORKLIST_{PROJECT}.md at the portfolio
root). You are running unattended: wherever that prompt says to ask the user,
do NOT wait for an answer - record the question, stop that path, and carry the
question in your report. Your final message must be the prompt's Step 4
detailed breakdown, or the stop report (existing worklist / nothing
actionable / blocked), in full - it is the only thing returned to the
orchestrator.
```

If the environment cannot launch sub-agents, say so and fall back to running
`derive-worklist.prompt.md` for each project **sequentially yourself**, in registry order, with
the same unattended rule. In that mode you act as each sub-agent in turn, so the per-project
rules apply to you — including writing that project's `WORKLIST_{PROJECT}.md` (the
orchestrator-writes-nothing rule below applies only to the fan-out mode). Do not silently skip
projects.

## Step 3 — Collate the report

When all agents return, produce one report grouped by project, in registry order:

- **Derived** — projects that got a new `WORKLIST_{PROJECT}.md`: the file path, item count, and
  the agent's full Step 4 breakdown (per-item source, what/why, acceptance criteria, type/effort,
  risks). Do not summarise away the detail — the user reviews from this report.
- **Stopped at the guard** — projects with a pre-existing worklist: its current state
  (checked/unchecked/blocked counts) as the agent reported it.
- **Nothing actionable** — projects whose agent honestly derived no items (no file written).
- **Failed or blocked** — any agent that errored or could not complete: the error, and whether
  you re-ran it (re-run a failed agent **once**; report a second failure rather than looping).

Close with the cross-portfolio view:

- Every **user decision** carried in any worklist or report (e.g. an undecided remediation
  strategy), gathered into one list — these need answers before the loops run.
- Suggested next `/loop` invocation line **per derived worklist**.
- Any registry/backlog mismatches the agents flagged, so the source of truth can be fixed.

## Rules

- Follow the **shared orchestration conventions** in `portfolio-prompts/project-layout.md`
  §"Orchestration fan-out" (no `PROJECT=` for the orchestrator; one agent per project, never two on
  the same tree; launch-count check; unattended; sequential fallback; re-run a failed agent at most
  once; relay faithfully).
- **Mode-specific (no-actioning):** in fan-out mode you write **no files** and make **no project
  changes** — only sub-agents write, and only their own `WORKLIST_{PROJECT}.md` (in the sequential
  fallback you write exactly those files yourself, nothing else).
- en-GB spelling.
