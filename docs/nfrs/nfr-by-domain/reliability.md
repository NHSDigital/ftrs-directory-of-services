# FtRS NFR – Reliability

This page is auto-generated; do not hand-edit.

## NFR Codes

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| REL-001 | Health checks, multi-AZ deployment documented | Service remains healthy across multiple availability zones with verified health checks. | STORY-REL-017 |
| REL-002 | AZ failure simulation maintains service | Simulated AZ failure does not interrupt service delivery. | STORY-REL-001 |
| REL-003 | Lifecycle reliability checklist completed | Lifecycle reliability checklist is completed for the service components. | STORY-REL-018 |
| REL-004 | DoS simulation mitigated; service responsive | Denial-of-service (DoS) simulation shows successful mitigation and continued responsiveness. | STORY-REL-019 |
| REL-005 | Injection attempt blocked; no code execution | Injection attacks are blocked, preventing arbitrary code execution attempts. | STORY-REL-020 |
| REL-006 | Placement scan shows no forbidden co-residency | Resource placement scan shows no forbidden co-residency (e.g., sensitive + public workloads). | STORY-REL-021 |
| REL-007 | Brute force/auth anomalies rate limited & alerted (peak 500 TPS burst capacity; rate limits + alerts) | Brute force or auth anomaly attempts are rate limited and create alerts. | STORY-REL-005 |
| REL-008 | MITM attempt fails; pinned cert validation passes | Man-in-the-middle (MITM) attempts fail due to secure certificate pinning. | STORY-REL-022 |
| REL-009 | Iframe embed blocked; headers verified | UI prevents iframe embedding (clickjacking) via secure headers. | STORY-REL-023 |
| REL-010 | Batch suspend/resume preserves data integrity | Pausing and resuming batch jobs does not corrupt or lose data. | STORY-REL-002 |
| REL-011 | Unhealthy node auto-replaced; workload continues | Unhealthy nodes are automatically replaced with workload continuity. | STORY-REL-003 |
| REL-012 | Single node removal shows stable performance & zero data loss | Removing a single node yields no data loss and minimal performance impact. | STORY-REL-024 |
| REL-013 | Tier failure graceful degradation & recovery evidenced | Tier failure triggers graceful degradation and later clean recovery. | STORY-REL-004 |
| REL-014 | External outage shows fallback & user messaging | External dependency outage invokes fallback and clear user messaging. | STORY-REL-025 |
| REL-015 | LB failure retains sessions & continues routing | Load balancer failure preserves sessions and maintains routing continuity. | STORY-REL-026 |
| REL-016 | Server error shows logout/message per spec | Server error paths show expected logout or user messaging per specification. | STORY-REL-016 |
| REL-017 | Restore drill meets RPO/RTO & ransomware defenses | Restore drills meet RPO/RTO targets and confirm ransomware defenses. | STORY-REL-027 |

## Controls

### REL-002

Simulated AZ failure does not interrupt service delivery.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [REL-002](#rel-002) | az-failure-simulation | AZ failure simulation maintains service | Successful failover with sustained service availability; no data loss | Chaos simulation + health checks | Quarterly exercise | int,ref | crud-apis,dos-search | draft | Validates resilience to Availability Zone failures |

### REL-003

Lifecycle reliability checklist is completed for the service components.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [REL-003](#rel-003) | reliability-checklist-complete | Lifecycle reliability checklist completed | 100% checklist items complete; exceptions recorded with expiry | Checklist tracker + evidence links | Pre-live + quarterly review | int,ref,prod | crud-apis,dos-search | draft | Ensures reliability practices across lifecycle |

### REL-004

Denial-of-service (DoS) simulation shows successful mitigation and continued responsiveness.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [REL-004](#rel-004) | dos-simulation-mitigated | DoS simulation mitigated; service responsive | Sustained responsiveness; error rate \u2264 1%; p95 latency within SLA during attack | Attack simulator + WAF/rate-limiter + metrics | Quarterly exercise | int,ref | crud-apis,dos-search | draft | Validates resilience under volumetric attacks |

### REL-007

Brute force or auth anomaly attempts are rate limited and create alerts.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [REL-007](#rel-007) | auth-brute-force-protection | Brute force/auth anomalies rate limited & alerted (peak 500 TPS legitimate burst supported) | Peak 500 TPS legitimate auth unaffected; anomalies blocked; alert ≤30s; ≤1% false positives | Auth gateway rate limiter + anomaly aggregator + performance harness + alerting | Continuous runtime enforcement + daily compliance script | dev,int,ref,prod | crud-apis,dos-search,dos-ingestion-api,etl-ods,read-only-viewer | draft | Protects availability & integrity under authentication attack patterns |

### REL-010

Pausing and resuming batch jobs does not corrupt or lose data.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [REL-010](#rel-010) | batch-suspend-resume-integrity | Batch suspend/resume preserves data integrity | 0 data loss; consistent resume and reconciliation | Batch controller + integrity checks | Release cycle validation | int,ref | etl-ods | draft | Ensures reliable batch operations |

### REL-011

Unhealthy nodes are automatically replaced with workload continuity.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [REL-011](#rel-011) | unhealthy-node-auto-replace | Unhealthy node auto-replaced; workload continues | Auto-replacement within policy; no user-visible downtime | Autoscaling group events + workload health | Continuous monitoring + quarterly drill | int,ref,prod | crud-apis,dos-search | draft | Maintains reliability during node failures |

### REL-012

Removing a single node yields no data loss and minimal performance impact.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [REL-012](#rel-012) | single-node-removal-safety | Single node removal shows stable performance & zero data loss | 0 data loss; p95 latency delta \u2264 10% during removal | Autoscaling events + workload health + integrity checks | Quarterly drill | int,ref | crud-apis,dos-search | draft | Ensures resilience to node loss without user impact |

### REL-013

Tier failure triggers graceful degradation and later clean recovery.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [REL-013](#rel-013) | tier-failure-graceful-degrade | Tier failure graceful degradation & recovery evidenced | Documented fallback; recovery time within SLA | Chaos experiments + observability evidence | Quarterly | int,ref | crud-apis,dos-search | draft | Demonstrates graceful degradation patterns |

### REL-014

External dependency outage invokes fallback and clear user messaging.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [REL-014](#rel-014) | external-outage-fallback | External outage shows fallback & user messaging | Documented fallback engaged; user messaging displayed; error rate \u2264 2%; recovery within SLA | Chaos experiments on external deps + observability evidence | Quarterly | int,ref | crud-apis,dos-search | draft | Demonstrates graceful handling of external dependency outages |

### REL-015

Load balancer failure preserves sessions and maintains routing continuity.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [REL-015](#rel-015) | lb-failure-session-retention | LB failure retains sessions & continues routing | Zero session loss; traffic re-routed within 30s; p95 latency delta \u2264 10% | LB failover drill + session continuity tests + metrics | Semi-annual drill | int,ref | crud-apis,dos-search | draft | Ensures resilience of routing tier |

### REL-016

Server error paths show expected logout or user messaging per specification.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [REL-016](#rel-016) | server-error-user-messaging | Server error shows logout/message per spec | Error paths conform to spec; correct logout/message; audit evidence across endpoints | Contract tests + UI behaviour checks + logs | CI per build + monthly audit | int,ref,prod | read-only-viewer | draft | Protects user experience during server errors |
