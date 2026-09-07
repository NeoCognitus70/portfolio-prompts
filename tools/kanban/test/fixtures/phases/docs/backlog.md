# Phased backlog (auth-table phase-derivation fixture — D7)

A ticket row appearing BEFORE any Phase heading must get no phase. Phase numbers
below are deliberately non-contiguous (0, 3, 7) and the heading levels are mixed
(`###` and `##`) to prove the adapter reads the heading's number, not a running
counter, and accepts any heading depth.

| ID | Ticket | Type | Priority | Tier | Blocked by | Status |
|---|---|---|---|---|---|---|
| `PRE-001` | Orphan before any phase | Feature | P0 | HIGH | — | Backlog |

### Phase 0 — Foundations (2 tickets)

| ID | Ticket | Type | Priority | Tier | Blocked by | Status |
|---|---|---|---|---|---|---|
| `P0-001` | First foundation | Foundation | P0 | HIGH | — | ✅ **Done** 2026-09-01 |
| `P0-002` | Second foundation | Infrastructure | P0 | HIGH | `P0-001` | Backlog |

### Phase 3 — Core implementation (3 tickets)

| ID | Ticket | Type | Priority | Tier | Blocked by | Status |
|---|---|---|---|---|---|---|
| `P3-001` | Core one | Feature | P0 | HIGH | — | Backlog |
| `P3-002` | Core two | Feature | P1 | MEDIUM | `P3-001` | Backlog |
| `P3-003` | Core three | Test | P2 | LOW | — | Backlog |

## Phase 7 — Production readiness (1 ticket)

| ID | Ticket | Type | Priority | Tier | Blocked by | Status |
|---|---|---|---|---|---|---|
| `P7-001` | Launch | Feature | P0 | HIGH | — | Backlog |
