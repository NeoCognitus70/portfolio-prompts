# Magento Phase 2 registry reconciliation

Owner authority: 2026-11-09, continue to Phase 2, including registry/backlog reconciliation and checked PR merges. Phase 1 project PR #68 and support PR #366 are now merged. Magento has reopened maintenance work; the existing resting/Closed 2026-08-03 registry row is stale.

Before implementation: change only Magento lifecycle to active, replace its historical closure label and notes with current maintenance scope, preserve gates/orchestration/presentation and Docker metadata, then regenerate the README table. Keep historical Items 1–15 resolved; MAG-MAINT-02 remains open and exploratory browsers are not promoted. Verify YAML semantic isolation, renderer check, library self-gate and CI before merging the separate PR. Do not upgrade dependencies or start WebKit work.
