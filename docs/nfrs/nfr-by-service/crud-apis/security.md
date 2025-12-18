# FtRS NFR – Service: Ingress API – Domain: Security

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Security NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066470803/Security)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Security | [SEC-001](#SEC-001) | Crypto algorithms conform; weak ciphers rejected | Use only strong, approved cryptographic algorithms; weak or deprecated ciphers are blocked. | (none) |
| Security | [SEC-014](#SEC-014) | mTLS handshake succeeds between designated services | Mutual TLS (mTLS) succeeds between designated internal services to protect sensitive flows. | [FTRS-1600](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1600) |
| Security | [SEC-029](#SEC-029) | All API endpoints enforce CIS2 JWT authentication (signature, issuer, audience, assurance claims) | All API endpoints enforce CIS2 JWT authentication with signature, issuer, audience and required assurance claim validation; invalid or missing tokens are rejected with structured errors. | [FTRS-1593](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1593) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### SEC-001

Crypto algorithms conform; weak ciphers rejected

See explanation: [SEC-001](../../explanations.md#Explanations-SEC-001)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| crypto-cipher-policy | Crypto algorithms conform; weak ciphers rejected | TLS1.2+ only; no weak/legacy ciphers enabled | CI per change + monthly scan | dev,int,ref,prod | Ingress API | draft | (none) | Enforces modern TLS standards; automated scans detect drift |

### SEC-014

mTLS handshake succeeds between designated services

See explanation: [SEC-014](../../explanations.md#Explanations-SEC-014)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| mtls-service-handshake | mTLS handshake succeeds between designated services using ITOC-approved CA signed leaf + intermediate certs (chain to ITOC root); invalid/expired/revoked/untrusted-issuer/weak-cipher attempts rejected | 100% handshake success for valid ITOC chain; 0 successful handshakes with expired, revoked, weak cipher, or non-ITOC issuer certs; rotation introduces 0 downtime | CI per build + cert rotation checks + revocation poll ≤5m | int,ref,prod | Ingress API | draft | [FTRS-1600](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1600) | Enforces trusted ITOC certificate chain, strong ciphers, timely revocation, and zero-downtime rotation for secure service-to-service trust |

### SEC-029

All API endpoints enforce CIS2 JWT authentication (signature, issuer, audience, assurance claims)

See explanation: [SEC-029](../../explanations.md#Explanations-SEC-029)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| cis2-jwt-auth-enforced | All API endpoints enforce CIS2 JWT authentication (signature, issuer, audience, assurance claims) | 100% endpoints require valid CIS2 JWT; invalid/missing tokens rejected with structured 401 | CI per build + continuous runtime enforcement | dev,int,ref,prod | Ingress API | draft | [FTRS-1593](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1593) | Ensures uniform strong authentication; claim + signature validation prevents unauthorized access |
