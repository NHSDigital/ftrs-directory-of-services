---
story_id: STORY-AVAIL-007
title: DR exercise restores service <2h
role: SRE
goal: Deliver: DR exercise restores service <2h
value: DR exercise restores service within target recovery time (< defined hours).
nfr_refs: [AVAIL-006]
status: draft
---

## Description

Implement and validate NFR `AVAIL-006` for domain `availability`.

## Acceptance Criteria

- End-to-end restore < 120 minutes; data loss = 0 per RPO
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `AVAIL-006`
- Domain: availability
- Control ID: `dr-exercise-rto`
- Measure: DR exercise restores service <2h
- Threshold: End-to-end restore < 120 minutes; data loss = 0 per RPO
- Tooling: DR runbook + timer + integrity checks
- Cadence: Semi-annual exercise
- Environments: int, ref


## Traceability

- Domain registry: requirements/nfrs/availability/nfrs.yaml
