# FtRS NFR – Service: Ingress API – Domain: Compatibility

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Compatibility NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471126/Compatibility)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Compatibility | [COMP-002](#IngressAPI–CompatibilityNFRs&Controls-COMP-002) | MFA (CIS2) succeeds across supported platforms | Multi-factor authentication (CIS2) works across supported platforms. | (none) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### COMP-002

MFA (CIS2) succeeds across supported platforms

See explanation: [COMP-002](../../explanations.md#Explanations-COMP-002)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| mfa-platforms | MFA (CIS2) succeeds across supported platforms | MFA journeys pass across supported platforms | Release cycle | int,ref,prod | Ingress API | draft | (none) | Ensures authentication compatibility |
