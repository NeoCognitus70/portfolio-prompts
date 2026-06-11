# Prompt — Write the session handover doc

Paste the text below to the agent at the **end** of a working session, prefixed with
`PROJECT=<project folder name>` (see the README registry). It produces the project's next
versioned `session-notes` handover (both `.md` and `.html`) **inside the `session-notes/` folder**
at the portfolio root (`test-automation-portfolio/session-notes/` — NEVER directly at the root
itself) and reconciles the source of truth.

> A misplaced handover breaks more than tidiness: the next session's orientation globs only
> `session-notes/`, so a root-level file is invisible, the version number gets reused, and the
> successor re-derives a stale picture. This happened with v11 (2026-06-10) — keep the file in the
> folder.

---

You are wrapping up a working session on the **`{PROJECT}`** portfolio project and must write a
clean handover so any agent or human can resume cold without re-deriving decisions. The invocation
names the target as `PROJECT=<folder name at the portfolio root>` — if it did not, **ask which
project**; never guess. Conventions are defined in `portfolio-prompts/project-layout.md`.

## Ground truth — read these before writing anything
1. **Source of truth:** `{PROJECT}/docs/backlog.md` (or the backlog path the project's registry
   row in `portfolio-prompts/README.md` records as a deviation). Item statuses here are authoritative.
2. **The latest existing handover:** the highest-numbered
   `{PROJECT}_session-notes_v{N}_*.md` in the **`session-notes/`** folder at the
   portfolio root (`test-automation-portfolio/session-notes/`). Compare versions **only among
   files carrying the `{PROJECT}_` prefix** — handovers for several projects share the folder —
   and compare `{N}` **numerically** (a plain filename sort orders `v9` after `v13`; a wrong
   "latest" here causes a version collision in the file you are about to write).
   Read it in full — your new doc *supersedes* it and should only restate settled context by
   reference, not re-explain it. **First handover:** if no `{PROJECT}_` handover exists, this new
   doc is **v1** — there is nothing to supersede; orient from the backlog and repo alone.
3. **Real repo state** — run and capture, do not assume:
   - `git -C {PROJECT} status --porcelain` (working tree must be reported honestly —
     dirty is fine, but say so)
   - `git -C {PROJECT} branch -vv`
   - `git -C {PROJECT} log --oneline -15`
   - any open PRs: `gh pr list` (run from inside the repo)

## First, reconcile the source of truth
Before writing the handover, update `{PROJECT}/docs/backlog.md` to reflect what actually changed
this session: item statuses, new findings, new sub-items, dated `**Update (YYYY-MM-DD)**` notes in
the affected items, and any Summary / Credibility Checklist tables. The handover *narrates* the
session; the backlog *records* the durable state. Keep them consistent.

## Then write the handover — two files, identical content
Write **both** into the **`session-notes/`** folder at the portfolio root
(`test-automation-portfolio/session-notes/`, i.e. one level above the repos — this keeps handovers
out of the repos' git history). Create the folder if it does not yet exist:

- `session-notes/{PROJECT}_session-notes_v{N+1}_{YYYYMMDD}T{HHMM}Z.md`
- `session-notes/{PROJECT}_session-notes_v{N+1}_{YYYYMMDD}T{HHMM}Z.html`

Where:
- `{N+1}` = previous highest version **for this project** + 1 (or `1` for a first handover).
- Timestamp is **UTC**, format `YYYYMMDDTHHMMZ` (e.g. `20260609T1830Z`). Get real UTC now; don't guess.
- Match the exact filename pattern of the existing files in the folder.

### Frontmatter (must match the prior docs)
Markdown — YAML frontmatter:
```
---
version: {N+1}
created: {YYYY-MM-DDTHH:MM}Z
supersedes: v{N} ({prior created timestamp})   # omit for a first handover
project: test-automation-portfolio
subject: {PROJECT}
type: session-notes
language: en-GB
---
```
HTML — the same fields inside a leading `<!-- ... -->` comment block, then a styled standalone page.

**Author the `.md` first; it is the single source.** Then *generate* the `.html` from it
mechanically — use a markdown converter if one is available (`pandoc`, `npx marked`, or similar),
or convert programmatically — rather than hand-authoring the body a second time. Reuse the prior
version's `.html` as the styling template (same `<head>`/`<style>`); for a project's first
handover, reuse the most recent handover `.html` of any project in the folder, or a clean minimal
style if none exists. Only the body content and frontmatter comment change. The two files must
carry the **same information** — if you spot an error after generating, fix the `.md` and
regenerate; never patch the `.html` independently.

### Structure (follow the established shape)
1. Title: `# Session Notes — {Project Display Name} (Handover v{N+1})` — the display name as used
   in the project's prior handovers, or its README `#` heading for a first handover.
2. **Purpose** one-liner, **Read first** (this file; name the 1–2 prior docs still worth reading and why),
   **Status** (🟢/🟡/🔴 + one honest sentence on where things stand).
3. **Repo working copy** path, **GitHub** URL, and any published artefact URLs the project claims
   (live report, demo site).
4. Numbered sections, adapted to what actually happened this session:
   - `## 1.` **Read-me-first deltas since v{N}** — the bullet list of what changed vs the prior handover.
   - `## 2.` **Chronology** — a table of bugs/changes: symptom → root cause → fix → commit.
   - `## 3.` CI / architecture notes if they changed.
   - `## 4.` **Repository state** — branch/commit/state table; key commits; working-tree cleanliness.
   - `## 5.` **Durable lessons** — gotchas that cost real debugging, "apply on sight".
   - `## 6.` **Environment** — CI + local bring-up facts.
   - `## 7.` **Backlog snapshot** — table mirroring `backlog.md`'s current state.
   - `## 8.` **Suggested next actions** — concrete, ordered, with the working norms a successor must respect.

## Rules
- **en-GB** spelling throughout (behaviour, prioritise, recognise…).
- Every claim of "done/green/passing" must trace to a real run, commit, or file — cite it. If something
  is unverified or left dirty, say so plainly; never round up.
- Convert relative dates to absolute (today is the session date in UTC).
- Don't duplicate settled architecture already captured in earlier handovers or ADRs — link/refer to it.
- Keep `.md` and `.html` in lockstep — same facts, same section numbers. The `.html` is derived
  from the `.md`; never edit it independently.

## Finish by reporting
- The two filenames written.
- The new version number and what it supersedes (or that it is the project's v1).
- A 3–5 line summary of what changed in the backlog (source of truth) this session.
