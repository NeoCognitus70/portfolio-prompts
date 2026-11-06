# Prompt — Portfolio Code Reviews Summary

Use this prompt to generate, inspect, or refresh the central point of reference for all latest project code reviews across the portfolio — or invoke it without pasting:
`Read and follow portfolio-prompts/portfolio-reviews-summary.prompt.md`.

It takes no `PROJECT=` parameter because it evaluates every project registered in `registry.yml`.

---

You are managing or inspecting the **central point of reference for portfolio code reviews** located at `portfolio-reviews/`.

## Step 0 — Purpose & Overview

The purpose of `portfolio-reviews/` is to provide a single point of reference at the portfolio root (`portfolio-reviews/README.md` and `portfolio-reviews/index.html`) to:
1. Quickly view the executive summary findings of the latest code review for each registered project.
2. Provide direct relative links to drill down into the full review index (`00_*.md`) and executive summary document (`01_EXECUTIVE_SUMMARY.md`) for any project.

## Step 1 — Inspection / Audit

To view current review findings:
1. Read `portfolio-reviews/README.md` (or open `portfolio-reviews/index.html`).
2. Verify that every showcase or methodology project in `registry.yml` has its latest code review represented.

## Step 2 — Regeneration / Maintenance

When reviews are added, resolve `LIBRARY_ROOT` and `PORTFOLIO_ROOT` separately. Use the canonical registry and already-fetched default-branch refs. Never change or publish target-project files as part of indexing.

1. Install pinned development dependencies from `<LIBRARY_ROOT>/requirements-dev.txt`.
2. Run with explicit paths (choose the inclusive archive date deliberately):
   ```bash
   python <LIBRARY_ROOT>/tools/build-portfolio-reviews.py --portfolio-root <PORTFOLIO_ROOT> --registry <LIBRARY_ROOT>/registry.yml --output-dir <OUTPUT_DIR> --since 2026-10-01
   python <LIBRARY_ROOT>/tools/build-portfolio-reviews.py --portfolio-root <PORTFOLIO_ROOT> --registry <LIBRARY_ROOT>/registry.yml --output-dir <OUTPUT_DIR> --since 2026-10-01 --check
   ```
3. Inspect all four outputs: internal `README.md` and `index.html`, public `public-index.html` and `public-manifest.json`. The public export includes showcase and methodology entries only, excludes local-only reviews, and pins links to captured default-branch commits. Internal links remain relative to `portfolio-reviews/` at the workspace root.
4. Verify latest-summary selection, all parallel bundles since the selected date, focused records and explicit coverage gaps. Review grades are attributed judgements, not current quality guarantees.
5. Check drill-down targets and hidden-project exclusion. A missing checkout, unresolved summary link or unpublished linked source is an error; do not silently replace it with a guessed URL.
6. The generator writes only its selected output directory; `--check` writes nothing. It never writes sibling landing files. Merge the central outputs before a separately authorised landing import pins their exact source commit. The landing site owns its snapshot and navigation.

## Step 3 — Report Findings

Summarize the results of the review index update or report:
- Total projects summarized.
- Latest review version and date per project.
- Confirmation that relative drill-down links are valid.
