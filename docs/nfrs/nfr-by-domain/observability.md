# FtRS NFR – Observability

This page is auto-generated; do not hand-edit.

## NFR Codes

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| OBS-001 | App & infra health panels show green | Application and infrastructure health panels display green status during normal operation. | STORY-OBS-001 |
| OBS-002 | Authenticated remote health dashboard accessible | Authenticated remote health dashboard is accessible to support teams. | STORY-OBS-026 |
| OBS-003 | Health event visible ≤60s after failure | Health events appear on dashboards shortly after failures (within target freshness). | STORY-OBS-027 |
| OBS-004 | Automated maintenance tasks executed; zero manual interventions | Automated maintenance tasks run successfully with no manual intervention required. | STORY-OBS-028 |
| OBS-005 | Performance metrics per layer present | Layered performance metrics (app, DB, cache) are visible. | STORY-OBS-029 |
| OBS-006 | Remote performance dashboard matches local view | Remote performance dashboard mirrors local environment metrics accurately. | STORY-OBS-030 |
| OBS-007 | Performance metrics latency ≤60s | Performance metrics latency (ingest to display) stays within defined limit (e.g., ≤60s). | STORY-OBS-002 |
| OBS-008 | TPS per endpoint displayed & threshold alert configured | Per-endpoint transactions per second (TPS) are displayed with alert thresholds. | STORY-OBS-003 |
| OBS-009 | Endpoint latency histograms with p50/p95/p99 | Latency histograms show p50/p95/p99 for each endpoint. | STORY-OBS-004 |
| OBS-010 | Aggregate latency panel accurate within 2% roll-up | Aggregate latency panel roll-ups remain within acceptable accuracy margin (e.g., ≤2%). | STORY-OBS-031 |
| OBS-011 | Failure types logged & classified in dashboard | Failure types are logged and classified for reporting. | STORY-OBS-032 |
| OBS-012 | Error percentage metric & alert configured | Error rate metric and alert exist to highlight reliability issues. | STORY-OBS-033 |
| OBS-013 | Infra log query returns expected fields | Infrastructure logs return expected structured fields for queries. | STORY-OBS-034 |
| OBS-014 | Infra log entries include required fields | Infrastructure log entries include required contextual fields (e.g., IDs, timestamps). | STORY-OBS-014 |
| OBS-015 | Retention policy enforced & reported | Log retention policy is enforced and reported. | STORY-OBS-035 |
| OBS-016 | SIEM forwarding delivers test event <60s | Security/event forwarding to SIEM delivers test events within freshness target. | STORY-OBS-036 |
| OBS-017 | All log levels supported; dynamic change works | All log levels are supported and can be changed dynamically. | STORY-OBS-037 |
| OBS-018 | Log level propagation <2min with alert on breach | Log level changes propagate quickly (under defined minutes) with alert if breach. | STORY-OBS-038 |
| OBS-019 | Operational log shows full transaction chain | Operational logs allow full transaction chain reconstruction. | STORY-OBS-014, STORY-OBS-019 |
| OBS-020 | Operations logs reconstruct workflow | Operations logs reconstruct workflow sequences accurately. | STORY-OBS-039 |
| OBS-021 | Operational events include transaction_id | Operational events include a transaction identifier for correlation. | STORY-OBS-040 |
| OBS-022 | Audit trail reconstructs user action | Audit trail can reconstruct a specific user action sequence. | STORY-OBS-041 |
| OBS-023 | Audit events share transaction_id & ordered timestamps | Audit events share transaction IDs and ordered timestamps for traceability. | STORY-OBS-042 |
| OBS-024 | Alert rule triggers multi-channel notification | Alert rules trigger multi-channel notifications (e.g., chat + email). | STORY-OBS-043 |
| OBS-025 | Alerts delivered to multi-channel with context | Alerts delivered with sufficient context to act (multi-channel). | STORY-OBS-025 |
| OBS-026 | Analytics query identifies usage pattern | Analytics queries identify usage patterns from captured metrics. | STORY-OBS-044 |
| OBS-027 | Analytics outage non-impacting to transactions | Analytics outages do not impact core transaction processing. | STORY-OBS-045 |
| OBS-028 | RBAC restricts dashboard sections | Role-based access control (RBAC) restricts dashboard sections appropriately. | STORY-OBS-046 |
| OBS-029 | Dashboard freshness age ≤60s | Dashboard freshness age remains under target (e.g., ≤60s). | STORY-OBS-047 |
| OBS-030 | Distributed trace spans cover end-to-end request | Distributed tracing spans cover end-to-end request path. | STORY-OBS-005 |
| OBS-031 | Anonymised behaviour metrics collected without identifiers | Anonymised behavioural metrics are collected without exposing personal identifiers. | STORY-OBS-048 |
| OBS-032 | Per-endpoint 4xx/5xx response metrics & alert thresholds configured | Per-endpoint 4xx and 5xx response metrics are captured with alert thresholds so error rate spikes are detected and acted upon quickly. | [FTRS-1573](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1573) |
| OBS-033 | Unauthorized API access attempts logged, classified, alerted | Unauthorized API access attempts (failed authentication, forbidden operations, rate limit breaches, anomalous spikes) are logged with required context and generate timely alerts for early detection of credential misuse or attack patterns. | [FTRS-1607](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1607) |

## Controls

### OBS-001

Application and infrastructure health panels display green status during normal operation.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-001](#obs-001) | health-panels-green | App & infra health panels show green | All critical panels green; no stale data | Health checks + dashboard status API | Continuous + CI verification on change | int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Ensures at-a-glance service health visibility |

### OBS-007

Performance metrics latency (ingest to display) stays within defined limit (e.g., ≤60s).

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-007](#obs-007) | perf-metrics-latency | Performance metrics latency ≤60s | Metrics pipeline delivers data within 60s latency | Metrics agent + ingestion SLA alerting | Continuous monitoring | int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Fresh metrics are required for accurate operational decisions |

### OBS-008

Per-endpoint transactions per second (TPS) are displayed with alert thresholds.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-008](#obs-008) | tps-threshold-alert | TPS per endpoint displayed & threshold alert configured | TPS dashboard present; alert rule configured and tested | Metrics backend + alerting system | CI validation + monthly alert fire drill | int,ref,prod | crud-apis,dos-search | draft | Detects throughput anomalies proactively |

### OBS-009

Latency histograms show p50/p95/p99 for each endpoint.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-009](#obs-009) | latency-histograms | Endpoint latency histograms with p50/p95/p99 | Histograms available per endpoint with p50/p95/p99 series | Metrics backend + dashboard | Continuous | int,ref,prod | crud-apis,dos-search | draft | Percentile visibility supports performance governance |

### OBS-010

Aggregate latency panel roll-ups remain within acceptable accuracy margin (e.g., ≤2%).

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-010](#obs-010) | aggregate-latency-accuracy | Aggregate latency panel accurate within 2% roll-up | Roll-up accuracy within \u22642% vs raw series | Dashboard query tests + calibration script | Monthly calibration | prod | crud-apis,dos-search | draft | Ensures trustworthy aggregate metrics |

### OBS-011

Failure types are logged and classified for reporting.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-011](#obs-011) | failure-type-classification | Failure types logged & classified in dashboard | 100% failures carry type; classification accuracy \u2265 95% | Structured logging + classifier + dashboard | Continuous + monthly accuracy audit | int,ref,prod | crud-apis,dos-search | draft | Improves incident triage |

### OBS-012

Error rate metric and alert exist to highlight reliability issues.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-012](#obs-012) | error-percentage-alert | Error percentage metric & alert configured | Alert triggers when error% > 1% over 5m; playbook linked | Metrics backend + alerting rules | Continuous + monthly tuning | prod | crud-apis,dos-search | draft | Early detection of reliability regressions |

### OBS-013

Infrastructure logs return expected structured fields for queries.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-013](#obs-013) | infra-log-query-fields | Infra log query returns expected fields | Queries return required fields (timestamp, severity, host, correlation_id) | Log query tests + schema | CI per build + weekly audit | int,ref,prod | crud-apis,dos-search | draft | Ensures log usability for ops |

### OBS-014

Infrastructure log entries include required contextual fields (e.g., IDs, timestamps).

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-014](#obs-014) | infra-log-required-fields | Infra log entries include required fields | 100% entries include required fields; schema lint passes | Log schema validators + CI checks | CI per build + monthly audit | int,ref,prod | crud-apis,dos-search | draft | Guarantees structured logging quality |

### OBS-025

Alerts delivered with sufficient context to act (multi-channel).

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-025](#obs-025) | migration-variance-alerts | Actionable alerts on data-migration error rate and duration variance | Alert when error_rate >1% over 5m window OR full-sync duration > baseline +20%; include playbook link, correlation_id, impacted counts | Metrics backend, alerting engine, synthetic event injector, dashboard | Continuous evaluation; monthly threshold tuning; weekly report | int,ref,prod | data-migration | draft | Early detection of pipeline health issues to reduce MTTR and prevent silent degradation |

### OBS-030

Distributed tracing spans cover end-to-end request path.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-030](#obs-030) | distributed-trace-coverage | Distributed trace spans cover end-to-end request | ≥95% of requests include spans across key tiers | Tracing SDKs + sampling config | Continuous + monthly sampling review | int,ref,prod | crud-apis,dos-search | draft | Enables end-to-end diagnosis and correlation across layers |

### OBS-033

Unauthorized API access attempts (failed authentication, forbidden operations, rate limit breaches, anomalous spikes) are logged with required context and generate timely alerts for early detection of credential misuse or attack patterns.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-033](#obs-033) | unauth-access-monitoring | Unauthorized API access attempts logged & alerted with context | 100% auth failures & forbidden requests produce structured log entry with reason, correlation_id, source_ip, user_agent; alert triggers on >5 failed auth attempts per principal per 1m or anomaly spike (>3x baseline) | API gateway logs, auth middleware, metrics backend, alerting rules, anomaly detection job | Continuous collection + weekly anomaly review + monthly rule tuning | int,ref,prod | crud-apis,dos-search,dos-ingestion-api,etl-ods,read-only-viewer | draft | Early detection of credential stuffing, token misuse, and privilege escalation attempts |
