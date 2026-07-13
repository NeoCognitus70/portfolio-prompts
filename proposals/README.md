# Proposals — structured registry + skills packaging

Prototype artefacts from the "turn the prompts into portable skills" review. **Nothing here is
wired into the live library yet** — these are drafts for discussion, kept in `proposals/` so they
don't touch the shipping prompts.

Two deliverables:

1. [`registry.yml`](registry.yml) — the prose README registry table, restructured as
   machine-readable data.
2. [`skills/analyze-repo/`](skills/analyze-repo/SKILL.md) — the proof-of-concept skill, distilled
   from [`github-repo-analysis-prompt.md`](../github-repo-analysis-prompt.md).

---

## 1. `registry.yml` — why and how

**Problem it solves.** Every prompt today resolves a project's backlog path, review folder, gates,
and couplings by *parsing English* out of the README table and its prose deviation notes. That is
the collection's chief drift risk and the main blocker to skill portability: a skill can't parse
prose reliably, but it can load a YAML file trivially.

**Design.** One `defaults:` block (mirroring `project-layout.md`) plus one row per project. A row
overrides a default only via its `deviations:` block — so the sudoku POC's `DOCS/.planning/backlog.md`
stops being lore buried in a table cell and becomes a field. Couplings (`couples_with:`), gate
strategy (`gates:`), orchestration membership (`orchestration_target:`), and live-API etiquette
(`live_api:`) are all first-class.

**How a prompt/skill consumes it** (pseudocode):

```
row      = registry.projects[PROJECT]                 # stop + ask if absent
backlog  = row.deviations.backlog ?? defaults.backlog # deviation wins
reviews  = row.deviations.reviews ?? defaults.reviews
gates    = resolve(defaults.gate_cascade, row.gates)  # first-hit-wins, from data not prose
targets  = registry.projects where orchestration_target  # the *-all-* fan-out set
```

**What it fixes from the review**, concretely:
- Weakness #1 (prose registry) — paths become data.
- Weakness #7 (hand-maintained couplings) — `couples_with` makes the coupling check mechanical.
- Weakness #8 (silent drift) — `unregistered_candidates:` lists projects in the workspace but not
  the registry (here: `markdown-renderer`, `orangehrm-pim-automation`), so a self-check can flag them.

**The README stays** — but as a *generated* view. A `refresh-registry` skill/script would render
the table from `registry.yml`, so the human-readable and machine-readable copies can never diverge.
That regenerator is the natural next build after this POC.

---

## 2. `analyze-repo` — the POC skill

Chosen as the proof of concept because it is the **zero-config outlier**: it takes no `PROJECT=`,
reads no registry, and needs no contract — so it isolates the "prompt → skill" mechanics without
also depending on `registry.yml` landing first. If this converts cleanly, the registry-bound
prompts follow the same pattern with one extra step (load the row).

**What changed vs the prompt:**

| `github-repo-analysis-prompt.md` | `analyze-repo/SKILL.md` |
| --- | --- |
| "Paste the text below the `---`, then supply inputs" | `description`-triggered + `argument-hint` — `/analyze-repo <repo> [depth]` |
| Inputs as a fill-in block | Parsed from the invocation args |
| ~260 lines, human-facing preamble | Tightened; section bodies compressed to their contract, acquire-first gate and evidence rules kept verbatim |
| House rules restated | Same en-GB / ASCII / file:line / "never fabricate a CVE" rules |

The **acquire-before-analysing** gate, **depth control**, **evidence rules**, and **section
structure** are preserved — those are the load-bearing parts.

### Try it

A skill is discovered at `.claude/skills/<name>/SKILL.md` in a project (or `~/.claude/skills/`
for all projects, or inside a plugin). To test this POC from the portfolio root:

```bash
# project-scoped (this workspace only)
mkdir -p .claude/skills
cp -r portfolio-prompts/proposals/skills/analyze-repo .claude/skills/

# then, in an interactive Claude Code session:
/analyze-repo https://github.com/<owner>/<repo> depth=standard
```

Or let it auto-trigger: "analyse the repo at <path> for me". Tune the `description:` if triggering
is too eager or too shy — the `skill-creator` skill has eval tooling built for exactly that.

> Note: skill files must live under a `.claude/skills/` (or plugin) directory to be *loaded*.
> Keeping the POC in `proposals/` means it is a **draft on disk, not an active skill** until copied
> — deliberate, so it can't fire before you've reviewed it.

---

## 3. Packaging the rest (sketch, not built)

Once the pattern is proven, ship the whole collection as a **Claude Code plugin**:

```
portfolio-prompts-plugin/
  plugin.json
  skills/
    analyze-repo/SKILL.md          # zero-config (this POC)
    resume-session/SKILL.md        # arg: project
    derive-worklist/SKILL.md       # arg: project [worklist]
    loop-worklist/SKILL.md         # /loop-driven
    write-handover/SKILL.md        # arg: project
    write-impl-log/SKILL.md        # arg: project
    write-code-review/SKILL.md     # arg: project
    close-project/SKILL.md         # arg: project
    derive-all-worklists/SKILL.md  # no arg — reads registry
    loop-all-worklists/SKILL.md    # no arg — explicit-invocation only (mutating; footgun if auto)
    review-all-projects/SKILL.md   # no arg — reads registry
    onboard-project/SKILL.md       # NEW: scaffolds a row + backlog + templates
    refresh-registry/SKILL.md      # NEW: regenerates the README table from registry.yml
  config/
    registry.yml                   # this file's schema, per workspace
    project-layout.md              # the contract, loaded not re-read
  templates/                       # backlog / impl-log / code-review / ADR
```

`project` becomes a skill **argument** across the seven single-project skills; the three fan-outs
take none and read `registry.yml`. To run on **any** project (not just this portfolio), a user
drops the plugin in, runs `onboard-project` once per repo to populate `registry.yml`, and gets the
whole lifecycle as `/`-commands.

**Conversion caveats** (from the review):
- Descriptions do the triggering — the seven single-project skills have overlapping semantics
  ("review", "handover", "log") and need carefully disambiguated descriptions.
- `loop-worklist` stays `/loop`-driven, not description-triggered.
- `loop-all-worklists` (the only mutating fan-out) should be explicit-invocation only.
- Skill bodies want to be leaner than the prompts; centralising paths into `registry.yml` /
  `project-layout.md` does most of that slimming — resist pasting the prompt prose verbatim.
