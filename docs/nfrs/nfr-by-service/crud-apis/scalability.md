# FtRS NFR – Service: CRUD APIs – Domain: Scalability

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

### Domain Sources

- [Scalability NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471101/Scalability)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Scalability | [SCAL-001](#scal-001) | Horizontal scale-out increases TPS linearly within tolerance | Horizontal scaling increases throughput nearly linearly without quality loss. | (none) |
| Scalability | [SCAL-002](#scal-002) | Vertical resize retains data & function without downtime | Vertical resizing (bigger instance) retains data and operation with no downtime. | (none) |
| Scalability | [SCAL-003](#scal-003) | All layers pass scalability checklist | All layers (app, DB, cache) meet defined scalability checklist items. | (none) |
| Scalability | [SCAL-004](#scal-004) | Scale-down events occur after sustained low utilisation | Scale-down only occurs after sustained low utilisation (not transient dips). | (none) |
| Scalability | [SCAL-005](#scal-005) | Autoscaling policy simulation triggers controlled scale | Autoscaling policy simulations trigger controlled scaling actions. | (none) |
| Scalability | [SCAL-006](#scal-006) | Scale event shows no SLA breach in latency/error | Scaling events do not cause SLA breaches in latency or error rate. | (none) |
| Scalability | [SCAL-007](#scal-007) | Capacity report shows ≥30% headroom | Capacity planning shows adequate headroom (e.g., ≥30%). | (none) |
| Scalability | [SCAL-008](#scal-008) | No manual scaling tickets for variance period | During the variance period no manual scaling tickets are needed. | (none) |
| Scalability | [SCAL-009](#scal-009) | Audit logs capture actor/reason for scaling | Audit logs record who initiated scaling and why. | (none) |
| Scalability | [SCAL-010](#scal-010) | Predictive alert fires at utilisation forecast threshold | Predictive alerts fire before utilisation reaches critical thresholds. | (none) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### SCAL-001

Horizontal scale-out increases TPS linearly within tolerance

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| horizontal-scale-linear | Horizontal scale-out increases TPS linearly within tolerance | TPS increases ~linearly per replica within agreed tolerance | Quarterly simulation | int,ref | CRUD APIs | draft | (none) | Validates scale-out effectiveness |

### SCAL-002

Vertical resize retains data & function without downtime

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| vertical-resize-no-downtime | Vertical resize retains data & function without downtime | Resize completes with zero downtime and no data loss | Semi-annual exercise | int,ref | CRUD APIs | draft | (none) | Ensures safe vertical scaling |

### SCAL-003

All layers pass scalability checklist

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| scalability-checklist-complete | All layers pass scalability checklist | 100% checklist items complete; exceptions recorded with expiry | Quarterly | int,ref | CRUD APIs | draft | (none) | Ensures scale readiness across tiers |

### SCAL-004

Scale-down events occur after sustained low utilisation

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| scale-down-sustained-low-util | Scale-down events occur after sustained low utilisation | No scale-down unless utilisation < 40% sustained for 30m; no flapping | Continuous + monthly policy audit | prod | CRUD APIs | draft | (none) | Prevents scale instability |

### SCAL-005

Autoscaling policy simulation triggers controlled scale

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| autoscaling-policy-simulation | Autoscaling policy simulation triggers controlled scale | Policy simulates expected scale events; no flapping | Quarterly | int,ref | CRUD APIs | draft | (none) | Confirms autoscaling tuning |

### SCAL-006

Scale event shows no SLA breach in latency/error

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| scale-event-sla | Scale event shows no SLA breach in latency/error | No breach in latency/error SLAs during scale | Continuous monitoring + quarterly drill | int,ref,prod | CRUD APIs | draft | (none) | Protects user experience during scaling |

### SCAL-007

Capacity report shows ≥30% headroom

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| capacity-headroom | Capacity report shows ≥30% headroom | >= 30% capacity headroom maintained | Monthly | prod | CRUD APIs | draft | (none) | Ensures buffer for demand spikes |

### SCAL-008

No manual scaling tickets for variance period

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| manual-scaling-eliminated | No manual scaling tickets for variance period | 0 manual scaling tickets in rolling 90 days | Monthly review | prod | CRUD APIs | draft | (none) | Confirms autoscaling effectiveness |

### SCAL-009

Audit logs capture actor/reason for scaling

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| scaling-audit-context | Audit logs capture actor/reason for scaling | 100% scale events have actor, reason, correlation_id | Continuous + quarterly audit | prod | CRUD APIs | draft | (none) | Provides traceability of scaling decisions |

### SCAL-010

Predictive alert fires at utilisation forecast threshold

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| predictive-utilisation-alert | Predictive alert fires at utilisation forecast threshold | Forecasted utilisation > 80% in 15m triggers alert; MTT Alert < 2m | Continuous + monthly tuning | prod | CRUD APIs | draft | (none) | Prevents SLA breach via early action |
