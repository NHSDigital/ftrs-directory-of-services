# FtRS NFR – Interoperability

Source: requirements/nfrs/cross-references/nfr-matrix.md

This page is auto-generated; do not hand-edit.

## NFR Codes

### Missing Metadata Checklist

- [Stories] INT-001
- [Stories] INT-002
- [Stories] INT-003
- [Stories] INT-006
- [Stories] INT-009
- [Stories] INT-010
- [Stories] INT-011
- [Stories] INT-012
- [Stories] INT-014
- [Stories] INT-015
- [Stories] INT-016
- [Stories] INT-018

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| INT-001 | Resources validated against UK Core profiles | Resources conform to UK Core profiles ensuring national standard alignment. | (none) |
| INT-002 | Versioning & deprecation policy published | Versioning and deprecation policy is published for integrators. | (none) |
| INT-003 | Minor releases backward compatible for 12 months | Minor releases remain backward compatible for the defined support window. | (none) |
| INT-004 | Semantic mapping round-trip fidelity preserved | Semantic mappings preserve meaning when round-tripped between formats. | STORY-INT-004 |
| INT-005 | Standard OperationOutcome error structure enforced | Error responses follow standard OperationOutcome structure. | STORY-INT-001 |
| INT-006 | Identifier normalization applied (uppercase, trimmed) | Identifiers are normalised (case, trimming) for consistent matching. | (none) |
| INT-007 | Strict content negotiation implemented | Strict content negotiation enforces supported media types only. | STORY-INT-002 |
| INT-008 | Reference data sync latency ≤24h | Reference data synchronises within defined latency (e.g., ≤24h). | STORY-INT-003 |
| INT-009 | Only documented FHIR search params accepted | Only documented FHIR search parameters are accepted; unknown ones rejected. | (none) |
| INT-010 | Version-controlled integration contract published | Integration contract is version-controlled and published. | (none) |
| INT-011 | Machine-readable changelog generated | Machine-readable changelog is generated for each release. | (none) |
| INT-012 | Terminology bindings validated | Terminology bindings are validated to ensure correct coding. | (none) |
| INT-013 | Correlation IDs preserved across calls | Correlation IDs persist across internal and external calls for tracing. | STORY-INT-004 |
| INT-014 | Null vs absent data handled per FHIR | Null vs absent data semantics follow FHIR specification rules. | (none) |
| INT-015 | ≥90% interoperability scenario coverage | Test coverage spans ≥90% of defined interoperability scenarios. | (none) |
| INT-016 | Stateless sequence-independent operations | Operations are stateless and do not rely on sequence order. | (none) |
| INT-017 | Complete field-level input validation every request | Input validation covers every field on every request to prevent malformed data. | STORY-INT-005, STORY-INT-017 |
| INT-018 | Comprehensive published OpenAPI documentation (overview, audience, related APIs, roadmap, SLA, tech stack, network access, security/auth, test environment, onboarding, endpoints with examples) | Comprehensive OpenAPI documentation is published (overview, audience, related APIs, roadmap, SLA, tech stack, security/auth, test environment, onboarding, endpoints with examples) to support integrator adoption. | (none) |
