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

Load `portfolio-prompts/registry.yml` as the source of truth. Include **every row under
`projects`**, including the `portfolio-prompts` meta project and projects whose status is complete
or product-oriented. Do not use `orchestration_target` as a filter; this is reporting, not a
fan-out workflow.

Resolve paths from the registry defaults plus each row's deviations, as defined in
`portfolio-prompts/project-layout.md` §"Machine-readable registry". Treat entries under
`unregistered_candidates` as a separate **registry-drift watchlist**, never as registered projects
and never inspect them as though they had a project contract.

Load `session-notes/manifest.json` from the portfolio root and prefer its `latest` entry for each
project. If the manifest is absent or invalid, find matching handovers using the naming rule in
`project-layout.md` and compare version numbers numerically. Do not regenerate the manifest.

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
6. **Default-branch CI** — discover the default branch read-only, then inspect recent workflow runs
   with a query such as
   `gh run list --repo <owner/repo> --branch <default> --json workflowName,status,conclusion,createdAt,url`.
   Select the newest run per workflow and report:
   - `GREEN` only when every latest workflow run completed successfully;
   - `RED` when any latest workflow run failed, timed out, or needs action;
   - `RUNNING` when at least one latest run is queued/in progress and none is red;
   - `MIXED` for other disagreeing or non-success conclusions;
   - `NO RUNS` when the query succeeds but returns no workflow runs; or
   - `UNAVAILABLE` when it cannot be queried.

Keep the evidence timestamp in the report. Local and remote state can change after it is observed.

## Step 3 — Report, do not remediate

Return one compact Markdown table in registry order with these columns:

| Project | Registry | Repo | Open backlog (H/M/L) | Latest handover | Open PRs | CI |
|---|---|---|---|---|---|---|

Use short cells, but retain links for PRs or failing/running workflow evidence when available.
After the table, include:

- **Portfolio totals** — registered projects; missing/non-checkout/dirty repositories; open HIGH,
  MEDIUM, LOW, and total backlog items where known; open PR count; and CI colour counts.
- **Attention needed** — every `RED`, `RUNNING`, `MIXED`, `UNAVAILABLE`, dirty checkout, missing
  handover, unreliable backlog count, registry mismatch, or open HIGH/MEDIUM item. Say `None` only
  when the evidence genuinely supports it.
- **Registry-drift watchlist** — repeat `unregistered_candidates` exactly as candidates, or `None`.
- **Read-only confirmation** — state that no files or repositories were changed and no remote Git
  state was refreshed.

Do not recommend or start remediation unless the user separately asks for it. Use en-GB spelling.
