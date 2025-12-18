# FtRS NFR – Service: Programme – Domain: Cost

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Cost NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471149/FinOps)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Cost | [COST-002](../../explanations.md#Explanations-COST-002) | Monthly Cost Explorer review & anomaly log | Monthly cost review identifies anomalies and tracks actions. | (none) |
| Cost | [COST-005](../../explanations.md#Explanations-COST-005) | Budgets & alert notifications configured & tested | Budgets and cost alert notifications are configured and tested. | (none) |
| Cost | [COST-006](../../explanations.md#Explanations-COST-006) | #ftrs-cost-alerts channel created & receiving test alerts | Dedicated cost alerts channel receives test and live notifications. | (none) |
| Cost | [COST-007](../../explanations.md#Explanations-COST-007) | Quarterly cost review minutes & tracked actions | Quarterly cost reviews record minutes and follow-up actions. | (none) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### COST-002

Monthly Cost Explorer review & anomaly log

See explanation: [COST-002](../../explanations.md#Explanations-COST-002)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| monthly-cost-review | Monthly Cost Explorer review & anomaly log | Review completed; anomalies logged with actions | Monthly | prod | Programme | draft | (none) | Ensures proactive cost management |

### COST-005

Budgets & alert notifications configured & tested

See explanation: [COST-005](../../explanations.md#Explanations-COST-005)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| budgets-and-alerts | Budgets & alert notifications configured & tested | Budgets configured; alerts tested successfully | Quarterly + pre-fiscal review | prod | Programme | draft | (none) | Prevents cost overruns via alerting |
