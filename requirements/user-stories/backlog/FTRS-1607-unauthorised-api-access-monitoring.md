---
story_id: STORY-OBS-006
jira_key: FTRS-1607
title: Unauthorised API access attempts are monitored, classified, and alerted
role: Security Operations Analyst
goal: Detect and respond rapidly to unauthorized or anomalous API access attempts
value: Reduces breach risk by early identification of credential misuse and attack patterns
nfr_refs: [OBS-033, SEC-029, SEC-001]
status: draft
---

## Description
Implement comprehensive monitoring for all unauthorized API access attempts including authentication failures, expired/invalid tokens, forbidden operations (403), rate limit breaches, and suspected credential stuffing. Provide structured logging, metrics, classification, alerting, and anomaly detection to enable timely security response and trend analysis.

## Acceptance Criteria
1. Structured log emitted for every unauthorized attempt with fields: `timestamp`, `service`, `env`, `endpoint`, `http_method`, `status_code`, `reason_code`, `source_ip`, `user_agent`, `correlation_id`, `token_subject` (if parseable), `failure_count_last_minute`.
2. Reason code taxonomy defined (e.g. `auth_invalid_signature`, `auth_expired`, `auth_revoked`, `permissions_denied`, `rate_limit_exceeded`, `suspected_stuffing`).
3. Metrics exposed: `api_unauth_attempts_total{reason_code,endpoint}`, `api_unauth_principal_failures_total{principal}`, `api_unauth_rate_limited_total{endpoint}`.
4. Real-time alerts fire when: a) >5 failures per principal in 1 minute, b) >100 total failures across platform in 5 minutes, c) >3x baseline anomaly (rolling 24h average) for any endpoint.
5. Dashboard panel shows last 24h unauthorized attempts with breakdown by reason_code and top N offending source_ips.
6. Anomaly detection job computes baseline (p95 daily unauthorized attempts per endpoint) and updates reference value every 24h; stored with timestamp + version.
7. False positive ratio (non-malicious developer test / known benign) maintained <10% of total unauthorized alerts; documented allowlist with expiry dates.
8. Weekly review report generated summarising counts, anomalies triggered, actions taken; archived to secure location.
9. Retention policy ensures logs kept ≥90 days with integrity (hash chain or storage immutability flag) for forensic purposes.
10. Integration test simulates invalid token burst & permission denial to validate alert triggers and structured log fields.
11. Alert payload includes correlation_id, aggregated failure counts, and a remediation playbook link.
12. No missing mandatory fields detected in sampled (1% random) log validation job; non-compliance fails CI quality gate.
13. Rate limit breach logs correlate with reliability brute-force protection metrics (REL-007) via shared correlation_id.
14. Access attempts with malformed JWT produce distinct reason_code and do not leak token content beyond header summary.
15. Dashboard latency for showing a new unauthorized event ≤60s from occurrence.

## Non-Functional Acceptance
- Control: OBS-033 (Unauthorized access monitoring)
- Threshold: 100% coverage; alert triggers per defined rules; dashboard freshness ≤60s
- Tooling: API gateway logs, auth middleware, metrics backend, alerting engine, anomaly detection job
- Cadence: Continuous collection, 1m & 5m alert evaluation, daily baseline update, weekly review
- Environments: int, ref, prod (dev optional; excluded from anomaly alerts)

## Test Strategy
| Test Type | Focus | Tooling |
|-----------|-------|---------|
| Unit | Reason code classification | Auth middleware tests |
| Integration | Burst & anomaly scenario | Simulation harness |
| Metrics | Accuracy & labels | Metrics scrape + validation script |
| Alerting | Threshold & anomaly triggers | Synthetic event injector |
| Log Schema | Mandatory field presence | CI schema validator |
| Performance | Dashboard freshness | Timestamp diff checks |

## Monitoring & Metrics
- `api_unauth_attempts_total{reason_code,endpoint}`
- `api_unauth_principal_failures_total{principal}`
- `api_unauth_rate_limited_total{endpoint}`
- `api_unauth_anomaly_alerts_total{endpoint}`
- `api_unauth_false_positive_total`

## Implementation Notes
- Prototype script `scripts/observability/unauth_access_monitoring.py` provides:
	- Structured log emission (JSON per event)
	- Rolling counters (principal & endpoint, 60s window) for threshold checks
	- Baseline anomaly detection stub (p95 * multiplier) fed by `baseline.sample.json`
- Auth middleware should call an internal function (future wrapper) instead of emitting directly to stdout; integrate with logging pipeline.
- Baseline JSON generated daily from aggregated metrics; versioned location to be defined (e.g., S3 or config repo path).
- Correlate with security controls (SEC-029) for JWT validation failure reasons.
- Future enhancement: push metrics to central backend (Prometheus/OpenTelemetry) rather than stdout summary.

## Risks & Mitigation
| Risk | Impact | Mitigation |
|------|--------|-----------|
| High false positives | Alert fatigue | Taxonomy refinement + allowlist expiries |
| Missing fields | Forensic gap | Schema validation & CI gate |
| Performance overhead | Increased latency | Asynchronous logging & efficient counters |
| Data privacy concerns | Excessive PII logging | Limit fields to operational metadata only |
| Anomaly drift | Missed attacks | Daily baseline recompute & manual review |

## Traceability
- NFR: OBS-033, SEC-029 (JWT auth), REL-007 (rate limiting), SEC-001 (crypto policy)
- Expectations Registry: `observability/expectations.yaml` control `unauth-access-monitoring`

## Open Questions
| Topic | Question | Next Step |
|-------|----------|-----------|
| Baseline window | Use 7d or 14d history? | Evaluate stability vs sensitivity |
| Correlation scope | Include geo/IP reputation? | Assess feasibility & privacy constraints |
| Dev environment inclusion | Value vs noise? | Decide after pilot |
