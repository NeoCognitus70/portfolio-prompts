# Prompt — Write a portfolio project in-depth report

Use this prompt to create a comprehensive, evidence-based account of one registered portfolio
project, or invoke it without pasting:
`Read and follow portfolio-prompts/write-project-in-depth-report.prompt.md using PROJECT=<folder>`.

This is a descriptive and historical report, not a code review, worklist, implementation task, or
external-repository assessment. It keeps the target project read-only and writes a versioned
Markdown/HTML pair into the portfolio-level `portfolio-in-depth-reports/` archive.

---

You are preparing an in-depth report on the **`{PROJECT}`** portfolio project.

The invocation must identify the target as `PROJECT=<folder name at the portfolio root>`. If it did
not, **ask which registered project to analyse and stop**. Never infer the project from the current
working directory. Resolve the library and portfolio roots using `project-layout.md` at the resolved
library root.

## Purpose

Produce a detailed, evidence-based report that allows a technical reader to understand:

- why the project exists and what it is intended to demonstrate;
- the problem, domain, audience, and workflows it addresses;
- the complete current design and meaningful repository contents;
- what the project currently builds, tests, publishes, or otherwise produces;
- how the implementation developed from its earliest available history to its current state;
- its reconciled current status; and
- its documented and reasonably inferred future direction.

The report must stand alone. A reader must not need previous conversation context or knowledge of the
agent that generated it.

## Operating boundaries

- Treat `{PROJECT}/` as **read-only**. Do not modify its source, documentation, configuration,
  dependencies, branches, index, or Git state.
- Write only the report pair under the designated portfolio-level output directory.
- Do not create backlog items, worklists, implementation changes, commits, pushes, pull requests, or
  external messages. Those require separate workflows and authority.
- This is not a defect review. Discuss limitations and risks only when they explain the design,
  history, current state, output, or future direction; do not assign review-style severity scores.
- Base claims on the repository, portfolio records, Git history, and accessible read-only project
  metadata. Label inference, uncertainty, contradiction, and missing evidence.
- Remain **AI-agent agnostic**. Do not name or depend on a particular agent, model, product, memory
  system, or proprietary capability in the generated report.
- Use en-GB spelling throughout.

## Inputs

Required:

- `PROJECT` — a registered project folder at the portfolio root.

Optional:

- `OUTPUT_ROOT` — portfolio-relative destination directory. Default:
  `portfolio-in-depth-reports/`.
- `AS_OF` — evidence cut-off date or commit. Default: the current checked-out revision and real
  current date.
- `AUDIENCE` — intended reader. Default: technical portfolio reviewer, architect, and future
  maintainer.

## Step 1 — Resolve and verify the project

Confirm that:

1. `{PROJECT}/` exists and is the registry row named by the invocation.
2. Its Git repository and authoritative backlog path are readable.
3. The output directory resolves beneath the portfolio root and **outside** the target repository.
4. The requested `AS_OF` revision exists, if one was supplied.

If `AS_OF` is not the checked-out `HEAD`, inspect that revision through read-only Git object access
(`git show`, `git ls-tree`, or an equivalent) rather than checking it out. Limit the historical
timeline and "current at cut-off" claims to evidence available at that revision. Describe later
commits and uncommitted working-tree files only as evidence outside the requested cut-off.

Capture before analysis:

- repository URL, current branch, `HEAD`, default branch, upstream relationship, and working-tree
  status;
- the report cut-off date and revision;
- the registry lifecycle status and presentation role; and
- any access or evidence limitation.

A dirty tree is not automatically a blocker because this workflow is read-only. Distinguish
uncommitted local evidence from committed project history and never imply that an uncommitted file is
part of the published project.

## Step 2 — Analyse the full meaningful contents

Inventory the project before drawing conclusions. Use the Git index as the baseline (`git ls-files`
or an equivalent) and inspect the working-tree status for additional local files. Read **every
Git-tracked, human-authored text file** and any untracked human-authored text needed to explain the
visible local state, including applicable content under:

- root documentation and configuration;
- source, application, library, or service directories;
- tests, features, specifications, fixtures, and test data;
- runner, compiler, formatter, and framework configuration;
- `.github/workflows/` and other CI/deployment configuration;
- `docs/`, ADRs, decision registers, implementation logs, planning records, project contracts, and
  runbooks;
- dependency manifests and lockfiles;
- Docker, infrastructure, publishing, and developer scripts;
- static sites, schemas, contracts, templates, and example outputs maintained as source; and
- review or assessment artefacts that provide dated evidence about the project's evolution.

Inventory but do not manually analyse every file in dependency, binary, cache, or generated-output
directories such as `.git/`, `node_modules/`, `vendor/`, `dist/`, `build/`, `target/`, test reports,
traces, screenshots, videos, and caches. Where generated artefacts are important project outputs,
inspect their source, generation path, and representative output. List every excluded area and why
it was excluded.

For a multi-stack project, analyse each stack independently before explaining their integration.
Record the meaningful file count and content-area coverage so "full" is auditable rather than a
claim based on a sample.

## Step 3 — Establish the evidence hierarchy

Use these sources for their appropriate questions:

1. **Current implementation and configuration** — what exists at the cut-off revision.
2. **Git commits, tags, merge history, and releases** — when and how implementation changed.
3. **Authoritative backlog** — current item state and owner-approved future work.
4. **ADRs and decision records** — architectural intent, rejected options, and superseded choices.
5. **Implementation logs** — delivery detail, breakages, decisions, and lessons.
6. **Versioned handovers** — historical session context and durable working knowledge.
7. **README, architecture, strategy, and planning documents** — intended behaviour and narrative.
8. **Code reviews** — independent observations at a particular revision and date.
9. **Pull requests, issues, CI, releases, and published artefacts**, when accessible — external
   corroboration.

Do not silently reconcile contradictions. State what each source claims, which source is
authoritative for that question, and whether the difference is normal historical evolution, stale
documentation, local uncommitted state, or an unresolved inconsistency.

## Step 4 — Reconstruct the implementation history

Inspect the **full available Git history**, not only the latest commits. Enumerate the complete
commit/tag/release timeline, then inspect the diffs and supporting records for material milestones.
Use repository-host PR/issue metadata when accessible through a read-only integration or CLI, but do
not make the report dependent on that access.

Do not produce a commit-by-commit dump. Group related changes into meaningful phases, releases,
review cycles, or implementation themes. For every significant milestone identify:

- date or date range;
- phase, release, backlog item, or initiating event;
- original need or trigger;
- implementation and design change;
- tests, CI, documentation, or published output added;
- important decision or trade-off;
- evidence: commit, tag, PR, backlog item, ADR, log, handover, or review; and
- resulting capability and influence on later work.

Cover, where present: initial foundation; feature phases; architectural changes; test-strategy
growth; review-derived remediation; CI/security/dependency/documentation hardening; publication;
provider or stack migrations; and closure, resting, or reopening events.

## Step 5 — Describe current design and output

Explain the project as it exists at the cut-off revision:

- purpose, intended audience, domain, use cases, and explicit non-goals;
- languages, frameworks, libraries, runtimes, and build systems;
- repository structure and component responsibilities;
- architectural style, dependency direction, interfaces, contracts, integrations, data flows, and
  state transitions;
- test architecture, executable specifications, levels/types, fixtures, data, isolation, and
  synchronisation model;
- CI/CD, validation gates, reporting, publication, and local reproduction path;
- runtime, deployment, infrastructure, and environment assumptions;
- configuration, security, dependency, and licence constraints that affect project use; and
- significant decisions, trade-offs, and durable lessons.

Describe every material current output and its consumer:

- applications, services, CLIs, libraries, or packages;
- automated suites and their intended evidence;
- reports, living documentation, schemas, contracts, or generated artefacts;
- published sites, API references, packages, releases, or demonstrations; and
- commands used to build, test, run, publish, or regenerate the project.

Classify each output as **verified current**, **configured but not independently verified**,
**historical**, or **planned**. Do not claim that an output is live or green unless current evidence
supports it. This workflow does not install dependencies or start heavyweight infrastructure by
default; prefer existing repository and CI evidence, and state when runtime verification was not
performed.

## Step 6 — Reconcile current status

Cross-check the implementation, authoritative backlog, latest handover, registry row, Git state, and
accessible PR/CI evidence. Report:

- lifecycle state;
- delivered scope and current revision;
- approved work that is still open;
- blocked or trigger-gated work;
- accepted limitations and non-goals;
- open pull requests or incomplete merge state, when accessible;
- latest verified validation/publication evidence; and
- whether the sources agree.

## Step 7 — Build the future-direction roadmap

Inference is allowed, but it must never masquerade as owner intent. Separate future direction into:

1. **Approved and actionable** — authoritative open work that can begin now.
2. **Approved but blocked** — authoritative work with a documented blocker or dependency.
3. **Trigger-gated** — work that becomes applicable only if its stated condition occurs.
4. **Documented proposals** — planning ideas not promoted to authoritative work.
5. **Inferred opportunities** — plausible directions derived by the report author but not approved.

For every entry include the proposed outcome, motivation, evidence source, authorisation category,
dependency/trigger, affected area, expected completion evidence, and consequence of not pursuing it.
State explicitly when a category is empty. A resting or closed project may correctly have no intended
future implementation beyond maintenance or an explicit reopening trigger.

## Step 8 — Write one versioned Markdown/HTML pair

Write both files under:

```text
<PORTFOLIO_ROOT>/<OUTPUT_ROOT>/{PROJECT}/
```

Default filenames:

```text
{PROJECT}_in-depth-report_v{N}_{YYYYMMDD}T{HHMM}Z.md
{PROJECT}_in-depth-report_v{N}_{YYYYMMDD}T{HHMM}Z.html
```

Determine `{N}` by parsing versions **numerically** among reports for this project only; use `v1`
when none exist. Use real UTC in the filename and never overwrite an earlier pair.

Markdown frontmatter:

```yaml
---
version: {N}
created: {YYYY-MM-DDTHH:MMZ}
project: test-automation-portfolio
subject: {PROJECT}
type: portfolio-in-depth-report
source-revision: {full commit SHA}
evidence-cut-off: {date or revision}
language: en-GB
---
```

Put the same fields in a leading HTML comment.

**Author the Markdown first; it is the sole content source.** Generate the HTML mechanically from
that Markdown. Render only the Markdown body **after** the closing frontmatter delimiter; do not
render the YAML frontmatter as visible page content. Copy its fields into the leading HTML metadata
comment instead.

Prefer an already-installed `marked` from the resolved library root (for example
`npm exec --offline -- marked`, or the platform-specific executable under
`<LIBRARY_ROOT>/node_modules/.bin/`; the library declares `marked`). Do not let report generation
download a package, change a lockfile, or install dependencies. A semantically equivalent
already-available CommonMark/GFM converter is an acceptable fallback when the local `marked` is
unavailable.

`marked` produces an HTML **fragment**. Wrap that mechanically rendered fragment in a complete
standalone document containing the leading metadata comment, `<!doctype html>`, `<html lang>`, a
UTF-8 `<head>`, viewport metadata, `<title>`, inline `<style>`, and a `<main>` body. For a later
version, reuse the preceding report's `<head>` and `<style>` so presentation does not drift. For a
first report, create a clean self-contained accessible style with readable tables/code, responsive
width, visible focus styles, and print-safe colours. Do not load external scripts, fonts, styles, or
assets.

The Markdown and HTML must contain the same information. If content changes after generation, edit
the Markdown and regenerate the HTML; never patch the HTML narrative independently.

## Required report structure

```text
# {Project Display Name} — In-Depth Project Report

## Report metadata
## 1. Executive summary
## 2. Project intention and problem domain
## 3. Repository content map
## 4. Current design and architecture
## 5. Test and evidence design
## 6. Current outputs and deliverables
## 7. Historical implementation roadmap
## 8. Current status
## 9. Intended future direction
## 10. Decisions, trade-offs, and durable lessons
## 11. Evidence gaps and uncertainties
## 12. Evidence index
```

Specific requirements:

- **Report metadata:** project, repository, revision, branch, lifecycle state, version, creation
  time, evidence cut-off, audience, working-tree state, and limitations.
- **Repository content map:** annotated tree, content-area catalogue, meaningful file count, and
  exclusions.
- **Architecture:** components, responsibilities, dependency direction, integrations, and at least
  one end-to-end flow. Use compact diagrams only when they materially improve comprehension.
- **Current outputs:** consumer, source/generation path, reproduction command, location/URL, and
  verification classification.
- **Historical roadmap:** phase narrative plus a chronological milestone table with evidence.
- **Current status:** explicit reconciliation of code, backlog, handover, registry, and Git/CI state.
- **Future direction:** five separately labelled authorisation categories; never blend inference with
  committed direction.
- **Evidence index:** key files, backlog/planning sources, ADRs, logs, handovers, reviews, commits,
  tags, releases, PRs, CI runs, and published artefacts actually used.

## Evidence and writing rules

- Cite repository-relative file paths and line numbers where practical.
- Cite full or unambiguous commit hashes, tags, backlog/ADR IDs, and PR numbers.
- Link externally verified artefacts when accessible.
- Prefer exact dates and label approximate dates.
- Do not fabricate motivation, results, deployment state, or future plans.
- Use GitHub-flavoured Markdown and clear technical prose.
- Explain why a design or historical change matters, not merely what a file contains.
- Avoid generic recommendations, repeated evidence, and review-style ratings.

## Validation

Before finishing:

1. Confirm the target project repository has not changed (`git status` matches the captured initial
   state).
2. Confirm every meaningful tracked content area was inspected or explicitly excluded.
3. Confirm historical claims cite repository/Git evidence.
4. Confirm approved future work comes from authoritative sources.
5. Confirm inferred opportunities are clearly separated.
6. Confirm Markdown links and citations resolve where locally checkable.
7. Confirm the Markdown/HTML filenames and metadata match, YAML frontmatter is not visible in the
   HTML body, every required Markdown heading rendered, the HTML is a complete standalone document,
   the pair contains the same information, generation left no temporary files, and no earlier report
   was overwritten.

## Finish by reporting

Report:

- full paths to both files;
- report version, source revision, and evidence cut-off;
- meaningful file/content-area coverage and exclusions;
- main historical phases identified;
- authoritative future-work position and number of inferred opportunities;
- any unavailable or contradictory evidence; and
- confirmation that the target project repository was unchanged.
