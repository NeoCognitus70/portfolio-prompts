# Cross-Project and Cross-Cutting Analysis

[<- Back to Index](00_CODE_REVIEW_Antigravity_v1_20261105T0856Z.md) | [Next: Recommendations ->](05_RECOMMENDATIONS.md)

**Reviewer:** AI assistant (Antigravity)
**Date:** 2026-11-05T08:56Z
**Repository Scope:** `portfolio-prompts` Cross-Cutting Architecture Analysis

This section evaluates the cross-cutting architectural themes, standards compliance, and internal cohesion within the `portfolio-prompts` repository and its interactions with child portfolio projects.

---

## 1. Tool-Agnostic Automation Guidance

- **Dual-Agent Portability:** Prompts and skills are engineered to be entirely platform-agnostic across AI coding assistants. The library ships dual manifests: [.claude-plugin/plugin.json](../../.claude-plugin/plugin.json) for Anthropic Claude Code and [.codex-plugin/plugin.json](../../.codex-plugin/plugin.json) for OpenAI Codex, backed by portable [skills/*/SKILL.md](../../skills/) wrappers that map 1:1 to canonical Markdown prompts.
- **Path and Invocation Portability:** All active invocation patterns and script calls strictly employ forward slashes (e.g. `portfolio-prompts/tools/check-library.py`), validated automatically by [tools/check-library.py](../../tools/check-library.py) lines 570-582 (`check_invocation_paths`) to prevent Windows-specific backslash lock-in.
- **Polyglot Runner Compatibility:** The prompt library's validation gate cascade ([project-layout.md](../../project-layout.md) lines 131-150) seamlessly accommodates diverse testing toolchains across child projects--supporting Serenity/JS, Playwright, Cucumber-JS, Playwright-BDD (`bddgen`), Pytest, Cypress, and .NET Reqnroll without toolchain favouritism.
- **Sub-Agent Orchestration Fallback:** Orchestration specifications ([project-layout.md](../../project-layout.md) lines 317-319) require sub-agent fan-out workflows to gracefully fall back to sequential parent execution if the hosting environment lacks sub-agent spawning capabilities.

---

## 2. Code-Agnostic Specifications & Artifacts

- **Standardised Control State:** Worklists are maintained in plain Markdown ([project-layout.md](../../project-layout.md) lines 224-255) using standard GFM checklist syntax (`- [ ] <id> -- <description> -- <source>`), ensuring that any programming language or shell script can parse, update, and track task state.
- **Self-Contained Output Deliverables:** The shared Kanban board generator ([tools/kanban/](../../tools/kanban/)) emits vanilla HTML, CSS, and embedded JSON datasets without reliance on front-end frameworks (React, Vue, Angular) or external CDNs, ensuring lifelong offline viewability.
- **Platform-Neutral Manifest Schema:** Handover state ([tools/build-handover-manifest.py](../../tools/build-handover-manifest.py)) and Docker records ([tools/docker_inventory.py](../../tools/docker_inventory.py)) output standard UTF-8 JSON representations, allowing cross-language consumers in Python, Node.js, PowerShell, or Bash to process metadata identically.

---

## 3. Single Source of Truth (SSOT)

- **Centralised Layout Contract:** All conventions governing paths, naming schemes, gate cascades, and working norms reside authoritatively in [project-layout.md](../../project-layout.md). Individual prompts link to this document rather than duplicating rules, preventing documentation drift.
- **Machine-Readable Registry:** [registry.yml](../../registry.yml) serves as the sole source of truth for repository configurations. The human-readable table in [README.md](../../README.md) is strictly generated via [tools/render-registry.py](../../tools/render-registry.py), with drift detection enforced by CI.
- **Authoritative Backlog Governance:** Every participating project, including `portfolio-prompts` itself ([docs/backlog.md](../../docs/backlog.md)), designates its backlog as the supreme source of truth for ticket status, priority scores, and risk classifications, superseding stale review comments or handovers.
- **Universal Working Norms:** The universal policy requiring all changes to project `main` branches to go via branch and pull request is defined once in [project-layout.md](../../project-layout.md) (line 326) and strictly prohibited from being restated in operational prompt bodies ([tools/check-library.py](../../tools/check-library.py) lines 547-568).

---

## 4. API & Schema Contract Compliance

- **Codex & Claude Plugin Specification Conformance:** Plugin descriptors in [.claude-plugin/](../../.claude-plugin/) and [.codex-plugin/](../../.codex-plugin/) strictly conform to vendor schemas. [tools/check-library.py](../../tools/check-library.py) (lines 370-382 and 446-545) verifies that suggested default prompts do not exceed the platform maximum of three and that marketplace descriptors declare valid installation and authentication policies.
- **Registry Schema Validation:** The structure of [registry.yml](../../registry.yml) is programmatically validated against expected keys (`projects`, `defaults`, `support_repositories`, `docker_external`) and enum constraints (`status`: `active`, `resting`, `meta`; `presentation_role`: `showcase`, `methodology`, `hidden`).
- **REST & OpenAPI Guidance for Child Projects:** While `portfolio-prompts` does not expose HTTP APIs directly, prompts such as [write-code-review.prompt.md](../../write-code-review.prompt.md) and [write-sut-architecture-report.prompt.md](../../write-sut-architecture-report.prompt.md) mandate rigorous auditing of REST/OpenAPI contract compliance across child projects (e.g. `auth-separation`, `credit-dashboard-sut`).

---

## 5. Screenplay Pattern Guidance & Parity

- **N/A - Direct Implementation:** `portfolio-prompts` is a meta-control repository and does not implement the Screenplay Pattern in its own codebase.
- **Pedagogical Governance of Child Screenplay Suites:** The library actively governs and reviews Screenplay implementations across child showcase repositories (e.g. `hand-baked-screenplay-pattern`, `calculator-screenplay-bdd`, `parabank-bank-automation`, `saleor-graphql-automation`, and `tradeblotter-wpf-screenplay`), evaluating their adherence to Tasks, Questions, Abilities, and Actors via [write-code-review.prompt.md](../../write-code-review.prompt.md) (lines 51-53).

---

## 6. Script & Batch File Design

- **POSIX and Windows Dual-Support:** Python maintenance scripts in [tools/](../../tools/) run cross-platform on Windows and Linux without modifying system paths or requiring platform-specific wrappers.
- **Subprocess Defensive Isolation:** [tools/workspace_preflight.py](../../tools/workspace_preflight.py) (lines 45-62) executes Git commands with `check=False`, captures stdout/stderr cleanly, disables optional locks, and validates command tokens against an immutable allowlist prior to execution.
- **Deterministic HTML/Markdown Generation:** Generation scripts employ standard encoding (`encoding="utf-8"`), explicit Unix line endings, and deterministic dictionary sorting, ensuring clean Git diffs across operating systems.
- **Script Quality Drift:** While core utilities ([check-library.py](../../tools/check-library.py), [workspace_preflight.py](../../tools/workspace_preflight.py)) follow rigorous software engineering practices, report generators ([build-portfolio-reviews.py](../../tools/build-portfolio-reviews.py), [generate_in_depth_reports_index.py](../../tools/generate_in_depth_reports_index.py)) display design drift by lacking argument parsers, `--check` switches, and unit tests.

---

## 7. Documentation Alignment & Synchronization

- **Automated Hyperlink Validation:** [tools/check-library.py](../../tools/check-library.py) lines 228-243 (`check_internal_links`) traverses all Markdown documentation across the repository, ensuring every relative link resolves to a valid file on disk.
- **Release Metadata Consistency:** Backlog item counts, total outstanding tallies, and version identifiers in [docs/backlog.md](../../docs/backlog.md) are cross-checked against plugin manifest versions in [.claude-plugin/plugin.json](../../.claude-plugin/plugin.json) and [.codex-plugin/plugin.json](../../.codex-plugin/plugin.json) on every run ([tools/check-library.py](../../tools/check-library.py) lines 434-444).
- **Comprehensive Implementation Logs:** Every major milestone from PP-31 to PP-42 is meticulously documented with a dedicated record in [docs/implementation-logs/](../../docs/implementation-logs/), capturing exact problem statements, root causes, commit hashes, and verification evidence.

---

## 8. Logging & History Standardization

- **Immutable Implementation Log Trail:** [docs/implementation-logs/](../../docs/implementation-logs/) contains append-only logs following the standardised template [docs/templates/implementation-log.template.md](../../docs/templates/implementation-log.template.md).
- **Paired Handover Control Records:** Session handovers are tracked as immutable `.md` and `.html` pairs in `../session-notes/`. Missing HTML companions trigger hard gate failures in [tools/check-library.py](../../tools/check-library.py) (lines 596-611) and [tools/build-handover-manifest.py](../../tools/build-handover-manifest.py).
- **Execution Evidence Standard:** Prompts enforce empirical evidence capture (exact test numbers, git SHAs, real execution snippets) rather than speculative assertions.

---

## 9. Test Coverage Metrics

- **Unit Test Coverage in Python Tooling:**
  - `tools/tests/test_workspace_preflight.py`: 4 tests (covers matrix scenarios, allowlist, exit codes, and subsets).
  - `tools/tests/test_docker_inventory.py`: 12 tests (covers reference parsing, volume detection, allowlist mutation rejection, and report rendering).
  - `tools/tests/test_kanban_generator.py`: 2 tests (covers cross-language fixture synchronisation and self-contained HTML constraints).
  - `tools/tests/test_prompt_skill_coverage.py`: 6 tests (covers bijection between prompts and skills).
  - `tools/tests/test_registry_semantics.py`: 5 tests (covers presentation roles and orchestration rules).
  - `tools/tests/test_release_metadata.py`: 8 tests (covers backlog consistency, plugin version alignment, and Codex default prompts).
  - `tools/tests/test_handover_manifest.py`: 5 tests (covers pair integrity, numeric sort ordering, and stray file filtering).
  - **Total Python Unit Tests:** 42 passing tests (execution time: ~320s on Windows, ~10s on Linux).
- **Node.js Test Coverage in Kanban Generator:**
  - `tools/kanban/test/adapters.test.mjs`: 20 tests (covers `auth-table` and `risk-block` adapters).
  - `tools/kanban/test/derive-status.test.mjs`: 20 tests (covers status derivation truth tables, priority rules, and statistics tallies).
  - `tools/kanban/test/generator.test.mjs`: 10 tests (covers self-contained generation, determinism, drift checking, and viewport layout constraints).
  - `tools/kanban/test/override.test.mjs`: 10 tests (covers JSON content overrides, ADR resolution, and schema validation).
  - **Total Node.js Unit Tests:** 60 passing tests (execution time: 1.8s).
- **Overall Quantitative Coverage:** 102 automated unit and integration tests, augmented by 15 high-level self-gate invariant checks in `check-library.py`.

---

[<- Previous: Project Reviews](03_PROJECT_REVIEWS/PROJECT_001_PORTFOLIO_PROMPTS.md) | [Back to Index](00_CODE_REVIEW_Antigravity_v1_20261105T0856Z.md) | [Next: Recommendations ->](05_RECOMMENDATIONS.md)
