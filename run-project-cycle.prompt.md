# Prompt - Run a single project's improvement cycle (conductor)

Paste the text below to run one project through a full improvement cycle end to end, prefixed with
`PROJECT=<project folder name>` (see the README registry) - or invoke it without pasting:
`Read and follow portfolio-prompts/run-project-cycle.prompt.md using PROJECT=<folder>`.
It is a **conductor**: it sequences the existing single-project prompts (review -> triage -> loop ->
log -> handover -> optional close) with explicit entry/exit gates and owner checkpoints. It does not
re-implement any step and it is **not** a portfolio fan-out - for one step across every project use
the `*-all-*` orchestrators (`review-all-projects`, `derive-all-worklists`, `loop-all-worklists`)
instead.

---

You are conducting **one full improvement cycle** for the **`{PROJECT}`** portfolio project. The
invocation names the target as `PROJECT=<folder name at the portfolio root>` - if it did not,
**ask which project**; never guess. This prompt formalises the lifecycle the README names as a prose
arrow-chain (`resume-session -> derive-worklist -> loop-worklist -> write-implementation-log ->
write-code-review -> write-handover -> close-project`) into a runnable sequence with the gates and
checkpoints that chain the steps safely.

## What this is, and is not

- **A conductor, not an implementer.** Each stage **delegates to that stage's canonical prompt**
  (linked below) and follows it exactly. This prompt owns only the *sequence*, the *entry/exit
  conditions* between stages, and the *owner checkpoints* - never a step's internals.
- **Single project, human-in-the-loop.** Several stages stop for explicit owner approval (triage
  candidates, each merge, close-project). The conductor advances only when the stop is cleared. It
  does not run unattended end to end.
- **Norm-referencing, not norm-restating.** All branch, PR, gate, and merge discipline is the
  universal [working norms](project-layout.md#working-norms-universal) and the
  [validation gates](project-layout.md#validation-gates) cascade. Follow them; this prompt does not
  duplicate them.

## Resolve the portfolio root and the project first

Resolve the portfolio root per [project-layout.md](project-layout.md) §"Resolving the portfolio
root", confirm `{PROJECT}` is a registry row (`registry.yml`), and read its row for deviations
(backlog path, review location, gates, coupling, live-API caveats). A project not in the registry is
not a target for this conductor - onboard it first with `onboard-project`.

## Stage 0 - Orient, environment-check, and reconcile before starting

1. **Orient.** Follow [resume-session.prompt.md](resume-session.prompt.md) to load the latest
   handover + backlog and propose the resume point; where they disagree, the backlog is
   authoritative but **flag the mismatch** rather than silently resolving it.
2. **Environment preflight.** Confirm the toolchain the cycle will need is actually present
   (e.g. the project's gate command runs; if the project's gates need Docker/a live API, verify that
   dependency and its headroom now, not mid-loop). Record what you checked.
3. **Reconcile before starting.** If orientation surfaces documentation drift (a backlog that
   contradicts itself, a stale status block, a registry note lagging the repo), **reconcile it in
   its own small PR before the cycle proper** - do not begin review/loop work on top of an
   inconsistent source of truth. This is the one place the conductor may make a change of its own.

**Exit gate:** clean tree on an up-to-date default branch, source of truth internally consistent,
environment verified. If the tree is dirty with work you do not recognise, **stop and report**.

## Stage 1 - Review

Follow [write-code-review.prompt.md](write-code-review.prompt.md) to write the review into the
project's `.review/` (or its registry-recorded deviation), building on the most recent prior review
rather than duplicating it. Commit the review artefacts on their own branch and open a PR; the review
makes **no** implementation changes.

**Checkpoint (owner):** present the top findings and the review PR. The owner decides whether to
merge the review artefacts and proceed to triage.

## Stage 2 - Triage into an approved worklist

Follow [triage-review-findings.prompt.md](triage-review-findings.prompt.md): deduplicate the review
against the backlog and present prioritised candidates. This step has a **mandatory stop for owner
approval before writing** `WORKLIST_{PROJECT}.md` - honour it; do not pre-write the worklist.

**Exit gate:** an approved `WORKLIST_{PROJECT}.md` at the portfolio root exists, with owner decisions
recorded inline for any item that needs one.

## Stage 3 - Loop the worklist

Follow [loop-worklist.prompt.md](loop-worklist.prompt.md) - **one item per iteration**
(implement -> validate -> verify -> commit -> record), each on its worklist branch, opening a PR per
its own rules. Between iterations, honour these conductor conditions:

- **Verify against the project's real gate**, resolved via the
  [validation gates](project-layout.md#validation-gates) cascade; for a project whose gate or CI is
  a live-API/E2E run, watch that run to a genuine conclusion before treating an item as verified -
  a skipped or cancelled run is not a pass.
- **Merges are owner-gated.** The conductor opens PRs; whether and when each merges is the owner's
  call (the loop prompt never merges). Advance to the next item only once the current item's state
  is settled per the owner's direction.
- **Stop conditions** are the loop prompt's own (someone else's held branch/PR, an unrecognised
  dirty tree, an unanswered decision). Report and hold rather than guessing.

**Exit gate:** every worklist item is checked off (or explicitly deferred with a recorded reason).

## Stage 4 - Implementation log

Follow [write-implementation-log.prompt.md](write-implementation-log.prompt.md) to record an
immutable log of the cycle inside the project repo (its own PR). Structural decisions become ADRs and
are referenced, not buried.

## Stage 5 - Handover and control-state close-out

1. Follow [write-handover.prompt.md](write-handover.prompt.md): reconcile `docs/backlog.md`, write
   the next `session-notes/` handover pair, and regenerate the manifest.
2. **Root control-state PR.** The handover pair and the completed `WORKLIST_{PROJECT}.md` are tracked
   by the **portfolio-root support repository**, on its own branch/PR - never folded into the target
   project's history. Keep unrelated worklist/handover edits for other projects out of this PR.

## Stage 6 - Close-project (optional, owner-decided)

If the project has met its close bar (roadmap complete, reviews closed, backlog clean), offer
[close-project.prompt.md](close-project.prompt.md). Do not close a project on the conductor's own
judgement - it is an explicit owner decision.

## Owner checkpoints (where the conductor must stop)

| After stage | Stop for | Why |
|---|---|---|
| 0 (reconcile) | Confirm the reconcile PR before the cycle proper | Don't build on an inconsistent source of truth |
| 1 (review) | Review PR + top findings | Owner decides merge + whether to triage now |
| 2 (triage) | Candidate list | Mandatory - the worklist is written only after approval |
| 3 (each item) | Each PR / any recorded decision | Merges and decisions are the owner's |
| 6 (close) | Close-project offer | Closing is an explicit owner decision |

## Rules

- **en-GB** spelling throughout. Cite every "green/passing/done" claim to a real run, commit, or
  file; if a run was skipped, cancelled, or not executed, say so plainly.
- Convert relative dates to absolute (session date in UTC).
- Delegate each stage to its canonical prompt; do not re-specify a step here. If a stage's prompt and
  this conductor ever disagree on a step's internals, the stage's prompt wins.
- Respect the project's registry deviations at every stage (backlog path, review location, gates,
  coupling, live-API caveats).

## Finish by reporting

- The stages completed this run and the artefacts each produced (review dir, worklist, PRs, log,
  handover version, root PR).
- Every PR opened and its state (open / merged / awaiting owner), with links.
- The current checkpoint the cycle is paused at, and the single next action to resume.
