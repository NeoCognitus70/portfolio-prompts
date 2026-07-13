# Prompt — Work through a list of recommended steps on a /loop

Use this prompt with the `/loop` command to have the agent work through an ordered list of
recommended steps one item per iteration, validating and verifying each before committing it with a
descriptive message.

Invocation examples:

```text
/loop Read and follow portfolio-prompts/loop-worklist.prompt.md using PROJECT=<folder>
/loop 10m Read and follow portfolio-prompts/loop-worklist.prompt.md using PROJECT=<folder> WORKLIST=<path-or-description>
```

`PROJECT` is the project folder name at the portfolio root (see the README registry) — if the
invocation does not name one, **ask before the first iteration**; never guess. A loop binds to
exactly **one** project. If no `WORKLIST` is given, derive one (see Step 0). To prepare and
review the worklist **before** starting the loop, run `derive-worklist.prompt.md` first — it
writes `WORKLIST_{PROJECT}.md` in this prompt's format without actioning anything, and Step 0
picks an existing file up as-is. The loop is
self-pacing when no interval is given: end the iteration when one item is fully done, and continue
on the next wake-up.

---

You are executing **one iteration of a work loop** against the **`{PROJECT}`** portfolio project.
Each iteration completes exactly **one** item from the worklist: implement → validate → verify →
commit → record. Do not start a second item in the same iteration, even if the first was quick —
small, reviewable, per-item commits are the point.

## Step 0 — Orient and establish the worklist (first iteration only, then reuse)

1. **Orient from the handover trail first** (fresh sessions have no prior context): read the latest
   `{PROJECT}` handover in `session-notes/` at the portfolio root — **prefer the manifest (PP-14):**
   if `session-notes/manifest.json` exists, use its `latest["{PROJECT}"]` entry; **else** take the
   **highest-numbered** `{PROJECT}_session-notes_v{N}_*.md` by hand, comparing versions **only among
   files carrying the `{PROJECT}_` prefix** (several projects share the folder) and comparing `{N}`
   **numerically**, not by filename sort — and the project's
   `{PROJECT}/docs/backlog.md` (or the backlog path its registry row in
   `portfolio-prompts/README.md` records as a deviation). If the project has **no handovers
   yet**, orient from the backlog and repo alone and say so. The **backlog is authoritative**
   where they disagree — but flag any handover/backlog/repo mismatch in this iteration's report
   rather than silently resolving it. Use what you learn (open items, held branches, working
   norms, in-flight PRs) to inform worklist derivation and Step 1's reality check. Do this once
   per loop, not per iteration.
   **Session-boundary test:** if you have no memory of reading the latest handover and backlog in
   *this* session (e.g. the loop resumed in a fresh context window), perform this orientation
   again before touching the worklist — `WORKLIST_{PROJECT}.md` existing is not evidence that
   *you* are oriented.
2. If the invocation names a `WORKLIST` (a file, a section, or a described set of steps), use it.
3. Otherwise derive it, in this order of preference:
   - `WORKLIST_{PROJECT}.md` at the **portfolio root**, if one exists from a previous iteration;
   - the **Recommendations / Next Steps** of the most recent `.review/CODE_REVIEW_*` in the target
     repo — or in the review location its registry row records as a deviation (e.g. `DOCS/.review/`)
     — ordered by the review's own severity: HIGH → MEDIUM → LOW;
   - open items in the project's `docs/backlog.md` (highest priority score first).

   **Cross-check every derived item against `docs/backlog.md` before materialising it** — the
   backlog is the source of truth and a review may be stale. Drop items the backlog records as
   done or closed (note each drop in this iteration's report rather than silently omitting it),
   and where the two disagree on priority, the backlog's view wins.
4. Materialise it as a checklist file — `WORKLIST_{PROJECT}.md` at the **portfolio root**, beside
   `session-notes/` and `portfolio-prompts/` and therefore **outside the repo's git history** — in
   the **canonical worklist format** defined in `portfolio-prompts/project-layout.md` §"Worklist
   file format". This file is the loop's memory: every iteration reads it first and updates it last.
5. If a `WORKLIST_{PROJECT}.md` already exists, do **not** regenerate it — pick up where it stands
   (the orientation read in item 1 still applies if this session has not yet performed it).

## Step 1 — Orient (every iteration)

- `git -C {PROJECT} status --porcelain` — the tree must be clean before starting. If it is dirty
  with changes you do not recognise, **stop and report**; do not stash or discard someone else's work.
- `git -C {PROJECT} log --oneline -5` and `gh pr list` (from inside the repo) — confirm where the
  previous iteration left off and whether a held branch or open PR is awaiting the user (if so,
  that is a stop condition — report).
- Read `WORKLIST_{PROJECT}.md`; select the **first unchecked item**. If all items are checked, go
  to Step 6 (loop completion) and **do not schedule another iteration**.

## Step 2 — Implement the selected item

- Re-read the item's source (review finding, backlog entry) in full before changing anything — the
  one-line summary in the worklist is a pointer, not the spec.
- Respect the project's working norms:
  - Apply the universal [working norms](project-layout.md#working-norms-universal). Create or reuse
    a branch named for the worklist (e.g. `worklist/<id>-<slug>`). **When creating it, branch from
    an up-to-date default branch**: `git fetch`, switch to `main`, `pull --ff-only`, then branch — a stale
    local `main`, or a checkout left sitting on an old merged branch, would otherwise put
    unrelated history in the PR. (A clean tree on the wrong branch is not a dirty-tree stop —
    switch, don't stop.) One PR may carry several worklist items as
    separate commits; open it when the first item is ready and push subsequent items to the same
    branch unless the items are unrelated enough to deserve separate PRs. Your **own** open
    worklist branch/PR is never the Step 1 stop condition — that refers to someone else's held
    work awaiting the user.
- Apply the repo's documented durable lessons from the start. The **single source** is the
  "Durable lessons" section of the project's latest handover (read in Step 0), plus
  `{PROJECT}/docs/project-contract.md` if it exists — examples of the kind of thing carried there
  (from the magento project): explicit waits on JS-framework renders, attribute assertions over
  occlusion-aware visibility, exactly one stdout formatter in the cucumber profile.
- Stay on-scope: fix what the item names. If you discover an adjacent problem, add it to
  `WORKLIST_{PROJECT}.md` as a new unchecked item rather than folding it in.

## Step 3 — Validate (mechanical gates)

Resolve the project's gates per `portfolio-prompts/project-layout.md` §"Validation gates" — the
canonical first-hit-wins cascade lives there in full (project-contract `Gates` -> registry-row
gates -> root `npm run verify` -> stack defaults run inside the touched stack's directory -> ask;
it also carries the cucumber-js vs playwright-bdd nuance). Run every gate that applies to what you
touched; all must pass before commit. In addition:

- Suite, where feasible: run the narrowest set that exercises the change (a single feature, tag,
  or test file locally if the runtime is available; otherwise rely on CI and say so). Do not start
  heavyweight infrastructure (e.g. a full Docker application stack) or a long E2E run unless the
  item itself requires it.
- Docs-only items: check every relative link you added or moved resolves, and re-grep the docs for
  the claim you corrected to confirm no other file still states the stale version.
- If a gate fails, fix it within the iteration. If it cannot be fixed without a decision that is
  the user's to make, revert to a clean tree, mark the item `BLOCKED (reason)` in
  `WORKLIST_{PROJECT}.md`, and report — never commit a failing state.

## Step 4 — Verify (acceptance criteria)

Validation says the change is sound; verification says it does what the item asked. Check the
item's acceptance criteria explicitly, one by one, and record the evidence (command output, line
references, screenshots if UI). If the criteria cannot all be met, treat as blocked — do not check
the item off on a partial.

## Step 5 — Commit and record

- Commit with a descriptive message in the repo's established style:
  `<type>(<scope>): <imperative summary>` — e.g. `docs(review R-01): correct screenplay-guide
  actor lifecycle to the BeforeAll pattern` or `fix(R-05): scope decline-message selector to the
  checkout messages region`. Reference the worklist/finding id in the message. Body lines for the
  *why* when the diff alone does not carry it. Never amend or squash existing history.
- Push to the worklist branch and note the commit hash.
- Update `WORKLIST_{PROJECT}.md`: check the item off with the commit hash and a one-line outcome.
  Update any tracking docs the project mandates (e.g. `CHANGELOG.md` for user-visible changes, the
  review's finding status if the worklist came from a review).
- End the iteration with a short report: item done, evidence, commit(s), what the next iteration
  will pick up.

## Step 6 — Loop completion

When every item is checked or blocked:

- If a code branch/PR is open, summarise its contents and present it for the user's review and
  merge — do not merge it yourself unless the user has already authorised it.
- Produce the closing report: items completed (with commits), items blocked (with reasons),
  follow-on items discovered and added, and validation status of the final state.
- Recommend whether a new session-notes handover or review-status update is warranted.
- Do not schedule a further wake-up.

## Rules

- en-GB spelling. One item per iteration. One project per loop. Never leave the tree dirty
  between iterations.
- Never commit on red: all applicable gates pass, or the item is reverted and marked blocked.
- Commit messages describe the change and its reason, not the process ("loop iteration 3" is not
  a commit message).
- Report honestly: if a gate was skipped (e.g. no local runtime for an E2E check), say so in both
  the iteration report and the commit body, and rely on CI explicitly.
- Stop conditions (report and end without scheduling): all items done; an item blocked on a user
  decision; an unrecognised dirty tree; a failing gate you cannot fix; any action that would be
  destructive or rewrite history.
