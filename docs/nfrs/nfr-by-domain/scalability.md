# FtRS NFR – Scalability

This page is auto-generated; do not hand-edit.

## NFR Codes

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| SCAL-001 | Horizontal scale-out increases TPS linearly within tolerance | Horizontal scaling increases throughput nearly linearly without quality loss. | STORY-SCAL-001 |
| SCAL-002 | Vertical resize retains data & function without downtime | Vertical resizing (bigger instance) retains data and operation with no downtime. | STORY-SCAL-002 |
| SCAL-003 | All layers pass scalability checklist | All layers (app, DB, cache) meet defined scalability checklist items. | STORY-SCAL-006 |
| SCAL-004 | Scale-down events occur after sustained low utilisation | Scale-down only occurs after sustained low utilisation (not transient dips). | STORY-SCAL-007 |
| SCAL-005 | Autoscaling policy simulation triggers controlled scale | Autoscaling policy simulations trigger controlled scaling actions. | STORY-SCAL-003 |
| SCAL-006 | Scale event shows no SLA breach in latency/error | Scaling events do not cause SLA breaches in latency or error rate. | STORY-SCAL-004 |
| SCAL-007 | Capacity report shows ≥30% headroom | Capacity planning shows adequate headroom (e.g., ≥30%). | STORY-SCAL-005 |
| SCAL-008 | No manual scaling tickets for variance period | During the variance period no manual scaling tickets are needed. | STORY-SCAL-008 |
| SCAL-009 | Audit logs capture actor/reason for scaling | Audit logs record who initiated scaling and why. | STORY-SCAL-009 |
| SCAL-010 | Predictive alert fires at utilisation forecast threshold | Predictive alerts fire before utilisation reaches critical thresholds. | STORY-SCAL-010 |

## Controls

### SCAL-001

Horizontal scaling increases throughput nearly linearly without quality loss.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SCAL-001](#scal-001) | horizontal-scale-linear | Horizontal scale-out increases TPS linearly within tolerance | TPS increases ~linearly per replica within agreed tolerance | Load tests + autoscaling reports | Quarterly simulation | int,ref | crud-apis,dos-search | draft | Validates scale-out effectiveness |

### SCAL-002

Vertical resizing (bigger instance) retains data and operation with no downtime.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SCAL-002](#scal-002) | vertical-resize-no-downtime | Vertical resize retains data & function without downtime | Resize completes with zero downtime and no data loss | Resize runbook + health checks | Semi-annual exercise | int,ref | crud-apis,dos-search | draft | Ensures safe vertical scaling |

### SCAL-003

All layers (app, DB, cache) meet defined scalability checklist items.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SCAL-003](#scal-003) | scalability-checklist-complete | All layers pass scalability checklist | 100% checklist items complete; exceptions recorded with expiry | Checklist tracker + evidence links | Quarterly | int,ref | crud-apis,dos-search | draft | Ensures scale readiness across tiers |

### SCAL-004

Scale-down only occurs after sustained low utilisation (not transient dips).

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SCAL-004](#scal-004) | scale-down-sustained-low-util | Scale-down events occur after sustained low utilisation | No scale-down unless utilisation < 40% sustained for 30m; no flapping | Autoscaling metrics + policy | Continuous + monthly policy audit | prod | crud-apis,dos-search | draft | Prevents scale instability |

### SCAL-005

Autoscaling policy simulations trigger controlled scaling actions.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SCAL-005](#scal-005) | autoscaling-policy-simulation | Autoscaling policy simulation triggers controlled scale | Policy simulates expected scale events; no flapping | Policy simulator + metrics | Quarterly | int,ref | crud-apis,dos-search | draft | Confirms autoscaling tuning |

### SCAL-006

Scaling events do not cause SLA breaches in latency or error rate.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SCAL-006](#scal-006) | scale-event-sla | Scale event shows no SLA breach in latency/error | No breach in latency/error SLAs during scale | Metrics/alerts during scale events | Continuous monitoring + quarterly drill | int,ref,prod | crud-apis,dos-search | draft | Protects user experience during scaling |

### SCAL-007

Capacity planning shows adequate headroom (e.g., ≥30%).

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SCAL-007](#scal-007) | capacity-headroom | Capacity report shows ≥30% headroom | >= 30% capacity headroom maintained | Capacity planning reports | Monthly | prod | crud-apis,dos-search | draft | Ensures buffer for demand spikes |

### SCAL-008

During the variance period no manual scaling tickets are needed.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SCAL-008](#scal-008) | manual-scaling-eliminated | No manual scaling tickets for variance period | 0 manual scaling tickets in rolling 90 days | Ticketing system + scaling audit | Monthly review | prod | crud-apis,dos-search | draft | Confirms autoscaling effectiveness |

### SCAL-009

Audit logs record who initiated scaling and why.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SCAL-009](#scal-009) | scaling-audit-context | Audit logs capture actor/reason for scaling | 100% scale events have actor, reason, correlation_id | Audit log pipeline + policy | Continuous + quarterly audit | prod | crud-apis,dos-search | draft | Provides traceability of scaling decisions |

### SCAL-010

Predictive alerts fire before utilisation reaches critical thresholds.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SCAL-010](#scal-010) | predictive-utilisation-alert | Predictive alert fires at utilisation forecast threshold | Forecasted utilisation > 80% in 15m triggers alert; MTT Alert < 2m | Forecasting job + alerting rules | Continuous + monthly tuning | prod | crud-apis,dos-search | draft | Prevents SLA breach via early action |
