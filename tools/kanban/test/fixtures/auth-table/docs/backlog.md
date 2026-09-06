# Demo backlog (auth-table dialect fixture)

Prose and summary tables sit alongside the ticket table; the adapter must ignore
them and read only the seven-column ticket rows.

## Summary (must be ignored — wrong shape / not backticked ids)

| Priority | Count | Done |
|---|---|---|
| P0 | 3 | 1 |

## Phase 0

| ID | Ticket | Type | Priority | Tier | Blocked by | Status |
|---|---|---|---|---|---|---|
| `DEMO-001` | Set up the thing | Foundation | P0 | HIGH | — | ✅ **Done** 2026-09-01 |
| `DEMO-002` | Out-of-scope extra | Infrastructure | P0 | HIGH | `DEMO-001` | Parked — out of scope under `ADR-0001` |
| `DEMO-003` | Build on the thing | Feature | P0 | HIGH | `DEMO-001` | Backlog |
| `DEMO-004` | Depends on unfinished work | Feature | P1 | MEDIUM | `DEMO-003` | Backlog |
| `DEMO-005` | Standalone task | Feature | P2 | LOW | — | Backlog |
| `DEMO-006` | Claims ready but is blocked | Test | P1 | MEDIUM | `DEMO-004` | Ready — awaiting start |

A closure-record line that is NOT a ticket row (only three cells):

| `DEMO-001` | closed | 2026-09-01 |
