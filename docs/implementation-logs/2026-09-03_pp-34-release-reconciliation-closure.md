# PP-34 Release Reconciliation Closure — 2026-09-03

## Session Summary

This session reconciled the `portfolio-prompts` release identity after source had moved beyond the
installed `0.3.0` cache without a version change. Release `0.4.0` was gated, merged through PR #74,
reinstalled from merged `main`, and verified from a fresh Codex process. PP-34 is now resolved;
PP-35 separately records the runtime presentation-metadata warnings discovered during final
verification.

---

## Objectives

1. ✅ Reconcile the stale backlog state and publish accumulated runtime-bearing changes as `0.4.0`.
2. ✅ Add deterministic backlog-status and manifest-version parity checks.
3. ✅ Merge, reinstall and verify the release from a fresh Codex process.
4. ✅ Prove source/cache parity for all 66 release-bearing paths and all 13 registry projects.
5. ✅ Close PP-34 without obscuring the two newly observed runtime warnings.
6. ⏸️ Repair the presentation-metadata warnings; this is separately scoped as PP-35.

---

## Test Results

| Stack | Suite | Before | After | Status |
|---|---|---|---|---|
| Python | Focused release-metadata unit tests | No focused coverage | 7/7 passing | ✅ PASS |
| Python | `python -B tools/check-library.py` | Existing gate passed before implementation | Extended gate passed before commit, after merge and on this closure patch | ✅ PASS |
| Plugin tooling | Codex plugin manifest validation | `0.3.0` validated but did not prevent release drift | `0.4.0+codex.20260903165138` validated | ✅ PASS |
| GitHub Actions | Prompt library integrity | PR #74 run `33784960239` passed | Merge commit `75e5c90` run `33785332613` passed | ✅ PASS |
| Codex runtime | Fresh installed-skill invocation | Installed `0.3.0` lacked later source changes | Fresh process loaded `0.4.0`, found 13 projects and completed `portfolio-status` | ✅ PASS with environment limitations |
| SHA-256 | Release-bearing source/cache parity | Four known source/cache differences | 66/66 paths; 0 missing, 0 extra, 0 mismatched | ✅ PASS |

The fresh read-only process could not access the normal GitHub keyring or user-level Git ignore
file. It therefore reported remote PR/CI evidence as `UNAVAILABLE` and exposed `.claude/` as
untracked; the parent session separately confirmed valid GitHub authentication and a clean,
aligned `portfolio-prompts/main` checkout.

---

## Changes Implemented

### Publish one truthful release identity

**Files changed in implementation commit `fcb6c5c`:**

- `.claude-plugin/plugin.json` — bumped the shared release to `0.4.0`.
- `.codex-plugin/plugin.json` — paired `0.4.0` with cachebuster `20260903165138`.
- `docs/backlog.md` — opened PP-34, reconciled PP-32/PP-33 history and corrected risk counts.
- `tools/build-portfolio-reviews.py` — removed an unrelated PP-33 identifier collision.
- `tools/check-library.py` — added release-metadata validation.
- `tools/tests/test_release_metadata.py` — added seven deterministic regression tests.

PR [#74](https://github.com/NeoCognitus70/portfolio-prompts/pull/74) merged as
`75e5c9066937ed6518329e3db37f905f68dc758d` after its integrity gate passed.

### Verify the installed release independently

**Evidence gathered:**

- `codex plugin add portfolio-prompts@portfolio-prompts` installed the merged release at
  `C:\Users\brook\.codex\plugins\cache\portfolio-prompts\portfolio-prompts\0.4.0+codex.20260903165138`.
- Fresh session `01a06867-ec9c-7a71-a878-a5a39e80ed2b` loaded `portfolio-status` from that cache,
  resolved the explicit portfolio root, and covered all 13 registry projects.
- A SHA-256 comparison across root prompts/configuration, `skills/`, `tools/`, and the Codex
  manifest found exactly 66 paths on each side with no missing, extra or changed files.

### Separate new warnings from the resolved drift

**Files changed in this closure patch:**

- `docs/backlog.md` — resolves PP-34 with merge/install/parity evidence and opens PP-35.
- `docs/implementation-logs/2026-09-03_pp-34-release-reconciliation-closure.md` — preserves this
  immutable closure record.

The fresh process directly attributed the four-entry `defaultPrompt` warning to this plugin's
manifest. Its icon warnings named no source, and this repository declares no icon fields, so PP-35
requires attribution before assigning an icon repair.

---

## Technical Decisions

| Decision | Rationale | Alternatives rejected |
|---|---|---|
| Close PP-34 and track the runtime warnings under PP-35 | PP-34 concerns release identity and cache parity, both of which are proven. Presentation metadata is a distinct, lower-priority defect. | Keep PP-34 open indefinitely despite satisfying every drift criterion; silently ignore the warnings. |
| Do not change manifests in the evidence-only closure patch | The patch records evidence in backlog/history only; it does not change prompts, skills, tools, registry data or runtime presentation behaviour. | Create a recursive release solely to record that the prior release was installed. |
| Treat icon ownership as unconfirmed | The warning omitted a source path and this plugin has no icon declarations. | Guess that `portfolio-prompts` emitted it and change unrelated files. |

No new ADR was required: these decisions apply to the PP-34 evidence boundary and PP-35 triage,
not to the library architecture.

---

## Documentation Updates

- `docs/backlog.md` — PP-34 closure evidence, PP-35 scope and reconciled risk summary.
- `docs/implementation-logs/2026-09-03_pp-34-release-reconciliation-closure.md` — this immutable
  implementation and release-closure record.

---

## Lessons Learned

- A manifest version match is necessary but insufficient: the installed cache should be checked by
  path inventory and content hash after reinstall.
- Plugin startup warnings can expose ingestion constraints that static schema validation misses;
  future self-gates should encode confirmed runtime limits.
- Warning attribution matters. A process that loads several plugins can emit presentation warnings
  without naming every source, so repository changes require exact provenance.
- A fresh read-only Codex process may not inherit the interactive session's GitHub keyring or global
  Git ignore file; unavailable evidence must remain explicit.

---

## Recommendations / Next Steps

- [ ] Implement PP-35 only after owner approval: reduce `defaultPrompt` to three, add regression
  coverage, and attribute the icon warnings — LOW priority.
- [ ] Review and commit this PP-34 closure patch as the next approval-gated step.
- [ ] After the closure PR merges, reconcile the portfolio-root worklist and write handover v3 in
  the separate root repository.

---

*Session logged: 2026-09-03. Author: Codex.*
