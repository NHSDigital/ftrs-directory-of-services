---
story_id: STORY-XXX
title: <Concise Title>
role: <Primary actor>
goal: <Goal the actor wants>
value: <Business/user value>
nfr_refs: [PERF-001, REL-001]
status: draft
---

## Description

Narrative describing the change.

## Acceptance Criteria

1. Criterion written in testable form.
2. ...
3. ... (aim ≥3, numbered)

## Non-Functional Acceptance

List concrete targets referencing expectations or spec (latency, error rate, metrics available).

## Test Strategy

| Test Type   | Tooling        | Focus                 |
| ----------- | -------------- | --------------------- |
| Unit        | Pytest         | Core logic            |
| Integration | k6/Locust      | Latency + correctness |
| Contract    | FHIR validator | Resource conformance  |

## Out of Scope

Items explicitly excluded.

## Implementation Notes

Technical hints, libraries, flags.

## Monitoring & Metrics

Key metrics to emit; log fields.

## Risks & Mitigation

| Risk | Impact | Mitigation |
| ---- | ------ | ---------- |

## Traceability

Links to spec sections & NFR codes.

## Open Questions

Unresolved items.
