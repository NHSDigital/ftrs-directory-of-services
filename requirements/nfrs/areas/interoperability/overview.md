# Interoperability NFRs Overview

## Purpose

Ensure the Find the Right Service (FtRS) platform exchanges data using consistent, standards-based, lossless representations that minimise integration friction and regression risk while supporting safe evolution.

## Goals

- Conform to FHIR R4 & UK Core profiles for resource structures.
- Provide predictable versioning and deprecation lifecycle for integrators.
- Preserve clinical semantics in transformations (lossless or explicitly documented reductions).
- Maintain identifier and terminology consistency across systems.
- Offer stable, machine-readable contracts and changelogs for automation.
- Sustain high-quality interoperability test coverage.

## Scope

Applies to all API endpoints and data exchange processes in every environment (dev, int, ref, sandpit, prod). Complements existing domains (governance, performance, reliability, accessibility, compatibility) rather than duplicating them.

## NFR Codes

Refer to canonical registry `index.yaml` for INT-001..INT-015 definitions.

| Code    | Theme                      | Summary                                                   |
| ------- | -------------------------- | --------------------------------------------------------- |
| INT-001 | Standards Compliance       | Validate resources against UK Core profiles                |
| INT-002 | Versioning                 | Publish version & deprecation policy                      |
| INT-003 | Backward Compatibility     | Guarantee non-breaking minor releases for defined window  |
| INT-004 | Semantic Fidelity          | Round-trip mapping retains clinical meaning               |
| INT-005 | Error Consistency          | Standard OperationOutcome shape & codes                   |
| INT-006 | Identifier Normalisation   | Consistent ODS code formatting                            |
| INT-007 | Content Negotiation        | Restrict/validate media types                             |
| INT-008 | Reference Data Currency    | Timely ODS sync (≤24h)                                    |
| INT-009 | Discoverability            | Standard FHIR search parameters only                      |
| INT-010 | Contract Publication       | Version-controlled integration specs                      |
| INT-011 | Machine-readable Changelog | Structured diff per release                               |
| INT-012 | Terminology Validation     | Enforce bindings for codes/valuesets                      |
| INT-013 | Correlation Preservation   | Maintain cross-system trace IDs                           |
| INT-014 | Null/Absent Semantics      | Follow FHIR guidelines for data absence                   |
| INT-015 | Test Coverage              | ≥90% critical exchange scenarios covered                  |
| INT-016 | Stateless Operations       | Operations remain stateless & sequence-independent        |
| INT-017 | Input Validation           | Complete field-level input validation every request       |
| INT-018 | API Documentation          | Comprehensive published OpenAPI & catalogue documentation |

## Verification Approach

- CI pipeline stages: profile validation (INT-001), terminology checks (INT-012), contract diff generation (INT-011).
- Automated contract and changelog publication on tagged releases (INT-002, INT-010, INT-011).
- Integration test suite executes scenario manifest and reports coverage (INT-015).
- Load & functional tests assert correlation ID propagation (INT-013).
- Mapping tests perform round-trip transforms and compare source vs output fields (INT-004).
- Negative API tests enforce content negotiation & error conformity (INT-005, INT-007).
- Scheduled sync job metrics reported for reference data latency (INT-008).

## Maturity & Roadmap

All INT codes start as `draft`. Progression to `approved` requires:

1. Tooling implemented and passing for ≥3 consecutive releases.
2. Coverage threshold (INT-015) achieved and sustained.
3. No unresolved high-severity interoperability defects for 90 days.

## Traceability

Each INT code will have an associated user story (STORY-186..STORY-200) linking acceptance criteria & tests. Matrix entries will map codes to stories for auditability.

## Open Questions

| Topic                  | Question                                                     | Action                         |
| ---------------------- | ------------------------------------------------------------ | ------------------------------ |
| Deprecation Window     | Is 12 months backward compatibility sufficient?              | Gather integrator feedback Q1. |
| Changelog Format       | JSON vs OpenAPI extension vs FHIR CapabilityStatement delta? | Prototype & select.            |
| Reference Data Latency | Tighten from 24h to 6h if feasible?                          | Evaluate ops cost vs benefit.  |
| Terminology Expansion  | Additional bindings required for future resources?           | Monitor roadmap revisions.     |

## Success Metrics

- ≤2% of production incidents related to interoperability defects.
- <10% of integration onboarding time spent resolving contract ambiguities.
- Test suite coverage ≥90% maintained across releases.

---

End of overview.
