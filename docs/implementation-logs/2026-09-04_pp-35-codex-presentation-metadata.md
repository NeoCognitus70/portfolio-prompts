# PP-35 Codex Presentation Metadata — 2026-09-04

## Session Summary

Diagnosed the Codex start-up warnings attributed to the installed portfolio-prompts plugin and implemented the repository-owned correction. The plugin supplied four `interface.defaultPrompt` entries while Codex accepts a maximum of three. The list now retains three broad entry routes, the constraint is enforced by the library self-check, and the patch release metadata is set to 0.4.1. The two icon warnings were independently attributed to the bundled spreadsheets plugin and are outside this repository. Merge, reinstall, and final fresh-process verification remain the closure gate for PP-35.

## Objectives

- [x] Reproduce the warnings in a fresh Codex process.
- [x] Attribute each warning through controlled one-process plugin isolation.
- [x] Reduce `interface.defaultPrompt` to the supported maximum without removing any skill.
- [x] Add a regression check and focused tests for the runtime constraint.
- [x] Prepare patch release 0.4.1 with a fresh Codex cachebuster.
- [ ] Merge, reinstall, and verify the installed release in a fresh Codex process.

## Tests Run

| Test | Result | Evidence |
|---|---|---|
| Release metadata unit tests | PASS | Increased from 7 to 9 tests; both new maximum-three cases pass. |
| Full library self-check | PASS | `python -B tools/check-library.py` passed with the new Codex prompt-count constraint. |
| Plugin package validator | PASS | `validate_plugin.py` accepted version `0.4.1+codex.20260903212342`. |
| Fresh-process warning baseline | PASS | Session `01a06924-176b-7b50-96f7-a7e98d428562` reproduced the portfolio default-prompt warning and two icon warnings. |
| Disable bundled spreadsheets plugin | PASS | Session `01a06926-2372-7dc0-b604-c8e35c265a94` removed both icon warnings while retaining the portfolio default-prompt warning. |
| Disable portfolio-prompts plugin | PASS | Session `01a06926-4f91-73e0-9255-824b0366975a` removed the default-prompt warning while retaining both icon warnings. |

## Changes Made

### Plugin manifests

- Updated the Claude plugin release version from 0.4.0 to 0.4.1.
- Updated the Codex plugin release using the plugin-creator cachebuster helper, producing `0.4.1+codex.20260903212342`.
- Removed the specialised in-depth-report suggestion from `interface.defaultPrompt` while leaving the `write-project-in-depth-report` skill installed and directly callable.
- Retained the three broad suggested entry routes: portfolio status, session resume, and external repository analysis.

### Validation and regression coverage

- Added `validate_codex_default_prompts` to reject missing, empty, invalid, or more-than-three suggested prompts.
- Added focused tests demonstrating that three suggestions pass and four fail with the Codex maximum-three message.
- Updated the self-check description to document the runtime constraint.

### Planning records

- Advanced the backlog to version 22.
- Recorded the diagnosis, implementation boundary, completed criteria, and remaining post-merge verification for PP-35.

## Warning Attribution

The repository owns only the warning that `interface.defaultPrompt` exceeds the maximum of three entries. The two icon warnings are emitted by `spreadsheets@openai-primary-runtime`, specifically `skills/excel-live-control/agents/openai.yaml`. Its `../spreadsheets/assets/file-spreadsheet.png` references resolve beneath the skill directory rather than the plugin-level `assets/` directory required by Codex. No bundled plugin or cache files were changed.

## Decisions and Rationale

- Keep the status, resume, and repository-analysis prompts because they are broad entry routes across the main portfolio workflows.
- Remove only the specialised report prompt from the presentation list; reducing one list does not remove or disable the underlying skill.
- Treat the icon warnings as an external bundled-plugin issue after two-way isolation, rather than masking them with an unrelated change here.
- Use a patch release because the change corrects presentation metadata and adds validation without changing skill behaviour or compatibility.
- Keep PP-35 open until the merged artifact is reinstalled and verified in a genuinely fresh Codex process.

## ADR Impact

No architecture decision record was required. The change is a bounded metadata correction plus validation of a documented runtime limit.

## Documentation Updated

- `docs/backlog.md`
- `docs/implementation-logs/2026-09-04_pp-35-codex-presentation-metadata.md`

## Lessons Learned

- Multiple start-up warnings sharing a plugin-load phase are not sufficient evidence that they have the same owner.
- One-process configuration overrides provide useful attribution evidence without changing persisted user state.
- Runtime presentation limits should be encoded in the repository self-check so future release preparation fails before installation.

## Next Steps

1. Review and merge the PP-35 implementation pull request.
2. Reinstall portfolio-prompts 0.4.1 through the standard plugin update flow.
3. Run a genuinely fresh Codex process and confirm that the portfolio default-prompt warning is absent.
4. Record the installed artifact evidence and close PP-35 in an evidence-only follow-up pull request.
5. Route the bundled spreadsheets icon-path issue to its owning plugin separately.

---

*Session logged: 2026-09-04. Author: Codex.*
