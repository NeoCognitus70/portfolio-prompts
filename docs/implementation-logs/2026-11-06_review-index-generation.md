# Review index generation — 6 November 2026

Implemented the tooling prerequisite for landing plan LAND-18. The central generator now writes only its selected output directory, exposes a non-writing check, retains parallel bundles and focused records, resolves summary links, and emits a public HTML/manifest pair with published source commits. The internal pair retains complete registry coverage.

Validation: `python -B tools/check-library.py` passed in this standalone clone (cross-repository folder and handover checks explicitly skipped). Six dedicated Git-fixture tests passed in 18.272 seconds. A workspace generation produced 15 public project summaries, 18 indexed bundles and six focused records for the inclusive 2026-10-01 window. Product code, findings and audit exceptions were not changed. Central and landing publication follow in their owning repositories.
