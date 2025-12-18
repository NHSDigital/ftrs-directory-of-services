# FtRS NFR – Service: Data Migration – Domain: Observability

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Observability NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066470827/Observability+Monitoring+Metrics+Dashboards+and+Alerting)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Observability | [OBS-025](#DataMigration–ObservabilityNFRs&Controls-OBS-025) | Alerts delivered to multi-channel with context | Alerts delivered with sufficient context to act (multi-channel). | (none) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### OBS-025

Alerts delivered to multi-channel with context

See explanation: [OBS-025](../../explanations.md#Explanations-OBS-025)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| migration-variance-alerts | Actionable alerts on data-migration error rate and duration variance | Alert when error_rate >1% over 5m window OR full-sync duration > baseline +20%; include playbook link, correlation_id, impacted counts | Continuous evaluation; monthly threshold tuning; weekly report | int,ref,prod | Data Migration | draft | (none) | Early detection of pipeline health issues to reduce MTTR and prevent silent degradation |
