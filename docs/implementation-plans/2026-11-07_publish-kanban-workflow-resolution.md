---
version: 1
created: 2026-11-07T17:30Z
project: portfolio-prompts
type: implementation-plan
item: publish-kanban-generator CI coverage
status: proposed
approved: "pending owner approval"
delivered: not yet
language: en-GB
---

# Implementation plan: resolve Publish kanban generator workflow CI classification

**Goal.** Eliminate the `NO RUNS` aggregate CI status for `portfolio-prompts` caused by active workflow ID `352366703` (`Publish kanban generator`) having zero default-branch runs, bringing `portfolio-prompts` to `GREEN` while maintaining continuous verification of the `tools/kanban` npm package.

## Evidence gathered before planning

A read-only investigation was conducted across GitHub Actions workflows, `portfolio-status.prompt.md`, `tools/kanban/README.md`, and recent backlog and acceptance records:

| Item | Evidence | Consequence |
|---|---|---|
| Complete workflow inventory | Querying `repos/NeoCognitus70/portfolio-prompts/actions/workflows` returns 2 workflows: ID `313043196` (`Prompt library integrity`, path `.github/workflows/library-integrity.yml`, state `active`) and ID `352366703` (`Publish kanban generator`, path `.github/workflows/publish-kanban.yml`, state `active`). | Both workflows are active members of current CI inventory. |
| Workflow triggers | `publish-kanban.yml` triggers strictly on `push: tags: ['kanban-v*']`. There is no `push: branches: [main]`, no `pull_request`, and no `workflow_dispatch`. | Runs only execute against tag refs (`refs/tags/kanban-v*`), never on default branch `main`. |
| Run history on `main` | `gh api 'repos/NeoCognitus70/portfolio-prompts/actions/workflows/352366703/runs?branch=main&per_page=1'` returns `total_count: 0, workflow_runs: []`. | The workflow has zero runs on branch `main`. |
| Historical tag runs | Workflow `352366703` has 3 successful runs on tags: `kanban-v1.0.0` (run 34133329872), `kanban-v1.1.0` (run 34292508726), and `kanban-v1.2.0` (run 34520241847). | The workflow is functional and tested, but tag runs are ref-isolated and do not count as default-branch execution. |
| Portfolio status classification | `portfolio-status.prompt.md` Step 2 Rule 4 mandates: `NO RUNS if there are no active workflows, or at least one active workflow has no run from a successful query. Name the missing coverage`. | Because workflow `352366703` is active with 0 runs on `main`, `portfolio-prompts` aggregates to `NO RUNS` despite `library-integrity.yml` passing on `main` (`c97b853`). |
| PP-42 acceptance context | `docs/acceptance/2026-11-02_pp-42-post-merge.md` explicitly noted: `Portfolio prompts: exact-merge integrity CI passed, but active Publish kanban generator has no default-branch run; aggregate NO RUNS. The report does not reinterpret tag-oriented release activity as main-branch execution.` | The reporting prompt intentionally and conservatively refuses to treat tag pushes as default-branch CI coverage. |

## Evaluation of options

### Option 1 (Recommended): Add default-branch check and packaging dry-run to `publish-kanban.yml`

* **Mechanism**:
  Update `publish-kanban.yml` to trigger on `push: branches: [main]`, `push: tags: ['kanban-v*']`, and `workflow_dispatch`.
  When running on `main` (or dispatch), execute Node 20 setup, `node --test`, and `npm pack --dry-run`.
  Only execute tag-matching assertion and `npm publish --access public` when `startsWith(github.ref, 'refs/tags/kanban-v')`.
* **Pros**:
  1. Provides continuous automated verification that `tools/kanban/` passes its unit tests and packages cleanly into an npm tarball on every push to `main`.
  2. Generates genuine, green default-branch runs for workflow `352366703`.
  3. Transitions `portfolio-prompts` aggregate CI to `GREEN` without requiring any changes to portfolio status rules or prompt specifications.
  4. Requires zero out-of-band operational intervention (no disabling/enabling cycles on GitHub).
  5. Safe: publishing is strictly gated behind the `kanban-v*` tag check and secret availability.
* **Cons**:
  Requires modifying `.github/workflows/publish-kanban.yml`, submitting a PR, and merging to `main`.

### Option 2: Manually disable workflow via GitHub API (`disabled_manually`)

* **Mechanism**:
  Execute `gh workflow disable 352366703 -R NeoCognitus70/portfolio-prompts`.
* **Pros**:
  1. No code edits required.
  2. Under `portfolio-status.prompt.md` Step 2 Rule 6, inactive workflows (`disabled_manually`) do not contribute to the current CI aggregate, allowing `portfolio-prompts` to aggregate to `GREEN` immediately based solely on `library-integrity.yml`.
* **Cons**:
  1. Introduces operational friction: maintainers must remember to run `gh workflow enable` before cutting any release tag `kanban-v*`, otherwise GitHub Actions will ignore the tag push.
  2. The workflow remains flagged in "Attention needed" as an inactive workflow (`disabled_manually`).
  3. Does not provide continuous validation of `tools/kanban` package bundling on `main`.

### Option 3: Refine `portfolio-status.prompt.md` aggregation rules for release workflows

* **Mechanism**:
  Change `portfolio-status.prompt.md` to exempt release/publishing workflows from default-branch run requirements, or evaluate their latest tag runs.
* **Pros**:
  Addresses the issue at the classifier level for all projects with tag-only release workflows (e.g. `hand-baked-screenplay-pattern`).
* **Cons**:
  1. High scope and risk: PP-42 was just accepted and closed on 2026-11-03.
  2. Requires bumping prompt library versions, re-running scenario acceptance suites, updating documentation, and reinstalling plugin caches across agent environments.
  3. Distinguishing release workflows reliably from core CI purely via GitHub API metadata is ambiguous and fragile.

## Recommended implementation steps (Option 1)

1. **Branch creation**:
   Create a dedicated branch `codex/publish-kanban-main-check-20261107` from clean `main`.

2. **Workflow adjustment (`.github/workflows/publish-kanban.yml`)**:
   Add `push: branches: [main]` and `workflow_dispatch` to triggers:
   ```yaml
   on:
     push:
       branches:
         - main
       tags:
         - "kanban-v*"
     workflow_dispatch:
   ```
   Add a job name reflecting action mode:
   ```yaml
   jobs:
     publish:
       name: ${{ startsWith(github.ref, 'refs/tags/kanban-v') && 'publish to npm' || 'verify package' }}
       runs-on: ubuntu-latest
       timeout-minutes: 5
       defaults:
         run:
           working-directory: tools/kanban
   ```
   Gate the tag version match and publish steps behind the tag condition:
   ```yaml
       - name: Verify tag matches package version
         if: startsWith(github.ref, 'refs/tags/kanban-v')
         run: |
           pkg_version="$(node -p "require('./package.json').version")"
           tag_version="${GITHUB_REF_NAME#kanban-v}"
           echo "package.json: $pkg_version   tag: $tag_version"
           if [ "$pkg_version" != "$tag_version" ]; then
             echo "::error::tag $GITHUB_REF_NAME does not match package.json version $pkg_version"
             exit 1
           fi

       - name: Run generator test suite
         run: node --test

       - name: Verify npm packaging (dry run)
         run: npm pack --dry-run

       - name: Publish (public)
         if: startsWith(github.ref, 'refs/tags/kanban-v')
         run: npm publish --access public
         env:
           NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
   ```

3. **Local validation**:
   - Run `cd tools/kanban && node --test` (49 tests pass).
   - Run `cd tools/kanban && npm pack --dry-run` to verify packaging output.
   - Run `python -B tools/check-library.py` to ensure self-gate passes.

4. **PR and merge**:
   - Commit changes, push branch, and open PR for owner review.
   - Upon owner merge to `main`, GitHub Actions will trigger both `library-integrity.yml` and `publish-kanban.yml` on `main`.

5. **Post-merge verification**:
   - Query `gh api 'repos/NeoCognitus70/portfolio-prompts/actions/workflows/352366703/runs?branch=main&per_page=1'`.
   - Verify that `total_count >= 1`, status is `completed`, and conclusion is `success`.
   - Verify that running portfolio status reports `portfolio-prompts` as `GREEN` with no missing workflow coverage in Attention needed.

## Verification

| Check | Tool / Command | Acceptance criteria |
|---|---|---|
| Local test suite | `cd tools/kanban && node --test` | 49 passing tests, 0 failures |
| Package dry-run | `cd tools/kanban && npm pack --dry-run` | Tarball contains only intended 8 distribution files; 0 errors |
| Library self-gate | `python -B tools/check-library.py` | All library integrity checks pass |
| Default-branch workflow run | `gh api 'repos/NeoCognitus70/portfolio-prompts/actions/workflows/352366703/runs?branch=main&per_page=1'` | Returns run with `conclusion: "success"`, matching main HEAD SHA |
| Portfolio status classification | Portfolio status prompt / query | `portfolio-prompts` current CI evaluates to `GREEN` |

## Decisions put to the owner

| Decision | Options | Recommended |
|---|---|---|
| Resolution strategy | Option 1 (dry-run on main) / Option 2 (disable manually) / Option 3 (prompt rule change) | **Option 1**: adds continuous package verification and resolves NO RUNS cleanly without manual operational overhead |
| Branch creation and execution | Proceed with implementation branch upon approval / Defer | Proceed upon approval |
