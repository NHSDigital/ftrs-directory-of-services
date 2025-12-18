# FtRS NFR – Interoperability

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Interoperability NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471146/Interoperability)

## NFR Codes

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| INT-001 | Resources validated against UK Core profiles | Resources conform to UK Core profiles ensuring national standard alignment. | [FTRS-978](https://nhsd-jira.digital.nhs.uk/browse/FTRS-978) |
| INT-002 | Versioning & deprecation policy published | Versioning and deprecation policy is published for integrators. | (none) |
| INT-003 | Minor releases backward compatible for 12 months | Minor releases remain backward compatible for the defined support window. | (none) |
| INT-004 | Semantic mapping round-trip fidelity preserved | Semantic mappings preserve meaning when round-tripped between formats. | (none) |
| INT-005 | Standard OperationOutcome error structure enforced | Error responses follow standard OperationOutcome structure. | (none) |
| INT-006 | Identifier normalization applied (uppercase, trimmed) | Identifiers are normalised (case, trimming) for consistent matching. | (none) |
| INT-007 | Strict content negotiation implemented | Strict content negotiation enforces supported media types only. | (none) |
| INT-008 | Reference data sync latency ≤24h | Reference data synchronises within defined latency (e.g., ≤24h). | (none) |
| INT-009 | Only documented FHIR search params accepted | Only documented FHIR search parameters are accepted; unknown ones rejected. | (none) |
| INT-010 | Version-controlled integration contract published | Integration contract is version-controlled and published. | (none) |
| INT-011 | Machine-readable changelog generated | Machine-readable changelog is generated for each release. | (none) |
| INT-012 | Terminology bindings validated | Terminology bindings are validated to ensure correct coding. | (none) |
| INT-013 | Correlation IDs preserved across calls | Correlation IDs persist across internal and external calls for tracing. | [FTRS-980](https://nhsd-jira.digital.nhs.uk/browse/FTRS-980) |
| INT-014 | Null vs absent data handled per FHIR | Null vs absent data semantics follow FHIR specification rules. | (none) |
| INT-015 | ≥90% interoperability scenario coverage | Test coverage spans ≥90% of defined interoperability scenarios. | (none) |
| INT-016 | Stateless sequence-independent operations | Operations are stateless and do not rely on sequence order. | (none) |
| INT-017 | Complete field-level input validation every request | Input validation covers every field on every request to prevent malformed data. | [FTRS-1488](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1488) |
| INT-018 | Comprehensive published OpenAPI documentation (overview, audience, related APIs, roadmap, SLA, tech stack, network access, security/auth, test environment, onboarding, endpoints with examples) | Comprehensive OpenAPI documentation is published (overview, audience, related APIs, roadmap, SLA, tech stack, security/auth, test environment, onboarding, endpoints with examples) to support integrator adoption. | (none) |
