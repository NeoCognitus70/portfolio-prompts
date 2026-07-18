---
name: onboard-project
description: "ONBOARD an existing unregistered local repository into the test-automation portfolio. Propose and confirm its registry metadata, backlog, gates, and scaffold; then publish staged target-repo and registry draft PRs without merging. MUTATING and explicit-only; not for creating/cloning a repo or repairing an existing registry member."
---

Onboard one existing local repository into the portfolio through staged, user-approved PRs.

Read and follow the [canonical prompt](../../onboard-project.prompt.md), following the body below
its `---` divider exactly.

- `PROJECT` is the prospective local folder name; it must not already be a registry row. Ask if it
  is missing.
- `GITHUB=<owner/repo>` is optional only when the target checkout's `origin` is unambiguous.
- First present the evidence-backed proposal and stop. Publish the target scaffold PR after
  approval, wait for its merge when required, then publish the registry PR. Never merge either PR.
- Resolve the **portfolio root** first, per the bundled [project layout](../../project-layout.md)
  §"Resolving the portfolio root" — an explicit `PORTFOLIO_ROOT=<path>` argument wins, else the
  library-parent, else the nearest qualifying CWD/ancestor; all portfolio-relative paths resolve
  against it.
