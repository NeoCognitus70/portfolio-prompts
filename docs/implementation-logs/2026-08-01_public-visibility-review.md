# Public Repository Visibility Review — 2026-08-01

## Session Summary

This session made `NeoCognitus70/portfolio-prompts` public after the owner approved option A and a
redacted disclosure review found no high-confidence secret exposure. The public methodology target
now returns HTTP 200 without authentication, and GitHub secret scanning, push protection and
validity checks are enabled. The review also exposed a missing explicit licence, now preserved as
blocked backlog item PP-32 rather than guessed by the implementing agent.

---

## Objectives

1. ✅ Review repository history and public GitHub surfaces before changing visibility.
2. ✅ Make the approved methodology repository public and verify unauthenticated access.
3. ✅ Enable the available GitHub secret-detection protections.
4. ✅ Record the structural decision and reconcile the newly identified licence gap.
5. ⏸️ Obtain the owner's licence choice and implement PP-32.

---

## Test Results

| Stack | Suite | Before | After | Status |
|---|---|---|---|---|
| Git history | Redacted high-confidence credential and sensitive-filename scan | Private repository; 129 commits pending review | 0 findings across 129 commits | ✅ PASS |
| GitHub | Issues, pull requests and comment text scan | 51 issues/PRs and 1 issue comment pending review | 0 high-confidence findings; 0 review comments | ✅ PASS |
| GitHub Actions | Completed run-log scan | 41 run logs pending review | 0 high-confidence findings; 0 unreadable logs | ✅ PASS |
| HTTP | Unauthenticated repository URL | 404 while private | 200 after publication | ✅ PASS |
| GitHub security | Secret-detection settings | Secret scanning disabled | Secret scanning, push protection and validity checks enabled | ✅ PASS |
| Python | `tools/check-library.py` | 13/13 on PP-31 closure | PASS on this documentation change | ✅ PASS |

---

## Changes Implemented

### Publish the methodology repository safely

**External state changed:**

- `NeoCognitus70/portfolio-prompts` — visibility changed from private to public after the approved
  disclosure review.
- GitHub repository security settings — secret scanning, push protection and validity checks
  enabled.

The review found no stored Actions secrets or variables, releases, wiki content, fork network,
rulesets or branch protection to migrate. No installed `gitleaks`, `trufflehog` or `git-secrets`
binary was available, so the review used compensating redacted history and GitHub-surface scans
whose output exposed no candidate values.

### Preserve the governance decision and follow-up

**Files changed:**

- `docs/adr/ADR-002-public-repository-visibility.md` — records the public-visibility decision,
  review boundary, safeguards and consequences.
- `docs/backlog.md` — creates PP-32 as a blocked owner-decision item and reconciles counts to 32
  resolved / 1 outstanding.
- `docs/implementation-logs/2026-08-01_public-visibility-review.md` — this immutable evidence
  record.

---

## Technical Decisions

| Decision | Rationale | Alternatives rejected |
|---|---|---|
| Publish only after a redacted history and GitHub-surface review | The public landing promise required unauthenticated access, while publication needed evidence that credentials and private material were not exposed. | Publishing without review; retaining a knowingly broken public link. |
| Enable secret scanning, push protection and validity checks immediately | Continuing automated protection reduces the chance that a future push introduces an exposed secret. | Relying only on the point-in-time manual scan. |
| Track the absent licence as blocked PP-32 | Public visibility is not a licence grant, and the rights holder must choose the intended reuse terms. | Guessing MIT, Apache-2.0 or another licensing posture. |

The structural visibility decision is recorded in
[`ADR-002`](../adr/ADR-002-public-repository-visibility.md).

---

## Documentation Updates

- `docs/adr/ADR-002-public-repository-visibility.md` — accepted visibility and security decision.
- `docs/backlog.md` — PP-32 and reconciled risk totals.
- `docs/implementation-logs/2026-08-01_public-visibility-review.md` — this immutable review log.

---

## Lessons Learned

- A public evidence link should be tested without an authenticated browser; repository ownership
  and visibility are separate from link correctness.
- Redacted scanning can preserve useful audit counts without printing candidate secrets into logs.
- Publishing reusable-looking source surfaces licensing ambiguity immediately; the safe response is
  an explicit owner checkpoint, not an inferred licence.

---

## Recommendations / Next Steps

- [ ] Choose the repository's licence posture and action PP-32 — owner / MEDIUM, blocked.
- [ ] Review and merge [PR #51](https://github.com/NeoCognitus70/portfolio-prompts/pull/51), then
  verify its post-merge `main` integrity run — owner / closure gate.
- [ ] Review LAND-03 in [portfolio PR #9](https://github.com/GBrooks1970/portfolio/pull/9); its
  generated methodology link now resolves publicly — portfolio owner / P1.

---

*Session logged: 2026-08-01. Author: Codex.*
