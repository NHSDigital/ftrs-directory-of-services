# FtRS NFR – Scalability

Source: requirements/nfrs/cross-references/nfr-matrix.md

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
