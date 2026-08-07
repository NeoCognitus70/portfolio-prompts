# Agent Skills Specification & Portfolio Compliance Report

**Document Location:** `portfolio-prompts/docs/agentskills-specification-compliance.md`  
**Specification Source:** [https://agentskills.io/specification](https://agentskills.io/specification)  
**Audit Target:** `portfolio-prompts/skills/` (15 skills)  
**Audit Date:** 2026-08-07  
**Overall Status:** **100% COMPLIANT**

---

## 1. Overview & Purpose

This document records the audit findings for all skills packaged in `portfolio-prompts/skills/` against the official **Agent Skills format specification** ([https://agentskills.io/specification](https://agentskills.io/specification)).

It also serves as the **authoritative compliance guide for future skills** added to `portfolio-prompts` or any other repository in this portfolio. Every future skill must strictly satisfy the mandatory rules detailed below.

---

## 2. Mandatory Specifications for Agent Skills

Any current or future skill created within `portfolio-prompts/skills/` (or imported into the portfolio) **MUST** meet all of the following specification requirements.

### 2.1 Directory Structure

A skill must be a standalone directory containing, at minimum, a `SKILL.md` file:

```text
skills/
└── <skill-name>/
    ├── SKILL.md          # Required: YAML frontmatter + Markdown instructions
    ├── scripts/          # Optional: executable scripts (Python, Bash, JS, etc.)
    ├── references/       # Optional: deep reference documentation loaded on demand
    └── assets/           # Optional: static templates, schemas, or resource files
```

* The skill instructions must be located at `skills/<skill-name>/SKILL.md`.
* Supplementary content should use `scripts/`, `references/`, or `assets/` to leverage progressive disclosure.

---

### 2.2 Directory & Skill Naming (`name`)

The `name` property defines the skill identifier and must conform strictly to the following format constraints:

1. **Character Set:** Lowercase ASCII letters (`a-z`), numbers (`0-9`), and single hyphens (`-`) ONLY.
   * ❌ No uppercase letters (`A-Z`)
   * ❌ No underscores (`_`), spaces, dots, or special characters
2. **Hyphen Rules:**
   * ❌ Must NOT start with a hyphen (e.g. `-my-skill`)
   * ❌ Must NOT end with a hyphen (e.g. `my-skill-`)
   * ❌ Must NOT contain consecutive hyphens (e.g. `my--skill`)
3. **Length:** Must be between 1 and 64 characters long.
4. **Directory Name Match (CRITICAL):** The `name` string in `SKILL.md` frontmatter **MUST MATCH THE PARENT DIRECTORY NAME EXACTLY**.
   * Example: `skills/analyze-repo/SKILL.md` MUST have `name: analyze-repo`.

---

### 2.3 `SKILL.md` Frontmatter Format

`SKILL.md` MUST begin with YAML frontmatter starting on line 1 with `---` and ending with `---` before the Markdown body.

#### Frontmatter Fields Table

| Field | Required | Max Length | Specification & Constraints |
|---|---|---|---|
| `name` | **Yes** | 64 chars | Lowercase `a-z`, `0-9`, `-` only. Must match parent directory name. |
| `description` | **Yes** | 1024 chars | Non-empty string. Must describe **what** the skill does AND **when/how** to activate it. |
| `license` | No | Short string | License name or reference to a bundled license file. |
| `compatibility` | No | 500 chars | Specifies environment requirements (e.g. CLI tools, OS, product limits). |
| `metadata` | No | Key-value map | Arbitrary string key to string value map for custom client extensions. |
| `allowed-tools` | No | Short string | Space-separated list of pre-approved tools (experimental). |

> [!IMPORTANT]
> **No Custom Top-Level Fields:** Frontmatter top-level keys must only be those defined by the Agent Skills specification (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`). Custom properties should be stored under the `metadata:` key-value map.

---

### 2.4 Markdown Body & Progressive Disclosure

1. **Keep `SKILL.md` Concise:** Main `SKILL.md` files should ideally remain under **500 lines** (~5000 tokens) so agent contexts are not bloated upon activation.
2. **Progressive Disclosure:**
   * **Level 1 (Startup):** Agent loads `name` and `description` (~100 tokens).
   * **Level 2 (Activation):** Agent loads full `SKILL.md` body when activated.
   * **Level 3 (Execution):** Agent reads `references/` or executes `scripts/` only as needed.
3. **File Reference Paths:** Reference other files using relative paths from the skill root (e.g. `[Reference Guide](references/GUIDE.md)` or `scripts/run.py`).

---

## 3. Portfolio Audit Findings (`portfolio-prompts/skills/`)

All 15 skills in `portfolio-prompts/skills/` were audited against the specification rules above.

### 3.1 Audit Summary Table

| Skill Directory | `name` in YAML | Name Match | `description` Length | Line Count | Status |
|---|---|---|---|---|---|
| [`analyze-repo`](../skills/analyze-repo/SKILL.md) | `analyze-repo` | ✅ Match | 488 chars | 16 lines | **COMPLIANT** |
| [`close-project`](../skills/close-project/SKILL.md) | `close-project` | ✅ Match | 409 chars | 21 lines | **COMPLIANT** |
| [`derive-all-worklists`](../skills/derive-all-worklists/SKILL.md) | `derive-all-worklists` | ✅ Match | 352 chars | 21 lines | **COMPLIANT** |
| [`derive-worklist`](../skills/derive-worklist/SKILL.md) | `derive-worklist` | ✅ Match | 414 chars | 22 lines | **COMPLIANT** |
| [`loop-all-worklists`](../skills/loop-all-worklists/SKILL.md) | `loop-all-worklists` | ✅ Match | 456 chars | 30 lines | **COMPLIANT** |
| [`loop-worklist`](../skills/loop-worklist/SKILL.md) | `loop-worklist` | ✅ Match | 335 chars | 23 lines | **COMPLIANT** |
| [`onboard-project`](../skills/onboard-project/SKILL.md) | `onboard-project` | ✅ Match | 334 chars | 20 lines | **COMPLIANT** |
| [`portfolio-status`](../skills/portfolio-status/SKILL.md) | `portfolio-status` | ✅ Match | 215 chars | 19 lines | **COMPLIANT** |
| [`resume-session`](../skills/resume-session/SKILL.md) | `resume-session` | ✅ Match | 438 chars | 20 lines | **COMPLIANT** |
| [`review-all-projects`](../skills/review-all-projects/SKILL.md) | `review-all-projects` | ✅ Match | 411 chars | 22 lines | **COMPLIANT** |
| [`run-project-cycle`](../skills/run-project-cycle/SKILL.md) | `run-project-cycle` | ✅ Match | 584 chars | 29 lines | **COMPLIANT** |
| [`triage-review-findings`](../skills/triage-review-findings/SKILL.md) | `triage-review-findings` | ✅ Match | 209 chars | 20 lines | **COMPLIANT** |
| [`write-code-review`](../skills/write-code-review/SKILL.md) | `write-code-review` | ✅ Match | 387 chars | 21 lines | **COMPLIANT** |
| [`write-handover`](../skills/write-handover/SKILL.md) | `write-handover` | ✅ Match | 394 chars | 21 lines | **COMPLIANT** |
| [`write-implementation-log`](../skills/write-implementation-log/SKILL.md) | `write-implementation-log` | ✅ Match | 364 chars | 21 lines | **COMPLIANT** |

---

### 3.2 Key Compliance Highlights

* **100% Directory-to-Name Parity:** Every `name:` in frontmatter matches its parent directory name exactly.
* **100% Valid Name Character Format:** All names consist purely of lowercase alphanumeric characters and single hyphens.
* **Rich & Scoped Descriptions:** All descriptions are between 209 and 584 characters long (well under the 1024 character max limit) and include clear operational trigger instructions.
* **Minimalist Body Size:** All 15 `SKILL.md` files are concise (16 to 30 lines total), delegating implementation details to canonical prompt files (`../../<prompt>.prompt.md`) via relative links to maintain progressive disclosure.
* **Zero Non-Standard Frontmatter Keys:** No unrecognised or custom top-level frontmatter keys exist.

---

## 4. Pre-Commit Validation Checklist for Future Skills

Before committing any new or modified skill to `portfolio-prompts/skills/`, run through this checklist:

- [ ] **Directory Name:** `skills/<skill-name>/` is lowercase alphanumeric + hyphens only (`^[a-z0-9]+(-[a-z0-9]+)*$`), max 64 chars.
- [ ] **`SKILL.md` Location:** File exists at `skills/<skill-name>/SKILL.md`.
- [ ] **Frontmatter Delimiters:** Starts on line 1 with `---` and closes with `---`.
- [ ] **`name` Field:** Matches parent directory name exactly.
- [ ] **`description` Field:** Non-empty, 1–1024 characters, explicitly states capability and activation triggers.
- [ ] **Frontmatter Keys:** Only standard keys (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`) used.
- [ ] **Body Length:** Under 500 lines. Heavy documentation split into `references/` or linked prompts.
