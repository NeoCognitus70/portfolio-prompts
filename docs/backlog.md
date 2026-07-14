# portfolio-prompts — Backlog

**Version:** 7 — PP-26 handover pair integrity resolved; no outstanding items
**Last Updated:** 2026-07-14
**Based on:** Second full library review ([`docs/library-review_2026-07-13.md`](library-review_2026-07-13.md)),
whose theme is turning the prose registry into machine-readable config and packaging the prompts as
portable skills. The first review (2026-06-17) produced PP-00..PP-12 (all resolved). Items carry the
`PP-` prefix and mirror `WORKLIST_portfolio-prompts.md` at the portfolio root (loop memory, outside
this repo).

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

Ordered by priority score (highest first). PP-13..PP-24 derive from the 2026-07-13 review
([`library-review_2026-07-13.md`](library-review_2026-07-13.md)); PP-25 implements portfolio backlog
item P-06. The review's section 4 weakness numbers are cited where applicable. A
`WORKLIST_portfolio-prompts.md` can be derived from these with
`derive-worklist.prompt.md using PROJECT=portfolio-prompts`.

### MEDIUM Priority (Score: 10–19)

#### PP-25: Add a safe portfolio workspace preflight — Score: 18
**Score:** Security (0) + Drift (10) + Maintenance (8) = **18**
**Status:** RESOLVED 2026-07-14 in
[`portfolio-prompts` PR #34](https://github.com/NeoCognitus70/portfolio-prompts/pull/34) —
`tools/workspace_preflight.py` now gates every orchestration fan-out.
**Problem (portfolio P-06):** fan-outs selected targets from prose and launched without a common,
non-mutating check that each checkout was structurally complete and that its local evidence was
qualified against already-fetched remote state.
**Success Criteria:**
- [x] A documented command loads `orchestration_target: true` rows from `registry.yml`, with optional
      subset and JSON modes; no second project list exists.
- [x] Each target reports folder/Git state, branch, dirty/upstream/ahead/behind state, authoritative
      backlog, resolved gate source/steps, latest handover pair, and advisory freshness against the
      fetched default head.
- [x] Missing/unsafe evidence is `BLOCKED`; behind/ahead, topic/detached branch, and handover
      qualifications are `WARN`; the exit-code contract distinguishes target blockers from a
      registry/invocation failure.
- [x] Git execution is restricted to a read-only allowlist with optional locks disabled. The tool
      never refreshes a remote or mutates a checkout.
- [x] `derive-all-worklists`, `review-all-projects`, and `loop-all-worklists` run the preflight before
      coupling or agent launch and faithfully exclude/report blocked targets.
- [x] Deterministic integration coverage exercises clean, dirty, behind, topic-branch,
      missing-backlog, and missing-handover fixtures and asserts checkout-visible Git state is
      unchanged. The library self-gate runs the suite in CI.

#### PP-13: Extract the project registry into a structured `registry.yml` — Score: 14
**Score:** Security (0) + Drift (8) + Maintenance (6) = **14**
**Status:** RESOLVED 2026-07-13 — `registry.yml` promoted to the library root and cited by the contract.
**Problem (review weaknesses #1, #7, #8):** Every prompt resolves a project's backlog path, review
folder, gates, and couplings by *parsing English* out of the README table and its prose deviation
notes. This is the library's chief drift risk and the main blocker to turning the prompts into
portable skills.
**Success Criteria:**
- [x] A machine-readable `registry.yml` (or equivalent) holds one `defaults:` block plus one row
      per project: `github`, `status`, `gates`, `deviations` (backlog/review/log/template paths),
      `couples_with`, `orchestration_target`, and any live-API/SDD/multi-stack flags. — **Done:**
      `portfolio-prompts/registry.yml` (8 projects incl. the meta row; parses; every non-meta
      `project` maps to a real folder).
- [x] The prompts/contract cite it as the source a skill loads; the README table becomes a
      *generated* view (see PP-23) rather than a hand-maintained one. — **Done:** the contract cites
      it (`project-layout.md` §"Machine-readable registry"); the README table is now generated by
      `tools/render-registry.py` (**PP-23**, resolved same day).
- [x] The prototype in `proposals/registry.yml` is reviewed, corrected, and promoted (or replaced).
      — **Done:** promoted to `../registry.yml`, corrected (both onboarded projects are now full
      rows, `unregistered_candidates` emptied); `proposals/README.md` updated to point at it.
**Depends on:** nothing. **Unblocks:** PP-23 (done), PP-24.

#### PP-14: Add a handover manifest/index to kill the version-parsing hazard — Score: 10
**Score:** Security (0) + Drift (6) + Maintenance (4) = **10**
**Status:** RESOLVED 2026-07-13 — `session-notes/manifest.json` + `tools/build-handover-manifest.py`.
**Problem (review weakness #2):** Handover version lives in the filename (`_v13_`), so every prompt
must repeat "parse `{N}` numerically, not lexically" and "glob the root for stray files". The design
causes a recurring class of bug (a v11 was once written to the root and missed).
**Success Criteria:**
- [x] `session-notes/` carries a manifest (e.g. `index.json`/`manifest.yml`) listing
      `{project, version, timestamp, path}`, updated by `write-handover` on every write. — **Done:**
      `session-notes/manifest.json` (a `handovers` index + a `latest` map), regenerated by
      `tools/build-handover-manifest.py`; `write-handover` now runs it after writing. Built against
      the live folder: 30 handovers, 8 projects, `latest` resolves magento to v18 (which a plain sort
      would miss).
- [x] `resume-session`, `derive-worklist`, `loop-worklist`, and `write-handover` read "latest" from
      the manifest, falling back to the numeric-glob rule only if the manifest is absent. — **Done:**
      all four prompts prefer `manifest.json` `latest["{PROJECT}"]` and keep the numeric-glob rule as
      an explicit fallback. Contract documents the manifest (`project-layout.md` §Handovers).
**Note:** the root support repository tracks the paired handovers but deliberately ignores the
generated manifest, so the manifest is not part of any PR; it is regenerated in place while the
prompts/tool that maintain it are tracked deliverables.

#### PP-15: Add real self-gates for the library (path/registry/format checks) — Score: 10
**Score:** Security (0) + Drift (5) + Maintenance (5) = **10**
**Status:** RESOLVED 2026-07-13 — `tools/check-library.py` is the library's verify gate.
**Problem (review weakness #4):** The library's gates are "docs-only (link/grep)". Nothing checks
that a path a prompt cites still exists, that every registry project name maps to a real folder, or
that the canonical worklist example parses as the format `loop-worklist` Step 0 expects. The library
asks every project for gates but under-gates itself.
**Success Criteria:**
- [x] A check script (invoked as the library's `verify` gate) asserts: every registry `project`
      resolves to a folder; every path cited in `project-layout.md`/prompts exists; the worklist
      example parses; internal doc links resolve. — **Done:** `tools/check-library.py` checks
      registry-folder mapping (+ drift: no unclassified workspace repo), README-generated (delegates
      to `render-registry.py --check`), internal Markdown links, and the worklist example. Wired as
      the `PROJECT=portfolio-prompts` gate in `registry.yml`. Standalone-clone safe.
- [x] `registry.yml` (PP-13), if present, is the input for the folder/name check. — **Done.**
**Caught on first run (now recorded):** two workspace repos, `portfolio-landing` and
`mobile-forex-automation`, were unclassified — added to `unregistered_candidates` pending a
membership decision (see below).

#### PP-16: Reconcile the registry with the two unregistered projects — Score: 10
**Score:** Security (0) + Drift (8) + Maintenance (2) = **10**
**Status:** RESOLVED 2026-07-13 — both projects were already onboarded to the README registry by
**PR #18** (`dfc8c5e`), which landed independently before the 2026-07-13 review PRs. This item was
authored against a `main` that predated #18, so it was born already-satisfied.
**Problem (review weakness #8):** `markdown-renderer` and `orangehrm-pim-automation` exist in the
workspace (both published, CI + Pages live) but are not registry rows, so the `*-all-*` fan-outs
silently skip them. `proposals/registry.yml` lists them under `unregistered_candidates:`.
**Success Criteria:**
- [x] A recorded decision: add each as a full registry row (with its gates/deviations), or document
      why it is deliberately excluded. — **Done (#18):** both added as full `Active` rows with gates
      (`markdown-renderer` = `npm run verify`; `orangehrm-pim-automation` = per `ci.yml`, docker + `npm test`).
- [x] If added, `orchestration_target` is set correctly so the fan-outs see them. — **Done:** both
      are plain `Active` rows, so the `*-all-*` fan-outs now target them.
**Residual — now cleared (PP-13, 2026-07-13):** the structured registry was promoted to
`registry.yml` at the library root with both projects as full rows (`unregistered_candidates`
emptied); the prototype `proposals/registry.yml` was removed. Nothing outstanding for PP-16.

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
**Status:** COMPLETE (PP-05)
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
**Status:** COMPLETE (PP-10)
**Problem:** The "launch all agents in one turn" rule is fragile — a real run forgot the 3rd
(sequential) agent and had to relaunch it.
**Success Criteria:**
- [ ] Each orchestrator's fan-out step contains an explicit "N targets == N agents launched"
      confirmation, with the coupled/sequential agent included in the count.

### LOW Priority (Score: 0–9)

#### PP-23: Add a `refresh-registry` prompt/script (regenerate README from `registry.yml`) — Score: 9
**Score:** Security (0) + Drift (5) + Maintenance (4) = **9**
**Status:** RESOLVED 2026-07-13 — `tools/render-registry.py` generates the README table from `registry.yml`.
**Problem:** Once the registry is data (PP-13), the README table must stay in sync with it. A
regenerator makes the human-readable table a generated view, so the two copies cannot diverge.
**Success Criteria:**
- [x] A prompt or script renders the README registry table from `registry.yml`; running it on a
      clean tree produces no diff. — **Done:** `tools/render-registry.py` rewrites the block between
      the README `<!-- REGISTRY:START/END -->` markers; verified idempotent (a second run and
      `--check` report no change). Composes each Notes cell as prose + Gates + Deviations + Depends.
      `registry.yml` gained `status_label` and generator-facing field notes; the README table and
      the mirror note now say "generated — do not hand-edit".

#### PP-24: Package the collection as a portable skill/plugin pack — Score: 9
**Score:** Security (0) + Drift (3) + Maintenance (6) = **9**
**Status:** RESOLVED 2026-07-13 — this repo is now a Claude Code plugin (`.claude-plugin/plugin.json`)
with 11 skills in `skills/`.
**Problem:** The prompts are portfolio-coupled only through `project-layout.md` + the registry.
Externalising those into loadable config (PP-13) lets each `*.prompt.md` become a `SKILL.md` with
`project` as an argument, runnable on any project.
**Success Criteria:**
- [x] `github-repo-analysis` shipped as the zero-config pilot skill — **Done:** `skills/analyze-repo/`
      (takes `repo` + `depth`, no PROJECT). **[~] "smoke-tested on a real repo":** all 11 skills are
      **structurally** validated by `tools/check-library.py` (frontmatter is valid YAML, `name`
      matches folder, the delegated `*.prompt.md` exists) — a real bug was caught and fixed
      (unquoted colons broke the YAML frontmatter). A **live auto-trigger test needs the plugin
      installed in an interactive session** (cannot be done in this non-interactive run) — recommended
      as a post-merge check.
- [x] A plugin manifest packages the skills + `registry.yml`/`project-layout.md` config + templates.
      — **Done:** `.claude-plugin/plugin.json`; the config/templates are bundled by virtue of living
      in the same repo, and skills load them via `${CLAUDE_PLUGIN_ROOT}`.
- [x] Skill `description`s disambiguated so the seven single-project skills trigger correctly;
      `loop-all-worklists` kept explicit-invocation only (mutating). — **Done:** each description
      states when-to-use + a "NOT for X (use Y)" disambiguator; `loop-all-worklists` is marked
      MUTATING/explicit-only.
**Design:** each skill is a **thin wrapper** that reads-and-follows its canonical `*.prompt.md`
(single source of truth, no duplication). `onboard-project` was intentionally left to PP-20 and is
now shipped; a separate `refresh-registry` skill remains superseded by `tools/render-registry.py`.
**Residual (portability):** the delegated lifecycle prompts still resolve portfolio-relative paths
against the CWD, so the single-project/fan-out skills target a session whose CWD is the portfolio
root; full any-workspace portability is follow-on. `analyze-repo` already has no such dependency.
**Depends on:** PP-13 (done).

#### PP-20: Add an `onboard-project` prompt — Score: 8
**Score:** Security (0) + Drift (3) + Maintenance (5) = **8**
**Status:** RESOLVED 2026-07-13 — added a prospective-project prompt and thin plugin skill. The
workflow discovers and confirms registry metadata, gates, backlog seed items, path deviations, and
recommended scaffold before any write. It stages the target scaffold PR first when needed, waits
for that contract to reach the target default branch, and only then stages the generated registry
PR; neither PR is merged by the workflow.
**Problem:** Onboarding a new project (registry row + `docs/backlog.md` + template scaffolding) is
implicit today — the inverse of `close-project` does not exist. It is done ad hoc.
**Success Criteria:**
- [x] A prompt that scaffolds a new project's backlog from the template, creates the recommended
      layout, and adds its registry row (via PR), stopping for the user where a decision is needed.

#### PP-17: Centralise the branch + PR universal norm into the contract — Score: 7
**Score:** Security (0) + Drift (4) + Maintenance (3) = **7**
**Status:** RESOLVED 2026-07-13 — the full policy remains only in `project-layout.md`; operational
prompts and plugin wrappers cite that section while retaining only their workflow-specific branch
mechanics. `check-library.py` now rejects policy restatements in active prompts and skill bodies.
**Problem (review weakness #6):** "All changes to `main` via branch + PR (harness blocks direct
pushes, 2026-06-10)" is restated in resume, loop, handover, close, and the contract — the same
PP-03/04/05 duplication pattern, not yet centralised.
**Success Criteria:**
- [x] The norm appears in full in exactly one place (`project-layout.md` §"Working norms"); the
      prompts cite it rather than restating the 2026-06-10 detail.

#### PP-21: Add a read-only `portfolio-status` prompt — Score: 6
**Score:** Security (0) + Drift (2) + Maintenance (4) = **6**
**Status:** RESOLVED 2026-07-13 — added a no-argument prompt and thin plugin skill that report every
registry project's local repo state, open backlog counts, latest handover, open PRs, and
default-branch CI. Missing evidence and registry-drift candidates remain explicit; the workflow
writes nothing, changes no repository, and does not refresh remote Git state.
**Problem:** There is no single command to see cross-registry state (latest handover version, open
PRs, CI colour, backlog counts) without mutating anything.
**Success Criteria:**
- [x] A read-only prompt that reports a per-project status line across the registry; writes no files
      and makes no repo changes.

#### PP-18: Make invocation paths OS-neutral — Score: 6
**Score:** Security (0) + Drift (3) + Maintenance (3) = **6**
**Status:** RESOLVED 2026-07-13 — all active README, prompt-header, and orchestrator launch examples
now use forward slashes. `check-library.py` prevents Windows-only invocation paths returning to
operational documentation while historical review/backlog evidence remains intact.
**Problem (review weakness #3):** Every invocation example uses Windows backslashes
(`portfolio-prompts\name.prompt.md`), a friction for cross-platform reuse and skill packaging.
**Success Criteria:**
- [x] Examples use forward slashes (valid on Windows too), or note both; no behaviour change.

#### PP-19: Add a human "reader's map" to the README — Score: 5
**Score:** Security (0) + Drift (2) + Maintenance (3) = **5**
**Status:** RESOLVED 2026-07-13 — README now gives first-time human readers a short route through
the lifecycle/table and invocation examples, points plugin users to skills, and separates that
reading path from the `project-layout.md`/`registry.yml` machine contract.
**Problem (review weakness #5):** The prompts are dense; a newcomer has no short orientation
separate from the machine conventions.
**Success Criteria:**
- [x] A one-paragraph "start here" map in the README distinguishing the human reading path from the
      machine conventions in `project-layout.md`.

#### PP-22: Add a `triage-review-findings` prompt — Score: 5
**Score:** Security (0) + Drift (2) + Maintenance (3) = **5**
**Status:** RESOLVED 2026-07-13 — added a named-review, two-phase prompt and thin plugin skill. It
normalises, deduplicates, backlog-checks, and prioritises findings in chat, then stops for explicit
user approval before writing the canonical portfolio-root worklist; it never actions or changes the
project repository. `derive-worklist` links to this explicit review-triage route.
**Problem:** The bridge from a `write-code-review` output to a derived worklist is folded into
`derive-worklist` today; an explicit triage step would make the review -> worklist hand-off legible.
**Success Criteria:**
- [x] A prompt (or a documented `derive-worklist` mode) that reads a named review and emits a
      prioritised, deduplicated candidate worklist for the user to approve.

#### PP-06: De-duplicate the `PROJECT=` rules between README and project-layout — Score: 9
**Score:** Security (0) + Drift (5) + Maintenance (4) = **9**
**Status:** COMPLETE (PP-06)
**Success Criteria:**
- [ ] The `PROJECT=` rule text exists in full in one file; the other links to it; the README
      registry table is unchanged.

#### PP-07: Add a dependency/security/licence deliverable to write-code-review — Score: 7
**Score:** Security (0) + Drift (3) + Maintenance (4) = **7**
**Status:** COMPLETE (PP-07)
**Success Criteria:**
- [ ] The review prompt names a dependency/security/licence deliverable with the
      "audit-if-available, never fabricate a CVE" caveat.

#### PP-09: Add "omit section as N/A — reason" + minimal-session flex to write-handover — Score: 6
**Score:** Security (0) + Drift (2) + Maintenance (4) = **6**
**Status:** COMPLETE (PP-09)
**Success Criteria:**
- [ ] The handover prompt permits `N/A — <reason>` for inapplicable sections without breaking the
      fixed shape.

#### PP-08: Pin one HTML-generation method in write-handover — Score: 6
**Score:** Security (0) + Drift (4) + Maintenance (2) = **6**
**Status:** COMPLETE (PP-08)
**Success Criteria:**
- [ ] The prompt names one default `.html` generation path; alternatives labelled fallbacks; the
      styling-template reuse is unambiguous.

#### PP-11: Add a minimal `docs/project-contract.md` example to project-layout — Score: 6
**Score:** Security (0) + Drift (2) + Maintenance (4) = **6**
**Status:** COMPLETE (PP-11)
**Success Criteria:**
- [ ] `project-layout.md` includes a copy-pasteable `project-contract.md` skeleton with a `Gates`
      section.

#### PP-12: Add a lifecycle diagram to README — Score: 5
**Score:** Security (0) + Drift (2) + Maintenance (3) = **5**
**Status:** COMPLETE (PP-12)
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
| MEDIUM (10–19) | 11 | **11 complete** (PP-00, PP-03, PP-04, PP-05, PP-10, PP-13, PP-14, PP-15, PP-16, PP-25, PP-26) — 0 open |
| LOW (0–9) | 16 | **16 complete** (PP-01, PP-02, PP-06..PP-09, PP-11, PP-12, PP-17..PP-24) — 0 open |
| **Total Outstanding** | **0** | — |
| Resolved | 27 | PP-00..PP-26 |

**Outstanding, by suggested order:** None.

---

## Resolved Items

Resolved items are kept as a record that the gap existed.

#### PP-26: Enforce handover pair integrity; keep freshness advisory (portfolio P-09) ✅ Resolved 2026-07-14
**Score: Security 0 + Drift 8 + Maintenance 4 = 12 (MEDIUM).**
**Problem:** four root handovers existed as Markdown without HTML companions and nothing failed —
missing presentation companions could recur silently. Handover-vs-head freshness needed to stay a
warning so legitimate post-handover commits do not produce false failures.
**Resolution:** `build-handover-manifest.py` now exits non-zero from both modes listing each
unpaired Markdown handover (write-handover's post-step becomes the authorship-time gate);
`check-library.py` gained a `handover-pairs` check that fails when the sibling `session-notes/`
archive contains an unpaired handover and skips with a note in standalone clones; deterministic
tests (`tools/tests/test_handover_manifest.py`) cover complete pairs, violations, numeric-latest,
and non-handover files, discovered by the self-gate's widened `test_*.py` pattern. Freshness
remains an advisory preflight `WARN`; `project-layout.md` now records the pair-integrity contract
and the refresh policy for resting/closed projects (backlog/Git cross-checking suffices; terminal
refresh at close, on scope-changing resume, or when public claims become wrong). The four missing
HTML companions themselves are generated in the root support repository's paired P-09/P-10 change.
**See:** portfolio `PORTFOLIO_BACKLOG.md` P-09.

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
