---
story_id: STORY-INT-024
title: Machine-readable changelog generated
role: Integration Engineer
goal: Deliver: Machine-readable changelog generated
value: Machine-readable changelog is generated for each release.
nfr_refs: [INT-011]
status: draft
---

## Description

Implement and validate NFR `INT-011` for domain `interoperability`.

## Acceptance Criteria

- Changelog generated per release with breaking changes highlighted
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `INT-011`
- Domain: interoperability
- Control ID: `machine-readable-changelog`
- Measure: Machine-readable changelog generated
- Threshold: Changelog generated per release with breaking changes highlighted
- Tooling: Release pipeline + changelog generator
- Cadence: Per release
- Environments: prod


## Traceability

- Domain registry: requirements/nfrs/interoperability/nfrs.yaml
