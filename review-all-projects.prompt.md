# Prompt — Code-review every project (parallel fan-out)

Paste the text below to the agent when you want **a comprehensive code review of every portfolio
project in one pass** — or invoke it without pasting:
`Read and follow portfolio-prompts/review-all-projects.prompt.md`.
It launches one sub-agent per project, each following `write-code-review.prompt.md` for its
project in parallel, then collates the top findings into a single cross-portfolio summary.

Each review is **evidence-only**: a sub-agent reads the code and writes review artefacts into the
project's review folder — it makes **no implementation changes**. The review artefacts are a repo
change, so each agent commits them on a branch and opens a PR (never merging).

To restrict the fan-out, append `PROJECTS=<folder>,<folder>,...`.

---

You are **orchestrating a code review across the portfolio**. You review nothing yourself and
write no files — your sub-agents do the per-project review; your job is target selection, the
fan-out, and the collated cross-portfolio summary. (Portfolio-scoped orchestration: no `PROJECT=`
is needed; every sub-agent receives its own — see the exception in
`portfolio-prompts/project-layout.md`.)

## Step 1 — Establish the targets

Read the **project registry** table in `portfolio-prompts/README.md`:

- If the invocation names `PROJECTS=`, use exactly that subset (validate each name against the
  registry — an unknown name is reported, not guessed at).
- Otherwise take **every onboarded registry row**. Skip only rows whose status says **not
  onboarded** (a project with no `docs/backlog.md`, or no registry-recorded backlog deviation,
  cannot be reviewed against its source of truth — report it as skipped).

Note each project's registry-recorded **deviations** (e.g. the sudoku POC's review folder is
`DOCS/.review/`, its backlog `DOCS/.planning/backlog.md`) — the sub-agents need these, and the
review's output location follows them.

## Step 2 — Parallelism and the coupling note

A code review **reads** a project's code and **writes** only review artefacts into that project's
own review folder — folders are disjoint per project, so the reviews run in parallel safely.

**One caveat, only if an agent runs the optional validation gates** (`write-code-review` runs them
"if dependencies are available"): where a project's gate builds **inside another project's working
tree** (per the registry coupling notes — e.g. `calculator-screenplay-bdd`'s `prepare:screenplay`
builds the sibling `hand-baked-screenplay-pattern`), two such agents must not run that build
concurrently. Handle it by instructing the coupled agents to **review against the static source
without running the cross-tree build gate** (a review does not require a green build — it reports
on the code as written), or assign the coupled pair to one sequential agent. State which you chose
in the report.

## Step 3 — Fan out (one sub-agent per project, all in the same turn)

Launch **one sub-agent per project**, all in a single turn so they run in parallel. **Launch-count
check:** agents launched must equal the projects in scope from Step 1 (including any sequential
coupled agent) — confirm explicitly before proceeding; a forgotten agent is a silent gap. Each
sub-agent's prompt must be **self-contained** (sub-agents start with no conversation context). Use
this template, filling both placeholders:

```text
Working directory: <absolute path of the portfolio root>
Read and follow portfolio-prompts/write-code-review.prompt.md using PROJECT=<project folder name>
Follow it exactly. Use your real model identity for {AGENT}/{AGENT_NAME} in the
review directory name and reviewer attribution - never copy an identity from a
previous review directory. Write the review into the project's review folder
(.review/, or the location its registry row records as a deviation, e.g.
DOCS/.review/); determine {N} by inspecting existing CODE_REVIEW_*_v* dirs IN
THAT LOCATION for your agent and incrementing, else v1.
Make NO implementation changes - review artefacts only. When validation would
build inside a sibling project's working tree (registry coupling note), review
the static source instead of running that build gate, and say so in the review.
When the review is written, commit it on a branch and open a PR; NEVER merge it.
Create the branch from an up-to-date default branch (git fetch; switch main;
pull --ff-only; then branch review/<project>-<agent>-vN) so the PR carries only
the review, not stale history; a clean tree on the wrong branch means switch,
not stop. If you must wait on anything (e.g. a validation run), wait in the
FOREGROUND - do not background and end your run.
You are running unattended: wherever the prompt says to ask the user, do NOT
wait - record the question in the review and your report and proceed.
Your final message must be the prompt's "Finish by reporting" block in full -
the review directory path, the files created, any validation commands run and
their result, the top 3-5 findings by severity, and the PR URL.
```

If the environment cannot launch sub-agents, fall back to running `write-code-review.prompt.md`
for each project **sequentially yourself**, in registry order. Do not silently skip projects.

## Step 4 — Collate the cross-portfolio summary

When all agents return, produce one report:

**Per project**, in registry order:
- The review directory path and the PR URL (awaiting the user's review/merge).
- Validation run and result (or that it was not run, and why — e.g. the cross-tree build skip).
- The top 3–5 findings by severity, as the agent reported them.
- Any question the agent recorded.

**Cross-portfolio synthesis** (the value of doing them together):
- **Common themes** — findings that recur across projects (e.g. a shared async-wait anti-pattern,
  documentation drift, missing CI gates), worth a portfolio-level fix.
- **Highest-severity findings across all projects**, ranked, as the recommended attention order.
- **Outliers** — anything one project does notably better or worse than its siblings.
- A note on whether any finding contradicts a project's backlog (`docs/backlog.md`, or the path
  its registry row records as a deviation — e.g. sudoku's `DOCS/.planning/backlog.md`) — the
  backlog is the source of truth; surface the contradiction rather than silently trusting either side.

## Rules

- Follow the **shared orchestration conventions** in `portfolio-prompts/project-layout.md`
  §"Orchestration fan-out" (no `PROJECT=` for the orchestrator; one agent per project, never two on
  the same tree; launch-count check; unattended; sequential fallback; re-run a failed agent at most
  once; relay faithfully).
- **Mode-specific (evidence-only):** you write **no files** and make **no repo changes** — only
  sub-agents write, each into its own project's review folder, committed on its own branch (in the
  sequential fallback those reviews and commits are yours, project by project). Sub-agents make no
  implementation changes, never merge PRs, never push to `main`.
- en-GB spelling.
