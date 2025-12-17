# FtRS NFR – Scalability

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Scalability NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471101/Scalability)

## NFR Codes

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| SCAL-001 | Horizontal scale-out increases TPS linearly within tolerance | Horizontal scaling increases throughput nearly linearly without quality loss. | (none) |
| SCAL-002 | Vertical resize retains data & function without downtime | Vertical resizing (bigger instance) retains data and operation with no downtime. | (none) |
| SCAL-003 | All layers pass scalability checklist | All layers (app, DB, cache) meet defined scalability checklist items. | (none) |
| SCAL-004 | Scale-down events occur after sustained low utilisation | Scale-down only occurs after sustained low utilisation (not transient dips). | (none) |
| SCAL-005 | Autoscaling policy simulation triggers controlled scale | Autoscaling policy simulations trigger controlled scaling actions. | (none) |
| SCAL-006 | Scale event shows no SLA breach in latency/error | Scaling events do not cause SLA breaches in latency or error rate. | (none) |
| SCAL-007 | Capacity report shows ≥30% headroom | Capacity planning shows adequate headroom (e.g., ≥30%). | (none) |
| SCAL-008 | No manual scaling tickets for variance period | During the variance period no manual scaling tickets are needed. | (none) |
| SCAL-009 | Audit logs capture actor/reason for scaling | Audit logs record who initiated scaling and why. | (none) |
| SCAL-010 | Predictive alert fires at utilisation forecast threshold | Predictive alerts fire before utilisation reaches critical thresholds. | (none) |
