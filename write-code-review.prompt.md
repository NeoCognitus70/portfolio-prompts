# Prompt - Write a comprehensive code review

Paste the text below to the agent when you want a full, evidence-backed review of the
**magento-checkout-automation** portfolio project. It uses the shared code-review template and writes
the finished review into the repo's `.review/` folder.

---

You are conducting a **comprehensive first-time code review** of the
**magento-checkout-automation** project.

## Inputs and source of truth

Use exactly these paths, relative to the portfolio root (`test-automation-portfolio/`):

- **Repository:** `magento-checkout-automation/`
- **Review template:** `templates/code-review.template.md`
- **Project status source of truth:** `magento-checkout-automation/docs/backlog.md`

Read the review template first and follow it as the output contract. Then read `docs/backlog.md` and
treat it as the canonical current project state. If other docs conflict with the backlog, call out the
conflict in the review rather than silently choosing the nicer story.

## Role and review standard

Act as a Senior Test Automation Architect / Senior Software Engineer reviewing a portfolio repository
for mid-level QA automation testers, software engineers, hiring managers, and technical leads.

Review for:

- Correctness and reliability of the Cucumber + Serenity/JS + Playwright implementation.
- Strength of the Screenplay architecture: Tasks, Questions, Abilities, interactions, and step glue.
- Quality of the Gherkin specifications and whether they remain business-readable.
- Test isolation, async waits, browser lifecycle, data setup, API usage, and checkout stability.
- Magento-specific risks, including Knockout.js checkout behaviour, Docker target setup, CI, and the
  custom payment-decline module.
- Documentation consistency across README, backlog, ADRs, strategy docs, runbooks, and implementation logs.
- Portfolio credibility: whether the repo proves senior automation judgement in a reviewable way.

Prioritise concrete findings over generic advice. Every significant issue must include file paths, line
numbers, impact, and a practical remediation strategy.

## Required scope

Review the full repo, with special attention to:

- `features/` - Gherkin specs, tags, scenario structure, deferred/quarantined coverage.
- `src/hooks/`, `src/tasks/`, `src/questions/`, `src/interactions/`, `src/api/`, and
  `src/step-definitions/` - Screenplay implementation and glue quality.
- `cucumber.js`, `src/serenity.config.ts`, `tsconfig.json`, `package.json`, and `package-lock.json`.
- `docker-compose.yml`, `docker-compose.ci.yml`, `Dockerfile.store-app`, `Dockerfile.store-db`,
  `docker/nginx/default.conf`, and `.github/workflows/`.
- `app/code/Portfolio/DeclinePayment/` - Magento module used to support deterministic payment failure.
- `README.md`, `CHANGELOG.md`, `docs/backlog.md`, `docs/architecture.md`, `docs/qa-strategy.md`,
  `docs/docker-magento-setup.md`, `docs/admin-api-token-guide.md`, `docs/screenplay-guide.md`,
  `docs/gherkin-style-guide.md`, `docs/adr/`, and `docs/implementation-logs/`.

Exclude generated or dependency-heavy folders from manual review unless a finding requires them:
`node_modules/`, `.git/`, `vendor/`, `var/`, `generated/`, `pub/static/`, `target/`, Serenity generated
reports, screenshots, traces, archives, and temporary probe files.

## Fact-gathering workflow

Before writing findings:

1. Inspect repository state:
   - `git status --short`
   - `git log --oneline -10`
   - `rg --files`
2. Read the review template completely.
3. Read `docs/backlog.md` completely and summarise the current state in your notes:
   - Active suite is expected to be green in CI.
   - The published Serenity report is expected to be live.
   - The main remaining backlog item is activating the deferred payment-failure scenario.
   - Validate these statements against the repo where possible; do not assume they are true without evidence.
4. Inspect the implementation and docs listed in the required scope.
5. Run lightweight validation if dependencies are available:
   - `npx cucumber-js --profile default --dry-run` — zero undefined/ambiguous steps.
   - `npx tsc --noEmit`.
   - Do not start a full Magento Docker stack or long E2E run unless explicitly asked. If you do not run
     tests, state that clearly in the review.

## Review output

Write the completed review inside the repository under:

```text
.review/CODE_REVIEW_{AGENT}_v{N}_{UTC_TIMESTAMP}/
```

Follow the template's folder structure and filenames exactly. Determine `{N}` by inspecting existing
`.review/CODE_REVIEW_*_v*_*` directories and incrementing the highest version for the current agent. If no
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

This is a **single-project repository** — apply the template's "Single-repository reviews"
customisation notes: `03_PROJECT_REVIEWS/` carries only `PROJECT_001_*.md`; treat
`04_CROSS_PROJECT_ANALYSIS.md` as cross-cutting analysis within the repo (suite vs CI vs Docker
vs docs vs the Magento module); and where a template section or checklist quantity does not
apply, keep the heading and write `N/A - <one-line justification>` instead of padding.

The review must include, at minimum:

- High-to-low risk list with evidence, impact, and remediation.
- Strengths as well as weaknesses.
- A specific assessment of the outstanding `@deferred` payment-failure work against the implemented
  `Portfolio_DeclinePayment` Magento module.
- A specific assessment of browser lifecycle, scenario isolation, waits, and Knockout.js checkout stability.
- A specific assessment of API-driven Background setup and admin-token/2FA assumptions.
- A CI and Docker assessment covering pre-baked images, health checks, GHCR dependency, secrets, Pages
  publishing, and local reproducibility.
- Documentation alignment against `docs/backlog.md`.
- Architecture assessment against Test Pyramid, SOLID, KISS, YAGNI, REST/OpenAPI, ISTQB strategies, and
  pedagogical value.

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
