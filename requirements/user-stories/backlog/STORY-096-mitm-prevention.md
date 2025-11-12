---
id: STORY-096
title: MITM prevention
nfr_refs:
  - REL-008
  - SEC-014
type: reliability
status: draft
owner: security-team
summary: Enforce strict TLS configuration and certificate pinning to prevent man-in-the-middle attacks.
---

## Description
Scan TLS endpoints for protocol/cipher compliance; implement certificate pinning for critical clients; simulate MITM interception attempts verifying failure and alerting.

## Acceptance Criteria
- TLS scan shows only strong protocols/ciphers (TLS1.2+/TLS1.3).
- Certificate pinning enabled for designated clients.
- MITM proxy attempt fails to establish session.
- Alert generated on pinning validation failure.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| tls_endpoint_scan | automated | Only approved protocols/ciphers |
| cert_pinning_config_check | manual | Pin list committed |
| mitm_proxy_attempt | automated | Connection terminated |
| pinning_failure_alert_test | automated | Alert emitted |

## Traceability
NFRs: REL-008, SEC-014
