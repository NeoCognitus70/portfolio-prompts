# PP-35 Codex Presentation Metadata Closure — 2026-09-04

## Session Summary

This session completed the post-merge evidence gate for PP-35. Release 0.4.1 was verified on merged `main`, reinstalled through the configured local marketplace, reconciled byte-for-byte with its installed cache, and exercised in a genuinely fresh Codex process. The former portfolio-prompts `defaultPrompt` warning is absent, so PP-35 is resolved; the remaining icon warnings stay attributed to the external bundled spreadsheets plugin.

---

## Objectives

1. ✅ Verify PR #76 and the exact merge commit passed their GitHub Actions gates.
2. ✅ Reinstall release `0.4.1+codex.20260903212342` from merged `main`.
3. ✅ Prove parity between merged source and every installed release-bearing path.
4. ✅ Confirm a fresh Codex process emits no warning attributable to portfolio-prompts.
5. ✅ Reconcile `docs/backlog.md` and close PP-35 without changing runtime-bearing files.

---

## Test Results

| Stack | Suite | Before | After | Status |
|---|---|---|---|---|
| GitHub Actions | Prompt library integrity | PR run `33818392506` passed | Exact-merge run `33818760253` passed for `58336ed5d85f469711964382e560a45a10263eee` | ✅ PASS |
| Python | Full library self-check | Passed on the implementation branch | Passed again on merged `main` | ✅ PASS |
| Plugin tooling | Package validation | `0.4.1+codex.20260903212342` passed before merge | Merged source passed before reinstall | ✅ PASS |
| SHA-256 | Release-bearing source/cache parity | Reinstall pending | 66/66 paths; zero missing, extra, or mismatched | ✅ PASS |
| Codex runtime | Fresh-process start-up | Baseline session emitted the maximum-three `defaultPrompt` warning | Session `01a069a9-ad11-7fe3-bb3a-b2053bc2f067` emitted no portfolio-prompts warning | ✅ PASS |

---

## Changes Implemented

### Verified the merged release independently

**Files changed:**

- None. The verification used merged commit `58336ed5d85f469711964382e560a45a10263eee` without modifying release-bearing source.

PR #76 merged implementation commit `133358316c67a26edf242d1a48a9e7ffb118a05d` at 2026-09-03T23:42:37Z. Its PR integrity run `33818392506` passed, followed by exact-merge `main` run `33818760253`.

### Reinstalled and reconciled the installed artifact

**Files changed:**

- None in the repository. `codex plugin add portfolio-prompts@portfolio-prompts` populated the managed plugin cache.

The reinstall reported root `C:\Users\brook\.codex\plugins\cache\portfolio-prompts\portfolio-prompts\0.4.1+codex.20260903212342`. A SHA-256 comparison covered both manifests, root prompts and configuration, `skills/`, and `tools/`: source and cache each contained 66 paths, with no missing, extra, or mismatched files.

### Closed the authoritative backlog item

**Files changed:**

- `docs/backlog.md` — advanced to version 23, moved PP-35 to Resolved Items, completed its final criterion, and set the outstanding count to zero.
- `docs/implementation-logs/2026-09-04_pp-35-codex-presentation-metadata-closure.md` — recorded this immutable post-merge evidence.

Fresh read-only session `01a069a9-ad11-7fe3-bb3a-b2053bc2f067` started from the installed release without the former `defaultPrompt` warning. It continued to show icon warnings already isolated to `spreadsheets@openai-primary-runtime` and an unrelated PowerShell shell-snapshot warning; neither is attributable to portfolio-prompts.

---

## Technical Decisions

| Decision | Rationale | Alternatives rejected |
|---|---|---|
| Close PP-35 through an evidence-only patch with no version bump | Release 0.4.1 already contains the runtime fix; this patch records proof of its merged and installed behaviour only. | Create another release merely to record that 0.4.1 was installed. |
| Keep the spreadsheets icon warnings outside this backlog | Two-way plugin isolation identifies a different owning plugin, and changing bundled cache content here would cross the repository boundary. | Misreport external start-up noise as a failed portfolio-prompts fix or alter an unowned plugin. |
| Require source/cache SHA-256 parity in addition to the version check | A matching manifest version alone does not prove the installed artifact contains the merged files. | Infer installation correctness from the install command's exit status alone. |

No new ADR was required because these decisions apply only to the evidence and ownership boundary for PP-35.

---

## Documentation Updates

- `docs/backlog.md` — records PP-35 as resolved and shows no outstanding prompt-library items.
- `docs/implementation-logs/2026-09-04_pp-35-codex-presentation-metadata-closure.md` — preserves the merge, installation, parity, and fresh-runtime evidence.

---

## Lessons Learned

- Post-merge runtime verification should retain the fresh session identifier as well as the installed cache path.
- Matching all release-bearing files by path and SHA-256 closes the gap between a successful install command and proof of the artifact actually installed.
- External warnings can remain visible without weakening closure when ownership has been demonstrated independently and the repository-owned warning is absent.

---

## Recommendations / Next Steps

- [ ] Merge the evidence-only PP-35 closure pull request — owner: maintainer; priority: immediate.
- [ ] Reconcile the portfolio-root worklist and handover after the project closure merges — owner: maintainer/Codex; priority: next control step.
- [ ] Route the bundled spreadsheets icon-path issue to its owning plugin outside this repository — owner: bundled-plugin maintainer; priority: low.

---

*Session logged: 2026-09-04. Author: Codex.*
