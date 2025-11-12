---
id: STORY-088
title: Enforce UK geo-IP access restriction
nfr_refs:
  - AVAIL-009
  - SEC-008
type: availability
status: draft
owner: platform-team
summary: Restrict FtRS UI and API access to authenticated UK IP ranges as first-line defence.
---

## Description
Implement geo-IP filtering; maintain allowlist of UK IP ranges; authenticate users & services; log & alert on non-UK access attempts.

## Acceptance Criteria
- Geo-IP filter configuration committed & versioned.
- Attempted access from non-UK IP blocked & logged.
- Weekly audit shows zero successful non-UK accesses.
- Alert delivered on repeated non-UK attempts (≥3 in 10 min).

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| non_uk_access_attempt | automated | Blocked & logged |
| weekly_audit_report | manual | Zero successful non-UK entries |
| repeated_attempts_alert_test | automated | Alert after threshold |
| config_versioning_check | manual | Config file versioned |

## Traceability
NFRs: AVAIL-009, SEC-008
