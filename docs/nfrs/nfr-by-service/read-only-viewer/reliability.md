# FtRS NFR – Service: Read-only Viewer – Domain: Reliability

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

### Domain Sources

- [Reliability NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471112/Reliability+and+Resilience)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Reliability | [REL-007](#rel-007) | Brute force/auth anomalies rate limited & alerted (peak 500 TPS burst capacity; rate limits + alerts) | Brute force or auth anomaly attempts are rate limited and create alerts. | [FTRS-1598 Auth brute force rate limited](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1598) |
| Reliability | REL-009 | Iframe embed blocked; headers verified | UI prevents iframe embedding (clickjacking) via secure headers. | (none) |
| Reliability | [REL-016](#rel-016) | Server error shows logout/message per spec | Server error paths show expected logout or user messaging per specification. | [FTRS-973 500 error responses are not standardized and lack a structured JSON format, impacting clarity and consistency](https://nhsd-jira.digital.nhs.uk/browse/FTRS-973) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### REL-007

Brute force/auth anomalies rate limited & alerted (peak 500 TPS burst capacity; rate limits + alerts)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| auth-brute-force-protection | Brute force/auth anomalies rate limited & alerted (peak 500 TPS legitimate burst supported) | Peak 500 TPS legitimate auth unaffected; anomalies blocked; alert ≤30s; ≤1% false positives | Continuous runtime enforcement + daily compliance script | dev,int,ref,prod | Read-only Viewer | draft | [FTRS-1598 Auth brute force rate limited](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1598) | Protects availability & integrity under authentication attack patterns |

### REL-016

Server error shows logout/message per spec

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| server-error-user-messaging | Server error shows logout/message per spec | Error paths conform to spec; correct logout/message; audit evidence across endpoints | CI per build + monthly audit | int,ref,prod | Read-only Viewer | draft | [FTRS-973 500 error responses are not standardized and lack a structured JSON format, impacting clarity and consistency](https://nhsd-jira.digital.nhs.uk/browse/FTRS-973) | Protects user experience during server errors |
