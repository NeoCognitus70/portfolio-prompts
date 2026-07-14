# Prompt — Triage review findings into an approved worklist

Use this prompt after a portfolio code review when you want to inspect, deduplicate, and prioritise
its findings before any work starts. Name both inputs:
`Read and follow portfolio-prompts/triage-review-findings.prompt.md using PROJECT=<folder> REVIEW=<review-path>`.

`REVIEW` may name a review directory or its main index, relative to the project repository. The
prompt first returns candidates in chat and **stops for approval**. Only after approval does it
write the canonical `WORKLIST_{PROJECT}.md`; it never changes the project repository or actions a
finding.

---

You are **triaging the findings from one named code review** for the **`{PROJECT}`** portfolio
project. The invocation must provide both `PROJECT=<folder name>` and `REVIEW=<path>`:

- If `PROJECT` is missing, ask which registered project to use; never guess.
- If `REVIEW` is missing, ask for the review path; do not silently choose the latest review.

Conventions and registered path deviations are defined in
`portfolio-prompts/project-layout.md` and `portfolio-prompts/registry.yml`.

**You are not actioning the findings.** Do not implement, fix, test, commit, push, edit the backlog,
or change the project repository. This is an interactive two-phase workflow: candidates in chat,
then — only after explicit user approval — one portfolio-root worklist file.

## Step 0 — Validate the inputs and worklist state

1. Resolve `PROJECT` against `registry.yml`, then resolve its registered review and backlog paths
   from the defaults plus row deviations.
2. Resolve `REVIEW` inside that project's registered review location. It may identify a review
   directory or the main index within one. If it is missing, outside that review location, or
   ambiguous, stop and report the exact problem rather than selecting a substitute.
3. If `WORKLIST_{PROJECT}.md` already exists at the portfolio root, do not overwrite it. Report its
   checked, unchecked, and blocked counts and ask whether this triage should propose an extension,
   a replacement, or no change. Continue only after the user decides; replacement still requires
   approval again at Step 3.

## Step 1 — Read the review and current evidence

Read the named review as one evidence set:

- For a directory, read every Markdown deliverable in it. For a main index, follow its internal
  links to the Markdown deliverables within the same review directory.
- Extract concrete risks, issues, and recommendations, retaining each source identifier, severity,
  evidence path/line, impact, proposed remediation, and stated validation.
- Do not turn strengths, observations, template filler, or `N/A` sections into work.

Then read the project's registered backlog completely; it is authoritative for current status and
priority. Reality-check only the files and lightweight local Git evidence needed to decide whether
a finding is stale. Do not run the project's validation gates during triage. If evidence cannot be
verified, label the uncertainty instead of assuming the finding is current or resolved.

## Step 2 — Normalise, deduplicate, and prioritise

Create actionable candidates using these rules:

1. **Normalise** each finding into a root problem, affected scope, proposed change, and verifiable
   acceptance criteria. Split a finding that cannot fit one loop iteration; combine fragments that
   are not independently useful.
2. **Deduplicate by root cause and outcome**, not wording. Merge findings only when they require the
   same change and can share acceptance criteria. Preserve every merged source identifier. Keep
   findings separate when their changes or verification can succeed independently.
3. **Cross-check the backlog and repo:**
   - drop findings already recorded as complete/closed or demonstrably fixed, with evidence;
   - map a finding to an existing open backlog item when it describes the same outcome, using the
     backlog's current priority and identifier;
   - mark an untracked but current finding as a proposed backlog candidate — do not edit the
     backlog during this workflow; and
   - flag a review/backlog/repo conflict as a user decision rather than choosing the nicer source.
4. **Order** unresolved HIGH before MEDIUM before LOW, using the backlog priority where a mapping
   exists and otherwise the review severity. Within a priority, put prerequisites first, then
   order by impact and verification value. Do not invent a numerical score the sources do not
   provide.

Use the existing backlog identifier for a one-to-one mapped item. Otherwise assign stable local
candidate ids `TRIAGE-01`, `TRIAGE-02`, and so on in the proposed execution order.

## Step 3 — Present candidates and stop for approval

Return a Markdown table containing:

| Candidate | Source finding(s) | Priority | Backlog disposition | Proposed work | Acceptance | Type / effort | Dependencies / decisions |
|---|---|---|---|---|---|---|---|

After the table, report:

- merged-source mappings and why each merge is sound;
- findings dropped as resolved, stale, non-actionable, or duplicate, with evidence;
- review/backlog/repo conflicts and any evidence gaps; and
- the proposed execution order and its dependency rationale.

Then **stop and ask the user to approve the candidate list as shown or specify removals, additions,
splits, merges, or reordering**. Do not write `WORKLIST_{PROJECT}.md` in the same turn that first
presents the candidates. Silence or a general acknowledgement is not approval; require an explicit
instruction to materialise the approved list.

If no actionable candidates remain, say so and write no file.

## Step 4 — Materialise only the approved list

After explicit approval, apply exactly the user's changes and write `WORKLIST_{PROJECT}.md` at the
portfolio root in the canonical format defined in `portfolio-prompts/project-layout.md`
§"Worklist file format". The header must name the project, named review path/version, backlog
cross-check, and derivation date. Preserve source finding ids in each item's source reference and
include verifiable acceptance criteria plus docs-only/code classification.

Do not include the worklist in a target-project commit. It is root-tracked control state outside the
project repositories; publishing it uses the portfolio root's separate branch/PR flow and is outside
this triage-only prompt. Finish by reporting the file path, root working-tree state,
approved/merged/dropped counts, unresolved decisions (which must not appear as executable items),
and the exact suggested `/loop` invocation.

## Rules

- The named review is evidence; the backlog is authoritative for current state and priority, and
  live repo evidence decides whether an implementation claim is still true.
- Cite review finding ids and evidence, backlog ids/statuses, and any commit/file evidence used.
- Until approval, write no files. After approval, the only permitted write is
  `WORKLIST_{PROJECT}.md` at the portfolio root; make no project changes.
- Do not pad the worklist with generic advice. Use en-GB spelling.
