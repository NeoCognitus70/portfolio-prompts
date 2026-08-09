---
name: portfolio-reviews-summary
description: "GENERATE, inspect, or refresh the central point of reference for all latest project code reviews across the portfolio in portfolio-reviews/."
---

Generate, inspect, or refresh the central point of reference for all latest project code reviews.

Read and follow the [canonical prompt](../../portfolio-reviews-summary.prompt.md), following the body below its `---` divider exactly.

- Takes **no `PROJECT=`** — it evaluates every showcase project in the bundled [registry](../../registry.yml).
- Resolves the **portfolio root** first, per the bundled [project layout](../../project-layout.md) §"Resolving the portfolio root".
- Uses `python portfolio-prompts/tools/build-portfolio-reviews.py` to regenerate `portfolio-reviews/README.md` and `portfolio-reviews/index.html`.
