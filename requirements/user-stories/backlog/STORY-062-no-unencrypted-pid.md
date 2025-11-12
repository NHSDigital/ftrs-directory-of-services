---
id: STORY-062
title: Prevent unencrypted PID exposure via APIs
nfr_refs:
  - SEC-026
  - SEC-025
type: security
status: draft
owner: platform-team
summary: Ensure external API responses never include unencrypted PID fields and enforce mutual TLS where required.
---

## Description
Scan API specifications and runtime responses to ensure PID fields are either absent or encrypted; validate mutual TLS for PID endpoints.

## Acceptance Criteria
- API contract review shows no plaintext PID fields.
- Runtime response sampling reveals no unencrypted PID.
- Mutual TLS enforced for PID endpoints; non-mTLS rejected.
- Monitoring alerts on unexpected PID leakage attempt.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| api_contract_pid_scan | automated | No unencrypted PID fields |
| response_sampling_check | automated | No PID leakage detected |
| pid_endpoint_mtls_enforcement | automated | Non-mTLS attempt rejected |
| leakage_alert_simulation | automated | Alert emitted & logged |

## Traceability
NFRs: SEC-026, SEC-025
