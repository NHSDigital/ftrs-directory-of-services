---
story_id: STORY-SEC-031
title: WAF security pillar checklist completed & gaps tracked
role: Security Engineer
goal: Deliver: WAF security pillar checklist completed & gaps tracked
value: Complete the AWS/WAF security pillar checklist and track remediation actions for any gaps.
nfr_refs: [SEC-002]
status: draft
---

## Description

Implement and validate NFR `SEC-002` for domain `security`.

## Acceptance Criteria

- Checklist complete; 100% actions tracked; 0 open critical gaps
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `SEC-002`
- Domain: security
- Control ID: `waf-pillar-checklist`
- Measure: WAF security pillar checklist completed & gaps tracked
- Threshold: Checklist complete; 100% actions tracked; 0 open critical gaps
- Tooling: WAF checklist repository + issue tracker gate
- Cadence: Quarterly + on change
- Environments: dev, int, ref, prod

## Traceability

- Domain registry: requirements/nfrs/security/nfrs.yaml
