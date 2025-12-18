# FtRS NFR – Service: Infrastructure – Domain: Cost

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Cost NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471149/FinOps)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Cost | [COST-001](../../explanations.md#Explanations-COST-001) | Mandatory tagging set present on 100% resources | All resources have mandatory cost tags for allocation and reporting. | (none) |
| Cost | [COST-002](../../explanations.md#Explanations-COST-002) | Monthly Cost Explorer review & anomaly log | Monthly cost review identifies anomalies and tracks actions. | (none) |
| Cost | [COST-003](../../explanations.md#Explanations-COST-003) | CloudHealth access for each team infra engineer | Each team infra engineer has access to cost analysis tooling (e.g., CloudHealth). | (none) |
| Cost | [COST-004](../../explanations.md#Explanations-COST-004) | CloudHealth optimisation & tag compliance reports | Optimisation and tag compliance reports are produced and reviewed. | (none) |
| Cost | [COST-005](../../explanations.md#Explanations-COST-005) | Budgets & alert notifications configured & tested | Budgets and cost alert notifications are configured and tested. | (none) |
| Cost | [COST-006](../../explanations.md#Explanations-COST-006) | #ftrs-cost-alerts channel created & receiving test alerts | Dedicated cost alerts channel receives test and live notifications. | (none) |
| Cost | [COST-007](../../explanations.md#Explanations-COST-007) | Quarterly cost review minutes & tracked actions | Quarterly cost reviews record minutes and follow-up actions. | (none) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### COST-001

Mandatory tagging set present on 100% resources

See explanation: [COST-001](../../explanations.md#Explanations-COST-001)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| mandatory-tagging | Mandatory tagging set present on 100% resources | 100% resources carry mandatory tags | Continuous + monthly report | dev,int,ref,prod | Infrastructure | draft | (none) | Enables cost visibility and accountability |

### COST-002

Monthly Cost Explorer review & anomaly log

See explanation: [COST-002](../../explanations.md#Explanations-COST-002)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| monthly-cost-review | Monthly Cost Explorer review & anomaly log | Review completed; anomalies logged with actions | Monthly | prod | Infrastructure | draft | (none) | Ensures proactive cost management |

### COST-003

CloudHealth access for each team infra engineer

See explanation: [COST-003](../../explanations.md#Explanations-COST-003)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| cloudhealth-access | CloudHealth access for each team infra engineer | Access provisioned; onboarding verified | Quarterly verification | prod | Infrastructure | draft | (none) | Ensures teams can act on cost insights |

### COST-004

CloudHealth optimisation & tag compliance reports

See explanation: [COST-004](../../explanations.md#Explanations-COST-004)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| optimisation-reports | CloudHealth optimisation & tag compliance reports | Reports generated; tracked actions created | Monthly | prod | Infrastructure | draft | (none) | Drives optimisation and tag hygiene |

### COST-005

Budgets & alert notifications configured & tested

See explanation: [COST-005](../../explanations.md#Explanations-COST-005)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| budgets-and-alerts | Budgets & alert notifications configured & tested | Budgets configured; alerts tested successfully | Quarterly + pre-fiscal review | prod | Infrastructure | draft | (none) | Prevents cost overruns via alerting |
