# FtRS NFR – Reliability

Source: requirements/nfrs/cross-references/nfr-matrix.md

This page is auto-generated; do not hand-edit.

## NFR Codes

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| REL-001 | Health checks, multi-AZ deployment documented | Service remains healthy across multiple availability zones with verified health checks. | (none) |
| REL-002 | AZ failure simulation maintains service | Simulated AZ failure does not interrupt service delivery. | STORY-REL-001 |
| REL-003 | Lifecycle reliability checklist completed | Lifecycle reliability checklist is completed for the service components. | (none) |
| REL-004 | DoS simulation mitigated; service responsive | Denial-of-service (DoS) simulation shows successful mitigation and continued responsiveness. | (none) |
| REL-005 | Injection attempt blocked; no code execution | Injection attacks are blocked, preventing arbitrary code execution attempts. | (none) |
| REL-006 | Placement scan shows no forbidden co-residency | Resource placement scan shows no forbidden co-residency (e.g., sensitive + public workloads). | (none) |
| REL-007 | Brute force/auth anomalies rate limited & alerted (peak 500 TPS burst capacity; rate limits + alerts) | Brute force or auth anomaly attempts are rate limited and create alerts. | FTRS-1598 |
| REL-008 | MITM attempt fails; pinned cert validation passes | Man-in-the-middle (MITM) attempts fail due to secure certificate pinning. | (none) |
| REL-009 | Iframe embed blocked; headers verified | UI prevents iframe embedding (clickjacking) via secure headers. | (none) |
| REL-010 | Batch suspend/resume preserves data integrity | Pausing and resuming batch jobs does not corrupt or lose data. | STORY-REL-002 |
| REL-011 | Unhealthy node auto-replaced; workload continues | Unhealthy nodes are automatically replaced with workload continuity. | STORY-REL-003 |
| REL-012 | Single node removal shows stable performance & zero data loss | Removing a single node yields no data loss and minimal performance impact. | (none) |
| REL-013 | Tier failure graceful degradation & recovery evidenced | Tier failure triggers graceful degradation and later clean recovery. | STORY-REL-004 |
| REL-014 | External outage shows fallback & user messaging | External dependency outage invokes fallback and clear user messaging. | (none) |
| REL-015 | LB failure retains sessions & continues routing | Load balancer failure preserves sessions and maintains routing continuity. | (none) |
| REL-016 | Server error shows logout/message per spec | Server error paths show expected logout or user messaging per specification. | STORY-REL-016 |
| REL-017 | Restore drill meets RPO/RTO & ransomware defenses | Restore drills meet RPO/RTO targets and confirm ransomware defenses. | (none) |

## Controls

### REL-002

Simulated AZ failure does not interrupt service delivery.
| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| az-failure-simulation | AZ failure simulation maintains service | Successful failover with sustained service availability; no data loss | Chaos simulation + health checks | Quarterly exercise | int,ref | crud-apis,dos-search | draft | Validates resilience to Availability Zone failures |

### REL-007

Brute force or auth anomaly attempts are rate limited and create alerts.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| auth-brute-force-protection | Brute force/auth anomalies rate limited & alerted (peak 500 TPS legitimate burst supported) | Peak 500 TPS legitimate auth unaffected; anomalies blocked; alert ≤30s; ≤1% false positives | Auth gateway rate limiter + anomaly aggregator + performance harness + alerting | Continuous runtime enforcement + daily compliance script | dev,int,ref,prod | crud-apis,dos-search,dos-ingestion-api,etl-ods,read-only-viewer | draft | Protects availability & integrity under authentication attack patterns |

### REL-010

Pausing and resuming batch jobs does not corrupt or lose data.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| batch-suspend-resume-integrity | Batch suspend/resume preserves data integrity | 0 data loss; consistent resume and reconciliation | Batch controller + integrity checks | Release cycle validation | int,ref | etl-ods | draft | Ensures reliable batch operations |

### REL-011

Unhealthy nodes are automatically replaced with workload continuity.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| unhealthy-node-auto-replace | Unhealthy node auto-replaced; workload continues | Auto-replacement within policy; no user-visible downtime | Autoscaling group events + workload health | Continuous monitoring + quarterly drill | int,ref,prod | crud-apis,dos-search | draft | Maintains reliability during node failures |

### REL-013

Tier failure triggers graceful degradation and later clean recovery.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| tier-failure-graceful-degrade | Tier failure graceful degradation & recovery evidenced | Documented fallback; recovery time within SLA | Chaos experiments + observability evidence | Quarterly | int,ref | crud-apis,dos-search | draft | Demonstrates graceful degradation patterns |
