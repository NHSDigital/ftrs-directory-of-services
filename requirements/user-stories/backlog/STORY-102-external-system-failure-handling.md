---
id: STORY-102
title: External system failure handling
nfr_refs:
  - REL-014
  - REL-002
type: reliability
status: draft
owner: architecture-team
summary: Detect and mitigate failures in mandatory or optional external systems with differentiated strategies.
---

## Description
Introduce controlled failures in integrated external systems (mandatory vs optional). Verify detection, circuit-breaking, retry, fallback, and alerting behaviour adhere to resilience expectations.

## Acceptance Criteria
- Mandatory system failure triggers retries & circuit breaker open state.
- Optional system failure results in silent degrade with user notification only if user-facing.
- Alerting includes system name, failure mode, and impact classification.
- Recovery closes circuit breaker automatically upon success threshold.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| mandatory_system_failure_injection | automated | Retries then breaker trips |
| optional_system_failure_injection | automated | Degraded mode; core unaffected |
| alert_payload_validation | automated | Contains system name & impact |
| breaker_recovery_threshold_test | automated | Breaker closes after success streak |

## Traceability
NFRs: REL-014, REL-002
