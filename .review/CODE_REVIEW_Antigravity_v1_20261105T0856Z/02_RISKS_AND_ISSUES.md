# Risks and Issues

[<- Back to Index](00_CODE_REVIEW_Antigravity_v1_20261105T0856Z.md) | [Next: Project Reviews ->](03_PROJECT_REVIEWS/PROJECT_001_PORTFOLIO_PROMPTS.md)

**Reviewer:** AI assistant (Antigravity)
**Date:** 2026-11-05T08:56Z
**Scope:** `portfolio-prompts` Risks and Issues Log

This register documents prioritised technical risks, architectural gaps, and maintainability concerns discovered during the code review of the `portfolio-prompts` repository. Findings are ordered from highest to lowest severity.

---

### Risk 1: Subprocess Process Spawning Latency on Windows in Preflight Unit Tests

- **Priority:** MEDIUM
- **Category:** Test Performance & CI Stability
- **Risk Description / Explanation:**
  The unit test suite for the workspace preflight inspector in [tools/tests/test_workspace_preflight.py](../../tools/tests/test_workspace_preflight.py) creates a new temporary directory and initialises six discrete, fully configured Git repositories (`clean`, `dirty`, `behind`, `topic`, `missing-backlog`, `missing-handover`) inside `setUp()` for every single test method. In each setup cycle, over 40 distinct `git` subcommands are executed sequentially via `subprocess.run()`. On Windows operating systems, where process spawning overhead is substantially higher than on POSIX environments (approximately 100-200ms per child process invocation), executing the 4 tests in `WorkspacePreflightTests` consumes over 300 seconds (5 minutes). Because [tools/check-library.py](../../tools/check-library.py) (lines 627-646) executes `unittest discover -s tools/tests` as an internal check, running the library self-gate locally on Windows takes over 5.3 minutes. This latency is perilously close to GitHub Actions job timeouts and discourages engineers or local agents from running the full gate prior to pushing.

- **Evidence Outline:**
  In [tools/tests/test_workspace_preflight.py](../../tools/tests/test_workspace_preflight.py) (lines 22-35):
  ```python
  class WorkspacePreflightTests(unittest.TestCase):
      def setUp(self) -> None:
          self._temp = tempfile.TemporaryDirectory()
          self.workspace = Path(self._temp.name)
          self.session_notes = self.workspace / "session-notes"
          self.session_notes.mkdir()
          self.projects: dict[str, Path] = {}

          self._make_project("clean", handover="fresh")
          self._make_project("dirty", handover="fresh", dirty=True)
          self._make_project("behind", handover="stale", behind=True)
          self._make_project("topic", handover="fresh", topic=True)
          self._make_project("missing-backlog", handover="fresh", backlog=False)
          self._make_project("missing-handover", handover=None)
  ```
  And in [.github/workflows/library-integrity.yml](../../.github/workflows/library-integrity.yml) (line 20):
  ```yaml
  jobs:
    verify:
      name: check-library
      runs-on: ubuntu-latest
      timeout-minutes: 5
  ```

- **Impact Analysis:**
  - Local verification on Windows developer machines takes upwards of 320 seconds, causing agents and contributors to skip running the gate or abort prematurely.
  - If additional tests are added without restructuring fixtures, the total execution time will exceed the 5-minute timeout configured in `library-integrity.yml`, resulting in spurious build cancellations.
  - Excessive disk I/O and temporary directory thrashing increases the likelihood of transient Windows NTFS file handle locking errors during `tearDown()`.

- **Refactor Recommendation and Strategy:**
  1. Migrate repository fixture creation from per-method `setUp()` to class-level `setUpClass()`. The fixture repositories are inspected in read-only mode by `workspace_preflight.py` and can be safely shared across test methods without state pollution.
  2. Implement an in-memory or shallow repository mock for pure command-parsing tests (`test_git_command_allowlist_rejects_mutation` and `test_cli_exit_codes_distinguish_ready_blocked_and_invalid`), reserving real Git subprocesses only for the matrix integration test.
  3. Increase the CI timeout in [.github/workflows/library-integrity.yml](../../.github/workflows/library-integrity.yml) to 10 minutes as an interim safety buffer.

---

### Risk 2: `build-portfolio-reviews.py` Lacks Read-Only `--check` Mode and Unconditionally Mutates Workspace State

- **Priority:** MEDIUM
- **Category:** Tooling Consistency & Gate Discipline
- **Risk Description / Explanation:**
  The portfolio maintenance suite establishes a strict contract across [tools/render-registry.py](../../tools/render-registry.py), [tools/build-handover-manifest.py](../../tools/build-handover-manifest.py), and [tools/kanban/generate-kanban.mjs](../../tools/kanban/generate-kanban.mjs): every generation tool must support a non-mutating `--check` flag that exits with code 0 if files are in sync and non-zero if drift is detected, without altering working tree state. However, [tools/build-portfolio-reviews.py](../../tools/build-portfolio-reviews.py) does not parse CLI arguments. When invoked with `--check` (e.g. by an automated audit or an agent probing capabilities), it disregards the argument and unconditionally regenerates and overwrites `portfolio-reviews/README.md`, `portfolio-reviews/index.html`, and `portfolio-landing/reviews.html`. Additionally, this script is not wired into [tools/check-library.py](../../tools/check-library.py), allowing review summary drift to accumulate unnoticed.

- **Evidence Outline:**
  In [tools/build-portfolio-reviews.py](../../tools/build-portfolio-reviews.py) (lines 9-11 and 445-455):
  ```python
  # Usage documentation mentions no arguments:
  # Usage:
  #     python tools/build-portfolio-reviews.py

  def main():
      print("build-portfolio-reviews: scanning for code review bundles...")
      data = discover_reviews()
      md_content = render_markdown(data)
      html_content = render_html(data)
      write_file(OUTPUT_MD, md_content)
      write_file(OUTPUT_HTML, html_content)
      ...
  ```
  Contrast with [tools/render-registry.py](../../tools/render-registry.py) (lines 142-153), where `--check` is honoured:
  ```python
  if "--check" in sys.argv:
      if updated == existing:
          print("render-registry: README table already up to date.")
          return 0
      print("render-registry: README table is STALE...")
      return 1
  ```

- **Impact Analysis:**
  - Running audits or verification commands can unintentionally dirty git working trees across sibling directories (`portfolio-reviews/` and `portfolio-landing/`), violating read-only inspection boundaries.
  - Review summary files can drift out of sync with new code review bundles without being caught by CI, as `build-portfolio-reviews.py` is entirely absent from the `check-library.py` self-gate.

- **Refactor Recommendation and Strategy:**
  1. Add standard CLI argument parsing to [tools/build-portfolio-reviews.py](../../tools/build-portfolio-reviews.py) supporting `--check` and `--write` (or defaulting to stdout/check).
  2. In `--check` mode, compare generated content against existing disk files and return exit code 1 if discrepancies exist.
  3. Wire `check_portfolio_reviews_generated(fails)` into [tools/check-library.py](../../tools/check-library.py), matching the behaviour of `check_readme_generated`.

---

### Risk 3: Undeclared and Ungated Third-Party Dependency (`markdown`) in Pedagogical Reports Generator

- **Priority:** LOW
- **Category:** Dependency Management & Environment Portability
- **Risk Description / Explanation:**
  The script [tools/generate_sut_pedagogical_reports_html.py](../../tools/generate_sut_pedagogical_reports_html.py) (lines 26-29) unconditionally attempts to `import markdown` and terminates execution if the module is missing (`pip install markdown`). However, neither the repository root nor `tools/` contains a `requirements.txt` or `pyproject.toml` declaring this dependency. Furthermore, [.github/workflows/library-integrity.yml](../../.github/workflows/library-integrity.yml) (line 34) only installs `PyYAML==6.0.3`. While `generate_sut_pedagogical_reports_html.py` is not currently executed in CI, any automated workflow or fresh environment attempting to execute this generator will fail immediately unless an undocumented manual installation step is performed.

- **Evidence Outline:**
  In [tools/generate_sut_pedagogical_reports_html.py](../../tools/generate_sut_pedagogical_reports_html.py) (lines 26-29):
  ```python
  try:
      import markdown
  except ImportError:
      sys.exit("generate_sut_pedagogical_reports_html.py requires 'markdown' (pip install markdown)")
  ```
  In [.github/workflows/library-integrity.yml](../../.github/workflows/library-integrity.yml) (line 34):
  ```yaml
  - name: Install gate dependency
    run: python -m pip install --disable-pip-version-check PyYAML==6.0.3
  ```

- **Impact Analysis:**
  - Inconsistent developer setup: new contributors or automated environments without pre-existing global Python site-packages experience immediate build failure.
  - Unpinned third-party dependencies expose HTML generation to rendering drift or breaking changes if differing versions of the `markdown` package are installed across machines.

- **Refactor Recommendation and Strategy:**
  1. Formalise a pinned dependency manifest (e.g. `requirements-dev.txt` or a minimal `pyproject.toml`) specifying `PyYAML==6.0.3` and `markdown>=3.6.0`.
  2. Alternatively, evaluate using standard Node.js rendering via `marked` (which is already declared in [package.json](../../package.json) line 10) to align presentation rendering across the portfolio without introducing additional Python dependencies.

---

### Risk 4: Missing Lockfile in `tools/kanban` Impedes Standard `npm audit` Vulnerability Scanning

- **Priority:** LOW
- **Category:** Dependency Scanning & Security Hygiene
- **Risk Description / Explanation:**
  The per-project Kanban generator package in [tools/kanban/](../../tools/kanban/) defines `package.json` with zero `dependencies` and zero `devDependencies` (using native `node --test`). However, it contains no committed `package-lock.json`. When standard compliance tools or security scanners run `npm audit` inside `tools/kanban/`, npm aborts with an error:
  `npm error code ENOLOCK: This command requires an existing lockfile. Try creating one first with: npm i --package-lock-only`.
  While the package is genuinely dependency-free, automated security pipelines that enforce `npm audit` across all `package.json` locations report this as a scanning failure.

- **Evidence Outline:**
  Executing `npm audit` in `portfolio-prompts/tools/kanban`:
  ```text
  npm error code ENOLOCK
  npm error audit This command requires an existing lockfile.
  npm error audit Try creating one first with: npm i --package-lock-only
  ```
  In [tools/kanban/package.json](../../tools/kanban/package.json) (lines 1-51): zero dependencies are listed.

- **Impact Analysis:**
  - Automated security scanners and corporate CI gates fail or require custom exception rules to bypass `tools/kanban`.
  - Misleading signal for auditors reviewing portfolio security compliance.

- **Refactor Recommendation and Strategy:**
  1. Run `npm i --package-lock-only` in `tools/kanban` and commit the generated `package-lock.json` (locking lockfileVersion 3 with empty dependencies mapping).
  2. Document in [tools/kanban/README.md](../../tools/kanban/README.md) that `tools/kanban` is intentionally zero-dependency and that the lockfile exists solely to satisfy automated security audit scanners.

---

### Risk 5: Test Coverage Gaps Across Ancillary Report Generator Scripts

- **Priority:** LOW
- **Category:** Test Architecture & Verification Gaps
- **Risk Description / Explanation:**
  The automated testing strategy in [tools/tests/](../../tools/tests/) covers `workspace_preflight.py`, `docker_inventory.py`, `kanban`, `handover_manifest.py`, `prompt_skill_coverage`, `registry_semantics`, and `release_metadata`. However, several substantial Python scripts in `tools/` have zero unit test coverage:
  - [tools/generate_in_depth_reports_index.py](../../tools/generate_in_depth_reports_index.py) (1,132 lines)
  - [tools/generate_sut_pedagogical_reports_html.py](../../tools/generate_sut_pedagogical_reports_html.py) (823 lines)
  - [tools/build-portfolio-reviews.py](../../tools/build-portfolio-reviews.py) (462 lines)
  - [tools/render-registry.py](../../tools/render-registry.py) (162 lines; tested only via black-box `--check` invocation)
  Together, these four scripts comprise over 2,500 lines of un-unittested Python code managing string slicing, regex parsing, and HTML document assembly.

- **Evidence Outline:**
  Listing `tools/tests/test_*.py` files shows coverage only for seven areas:
  - `test_docker_inventory.py`
  - `test_handover_manifest.py`
  - `test_kanban_generator.py`
  - `test_prompt_skill_coverage.py`
  - `test_registry_semantics.py`
  - `test_release_metadata.py`
  - `test_workspace_preflight.py`
  No tests exist for `test_build_portfolio_reviews.py`, `test_render_registry.py`, or the pedagogical report generators.

- **Impact Analysis:**
  - Logic regressions in regex parsing (e.g. timestamp or reviewer extraction in `build-portfolio-reviews.py` lines 29-50) can silently corrupt generated index files without failing the CI pipeline.
  - Changes to `presentation.json` or HTML structure in child repositories can trigger uncaught runtime exceptions during report index building.

- **Refactor Recommendation and Strategy:**
  1. Add lightweight unit test modules in `tools/tests/` using sample string fixtures to verify parsing and rendering behaviour for `build-portfolio-reviews.py` and `render-registry.py`.
  2. Include end-to-end fixture snapshot tests verifying that generated HTML structures match expected schemas.

---

[<- Previous: Executive Summary](01_EXECUTIVE_SUMMARY.md) | [Back to Index](00_CODE_REVIEW_Antigravity_v1_20261105T0856Z.md) | [Next: Project Reviews ->](03_PROJECT_REVIEWS/PROJECT_001_PORTFOLIO_PROMPTS.md)
