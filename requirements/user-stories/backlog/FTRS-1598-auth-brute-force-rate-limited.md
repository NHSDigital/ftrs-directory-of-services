---
story_id: STORY-REL-005
jira_key: FTRS-1598
title: Brute force/auth anomalies rate limited & alerted (supports peak 500 TPS legitimate auth)
role: Reliability Engineer
goal: Ensure authentication subsystem resists brute force attacks while supporting peak 500 TPS legitimate auth throughput
value: Preserves availability & integrity during credential attack attempts
nfr_refs: [REL-007]
status: draft
---

## Description

Implement and validate protections so that brute force or anomalous authentication attempts are aggressively rate limited, blocked, and alerted without degrading legitimate authentication traffic. The system must safely handle peak bursts up to 500 TPS of valid authentication (login / token exchange) while detecting and throttling malicious patterns (rapid failures, credential stuffing, distributed low-rate attacks). Alerts must surface actionable details (source aggregation, reason, affected endpoints) and metrics must enable trend analysis.

## Acceptance Criteria

1. Peak legitimate auth throughput capacity up to 500 TPS (tested as ≥5‑minute burst) keeps p95 auth latency within existing SLA in performance harness.
2. Global + per-credential rate limits applied: repeated failed attempts for same principal or IP/network segment blocked after threshold (e.g. >5 failures in 60s) with exponential backoff.
3. Distributed low-and-slow attack detection aggregates failures across ≥20 distinct IPs targeting same principal within 5m window and triggers protective throttling.
4. Credential stuffing detection: >50 distinct usernames from single IP / subnet within 60s blocked.
5. Rate-limited responses return 429 with standard OperationOutcome body (INT-005) including reason code `rate_limited` and correlation id.
6. Legitimate traffic at peak 500 TPS burst shows ≤1% false positive rate (blocked legitimate attempts) in test scenarios.
7. Anomaly alert fired within ≤30s of threshold breach containing: attack type, affected principal (if single), aggregated source count, current block status.
8. Metrics emitted: `auth_attempts_total{result="success|failure",reason}`, `auth_rate_limited_total{reason}`, `auth_anomaly_alert_total{type}`, `auth_latency_ms` histogram.
9. JWKS / MFA flows (if present) not degraded under attack; baseline auth success rate ≥99% during simulated brute force flood.
10. Configuration externalised: thresholds (per-IP, per-user, global failure window), 500 TPS peak capacity target, alert channels; no hard-coded values.
11. Negative test suite covers: single-IP rapid brute force, distributed spray, credential stuffing, replay of expired tokens, mixed legitimate + attack traffic.
12. Audit logs record blocked attempts (IP hash, principal hash, reason) without storing raw secrets or passwords.
13. System supports adaptive escalation: automatically tighten per-IP threshold when global anomaly condition active.
14. Daily compliance script validates thresholds match documented values and warns on drift.
15. Documentation updated: attack classes, threshold values, false positive tuning guidance, recovery/run book.

## Non-Functional Acceptance

- Capacity: Handles peak bursts up to 500 TPS legitimate auth (p95 latency within SLA; not required to sustain continuously).
- False Positives: ≤1% at 500 TPS.
- Detection Latency: Alert emitted ≤30s post threshold breach.
- Environments: dev, int, ref, prod (capacity proven in at least int/ref; production observation baseline logged).
- Tooling: Auth gateway/middleware + anomaly aggregator + performance harness.

## Test Strategy

| Test Type   | Tooling                       | Focus                           |
| ----------- | ----------------------------- | ------------------------------- |
| Performance | Load harness (auth scenarios) | 500 TPS capacity & latency      |
| Negative    | Attack simulators             | Block & alert correctness       |
| Integration | End-to-end auth flow          | No degradation under limits     |
| Reliability | Fault + attack combined       | Stability under stress          |
| Audit       | Log inspection tooling        | Proper redaction & completeness |

## Out of Scope

- MFA claim validation specifics (covered by security stories)
- Long-term behavioural ML anomaly detection (future enhancement)

## Implementation Notes

- Use token bucket or leaky bucket per principal + sliding window aggregator for distributed pattern detection.
- Maintain in-memory counters with periodic flush to metrics backend; ensure atomic increments.
- Hash sensitive identifiers (principal, IP) before logging/metric labels to avoid PII exposure.
- Provide structured reason codes: `rapid_failures`, `distributed_failures`, `credential_stuffing`, `rate_limited`.
- Backoff strategy: incremental delay + temporary block list with TTL.

## Monitoring & Metrics

- `auth_attempts_total` counter partitioned by result & reason
- `auth_rate_limited_total` counter
- `auth_anomaly_alert_total` counter
- `auth_latency_ms` histogram (observe impact of protections)
- Dashboard panels: legitimate TPS vs blocked attempts, alert timeline, false positive estimate

## Risks & Mitigation

| Risk                                           | Impact                     | Mitigation                                   |
| ---------------------------------------------- | -------------------------- | -------------------------------------------- |
| Over-aggressive limits                         | Legitimate user lockouts   | Threshold tuning & false positive monitoring |
| Distributed attack evades simple per-IP limits | Unchecked credential spray | Cross-IP aggregation & adaptive escalation   |
| Latency overhead from checks                   | SLA breach                 | Efficient in-memory counters & batching      |
| Logging sensitive data                         | Privacy issues             | Hashing + field allowlist                    |
| Configuration drift                            | Weak protection            | Daily compliance script & CI validation      |

## Traceability

- NFR: REL-007
- Related NFRs: SEC-016 (MFA resilience), OBS-032 (endpoint error metrics)
- Matrix: `requirements/nfrs/cross-references/nfr-matrix.md`

## Open Questions

| Topic              | Question                                | Next Step                        |
| ------------------ | --------------------------------------- | -------------------------------- |
| Threshold Values   | Final per-user/IP failure counts?       | Security review & tuning session |
| Distributed Window | Optimal aggregation duration?           | Load test experiments            |
| Alert Channels     | Which destinations (PagerDuty / Slack)? | Confirm with ops team            |
| Hashing Method     | Which algorithm for identifier hashing? | Decide (e.g. SHA-256 + salt)     |
| Replay Handling    | Need jti cache for login tokens?        | Threat model confirmation        |
