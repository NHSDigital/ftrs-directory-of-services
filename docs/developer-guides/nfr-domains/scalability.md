# FtRS NFR – Scalability

Source: requirements/nfrs/cross-references/nfr-matrix.md

This page is auto-generated; do not hand-edit.

## NFR Codes

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| SCAL-001 | Horizontal scale-out increases TPS linearly within tolerance | Horizontal scaling increases throughput nearly linearly without quality loss. | STORY-SCAL-001 |
| SCAL-002 | Vertical resize retains data & function without downtime | Vertical resizing (bigger instance) retains data and operation with no downtime. | STORY-SCAL-002 |
| SCAL-003 | All layers pass scalability checklist | All layers (app, DB, cache) meet defined scalability checklist items. | (none) |
| SCAL-004 | Scale-down events occur after sustained low utilisation | Scale-down only occurs after sustained low utilisation (not transient dips). | (none) |
| SCAL-005 | Autoscaling policy simulation triggers controlled scale | Autoscaling policy simulations trigger controlled scaling actions. | STORY-SCAL-003 |
| SCAL-006 | Scale event shows no SLA breach in latency/error | Scaling events do not cause SLA breaches in latency or error rate. | STORY-SCAL-004 |
| SCAL-007 | Capacity report shows ≥30% headroom | Capacity planning shows adequate headroom (e.g., ≥30%). | STORY-SCAL-005 |
| SCAL-008 | No manual scaling tickets for variance period | During the variance period no manual scaling tickets are needed. | (none) |
| SCAL-009 | Audit logs capture actor/reason for scaling | Audit logs record who initiated scaling and why. | (none) |
| SCAL-010 | Predictive alert fires at utilisation forecast threshold | Predictive alerts fire before utilisation reaches critical thresholds. | (none) |

## Controls

### SCAL-001

Horizontal scaling increases throughput nearly linearly without quality loss.
| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| horizontal-scale-linear | Horizontal scale-out increases TPS linearly within tolerance | TPS increases ~linearly per replica within agreed tolerance | Load tests + autoscaling reports | Quarterly simulation | int,ref | crud-apis,dos-search | draft | Validates scale-out effectiveness |

### SCAL-002

Vertical resizing (bigger instance) retains data and operation with no downtime.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| vertical-resize-no-downtime | Vertical resize retains data & function without downtime | Resize completes with zero downtime and no data loss | Resize runbook + health checks | Semi-annual exercise | int,ref | crud-apis,dos-search | draft | Ensures safe vertical scaling |

### SCAL-005

Autoscaling policy simulations trigger controlled scaling actions.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| autoscaling-policy-simulation | Autoscaling policy simulation triggers controlled scale | Policy simulates expected scale events; no flapping | Policy simulator + metrics | Quarterly | int,ref | crud-apis,dos-search | draft | Confirms autoscaling tuning |

### SCAL-006

Scaling events do not cause SLA breaches in latency or error rate.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| scale-event-sla | Scale event shows no SLA breach in latency/error | No breach in latency/error SLAs during scale | Metrics/alerts during scale events | Continuous monitoring + quarterly drill | int,ref,prod | crud-apis,dos-search | draft | Protects user experience during scaling |

### SCAL-007

Capacity planning shows adequate headroom (e.g., ≥30%).

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| capacity-headroom | Capacity report shows ≥30% headroom | >= 30% capacity headroom maintained | Capacity planning reports | Monthly | prod | crud-apis,dos-search | draft | Ensures buffer for demand spikes |
