---
story_id: STORY-REL-025
title: External outage shows fallback & user messaging
role: SRE
goal: Deliver: External outage shows fallback & user messaging
value: External dependency outage invokes fallback and clear user messaging.
nfr_refs: [REL-014]
status: draft
---

## Description

Implement and validate NFR `REL-014` for domain `reliability`.

## Acceptance Criteria

- Documented fallback engaged; user messaging displayed; error rate \u2264 2%; recovery within SLA
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `REL-014`
- Domain: reliability
- Control ID: `external-outage-fallback`
- Measure: External outage shows fallback & user messaging
- Threshold: Documented fallback engaged; user messaging displayed; error rate \u2264 2%; recovery within SLA
- Tooling: Chaos experiments on external deps + observability evidence
- Cadence: Quarterly
- Environments: int, ref


## Traceability

- Domain registry: requirements/nfrs/reliability/nfrs.yaml
