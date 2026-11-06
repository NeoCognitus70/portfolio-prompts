# Design proposal - portfolio-structural-review

**Status:** APPROVED and used on 2026-11-05; retained as a proposal archive, not installed as a canonical library entry.\
**Prepared:** 2026-11-05\
**Author:** Codex (GPT-6)\
**Requested outcome:** analyse the previous structural reviews and design a reusable portfolio prompt if no equivalent exists.

## Recommendation

Add `portfolio-structural-review.prompt.md` as an evidence-only, portfolio-level review workflow. It should assess the portfolio's structure, operational consistency, presentation and demonstrated capabilities, compare them with prior structural reviews, and propose bounded candidates for later approval. It should write a new report and evidence appendix without fixing the subjects it reviews.

The complete approved instructions are in [the proposal prompt](portfolio-structural-review.prompt.md). The owner approved the design and explicitly instructed its first use on 2026-11-05. Canonical library installation remains a separate integration step.

## What the previous reviews establish

These are historical observations, not a new assessment of today's portfolio.

| Review | Main contribution | Design lesson |
| --- | --- | --- |
| [7 July 2026](https://github.com/GBrooks1970/test-automation-portfolio/blob/165b91489356d86455ac16a423e7852c1bc331f4/portfolio-docs/PORTFOLIO_STRUCTURAL_REVIEW_2026-07-07.md) | Separated root structure from project-internal quality; identified registry omissions, missing portfolio presentation, unversioned support records and capability gaps | Preserve the structural/code-review boundary and reconcile registry membership against the workspace; never hard-code the old seven-project inventory |
| [14 July 2026](https://github.com/GBrooks1970/test-automation-portfolio/blob/165b91489356d86455ac16a423e7852c1bc331f4/portfolio-docs/PORTFOLIO_STRUCTURAL_REVIEW_2026-07-14.md) | Compared the baseline with current evidence; assessed licences, control-plane integrity, local/remote Git state, handover pairs, capabilities, parked work and scored candidates | Best basis for a repeatable report: retain the change table, explicit evidence limits, ownership, acceptance boundaries and a separate approval step |
| [5 August 2026](https://github.com/GBrooks1970/test-automation-portfolio/blob/165b91489356d86455ac16a423e7852c1bc331f4/portfolio-docs/PORTFOLIO_STRUCTURAL_REVIEW_2026-08-05.md) | Reconciled registry, support/meta roles, lifecycle, worklists and public evidence after the landing programme | Preserve these dimensions and classify public artefacts accurately; improve the boundary between review findings and remediation |

The progression is from missing portfolio foundations, to maintenance and claim integrity, to public-evidence coverage and control-record hygiene. It does not justify automatically recommending another project whenever the review runs.

## Weaknesses the new prompt should avoid

1. **Mixing review and remediation.** The August method says read-only inspection (line 14), but the verdict says README corrections were included in the same change (lines 22-26). The proposed workflow writes only its own report/evidence directory. Fixes and backlog reconciliation remain separate actions.
2. **Recycling old gaps as current facts.** July's mobile gap later became mobile-web evidence, explicitly distinguished from native-device automation. Accessibility, contracts, visual testing and other capabilities also need fresh, scoped evidence before they can be called missing or complete.
3. **Overbroad health statements.** August's statement that every registry repository reports `npm audit = 0` (line 106) needs package/toolchain, timestamp and scope qualifications. A structural review should assess the audit policy and available evidence, not silently run every audit or infer a universal clean bill of health.
4. **Latest-run simplification.** July's CI summary predates the current workflow-inventory-aware rules. Reuse the present [portfolio-status prompt](../../portfolio-status.prompt.md) evidence and CI classification rules; do not fork a second algorithm or count a successful old run as coverage of the current head.
5. **Unclear denominators.** Showcase projects, methodology projects, hidden projects, meta tooling and support repositories are distinct populations. Neither the orchestration target filter nor the public showcase list is the whole structural scope.
6. **Historical authority drift.** Old reports, archived worklists and terminal handovers provide chronology. Current authoritative backlogs, source, registry roles and dated external observations determine current conclusions.
7. **Candidate IDs becoming commitments.** Use review-local IDs and deduplicate against existing owning backlogs. Do not allocate a new `P-` or `PP-` ID, alter status or assume that a review recommendation is accepted work.
8. **Concurrent-work collisions.** Record source SHAs before and after reading, retain other agents' changes, and reserve a unique output directory. A dirty or moving checkout is evidence to qualify, not permission to reset it or omit its project.

## Existing prompt coverage

The current canonical prompt catalogue, filenames, skill index, proposal notes and prompt-library backlog were checked. No dedicated structural-review prompt was found.

| Existing prompt | Its contract | Why it does not replace this proposal |
| --- | --- | --- |
| [portfolio-status](../../portfolio-status.prompt.md) | Read-only current-state report; writes nothing and does not recommend remediation | Supplies reusable evidence semantics, but not a durable structural review, historical comparison, capability analysis or candidate programme |
| [review-all-projects](../../review-all-projects.prompt.md) | Delegates comprehensive project code reviews and opens review PRs | Reviews project internals and has publication side effects that a structural review does not need |
| [portfolio-reviews-summary](../../portfolio-reviews-summary.prompt.md) | Builds or inspects the central index of project code reviews | Aggregates existing reviews, not portfolio governance, structure, public claims or capability gaps |
| [write-project-in-depth-report](../../write-project-in-depth-report.prompt.md) | Descriptive dossier for one registered project | Single-project historical/design scope, not portfolio-level structural findings |
| [triage-review-findings](../../triage-review-findings.prompt.md) | Proposes candidates from one named project review, then writes a worklist only after approval | A later project-level planning action; it must not implicitly own portfolio findings or execute this review |

## Proposed contract

- **Name:** `portfolio-structural-review`.
- **Parameters:** optional `PORTFOLIO_ROOT`, `BASELINE`, `EVIDENCE=live|local` (default live) and `TARGET_ROLES`. No `PROJECT=` and no silent subset.
- **Scope:** root support repository, all registered projects, meta tooling, classified support repositories, presentation surfaces, and separately labelled unregistered candidates.
- **Authority:** `project-layout.md` for path/registry conventions; current owning backlogs for status; current source and dated observations for verification.
- **Writes:** one exclusively reserved report directory under `portfolio-docs/structural-reviews/`. Markdown report, evidence appendix and a small source manifest; no HTML or central-index update is required.
- **Network:** read-only repository metadata, exact-ref files, workflow queries and public GET checks in live mode. Local mode clearly marks remote facts unverified. Neither mode fetches or changes Git refs.
- **Execution:** one reviewer by default. No project-code-review fan-out, dependency installation, application tests, infrastructure startup or dependency-audit sweep.
- **Output:** historical disposition, current inventory, structural findings, public-claim/evidence matrix, capability matrix, parked-work disposition and scored/deduplicated candidates with owners and acceptance boundaries.
- **Approval:** this draft is not used before approval. A later explicit invocation of the approved prompt authorises report creation; implementing its findings still requires a separate instruction.

## Report and evidence design

Preserve the 14 July review's useful narrative, with a standard evidence table and consistent statuses. Every significant finding must identify an owning surface, source path/line or URL/ref, observation date, impact, recommendation and whether it is new, carried, regressed or already accepted/deferred. Unknown evidence remains unknown.

Capability judgements distinguish implemented code, executed evidence, current evidence and public visibility. A private Azure project is not an absent capability or automatically publishable; browser emulation is not native-device testing; schema validation is not consumer-driven contracts; HTTP 200 is not proof that a page contains the expected report. Recommendations prefer a bounded improvement to existing evidence unless a new project fills a real, role-relevant gap.

The current portfolio backlog defines its score as Strategic/Completeness Value + Breakage/Gap Probability + Maintenance Burden, each 0-10, with HIGH 20-30, MEDIUM 10-19 and LOW 0-9. The draft reads that definition afresh rather than freezing it. The direction of Maintenance Burden must be explained: do not quietly replace the existing model with an effort estimate.

## Promotion checklist after approval

This is a proposed integration checklist, not work performed in this task.

1. Confirm whether approval covers design only, promotion, execution, or some combination; carry forward the owner's actual wording without assuming permission to run.
2. Place the approved prompt at the canonical library root and remove the draft-only banner. Retain this proposal as its design history.
3. Add the normal thin `skills/portfolio-structural-review/SKILL.md` wrapper and per-skill UI metadata, following current library conventions. Use explicit invocation by default because the workflow writes durable reports and may perform substantial remote inspection.
4. Register the prompt/skill in their catalogues and add the portfolio-scoped exception in `project-layout.md`; keep its path and CI rules delegated rather than copied. Reconcile library backlog/release metadata only within the approved integration scope.
5. Run the library's required gate and a bounded acceptance exercise. A prompt-only root addition is insufficient: `tools/check-library.py` lines 421-430 enforce prompt-to-skill coverage.
6. Run the structural review only when the owner's approval authorises using it. Do not automatically start it as part of packaging validation.

## Design acceptance cases

These are static design checks, not a live portfolio review.

| Situation | Required behaviour |
| --- | --- |
| An old review says a project is private or a capability absent | Recheck current evidence; mark unknown if unavailable |
| A current project is hidden, resting or not an orchestration target | Include it in structural inventory; respect its public-visibility boundary |
| A checkout is dirty or changes during reading | Record/qualify the state; use pinned evidence where available; never alter it |
| GitHub is unavailable or a workflow inventory is incomplete | Preserve local findings; report unavailable remote coverage rather than green |
| A page responds 200 with a login/error/old report | Record transport success separately from content/provenance failure |
| An old finding is already closed or explicitly deferred | Record its disposition; do not create a duplicate backlog item |
| Two reviewers start in the same minute | Reserve distinct versioned directories; never overwrite or update a shared index |
| A README needs an obvious fix | Report it with evidence; do not apply the fix during the review |
| A capability proposal requires a new external service or live security probe | Keep it a candidate; do not create accounts, start infrastructure or probe third-party systems |
| The prompt has been drafted but approval to use it has not arrived | Stop with the draft proposal; do not produce a current structural review |

## This task's delivery boundary

At the original design stage, only this design and its companion prompt were authored; execution awaited owner approval. The owner subsequently approved the design and instructed its use. The first structural review was completed in the root support repository under `portfolio-docs/structural-reviews/PORTFOLIO_STRUCTURAL_REVIEW_CODEX_v1_20261105T2150Z/`. This publication archives the approved proposal; it does not install a skill, register a canonical prompt or implement review findings.
