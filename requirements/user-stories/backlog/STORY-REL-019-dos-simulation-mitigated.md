---
story_id: STORY-REL-019
title: DoS simulation mitigated; service responsive
role: SRE
goal: Deliver: DoS simulation mitigated; service responsive
value: Denial-of-service (DoS) simulation shows successful mitigation and continued responsiveness.
nfr_refs: [REL-004]
status: draft
---

## Description

Implement and validate NFR `REL-004` for domain `reliability`.

## Acceptance Criteria

- Sustained responsiveness; error rate \u2264 1%; p95 latency within SLA during attack
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `REL-004`
- Domain: reliability
- Control ID: `dos-simulation-mitigated`
- Measure: DoS simulation mitigated; service responsive
- Threshold: Sustained responsiveness; error rate \u2264 1%; p95 latency within SLA during attack
- Tooling: Attack simulator + WAF/rate-limiter + metrics
- Cadence: Quarterly exercise
- Environments: int, ref


## Traceability

- Domain registry: requirements/nfrs/reliability/nfrs.yaml
