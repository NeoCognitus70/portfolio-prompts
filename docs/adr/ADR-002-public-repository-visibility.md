# ADR-002 — Public Repository Visibility

**Status:** Accepted
**Date:** 2026-08-01
**Backlog:** PP-31 / PP-32 / portfolio landing OD-LAND-05

## Context

The portfolio landing page presents `portfolio-prompts` as its public methodology and links directly
to the repository. The repository was private, so unauthenticated visitors received an HTTP 404 and
could not inspect the methodology promised by the public portfolio.

Publishing a repository also exposes its code, history, branches, issues, pull requests and Actions
logs. Before changing visibility, a redacted disclosure review therefore inspected all 129 commits,
current files, sensitive filenames, commit messages, GitHub issues and pull requests, comments,
Actions runs and logs, releases, wiki references, repository variables and secret metadata. It found
no high-confidence credential or private-key exposure. Three current test-evidence documents contain
ordinary local workspace paths, but no home-directory identity or credentials.

## Decision

`NeoCognitus70/portfolio-prompts` is public so the portfolio's methodology link is useful to an
unauthenticated visitor and the registry-owned `methodology` presentation role has a reachable
target.

After publication, GitHub secret scanning, push protection and validity checks are enabled. The
repository's missing explicit licence is tracked separately as PP-32 and remains blocked on an owner
decision; public visibility must not be interpreted as permission to reuse the work.

## Consequences

- The public methodology link resolves without authentication.
- Repository content and collaboration surfaces are publicly visible and the repository can be
  forked under GitHub's visibility rules.
- GitHub's repository security features provide continuing secret-detection safeguards.
- The owner must choose the licensing posture before the library can make a clear reuse grant.
- Future visibility or security-setting changes must be recorded with fresh evidence rather than
  inferred from this point-in-time review.

## Alternatives rejected

- **Keep the repository private:** preserves the broken public methodology link and contradicts the
  accepted presentation-role contract.
- **Remove or hide the methodology link:** masks the ownership problem instead of making the
  promised evidence accessible.
- **Assume a permissive licence:** licence selection is a rights-holder decision and cannot be made
  safely by an implementing agent.

## References

- [GitHub: Setting repository visibility](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility)
- [Portfolio presentation ownership decision](https://github.com/GBrooks1970/portfolio/blob/main/docs/decisions/001-presentation-ownership.md)
