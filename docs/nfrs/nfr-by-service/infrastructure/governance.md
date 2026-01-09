# FtRS NFR – Service: Infrastructure – Domain: Governance

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Governance NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471139/Compliance+and+Governance)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Governance | [GOV-001](#Infrastructure–GovernanceNFRs&Controls-GOV-001) | Service Management pre-live acceptance signed | Service Management pre-live acceptance is signed off before go-live. | (none) |
| Governance | [GOV-002](#Infrastructure–GovernanceNFRs&Controls-GOV-002) | Well-Architected review completed & actions closed | Well-Architected review completed; remediation actions closed. | [FTRS-356](https://nhsd-jira.digital.nhs.uk/browse/FTRS-356) |
| Governance | [GOV-004](#Infrastructure–GovernanceNFRs&Controls-GOV-004) | Engineering Red-lines compliance checklist signed | Engineering red-lines compliance checklist is signed. | (none) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### GOV-001

Service Management pre-live acceptance signed

See explanation: [GOV-001](../../explanations.md#Explanations-GOV-001)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| service-management-pre-live | Service Management pre-live acceptance signed | Acceptance signed; evidence stored | Pre-live | prod | Infrastructure | draft | (none) | Ensures service readiness sign-off |

### GOV-002

Well-Architected review completed & actions closed

See explanation: [GOV-002](../../explanations.md#Explanations-GOV-002)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| well-architected-review | Well-Architected review completed & actions closed | Review complete; actions closed or exceptioned | Pre-live + annual | prod | Infrastructure | draft | (none) | Maintains architectural quality |

### GOV-004

Engineering Red-lines compliance checklist signed

See explanation: [GOV-004](../../explanations.md#Explanations-GOV-004)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| nhs-github-enterprise-repos | All FtRS code repositories are hosted in NHS GitHub Enterprise and comply with securing-repositories policy; engineering dashboards show compliance | 100% repositories on NHS GitHub Enterprise; 100% securing-repositories checks passing; exceptions recorded with owner and review date | Continuous (CI on change) + quarterly governance review | dev,int,ref,prod | Infrastructure | draft | (none) | Enforces organisational SDLC-1 Red Line for using NHS GitHub Enterprise and securing repositories; provides traceable evidence and automated verification |
