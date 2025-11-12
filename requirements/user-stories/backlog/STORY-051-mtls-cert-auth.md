---
id: STORY-051
title: Mutual TLS certificate authentication between services
nfr_refs:
  - SEC-014
  - SEC-025
type: security
status: draft
owner: platform-team
summary: Enforce mutual certificate authentication for designated inter-service and PID flows.
---

## Description
Deploy service certificates issued by approved CA. Configure inbound listeners and clients to perform mutual TLS handshake for sensitive data flows including PID. Validate expiry alerting and renewal readiness.

## Acceptance Criteria
- mTLS succeeds for authorised service pairs.
- Unauthorised certificate handshake fails with audit log entry.
- Certificate metadata (issuer, expiry) visible in monitoring dashboard.
- Renewal dry-run demonstrates zero downtime procedure.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| authorised_mtls_handshake | automated | 200 success; trace spans correlated |
| unauthorised_cert_test | automated | Handshake fails; error logged |
| cert_metadata_visibility | manual | Dashboard shows correct expiry date |
| renewal_dry_run | manual | Replacement completes without outage |

## Traceability
NFRs: SEC-014, SEC-025
