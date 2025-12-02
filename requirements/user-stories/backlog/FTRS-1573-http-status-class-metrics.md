---
story_id: STORY-OBS-006
jira_key: FTRS-1573
title: HTTP Status Class Metrics & Alerts
role: Platform Engineer
goal: Observe and act on per-endpoint 4xx and 5xx error patterns
value: Enables rapid detection of client misuse and server instability
nfr_refs: [OBS-032]
status: draft
---

## Description

Implement per-endpoint instrumentation and alerting for HTTP status class outcomes (2xx, 3xx, 4xx, 5xx). Distinguish between client error (4xx) and server error (5xx) rates to support reliability, performance protection, and proactive remediation. Complements existing latency and TPS metrics.

## Acceptance Criteria

1. Metrics emitted per endpoint: `requests_total` (counter), `responses_total` (counter with `status_code` label) OR explicit `responses_4xx_total`, `responses_5xx_total` counters.
2. Derived ratio metrics available via dashboard queries: 4xx ratio and 5xx ratio (e.g. PromQL expressions documented).
3. 5xx error ratio alert: triggers when >1% of requests (rolling 5m) OR >5 consecutive 5xx spikes in 2m.
4. 4xx surge alert: triggers when 4xx ratio >10% sustained 10m (to detect integration misuse) excluding known benign codes (list documented).
5. Panels display: current counts, 24h sparkline, top 3 status codes, error ratio, last alert time.
6. All metrics tagged with `service`, `operation_id`, `environment`, `status_class`.
7. Dashboard & alert config version-controlled; change log entry recorded.
8. Validation script passes: emits at least one 4xx and 5xx synthetic request and asserts counters increment.
9. Documentation includes remediation guidance for common 4xx (validation failed) and 5xx (dependency timeout).
10. No PII in status metrics; labels exclude user identifiers.

## Non-Functional Acceptance

- Metrics cardinality: status labels limited to class or whitelisted codes (<15 distinct per service).
- Scrape freshness: metrics visible <60s after emission.
- Alert latency: <90s from breach condition to notification.

## Test Strategy

| Test Type        | Tooling                     | Focus                                    |
| ---------------- | --------------------------- | ---------------------------------------- |
| Unit             | Local test harness          | Counter increment on simulated responses |
| Integration      | Load test + fault injection | Ratio calculations under mixed outcomes  |
| Alert Simulation | Prometheus rule test        | Threshold trigger correctness            |
| Documentation    | Manual review               | Remediation guidance completeness        |

## Out of Scope

- Detailed per-user error attribution (privacy concerns)
- Non-HTTP protocols (will be separate story if needed)

## Implementation Notes

- Prefer single counter `http_responses_total{status_code="404"}` then derive class using regex or recording rule.
- Optionally record class directly: `http_responses_class_total{status_class="4xx"}` for simpler ratio queries.
- Recording rules:
  - `sum(rate(http_responses_class_total{status_class="5xx"}[5m])) / sum(rate(http_requests_total[5m]))` => 5xx ratio.
  - `sum(rate(http_responses_class_total{status_class="4xx"}[10m])) / sum(rate(http_requests_total[10m]))` => 4xx ratio.
- Alert thresholds tuned after initial baseline; include runbook link.

## Monitoring & Metrics

- `http_requests_total` counter (baseline volume)
- `http_responses_class_total` counter (labels: service, operation_id, status_class)
- `http_responses_total` counter (labels: service, operation_id, status_code)
- `http_5xx_ratio` recording rule
- `http_4xx_ratio` recording rule
- Alerts: `High5xxErrorRate`, `High4xxErrorRate`

## Risks & Mitigation

| Risk                                     | Impact                    | Mitigation                                             |
| ---------------------------------------- | ------------------------- | ------------------------------------------------------ |
| High cardinality from status_code labels | Metric storage cost       | Limit to codes with occurrences; use class aggregation |
| Over-alerting on transient spikes        | Alert fatigue             | Use multi-window (short + long) check                  |
| Missing client misuse detection          | Hidden integration issues | 4xx ratio alert & dashboard drill-down                 |

## Traceability

- NFR: OBS-032
- Jira: FTRS-1573
- Matrix: `nfr-matrix.md` updated (OBS-032 row)

## Open Questions

1. Do we need separate metrics for redirects (3xx) or aggregate into success class?
2. Should 4xx surge alert exclude 429 if rate-limiter triggers expected behavior?
