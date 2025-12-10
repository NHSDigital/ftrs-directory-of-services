---
story_id: STORY-AVAIL-010
title: Non-UK access attempts blocked & logged
role: SRE
goal: Deliver: Non-UK access attempts blocked & logged
value: Access from non-approved geographic regions is blocked and logged.
nfr_refs: [AVAIL-009]
status: draft
---

## Description

Implement and validate NFR `AVAIL-009` for domain `availability`.

## Acceptance Criteria

- 100% non-UK requests blocked at edge; structured log with country + ip
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `AVAIL-009`
- Domain: availability
- Control ID: `geo-blocking-enforced`
- Measure: Non-UK access attempts blocked & logged
- Threshold: 100% non-UK requests blocked at edge; structured log with country + ip
- Tooling: WAF geo rules + edge logs
- Cadence: Continuous + weekly audit
- Environments: prod


## Traceability

- Domain registry: requirements/nfrs/availability/nfrs.yaml
