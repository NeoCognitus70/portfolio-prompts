---
name: write-sut-architecture-report
description: "Write an authoritative, evidence-grounded pedagogical architecture and testability report for a desktop, microservice, dual-surface, or web System Under Test (SUT). Analyses domain models, runtime threading, state management, UIA3/API accessibility surfaces, and Screenplay pattern integration."
---

Write a pedagogical architecture and testability report for a System Under Test (SUT).

Read and follow the [canonical prompt](../../write-sut-architecture-report.prompt.md), following the
body below its `---` divider exactly.

- `SUT_PATH` is the relative path to the SUT project folder (e.g. `src/TradeBlotter.Sut` or `services/`).
- `PROJECT` is the registered project folder supplied by the user (or derived from working directory).
- Keep the target project read-only. Write reports under the portfolio-level `portfolio-pedagogical-reports/` archive.
- Ensure all architectural diagrams use Mermaid with valid syntax and zero raw HTML tags in labels.
