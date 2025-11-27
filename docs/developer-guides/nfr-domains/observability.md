# FtRS NFR – Observability

Source: requirements/nfrs/cross-references/nfr-matrix.md

This page is auto-generated; do not hand-edit.

## NFR Codes

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| OBS-001 | App & infra health panels show green | Application and infrastructure health panels display green status during normal operation. | STORY-OBS-001 |
| OBS-002 | Authenticated remote health dashboard accessible | Authenticated remote health dashboard is accessible to support teams. | (none) |
| OBS-003 | Health event visible ≤60s after failure | Health events appear on dashboards shortly after failures (within target freshness). | (none) |
| OBS-004 | Automated maintenance tasks executed; zero manual interventions | Automated maintenance tasks run successfully with no manual intervention required. | (none) |
| OBS-005 | Performance metrics per layer present | Layered performance metrics (app, DB, cache) are visible. | (none) |
| OBS-006 | Remote performance dashboard matches local view | Remote performance dashboard mirrors local environment metrics accurately. | (none) |
| OBS-007 | Performance metrics latency ≤60s | Performance metrics latency (ingest to display) stays within defined limit (e.g., ≤60s). | STORY-OBS-002 |
| OBS-008 | TPS per endpoint displayed & threshold alert configured | Per-endpoint transactions per second (TPS) are displayed with alert thresholds. | STORY-OBS-003 |
| OBS-009 | Endpoint latency histograms with p50/p95/p99 | Latency histograms show p50/p95/p99 for each endpoint. | STORY-OBS-004 |
| OBS-010 | Aggregate latency panel accurate within 2% roll-up | Aggregate latency panel roll-ups remain within acceptable accuracy margin (e.g., ≤2%). | (none) |
| OBS-011 | Failure types logged & classified in dashboard | Failure types are logged and classified for reporting. | (none) |
| OBS-012 | Error percentage metric & alert configured | Error rate metric and alert exist to highlight reliability issues. | (none) |
| OBS-013 | Infra log query returns expected fields | Infrastructure logs return expected structured fields for queries. | (none) |
| OBS-014 | Infra log entries include required fields | Infrastructure log entries include required contextual fields (e.g., IDs, timestamps). | STORY-OBS-014 |
| OBS-015 | Retention policy enforced & reported | Log retention policy is enforced and reported. | (none) |
| OBS-016 | SIEM forwarding delivers test event <60s | Security/event forwarding to SIEM delivers test events within freshness target. | (none) |
| OBS-017 | All log levels supported; dynamic change works | All log levels are supported and can be changed dynamically. | (none) |
| OBS-018 | Log level propagation <2min with alert on breach | Log level changes propagate quickly (under defined minutes) with alert if breach. | (none) |
| OBS-019 | Operational log shows full transaction chain | Operational logs allow full transaction chain reconstruction. | STORY-OBS-019 |
| OBS-020 | Operations logs reconstruct workflow | Operations logs reconstruct workflow sequences accurately. | (none) |
| OBS-021 | Operational events include transaction_id | Operational events include a transaction identifier for correlation. | (none) |
| OBS-022 | Audit trail reconstructs user action | Audit trail can reconstruct a specific user action sequence. | (none) |
| OBS-023 | Audit events share transaction_id & ordered timestamps | Audit events share transaction IDs and ordered timestamps for traceability. | (none) |
| OBS-024 | Alert rule triggers multi-channel notification | Alert rules trigger multi-channel notifications (e.g., chat + email). | (none) |
| OBS-025 | Alerts delivered to multi-channel with context | Alerts delivered with sufficient context to act (multi-channel). | STORY-OBS-025 |
| OBS-026 | Analytics query identifies usage pattern | Analytics queries identify usage patterns from captured metrics. | (none) |
| OBS-027 | Analytics outage non-impacting to transactions | Analytics outages do not impact core transaction processing. | (none) |
| OBS-028 | RBAC restricts dashboard sections | Role-based access control (RBAC) restricts dashboard sections appropriately. | (none) |
| OBS-029 | Dashboard freshness age ≤60s | Dashboard freshness age remains under target (e.g., ≤60s). | (none) |
| OBS-030 | Distributed trace spans cover end-to-end request | Distributed tracing spans cover end-to-end request path. | STORY-OBS-005 |
| OBS-031 | Anonymised behaviour metrics collected without identifiers | Anonymised behavioural metrics are collected without exposing personal identifiers. | (none) |
| OBS-032 | Per-endpoint 4xx/5xx response metrics & alert thresholds configured | Per-endpoint 4xx and 5xx response metrics are captured with alert thresholds so error rate spikes are detected and acted upon quickly. | FTRS-1573 |
| OBS-033 | Unauthorized API access attempts logged, classified, alerted | Unauthorized API access attempts (failed authentication, forbidden operations, rate limit breaches, anomalous spikes) are logged with required context and generate timely alerts for early detection of credential misuse or attack patterns. | FTRS-1607 |

## Controls

### OBS-001
Application and infrastructure health panels display green status during normal operation.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| health-panels-green | App & infra health panels show green | All critical panels green; no stale data | Health checks + dashboard status API | Continuous + CI verification on change | int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Ensures at-a-glance service health visibility |

### OBS-007
Performance metrics latency (ingest to display) stays within defined limit (e.g., ≤60s).

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| perf-metrics-latency | Performance metrics latency ≤60s | Metrics pipeline delivers data within 60s latency | Metrics agent + ingestion SLA alerting | Continuous monitoring | int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Fresh metrics are required for accurate operational decisions |

### OBS-008
Per-endpoint transactions per second (TPS) are displayed with alert thresholds.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| tps-threshold-alert | TPS per endpoint displayed & threshold alert configured | TPS dashboard present; alert rule configured and tested | Metrics backend + alerting system | CI validation + monthly alert fire drill | int,ref,prod | crud-apis,dos-search | draft | Detects throughput anomalies proactively |

### OBS-009
Latency histograms show p50/p95/p99 for each endpoint.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| latency-histograms | Endpoint latency histograms with p50/p95/p99 | Histograms available per endpoint with p50/p95/p99 series | Metrics backend + dashboard | Continuous | int,ref,prod | crud-apis,dos-search | draft | Percentile visibility supports performance governance |

### OBS-025
Alerts delivered with sufficient context to act (multi-channel).

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| migration-variance-alerts | Actionable alerts on data-migration error rate and duration variance | Alert when error_rate >1% over 5m window OR full-sync duration > baseline +20%; include playbook link, correlation_id, impacted counts | Metrics backend, alerting engine, synthetic event injector, dashboard | Continuous evaluation; monthly threshold tuning; weekly report | int,ref,prod | data-migration | draft | Early detection of pipeline health issues to reduce MTTR and prevent silent degradation |

### OBS-030
Distributed tracing spans cover end-to-end request path.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| distributed-trace-coverage | Distributed trace spans cover end-to-end request | ≥95% of requests include spans across key tiers | Tracing SDKs + sampling config | Continuous + monthly sampling review | int,ref,prod | crud-apis,dos-search | draft | Enables end-to-end diagnosis and correlation across layers |

### OBS-033
Unauthorized API access attempts (failed authentication, forbidden operations, rate limit breaches, anomalous spikes) are logged with required context and generate timely alerts for early detection of credential misuse or attack patterns.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| unauth-access-monitoring | Unauthorized API access attempts logged & alerted with context | 100% auth failures & forbidden requests produce structured log entry with reason, correlation_id, source_ip, user_agent; alert triggers on >5 failed auth attempts per principal per 1m or anomaly spike (>3x baseline) | API gateway logs, auth middleware, metrics backend, alerting rules, anomaly detection job | Continuous collection + weekly anomaly review + monthly rule tuning | int,ref,prod | crud-apis,dos-search,dos-ingestion-api,etl-ods,read-only-viewer | draft | Early detection of credential stuffing, token misuse, and privilege escalation attempts |

