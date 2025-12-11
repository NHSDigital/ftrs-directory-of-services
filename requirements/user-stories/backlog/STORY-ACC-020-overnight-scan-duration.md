---
story_id: STORY-ACC-020
title: Overnight full scan duration <2h
role: UX Engineer
goal: Deliver: Overnight full scan duration <2h
value: Overnight full scan finishes under defined maximum duration.
nfr_refs: [ACC-020]
status: draft
---

## Description

Implement and validate NFR `ACC-020` for domain `accessibility`.

## Acceptance Criteria

- Full scan completes < 2 hours
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `ACC-020`
- Domain: accessibility
- Control ID: `overnight-scan-duration`
- Measure: Overnight full scan duration <2h
- Threshold: Full scan completes < 2 hours
- Tooling: Scan scheduler + timer
- Cadence: Nightly
- Environments: int

## Traceability

- Domain registry: requirements/nfrs/accessibility/nfrs.yaml
