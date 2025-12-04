# FtRS NFR – Interoperability

Source: requirements/nfrs/cross-references/nfr-matrix.md

This page is auto-generated; do not hand-edit.

## NFR Codes

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| INT-001 | Resources validated against UKCore profiles | Resources conform to UK Core profiles ensuring national standard alignment. | (none) |
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
| INT-018 | Comprehensive published OpenAPI documentation (overview, audience, related APIs, roadmap, SLA, tech stack, network access, security/auth, test env, onboarding, endpoints with examples) | Comprehensive OpenAPI documentation is published (overview, audience, related APIs, roadmap, SLA, tech stack, security/auth, test environment, onboarding, endpoints with examples) to support integrator adoption. | (none) |

## Controls

### INT-005

Error responses follow standard OperationOutcome structure.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| operationoutcome-structure | Standard OperationOutcome error structure enforced | 100% error responses conform to OperationOutcome spec | Contract tests + schema validators | CI per build + weekly contract audit | int,ref,prod | crud-apis,dos-search | draft | Ensures consistent error semantics across integrations |

### INT-007

Strict content negotiation enforces supported media types only.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| strict-content-negotiation | Strict content negotiation implemented | Only documented media types accepted; correct response Content-Type | API contract tests + gateway policies | CI per build | int,ref,prod | crud-apis,dos-search | draft | Prevents ambiguity in accepted formats |

### INT-008

Reference data synchronises within defined latency (e.g., ≤24h).

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| reference-data-sync-latency | Reference data sync latency ≤24h | Sync completes within 24 hours | ETL scheduler + latency report | Daily | prod | etl-ods | draft | Timely reference data ensures correct behaviour |

### INT-013

Correlation IDs persist across internal and external calls for tracing.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| correlation-id-preserved | Correlation IDs preserved across calls | 100% requests preserve transaction_id/correlation_id in logs and headers | Middleware + log correlation tests | CI per build + monthly audit | int,ref,prod | crud-apis,dos-search | draft | Enables end-to-end tracing and diagnostics |

### INT-016

Operations are stateless and do not rely on sequence order.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| stateless-sequence-independence | Stateless sequence-independent operations | 100% documented operations produce correct outcome independent of prior invocation order | Idempotence + shuffled sequence integration tests | CI per build + quarterly audit | int,ref,prod | crud-apis,dos-search | draft | Enables horizontal scaling and predictable consumer integration |

### INT-017

Input validation covers every field on every request to prevent malformed data.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| field-validation-complete | Complete field-level input validation every request | 100% of inputs validated; rich error responses on failure | Validation layer + contract tests | CI per build | int,ref,prod | crud-apis | draft | Protects system integrity via strict input validation |

### INT-018

Comprehensive OpenAPI documentation is published (overview, audience, related APIs, roadmap, SLA, tech stack, security/auth, test environment, onboarding, endpoints with examples) to support integrator adoption.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| api-documentation-completeness | Comprehensive published OpenAPI documentation | All required catalogue sections present; spec passes lint; updated ≤5 business days after prod change | Spectral lint + spec diff + manual checklist | CI per build + weekly audit | int,ref,prod | crud-apis,dos-search | draft | Reduces integration friction; ensures transparency for consumers |
