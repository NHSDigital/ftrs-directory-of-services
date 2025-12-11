# FtRS NFR – Interoperability

This page is auto-generated; do not hand-edit.

## NFR Codes

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| INT-001 | Resources validated against UK Core profiles | Resources conform to UK Core profiles ensuring national standard alignment. | STORY-INT-018 |
| INT-002 | Versioning & deprecation policy published | Versioning and deprecation policy is published for integrators. | STORY-INT-019 |
| INT-003 | Minor releases backward compatible for 12 months | Minor releases remain backward compatible for the defined support window. | STORY-INT-020 |
| INT-004 | Semantic mapping round-trip fidelity preserved | Semantic mappings preserve meaning when round-tripped between formats. | STORY-INT-004 |
| INT-005 | Standard OperationOutcome error structure enforced | Error responses follow standard OperationOutcome structure. | STORY-INT-001 |
| INT-006 | Identifier normalization applied (uppercase, trimmed) | Identifiers are normalised (case, trimming) for consistent matching. | STORY-INT-021 |
| INT-007 | Strict content negotiation implemented | Strict content negotiation enforces supported media types only. | STORY-INT-002 |
| INT-008 | Reference data sync latency ≤24h | Reference data synchronises within defined latency (e.g., ≤24h). | STORY-INT-003 |
| INT-009 | Only documented FHIR search params accepted | Only documented FHIR search parameters are accepted; unknown ones rejected. | STORY-INT-022 |
| INT-010 | Version-controlled integration contract published | Integration contract is version-controlled and published. | STORY-INT-023 |
| INT-011 | Machine-readable changelog generated | Machine-readable changelog is generated for each release. | STORY-INT-024 |
| INT-012 | Terminology bindings validated | Terminology bindings are validated to ensure correct coding. | STORY-INT-005, STORY-INT-025 |
| INT-013 | Correlation IDs preserved across calls | Correlation IDs persist across internal and external calls for tracing. | STORY-INT-004, STORY-OBS-019 |
| INT-014 | Null vs absent data handled per FHIR | Null vs absent data semantics follow FHIR specification rules. | STORY-INT-026 |
| INT-015 | ≥90% interoperability scenario coverage | Test coverage spans ≥90% of defined interoperability scenarios. | STORY-INT-027 |
| INT-016 | Stateless sequence-independent operations | Operations are stateless and do not rely on sequence order. | STORY-INT-028 |
| INT-017 | Complete field-level input validation every request | Input validation covers every field on every request to prevent malformed data. | STORY-INT-017 |
| INT-018 | Comprehensive published OpenAPI documentation (overview, audience, related APIs, roadmap, SLA, tech stack, network access, security/auth, test environment, onboarding, endpoints with examples) | Comprehensive OpenAPI documentation is published (overview, audience, related APIs, roadmap, SLA, tech stack, security/auth, test environment, onboarding, endpoints with examples) to support integrator adoption. | STORY-INT-006, STORY-INT-029 |
