# Prompt — Write a walkthrough document

Paste the text below to the agent after a discrete batch of work is completed, prefixed with
`PROJECT=<project folder name>` (see the README registry) or `PROJECT=root` for cross-portfolio work —
or invoke it without pasting:
`Read and follow portfolio-prompts/write-walkthrough.prompt.md using PROJECT=<folder>`.
It produces a new, immutable walkthrough document in the repository and updates native IDE planning
artifacts where supported.

---

You are recording a **walkthrough document** for a completed batch of work on the **`{PROJECT}`**
repository. The invocation names the target as `PROJECT=<folder name at the portfolio root>` or
`PROJECT=root` — if it did not, **ask which project**; never guess.

A walkthrough is a focused, evidence-grounded record verifying a discrete batch of commits or a feature
slice — faster and more visual than a full session handover, and more directly tied to immediate test
verification than a long-form implementation log.

## 1. Gather Ground Truth First (Do not guess or invent)
Before writing anything, inspect real repository state:
- **Git status and history:** `git -C {PROJECT} status --porcelain`, `git -C {PROJECT} diff --stat`, and
  `git -C {PROJECT} log -n 5 --oneline` for the commits produced in this batch.
- **Verification gate results:** Run or inspect the relevant test and quality gates (e.g. `npm test`,
  `npm run verify`, `npm run typecheck`, `npm run lint`, `npm audit`, unit test suites).
  Capture **exact numeric counts and execution durations** (e.g. "49 passed, 0 failed, duration 12.6s"),
  never vague estimates like "tests passed".
- **Requirements & Backlog:** Confirm which requirements, tickets, or backlog items (`docs/backlog.md`
  or root `PORTFOLIO_BACKLOG.md`) were addressed or advanced.

## 2. Structure of the Walkthrough Document
Author the document following this exact structure:

### `# Walkthrough — <Topic / Feature / Batch Title>`

### `## Executive Summary`
A concise 2–4 sentence summary stating the core objective, what was accomplished, and the resulting state.

### `## 1. Changes Implemented`
Group changes logically by component, layer, or feature area.
For every created, modified, or deleted file, provide:
- A clickable link with the file path (`file:///...`).
- A concise explanation of the architectural purpose, design rationale, and non-obvious details.
- Short before/after snippets where a code change is subtle or critical.

### `## 2. Verification & Test Evidence`
- **Verification Table:**
  | Command | Quality Gate / Suite | Status | Metrics (Passed/Total) | Duration |
  |---|---|---|---|---|
- **Reproduction Output Snippets:** Real console captures showing zero vulnerabilities, clean typecheck,
  passing unit/component test counts, and remote CI run IDs.

### `## 3. Operational State & Invariants`
- Git branch name, clean working tree status, upstream synchronization (`ahead=0, behind=0`).
- Remote GitHub Actions CI status on the relevant branch/PR.
- Conformance to workspace and project invariants (e.g., Docker storage on `E:\_DockerData`, strict SDD
  traceability, security audit gates, and en-GB documentation spelling).

### `## 4. Recommended Next Actions`
- Prioritised, numbered options for logical next steps, identifying the primary recommended action.

## 3. Output Destinations
To ensure durable history across all AI agents and tools:
1. **Repository Versioned Record (Always):**
   - If `PROJECT=root`: Write to `docs/walkthroughs/YYYY-MM-DD_short-slug.md` at the portfolio root.
   - If `{PROJECT}` is a sub-repository: Write to `{PROJECT}/docs/walkthroughs/YYYY-MM-DD_short-slug.md`.
   - Create the `docs/walkthroughs/` directory if it does not yet exist.
   - Files are immutable: use a new date/slug per batch rather than overwriting past walkthroughs.
2. **Antigravity / Gemini IDE Integration (Conditional):**
   - If running within the Google Antigravity environment, also write or update
     `<appDataDir>\brain\<conversation-id>/walkthrough.md` so the interactive IDE UI renders the
     walkthrough view.
