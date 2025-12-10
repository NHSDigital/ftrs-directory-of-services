---
story_id: STORY-OBS-032
title: Failure types logged & classified in dashboard
role: SRE
goal: Deliver: Failure types logged & classified in dashboard
value: Failure types are logged and classified for reporting.
nfr_refs: [OBS-011]
status: draft
---

## Description

Implement and validate NFR `OBS-011` for domain `observability`.

## Acceptance Criteria

- 100% failures carry type; classification accuracy \u2265 95%
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `OBS-011`
- Domain: observability
- Control ID: `failure-type-classification`
- Measure: Failure types logged & classified in dashboard
- Threshold: 100% failures carry type; classification accuracy \u2265 95%
- Tooling: Structured logging + classifier + dashboard
- Cadence: Continuous + monthly accuracy audit
- Environments: int, ref, prod


## Traceability

- Domain registry: requirements/nfrs/observability/nfrs.yaml
