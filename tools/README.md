# tools/

Maintenance scripts for the prompt library. Both require Python 3 + PyYAML (`pip install pyyaml`)
and are run from the `portfolio-prompts/` directory.

| Script | Purpose | PP |
|---|---|---|
| [`render-registry.py`](render-registry.py) | Generate the README project-registry table from `registry.yml` (the source of truth). Rewrites the block between the README `<!-- REGISTRY:START/END -->` markers. `--check` exits non-zero if the table is stale. | PP-23 |
| [`check-library.py`](check-library.py) | The library's **self-gate**: registry rows map to real folders, no unclassified workspace repo, README table is generated, internal doc links resolve, and the worklist example parses. | PP-15 |
| [`build-handover-manifest.py`](build-handover-manifest.py) | Rebuild `session-notes/manifest.json` (the handover index) by scanning the folder, so readers resolve "latest per project" without re-deriving it from filenames. Run by `write-handover`; `--check` exits non-zero if stale. Writes outside the repo (untracked). | PP-14 |

## The library's verify gate

`python tools/check-library.py` is the gate for `PROJECT=portfolio-prompts` (recorded in its
`registry.yml` row). Run it before committing docs changes to the library:

```bash
python tools/render-registry.py     # if you edited registry.yml
python tools/check-library.py       # must print PASS
```

`check-library.py` runs `render-registry.py --check` internally, so a stale table fails the gate.
In a standalone clone of just this repo (no sibling project checkouts), the cross-repo folder
checks are skipped automatically.
