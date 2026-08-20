# Prompt — Analyse a GitHub repository (pedagogical technical report)

General-purpose analysis prompt — produces a deep, evidence-based, teaching-oriented report on an
**arbitrary** repository (typically one *outside* this portfolio). Paste the text below the `---`
divider, or invoke it without pasting:
`Read and follow portfolio-prompts/github-repo-analysis-prompt.md`, then supply the repository
inputs.

**This is the outlier in the library.** Unlike the other prompts it is **not** registry-bound and
takes **no `PROJECT=`** — its target is any repo by URL or local path. Use it for an unfamiliar or
external codebase you want to understand or evaluate for adoption, and where the deliverable is a
standalone report. For an *onboarded portfolio project* reviewed against its own `docs/backlog.md`
and committed into `.review/`, use [write-code-review.prompt.md](write-code-review.prompt.md)
instead. For a descriptive, historical account of one onboarded project's intention, design,
outputs, implementation chronology, current state, and future direction, use
[write-project-in-depth-report.prompt.md](write-project-in-depth-report.prompt.md). The three
workflows deliberately separate external learning/adoption analysis, portfolio code review, and
portfolio project documentation.

---

You are an expert software architect, senior test automation architect, and technical educator.

Your task is to analyse the supplied repository and produce a pedagogical technical report. The
report must explain what the repository does, why it exists, what problem it is trying to solve,
how it is designed, how it is tested or should be tested, and how the code works.

The report must be suitable for a technically experienced reader who wants to understand the
repository deeply, not just get a surface-level summary.

## Repository input

* Repository URL or local path: `<insert GitHub URL or filesystem path>`
* Branch or commit, if known: `<insert branch, tag, or commit>`
* Primary areas of interest: `<insert optional focus areas>`
* Intended audience: `<insert audience, e.g. senior engineer, tester, architect, learner>`
* Preferred depth: `<summary | standard | deep-dive>` (default: standard)

## Step 0 — Acquire and scope the repository before analysing anything

Do this first; do not write a single finding until you have the code in front of you.

1. **Get the code.** If given a local path, work from it. If given a URL, clone it
   (`git clone --depth 50 <url>`; check out the named branch/commit if supplied). If you cannot
   access the repository (no network, private repo, no credentials), **stop and say so** — request
   access or an archive rather than analysing from the URL string or from memory. Never describe a
   repository you have not actually read.
2. **Map it.** `git ls-files` (or a recursive listing) for the file tree; read `README*`,
   `LICENSE*`, and every dependency manifest (`package.json`, `pyproject.toml`/`requirements.txt`,
   `*.csproj`/`*.sln`, `go.mod`, `pom.xml`, `Cargo.toml`, etc.) before forming any conclusion.
3. **Read the history, cheaply.** `git log --oneline -20`, `git shortlog -sne | head`, and the
   dates of the first and last commits — commit cadence, contributor count, and recency are strong,
   low-cost maturity signals that sections 2 and 14 depend on.
4. **Detect the shape.** Single-language single-tree, or **multi-stack / monorepo** (several
   independent toolchains, no single root manifest)? If multi-stack, treat each stack as its own
   sub-tree throughout: produce a per-stack repository map (§2), and run any stack-specific
   reasoning inside the relevant sub-tree, never assuming one shared `src/`+`tests/` layout.

## Depth control — make the template fit the repo

The `Preferred depth` input selects how much of the structure below you emit. Honour it; do not
emit a 14-section report for a 200-line library.

* **summary** — sections **1, 5 (high-level only), 9.5, 13 (top items), 14** plus the rating
  table. One page for a stakeholder.
* **standard** (default) — sections **1–6, 8, 9, 10, 12, 13, 14**. Omit 7 and 11 unless the repo
  has non-trivial algorithms or a teaching purpose that warrants a walkthrough.
* **deep-dive** — **all 14 sections.**

In any tier, if a *retained* section genuinely does not apply to this repo, keep the heading and
write `N/A — <one-line justification>` rather than padding it with generic prose. A short, honest
report beats a long, inflated one.

## Analysis rules

1. Inspect the repository structure (Step 0) before drawing conclusions.
2. Base **all** findings on actual repository evidence.
3. Cite file paths and line numbers where possible (`path/to/file.ext:42`).
4. Use short code snippets to explain important concepts — only where they add explanatory value.
5. Do not invent behaviour unsupported by the code, documentation, tests, configuration, or commit
   structure.
6. Clearly distinguish between:
   * What the repository explicitly shows
   * What can be reasonably inferred (label it as an inference)
   * What is missing or unclear
7. Explain reasoning step by step where it aids understanding.
8. Prefer precise, technical explanations over generic commentary; avoid filler.
9. Adapt tone and depth to the stated **audience** (a learner needs more "why", an architect more
   trade-offs).
10. When uncertain, say so directly.

Produce the report using the following structure (subject to the depth control above).

# Repository Analysis Report

## 1. Executive Summary

A concise summary covering: the repository's apparent purpose; the problem it solves; the main
technologies; the architectural style; the current testing position; the main strengths; the main
risks, gaps, or unknowns. Readable for a technical stakeholder who may not read the full report.

## 2. Repository Overview

Explain: repository name and apparent domain; primary language(s); frameworks, libraries, tooling;
build system and package management; entry points; main folders and their responsibilities;
configuration files and what they suggest; and (from Step 0.3) the history signals — age, commit
cadence, contributor count, recency.

Include a repository map of **only directories/files actually present**, for example:

```text
/repository-root
  /src              - application source code
  /tests            - automated tests
  /docs             - documentation
  package.json      - dependency and script configuration
  README.md         - project overview
```

For a **multi-stack / monorepo**, give one map per stack and note the absence of a unifying root
toolchain.

## 3. Purpose and Intention

What the repository appears intended to do: the user/developer need it addresses; likely target
users; supported workflows; the business or technical problem; and whether the README, docs,
source, test names, API routes, CLI commands, configuration, and example data support this
interpretation. Cite the evidence.

## 4. Problem Statement

Describe the problem in plain language: domain, inputs, outputs, constraints, failure modes, the
value the solution provides, and what would happen if this repository did not exist. Where
appropriate, express it as:

```text
Given <context>
When <event or input>
Then <expected outcome>
```

## 5. Architectural Design

Analyse: high-level architecture; major components and their responsibilities; dependency
direction; separation of concerns; layering; external integrations; persistence; API boundaries;
configuration strategy; error handling; logging/observability; security considerations. Use a
text diagram where useful, and identify the pattern if evident (layered, hexagonal, clean, MVC,
microservice, modular monolith, event-driven, CLI tool, library/package, test-automation
framework). If the architecture is unclear or inconsistent, explain why.

## 6. Data Flow

How data moves through the system: inputs, outputs, transformations, validation points,
persistence points, external calls, error/retry paths, state management. Include at least one
end-to-end flow and, where useful, a simplified text sequence diagram.

## 7. Algorithms and Core Logic

For each meaningful algorithm or logic area: file path; function/class/module; purpose; inputs;
outputs; step-by-step behaviour; complexity where relevant; edge cases; risks or assumptions. Use
short snippets, then explain why the code matters, what decision it makes, how it serves the
repository's purpose, and any hidden complexity. If no formal algorithms exist, explain the main
business rules, orchestration, validation, or framework behaviour instead.

## 8. SOLID Principles Review

### 8.1 Single Responsibility — focused responsibilities? Good examples, problem examples, refactors.
### 8.2 Open/Closed — extensible without modifying existing logic? Interfaces, strategies, plugin points vs hard-coded branching.
### 8.3 Liskov Substitution — are abstractions and implementations safely interchangeable? If the repo barely uses inheritance/polymorphism, say so.
### 8.4 Interface Segregation — are contracts appropriately focused? Large interfaces, unused methods, role-specific contracts.
### 8.5 Dependency Inversion — dependency direction; high-level modules on abstractions; coupling to frameworks/DB/HTTP/filesystem/third-party libs.

Summarise in a table:

| Principle | Observed position | Evidence | Risk | Recommendation |
| --------- | ----------------- | -------- | ---- | -------------- |

## 9. ISTQB-Aligned Test Strategy Review

### 9.1 Test Levels — evidence of unit, component, integration, API, E2E, acceptance, contract, performance, security tests, static analysis.
### 9.2 Test Types — functional, non-functional, regression, smoke, exploratory support, negative, boundary value, equivalence partitioning, error handling, accessibility/security/performance where relevant.
### 9.3 Test Design Techniques — boundary value analysis, equivalence partitioning, decision tables, state transition, pairwise, use case, risk-based.
### 9.4 Test Automation Strategy — framework choices, maintainability, test data, mocking/stubbing, fixtures, CI integration, reporting, flakiness risks, isolation, naming, Arrange-Act-Assert, BDD usage.
### 9.5 Test Gaps and Recommendations — strengths; missing levels; missing types; high-risk areas; suggested priority; example test cases.

| Area | Current evidence | Risk | Recommended tests | Priority |
| ---- | ---------------- | ---- | ----------------- | -------- |

## 10. Code Quality and Maintainability

Readability, naming, modularity, duplication, complexity, error handling, configuration
management, dependency management, documentation, build reproducibility, security hygiene,
observability, maintainability risks. Include concrete examples from the code.

## 11. Pedagogical Code Walkthrough

Select the most important parts and teach them. For each: a short snippet; what it does; why it
exists; how it fits the wider system; design trade-offs; what a maintainer should watch. Format:

```text
File: <path>
Concept: <concept name>
Why it matters: <reason>
```

## 12. Dependency, Security, and Licence Review

(For an external repo this is often the reader's top question — "should I trust/adopt this?")

* **Dependencies:** read the lockfile; flag outdated, abandoned, or unusually heavy dependencies.
  Run `npm audit` / `pip-audit` / equivalent **if the toolchain is available**; otherwise inspect
  versions manually and say the audit was not run.
* **Security hygiene:** secrets in the tree, unsafe input handling, injection/eval surfaces,
  auth/token assumptions, dangerous defaults. Report with file:line; do not fabricate a CVE.
* **Licence:** state the licence from `LICENSE`/manifest, note any copyleft or
  incompatible-dependency concern, or that no licence is declared (a real adoption risk).

## 13. Architectural Risks and Trade-offs

Coupling, scalability, testing, security, data-consistency, maintainability, deployment,
dependency, and documentation risks. For each: evidence, impact, likelihood, mitigation.

| Risk | Evidence | Impact | Likelihood | Mitigation |
| ---- | -------- | ------ | ---------- | ---------- |

## 14. Improvement Roadmap and Final Assessment

Practical recommendations in priority order — **Immediate / Short-term / Medium-term /
Longer-term** — each with what to change, why it matters, expected benefit, approximate effort,
and risk of not doing it.

Then conclude with overall technical maturity, architectural clarity, test-strategy maturity,
maintainability outlook, suitability for extension, and key learning points. Finish with:

| Category        | Assessment | Rationale |
| --------------- | ---------- | --------- |
| Purpose clarity | <rating>   | <reason>  |
| Architecture    | <rating>   | <reason>  |
| SOLID alignment | <rating>   | <reason>  |
| Test strategy   | <rating>   | <reason>  |
| Maintainability | <rating>   | <reason>  |
| Security/deps   | <rating>   | <reason>  |
| Documentation   | <rating>   | <reason>  |

Ratings: **Strong | Adequate | Mixed | Weak | Unclear.**

## Output Requirements

The final report must: start with the executive summary; use clear headings; use code snippets
only where they add explanatory value; include file:line references; explain reasoning, not just
conclusions; avoid generic filler; be evidence-based; highlight unknowns explicitly; and be
genuinely useful to someone learning the repository.

* **House style:** en-GB spelling (behaviour, prioritise, recognise...), ASCII only — consistent
  with the rest of the portfolio's written artefacts.
* **Destination:** write the report to a file named
  `REPO_ANALYSIS_<repo-name>_<YYYYMMDD>.md` in the working directory (or wherever the invocation
  asks), and report the path; if the invocation asks only for a chat report, deliver it inline
  instead. Do not commit it into the analysed repo.

If repository access is incomplete, state what could not be inspected and provide a partial
analysis based only on available evidence.
