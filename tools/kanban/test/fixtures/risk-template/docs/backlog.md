<!--
  Fixture for the shipping `risk-block` template dialect. Deliberately covers, in one file:
  the canonical item heading, both real-world heading variants seen in the portfolio
  (a review-qualified number and an explicit id), body extraction, the resolved section,
  and prose `####` headings that must NEVER become cards.
-->

# Demo Project — Backlog

**Version:** 3 — template-dialect fixture.
**Last Updated:** 2026-09-08

**Priority Scoring System:**
- **Score = Security Impact (0–10) + Breakage Probability (0–10) + Maintenance Burden (0–10)**
- **HIGH (20–30):** Critical — immediate action required
- **MEDIUM (10–19):** Important — schedule within current sprint cycle
- **LOW (0–9):** Desirable — schedule when capacity allows

---

## Outstanding Risks

### HIGH Priority (Score: 20–30)

#### Risk #1: Credentials written to the application log — Score: 24

**Priority Score:** Security Impact (10) + Breakage Probability (7) + Maintenance Burden (7) = **24 points**
**Impact:** Secrets are recoverable from retained log archives.
**Effort:** 4h
**Status:** IN PROGRESS
**Affected Stacks:** api

**Problem:**
The request logger serialises the whole payload, so login requests persist the
plaintext password into the shared log sink.

**Impact Analysis:**
- **Security (10/10):** credentials are readable by anyone with log access.
- **Breakage (7/10):** redaction touches a hot path used by every route.
- **Maintenance (7/10):** the logger is duplicated across three services.

**Refactor Strategy:**
Introduce a redaction allowlist in the shared logger and cover it with a test.

**Success Criteria:**
- [ ] Password and token fields are redacted before serialisation.
- [ ] A regression test asserts no credential reaches the sink.

#### Risk #2 (review #1): Login endpoint has no rate limiting — Score: 21

**Status:** READY TO START

**Problem:**
Repeated failed logins are neither throttled nor locked out.

**Success Criteria:**
- [ ] Failed attempts are throttled per account and per source address.

### MEDIUM Priority (Score: 10–19)

#### Risk PBR-07: Backup restore has never been drilled — Score: 12

**Status:** BLOCKED

**Problem:**
Backups are taken nightly but a restore has never been executed, so recovery
time is unmeasured.

**Success Criteria:**
- [ ] A restore drill is executed against a scratch environment.
- [ ] Measured recovery time is recorded in the runbook.

### LOW Priority (Score: 0–9)

#### Risk #4: Dependency audit is overdue — Score: 6

**Status:** COMPLETE

**Problem:**
The scheduled dependency audit has not run for two quarters.

---

## Delivery notes

These `####` headings are prose, not risks. A dialect that turned any `####`
heading into a card would emit phantom tickets here — they carry no `Score:`
and sit outside the resolved section, so they must be ignored.

#### Out of scope

Anything touching the billing service.

#### Implementation acceptance criteria

Covered by the per-risk success criteria above.

#### Validation and closure criteria

The suite must be green before closure.

---

### Resolved Risks

#### Session cookie missing the Secure attribute ✅ Resolved 2026-08-07

**Resolution:** The cookie is now issued with Secure and SameSite=Lax.
**See:** commit 1a2b3c4
