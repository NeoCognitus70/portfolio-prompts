# Prompt — Portfolio status (read-only)

Use this prompt for a current, cross-project view of the test-automation portfolio — or invoke it
without pasting:
`Read and follow portfolio-prompts/portfolio-status.prompt.md`.

It takes no `PROJECT=` because it reports every project in `registry.yml`. It is strictly
**read-only**: it must not write files, change a repository, refresh generated artefacts, or fetch
remote Git state.

---

You are producing a **read-only status report for the whole test-automation portfolio**. The report
must make incomplete or unavailable evidence visible; never turn missing evidence into a healthy
status.

## Step 0 — Preserve the read-only boundary

- Write no files and make no repository changes. Do not regenerate the README registry table or
  handover manifest, create worklists, install dependencies, run tests, commit, push, or open PRs.
- Do not use mutating or state-refreshing Git commands, including `fetch`, `pull`, `checkout`,
  `switch`, `reset`, `clean`, `stash`, or branch creation. Local inspection commands such as
  `git -C <path> status --porcelain`, `branch --show-current`, and `log -1` are allowed.
- Remote inspection through read-only `gh` queries is allowed. If `gh`, authentication, network
  access, or a requested repository is unavailable, record **UNAVAILABLE** for the affected field
  and continue; do not ask the user to repair it before reporting everything else.
- Do not launch sub-agents. This is a lightweight aggregation task and shared mutable working trees
  make parallel Git inspection unnecessary.

## Step 1 — Establish the registered scope

Load `registry.yml` at the resolved library root as the source of truth. Include **every row under
`projects`**, including the `portfolio-prompts` meta project and projects whose status is complete
or product-oriented. Do not use `orchestration_target` as a filter; this is reporting, not a
fan-out workflow.

Resolve paths from the registry defaults plus each row's deviations, as defined in
`project-layout.md` at the resolved library root §"Machine-readable registry". Treat entries under
`unregistered_candidates` as a separate **registry-drift watchlist**, never as registered projects
and never inspect them as though they had a project contract.

Load `session-notes/manifest.json` from the portfolio root and prefer its `latest` entry for each
project. If the manifest is absent, invalid, or stale (a project has a newer handover file on disk
than the version recorded in `manifest.json`), dynamically resolve the latest version using the
authoritative naming rule in `project-layout.md` and compare version numbers numerically. Do not
regenerate the manifest (this prompt is read-only). Note any local manifest staleness as an
informational local cache refresh suggestion (advising running `python portfolio-prompts/tools/build-handover-manifest.py`),
not as a repository or project defect.

## Step 2 — Gather one evidence record per project

For each registry project, gather these fields without changing its checkout:

1. **Registry** — recorded status and whether the registered local folder exists.
2. **Repo** — current branch, abbreviated HEAD, and `clean` or `dirty` from local Git. Report
   `NOT A CHECKOUT` or `MISSING` rather than guessing where local evidence is unavailable.
3. **Backlog** — counts of open HIGH, MEDIUM, and LOW items, plus the total open count. Prefer an
   explicit current risk/status summary in the registered backlog. Otherwise count only
   unambiguous, current item statuses in active sections; exclude historical/resolved records. If
   the document cannot be counted reliably, use `UNKNOWN` and name the ambiguity in the anomaly
   summary.
4. **Handover** — latest version and timestamp, or `NONE`. Flag a manifest entry whose referenced
   file is missing.
5. **Open PRs** — count and numbers from a read-only query such as
   `gh pr list --repo <owner/repo> --state open --json number,title,url,isDraft,headRefName`.
6. **Current default-branch CI** — collect the following evidence read-only. Keep workflow
   inventory, latest runs and historical observations separate; run history alone is not a list
   of current workflows.

   **Inventory and identity**
   - Discover the default branch and its current head SHA. Retrieve the complete, paginated
     workflow inventory, retaining `id`, `name`, `path` and `state`, for example with
     `gh api --paginate 'repos/<owner/repo>/actions/workflows?per_page=100'`.
     Confirm pagination completed successfully; a failed or truncated inventory is unavailable
     evidence, not proof that an omitted workflow was retired.
   - Join runs to inventory by `workflow_id`/`id`, never by display name. Renames must not split
     one workflow, and two workflows with the same name must not overwrite each other.
   - For each inventoried workflow, query its newest run on the discovered default branch,
     for example `gh api 'repos/<owner/repo>/actions/workflows/<id>/runs?branch=<default>&per_page=1'`.
     URL-encode substituted path/query values. Retain workflow ID, status, conclusion, timestamp,
     head SHA, event and URL. Do not rely on a fixed global run list to cover every active workflow:
     it can omit a low-frequency workflow behind many runs of another workflow.
   - Partition inventory into `active` workflows and explicitly inactive workflows (including
     `disabled_manually`, `disabled_inactivity`, `disabled_fork` and `deleted` if returned).
     Report every inactive workflow's exact state and latest known run separately. An inventoried
     workflow is not absent/retired merely because it is disabled. An unrecognised state makes
     the current classification `UNAVAILABLE`; retain the raw state for investigation.

   **Aggregate current CI in this order**
   1. `UNAVAILABLE` if inventory is incomplete/unqueryable, a workflow state cannot be classified,
      an inventoried workflow's latest-run query fails, or required identity/status fields are
      missing or malformed. Keep any known active failure visible
      in Attention needed even when the aggregate is unavailable. Failure of an optional history
      query does not invalidate otherwise complete current evidence; mark that history unavailable.
   2. `RED` if any active workflow's latest run concluded `failure`, `timed_out` or `action_required`.
   3. `RUNNING` if any active workflow's latest run has status `queued`, `requested`, `waiting`,
      `pending` or `in_progress` and none is red. An unknown run status is unavailable evidence,
      not proof that a run is in progress.
   4. `NO RUNS` if there are no active workflows, or at least one active workflow has no run from a
      successful query. Name the missing coverage; known RED/RUNNING takes precedence, but the
      missing coverage still appears in Attention needed.
   5. `MIXED` if any remaining active latest run has a conclusion other than `success`, including
      cancelled, skipped, neutral, stale, missing or unrecognised conclusions. Never round these
      up to GREEN, even when every workflow has the same non-success conclusion.
   6. `GREEN` only when at least one active workflow exists and every active workflow's latest run
      completed successfully. Inactive workflow results do not contribute to this current colour.

   **History and freshness**
   - Inspect a bounded default-branch history window, for example the newest 100 runs from
     `gh api 'repos/<owner/repo>/actions/runs?branch=<default>&per_page=100'`. State the retrieved
     count and oldest/newest observed timestamps; if history is limited or unavailable, say so.
     Do not claim an exhaustive historical audit. This window supplements per-workflow discovery.
   - Only after a complete successful inventory, classify runs whose workflow IDs are absent
     from it as historical runs of absent/retired workflows. Keep the newest observed run per
     absent ID, with its name, conclusion, date and link, outside current CI totals. Say "absent
     from the current inventory"; the API observation does not establish why it was removed.
   - Historical failures must remain visible in a historical-workflow note; do not delete,
     rerun or change them. A history-only failure must not increment the current RED count.
   - Retain evidence dates and SHAs. If a selected run predates or differs from the observed
     default-branch head, explicitly state that it does not establish exact-head coverage.
     Failure to query the head SHA leaves freshness unverified; never invent a match. A workflow's
     latest successful run can still be GREEN as observed-run status, with that limitation shown.

   Review examples: [CI classification scenarios](docs/portfolio-status-ci-scenarios.md).

Keep the evidence timestamp in the report. Local and remote state can change after it is observed.

## Step 3 — Report, do not remediate

Return one compact Markdown table in registry order with these columns:

| Project | Registry | Repo | Open backlog (H/M/L) | Latest handover | Open PRs | Current CI |
|---|---|---|---|---|---|---|

Use short cells, but retain links for PRs or failing/running workflow evidence when available.
After the table, include:

- **Portfolio totals** — registered projects; missing/non-checkout/dirty repositories; open HIGH,
  MEDIUM, LOW, and total backlog items where known; open PR count; and **current CI** colour counts
  (one aggregate per registered project; absent/retired workflow runs are excluded).
- **Attention needed** — every `RED`, `RUNNING`, `MIXED`, `UNAVAILABLE`, dirty checkout, missing
  handover, unreliable backlog count, registry mismatch, or open HIGH/MEDIUM item. Also list disabled
  or otherwise inactive workflows, missing run coverage, known active failures obscured by an
  UNAVAILABLE aggregate, and run/head freshness limitations. A GREEN current colour does not remove
  those notes. Say `None` only when the evidence genuinely supports it.
- **Historical workflows** — absent/retired workflow observations, including failure links and
  dates, kept separate from current attention and totals. State the inspected history windows and
  any unavailable history or uncertain retirement classification. Say `None observed within the
  inspected windows` only when supported; never imply that all historical runs were audited.
- **Registry-drift watchlist** — repeat `unregistered_candidates` exactly as candidates, or `None`.
- **Read-only confirmation** — state that no files or repositories were changed and no remote Git
  state was refreshed.

Do not recommend or start remediation unless the user separately asks for it. Use en-GB spelling.
