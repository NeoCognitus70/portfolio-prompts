---
name: write-project-in-depth-report
description: "Write a versioned Markdown/HTML in-depth report for one registered test-automation-portfolio project: intention, current design and outputs, complete implementation history, current status, and documented or clearly inferred future direction. Use for a descriptive portfolio dossier written outside the target repo; not for a code review or external repository analysis."
---

Write an evidence-based in-depth report for one registered **test-automation-portfolio** project.

Read and follow the [canonical prompt](../../write-project-in-depth-report.prompt.md), following the
body below its `---` divider exactly.

- `PROJECT` is the registered project folder supplied by the user. If none was given, ask; never
  guess.
- Resolve the portfolio root using the bundled [project layout](../../project-layout.md).
- Keep the target project read-only. Write the versioned Markdown/HTML pair only under the
  portfolio-level `portfolio-in-depth-reports/{PROJECT}/` archive (or the user-supplied output root).
- Keep owner-approved/documented future work separate from explicitly labelled inference.
