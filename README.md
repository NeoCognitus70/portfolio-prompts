# Portfolio Prompts

Reusable session prompts for the **test-automation-portfolio** projects (currently written against
**magento-checkout-automation**; parameterisation for the other portfolio projects is planned).

This folder lives at the portfolio root, **outside** the individual project repos, and is tracked
as its **own git repository** (`portfolio-prompts`) — the prompt library has history without
polluting any project's history.

| Prompt | When to use | What it does |
|---|---|---|
| [write-handover.prompt.md](write-handover.prompt.md) | End of a session | Reconciles `docs/backlog.md` (source of truth), then writes the next `session-notes` handover (`.md` + `.html`) into `session-notes/`, superseding the previous version. |
| [resume-session.prompt.md](resume-session.prompt.md) | Start of a session | Loads the latest handover from `session-notes/`, cross-checks it against the backlog and the live repo, and proposes the resume point — then waits for confirmation. |
| [write-implementation-log.prompt.md](write-implementation-log.prompt.md) | After a dev task | Writes a new immutable implementation log into `magento-checkout-automation/docs/implementation-logs/` from the repo template. |
| [write-code-review.prompt.md](write-code-review.prompt.md) | Code review | Uses `templates/code-review.template.md` and `docs/backlog.md` to write a comprehensive review into the repo's `.review/` folder. |
| [loop-worklist.prompt.md](loop-worklist.prompt.md) | Working through an ordered list of steps | Driven via the `/loop` command (not pasted). Completes one worklist item per iteration — implement → validate → verify → commit → record — tracked in `WORKLIST.md` (portfolio root), with stop conditions and a closing report. |
| [close-project.prompt.md](close-project.prompt.md) | Final session of a project | Verifies every public-facing claim (live report content, CI, README), reconciles the backlog one last time, retires `WORKLIST.md`, and writes a terminal handover marked FINAL. |

**Conventions the prompts rely on:**
- Source of truth: `magento-checkout-automation/docs/backlog.md`.
- Handovers live in `../session-notes/` (outside the repo, untracked), named
  `magento-checkout-automation_session-notes_v{N}_{YYYYMMDD}T{HHMM}Z.{md,html}` —
  monotonically versioned, UTC-timestamped, en-GB.
- Implementation logs live **inside the repo** at
  `magento-checkout-automation/docs/implementation-logs/YYYY-MM-DD_short-slug.md` (tracked, append-only),
  written from `docs/templates/implementation-log.template.md`.

Usage: open the relevant `.prompt.md`, copy the text below its `---` divider, and paste it to the agent.
**Exception:** `loop-worklist.prompt.md` is invoked via the `/loop` command (see the invocation
examples in its header), not pasted.
