---
story_id: STORY-SEC-050
title: Release pipeline blocks on critical unresolved findings
role: Security Engineer
goal: Deliver: Release pipeline blocks on critical unresolved findings
value: Releases are halted if critical unresolved security findings remain.
nfr_refs: [SEC-028]
status: draft
---

## Description

Implement and validate NFR `SEC-028` for domain `security`.

## Acceptance Criteria

- 0 critical unresolved findings prior to release
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `SEC-028`
- Domain: security
- Control ID: `release-block-critical-findings`
- Measure: Release pipeline blocks on critical unresolved findings
- Threshold: 0 critical unresolved findings prior to release
- Tooling: Pipeline gate integrated with SCA, container, IaC scanners
- Cadence: Per release
- Environments: dev, int, ref

## Traceability

- Domain registry: requirements/nfrs/security/nfrs.yaml
