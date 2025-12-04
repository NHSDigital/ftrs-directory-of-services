---
story_id: STORY-SEC-015
jira_key: FTRS-1604
title: Automated certificate expiry monitoring and proactive renewal
role: Platform Operations Engineer
goal: Ensure all TLS/mTLS certificates are renewed well before expiry with zero downtime
value: Prevents outages, protects trust, and reduces emergency change risk
nfr_refs: [SEC-015, SEC-001, SEC-014, SEC-030]
status: draft
---

## Description

Implement end-to-end automation that tracks every TLS/mTLS certificate (public endpoints, internal service mesh, database connections, message brokers) and renews them proactively before expiry. The system must continuously monitor expiry horizons, generate alerts at defined thresholds, perform unattended renewals (where supported), and orchestrate staged deployment (dual-cert / overlapping validity) to eliminate downtime. No certificate is allowed to reach an "critical" threshold window or expire in any environment.

## Acceptance Criteria

1. Central certificate inventory includes: subject, SANs, issuing CA chain, environment, service, key type, creation date, expiry date, renewal mechanism, secret store path.
2. Inventory validated daily against live endpoints (curl/OpenSSL handshake) — discrepancies (missing or stale entries) fail the compliance check.
3. Configurable renewal thresholds: warn at <=45 days, escalate at <=30 days, critical at <=14 days before expiry.
4. Alert routing: warnings -> ticket queue, escalations -> on-call channel, critical -> pager; all alerts include service, remaining days, rotation playbook link.
5. Automated renewal pipeline (for managed certs) triggers at escalation threshold producing a new certificate; deployment uses dual-cert overlap ensuring uninterrupted mTLS/TLS handshakes.
6. Zero expired certificates in dev/int/ref/prod during continuous monitoring period (rolling 90-day window).
7. Renewal pipeline artifacts omit private key material (only fingerprint, serial, not full PEM) and are retained <30 days.
8. Post-renewal validation: endpoint handshake shows new cert; CRL/OCSP validity check passes; certificate chain matches approved ITOC CA where mandated (SEC-014 alignment).
9. Metrics exposed: `cert_expiry_days_remaining{service,environment}` gauge per cert; `cert_renewal_success_total{service}` counter; `cert_renewal_failure_total{reason}` counter; `cert_expiry_alerts_total{severity}` counter.
10. Dashboard visualizes: approaching-expiry certificates (<=60 days), renewal status, failures grouped by reason.
11. Weekly report summarises renewals executed, upcoming escalations, any anomalies; stored with timestamp and tooling version.
12. Manual certificate entries (non-automated) produce an audit task before escalation threshold; missing completion auto-escalates to critical.
13. Integration test simulates certificate near-expiry (injected test cert) verifying alert sequence and automated renewal path.
14. Compliance script blocks merge if any production certificate <=30 days remaining without active renewal job scheduled.
15. Rotation playbook includes rollback steps and verification of old cert revocation / retirement within 24h of deployment.

## Non-Functional Acceptance

- Control: SEC-015 (certificate expiry & renewal)
- Thresholds: Warning 45d, Escalation 30d, Critical 14d, Expired 0d (disallowed)
- Tooling: Inventory validator, handshake probe, renewal pipeline, alerting, dashboard, compliance gate
- Cadence: Daily validation, continuous metrics, weekly reporting, threshold-driven renewals
- Environments: dev, int, ref, prod

## Test Strategy

| Test Type        | Focus                                          | Tooling                                     |
| ---------------- | ---------------------------------------------- | ------------------------------------------- |
| Unit             | Threshold calculations & alert classification  | Python threshold evaluator / date utilities |
| Integration      | Renewal pipeline end-to-end (staged dual-cert) | CI workflow + staging service               |
| Compliance       | Inventory vs handshake audit                   | Probe script (OpenSSL)                      |
| Synthetic Expiry | Simulated near-expiry cert triggers alerts     | Inject test cert fixture                    |
| Regression       | No expired cert in rolling window              | Metrics + historical scan                   |

## Monitoring & Metrics

- `cert_expiry_days_remaining{service,environment}`
- `cert_renewal_success_total{service}` / `cert_renewal_failure_total{reason}`
- `cert_expiry_alerts_total{severity}`
- SLO: 100% of certificates renewed before critical threshold (no <=14d without scheduled job)

## Implementation Notes

- Leverage secret store metadata for expiry extraction; fallback to parsing PEM via OpenSSL if not provided.
- Dual-cert deployment: introduce new cert while retaining old until successful traffic validation, then revoke old.
- Provide CLI (`scripts/nfr/cert_expiry_check.py`) for local verification reused in CI.
- Alert enrichment with rotation playbook URL and next scheduled run timestamp.

## Risks & Mitigation

| Risk                  | Impact           | Mitigation                             |
| --------------------- | ---------------- | -------------------------------------- |
| Inventory drift       | Missed renewals  | Daily handshake audit & merge gate     |
| Renewal failure late  | Potential outage | Early escalation & retry strategy      |
| False alerts          | Noise & fatigue  | Threshold tuning + dedup suppression   |
| Dual-cert conflict    | Handshake issues | Staged rollout & pre-production canary |
| Manual cert oversight | Expiry risk      | Automated task generation & escalation |

## Traceability

- NFR: SEC-015 (expiry & renewal), SEC-001 (crypto policy), SEC-014 (mTLS chain), SEC-030 (secure storage)
- Expectations Registry: `security/expectations.yaml` control related to certificate lifecycle

## Open Questions

| Topic               | Question                                         | Next Step                              |
| ------------------- | ------------------------------------------------ | -------------------------------------- |
| Renewal thresholds  | Are 45/30/14 values final?                       | Confirm with security governance board |
| Revocation handling | CRL vs OCSP enforcement depth?                   | Decide based on CA capabilities        |
| Dashboard tech      | Reuse existing observability stack or new panel? | Evaluate Grafana vs internal UI        |
| Manual certs        | Phase out or retain for edge cases?              | Identify candidates for automation     |
