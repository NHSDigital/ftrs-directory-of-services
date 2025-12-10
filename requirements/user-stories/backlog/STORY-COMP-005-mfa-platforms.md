---
story_id: STORY-COMP-005
title: MFA (CIS2) succeeds across supported platforms
role: QA Engineer
goal: Deliver: MFA (CIS2) succeeds across supported platforms
value: Multi-factor authentication (CIS2) works across supported platforms.
nfr_refs: [COMP-002]
status: draft
---

## Description

Implement and validate NFR `COMP-002` for domain `compatibility`.

## Acceptance Criteria

- MFA journeys pass across supported platforms
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `COMP-002`
- Domain: compatibility
- Control ID: `mfa-platforms`
- Measure: MFA (CIS2) succeeds across supported platforms
- Threshold: MFA journeys pass across supported platforms
- Tooling: Cross-platform test suite + identity provider logs
- Cadence: Release cycle
- Environments: int, ref, prod

## Traceability

- Domain registry: requirements/nfrs/compatibility/nfrs.yaml
