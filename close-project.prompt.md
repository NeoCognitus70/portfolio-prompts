# Prompt — Close out a project

Paste the text below to the agent in the **final session** of a project, prefixed with
`PROJECT=<project folder name>` (see the README registry), when the backlog is complete (or every
remaining item has been explicitly deferred with a reason) and the project is being archived as a
finished portfolio piece. It verifies the public-facing claims, retires the process artefacts, and
writes a terminal handover so the project can rest without a successor session being expected.

---

You are closing out the **`{PROJECT}`** portfolio project. The invocation names the target as
`PROJECT=<folder name at the portfolio root>` — if it did not, **ask which project**; never guess.
The aim is to leave the repo, its public artefacts, and the portfolio-root process files in a
state where (a) a portfolio reviewer finds everything accurate, and (b) any future session that
*does* open can orient instantly from one terminal handover.

## Step 0 — Confirm closure is warranted

Read `{PROJECT}/docs/backlog.md` in full. Closure requires every item to be
**done, closed, or explicitly deferred with a recorded reason**. If any item is genuinely open,
**stop and report** — recommend either finishing it or formally deferring it (a user decision);
do not close over an open item.

## Step 1 — Final reconciliation of the source of truth

Update `{PROJECT}/docs/backlog.md` one last time:

- Final statuses on every item, with a dated `**Update (YYYY-MM-DD)**` closing note where needed.
- Any Summary and Credibility Checklist tables reflect the end state.
- Add a dated **Project closed** note at the top stating the closure date and the terminal
  handover version that narrates it.

## Step 2 — Verification sweep (evidence, not assumption)

Verify every public-facing claim the project makes and record the evidence:

- **Published artefacts:** fetch every URL the README claims (living-docs report, demo site,
  published docs) and confirm each has real *content* (scenario counts, named features, working
  pages) — not just an HTTP 200. An empty shell has shipped before.
- **CI:** the latest run on `main` is green — cite the run.
- **README:** every claim (badges, links, coverage statements, setup steps) is accurate as
  of today; fix what is not (via branch + PR — direct pushes to `main`, including docs-only,
  are blocked).
- **PRs and branches:** `gh pr list` shows nothing open, or anything held is named in the terminal
  handover with its disposition. List unmerged branches and their fate (keep/delete — deletion
  only with the user's say-so).
- **Working tree:** clean; cite `git -C {PROJECT} status --porcelain`.
- **Strays:** glob the portfolio root for misplaced `*session-notes_v*` files; move any into
  `session-notes/` and note it.

## Step 3 — Retire the process artefacts

- `WORKLIST_{PROJECT}.md` at the portfolio root: if all items are checked or formally moved to the
  backlog as deferred, delete it (or mark it `CLOSED` at the top if the user prefers an audit
  trail — ask only if no preference is on record).
- Note in the terminal handover where each artefact class lives: handovers (`session-notes/`),
  implementation logs (`docs/implementation-logs/`), reviews (`.review/`), ADRs (`docs/adr/`).
- Update the project's row in the `portfolio-prompts/README.md` registry to **Complete** with the
  closure date (commit in the `portfolio-prompts` repo).

## Step 4 — Write the terminal handover

Follow `portfolio-prompts/write-handover.prompt.md` in full (versioning, naming, frontmatter,
`.md` + generated `.html`, en-GB), with these deltas:

- Title suffix: `# Session Notes — {Project Display Name} (Handover v{N+1} — FINAL)`.
- **Status** line states the honest closing colour and that the project is **closed — no
  successor session is expected**.
- Add a **Project closure summary** section: what the project set out to prove, what it proves
  now, and the evidence trail (final commit, published artefacts, CI run, review version).
- The **Suggested next actions** section becomes **If this project is ever reopened** — the first
  three things a future session should check (e.g. staleness of pinned images/dependencies,
  published artefacts still live, CI still green on a re-run).

## Rules

- en-GB spelling. Every "done/green/live" claim cites a run, commit, URL fetch, or file.
- Nothing destructive without explicit instruction: no branch deletion, no history rewriting, no
  repo archival on GitHub — recommend those as user actions instead.
- If any verification in Step 2 fails, the project is **not closed**: report the failure and stop
  rather than writing a terminal handover over a red state.

## Finish by reporting

- The verification sweep results, item by item, with evidence.
- The terminal handover filenames and version.
- The final state of `WORKLIST_{PROJECT}.md` and the backlog.
- Any user actions recommended (branch deletion, GitHub archival, deferred items revisit-by date).
