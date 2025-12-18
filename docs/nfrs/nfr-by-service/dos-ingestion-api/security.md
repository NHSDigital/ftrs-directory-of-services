# FtRS NFR – Service: dos-ingestion-api – Domain: Security

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Security NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066470803/Security)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Security | [SEC-001](#SEC-001) | Crypto algorithms conform; weak ciphers rejected | Use only strong, approved cryptographic algorithms; weak or deprecated ciphers are blocked. | (none) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### SEC-001

Crypto algorithms conform; weak ciphers rejected

See explanation: [SEC-001](../../explanations.md#Explanations-SEC-001)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| crypto-cipher-policy | Crypto algorithms conform; weak ciphers rejected | TLS1.2+ only; no weak/legacy ciphers enabled | CI per change + monthly scan | dev,int,ref,prod | dos-ingestion-api | draft | (none) | Enforces modern TLS standards; automated scans detect drift |
