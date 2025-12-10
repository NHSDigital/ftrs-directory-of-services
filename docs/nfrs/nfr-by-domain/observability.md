# FtRS NFR – Observability

Source: requirements/nfrs/cross-references/nfr-matrix.md

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
| OBS-032 | Per-endpoint 4xx/5xx response metrics & alert thresholds configured | Per-endpoint 4xx and 5xx response metrics are captured with alert thresholds so error rate spikes are detected and acted upon quickly. | FTRS-1573 |
| OBS-033 | Unauthorized API access attempts logged, classified, alerted | Unauthorized API access attempts (failed authentication, forbidden operations, rate limit breaches, anomalous spikes) are logged with required context and generate timely alerts for early detection of credential misuse or attack patterns. | FTRS-1607 |

