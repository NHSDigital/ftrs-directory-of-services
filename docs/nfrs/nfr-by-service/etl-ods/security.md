# FtRS NFR – Service: ODS ETL – Domain: Security

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Security NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066470803/Security)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Security | [SEC-001](#sec-001) | Crypto algorithms conform; weak ciphers rejected | Use only strong, approved cryptographic algorithms; weak or deprecated ciphers are blocked. | (none) |
| Security | [SEC-029](#sec-029) | All API endpoints enforce CIS2 JWT authentication (signature, issuer, audience, assurance claims) | All API endpoints enforce CIS2 JWT authentication with signature, issuer, audience and required assurance claim validation; invalid or missing tokens are rejected with structured errors. | [FTRS-1593](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1593) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### SEC-001

Crypto algorithms conform; weak ciphers rejected

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| crypto-cipher-policy | Crypto algorithms conform; weak ciphers rejected | TLS1.2+ only; no weak/legacy ciphers enabled | CI per change + monthly scan | dev,int,ref,prod | ODS ETL | draft | (none) | Enforces modern TLS standards; automated scans detect drift |

### SEC-029

All API endpoints enforce CIS2 JWT authentication (signature, issuer, audience, assurance claims)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| cis2-jwt-auth-enforced | All API endpoints enforce CIS2 JWT authentication (signature, issuer, audience, assurance claims) | 100% endpoints require valid CIS2 JWT; invalid/missing tokens rejected with structured 401 | CI per build + continuous runtime enforcement | dev,int,ref,prod | ODS ETL | draft | [FTRS-1593](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1593) | Ensures uniform strong authentication; claim + signature validation prevents unauthorized access |
