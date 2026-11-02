---
version: 1
created: 2026-11-01T11:51Z
project: portfolio-prompts
type: implementation-plan
item: PP-41
status: implemented
approved: "2026-11-01, owner instructed Action 1; implementation, validation and separate records authorised; owner retains merge authority"
delivered: "2026-11-01, locally implemented and validated; publication awaits owner review"
language: en-GB
---

# Implementation plan: PP-41 installed registry and handover-index refresh

**Goal.** Make the installed portfolio-status skill read Credit Dashboard as resting/closed and make the generated handover index select its existing terminal v22. Preserve the closed project's code and historical handovers.

## Evidence gathered before planning

Read-only checks on 1 November 2026 established the following. Before branching, fetch confirmed each local base equals origin/main: library `78cda575c9b42c6cb8783eb719e6e67abd4f59f0`, portfolio support `fb4b0f2c68fa6811debd78ad3d4e7057ceed9c98`.

| Finding | Consequence for the plan |
|---|---|
| Source registry already records Credit Dashboard resting and closed on 23 October; installed 0.7.3 cache says active | Refresh the packaged source through the supported installer; do not hand-edit cache files or rewrite the correct registry |
| Source and installed manifests still share 0.7.3 identity after later registry changes | Assign patch release 0.7.4 with a fresh Codex cachebuster |
| Manifest selects Credit Dashboard v21 despite an existing complete v22 pair | Regenerate with the existing builder; do not create another Credit Dashboard handover |
| `build-handover-manifest.py --check` exits 1 with STALE | Retain this negative baseline, then require a clean check |
| Configured marketplace resolves to the workspace portfolio-prompts checkout | Use `codex plugin add portfolio-prompts@portfolio-prompts --json` after library validation |

## Steps

1. File this plan and add its row to `docs/implementation-plans/_index.md`; copy the shared plan template into `docs/templates/`.
2. Record PP-41 in `docs/backlog.md`, bump `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` to shared release 0.7.4, and generate the ignored root `session-notes/manifest.json` with the existing builder.
3. Run registry and library gates. Install through the supported Codex command and compare source/cache runtime-bearing files by SHA-256, including `registry.yml`; require all 17 project rows to agree and Credit Dashboard to be resting.
4. Append `docs/implementation-logs/2026-11-01_pp-41-installed-registry-refresh.md`. Write portfolio-prompts handover v10 in the root `session-notes/` directory as Markdown and mechanically generated HTML, reusing v9 styling.
5. Rebuild/check the manifest, verify handover content parity and links, and review exact Git diffs. Record the final outcome without rewriting this approved plan body.

## Verification

- Negative baseline: manifest check must reject the pre-refresh stale index (already observed, exit 1).
- Source/cache comparison must reject the old cache's registry; the new cache must match all selected runtime-bearing files and all 17 registry project rows.
- `python -B tools/render-registry.py --check` and `python -B tools/check-library.py` must pass in the library.
- Root manifest builder/check must select Credit Dashboard v22 and portfolio-prompts v10, with complete pairs.
- Markdown/HTML metadata, generated body and local links must agree. `git diff --check` must pass in each affected repository.
- No claim that this already-running chat has reloaded its initial skill catalogue; the new installed files are the acceptance surface. A new chat loads the refreshed catalogue.

## Delivery

Library branch: `codex/pp-41-installed-registry-refresh`. Root records branch: `codex/status-quick-wins-records`, with Action 1 and Action 2 recorded separately. Create reviewable commits and draft PRs after validation; owner authorises each merge. Local installation is authorised by Action 1 and may precede PR merge; record that distinction. No npm package publication or Credit Dashboard development is included.

## Decisions put to the owner

| Decision | Options | Recommended | Owner's answer |
|---|---|---|---|
| Execute the metadata correction | Correct records and installation / leave the mismatch | Correct records and installation | Action 1 authorised, 2026-11-01 |
| Record ownership | Prompt-library maintenance / reopen Credit Dashboard | Prompt-library maintenance, preserving terminal v22 | Routine implementation choice within authorised Action 1 |
| Merge authority | Owner review after implementation / automatic merge | Owner review | No automatic merge authority requested or inferred |

## Outcome

Local implementation complete. Supported installation is 0.7.4+codex.20261101115356; 103/103 checked release-bearing files and all 17 registry rows match source. Credit Dashboard is resting and its existing v22 is selected. Registry and complete library gates passed (library: 39.473 s). Separate log and v10 Markdown/HTML handover are provided. The manifest and generated-pair checks are recorded in the handover. Publication uses the approved library and support branches and awaits owner review; no merge or npm publication is claimed.
