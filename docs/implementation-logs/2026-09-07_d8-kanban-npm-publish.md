# Publish the shared kanban generator as a public npm package (D8) — 2026-09-07

## Session Summary

Turned the in-repo `tools/kanban` generator + drift-gate into a standalone **public npm
package** (`portfolio-kanban-generator`) so downstream project repos can run the gate in
CI via `npx` without vendoring the tool, per decision **D8**. The prompt-library source
repo stays private (`"private": true` at the root); only this one directory is published.
The first release, `1.0.0`, was cut and verified live on the npm registry, and the first
consumer (`auth-separation`) is already building green against it.

---

## Objectives

1. ✅ Give `tools/kanban` its own `package.json` — name, `type:module`, `bin`, `files`
   whitelist (generator + `lib/` + README + LICENSE only), `engines`,
   `publishConfig.access=public`, repository/homepage/bugs.
2. ✅ Confirm zero runtime dependencies (vanilla Node) — none declared.
3. ✅ Provide a package LICENCE (owner decision) — MIT, matching the repo root.
4. ✅ Add a release/publish path — a tag-triggered GitHub Actions workflow, plus a
   documented manual `npm publish` fallback.
5. ✅ Cut the first release and record the exact published name + version.
6. ✅ Keep `node --test` green and the `check-library.py` `check_kanban` /
   `tools/tests` guard intact.

---

## Test Results

| Stack | Suite | Before | After | Status |
|---|---|---|---|---|
| Node | `tools/kanban` generator (`node --test`) | 49/49 | 49/49 | ✅ PASS |
| Python | `tools/check-library.py` self-gate | PASS | PASS | ✅ PASS (`check_kanban` intact) |
| Python | `unittest discover -s tools/tests` (incl. kanban cross-boundary guard) | 24/24 | 24/24 | ✅ PASS |
| npm | `npm pack --dry-run` (published file list) | — | 8 files, 18.3 kB | ✅ whitelist correct |
| npm | `npx portfolio-kanban-generator@1.0.0 --check --dialect auth-table` vs. auth-table fixture | — | exit 0, "in sync" | ✅ PASS |

CI on merge: `check-library` on PR #83 **pass** (10s); `Prompt library integrity` on
`main` after merge **success** (10s); `Publish kanban generator` tag run for
`kanban-v1.0.0` **success**.

---

## Changes Implemented

### Package manifest for `tools/kanban`

**Files changed:**
- `tools/kanban/package.json` (new) — package `portfolio-kanban-generator` `1.0.0`;
  `"type":"module"`; `bin.generate-kanban` → `generate-kanban.mjs`; `engines.node >=18`;
  `publishConfig.access=public`; `repository` (with `directory: tools/kanban`),
  `homepage`, `bugs`. The `files` array whitelists **only** `generate-kanban.mjs`,
  `lib/`, `README.md`, `LICENSE` — `test/` and its fixtures are excluded from the
  tarball (verified with `npm pack --dry-run`: 8 files). A single bin is intentional —
  `npx portfolio-kanban-generator@<version>` runs it even though the bin name differs
  from the package name, which is what the downstream CI invocation relies on.

### Package licence

**Files changed:**
- `tools/kanban/LICENSE` (new) — MIT, copied verbatim from the repo root
  (`Copyright (c) 2026 Gary Brooks`). npm publishes the package-root LICENCE regardless
  of the `files` list, so the tarball now carries its own licence.

### Tag-triggered publish workflow

**Files changed:**
- `.github/workflows/publish-kanban.yml` (new) — triggers on `kanban-v*` tags. Steps:
  verify the tag version equals `package.json` version, run `node --test`, then
  `npm publish --access public` using `NODE_AUTH_TOKEN` from the repo secret
  `NPM_TOKEN`. Zero deps means no install step is needed before publish. The existing
  `library-integrity.yml` is unchanged and still runs on PR/push.

### README publishing guidance

**Files changed:**
- `tools/kanban/README.md` — added the npm/npx usage (pinned `npx …@1.0.0` for CI) and
  a maintainer "Publishing" section documenting the tag-release flow and the manual
  `npm publish` / `npm pack --dry-run` fallback.

---

## Technical Decisions

| Decision | Rationale | Alternatives rejected |
|---|---|---|
| Unscoped name `portfolio-kanban-generator` | Works with any single npm account — lowest friction while the npm account was still an owner prerequisite; descriptive; name was free on the registry | Scoped `@neocognitus70/…` (requires an npm org/user of that name to exist first); shorter `portfolio-kanban` (less self-describing) |
| Version `1.0.0` for the first release | The CLI contract (`--check --dialect auth-table …`) is stable and tested, and a downstream consumer pins it — a 1.0 signals that stability | `0.1.0` (understates the committed, depended-upon contract) |
| Licence: MIT | The repo root already declared MIT (Gary Brooks); reused it rather than introducing a new licence decision | Adding a different OSI licence (would have been a fresh owner decision with no cause) |
| Publish via tag-triggered CI (`NPM_TOKEN` secret) with a manual fallback documented | Repeatable, auth held in a secret, tag/version guard prevents mismatched releases | Manual-only publish (not repeatable, easy to forget the file whitelist / `--access public`) |
| npm token: granular access token, "All Packages" + Read-and-write + Bypass-2FA for the first release | A granular token cannot be scoped to a package that does not exist yet, so the first publish needs All-Packages; bypass-2FA is required because CI cannot answer an OTP | Classic Automation token (viable, no expiry — kept as the documented alternative); package-scoped granular token (only possible after 1.0.0 exists — noted as the post-release hardening step) |

No new ADR was created: the render-stack and generator-design decisions already live in
`tools/kanban/DECISION-render-stack.md`, and D8 is a packaging/release decision recorded
in this log rather than a structural change to the library's own architecture.

---

## Documentation Updates

- `tools/kanban/README.md` — npm/npx usage + maintainer "Publishing" section (above).
- `tools/kanban/package.json`, `tools/kanban/LICENSE`, `.github/workflows/publish-kanban.yml`
  — new files (listed under Changes Implemented).
- `docs/backlog.md` — **not** updated: the PP backlog is at zero outstanding
  (PP-00..PP-35 resolved) and this work belongs to the cross-portfolio kanban
  programme (D-decisions / T-tasks), not a PP item.

---

## Lessons Learned

- **`files` + `npm pack --dry-run` is the reliable way to prove the tarball excludes
  test fixtures.** Relying on `.npmignore` or assumptions is error-prone; the dry-run
  gives an exact file list to check against the intended whitelist.
- **A single `bin` whose name differs from the package name still works via `npx <pkg>`**
  — npm runs the sole bin regardless of its name, so the downstream
  `npx portfolio-kanban-generator@1.0.0 …` invocation needed no bin-name gymnastics.
- **First-publish scoping caveat for granular npm tokens:** you cannot scope a token to
  a package that does not exist yet, so release #1 requires an All-Packages token (or a
  classic Automation token); tighten to a package-scoped token only after the package
  exists.
- **Publishing is genuinely out of a session's hands.** The build/wiring was fully
  preparable, but `npm publish` needed the owner's credentials and an explicit
  go-ahead; the value this session could add unattended was staging everything and
  making the exact blockers and steps explicit in the PR.
- **A public package off a private repo** is cleanly expressed by the root staying
  `"private": true` and the subdirectory carrying its own manifest — no repo split
  required.

---

## Recommendations / Next Steps

- [x] Publish `portfolio-kanban-generator@1.0.0` and verify it live — done
      (`npm view` → 1.0.0; npx smoke test exit 0).
- [x] Downstream adoption by `auth-separation` — done (PR #22 merged, squash `066e883`;
      CI green; consumes the pinned package via `npx`, no vendoring).
- [ ] After 1.0.0, rotate `NPM_TOKEN` to a **granular token scoped to
      `portfolio-kanban-generator`** (Read-and-write) for least privilege on subsequent
      releases — owner, LOW.
- [ ] For any future generator change, bump `tools/kanban/package.json` and cut a new
      `kanban-v<version>` tag; downstream consumers pin exact versions, so a new release
      is required for them to pick up changes — maintainer, as-needed.

---

*Session logged: 2026-09-07. Author: Claude Code.*
