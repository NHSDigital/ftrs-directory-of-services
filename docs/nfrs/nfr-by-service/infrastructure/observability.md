# FtRS NFR – Service: Infrastructure – Domain: Observability

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Observability NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066470827/Observability+Monitoring+Metrics+Dashboards+and+Alerting)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Observability | [OBS-001](#obs-001) | App & infra health panels show green | Application and infrastructure health panels display green status during normal operation. | [FTRS-1015](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1015) |
| Observability | OBS-002 | Authenticated remote health dashboard accessible | Authenticated remote health dashboard is accessible to support teams. | (none) |
| Observability | OBS-003 | Health event visible ≤60s after failure | Health events appear on dashboards shortly after failures (within target freshness). | [FTRS-1003](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1003) |
| Observability | OBS-004 | Automated maintenance tasks executed; zero manual interventions | Automated maintenance tasks run successfully with no manual intervention required. | (none) |
| Observability | OBS-005 | Performance metrics per layer present | Layered performance metrics (app, DB, cache) are visible. | [FTRS-1016](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1016) |
| Observability | OBS-006 | Remote performance dashboard matches local view | Remote performance dashboard mirrors local environment metrics accurately. | (none) |
| Observability | [OBS-007](#obs-007) | Performance metrics latency ≤60s | Performance metrics latency (ingest to display) stays within defined limit (e.g., ≤60s). | (none) |
| Observability | [OBS-008](#obs-008) | TPS per endpoint displayed & threshold alert configured | Per-endpoint transactions per second (TPS) are displayed with alert thresholds. | [FTRS-1688](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1688) |
| Observability | [OBS-009](#obs-009) | Endpoint latency histograms with p50/p95/p99 | Latency histograms show p50/p95/p99 for each endpoint. | (none) |
| Observability | [OBS-010](#obs-010) | Aggregate latency panel accurate within 2% roll-up | Aggregate latency panel roll-ups remain within acceptable accuracy margin (e.g., ≤2%). | (none) |
| Observability | [OBS-011](#obs-011) | Failure types logged & classified in dashboard | Failure types are logged and classified for reporting. | [FTRS-998](https://nhsd-jira.digital.nhs.uk/browse/FTRS-998) |
| Observability | [OBS-012](#obs-012) | Error percentage metric & alert configured | Error rate metric and alert exist to highlight reliability issues. | [FTRS-1017](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1017) |
| Observability | [OBS-013](#obs-013) | Infra log query returns expected fields | Infrastructure logs return expected structured fields for queries. | [FTRS-323](https://nhsd-jira.digital.nhs.uk/browse/FTRS-323) |
| Observability | [OBS-014](#obs-014) | Infra log entries include required fields | Infrastructure log entries include required contextual fields (e.g., IDs, timestamps). | (none) |
| Observability | OBS-015 | Retention policy enforced & reported | Log retention policy is enforced and reported. | (none) |
| Observability | OBS-016 | SIEM forwarding delivers test event <60s | Security/event forwarding to SIEM delivers test events within freshness target. | (none) |
| Observability | OBS-017 | All log levels supported; dynamic change works | All log levels are supported and can be changed dynamically. | (none) |
| Observability | OBS-018 | Log level propagation <2min with alert on breach | Log level changes propagate quickly (under defined minutes) with alert if breach. | (none) |
| Observability | OBS-019 | Operational log shows full transaction chain | Operational logs allow full transaction chain reconstruction. | (none) |
| Observability | OBS-020 | Operations logs reconstruct workflow | Operations logs reconstruct workflow sequences accurately. | (none) |
| Observability | OBS-021 | Operational events include transaction_id | Operational events include a transaction identifier for correlation. | (none) |
| Observability | OBS-022 | Audit trail reconstructs user action | Audit trail can reconstruct a specific user action sequence. | (none) |
| Observability | OBS-023 | Audit events share transaction_id & ordered timestamps | Audit events share transaction IDs and ordered timestamps for traceability. | [FTRS-1018](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1018) |
| Observability | OBS-024 | Alert rule triggers multi-channel notification | Alert rules trigger multi-channel notifications (e.g., chat + email). | (none) |
| Observability | OBS-026 | Analytics query identifies usage pattern | Analytics queries identify usage patterns from captured metrics. | (none) |
| Observability | OBS-027 | Analytics outage non-impacting to transactions | Analytics outages do not impact core transaction processing. | (none) |
| Observability | OBS-028 | RBAC restricts dashboard sections | Role-based access control (RBAC) restricts dashboard sections appropriately. | (none) |
| Observability | OBS-029 | Dashboard freshness age ≤60s | Dashboard freshness age remains under target (e.g., ≤60s). | (none) |
| Observability | [OBS-030](#obs-030) | Distributed trace spans cover end-to-end request | Distributed tracing spans cover end-to-end request path. | [FTRS-885](https://nhsd-jira.digital.nhs.uk/browse/FTRS-885) |
| Observability | OBS-031 | Anonymised behaviour metrics collected without identifiers | Anonymised behavioural metrics are collected without exposing personal identifiers. | (none) |
| Observability | OBS-032 | Per-endpoint 4xx/5xx response metrics & alert thresholds configured | Per-endpoint 4xx and 5xx response metrics are captured with alert thresholds so error rate spikes are detected and acted upon quickly. | [FTRS-1573](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1573) |
| Observability | [OBS-033](#obs-033) | Unauthorized API access attempts logged, classified, alerted | Unauthorized API access attempts (failed authentication, forbidden operations, rate limit breaches, anomalous spikes) are logged with required context and generate timely alerts for early detection of credential misuse or attack patterns. | (none) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### OBS-001

App & infra health panels show green

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| health-panels-green | App & infra health panels show green | All critical panels green; no stale data | Continuous + CI verification on change | int,ref,prod | Infrastructure | draft | [FTRS-1015](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1015) | Ensures at-a-glance service health visibility |

### OBS-007

Performance metrics latency ≤60s

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| perf-metrics-latency | Performance metrics latency ≤60s | Metrics pipeline delivers data within 60s latency | Continuous monitoring | int,ref,prod | Infrastructure | draft | (none) | Fresh metrics are required for accurate operational decisions |

### OBS-008

TPS per endpoint displayed & threshold alert configured

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| tps-threshold-alert | TPS per endpoint displayed & threshold alert configured | TPS dashboard present; alert rule configured and tested | CI validation + monthly alert fire drill | int,ref,prod | Infrastructure | draft | [FTRS-1688](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1688) | Detects throughput anomalies proactively |

### OBS-009

Endpoint latency histograms with p50/p95/p99

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| latency-histograms | Endpoint latency histograms with p50/p95/p99 | Histograms available per endpoint with p50/p95/p99 series | Continuous | int,ref,prod | Infrastructure | draft | (none) | Percentile visibility supports performance governance |

### OBS-010

Aggregate latency panel accurate within 2% roll-up

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| aggregate-latency-accuracy | Aggregate latency panel accurate within 2% roll-up | Roll-up accuracy within \u22642% vs raw series | Monthly calibration | prod | Infrastructure | draft | (none) | Ensures trustworthy aggregate metrics |

### OBS-011

Failure types logged & classified in dashboard

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| failure-type-classification | Failure types logged & classified in dashboard | 100% failures carry type; classification accuracy \u2265 95% | Continuous + monthly accuracy audit | int,ref,prod | Infrastructure | draft | [FTRS-998](https://nhsd-jira.digital.nhs.uk/browse/FTRS-998) | Improves incident triage |

### OBS-012

Error percentage metric & alert configured

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| error-percentage-alert | Error percentage metric & alert configured | Alert triggers when error% > 1% over 5m; playbook linked | Continuous + monthly tuning | prod | Infrastructure | draft | [FTRS-1017](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1017) | Early detection of reliability regressions |

### OBS-013

Infra log query returns expected fields

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| infra-log-query-fields | Infra log query returns expected fields | Queries return required fields (timestamp, severity, host, correlation_id) | CI per build + weekly audit | int,ref,prod | Infrastructure | draft | [FTRS-323](https://nhsd-jira.digital.nhs.uk/browse/FTRS-323) | Ensures log usability for ops |

### OBS-014

Infra log entries include required fields

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| infra-log-required-fields | Infra log entries include required fields | 100% entries include required fields; schema lint passes | CI per build + monthly audit | int,ref,prod | Infrastructure | draft | (none) | Guarantees structured logging quality |

### OBS-030

Distributed trace spans cover end-to-end request

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| distributed-trace-coverage | Distributed trace spans cover end-to-end request | ≥95% of requests include spans across key tiers | Continuous + monthly sampling review | int,ref,prod | Infrastructure | draft | [FTRS-885](https://nhsd-jira.digital.nhs.uk/browse/FTRS-885) | Enables end-to-end diagnosis and correlation across layers |

### OBS-033

Unauthorized API access attempts logged, classified, alerted

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| unauth-access-monitoring | Unauthorized API access attempts logged & alerted with context | 100% auth failures & forbidden requests produce structured log entry with reason, correlation_id, source_ip, user_agent; alert triggers on >5 failed auth attempts per principal per 1m or anomaly spike (>3x baseline) | Continuous collection + weekly anomaly review + monthly rule tuning | int,ref,prod | Infrastructure | draft | (none) | Early detection of credential stuffing, token misuse, and privilege escalation attempts |
