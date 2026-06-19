# Prompt — Derive a worklist (without actioning it)

Paste the text below to the agent when you want the worklist **prepared and reviewed before any
work starts**, prefixed with `PROJECT=<project folder name>` (see the README registry) — or
invoke it without pasting:
`Read and follow portfolio-prompts\derive-worklist.prompt.md using PROJECT=<folder>`.
It
performs the same orientation and derivation as `loop-worklist.prompt.md` Step 0, materialises
`WORKLIST_{PROJECT}.md` at the portfolio root in exactly the format the loop consumes, and then
**stops** — reporting a detailed breakdown in the chat for you to review, reorder, or trim before
starting the loop.

Optionally append `WORKLIST=<path-or-description>` to name the source (a file, a review section,
or a described set of steps) instead of letting the agent derive one.

Typical flow:

```text
1. Paste this prompt            → WORKLIST_{PROJECT}.md written + detailed breakdown in chat
2. Review/adjust the items      → edit the file or tell the agent what to change
3. /loop Read and follow portfolio-prompts\loop-worklist.prompt.md using PROJECT=<folder>
                                → the loop picks the file up and works through it
```

---

You are **deriving a worklist** for the **`{PROJECT}`** portfolio project. The invocation names
the target as `PROJECT=<folder name at the portfolio root>` — if it did not, **ask which
project**; never guess. Conventions are defined in `portfolio-prompts/project-layout.md`.

**You are NOT actioning the worklist.** Do not implement, fix, commit, or push anything in the
project repo — no matter how small or obvious an item looks. The sole outputs of this session are
(a) the `WORKLIST_{PROJECT}.md` file and (b) a detailed breakdown in the chat. The work itself
belongs to a later `loop-worklist.prompt.md` run, after the user has reviewed the list.

## Step 0 — Guard against an existing worklist

If `WORKLIST_{PROJECT}.md` already exists at the portfolio root, **stop and report** its current
state (items checked/unchecked/blocked) instead of overwriting it — an in-progress loop's memory
must not be silently regenerated. Ask whether to extend it, replace it, or leave it alone; proceed
only on the user's answer.

## Step 1 — Orient (same sources as the loop)

1. Read the **highest-numbered** `session-notes/{PROJECT}_session-notes_v{N}_*.md` at the
   portfolio root — compare versions **only among files carrying the `{PROJECT}_` prefix** and
   compare `{N}` **numerically**, not by filename sort. If the project has no handovers yet,
   orient from the backlog and repo alone and say so.
2. Read the project's backlog: `{PROJECT}/docs/backlog.md`, or the backlog path its registry row
   in `portfolio-prompts/README.md` records as a deviation. The **backlog is authoritative**
   where sources disagree — flag any handover/backlog/repo mismatch in your report rather than
   silently resolving it.
3. Reality-check the repo: `git -C {PROJECT} status --porcelain`, `git -C {PROJECT} log
   --oneline -5`, and `gh pr list` (from inside the repo). Held branches, open PRs, or a dirty
   tree do not block *deriving* the list, but they must be named in the report — the loop's
   Step 1 will treat them as stop conditions.

## Step 2 — Derive the items

In this order of preference:

1. If the invocation names a `WORKLIST` (a file, a section, or a described set of steps), use it
   as the source.
2. Otherwise, the **Recommendations / Next Steps** of the most recent `CODE_REVIEW_*` in the
   target repo's review location (`.review/`, or the location its registry row records as a
   deviation, e.g. `DOCS/.review/`) — ordered by the review's own severity: HIGH → MEDIUM → LOW.
3. Otherwise, open items in the project's backlog (highest priority score first).

**Cross-check every derived item against the backlog before materialising it** — a review may be
stale. Drop items the backlog records as done or closed (note each drop in the report), and where
the two disagree on priority, the backlog's view wins.

Keep items **actionable and verifiable**: each must name what changes and how "done" will be
checked. Split anything that would take more than one loop iteration; merge fragments that only
make sense together.

## Step 3 — Materialise `WORKLIST_{PROJECT}.md`

Write the file at the **portfolio root** (beside `session-notes/` and `portfolio-prompts/`,
therefore outside the repo's git history), in the **canonical worklist format** defined in
`portfolio-prompts/project-layout.md` §"Worklist file format" (header naming project / source(s) /
date; one `- [ ] <id> — <description> — <source ref>` line per item, in execution order; acceptance
criteria + docs-only/code beneath each) — the loop must be able to pick it up unchanged.

Do not commit this file anywhere; it is untracked loop memory.

## Step 4 — Report the detailed breakdown in chat

End with a report the user can review without opening the file. For **each item**, in worklist
order:

- **Id and title** (as in the file).
- **Source:** where it came from (review finding id, backlog item number, or the given
  `WORKLIST`), with the severity/priority the source assigns.
- **What and why:** 2–4 sentences — what is wrong or missing now, what the change is, and why it
  matters (the file carries the one-liner; the chat carries the reasoning).
- **Acceptance criteria:** as in the file, expanded where the one-line form is terse.
- **Type and rough effort:** docs-only or code; small/medium/large.
- **Risks or dependencies:** anything the loop iteration should know before starting (ordering
  constraints, a decision that might be the user's to make, infrastructure it would need).

Then close with:

- Items considered and **dropped** (backlog says done/closed), each with its reason.
- Any handover/backlog/repo mismatches found in Step 1.
- Repo reality notes for the loop's stop conditions: open PRs, held branches, dirty tree.
- The file path written, and the suggested `/loop` invocation line to start the work.

## Rules

- en-GB spelling. Cite what you read (handover version, review version, backlog items, commit
  hashes) so the user can trust the derivation.
- **No project changes whatsoever**: read-only in the repo; the only file written is
  `WORKLIST_{PROJECT}.md` at the portfolio root.
- Do not pad: a short worklist honestly derived beats a long one inflated with vague items. If
  there is genuinely nothing actionable, say so and write no file.
