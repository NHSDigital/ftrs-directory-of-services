# FtRS NFR – Service: DoS Search – Domain: Availability

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

### Domain Sources

- [Availability NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471107/Availability)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Availability | [AVAIL-001](#avail-001) | Availability report shows ≥99.90% multi-AZ uptime | Multi-AZ deployment achieves target uptime (e.g., ≥99.90%). | (none) |
| Availability | [AVAIL-002](#avail-002) | Region DR simulation meets plan objectives | Disaster recovery (DR) simulation meets documented objectives. | [FTRS-11 Create and Test Disaster Recovery processes to ensure we are able to recover within a time and scope that is acceptable to the business](https://nhsd-jira.digital.nhs.uk/browse/FTRS-11) |
| Availability | [AVAIL-003](#avail-003) | Uptime monitoring confirms 24x7 coverage | Continuous uptime monitoring covers 24x7 operations. | (none) |
| Availability | [AVAIL-004](#avail-004) | Monthly maintenance minutes ≤150; single ≤60 | Maintenance windows stay within monthly and per-event minute limits. | (none) |
| Availability | [AVAIL-005](#avail-005) | Tuesday window executed; smoke tests pass | Scheduled maintenance executes successfully with passing smoke tests afterward. | [FTRS-1004 Create smoke tests](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1004), [FTRS-1693 APIM: create automated tests for smoke testing](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1693) |
| Availability | [AVAIL-006](#avail-006) | DR exercise restores service <2h | DR exercise restores service within target recovery time (< defined hours). | [FTRS-11 Create and Test Disaster Recovery processes to ensure we are able to recover within a time and scope that is acceptable to the business](https://nhsd-jira.digital.nhs.uk/browse/FTRS-11), [FTRS-751 Security - Assess threat modelling exercise](https://nhsd-jira.digital.nhs.uk/browse/FTRS-751) |
| Availability | [AVAIL-007](#avail-007) | Replication lag ≤60s; fail-over data delta minimal | Data replication lag remains under target ensuring minimal failover delta. | (none) |
| Availability | [AVAIL-008](#avail-008) | API uptime aligns with core service | API uptime aligns with overall service availability target. | (none) |
| Availability | [AVAIL-009](#avail-009) | Non-UK access attempts blocked & logged | Access from non-approved geographic regions is blocked and logged. | (none) |
| Availability | [AVAIL-010](#avail-010) | Blue/green deployment produces 0 failed requests | Blue/green deployments complete with zero failed user requests. | (none) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### AVAIL-001

Availability report shows ≥99.90% multi-AZ uptime

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| multi-az-uptime-report | Availability report shows ≥99.90% multi-AZ uptime | >= 99.90% monthly uptime across multi-AZ deployment | Monthly | prod | DoS Search | draft | (none) | Tracks SLA against multi-AZ deployment goals |

### AVAIL-002

Region DR simulation meets plan objectives

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| region-dr-simulation | Region DR simulation meets plan objectives | DR exercise meets RTO/RPO targets and user impact objectives | Semi-annual | int,ref | DoS Search | draft | [FTRS-11 Create and Test Disaster Recovery processes to ensure we are able to recover within a time and scope that is acceptable to the business](https://nhsd-jira.digital.nhs.uk/browse/FTRS-11) | Validates disaster recovery readiness across regions |

### AVAIL-003

Uptime monitoring confirms 24x7 coverage

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| uptime-monitoring-coverage | Uptime monitoring confirms 24x7 coverage | 24x7 coverage; alerts configured for service degradation | Continuous monitoring | prod | DoS Search | draft | (none) | Ensures continuous availability monitoring |

### AVAIL-004

Monthly maintenance minutes ≤150; single ≤60

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| maintenance-window-minutes | Monthly maintenance minutes ≤150; single ≤60 | Monthly total ≤150 minutes; single window ≤60 minutes | Monthly | prod | DoS Search | draft | (none) | Controls maintenance impact to meet availability objectives |

### AVAIL-005

Tuesday window executed; smoke tests pass

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| scheduled-maintenance-smoke-tests | Tuesday window executed; smoke tests pass | Maintenance completes; post-window smoke tests 100% pass; no Sev-1/2 incidents | Weekly maintenance window | prod | DoS Search | draft | [FTRS-1004 Create smoke tests](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1004), [FTRS-1693 APIM: create automated tests for smoke testing](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1693) | Ensures safe scheduled maintenance without user impact |

### AVAIL-006

DR exercise restores service <2h

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| dr-exercise-rto | DR exercise restores service <2h | End-to-end restore < 120 minutes; data loss = 0 per RPO | Semi-annual exercise | int,ref | DoS Search | draft | [FTRS-11 Create and Test Disaster Recovery processes to ensure we are able to recover within a time and scope that is acceptable to the business](https://nhsd-jira.digital.nhs.uk/browse/FTRS-11) | Validates recovery objectives and data integrity |

### AVAIL-007

Replication lag ≤60s; fail-over data delta minimal

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| replication-lag-threshold | Replication lag \u226460s; fail-over data delta minimal | Replication lag \u2264 60s for primary datasets; failover delta \u2264 1% records | Continuous + monthly report | prod | DoS Search | draft | (none) | Ensures rapid failover with minimal inconsistency |

### AVAIL-008

API uptime aligns with core service

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| api-uptime-sla | API uptime aligns with core service | API uptime \u2265 99.90% monthly; maintenance excluded per policy | Monthly | prod | DoS Search | draft | (none) | Aligns API availability to overall SLA |

### AVAIL-009

Non-UK access attempts blocked & logged

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| geo-blocking-enforced | Non-UK access attempts blocked & logged | 100% non-UK requests blocked at edge; structured log with country + ip | Continuous + weekly audit | prod | DoS Search | draft | (none) | Reduces risk from out-of-region access |

### AVAIL-010

Blue/green deployment produces 0 failed requests

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| blue-green-zero-failures | Blue/green deployment produces 0 failed requests | 0 failed requests during blue/green switch | Per deployment | int,ref,prod | DoS Search | draft | (none) | Ensures safe deployments without user impact |
