---
story_id: STORY-SEC-030
jira_key: FTRS-1600
title: ITOC-signed mTLS certificates enforced
role: Security Engineer
goal: Ensure all service-to-service mTLS certificates are signed by ITOC-approved CA
value: Guarantees trusted certificate chain, centralized governance, and reduced impersonation risk
nfr_refs: [SEC-014, SEC-001, SEC-015, SEC-011]
status: draft
---

## Description

All designated internal service-to-service communications MUST use mutual TLS where the presented client/server certificates are issued by an ITOC-approved intermediate CA and validate up to the ITOC root. This story delivers certificate issuance, validation (chain + revocation), rotation, monitoring, and testing to prove enforcement and operational safety.

## Acceptance Criteria

1. 100% of covered service-to-service calls (crud-apis ↔ dos-search ↔ etl-ods ↔ dos-ingestion-api ↔ read-only-viewer) negotiate mTLS using certificates signed by ITOC-approved CA.
2. Certificate chain validation confirms: leaf -> intermediate (ITOC-approved) -> ITOC root; failure triggers structured security log with `chain_invalid` flag.
3. Handshake with an expired certificate is rejected and logs event containing: `cert_subject`, `issuer`, `expiry_ts`, `environment`, `correlation_id`.
4. Revoked certificate handshake fails within ≤5 minutes of revocation list (CRL) or OCSP status change publication.
5. Rotation process completes with zero downtime; new cert active before old expiry; alert raised ≥30 days pre-expiry (SEC-015 alignment).
6. Approved cipher suites only (per SEC-001 policy); attempts with weak/legacy cipher result in handshake failure and audit log entry `weak_cipher_attempt=1`.
7. p95 additional latency overhead from mTLS handshake < 20ms on int, ref, prod (SEC-011 alignment measured via integration perf tests).
8. Private key material stored exclusively in secrets manager / secure keystore; repo & artifact scans report 0 occurrences of plaintext key material.
9. Automated integration tests simulate: valid, expired, revoked, wrong CA, weak cipher; each scenario produces expected pass/fail outcome and log evidence.
10. Monitoring dashboard exposes success %, latency p95, failure breakdown (expired, revoked, chain_invalid, weak_cipher) with success rate ≥99.9%.

## Non-Functional Acceptance

- Control ID: `mtls-service-handshake`
- Chain Requirement: Leaf & intermediate signed by ITOC-approved CA; root = ITOC
- Latency Threshold: mTLS handshake adds <20ms p95 overhead
- Availability: Rotation introduces 0 failed handshakes during cutover window
- Security: 0 successful handshakes with expired/revoked/weak-cipher/wrong-CA certs
- Observability: Metrics emitted: `mtls_handshake_success_total`, `mtls_handshake_failure_total` (labels: reason, service_pair), `mtls_handshake_latency_ms` histogram

## Test Strategy

| Test Type   | Tooling                                   | Focus                                        |
| ----------- | ----------------------------------------- | -------------------------------------------- |
| Integration | CI pipeline (pytest + custom TLS harness) | Handshake scenarios & chain validity         |
| Performance | k6 / Locust                               | Latency overhead p95 & failure impact        |
| Security    | Automated cert validation scripts         | Chain, revocation, cipher policy compliance  |
| Monitoring  | Synthetic probes                          | Continuous handshake success rate & alerting |

## Out of Scope

- External (public internet) TLS termination policies (covered elsewhere).
- Non-mTLS service-to-public endpoints.

## Implementation Notes

- Use existing certificate management pipeline extended to request ITOC intermediate-signed certs.
- Add OCSP/CRL validation step in gateway / sidecar.
- Introduce structured logging fields: `mtls_reason`, `cert_subject`, `issuer`, `correlation_id`.
- Provide rotation runbook referencing SEC-015 alert flow.

## Monitoring & Metrics

- `mtls_handshake_success_total`
- `mtls_handshake_failure_total` (reason labels: expired, revoked, chain_invalid, weak_cipher, untrusted_issuer)
- `mtls_handshake_latency_ms` (histogram)
- Alert: success rate <99.9% over 5m or any `chain_invalid` spike >10 in 5m.

## Risks & Mitigation

| Risk                      | Impact               | Mitigation                                |
| ------------------------- | -------------------- | ----------------------------------------- |
| Revocation latency        | Window of exposure   | Frequent CRL/OCSP polling (≤5m)           |
| Misconfigured cipher list | Handshake failures   | Pre-deploy validation + integration tests |
| Rotation misfire          | Downtime             | Staged dual-cert deployment + live probes |
| Logging omissions         | Limited auditability | Enforced structured log schema + tests    |

## Traceability

- NFR: SEC-014 (mTLS service handshake), SEC-001 (cipher policy), SEC-011 (latency), SEC-015 (cert expiry alert)
- Expectations Registry: `security/expectations.yaml` control `mtls-service-handshake`

## Open Questions

1. Confirm exact ITOC intermediate CA naming convention to validate issuer DN.
2. Determine OCSP vs CRL precedence if both available.
3. Define rotation cadence (e.g., 180 days vs 365) per platform policy.
