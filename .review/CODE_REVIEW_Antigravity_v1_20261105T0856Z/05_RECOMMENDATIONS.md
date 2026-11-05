# Recommendations

[<- Back to Index](00_CODE_REVIEW_Antigravity_v1_20261105T0856Z.md) | [Next: Architecture Assessment ->](06_ARCHITECTURE_ASSESSMENT.md)

**Reviewer:** AI assistant (Antigravity)
**Date:** 2026-11-05T08:56Z
**Scope:** Actionable Refactoring, Next Steps, and Strategic Roadmap

---

## 1. Recommended Refactors (Priority Improvements)

- **Optimise Preflight Git Fixtures in `test_workspace_preflight.py`:**
  - *Location:* [tools/tests/test_workspace_preflight.py](../../tools/tests/test_workspace_preflight.py) (lines 22-35).
  - *Refactor:* Replace the per-test `setUp()` fixture instantiation with `setUpClass()`. Because the inspection logic in `workspace_preflight.py` is strictly read-only, sharing a single set of six mocked repositories across test methods eliminates over 120 redundant Git process invocations on Windows, reducing execution time from 320 seconds to under 20 seconds.
- **Implement Non-Mutating `--check` Mode in `build-portfolio-reviews.py`:**
  - *Location:* [tools/build-portfolio-reviews.py](../../tools/build-portfolio-reviews.py) (lines 9-20 and 445-460).
  - *Refactor:* Implement CLI flag handling supporting `--check`. In `--check` mode, compare generated markdown and HTML strings against disk contents without writing, exiting with code 1 upon detected drift. Integrate `check_portfolio_reviews_generated` into [tools/check-library.py](../../tools/check-library.py) to gate review index synchronization.
- **Commit `package-lock.json` in `tools/kanban` for Clean Security Audits:**
  - *Location:* [tools/kanban/package.json](../../tools/kanban/package.json) (lines 1-51).
  - *Refactor:* Execute `npm i --package-lock-only` within `tools/kanban` to generate a lightweight, empty-dependency lockfile. This satisfies automated corporate vulnerability scanners (`npm audit`) without adding third-party runtime or development dependencies.
- **Formalise Python Dependency Manifest for Maintenance Tools:**
  - *Location:* Repository root.
  - *Refactor:* Create a minimal `requirements-tools.txt` or `pyproject.toml` pinning `PyYAML==6.0.3` and `markdown>=3.6.0`. Update [.github/workflows/library-integrity.yml](../../.github/workflows/library-integrity.yml) to install from this manifest, resolving the undocumented dependency requirement in [tools/generate_sut_pedagogical_reports_html.py](../../tools/generate_sut_pedagogical_reports_html.py).
- **Unit Test Coverage for Core Generator Utilities:**
  - *Location:* [tools/tests/](../../tools/tests/).
  - *Refactor:* Introduce unit test suites for `build-portfolio-reviews.py` and `render-registry.py`, isolating regex parsing of reviewer attribution, timestamps, and table formatting to guard against silent markdown corruption.

---

## 2. Next Steps (Immediate Action Items)

- **Audit CI Execution Duration in GitHub Actions:**
  - Review recent GitHub Actions run durations for `library-integrity.yml`. If runner queue times or step execution times approach 4 minutes, bump the job timeout to 10 minutes to prevent transient timeout failures.
- **Perform Drift Check on Portfolio Review Summaries:**
  - Once `--check` is added to `build-portfolio-reviews.py`, run a manual check across all registered showcase review directories to verify that no recent review bundles have been omitted from `portfolio-reviews/README.md`.
- **Verify Codex and Claude Plugin Cache Ingestion:**
  - Confirm that the latest plugin descriptor updates ([.claude-plugin/plugin.json](../../.claude-plugin/plugin.json) and [.codex-plugin/plugin.json](../../.codex-plugin/plugin.json)) load without warning or validation error in both assistant environments, specifically testing the three default prompts.
- **Document Windows Test Execution Nuance in `tools/README.md`:**
  - Add an operational note in [tools/README.md](../../tools/README.md) advising developers running on Windows that `unittest discover` can take 5+ minutes due to NTFS process creation overhead, detailing how to execute focused tests via `-k` or specific test module paths during rapid iteration.

---

## 3. Future Project Ideas (Long-Term Enhancements)

- **Single-Source Prompt-to-Skill Generation:**
  - Replace the dual maintenance of canonical Markdown prompts (`*.prompt.md`) and thin skill wrappers (`skills/*/SKILL.md`) with a build-time compiler. A single source specification could mechanically generate both CLI-pasteable prompt files and Claude/Codex skill folders, eliminating any possibility of divergent instructions.
- **Native JSON Schema Validation for `registry.yml`:**
  - Formalise a standard JSON Schema (`schemas/registry.schema.json`) for [registry.yml](../../registry.yml). Utilize `jsonschema` in [tools/check-library.py](../../tools/check-library.py) to provide declarative validation of fields, types, and allowed enums, replacing imperative dict-checking logic.
- **WebAssembly / Static Browser Kanban Preview:**
  - Package the Kanban generation engine into an in-browser WASM or pure client-side ES module within `portfolio-landing`, allowing stakeholders to drag-and-drop or live-preview local `backlog.md` files without requiring Node.js to be installed on their host machines.
- **Automated Docker Cleanup Assistant:**
  - Extend [tools/docker_inventory.py](../../tools/docker_inventory.py) with an interactive or gated `--cleanup-script` generator that produces approved, reversible `docker rm` and `docker volume rm` shell scripts specifically targeting orphaned, unclaimed containers and volumes.

---

[<- Previous: Cross-Project Analysis](04_CROSS_PROJECT_ANALYSIS.md) | [Back to Index](00_CODE_REVIEW_Antigravity_v1_20261105T0856Z.md) | [Next: Architecture Assessment ->](06_ARCHITECTURE_ASSESSMENT.md)
