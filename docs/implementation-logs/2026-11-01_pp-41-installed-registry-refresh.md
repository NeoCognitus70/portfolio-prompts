# PP-41: installed registry and handover-index refresh — 2026-11-01

## Session Summary

Action 1 corrects the installed portfolio status metadata and generated handover index. The supported installer now provides `0.7.4+codex.20261101115356`, whose 17 registry rows and 103 checked release-bearing files match the workspace source. Credit Dashboard remains resting/closed, and its existing terminal v22 is selected without changing that project. Local implementation is complete; repository publication remains subject to owner review.

## Objectives

1. Complete — identify the source/cache mismatch and refresh through the supported installer.
2. Complete — regenerate the ignored manifest and preserve Credit Dashboard v22.
3. Complete — provide a separate approved plan, implementation log and portfolio-prompts v10 handover pair.
4. Deferred to owner review — merge the library and portfolio support branches; no npm package publication is included.

## Test Results

| Check | Before | After | Result |
|---|---|---|---|
| Installed registry | 0.7.3 says Credit Dashboard active; registry SHA differs from source | 17/17 rows equal; Credit Dashboard resting | PASS |
| Release-bearing file comparison | Old registry mismatch established | 103/103 files byte-identical, zero missing or different | PASS |
| Manifest drift check | Exit 1, STALE; Credit Dashboard v21 selected | Regenerated index selects existing v22 | PASS |
| Registry renderer `--check` | Not rerun before changes | Exit 0 | PASS |
| Library gate | First authoring pass rejected the PP-41 heading/count mismatch | Corrected the heading; complete gate exit 0 in 39.473 s | PASS |

The first authoring failure was caused by using a resolved-item heading level in the outstanding section. Correcting `####` to the required `###` made the item count visible to the existing validator; no validator was weakened. Final record/pair checks are captured in handover v10.

Observed installer result:

```json
{"pluginId":"portfolio-prompts@portfolio-prompts","version":"0.7.4+codex.20261101115356","authPolicy":"ON_INSTALL"}
```

The old installed registry SHA-256 was `45de552dcf26784afebc5d3b893647f845e8b6ad2ab1ebfd99e6a3cda3e2cd58`; the source and refreshed registry both hash to `938e6dd4d6d656d88ac316409dce2e108d621caa9517ebee6d43076893f3082b`. The 103-file comparison covers tracked prompt, skill, tool, registry, layout, README and plugin-manifest files. It is not a claim that the already-running chat reloaded its initial catalogue.


Close-out resumed on **2026-11-02**. Fetched main and the implementation base remained unchanged. Markdown/HTML metadata and generated bodies, all eight handover sections, preserved CSS, local links and latest-manifest selections passed; the manifest contains 127 handovers across 19 subjects with complete pairs. The final registry/library gate passed in 57.039 s. Codex subsequently supplied an updated skill catalogue rooted at the installed 0.7.4 path; this confirms the catalogue path refresh, without claiming a new independent agent execution.

## Changes Implemented

### Release and installation identity

`.claude-plugin/plugin.json` now identifies 0.7.4; `.codex-plugin/plugin.json` identifies `0.7.4+codex.20261101115356`. `codex plugin add portfolio-prompts@portfolio-prompts --json` installed the configured local marketplace source into the versioned Codex cache. Source registry contents were already correct and were preserved. Installed cache files were not hand-edited.

### Handover discovery

The existing builder regenerated root `session-notes/manifest.json`. This generated file remains ignored. Credit Dashboard v22 is preserved; the maintenance handover belongs to portfolio-prompts as v10. A source/cache mismatch and stale manifest were separate defects and were verified separately.

## Technical Decisions

| Decision | Rationale | Alternative considered |
|---|---|---|
| Assign a fresh patch release identity | Later source changes shared the old installed version identity | Reuse the stale cache identity |
| Use the supported installer | It owns cache creation and installed state | Edit cached registry files manually |
| Record maintenance against portfolio-prompts | Credit Dashboard is closed and needs no new development handover | Reopen Credit Dashboard |
| Separate local completion from publication | The owner authorised local execution but retains merge authority | Describe an unmerged branch as published |

These apply existing working norms; no new architecture decision is introduced. Library base: `78cda575c9b42c6cb8783eb719e6e67abd4f59f0`; support base: `fb4b0f2c68fa6811debd78ad3d4e7057ceed9c98`. Final source commit and review links are recorded in v10.

## Documentation Updates

- `docs/backlog.md` v31 — PP-41 closure and explicit publication boundary.
- `docs/templates/implementation-plan.template.md` — copy of the shared planning template.
- `docs/implementation-plans/2026-11-01_pp-41-installed-registry-refresh.md` and `_index.md` — approved plan and measured outcome.
- This append-only implementation log.
- Portfolio root `session-notes/portfolio-prompts_session-notes_v10_20261101T1158Z.md` and `.html` — separate maintenance handover.
- Root `session-notes/manifest.json` — regenerated local index, deliberately untracked.

## Lessons Learned

- Correct source metadata does not establish that a previously installed plugin reads it. Compare the installed files and version explicitly.
- Check generated handover discovery separately from the existence of a complete handover pair.
- A validator can expose a documentation heading error; repair the document and rerun the unchanged gate.

## Recommendations / Next Steps

- Owner: review the PP-41 library branch and corresponding root records PR before merging.
- After merge, fetch and reconcile the working copies, then rerun the supported installation if the merged release-bearing source differs.
- Start a new chat to load the refreshed catalogue; do not infer an in-place catalogue reload from cache parity.

*Session logged: 2026-11-01; close-out: 2026-11-02. Author: Codex.*
