---
story_id: STORY-SCAL-007
title: Scale-down events occur after sustained low utilisation
role: Platform Engineer
goal: Deliver: Scale-down events occur after sustained low utilisation
value: Scale-down only occurs after sustained low utilisation (not transient dips).
nfr_refs: [SCAL-004]
status: draft
---

## Description

Implement and validate NFR `SCAL-004` for domain `scalability`.

## Acceptance Criteria

- No scale-down unless utilisation < 40% sustained for 30m; no flapping
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `SCAL-004`
- Domain: scalability
- Control ID: `scale-down-sustained-low-util`
- Measure: Scale-down events occur after sustained low utilisation
- Threshold: No scale-down unless utilisation < 40% sustained for 30m; no flapping
- Tooling: Autoscaling metrics + policy
- Cadence: Continuous + monthly policy audit
- Environments: prod


## Traceability

- Domain registry: requirements/nfrs/scalability/nfrs.yaml
