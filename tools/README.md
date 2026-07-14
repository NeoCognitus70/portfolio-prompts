# tools/

Maintenance scripts for the prompt library, run from the `portfolio-prompts/` directory. All use
Python 3; `render-registry.py` and `check-library.py` additionally require PyYAML
(`python -m pip install PyYAML`).

| Script | Purpose | PP |
|---|---|---|
| [`render-registry.py`](render-registry.py) | Generate the README project-registry table from `registry.yml` (the source of truth). Rewrites the block between the README `<!-- REGISTRY:START/END -->` markers. `--check` exits non-zero if the table is stale. | PP-23 |
| [`check-library.py`](check-library.py) | The library's **self-gate**: registry/classification safety, generated README, links, working norms, invocation paths, worklist format, and deterministic preflight scenarios. | PP-15, PP-17, PP-18, PP-25 |
| [`build-handover-manifest.py`](build-handover-manifest.py) | Rebuild `session-notes/manifest.json` (the handover index) by scanning the folder, so readers resolve "latest per project" without re-deriving it from filenames. Run by `write-handover`; `--check` exits non-zero if stale. The root repository tracks the handover pairs but deliberately ignores this generated manifest. | PP-14 |
| [`workspace_preflight.py`](workspace_preflight.py) | Read-only registry-driven safety report for orchestration: checkout presence/state, upstream/ahead/behind, backlog, gates, latest handover pair, and advisory freshness against the already-fetched default head. | PP-25 / portfolio P-06 |

## Workspace preflight

Run from the portfolio root before any orchestration fan-out:

```bash
python portfolio-prompts/tools/workspace_preflight.py
python portfolio-prompts/tools/workspace_preflight.py --projects=project-a,project-b
python portfolio-prompts/tools/workspace_preflight.py --json
```

The command reads `registry.yml` and selects only rows with `orchestration_target: true`; it never
maintains a second project list. It reads local files and already-fetched Git refs only. It never
fetches, pulls, switches, resets, cleans, stages, or changes any checkout.

- `READY`: current, structurally complete local evidence.
- `WARN`: readable evidence with a qualification such as behind/ahead, topic branch, missing or
  stale handover. Fan-outs may proceed and must report the warning.
- `BLOCKED`: unsafe/incomplete evidence such as a missing checkout/backlog, unreadable Git state,
  or dirty tree. Fan-outs exclude and report that target.

Exit `0` means no target blockers, `1` means at least one blocked target, and `2` means the
registry/invocation itself could not be evaluated. `--json` emits the same fields for automation.

## The library's verify gate

`python tools/check-library.py` is the gate for `PROJECT=portfolio-prompts` (recorded in its
`registry.yml` row). Run it before committing docs changes to the library:

```bash
python tools/render-registry.py     # if you edited registry.yml
python tools/check-library.py       # must print PASS
```

`check-library.py` runs `render-registry.py --check` and the deterministic workspace-preflight
scenario suite internally, so a stale table or a preflight regression fails the gate.
In a standalone clone of just this repo (no sibling project checkouts), the cross-repo folder
checks are skipped automatically.

The same gate runs in `.github/workflows/library-integrity.yml` for pull requests and pushes to
`main`, with read-only repository permissions.
