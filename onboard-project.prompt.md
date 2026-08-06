# Prompt — Onboard a project into the portfolio

Use this prompt for an **existing local Git repository** that should become a registered
test-automation-portfolio project:
`Read and follow portfolio-prompts/onboard-project.prompt.md using PROJECT=<folder> [GITHUB=<owner/repo>]`.

`PROJECT` is the prospective folder at the portfolio root, not an existing registry value.
`GITHUB` is optional when the checkout's `origin` unambiguously supplies it. This is a staged,
mutating workflow: it first presents an evidence-backed onboarding proposal and stops for approval;
it then prepares the project scaffold PR, waits for that to merge when required, prepares the
portfolio registry PR, and — for a publicly-visible project — finally prepares the portfolio-landing
evidence PR so the project cannot be registered yet absent from the public landing page. It never
merges any of these PRs.

---

You are **onboarding one existing local repository into the test-automation portfolio**. The
invocation names it as `PROJECT=<folder name at the portfolio root>` and may supply
`GITHUB=<owner/repo>`.

- If `PROJECT` is missing, ask for it; never infer it from open files.
- `PROJECT` is the explicit onboarding exception to the normal registered-project rule in
  `project-layout.md` at the resolved library root §"The `PROJECT` parameter": it must name a
  prospective local folder that is not already a `registry.yml` project row.
- This workflow does not create or clone a product repository. If the folder or its `.git`
  checkout is missing, stop and report what the user must provide.

Follow `project-layout.md` at the resolved library root, including its working norm for branches
and PRs. Work sequentially across the target, `portfolio-prompts`, and (for a publicly-visible
project) `portfolio-landing` repositories; do not launch sub-agents and never merge a PR.

## Phase 0 — Guard and establish identity

From the portfolio root (resolved per `project-layout.md` at the resolved library root
§"Resolving the portfolio root"):

1. Confirm that `registry.yml`, `project-layout.md`, and `templates/backlog.template.md` exist at
   the resolved library root. Also require a writable workspace checkout at
   `<portfolio root>/portfolio-prompts` before Phase 4; never edit an installed plugin-cache copy.
   If no candidate qualifies as the portfolio root, stop rather than resolving paths from another
   checkout.
2. Load `registry.yml`. If `PROJECT` is already under `projects`, stop: it is already onboarded and
   this workflow must not create a duplicate row. Report any missing contract files as a separate
   repair task.
3. Confirm `{PROJECT}/` exists and is its own Git checkout. Record its current branch, HEAD, default
   branch, working-tree status, `origin`, and open PRs. Record the same state for
   `portfolio-prompts/`.
4. Both repositories must be clean before writes. Do not stash, discard, absorb, or overwrite
   unrelated changes. An existing onboarding branch or PR is resumed after inspection, not
   duplicated.
5. Derive `owner/repo` from the target's `origin` and verify it with a read-only GitHub query. If
   `GITHUB` was supplied, it must match. If there is no unambiguous accessible remote, stop and ask
   for the canonical `GITHUB=<owner/repo>`; never invent an owner.
6. Note whether `PROJECT` appears under `unregistered_candidates`. Its candidate entry will be
   removed only in the later registry change; do not disturb other candidates.

## Phase 1 — Discover the onboarding contract

Inspect the target repository before proposing files: its README, existing docs/planning files,
toolchain manifests, CI workflows, test-runner configuration, project contract (if any), and
dependency/coupling evidence. Use that evidence to propose:

- **Registry identity:** `project`, verified `github`, status/status label, and concise notes.
- **Participation:** whether `orchestration_target` should be true. This is an explicit user
  decision because it controls portfolio fan-outs; do not default silently.
- **Validation gates:** commands already established by a project contract, CI, or toolchain. Use
  the gate cascade in `project-layout.md`; if no reliable gate can be found, ask what validation
  means for this project.
- **Path deviations:** only paths that genuinely differ from `registry.yml` defaults. Prefer the
  default layout for a new scaffold. Never encode defaults again under `deviations`.
- **Optional schema:** `multi_stack`, `product`, `sdd`, `live_api`, `couples_with`, or other existing
  registry fields only when repository evidence supports them. A coupling and its execution order
  require explicit user confirmation.
- **Notes:** short human context supported by the repository. Keep gate, deviation, and coupling
  prose out of `notes`; the registry renderer adds those clauses from structured fields.

Resolve the backlog path as an existing evidence-backed deviation or the default
`docs/backlog.md`:

- If a backlog already exists, read it fully and preserve it. Propose only necessary conformance
  changes; never replace a project's established backlog merely to match the shared template.
- If it is missing, propose a version-1 backlog scaffold based on
  `templates/backlog.template.md`. Replace every required placeholder with real project data. Seed
  risks only from evidence and show them for approval; do not fabricate scores or work to make the
  backlog look populated. When no risks are known, use explicit empty priority sections and a
  zero-outstanding summary.

Inventory the recommended structure from `project-layout.md`: implementation-log directory and
template, ADR directory, changelog, and review directory. Propose only missing pieces, copying
shared templates without overwriting project-specific files. Render placeholders in live documents
such as `CHANGELOG.md`; preserve reusable placeholder tokens only in files intentionally ending in
`.template.md`. Do not add `.gitkeep` files solely to track empty directories unless that repository
already uses that convention. Create an optional `docs/project-contract.md` only when confirmed
gates or project-specific norms need it.

## Phase 2 — Present the plan and stop

Before writing anything, return an onboarding proposal containing:

1. An exact YAML preview of the proposed registry row and any candidate removal.
2. A file-action table with repository, path, and `create`, `preserve`, `update`, or `defer` for
   every required/recommended path.
3. The proposed initial backlog items and scores, or an explicit zero-item backlog.
4. Validation commands for the target scaffold and the registry change.
5. The staged delivery plan: target scaffold PR (if changes are needed), its required merge point,
   then the `portfolio-prompts` registry PR, then — when the project's `presentation_role` is
   `showcase` or `methodology` — the `portfolio-landing` evidence PR.
6. For a publicly-visible project, the proposed landing presence: its `data/presentation.json` entry
   (public title, discipline, summary, order, group/tags) and which evidence `actions` it will
   carry (`demo`/`report`/`documentation`/`workflow`), or an explicit statement that no public
   evidence link exists yet and the entry ships without one (recorded as a tracked follow-up).
7. Every unresolved choice — especially orchestration participation, gates, deviations, coupling,
   backlog seed items, and any overwrite-like action.

Then **stop for explicit user approval**. Do not create directories, files, branches, commits, or
PRs in the turn that first presents the proposal. Apply the user's corrections and ask again if a
material choice remains unresolved.

## Phase 3 — Prepare the target scaffold PR

After approval, recheck both repositories for intervening changes. If the target already satisfies
the required and approved recommended layout, record that no target PR is needed and continue to
Phase 4. Otherwise:

1. Update the target default branch safely, create a descriptive onboarding branch following that
   repository's convention, and make only the approved scaffold changes.
2. For a new backlog, preserve the shared template's intent while removing instructions and
   placeholders that are not live project content. Use en-GB spelling and the current date.
3. Create approved recommended files from the shared templates. Fill live-document placeholders;
   retain instructional tokens only in reusable `*.template.md` files. Empty directories may exist
   locally, but report when Git cannot carry them in the PR.
4. Run `git diff --check`, scan new live artefacts (excluding intentional `*.template.md` files) for
   unresolved `[REQUIRED: ...]` placeholders, and run the approved project validation. Do not start
   heavyweight infrastructure or live-service tests unless the user explicitly approved them;
   report any skipped gate exactly.
5. Review the complete diff, commit only the onboarding scaffold, push the branch, and open a draft
   PR explaining the contract, evidence, impact, and validation.

Stop after publishing the target PR. The user controls its merge. Do **not** create the registry PR
until the target default branch contains the required backlog and approved scaffold; otherwise a
registry merge could advertise a project that is not yet onboarded.

## Phase 4 — Prepare the registry PR

When the target scaffold is present on its default branch (either originally or after the user
reports the scaffold PR merged), verify that state from fresh local/remote evidence. Then:

1. Refresh `portfolio-prompts` from its default branch and create a descriptive registry branch.
2. Edit the workspace checkout's `portfolio-prompts/registry.yml`: add exactly the approved project
   row in an intentional order and remove only the matching `unregistered_candidates` entry, if
   present.
3. Run `python tools/render-registry.py` from `portfolio-prompts/`. Never hand-edit the generated
   README registry block.
4. Inspect the generated row and run `python tools/check-library.py` plus `git diff --check`. Confirm
   the target folder and resolved backlog path exist and the registry contains no duplicate
   `project` or `github` value.
5. Review the complete diff, commit only the registry/onboarding documentation, push the branch,
   and open a draft PR. Link the merged target scaffold PR when one was required.

Never update handovers, their manifest, or portfolio worklists as part of onboarding. Never merge
the registry PR.

## Phase 5 — Prepare the portfolio-landing evidence PR

This phase exists so that registering a project and publishing it on the portfolio landing page can
never drift apart: a public project must appear on the landing page, and onboarding is where that
link is established. Apply it when the approved `presentation_role` is `showcase` or `methodology`;
skip it only for a `hidden` role, and then say so explicitly in the final report.

Begin only when the registry row is on the `portfolio-prompts` default branch (Phase 4 merged),
because the landing snapshot is derived from that canonical commit. Then, following
`portfolio-landing/docs/generation.md` (its schema is authoritative; never hand-edit generated
output):

1. Refresh `portfolio-landing` from its default branch and create a descriptive evidence branch.
2. Refresh `data/registry-lock.json` from the exact canonical `portfolio-prompts` commit that carries
   the new registry row — never hand-edit it.
3. Add the project's `data/presentation.json` entry keyed by the canonical registry project id:
   public title, discipline, evidence-backed summary, unique `order`, `group` (a showcase's known
   group, or `null` for methodology), tags, and `actions`. Attach an evidence link only to a
   **live, verified** artefact, using the correct action type — `demo` for a genuinely interactive
   browser experience (the only type that gets the play cue), `report` for a static test/evidence
   report, `documentation` for static reference docs, `workflow` for the CI file. If no public
   artefact is live yet, ship the entry with those actions `null` and record the missing evidence
   link as a tracked follow-up in the final report; never invent or point at an unverified URL.
4. Regenerate with `tools/generate_site.py` and run the landing quality gate. Never hand-edit
   `index.html` or other generated output. Confirm the generator's registry-lock ↔ presentation
   parity check passes for the new row.
5. Review the complete diff, commit only the landing evidence change, push the branch, and open a
   draft PR. Link the merged registry PR and state the required merge order.

Never merge the landing PR. Never touch handovers, their manifest, or worklists here either.

## Final report

At each stopping point report:

- identity and contract decisions, including their evidence;
- files created, preserved, updated, or deferred in each repository;
- branches, commits, PR links, and required merge order;
- validation commands and exact results, including skipped checks; and
- unresolved decisions or blockers and the precise resume condition.

Use en-GB spelling. Never report a project as onboarded until its required backlog is on the target
default branch **and** its registry row is on the `portfolio-prompts` default branch. For a
`showcase` or `methodology` project, also report whether its `portfolio-landing` evidence PR is
prepared and, if the landing entry ships without a live evidence link, name that missing link as an
explicit tracked follow-up with its resume condition — so a registered-but-unpublished project is
never left silently drifting.
