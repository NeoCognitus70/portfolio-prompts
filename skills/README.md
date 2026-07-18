# Skills — the portfolio-prompts plugin

This repository is a dual-platform Claude Code and Codex plugin. Every skill delegates to the
canonical `*.prompt.md` at the library root, so the prompt remains the single source of truth while
the skill adds triggering, input handling, UI metadata, and invocation policy.

## Skills

| Skill | Delegates to | Input | Notes |
|---|---|---|---|
| `onboard-project` | `onboard-project.prompt.md` | project, optional GitHub repo | Explicit-only; staged scaffold + registry draft PRs |
| `resume-session` | `resume-session.prompt.md` | project | Start of a session |
| `derive-worklist` | `derive-worklist.prompt.md` | project, optional worklist source | Plan a worklist; no actioning |
| `loop-worklist` | `loop-worklist.prompt.md` | project, optional worklist source | Explicit-only; execute one item per invocation or iteration |
| `write-implementation-log` | `write-implementation-log.prompt.md` | project | After a development task |
| `write-code-review` | `write-code-review.prompt.md` | project | Review an onboarded project |
| `triage-review-findings` | `triage-review-findings.prompt.md` | project and review path | Review findings to approved worklist; no actioning |
| `write-handover` | `write-handover.prompt.md` | project | End of a session |
| `close-project` | `close-project.prompt.md` | project | Explicit-only; final session |
| `derive-all-worklists` | `derive-all-worklists.prompt.md` | optional project list | Fan-out, no actioning |
| `review-all-projects` | `review-all-projects.prompt.md` | optional project list | Explicit-only; evidence artefacts + PRs |
| `loop-all-worklists` | `loop-all-worklists.prompt.md` | optional projects and item cap | Explicit-only, mutating fan-out + confirmation gate |
| `portfolio-status` | `portfolio-status.prompt.md` | optional portfolio root | Whole-portfolio status, strictly read-only |
| `analyze-repo` | `github-repo-analysis-prompt.md` | repo and optional depth | Zero-config; any repo, no registry |

## Install with Claude Code

The repo hosts its Claude Code marketplace at `.claude-plugin/marketplace.json`:

```bash
/plugin marketplace add NeoCognitus70/portfolio-prompts
/plugin install portfolio-prompts@portfolio-prompts
```

For local development, load a checkout directly:

```bash
claude --plugin-dir /path/to/portfolio-prompts
```

Claude Code skills appear namespaced, for example:

```text
/portfolio-prompts:resume-session calculator-screenplay-bdd
/loop /portfolio-prompts:loop-worklist calculator-screenplay-bdd
```

## Install with Codex

The Codex manifest is `.codex-plugin/plugin.json`; the repo-scoped marketplace is
`.agents/plugins/marketplace.json`. Add the repository marketplace, then install the plugin from
its `portfolio-prompts` marketplace:

```bash
codex plugin marketplace add NeoCognitus70/portfolio-prompts
codex plugin add portfolio-prompts@portfolio-prompts
```

For a local checkout, replace the GitHub shorthand in the first command with the absolute checkout
path. Start a new Codex task after installing or updating so the skill list is refreshed.

Invoke Codex skills with `$` mentions:

```text
Use $portfolio-prompts:resume-session for calculator-screenplay-bdd.
Use $portfolio-prompts:loop-worklist to execute the next item for calculator-screenplay-bdd.
Use $portfolio-prompts:portfolio-status to report the current portfolio state.
```

## Invocation policy and mutation gates

Codex-specific UI metadata and policy live in each skill's `agents/openai.yaml`; shared
`SKILL.md` frontmatter stays portable. Codex disables implicit invocation for `onboard-project`,
`loop-worklist`, `loop-all-worklists`, `review-all-projects`, and `close-project` because those
workflows create branches, commits, PRs, or terminal state.

`loop-all-worklists` also has a mandatory platform-neutral confirmation gate before any action,
including preflight, unless the user explicitly invoked that skill in the current turn. This gate
remains the real safeguard: the 2026-07-17 Claude Code probe showed that Claude's former
`disable-model-invocation` flag alone did not prevent model-initiated invocation. The portable
frontmatter therefore omits that ineffective product-specific field.

## Library and portfolio root resolution

- Each skill reaches its prompt, registry, and contract through links relative to its `SKILL.md`.
  The library root is two directories above the skill, so installed Codex cache paths and local
  Claude Code checkouts both work without a product-specific environment variable.
- Resolve the portfolio root once per invocation using `project-layout.md`: an explicit
  `PORTFOLIO_ROOT` wins; otherwise use the library parent when the library is the workspace
  checkout; otherwise search the CWD and its ancestors for the nearest directory containing
  `portfolio-prompts/registry.yml`.
- A Codex plugin cache is not a portfolio workspace. When the library parent does not qualify,
  launch Codex at or inside the portfolio checkout, or supply `PORTFOLIO_ROOT` explicitly.
- Orchestrators pass the absolute library-root prompt path and portfolio working directory to each
  sub-agent. They launch bounded waves that respect the environment's available concurrency.
- Bundled tools locate the library from their own path. Operational prompts invoke them through the
  resolved absolute library root, so their behaviour is independent of the current directory.

`onboard-project` and `close-project` are the exceptions that must publish changes to the library
itself. They require a writable workspace checkout at `<portfolio root>/portfolio-prompts` and
never edit an installed plugin-cache copy.
