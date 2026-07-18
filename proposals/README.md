# Proposals — structured registry + skills packaging (both shipped)

This folder held the prototypes from the "turn the prompts into portable skills" review. **Both have
now shipped into the live library**, so this folder is historical — it records the design rationale;
the real artefacts live at the repo root.

| Proposal | Shipped as | Item |
|---|---|---|
| Structured registry (`registry.yml`) | [`../registry.yml`](../registry.yml) + generated README table ([`../tools/render-registry.py`](../tools/render-registry.py)) | PP-13, PP-23 |
| Skills / plugin pack | [`../.claude-plugin/plugin.json`](../.claude-plugin/plugin.json) + [`../.codex-plugin/plugin.json`](../.codex-plugin/plugin.json) + [`../skills/`](../skills/README.md) (14 skills) | PP-24 + Codex compatibility |

---

## 1. `registry.yml` — why and how (design notes)

**Problem it solved.** Every prompt used to resolve a project's backlog path, review folder, gates,
and couplings by *parsing English* out of the README table — the collection's chief drift risk and
the main blocker to skill portability. A skill can't parse prose reliably, but it can load a YAML file.

**Design.** One `defaults:` block (mirroring `project-layout.md`) plus one row per project. A row
overrides a default only via its `deviations:` block. Couplings (`couples_with:`), gate strategy
(`gates:`), orchestration membership (`orchestration_target:`), and live-API etiquette (`live_api:`)
are all first-class. A skill resolves a row with:

```
row      = registry.projects[PROJECT]                 # stop + ask if absent
backlog  = row.deviations.backlog ?? defaults.backlog # deviation wins
gates    = resolve(defaults.gate_cascade, row.gates)  # first-hit-wins, from data not prose
targets  = registry.projects where orchestration_target  # the *-all-* fan-out set
```

The README table is now a **generated** view of this file (`tools/render-registry.py`), so the
human-readable and machine-readable copies cannot diverge. `tools/check-library.py` gates it.

## 2. Skills / plugin pack — how it landed

Each prompt became a **thin delegating skill** (`skills/<name>/SKILL.md`) that reads and follows its
canonical `*.prompt.md`, so the prompt stays the single source of truth and the skill only adds a
portable `name`/`description` trigger. Codex UI metadata and implicit-invocation policy live in each
skill's `agents/openai.yaml`. `analyze-repo` was the zero-config pilot — no `PROJECT`, registry, or
contract — so it runs against any repo unchanged. See
[`../skills/README.md`](../skills/README.md) for the full list, dual-platform install steps, and
library/portfolio root resolution.

`onboard-project` subsequently shipped. A separate `refresh-registry` skill was superseded by
`tools/render-registry.py`.
