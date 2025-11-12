---
id: STORY-119
title: Infrastructure logs forwardable to central SIEM
nfr_refs:
  - OBS-016
  - OBS-015
type: observability
status: draft
owner: security-team
summary: Forward infrastructure logs to central SIEM for threat monitoring.
---

## Description
Configure reliable, secure forwarding pipeline sending infra logs to SIEM with delivery guarantees and field mapping.

## Acceptance Criteria
- Test event appears in SIEM within 60s.
- Forwarding failures retried with backoff; backlog monitored.
- Secure transport (TLS) enforced.
- Field mapping consistent; schema validation passes.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| test_event_forwarding | automated | Appears <60s |
| forwarding_failure_simulation | automated | Retries logged |
| tls_enforcement_check | automated | TLS required |
| schema_mapping_validation | automated | Pass |

## Traceability
NFRs: OBS-016, OBS-015
