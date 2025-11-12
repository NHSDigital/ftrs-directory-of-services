---
id: STORY-011
title: Encrypt all data in transit
nfr_refs:
  - SEC-003
  - SEC-025
type: security
status: draft
owner: security-team
summary: Ensure all internal and external component interactions use strong TLS with mutual auth for PID flows.
---

## Description
All service-to-service and client-to-service communications must be protected using TLS1.2+ (pref TLS1.3). PID related flows additionally require mutual TLS.

## Acceptance Criteria
- All endpoints reject plaintext HTTP (automatic redirect or 4xx).
- TLS configuration scan reports only approved cipher suites.
- Attempt to downgrade to TLS1.1 fails and is logged.
- PID request without client certificate is rejected.
- Mutual TLS handshake succeeds for authorised PID client certificates.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| tls_probe_all_endpoints | automated | 100% endpoints TLS only |
| cipher_suite_scan | automated | Only allowed ciphers present |
| downgrade_attempt | automated | Connection terminated; event logged |
| pid_mtls_missing_cert | automated | 401/403 with audit entry |
| pid_mtls_valid_cert | automated | 200 success; trace logged |

## Traceability
NFRs: SEC-003, SEC-025
