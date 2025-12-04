# Observability, Monitoring & Alerting NFRs

This document defines atomic Non-Functional Requirements (NFRs) for FtRS covering Health & Performance Monitoring, Logging (Infrastructure / Operational / Audit), Alerting, Analytics, Dashboards, and Traceability.

## Scope & Assumptions

- Applies to all environments (pre-production, production) unless explicitly constrained.
- Functional equivalence expected for prior tooling (Splunk, Instana, CloudWatch); implementation technology may change but capabilities must remain.
- Requirements are technology-agnostic but verifiable.
- Logs retained & managed per NHS Records Management Code of Practice.

## Legend

- Code: Immutable identifier (prefix OBS-\*)
- Requirement: Single atomic statement of expected outcome/capability
- Rationale: Why this matters (business / operational value)
- Verification: How we prove it (test, inspection, automation)
- Tags: Classification aids (domain, category, lifecycle)

## NFR Table

| Code    | Requirement                                                                                            | Rationale                                              | Verification                                                             | Tags                                          |
| ------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------ | ------------------------------------------------------------------------ | --------------------------------------------- |
| OBS-001 | Provide health monitoring for application, infrastructure, OS and system-wide components               | Early fault detection improves availability            | Health endpoints + infra probes return green; synthetic checks dashboard | observability, monitoring, health             |
| OBS-002 | Health monitoring interface accessible remotely outside monitored environment                          | Enable central operations oversight                    | Attempt remote access from mgmt network succeeds                         | observability, monitoring, health, remote     |
| OBS-003 | Health telemetry available real/near-real-time (<=60s latency)                                         | Timely reaction prevents escalation                    | Time delta between event and dashboard <60s in test                      | observability, monitoring, health, timeliness |
| OBS-004 | Health monitoring maintenance & support tasks automated where feasible                                 | Reduce toil & human error                              | Script/automation inventory; manual steps <20%                           | observability, monitoring, automation         |
| OBS-005 | Provide performance monitoring for application, infra, OS, system components                           | Capacity planning & SLA assurance                      | Metrics exist for all layers; sampling verified                          | observability, monitoring, performance        |
| OBS-006 | Performance monitoring interface accessible remotely                                                   | Central benchmark analysis                             | Remote metric query returns data                                         | observability, performance, remote            |
| OBS-007 | Performance telemetry near-real-time (<=60s)                                                           | Fast degradation detection                             | Load test emits metric, appears <60s                                     | observability, performance, timeliness        |
| OBS-008 | Capture transactions per second per API endpoint                                                       | Throughput insight & scaling                           | k6 test; TPS metric per endpoint visible                                 | observability, performance, api, metrics      |
| OBS-009 | Capture response time per endpoint (p50/p95/p99)                                                       | User experience quality                                | Latency histogram exported; thresholds logged                            | observability, performance, latency           |
| OBS-010 | Capture aggregate (combined) response time across all endpoints                                        | Global performance trend                               | Aggregated dashboard panel present                                       | observability, performance, latency           |
| OBS-011 | Capture failures by type with code & detail                                                            | Rapid root cause analysis                              | Inject fault; failure classification logged                              | observability, performance, errors            |
| OBS-012 | Capture error percentage vs total responses                                                            | SLA & error budget tracking                            | Error rate panel matches induced load test                               | observability, performance, errors            |
| OBS-013 | Infrastructure log repository secure, purgeable, exportable, queryable, human-readable                 | Forensics & compliance                                 | Permissions audit + export test + query examples                         | observability, logging, infrastructure        |
| OBS-014 | Infrastructure events persist: params, response, data nature & changes, datetime, sequence             | Tamper detection & replay                              | Log sample matches schema; sequence monotonic                            | observability, logging, infrastructure        |
| OBS-015 | Infrastructure log retention aligns with NHS Records Management                                        | Regulatory compliance                                  | Retention policy configuration reviewed & documented                            | observability, logging, retention             |
| OBS-016 | Infrastructure logs forwardable to central SIEM                                                        | Centralised threat monitoring                          | Simulated event appears in SIEM feed                                     | observability, logging, siem                  |
| OBS-017 | Support log levels ERROR/WARN/INFO/DEBUG/TRACE with defined semantics                                  | Noise control & diagnostic depth                       | Dynamic level change shows adjusted output                               | observability, logging, levels                |
| OBS-018 | Log level changes apply near-immediately (<2 min) per component                                        | Responsive diagnostics                                 | Change level; timestamp delta <2min                                      | observability, logging, levels, timeliness    |
| OBS-019 | Operational events logging capability for each application component                                   | End-to-end transaction visibility                      | Sample transaction shows operation chain                                 | observability, logging, operational           |
| OBS-020 | Operations log repository secure/purgeable/exportable/queryable/human-readable & correlatable          | Incident triage & traceability                         | Correlation test reconstructs user flow                                  | observability, logging, operational           |
| OBS-021 | Operational event fields: params, response, data identity, changes, datetime, sequence, transaction id | Subject access & audit support                         | Schema validation & sample check pass                                    | observability, logging, operational, audit    |
| OBS-022 | Audit event logging for user-centric actions with correlatable repository properties                   | Compliance & SAR support                               | SAR simulation retrieves audit trail                                     | observability, audit, logging                 |
| OBS-023 | All audit events in a transaction share transaction id & timestamp cluster                             | Trace integrity                                        | Multi-event test shows shared ID & close times                           | observability, audit, correlation             |
| OBS-024 | Configurable alert conditions on operational & infrastructure events                                   | Proactive incident response                            | Add alert rule; trigger by test event                                    | observability, alerting                       |
| OBS-025 | Alerts deliver contextual payload to multiple channels (email, IM, webhook, subscribed service)        | Fast stakeholder notification                          | Channel configuration test sends multi-channel alerts                           | observability, alerting, channels             |
| OBS-026 | Support analytics to discover & interpret patterns across interactions & infra metrics                 | Continuous improvement                                 | Query suite executes & returns insights                                  | observability, analytics                      |
| OBS-027 | Analytics failures never impact primary transaction success                                            | Resilience & user experience                           | Disable analytics; core flow still succeeds                              | observability, analytics, resilience          |
| OBS-028 | Provide role-based dashboards for health, performance, logging, alerting metrics                       | Focused operational insight                            | RBAC test: viewer vs admin panels differ                                 | observability, dashboards, rbac               |
| OBS-029 | Dashboard data freshness near-real-time (<60s lag)                                                     | Decision accuracy                                      | Timestamp comparison across panels                                       | observability, dashboards, timeliness         |
| OBS-030 | Capture distributed traces with span & transaction IDs across service boundary                         | Deep root cause analysis                               | Trace from ingress to storage visible                                    | observability, tracing                        |
| OBS-031 | Record anonymised end user behaviour metrics respecting privacy safeguards                             | Product usage insight                                  | Pseudonymisation check; no PID exposed                                   | observability, analytics, privacy             |
| OBS-032 | Expose per-endpoint 4xx/5xx error metrics with alert thresholds                                        | Faster detection of client misuse & server instability | Emit synthetic 4xx/5xx; counters increment; alert rule simulation fires  | observability, errors, alerting, metrics      |

## Derived / Not Explicit in Source Text

- Dashboards (OBS-028, OBS-029) inferred from needs for monitoring usability.
- Distributed tracing (OBS-030) inferred from prior Instana usage.
- End user behaviour (OBS-031) flagged in source with TODO marker.
- HTTP status class error metrics & alerting (OBS-032) added to ensure proactive error budget tracking.

## Verification Strategy Summary

- Automated integration tests for metrics & traces.
- Synthetic transactions for latency & error instrumentation.
- Configuration inspection (RBAC, retention, alert channels).
- Log schema validation using JSON schema or grok patterns.
- Manual fail-over / chaos tests to observe alert & trace behaviours.

## Open Items / Follow-Up

- Define concrete retention periods (X months) for OBS-015.
- Specify SLO thresholds for OBS-009/010 (p95, p99 values) & link to performance domain codes.
- Implement automated validator ensuring each new user story declares relevant OBS codes.
