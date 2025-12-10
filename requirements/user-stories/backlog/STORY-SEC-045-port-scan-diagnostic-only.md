---
story_id: STORY-SEC-045
title: Port scan matches approved diagnostic list only
role: Security Engineer
goal: Deliver: Port scan matches approved diagnostic list only
value: Port scans reveal only approved diagnostic and service ports—no unexpected exposures.
nfr_refs: [SEC-021]
status: draft
---

## Description

Implement and validate NFR `SEC-021` for domain `security`.

## Acceptance Criteria

- No unexpected open ports detected outside approved list
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `SEC-021`
- Domain: security
- Control ID: `port-scan-diagnostic-only`
- Measure: Port scan matches approved diagnostic list only
- Threshold: No unexpected open ports detected outside approved list
- Tooling: Automated port scan + baseline comparison
- Cadence: Monthly + CI smoke on infra changes
- Environments: dev, int, ref, prod

## Traceability

- Domain registry: requirements/nfrs/security/nfrs.yaml
