---
story_id: STORY-AVAIL-011
title: Blue/green deployment produces 0 failed requests
role: SRE
goal: Deliver: Blue/green deployment produces 0 failed requests
value: Blue/green deployments complete with zero failed user requests.
nfr_refs: [AVAIL-010]
status: draft
---

## Description

Implement and validate NFR `AVAIL-010` for domain `availability`.

## Acceptance Criteria

- 0 failed requests during blue/green switch
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `AVAIL-010`
- Domain: availability
- Control ID: `blue-green-zero-failures`
- Measure: Blue/green deployment produces 0 failed requests
- Threshold: 0 failed requests during blue/green switch
- Tooling: Deployment controller + canary telemetry
- Cadence: Per deployment
- Environments: int, ref, prod


## Traceability

- Domain registry: requirements/nfrs/availability/nfrs.yaml
