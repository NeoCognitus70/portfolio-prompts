# Prompt — Portfolio Code Reviews Summary

Use this prompt to generate, inspect, or refresh the central point of reference for all latest project code reviews across the portfolio — or invoke it without pasting:
`Read and follow portfolio-prompts/portfolio-reviews-summary.prompt.md`.

It takes no `PROJECT=` parameter because it evaluates every showcase project registered in `registry.yml`.

---

You are managing or inspecting the **central point of reference for portfolio code reviews** located at `portfolio-reviews/`.

## Step 0 — Purpose & Overview

The purpose of `portfolio-reviews/` is to provide a single point of reference at the portfolio root (`portfolio-reviews/README.md` and `portfolio-reviews/index.html`) to:
1. Quickly view the executive summary findings of the latest code review for each registered project.
2. Provide direct relative links to drill down into the full review index (`00_*.md`) and executive summary document (`01_EXECUTIVE_SUMMARY.md`) for any project.

## Step 1 — Inspection / Audit

To view current review findings:
1. Read `portfolio-reviews/README.md` (or open `portfolio-reviews/index.html`).
2. Verify that every active or resting showcase project in `registry.yml` has its latest code review represented.

## Step 2 — Regeneration / Maintenance

When new code reviews are added to any project, or to refresh the summary files:
1. Execute the generator script:
   ```bash
   python portfolio-prompts/tools/build-portfolio-reviews.py
   ```
2. Verify that both `portfolio-reviews/README.md` and `portfolio-reviews/index.html` were created/updated successfully.
3. Verify that relative links correctly point to each project's latest `CODE_REVIEW_*` bundle.

## Step 3 — Report Findings

Summarize the results of the review index update or report:
- Total projects summarized.
- Latest review version and date per project.
- Confirmation that relative drill-down links are valid.
