---
story_id: STORY-INT-006
jira_key:
title: Comprehensive OpenAPI Documentation Published for All Managed APIs
role: API Consumer Advocate
goal: Access consistent, complete, and accurate API documentation via NHS API Catalogue
value: Reduces integration friction, accelerates onboarding, improves safe reuse
nfr_refs: [INT-018]
status: draft
---

## Description

Produce and maintain a complete OpenAPI specification and associated catalogue documentation for each FtRS API exposed via Apigee (API Management). Documentation must satisfy interoperability transparency: functional overview, intended audience and use cases, related APIs, lifecycle status and roadmap, service level (SLA/SLO summary), technology stack, network access options (internet/HSCN), security & authorisation scheme, sandbox/test environment details, onboarding process steps, and full endpoint definitions with request/response schemas and illustrative examples.

## Acceptance Criteria

1. Plain English overview paragraph present (≤150 words) accurately describing core purpose.
2. Audience & permitted use section lists user groups + links to relevant "building healthcare software" guides.
3. Related APIs list includes FtRS and external dependencies (minimum 2 if applicable) with rationale.
4. Status & roadmap section declares current lifecycle stage (e.g. beta/GA) + next 2 planned milestones with indicative dates.
5. Service level section summarises availability & performance SLOs referencing authoritative NFR codes.
6. Technology stack section names primary frameworks/services (e.g. Apigee proxy, language runtime, data store) without internal secrets.
7. Network access options enumerate internet vs HSCN connectivity and any IP allowlist assumptions.
8. Security & authorisation section specifies auth flows (e.g. OAuth2 mTLS, API key) + required headers and token scopes with example.
9. Test/sandbox environment details include base URL, data characteristics (synthetic/anonymised), reset cadence, and usage limits.
10. Onboarding process checklist (≤12 steps) covers registration, credentials, test certification, production promotion.
11. OpenAPI spec contains all operations with summaries, descriptions, tags, parameter schemas, response schemas, error model, and at least one example per 2xx and representative error.
12. OpenAPI passes automated lint (no critical warnings) and schema validation tooling in CI.
13. Catalogue page renders required sections (manual verification) and links to downloadable spec.
14. Versioning & deprecation policy section references INT-002 and links changelog.
15. Documentation update process defined (owners + review cadence) and traceability note added.

## Non-Functional Acceptance

- Lint severity: 0 critical, ≤5 minor advisory items.
- Publish cadence: updates within 5 business days of a production API change.
- Traceability: spec version annotated with commit SHA and date.

## Implementation Notes

- Leverage existing OAS tooling (`spectral`, `openapi-diff`) in CI pipeline.
- Use shared error schema (OperationOutcome) to maintain interoperability (INT-005 link).
- Separate examples for common error codes (400 validation, 401 auth failure, 429 rate limit).

## Monitoring & Metrics

- `api_spec_publish_events_total` counter
- `api_spec_lint_errors_total` counter (labels: severity)
- `api_spec_outdated_days` gauge (derived: days since last prod change not reflected)

## Risks & Mitigation

| Risk                                          | Impact                 | Mitigation                                         |
| --------------------------------------------- | ---------------------- | -------------------------------------------------- |
| Incomplete examples reduce integrator clarity | Increased support load | Enforce example presence rule in lint              |
| Spec drift after rapid iteration              | Integration failures   | Automate diff + alert if >5 days stale             |
| Over-disclosure of internal tech              | Security posture risk  | Limit stack list to externally relevant components |

## Traceability

- NFR: INT-018
- Matrix: `nfr-matrix.md` updated with INT-018 row

## Open Questions

1. Should onboarding include automated self-service key issuance or manual review only?
2. Do we expose sandbox refresh schedule publicly or via support channel?
