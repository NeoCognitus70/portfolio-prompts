# portfolio-prompts — Backlog

**Version:** 1 — initial backlog; onboards the prompt library to its own contract (PP-00)
**Last Updated:** 2026-06-17
**Based on:** Analysis of all 13 library files (chat review, 2026-06-17), focus on
`github-repo-analysis-prompt.md`. Items carry the `PP-` prefix and mirror
`WORKLIST_portfolio-prompts.md` at the portfolio root (loop memory, outside this repo).

This backlog is the source of truth for improvements to the **prompt library itself**. Ordering is
by priority score (highest first).

**Priority Scoring System** (adapted for a docs/prompt library):
- **Score = Security Impact (0–10) + Drift/Breakage Probability (0–10) + Maintenance Burden (0–10)**
- For a prompt library, **Security Impact is effectively 0**; priority is driven by drift risk
  (the same rule restated in many files going out of sync) and maintenance burden.
- **HIGH (20–30) / MEDIUM (10–19) / LOW (0–9).**

**Scope note (PP-00 decision):** `portfolio-prompts` is a **meta** member of the registry — it is
self-onboarded (this backlog exists, so single-project prompts such as `resume-session`,
`derive-worklist`, `loop-worklist`, `write-implementation-log`, and `write-code-review` work
against `PROJECT=portfolio-prompts`), but it is **not a target of the orchestration fan-outs**
(`derive-all-worklists`, `loop-all-worklists`, `review-all-projects`), which operate on the
test-automation projects, not the prompt library.

---

## Outstanding Items

Ordered by priority score (highest first).

### MEDIUM Priority (Score: 10–19)

#### PP-03: Centralise the validation-gate cascade — Score: 12
**Score:** Security (0) + Drift (6) + Maintenance (6) = **12**
**Status:** COMPLETE (PP-03)
**Problem:** The first-hit-wins gate cascade is restated near-verbatim in `loop-worklist`,
`derive-worklist`, and `write-code-review`; `project-layout.md` already holds the canonical copy.
A change today is a 4-file edit with drift risk.
**Success Criteria:**
- [ ] Cascade text appears in full in exactly one file (`project-layout.md`).
- [ ] The three consumers cite it; consumer-specific nuance kept as a short delta, not a full copy.

#### PP-04: Centralise the WORKLIST file-format spec + worked example — Score: 12
**Score:** Security (0) + Drift (6) + Maintenance (6) = **12**
**Status:** COMPLETE (PP-04)
**Problem:** The `- [ ]` item-line format + acceptance-criteria convention is restated in
`derive-worklist`, `loop-worklist`, and both `*-all-worklists` orchestrators, with no canonical
example to lock the shape.
**Success Criteria:**
- [ ] One canonical format spec + a minimal 2-item example in `project-layout.md`.
- [ ] Consumers cite it; the example parses as the format the loop's Step 0 expects.

#### PP-05: Extract the shared orchestrator sub-agent scaffold — Score: 12
**Score:** Security (0) + Drift (6) + Maintenance (6) = **12**
**Status:** READY TO START
**Problem:** `derive-all-worklists`, `loop-all-worklists`, and `review-all-projects` each carry a
long, near-identical self-contained sub-agent template + unattended-mode rules.
**Success Criteria:**
- [ ] Common scaffold (working-directory line, "follow it exactly", unattended rule, "final
      message is the only thing returned", sequential fallback) lives in one place in
      `project-layout.md`.
- [ ] The three orchestrators cite it and retain only their mode-specific deltas.

#### PP-00: Onboard portfolio-prompts to its own contract — Score: 10
**Score:** Security (0) + Drift (3) + Maintenance (7) = **10**
**Status:** COMPLETE (this commit) — see Resolved.
**Problem:** The library breaks its own onboarding rule: no registry row, no `docs/backlog.md`, so
the loop/resume/derive prompts have nothing to orient from.

#### PP-10: Add a launch-count self-check guard to the three orchestrators — Score: 10
**Score:** Security (0) + Drift (7, a real miss occurred) + Maintenance (3) = **10**
**Status:** READY TO START
**Problem:** The "launch all agents in one turn" rule is fragile — a real run forgot the 3rd
(sequential) agent and had to relaunch it.
**Success Criteria:**
- [ ] Each orchestrator's fan-out step contains an explicit "N targets == N agents launched"
      confirmation, with the coupled/sequential agent included in the count.

### LOW Priority (Score: 0–9)

#### PP-06: De-duplicate the `PROJECT=` rules between README and project-layout — Score: 9
**Score:** Security (0) + Drift (5) + Maintenance (4) = **9**
**Status:** READY TO START
**Success Criteria:**
- [ ] The `PROJECT=` rule text exists in full in one file; the other links to it; the README
      registry table is unchanged.

#### PP-07: Add a dependency/security/licence deliverable to write-code-review — Score: 7
**Score:** Security (0) + Drift (3) + Maintenance (4) = **7**
**Status:** READY TO START
**Success Criteria:**
- [ ] The review prompt names a dependency/security/licence deliverable with the
      "audit-if-available, never fabricate a CVE" caveat.

#### PP-09: Add "omit section as N/A — reason" + minimal-session flex to write-handover — Score: 6
**Score:** Security (0) + Drift (2) + Maintenance (4) = **6**
**Status:** READY TO START
**Success Criteria:**
- [ ] The handover prompt permits `N/A — <reason>` for inapplicable sections without breaking the
      fixed shape.

#### PP-08: Pin one HTML-generation method in write-handover — Score: 6
**Score:** Security (0) + Drift (4) + Maintenance (2) = **6**
**Status:** READY TO START
**Success Criteria:**
- [ ] The prompt names one default `.html` generation path; alternatives labelled fallbacks; the
      styling-template reuse is unambiguous.

#### PP-11: Add a minimal `docs/project-contract.md` example to project-layout — Score: 6
**Score:** Security (0) + Drift (2) + Maintenance (4) = **6**
**Status:** READY TO START
**Success Criteria:**
- [ ] `project-layout.md` includes a copy-pasteable `project-contract.md` skeleton with a `Gates`
      section.

#### PP-12: Add a lifecycle diagram to README — Score: 5
**Score:** Security (0) + Drift (2) + Maintenance (3) = **5**
**Status:** READY TO START
**Problem:** No "which prompt when?" ordering aid beyond the table. (The general-purpose
analysis-prompt index entry was already added in PP-01.)
**Success Criteria:**
- [ ] README shows the lifecycle ordering (resume -> derive -> loop -> implementation-log ->
      code-review -> handover -> close, with the three orchestration fan-outs noted).

#### PP-02: Cross-link github-repo-analysis and write-code-review — Score: 4
**Score:** Security (0) + Drift (2) + Maintenance (2) = **4**
**Status:** COMPLETE (PP-02)
**Problem:** ~70% topic overlap; the analysis prompt already points at the review prompt (PP-01),
but the reciprocal pointer is missing.
**Success Criteria:**
- [ ] `write-code-review.prompt.md` contains a "use the other when..." pointer to the analysis
      prompt, consistent with the analysis prompt's existing pointer.

---

## Risk Summary

| Priority | Count | Status Distribution |
|---|---|---|
| HIGH (20–30) | 0 | — |
| MEDIUM (10–19) | 5 | 4 ready, 1 complete (PP-00) |
| LOW (0–9) | 7 | 7 ready |
| **Total Outstanding** | **11** | (PP-02..PP-12 excl. PP-00) |
| Resolved | 2 | PP-00, PP-01 |

---

## Resolved Items

Resolved items are kept as a record that the gap existed.

#### PP-01: Integrate the orphaned github-repo-analysis prompt ✅ Resolved 2026-06-17
**Resolution:** Rewrote and committed the previously-untracked `github-repo-analysis-prompt.md`
(acquisition Step 0, depth-driven sections, dependency/security/licence pass, commit-history
maturity signals, multi-stack handling, defined output + en-GB/ASCII, cross-link to
write-code-review); listed it in the README as a general-purpose (not registry-bound) prompt.
**See:** commit `88295d1`, PR #11.

#### PP-00: Onboard portfolio-prompts to its own contract ✅ Resolved 2026-06-17
**Resolution:** Added a **meta** `portfolio-prompts` row to the README project registry and created
this `docs/backlog.md` seeded with PP-00..PP-12. The library is now self-onboarded for
single-project prompts but excluded as a target of the orchestration fan-outs (see the Scope note
above).
**See:** this commit.
