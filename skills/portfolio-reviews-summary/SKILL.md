---
name: portfolio-reviews-summary
description: "GENERATE, inspect, or refresh the central point of reference for all latest project code reviews across the portfolio in portfolio-reviews/."
---

Generate, inspect, or refresh the central point of reference for all latest project code reviews.

Read and follow the [canonical prompt](../../portfolio-reviews-summary.prompt.md), following the body below its `---` divider exactly.

- Takes **no `PROJECT=`** — it evaluates every registered project, including methodology and internal hidden-project coverage in the bundled [registry](../../registry.yml).
- Resolves the **portfolio root** first, per the bundled [project layout](../../project-layout.md) §"Resolving the portfolio root".
- Uses `<LIBRARY_ROOT>/tools/build-portfolio-reviews.py` with explicit `--portfolio-root`, `--registry`, `--output-dir` and `--since` arguments, then non-writing `--check`. Produces the internal pair and filtered public HTML/manifest; never changes sibling landing files.
