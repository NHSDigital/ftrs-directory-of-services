# FtRS NFR – Observability

Source: requirements/nfrs/cross-references/nfr-matrix.md

This page is auto-generated; do not hand-edit.

## NFR Codes

### Missing Metadata Checklist

- [Stories] OBS-002
- [Stories] OBS-003
- [Stories] OBS-004
- [Stories] OBS-005
- [Stories] OBS-006
- [Stories] OBS-010
- [Stories] OBS-011
- [Stories] OBS-012
- [Stories] OBS-013
- [Stories] OBS-015
- [Stories] OBS-016
- [Stories] OBS-017
- [Stories] OBS-018
- [Stories] OBS-020
- [Stories] OBS-021
- [Stories] OBS-022
- [Stories] OBS-023
- [Stories] OBS-024
- [Stories] OBS-026
- [Stories] OBS-027
- [Stories] OBS-028
- [Stories] OBS-029
- [Stories] OBS-031

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
