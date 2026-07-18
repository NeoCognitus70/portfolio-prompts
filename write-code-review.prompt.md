# Prompt - Write a comprehensive code review

Paste the text below to the agent when you want a full, evidence-backed review of a portfolio
project, prefixed with `PROJECT=<project folder name>` (see the README registry) — or invoke it
without pasting:
`Read and follow portfolio-prompts/write-code-review.prompt.md using PROJECT=<folder>`.
It uses the
shared code-review template and writes the finished review into the repo's `.review/` folder.

Use **this** prompt for an **onboarded portfolio project** reviewed against its own
`docs/backlog.md`, with the review committed into `.review/`. For an **external or unfamiliar
repository** you want to understand or evaluate as a standalone report (no `PROJECT=`, not
registry-bound), use [github-repo-analysis-prompt.md](github-repo-analysis-prompt.md) instead — the
two overlap on architecture/SOLID/test-strategy, but that one is the external/learning read.

---

You are conducting a **comprehensive code review** of the **`{PROJECT}`** portfolio project. The
invocation names the target as `PROJECT=<folder name at the portfolio root>` - if it did not,
**ask which project**; never guess.

## Inputs and source of truth

Use exactly these paths, relative to the portfolio root (`test-automation-portfolio/`) — except
where the project's registry row in `README.md` at the resolved library root records a deviation
(e.g. a different backlog path or an in-repo template set), which overrides the default:

- **Repository:** `{PROJECT}/`
- **Review template:** `templates/code-review.template.md`
- **Project status source of truth:** `{PROJECT}/docs/backlog.md`
- **Layout contract:** `project-layout.md` at the resolved library root

Read the review template first and follow it as the output contract. Then read `docs/backlog.md`
and treat it as the canonical current project state (if it does not exist, note that as a finding
in itself - the project is not onboarded to the portfolio conventions). If other docs conflict
with the backlog, call out the conflict in the review rather than silently choosing the nicer story.

## Role and review standard

Act as a Senior Test Automation Architect / Senior Software Engineer reviewing a portfolio repository
for mid-level QA automation testers, software engineers, hiring managers, and technical leads.

First establish the project's stack and intent from its `README.md` and `package.json`, then
review for:

- Correctness and reliability of the test implementation for the stack the project declares
  (e.g. Cucumber + Serenity/JS + Playwright; playwright-bdd; vitest).
- Strength of the architectural pattern the project teaches or uses (e.g. Screenplay: Tasks,
  Questions, Abilities, interactions, and step glue), and whether the implementation is faithful
  to it.
- Quality of any executable specifications (Gherkin or equivalent) and whether they remain
  business-readable.
- Test isolation, async waits, runtime lifecycle, data setup, API usage, and suite stability.
- Stack-specific risks - derive these from the project's own README, docs, and configuration
  rather than assuming another project's risk profile.
- Documentation consistency across README, backlog, ADRs, strategy docs, runbooks, and
  implementation logs (where present).
- Portfolio credibility: whether the repo proves senior automation judgement in a reviewable way.

Prioritise concrete findings over generic advice. Every significant issue must include file paths, line
numbers, impact, and a practical remediation strategy.

## Required scope

Map the repo first (`rg --files`), then review it in full, with special attention to:

- Executable specifications (`features/`, `spec/`, `tests/` - whatever the project uses): tags,
  structure, deferred/quarantined coverage.
- The source layers (`src/` and its subdivisions): pattern implementation and glue quality.
- Build/runner configuration: `package.json`, `package-lock.json`, `tsconfig*.json`, and the test
  runner configs the project uses (e.g. `cucumber.js`, `playwright.config.ts`, `vitest.config.ts`).
- CI: `.github/workflows/`, plus any Docker/compose files and supporting infrastructure the
  project ships.
- Any application or fixture modules the repo carries to support the tests.
- `README.md`, `CHANGELOG.md`, `docs/` (backlog, ADRs, guides, implementation logs - whatever
  exists), and any `planning/` documents.

Exclude generated or dependency-heavy folders from manual review unless a finding requires them:
`node_modules/`, `.git/`, `dist/`, `vendor/`, `var/`, `generated/`, `target/`, generated
reports (`playwright-report/`, `test-results/`, Serenity output), screenshots, traces, archives,
and temporary probe files.

## Fact-gathering workflow

Before writing findings:

1. Inspect repository state:
   - `git status --short`
   - `git log --oneline -10`
   - `rg --files`
2. Read the review template completely.
3. Read `docs/backlog.md` completely and summarise its current claims in your notes (suite health,
   published artefacts, open items). Validate those claims against the repo where possible; do not
   assume they are true without evidence.
4. Inspect the implementation and docs listed in the required scope.
5. Run lightweight validation if dependencies are available, resolving the project's gates per
   `project-layout.md` at the resolved library root §"Validation gates" — the canonical
   first-hit-wins cascade lives there in full (project-contract `Gates` -> registry-row gates -> root `npm run verify` ->
   stack defaults run inside the relevant stack directory -> ask; with the cucumber-js vs
   playwright-bdd nuance).
   - Do not start heavyweight infrastructure (e.g. a full Docker application stack) or a long E2E
     run unless explicitly asked. If you do not run tests, state that clearly in the review.

## Review output

Write the completed review inside the repository under:

```text
.review/CODE_REVIEW_{AGENT}_v{N}_{UTC_TIMESTAMP}/
```

(or under the review location the project's registry row records as a deviation, e.g.
`DOCS/.review/` — match where the project's existing reviews live).

Follow the template's folder structure and filenames exactly. Determine `{N}` by inspecting existing
`CODE_REVIEW_*_v*_*` directories **in that same location** and incrementing the highest version for the current agent. If no
review exists for the current agent, use `v1`. Use a UTC timestamp in `YYYYMMDDTHHMMZ` format with no seconds.

Use the current assistant identity for `{AGENT}` and reviewer attribution:

```text
Reviewer: AI assistant ({AGENT_NAME})
```

Replace `{AGENT_NAME}` with the model/agent actually performing this review. Never copy the
identity from a previous review directory.

## Required deliverables

Create every file required by the template:

- Main index: `00_CODE_REVIEW_{AGENT}_v{N}_{UTC_TIMESTAMP}.md`
- `01_EXECUTIVE_SUMMARY.md`
- `02_RISKS_AND_ISSUES.md`
- `03_PROJECT_REVIEWS/PROJECT_001_*.md` and any additional project files that fit the repo structure
- `04_CROSS_PROJECT_ANALYSIS.md`
- `05_RECOMMENDATIONS.md`
- `06_ARCHITECTURE_ASSESSMENT.md`
- `07_MIGRATION_PLANS.md`
- Optional `ANNEX/` files only when they add useful evidence, metrics, or deep dives

Each portfolio repo is a **single-project repository** - apply the template's "Single-repository
reviews" customisation notes: `03_PROJECT_REVIEWS/` carries only `PROJECT_001_*.md`; treat
`04_CROSS_PROJECT_ANALYSIS.md` as cross-cutting analysis within the repo (suite vs CI vs
infrastructure vs docs vs any app/fixture modules); and where a template section or checklist
quantity does not apply, keep the heading and write `N/A - <one-line justification>` instead of
padding.

The review must include, at minimum:

- High-to-low risk list with evidence, impact, and remediation.
- Strengths as well as weaknesses.
- A specific assessment of any deferred, quarantined, or planned-but-unimplemented coverage the
  backlog or planning docs name, against what the repo actually implements.
- A specific assessment of runtime lifecycle, test isolation, waits/synchronisation, and suite
  stability for the project's stack.
- A specific assessment of data setup and any API/token/auth assumptions the suite makes.
- A CI assessment covering workflow correctness, caching/image strategy, secrets, published
  artefacts, and local reproducibility.
- Documentation alignment against `docs/backlog.md`.
- A dependency, security, and licence pass: lockfile freshness and any outdated or abandoned
  dependencies; an audit (`npm audit` or the stack equivalent) **if the toolchain is available** -
  otherwise inspect versions manually and state that the audit was not run; secrets committed to
  the tree and any unsafe-input / injection surfaces; and the declared licence (or its absence).
  Report with file:line; never fabricate a CVE.
- Architecture assessment against Test Pyramid, SOLID, KISS, YAGNI, REST/OpenAPI (where APIs are
  involved), ISTQB strategies, and pedagogical value.

## Evidence rules

- Use repository-relative paths in review files, matching the template format:
  `[filename.ext](path/to/filename.ext) (line XX)`.
- Include short fenced code snippets only when they clarify a finding.
- Prefer exact line numbers from the current files.
- If a claim is inferred rather than proven by a command or source file, label it as an inference.
- Do not invent test results, CI status, report availability, or GitHub state. If you cannot verify
  something locally, say so.

## Writing rules

- Markdown, GitHub-flavoured.
- ASCII only.
- en-GB spelling throughout (behaviour, prioritise, recognise...), as in the rest of the portfolio.
- Clear, direct, reviewer-ready prose.
- No implementation changes unless explicitly requested. This task is to write review artifacts.
- Keep all navigation links required by the template: breadcrumb headers, footers, and a complete index.
- Make the review useful to both a portfolio reviewer and the next engineer who might improve the repo.

## Finish by reporting

After writing the review, report:

- The full path to the review directory.
- The list of files created.
- Any validation commands run and whether they passed.
- The top 3-5 findings by severity.
