# ADR-001 — Registry-Owned Presentation Role

**Status:** Accepted
**Date:** 2026-08-01
**Backlog:** PP-31 / portfolio landing LAND-02R
**Source decision:** [`GBrooks1970/portfolio` decision 001](https://github.com/GBrooks1970/portfolio/blob/main/docs/decisions/001-presentation-ownership.md)

## Context

The canonical registry owns portfolio membership, lifecycle status and orchestration eligibility,
but it did not state whether a member should appear as a public showcase, methodology/tooling, or
remain hidden. The landing page previously duplicated membership in hand-authored HTML, which
allowed its inventory to drift when ParaBank joined the registry.

Lifecycle and orchestration cannot safely stand in for visibility. Resting projects remain public
showcases, the meta prompt library is public methodology, and hidden membership may still need
lifecycle records.

## Decision

Every row under `registry.yml` `projects:` must declare exactly one scalar `presentation_role`:

- `showcase` — public showcase card and showcase count;
- `methodology` — public methodology/tooling, excluded from showcase counts; or
- `hidden` — registered but absent from public presentation and counts.

The field is independent of `status` and `orchestration_target`; validators must not derive or
cross-couple them. Support repositories remain under `support_repositories:` and do not receive a
project presentation role.

The registry owns the role and GitHub slug. The landing repository owns public copy, display order,
tags and optional evidence actions. Generation and parity checks consume the registry at build/check
time, while the deployed static page makes no runtime registry or GitHub API calls.

## Initial classification

Nine non-meta projects are `showcase`. `portfolio-prompts` is `methodology`. No project is currently
`hidden`.

## Consequences

- The self-gate fails if a project row omits the field or uses an unsupported/non-scalar value.
- The generated README registry view exposes the role for human review.
- Future onboarding must choose a role explicitly; visibility cannot happen accidentally.
- Landing generator work remains blocked until this schema change merges and records its commit.
- Adding a field requires coordinated changes in registry tooling, documentation and tests.

## Alternatives rejected

- **Infer from lifecycle status:** resting is about backlog state, not visibility.
- **Infer from orchestration eligibility:** fan-out safety is unrelated to public presentation.
- **Let the landing manifest own the role:** this would duplicate membership authority and recreate
  the drift LAND-01 corrected.
- **Fetch role data in visitors' browsers:** runtime coupling is unnecessary for a static portfolio.
