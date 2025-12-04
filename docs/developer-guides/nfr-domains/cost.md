# FtRS NFR – Cost

Source: requirements/nfrs/cross-references/nfr-matrix.md

This page is auto-generated; do not hand-edit.

## NFR Codes

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| COST-001 | Mandatory tagging set present on 100% resources | All resources have mandatory cost tags for allocation and reporting. | STORY-COST-001 |
| COST-002 | Monthly Cost Explorer review & anomaly log | Monthly cost review identifies anomalies and tracks actions. | STORY-COST-002 |
| COST-003 | CloudHealth access for each team infra engineer | Each team infra engineer has access to cost analysis tooling (e.g., CloudHealth). | STORY-COST-003 |
| COST-004 | CloudHealth optimisation & tag compliance reports | Optimisation and tag compliance reports are produced and reviewed. | STORY-COST-004 |
| COST-005 | Budgets & alert notifications configured & tested | Budgets and cost alert notifications are configured and tested. | STORY-COST-005 |
| COST-006 | #ftrs-cost-alerts channel created & receiving test alerts | Dedicated cost alerts channel receives test and live notifications. | (none) |
| COST-007 | Quarterly cost review minutes & tracked actions | Quarterly cost reviews record minutes and follow-up actions. | (none) |

## Controls

### COST-001

All resources have mandatory cost tags for allocation and reporting.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| mandatory-tagging | Mandatory tagging set present on 100% resources | 100% resources carry mandatory tags | AWS Config rules + tag audit automation | Continuous + monthly report | dev,int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Enables cost visibility and accountability |

### COST-002

Monthly cost review identifies anomalies and tracks actions.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|

| monthly-cost-review | Monthly Cost Explorer review & anomaly log | Review completed; anomalies logged with actions | Cost Explorer + anomaly detection | Monthly | prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Ensures proactive cost management |

### COST-003

Each team infra engineer has access to cost analysis tooling (e.g., CloudHealth).

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| cloudhealth-access | CloudHealth access for each team infra engineer | Access provisioned; onboarding verified | CloudHealth admin + access logs | Quarterly verification | prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Ensures teams can act on cost insights |

### COST-004

Optimisation and tag compliance reports are produced and reviewed.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| optimisation-reports | CloudHealth optimisation & tag compliance reports | Reports generated; tracked actions created | CloudHealth reporting + tracker | Monthly | prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Drives optimisation and tag hygiene |

### COST-005

Budgets and cost alert notifications are configured and tested.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| budgets-and-alerts | Budgets & alert notifications configured & tested | Budgets configured; alerts tested successfully | AWS Budgets + notifications | Quarterly + pre-fiscal review | prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Prevents cost overruns via alerting |
