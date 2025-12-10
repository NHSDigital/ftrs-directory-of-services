---
story_id: STORY-SCAL-009
title: Audit logs capture actor/reason for scaling
role: Platform Engineer
goal: Deliver: Audit logs capture actor/reason for scaling
value: Audit logs record who initiated scaling and why.
nfr_refs: [SCAL-009]
status: draft
---

## Description

Implement and validate NFR `SCAL-009` for domain `scalability`.

## Acceptance Criteria

- 100% scale events have actor, reason, correlation_id
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `SCAL-009`
- Domain: scalability
- Control ID: `scaling-audit-context`
- Measure: Audit logs capture actor/reason for scaling
- Threshold: 100% scale events have actor, reason, correlation_id
- Tooling: Audit log pipeline + policy
- Cadence: Continuous + quarterly audit
- Environments: prod


## Traceability

- Domain registry: requirements/nfrs/scalability/nfrs.yaml
