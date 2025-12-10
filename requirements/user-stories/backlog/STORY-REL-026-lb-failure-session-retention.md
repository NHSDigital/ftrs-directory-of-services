---
story_id: STORY-REL-026
title: LB failure retains sessions & continues routing
role: SRE
goal: Deliver: LB failure retains sessions & continues routing
value: Load balancer failure preserves sessions and maintains routing continuity.
nfr_refs: [REL-015]
status: draft
---

## Description

Implement and validate NFR `REL-015` for domain `reliability`.

## Acceptance Criteria

- Zero session loss; traffic re-routed within 30s; p95 latency delta \u2264 10%
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `REL-015`
- Domain: reliability
- Control ID: `lb-failure-session-retention`
- Measure: LB failure retains sessions & continues routing
- Threshold: Zero session loss; traffic re-routed within 30s; p95 latency delta \u2264 10%
- Tooling: LB failover drill + session continuity tests + metrics
- Cadence: Semi-annual drill
- Environments: int, ref


## Traceability

- Domain registry: requirements/nfrs/reliability/nfrs.yaml
