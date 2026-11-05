# Migration Strategy and Plans

[<- Back to Index](00_CODE_REVIEW_Antigravity_v1_20261105T0856Z.md) | [Back to Main Index](00_CODE_REVIEW_Antigravity_v1_20261105T0856Z.md)

**Reviewer:** AI assistant (Antigravity)
**Date:** 2026-11-05T08:56Z
**Scope:** Strategic Evolution Roadmaps for `portfolio-prompts`

---

## 1. Single Source of Truth for Prompts & Skills (Consolidation Plan)

Currently, the repository maintains canonical prompt files (`*.prompt.md` at root) and thin skill wrappers (`skills/<name>/SKILL.md`) in parallel. While [tools/check-library.py](../../tools/check-library.py) verifies bijection, changes require dual-file bookkeeping.

- **Phase 1: Define Unified Skill-First Canonical Schema:** Establish `skills/<name>/SKILL.md` as the authoritative definition point for both human CLI prompts and automated AI skills, carrying standardized YAML frontmatter and invocation examples.
- **Phase 2: Author Automated Prompt Projection Compiler:** Implement `tools/compile-prompts.py` to project root-level `*.prompt.md` files automatically from `skills/*/SKILL.md`, embedding standard header notices warning against direct manual edits.
- **Phase 3: Integrate Projection Gate in CI:** Wire `compile-prompts.py --check` into [tools/check-library.py](../../tools/check-library.py), failing the self-gate if any root prompt drifts from its skill definition.
- **Phase 4: Deprecate Redundant Root Prompt Files:** In a future major milestone, evaluate updating documentation and agent contracts to read directly from `skills/<name>/SKILL.md`, retiring root-level prompt files entirely.
- **Phase 5: Automated Manifest Synchronization:** Enhance the compiler to regenerate [.claude-plugin/plugin.json](../../.claude-plugin/plugin.json) and [.codex-plugin/plugin.json](../../.codex-plugin/plugin.json) automatically from the skill inventory, eliminating all manual JSON manifest maintenance.

---

## 2. Docker Compose & Containerization Strategy

As a documentation, prompt, and CLI tooling repository, `portfolio-prompts` does not ship an active backend application service requiring a dedicated runtime container. However, its role as the portfolio's Docker auditor requires containerization governance.

- **N/A - Direct Application SUT Container:** `portfolio-prompts` is a meta-control plane and does not require local Docker Compose services for its own execution.
- **Docker Inventory Maintenance:** Maintain [tools/docker_inventory.py](../../tools/docker_inventory.py) as the authoritative read-only auditor for all container images, Compose services, and named volumes across child projects (e.g. Magento, ParaBank, OrangeHRM, Saleor).
- **Enforce Ephemeral Volume Discipline:** Ensure child project `docker:` blocks in [registry.yml](../../registry.yml) declare explicit teardown policies (e.g. `down -v`) to prevent unbounded disk growth in `E:\_DockerData`.
- **Preflight Docker Engine Check:** Update [tools/workspace_preflight.py](../../tools/workspace_preflight.py) to optionally probe Docker daemon responsiveness when evaluating child projects that declare Docker-backed verification gates.
- **Containerised Portable Test Runner (Optional):** Provide an optional, minimal `Dockerfile` for `portfolio-prompts` that encapsulates Python 3.13, Node 20, and PyYAML, enabling engineers on restricted environments to run `check-library.py` in an isolated container without local runtime configuration.

---

## 3. GitHub Actions CI/CD Modernisation & Release Hardening

The current CI workflow ([.github/workflows/library-integrity.yml](../../.github/workflows/library-integrity.yml)) provides robust, least-privilege verification (`contents: read`). The following plan outlines enhancements for speed, security, and release assurance.

- **Step 1: Increase Job Timeout Buffer:** Increase `timeout-minutes: 5` to `timeout-minutes: 10` in [.github/workflows/library-integrity.yml](../../.github/workflows/library-integrity.yml) (line 20) to prevent spurious job cancellations caused by runner disk latency or Windows self-tests.
- **Step 2: Optimise Subprocess Execution in Preflight Tests:** Refactor [tools/tests/test_workspace_preflight.py](../../tools/tests/test_workspace_preflight.py) to share Git fixtures across tests using `setUpClass()`, reducing overall CI test suite run time from over 5 minutes to under 30 seconds.
- **Step 3: Add Explicit Dependency Caching:** Add GitHub Actions caching for pip dependencies (`actions/setup-python` cache: 'pip') to accelerate runner boot time and reduce external network calls.
- **Step 4: Formalise Automated Npm Security Scanning:** Add an explicit `npm audit` step in [.github/workflows/publish-kanban.yml](../../.github/workflows/publish-kanban.yml) (operating against a newly committed `tools/kanban/package-lock.json`) prior to running `npm publish`.
- **Step 5: Implement Automated Release Tagging:** Automate the creation of release tags (`kanban-v*`) via a release-please or semantic-release workflow when changes in `tools/kanban/` are merged to `main`, eliminating manual owner tagging steps.
- **Step 6: Publish Build Provenance (Attestations):** Configure GitHub Actions artifact attestations for the published `portfolio-kanban-generator` npm package to guarantee supply-chain integrity for enterprise portfolio consumers.

---

[<- Previous: Architecture Assessment](06_ARCHITECTURE_ASSESSMENT.md) | [Back to Index](00_CODE_REVIEW_Antigravity_v1_20261105T0856Z.md)
