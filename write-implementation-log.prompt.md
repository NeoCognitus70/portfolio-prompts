# Prompt — Write an implementation log

Paste the text below to the agent after a piece of development work is complete. It produces a new,
immutable implementation log inside the repo from the project template.

---

You are recording an **implementation log** for the work just completed on the
**magento-checkout-automation** project. Implementation logs are an append-only history of what was
built, decided, broke, and learned in a development session — written for the engineer or agent who
comes next.

## Template and location (use exactly these)
- **Template:** `magento-checkout-automation/docs/templates/implementation-log.template.md` — read it
  first and follow its structure section-for-section.
- **Write to:** `magento-checkout-automation/docs/implementation-logs/YYYY-MM-DD_short-slug.md`
  - `YYYY-MM-DD` = today's date.
  - `short-slug` = a few kebab-case words naming the work (match the style of the files already in that
    folder, e.g. `2026-06-06_backlog-3-api-background.md`). If the work maps to a backlog item, lead
    the slug with it (`backlog-{n}-...`).
  - This file lives **inside the repo** (unlike the session handovers) — it is a tracked artifact.

## Gather the facts before writing (don't invent them)
- **What changed:** `git -C magento-checkout-automation status --porcelain`,
  `git -C magento-checkout-automation diff --stat`, and
  `git -C magento-checkout-automation log --oneline -10` for the commits this session produced.
- **Test results:** the real output of whatever was run (e.g. `npm run test:smoke`, the `@placesOrder`
  run, `npx tsc --noEmit`). Record actual scenario/step counts, not estimates. Omit the Test Results
  table only if no tests were executed.
- **Source of truth:** `magento-checkout-automation/docs/backlog.md` — to reference the correct item
  numbers in Objectives and Recommendations.

## Fill in every REQUIRED section of the template
- **Title + date** — `# <Topic / Feature / Phase> — YYYY-MM-DD`.
- **Session Summary** — 2–4 sentences: goal, what was achieved, resulting state.
- **Objectives** — numbered, each marked ✅ done / ❌ not done / ⏸️ deferred.
- **Test Results** — table with passing/total per feature and real pass/fail status (omit if nothing ran).
- **Changes Implemented** — one subsection per logical change, with concrete file paths and rationale
  where non-obvious; include a short before/after snippet only when the change is subtle.
- **Technical Decisions** — decision / rationale / alternatives-rejected table for anything decided this
  session and not already in `docs/adr/`. **If a decision is structural, create a new ADR in
  `docs/adr/` and reference it here** rather than burying it in the log.
- **Documentation Updates** — every doc file changed as a result of this session (including `backlog.md`).
- **Lessons Learned** — reusable patterns, surprises, what you'd do differently. Promote anything
  durable and stack-wide into the relevant handover's "Durable lessons".
- **Recommendations / Next Steps** — checkbox list linked to `docs/backlog.md` items, with priority.
- **Footer** — `*Session logged: YYYY-MM-DD. Author: <Gary Brooks / Claude Code>*`.

## Rules
- **Append-only / immutable:** create a new file; never rewrite a past log. Corrections to an old log go
  in a new log that references it.
- **en-GB** spelling throughout.
- Every "passing / green / done" claim must trace to real command output or a commit hash — cite it.
  If something failed or was deferred, say so; don't round up.
- Keep the template's section order and headings intact — reviewers and agents rely on the fixed shape.
- Strip all `[REQUIRED: ...]` / `[OPTIONAL: ...]` placeholders and the leading `<!-- ... -->` guidance
  comment from the finished file.

## Finish by reporting
- The filename written (full path).
- A 2–3 line summary of what the log records.
- Whether any new ADR was created, and whether `backlog.md` needs a follow-up update to stay consistent.
