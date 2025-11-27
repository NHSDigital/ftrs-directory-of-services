# FtRS NFR – Service: dos-ingestion-api – Domain: Reliability

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

### Domain Sources

- [Reliability NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471112/Reliability+and+Resilience)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Reliability | [REL-007](#rel-007) | Brute force/auth anomalies rate limited & alerted (peak 500 TPS burst capacity; rate limits + alerts) | Brute force or auth anomaly attempts are rate limited and create alerts. | [FTRS-1598 Auth brute force rate limited](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1598) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### REL-007

Brute force/auth anomalies rate limited & alerted (peak 500 TPS burst capacity; rate limits + alerts)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| auth-brute-force-protection | Brute force/auth anomalies rate limited & alerted (peak 500 TPS legitimate burst supported) | Peak 500 TPS legitimate auth unaffected; anomalies blocked; alert ≤30s; ≤1% false positives | Continuous runtime enforcement + daily compliance script | dev,int,ref,prod | dos-ingestion-api | draft | [FTRS-1598 Auth brute force rate limited](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1598) | Protects availability & integrity under authentication attack patterns |
