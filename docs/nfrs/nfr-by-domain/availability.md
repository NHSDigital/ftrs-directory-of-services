# FtRS NFR – Availability

This page is auto-generated; do not hand-edit.

## NFR Codes

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| AVAIL-001 | Availability report shows ≥99.90% multi-AZ uptime | Multi-AZ deployment achieves target uptime (e.g., ≥99.90%). | STORY-AVAIL-001 |
| AVAIL-002 | Region DR simulation meets plan objectives | Disaster recovery (DR) simulation meets documented objectives. | STORY-AVAIL-002 |
| AVAIL-003 | Uptime monitoring confirms 24x7 coverage | Continuous uptime monitoring covers 24x7 operations. | STORY-AVAIL-003 |
| AVAIL-004 | Monthly maintenance minutes ≤150; single ≤60 | Maintenance windows stay within monthly and per-event minute limits. | STORY-AVAIL-004 |
| AVAIL-005 | Tuesday window executed; smoke tests pass | Scheduled maintenance executes successfully with passing smoke tests afterward. | STORY-AVAIL-006 |
| AVAIL-006 | DR exercise restores service <2h | DR exercise restores service within target recovery time (< defined hours). | STORY-AVAIL-007 |
| AVAIL-007 | Replication lag ≤60s; fail-over data delta minimal | Data replication lag remains under target ensuring minimal failover delta. | STORY-AVAIL-008 |
| AVAIL-008 | API uptime aligns with core service | API uptime aligns with overall service availability target. | STORY-AVAIL-009 |
| AVAIL-009 | Non-UK access attempts blocked & logged | Access from non-approved geographic regions is blocked and logged. | STORY-AVAIL-010 |
| AVAIL-010 | Blue/green deployment produces 0 failed requests | Blue/green deployments complete with zero failed user requests. | STORY-AVAIL-005, STORY-AVAIL-011 |

## Controls

### AVAIL-001

Multi-AZ deployment achieves target uptime (e.g., ≥99.90%).

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [AVAIL-001](#avail-001) | multi-az-uptime-report | Availability report shows ≥99.90% multi-AZ uptime | >= 99.90% monthly uptime across multi-AZ deployment | Uptime monitoring + monthly report automation | Monthly | prod | crud-apis,dos-search | draft | Tracks SLA against multi-AZ deployment goals |

### AVAIL-002

Disaster recovery (DR) simulation meets documented objectives.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [AVAIL-002](#avail-002) | region-dr-simulation | Region DR simulation meets plan objectives | DR exercise meets RTO/RPO targets and user impact objectives | DR runbooks + simulation exercises | Semi-annual | int,ref | crud-apis,dos-search | draft | Validates disaster recovery readiness across regions |

### AVAIL-003

Continuous uptime monitoring covers 24x7 operations.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [AVAIL-003](#avail-003) | uptime-monitoring-coverage | Uptime monitoring confirms 24x7 coverage | 24x7 coverage; alerts configured for service degradation | Uptime monitors + alerting system | Continuous monitoring | prod | crud-apis,dos-search | draft | Ensures continuous availability monitoring |

### AVAIL-004

Maintenance windows stay within monthly and per-event minute limits.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [AVAIL-004](#avail-004) | maintenance-window-minutes | Monthly maintenance minutes ≤150; single ≤60 | Monthly total ≤150 minutes; single window ≤60 minutes | Maintenance logs + reporting | Monthly | prod | crud-apis,dos-search | draft | Controls maintenance impact to meet availability objectives |

### AVAIL-005

Scheduled maintenance executes successfully with passing smoke tests afterward.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [AVAIL-005](#avail-005) | scheduled-maintenance-smoke-tests | Tuesday window executed; smoke tests pass | Maintenance completes; post-window smoke tests 100% pass; no Sev-1/2 incidents | Deployment controller + smoke test suite + incident log | Weekly maintenance window | prod | crud-apis,dos-search | draft | Ensures safe scheduled maintenance without user impact |

### AVAIL-006

DR exercise restores service within target recovery time (< defined hours).

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [AVAIL-006](#avail-006) | dr-exercise-rto | DR exercise restores service <2h | End-to-end restore < 120 minutes; data loss = 0 per RPO | DR runbook + timer + integrity checks | Semi-annual exercise | int,ref | crud-apis,dos-search | draft | Validates recovery objectives and data integrity |

### AVAIL-007

Data replication lag remains under target ensuring minimal failover delta.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [AVAIL-007](#avail-007) | replication-lag-threshold | Replication lag \u226460s; fail-over data delta minimal | Replication lag \u2264 60s for primary datasets; failover delta \u2264 1% records | Replication metrics + failover audit | Continuous + monthly report | prod | crud-apis,dos-search | draft | Ensures rapid failover with minimal inconsistency |

### AVAIL-008

API uptime aligns with overall service availability target.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [AVAIL-008](#avail-008) | api-uptime-sla | API uptime aligns with core service | API uptime \u2265 99.90% monthly; maintenance excluded per policy | Uptime monitors + SLA calculator | Monthly | prod | crud-apis,dos-search | draft | Aligns API availability to overall SLA |

### AVAIL-009

Access from non-approved geographic regions is blocked and logged.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [AVAIL-009](#avail-009) | geo-blocking-enforced | Non-UK access attempts blocked & logged | 100% non-UK requests blocked at edge; structured log with country + ip | WAF geo rules + edge logs | Continuous + weekly audit | prod | crud-apis,dos-search | draft | Reduces risk from out-of-region access |

### AVAIL-010

Blue/green deployments complete with zero failed user requests.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [AVAIL-010](#avail-010) | blue-green-zero-failures | Blue/green deployment produces 0 failed requests | 0 failed requests during blue/green switch | Deployment controller + canary telemetry | Per deployment | int,ref,prod | crud-apis,dos-search | draft | Ensures safe deployments without user impact |
