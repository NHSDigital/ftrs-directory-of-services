# FtRS NFR – Availability

Source: requirements/nfrs/cross-references/nfr-matrix.md

This page is auto-generated; do not hand-edit.

## NFR Codes

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| AVAIL-001 | Availability report shows ≥99.90% multi-AZ uptime | Multi-AZ deployment achieves target uptime (e.g., ≥99.90%). | STORY-AVAIL-001 |
| AVAIL-002 | Region DR simulation meets plan objectives | Disaster recovery (DR) simulation meets documented objectives. | STORY-AVAIL-002 |
| AVAIL-003 | Uptime monitoring confirms 24x7 coverage | Continuous uptime monitoring covers 24x7 operations. | STORY-AVAIL-003 |
| AVAIL-004 | Monthly maintenance minutes ≤150; single ≤60 | Maintenance windows stay within monthly and per-event minute limits. | STORY-AVAIL-004 |
| AVAIL-005 | Tuesday window executed; smoke tests pass | Scheduled maintenance executes successfully with passing smoke tests afterward. | (none) |
| AVAIL-006 | DR exercise restores service <2h | DR exercise restores service within target recovery time (< defined hours). | (none) |
| AVAIL-007 | Replication lag ≤60s; failover data delta minimal | Data replication lag remains under target ensuring minimal failover delta. | (none) |
| AVAIL-008 | API uptime aligns with core service | API uptime aligns with overall service availability target. | (none) |
| AVAIL-009 | Non-UK access attempts blocked & logged | Access from non-approved geographic regions is blocked and logged. | (none) |
| AVAIL-010 | Blue/green deployment produces 0 failed requests | Blue/green deployments complete with zero failed user requests. | (none) |

## Controls

### AVAIL-001

Multi-AZ deployment achieves target uptime (e.g., ≥99.90%).
| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| multi-az-uptime-report | Availability report shows ≥99.90% multi-AZ uptime | >= 99.90% monthly uptime across multi-AZ deployment | Uptime monitoring + monthly report automation | Monthly | prod | crud-apis,dos-search | draft | Tracks SLA against multi-AZ deployment goals |

### AVAIL-002

Disaster recovery (DR) simulation meets documented objectives.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| region-dr-simulation | Region DR simulation meets plan objectives | DR exercise meets RTO/RPO targets and user impact objectives | DR runbooks + simulation exercises | Semi-annual | int,ref | crud-apis,dos-search | draft | Validates disaster recovery readiness across regions |

### AVAIL-003

Continuous uptime monitoring covers 24x7 operations.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| uptime-monitoring-coverage | Uptime monitoring confirms 24x7 coverage | 24x7 coverage; alerts configured for service degradation | Uptime monitors + alerting system | Continuous monitoring | prod | crud-apis,dos-search | draft | Ensures continuous availability monitoring |

### AVAIL-004

Maintenance windows stay within monthly and per-event minute limits.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| maintenance-window-minutes | Monthly maintenance minutes ≤150; single ≤60 | Monthly total ≤150 minutes; single window ≤60 minutes | Maintenance logs + reporting | Monthly | prod | crud-apis,dos-search | draft | Controls maintenance impact to meet availability objectives |

### AVAIL-010

Blue/green deployments complete with zero failed user requests.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| blue-green-zero-failures | Blue/green deployment produces 0 failed requests | 0 failed requests during blue/green switch | Deployment controller + canary telemetry | Per deployment | int,ref,prod | crud-apis,dos-search | draft | Ensures safe deployments without user impact |
