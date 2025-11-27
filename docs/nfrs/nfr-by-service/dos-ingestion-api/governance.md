# FtRS NFR – Service: dos-ingestion-api – Domain: Governance

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

### Domain Sources

- [Governance NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471139/Compliance+and+Governance)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Governance | [GOV-004](#gov-004) | Engineering Red-lines compliance checklist signed | Engineering red-lines compliance checklist is signed. | [FTRS-6 Adhere to engineering red lines by implementing necessary changes](https://nhsd-jira.digital.nhs.uk/browse/FTRS-6) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### GOV-004

Engineering Red-lines compliance checklist signed

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| nhs-github-enterprise-repos | All FtRS code repositories are hosted in NHS GitHub Enterprise and comply with securing-repositories policy; engineering dashboards show compliance | 100% repositories on NHS GitHub Enterprise; 100% securing-repositories checks passing; exceptions recorded with owner and review date | Continuous (CI on change) + quarterly governance review | dev,int,ref,prod | dos-ingestion-api | draft | [FTRS-6 Adhere to engineering red lines by implementing necessary changes](https://nhsd-jira.digital.nhs.uk/browse/FTRS-6) | Enforces organisational SDLC-1 Red Line for using NHS GitHub Enterprise and securing repositories; provides traceable evidence and automated verification |
