---
title: Template
status: draft
version: 0.0.1
---
Copy this file to a new spec: `requirements/service-specs/<feature-name>.md`.
Keep sections even if initially empty; mark unknowns under Open Questions.

## 1. Overview

Purpose, target users/actors, primary value proposition, business outcomes.

## 2. Scope

In-scope capabilities (bullets) and explicit out-of-scope items.

## 3. Domain Context

Context diagram reference, upstream/downstream systems, triggering events.

## 4. Functional Flows

Sequence diagrams or step lists for key flows (Create, Update, Search, Error recovery).

## 5. Data Model

Key FHIR / domain resources, important fields, cardinalities, validation rules.

## 6. Interfaces / Endpoints

| Operation | Method | Path | Params | Returns | Errors |
| --------- | ------ | ---- | ------ | ------- | ------ |

Describe request/response examples (FHIR Bundles, OperationOutcome) and pagination parameters.

## 7. Non-Functional Requirements Mapping

List NFR codes (e.g., PERF-001, REL-001) with brief applicability notes.

## 8. Performance & Capacity

Expected volumes (RPS, daily totals), latency targets (link to performance expectations), concurrency profiles.

## 9. Reliability & Resilience

Failure modes, graceful degradation plan, retry strategies, circuit breaker logic.

## 10. Security & Privacy

AuthN/Z model, scopes/roles, data protection, audit trail, threat considerations.

## 11. Observability

Logging strategy (structured fields), metrics (names & types), traces/spans, alert rules.

## 12. Scalability

Horizontal/vertical scaling approach, statefulness constraints, partitioning strategy.

## 13. Compliance & Governance

Standards adhered to (FHIR versions, NHS guidelines), policy checks, review cadences.

## 14. Deployment & Migration

Configuration parameters, feature flags, rollout strategy, backfill or migration steps.

## 15. Risks & Mitigations

| Risk | Impact | Mitigation |
| ---- | ------ | ---------- |

## 16. Open Questions

List unknowns with owners and target resolution dates.

## 17. Decisions Log

| Decision | Context | Option Chosen | Rationale | Date | Owner |
| -------- | ------- | ------------- | --------- | ---- | ----- |

## 18. Glossary

Key terms and abbreviations.

## 19. Traceability

Mapping to user stories (placeholder IDs), test suites, and NFR codes.

## 20. Change History

| Version | Date | Author | Summary |
| ------- | ---- | ------ | ------- |
