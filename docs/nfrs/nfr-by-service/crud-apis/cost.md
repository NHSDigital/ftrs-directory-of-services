# FtRS NFR – Service: Ingress API – Domain: Cost

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Cost NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471149/FinOps)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Cost | [COST-001](#COST-001) | Mandatory tagging set present on 100% resources | All resources have mandatory cost tags for allocation and reporting. | (none) |
| Cost | [COST-002](#COST-002) | Monthly Cost Explorer review & anomaly log | Monthly cost review identifies anomalies and tracks actions. | (none) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### COST-001

Mandatory tagging set present on 100% resources

See explanation: [COST-001](../../explanations.md#Explanations-COST-001)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| mandatory-tagging | Mandatory tagging set present on 100% resources | 100% resources carry mandatory tags | Continuous + monthly report | dev,int,ref,prod | Ingress API | draft | (none) | Enables cost visibility and accountability |

### COST-002

Monthly Cost Explorer review & anomaly log

See explanation: [COST-002](../../explanations.md#Explanations-COST-002)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| monthly-cost-review | Monthly Cost Explorer review & anomaly log | Review completed; anomalies logged with actions | Monthly | prod | Ingress API | draft | (none) | Ensures proactive cost management |
