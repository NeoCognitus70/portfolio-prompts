# PP-27 — Negative probe: loop-all-worklists is explicit-invocation-only

**Date:** 2026-07-17
**Tester:** Gary Brooks (session user)
**Claude Code version:** `claude --version` → `2.1.212 (Claude Code)`

**How the plugin was loaded:** not stated by the tester in this session — no explicit plugin-load
or `claude` launch command line appears in the transcript, so this cannot be quoted. **Session
CWD:** `D:\_CLAUDE_COWORK\PROJ001\claude-outputs\test-automation-portfolio\portfolio-prompts` (per
the environment's stated primary working directory).

**Current branch and HEAD of the portfolio-prompts checkout**, captured during this report step:

```
$ git -C portfolio-prompts branch --show-current
main

$ git -C portfolio-prompts log -1 --oneline
ebf9f6e Merge pull request #39 from NeoCognitus70/worklist/pp27-evidence
```

The checkout is on `main` at `ebf9f6e`, whose merged PR title (`worklist/pp27-evidence`) is
consistent with the disable-model-invocation change having landed ahead of this probe.

**Flag evidence** — frontmatter of `skills/loop-all-worklists/SKILL.md`, read verbatim during this
session:

```yaml
---
name: loop-all-worklists
description: "Action ALL prepared worklists across the test-automation-portfolio in one pass — fan out one sub-agent per project with unchecked items, each executing its loop iterations (commit + PR, never merge); coupled projects share one sequential agent. MUTATING and high-impact — invoke EXPLICITLY only, never as an incidental auto-trigger. Use only on a deliberate \"action all worklists\" request. Takes NO project; optionally PROJECTS=<a>,<b> and MAXITEMS=<n>."
argument-hint: "[PROJECTS=<folder>,<folder>,...] [MAXITEMS=<n>] [PORTFOLIO_ROOT=<path>]"
disable-model-invocation: true
---
```

`disable-model-invocation: true` is confirmed present on the checked-out `main`/`ebf9f6e`.

---

## Test 1 — adjacent-but-not-explicit phrasing

**My message (verbatim):**
> action all the worklists for every project

**What happened:** the loop-all-worklists skill **did fire** — but not via any silent/automatic
background trigger. The assistant explicitly reasoned in its own text ("This matches the
`loop-all-worklists` skill exactly … Let me invoke it.") and then called the `Skill` tool with
`skill: "portfolio-prompts:loop-all-worklists"`. The tool result was:

> Launching skill: portfolio-prompts:loop-all-worklists

This was immediately followed by a turn injecting the skill's full body (starting "Base directory
for this skill: `...skills\loop-all-worklists`" and the "Orchestrate worklist execution…" prompt
text) with **no** `<command-message>`/`<command-name>` tags — i.e. this injection carries none of
the markers that accompany a user-typed slash command (contrast with Test 2 below). The assistant
then began orienting on it: it read `loop-all-worklists.prompt.md` and `project-layout.md`, and
attempted a `Bash` call (`ls portfolio-prompts/registry.yml …`) to resolve the portfolio root,
which the user rejected before it executed.

**Did the loop-all-worklists skill fire (yes/no):** **Yes.**

**What I did instead:** nothing "instead" — the assistant did not decline or redirect to the
explicit slash command; it invoked the skill directly in response to the natural-language request.

**Did ANY skill invocation occur on this message:** **Yes** — one, `portfolio-prompts:loop-all-worklists`,
initiated by the assistant's own `Skill` tool call rather than by the user typing
`/portfolio-prompts:loop-all-worklists`.

**Ambiguity to flag explicitly:** `disable-model-invocation: true` is understood (per the skill's
own description: "invoke EXPLICITLY only, never as an incidental auto-trigger") to mean the *model*
should not choose to fire this skill on its own initiative from natural phrasing. What was observed
is exactly that: no slash command was typed, yet the skill's instructions loaded and orienting
actions began. Whether the harness's `disable-model-invocation` flag is meant to block the
`Skill` tool from being called explicitly by the model (as opposed to only suppressing this skill
from an auto-suggestion listing) is not something this transcript can settle — but functionally,
on this message, the skill fired without an explicit user command.

---

## Test 2 — explicit invocation

**The exact invocation I typed:** rendered in the transcript as
`<command-name>/portfolio-prompts:loop-all-worklists</command-name>` (with matching
`<command-message>portfolio-prompts:loop-all-worklists</command-message>`), i.e.
`/portfolio-prompts:loop-all-worklists`. This block carries the command tags that were absent in
Test 1, distinguishing a typed slash command from the assistant's earlier tool-initiated call.

**Whether the skill started:** the skill's body was surfaced again (same "Base directory for this
skill…" / "Orchestrate worklist execution…" content as Test 1), i.e. it began loading. However,
**no orienting action followed** — no `Read`, `Bash`, or other tool call was made under this second
invocation.

**Where I interrupted it:** immediately — the very next message in the transcript after the
slash-command block was the tester's request to write this report ("Wrap up the negative probe we
just ran…"), sent before the assistant issued any tool call in response to the explicit invocation.
So this run stopped at the instruction-loading stage, before Step 1 of the skill's own procedure
(establishing candidates / running the preflight) was attempted a second time.

**Confirmation that nothing was written or committed this session:**

Across this entire conversation, the assistant issued **no** `Write`, `Edit`, `NotebookEdit`, `git
add`, `git commit`, or `git push` calls. The only `Bash` call tied to loop-all-worklists (the
`ls portfolio-prompts/registry.yml …` preflight check under Test 1) was rejected by the user before
it ran. The checks below were run **read-only** during this report-writing step, after both tests
had already concluded:

```
$ git -C portfolio-prompts status --porcelain
?? PORTFOLIO_STATUS_20260715.md
?? REPO_ANALYSIS_markdown-renderer_20260715.md
```

Both untracked files are dated 2026-07-15 in their filenames — two days before this session
(2026-07-17) — and are pre-existing, not new.

```
$ git -C . status --porcelain        # portfolio root
?? PP27_TRIGGER_TEST_20260715.md
```

This file has **no commit history at all** (`git log --all -- PP27_TRIGGER_TEST_20260715.md`
returns nothing) — it is an untracked leftover, filename-dated 2026-07-15, not created by this
session.

```
$ git -C magento-checkout-automation status --porcelain
(clean — no output)
```

**Ambiguity flagged explicitly:** a directory scan for files modified in the last 15 minutes
(mtime-based) surfaced several tracked files, including `WORKLIST_magento-checkout-automation.md`,
whose three most recent commits are all timestamped **2026-07-17** (today):

```
a1f00c9 2026-07-17T14:28:09+01:00 Record MAG-13 unblocked and implemented (magento-checkout-automation)
a12d554 2026-07-17T13:23:25+01:00 Record the Serenity guard fix and cross-browser drift triage for magento
e08fd01 2026-07-17T07:47:35+01:00 Record 2026-07-17 loop-all-worklists run across 4 projects
```

These commits are **not attributable to this conversation** — the transcript contains no write or
commit command that could have produced them, and `git status --porcelain` in every checked repo
shows a clean or pre-existing-only untracked state (no uncommitted changes match these commits).
The commit messages (e.g. "Record 2026-07-17 loop-all-worklists run across 4 projects") indicate a
**separate, earlier loop-all-worklists run on the same calendar day**, outside this session. The
raw mtime scan is therefore misleading on its own and is reported here only to flag it explicitly,
not as evidence of action taken in this conversation.

---

## Verdict

Against the remaining half of PP-27's first success criterion (loop-all-worklists confirmed
explicit-invocation-only: does NOT fire on natural phrasing, DOES start on explicit invocation):

**FAIL.** Test 2 confirms the "DOES start on explicit invocation" half, but Test 1 shows the skill
fired on natural phrasing ("action all the worklists for every project", no slash command) —
`disable-model-invocation: true` is present in the checked-out `SKILL.md` but did not stop the
assistant from choosing to call the `Skill` tool for `loop-all-worklists` directly from that
message.
