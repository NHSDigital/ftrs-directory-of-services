# FtRS NFR – Service: CRUD APIs – Domain: Reliability

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Reliability NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471112/Reliability+and+Resilience)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Reliability | REL-001 | Health checks, multi-AZ deployment documented | Service remains healthy across multiple availability zones with verified health checks. | (none) |
| Reliability | [REL-002](#rel-002) | AZ failure simulation maintains service | Simulated AZ failure does not interrupt service delivery. | (none) |
| Reliability | [REL-003](#rel-003) | Lifecycle reliability checklist completed | Lifecycle reliability checklist is completed for the service components. | (none) |
| Reliability | [REL-004](#rel-004) | DoS simulation mitigated; service responsive | Denial-of-service (DoS) simulation shows successful mitigation and continued responsiveness. | (none) |
| Reliability | REL-005 | Injection attempt blocked; no code execution | Injection attacks are blocked, preventing arbitrary code execution attempts. | (none) |
| Reliability | REL-006 | Placement scan shows no forbidden co-residency | Resource placement scan shows no forbidden co-residency (e.g., sensitive + public workloads). | (none) |
| Reliability | [REL-007](#rel-007) | Brute force/auth anomalies rate limited & alerted (peak 500 TPS burst capacity; rate limits + alerts) | Brute force or auth anomaly attempts are rate limited and create alerts. | [FTRS-1598 Auth brute force rate limited](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1598) |
| Reliability | REL-008 | MITM attempt fails; pinned cert validation passes | Man-in-the-middle (MITM) attempts fail due to secure certificate pinning. | (none) |
| Reliability | [REL-011](#rel-011) | Unhealthy node auto-replaced; workload continues | Unhealthy nodes are automatically replaced with workload continuity. | (none) |
| Reliability | [REL-012](#rel-012) | Single node removal shows stable performance & zero data loss | Removing a single node yields no data loss and minimal performance impact. | (none) |
| Reliability | [REL-013](#rel-013) | Tier failure graceful degradation & recovery evidenced | Tier failure triggers graceful degradation and later clean recovery. | [FTRS-343 Perform Chaos Testing for FtRS Platform](https://nhsd-jira.digital.nhs.uk/browse/FTRS-343) |
| Reliability | [REL-014](#rel-014) | External outage shows fallback & user messaging | External dependency outage invokes fallback and clear user messaging. | (none) |
| Reliability | [REL-015](#rel-015) | LB failure retains sessions & continues routing | Load balancer failure preserves sessions and maintains routing continuity. | (none) |
| Reliability | REL-017 | Restore drill meets RPO/RTO & ransomware defenses | Restore drills meet RPO/RTO targets and confirm ransomware defenses. | [FTRS-11 Create and Test Disaster Recovery processes to ensure we are able to recover within a time and scope that is acceptable to the business](https://nhsd-jira.digital.nhs.uk/browse/FTRS-11), [FTRS-344 Create AWS Backup Plans for FtRS Platform](https://nhsd-jira.digital.nhs.uk/browse/FTRS-344) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### REL-002

AZ failure simulation maintains service

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| az-failure-simulation | AZ failure simulation maintains service | Successful failover with sustained service availability; no data loss | Quarterly exercise | int,ref | CRUD APIs | draft | (none) | Validates resilience to Availability Zone failures |

### REL-003

Lifecycle reliability checklist completed

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| reliability-checklist-complete | Lifecycle reliability checklist completed | 100% checklist items complete; exceptions recorded with expiry | Pre-live + quarterly review | int,ref,prod | CRUD APIs | draft | (none) | Ensures reliability practices across lifecycle |

### REL-004

DoS simulation mitigated; service responsive

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| dos-simulation-mitigated | DoS simulation mitigated; service responsive | Sustained responsiveness; error rate \u2264 1%; p95 latency within SLA during attack | Quarterly exercise | int,ref | CRUD APIs | draft | (none) | Validates resilience under volumetric attacks |

### REL-007

Brute force/auth anomalies rate limited & alerted (peak 500 TPS burst capacity; rate limits + alerts)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| auth-brute-force-protection | Brute force/auth anomalies rate limited & alerted (peak 500 TPS legitimate burst supported) | Peak 500 TPS legitimate auth unaffected; anomalies blocked; alert ≤30s; ≤1% false positives | Continuous runtime enforcement + daily compliance script | dev,int,ref,prod | CRUD APIs | draft | [FTRS-1598 Auth brute force rate limited](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1598) | Protects availability & integrity under authentication attack patterns |

### REL-011

Unhealthy node auto-replaced; workload continues

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| unhealthy-node-auto-replace | Unhealthy node auto-replaced; workload continues | Auto-replacement within policy; no user-visible downtime | Continuous monitoring + quarterly drill | int,ref,prod | CRUD APIs | draft | (none) | Maintains reliability during node failures |

### REL-012

Single node removal shows stable performance & zero data loss

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| single-node-removal-safety | Single node removal shows stable performance & zero data loss | 0 data loss; p95 latency delta \u2264 10% during removal | Quarterly drill | int,ref | CRUD APIs | draft | (none) | Ensures resilience to node loss without user impact |

### REL-013

Tier failure graceful degradation & recovery evidenced

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| tier-failure-graceful-degrade | Tier failure graceful degradation & recovery evidenced | Documented fallback; recovery time within SLA | Quarterly | int,ref | CRUD APIs | draft | [FTRS-343 Perform Chaos Testing for FtRS Platform](https://nhsd-jira.digital.nhs.uk/browse/FTRS-343) | Demonstrates graceful degradation patterns |

### REL-014

External outage shows fallback & user messaging

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| external-outage-fallback | External outage shows fallback & user messaging | Documented fallback engaged; user messaging displayed; error rate \u2264 2%; recovery within SLA | Quarterly | int,ref | CRUD APIs | draft | (none) | Demonstrates graceful handling of external dependency outages |

### REL-015

LB failure retains sessions & continues routing

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| lb-failure-session-retention | LB failure retains sessions & continues routing | Zero session loss; traffic re-routed within 30s; p95 latency delta \u2264 10% | Semi-annual drill | int,ref | CRUD APIs | draft | (none) | Ensures resilience of routing tier |
