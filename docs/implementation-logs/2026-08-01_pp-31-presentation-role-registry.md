# PP-31 Canonical Presentation Role Registry — 2026-08-01

## Session Summary

This session implemented the registry half of the portfolio landing repository's accepted
presentation-ownership contract. Commit
[`d9ea5d0`](https://github.com/NeoCognitus70/portfolio-prompts/commit/d9ea5d02886bf518aaebd33f72f9e1cdbe31d1f5)
adds a required presentation role, deterministic validation and human-readable registry output;
draft PR [#50](https://github.com/NeoCognitus70/portfolio-prompts/pull/50) is ready for owner review.
Nine projects are classified as showcases and `portfolio-prompts` as methodology, with no hidden
projects in the initial classification.

---

## Objectives

1. ✅ Encode the accepted `showcase`, `methodology`, and `hidden` presentation roles in the
   canonical project registry.
2. ✅ Enforce the schema with deterministic validation and focused regression tests.
3. ✅ Document the ownership boundary and structural decision for future maintainers and agents.
4. ⏸️ Complete owner merge and confirm post-merge `main` CI; these remain PP-31 review gates.

---

## Test Results

| Stack | Suite | Before | After | Status |
|---|---|---|---|---|
| Python | Focused registry semantics | N/A — new suite | 5/5 | ✅ PASS |
| Python | Full deterministic tool suite | 8/8 baseline | 13/13 | ✅ PASS |
| Python | `tools/check-library.py` self-gate | Presentation field absent | PASS, including role semantics and generated README | ✅ PASS |

---

## Changes Implemented

### Canonical presentation classification

**Files changed:**

- `registry.yml` — requires one role per project and records the initial nine-showcase,
  one-methodology classification.
- `tools/render-registry.py` — renders the role as a deterministic README table column.
- `README.md` — exposes the generated role column and explains its public meaning.

### Validation and regression coverage

**Files changed:**

- `tools/check-library.py` — validates supported scalar roles independently of lifecycle and
  orchestration rules.
- `tools/tests/test_registry_semantics.py` — covers all supported values, missing and invalid
  values, multiple-value rejection, and the existing meta-project constraint.

### Governance and reusable evidence structure

**Files changed:**

- `docs/backlog.md` — adds PP-31 and records its implementation and review evidence.
- `docs/adr/ADR-001-presentation-role.md` — records the structural schema and ownership boundary.
- `docs/templates/implementation-log.template.md` — establishes the project-local canonical log
  template required by the implementation-log workflow.
- `project-layout.md` — adds role resolution to the machine-registry contract.
- `tools/README.md` — documents the expanded self-gate and test suite.

---

## Technical Decisions

| Decision | Rationale | Alternatives rejected |
|---|---|---|
| Require one scalar `presentation_role` on every project row, independently of `status` and `orchestration_target` | Public presentation, backlog lifecycle, and automation fan-out safety are distinct concerns. See `docs/adr/ADR-001-presentation-role.md`. | Inferring visibility from lifecycle or orchestration; duplicating membership authority in the landing repository; runtime browser fetches. |
| Classify the nine non-meta projects as `showcase` and `portfolio-prompts` as `methodology` | This preserves all current portfolio projects publicly while excluding the prompt library from showcase counts. | Hiding resting projects; counting methodology tooling as a showcase. |

---

## Documentation Updates

- `README.md` — generated presentation column and ownership prose.
- `docs/backlog.md` — PP-31 scope, criteria, status, and evidence.
- `docs/adr/ADR-001-presentation-role.md` — accepted structural decision.
- `docs/templates/implementation-log.template.md` — project-local canonical template.
- `docs/implementation-logs/2026-08-01_pp-31-presentation-role-registry.md` — this immutable
  implementation record.
- `project-layout.md` — registry field and consumer contract.
- `tools/README.md` — validator and test documentation.

---

## Lessons Learned

- A public-project count needs its own explicit source-of-truth field; lifecycle and orchestration
  metadata cannot safely answer a presentation question.
- Extracting row validation into a pure helper makes invalid YAML shapes testable without invoking
  cross-repository filesystem checks.
- Publishing the implementation commit before writing the immutable log allows the record to cite
  exact, durable commit and PR identifiers instead of placeholders.

---

## Recommendations / Next Steps

- [ ] Review and merge [PR #50](https://github.com/NeoCognitus70/portfolio-prompts/pull/50), then
  confirm post-merge `main` CI — owner / PP-31.
- [ ] Pin the merged registry commit in the landing generator and implement its generated/parity
  checks — landing owner / LAND-03.
- [ ] Keep public copy, ordering, tags and optional evidence actions in the landing repository;
  consume only membership, slug and presentation role from this registry — future agents.

---

*Session logged: 2026-08-01. Author: Codex.*
