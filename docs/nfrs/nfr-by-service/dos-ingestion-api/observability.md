# FtRS NFR – Service: dos-ingestion-api – Domain: Observability

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

### Domain Sources

- [Observability NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066470827/Observability+Monitoring+Metrics+Dashboards+and+Alerting)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Observability | [OBS-001](#obs-001) | App & infra health panels show green | Application and infrastructure health panels display green status during normal operation. | [FTRS-1015 Enable and Set Up Monitoring Endpoints](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1015) |
| Observability | [OBS-007](#obs-007) | Performance metrics latency ≤60s | Performance metrics latency (ingest to display) stays within defined limit (e.g., ≤60s). | (none) |
| Observability | [OBS-033](#obs-033) | Unauthorized API access attempts logged, classified, alerted | Unauthorized API access attempts (failed authentication, forbidden operations, rate limit breaches, anomalous spikes) are logged with required context and generate timely alerts for early detection of credential misuse or attack patterns. | [FTRS-1607 Unauthorised API access monitoring](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1607), [FTRS-1650 Adjust API Gateway Rate limiting to cater for 150tps](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1650) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### OBS-001

App & infra health panels show green

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| health-panels-green | App & infra health panels show green | All critical panels green; no stale data | Continuous + CI verification on change | int,ref,prod | dos-ingestion-api | draft | [FTRS-1015 Enable and Set Up Monitoring Endpoints](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1015) | Ensures at-a-glance service health visibility |

### OBS-007

Performance metrics latency ≤60s

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| perf-metrics-latency | Performance metrics latency ≤60s | Metrics pipeline delivers data within 60s latency | Continuous monitoring | int,ref,prod | dos-ingestion-api | draft | (none) | Fresh metrics are required for accurate operational decisions |

### OBS-033

Unauthorized API access attempts logged, classified, alerted

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| unauth-access-monitoring | Unauthorized API access attempts logged & alerted with context | 100% auth failures & forbidden requests produce structured log entry with reason, correlation_id, source_ip, user_agent; alert triggers on >5 failed auth attempts per principal per 1m or anomaly spike (>3x baseline) | Continuous collection + weekly anomaly review + monthly rule tuning | int,ref,prod | dos-ingestion-api | draft | [FTRS-1607 Unauthorised API access monitoring](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1607), [FTRS-1650 Adjust API Gateway Rate limiting to cater for 150tps](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1650) | Early detection of credential stuffing, token misuse, and privilege escalation attempts |
