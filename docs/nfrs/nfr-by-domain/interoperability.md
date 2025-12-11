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

## Controls

### INT-001

Resources conform to UK Core profiles ensuring national standard alignment.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-001](#int-001) | uk-core-profile-validation | Resources validated against UK Core profiles | 100% resources pass UK Core validation in CI and pre-release audit | FHIR validators + contract test suite | CI per build + quarterly audit | int,ref,prod | crud-apis,dos-search | draft | Ensures national standard alignment |

### INT-002

Versioning and deprecation policy is published for integrators.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-002](#int-002) | versioning-deprecation-policy | Versioning & deprecation policy published | Policy published; changes communicated; minimum 6 months deprecation window | Documentation repo + change comms channel | Review quarterly; update on change | prod | crud-apis,dos-search | draft | Reduces integration friction |

### INT-003

Minor releases remain backward compatible for the defined support window.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-003](#int-003) | backward-compatibility-window | Minor releases backward compatible for 12 months | No breaking changes; deprecation window \u226512 months; exceptions recorded | Contract tests + release notes | CI per build + release review | prod | crud-apis,dos-search | draft | Protects consumer integrations |

### INT-004

Semantic mappings preserve meaning when round-tripped between formats.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-004](#int-004) | semantic-roundtrip-fidelity | Semantic mapping round-trip fidelity preserved | Round-trip preserves fields and codes; divergence \u2264 1% | Mapping tests + diff reports | CI per build + monthly audit | int,ref | crud-apis,dos-search | draft | Maintains semantic integrity |

### INT-005

Error responses follow standard OperationOutcome structure.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-005](#int-005) | operationoutcome-structure | Standard OperationOutcome error structure enforced | 100% error responses conform to OperationOutcome spec | Contract tests + schema validators | CI per build + weekly contract audit | int,ref,prod | crud-apis,dos-search | draft | Ensures consistent error semantics across integrations |

### INT-006

Identifiers are normalised (case, trimming) for consistent matching.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-006](#int-006) | identifier-normalization-enforced | Identifier normalization applied (uppercase, trimmed) | 100% identifiers normalised; mismatches \u2264 0.1% | Normalization middleware + validation tests | CI per build + monthly audit | int,ref,prod | crud-apis,dos-search | draft | Ensures consistent identifier handling |

### INT-007

Strict content negotiation enforces supported media types only.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-007](#int-007) | strict-content-negotiation | Strict content negotiation implemented | Only documented media types accepted; correct response Content-Type | API contract tests + gateway policies | CI per build | int,ref,prod | crud-apis,dos-search | draft | Prevents ambiguity in accepted formats |

### INT-008

Reference data synchronises within defined latency (e.g., ≤24h).

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-008](#int-008) | reference-data-sync-latency | Reference data sync latency ≤24h | Sync completes within 24 hours | ETL scheduler + latency report | Daily | prod | etl-ods | draft | Timely reference data ensures correct behaviour |

### INT-009

Only documented FHIR search parameters are accepted; unknown ones rejected.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-009](#int-009) | documented-search-params-only | Only documented FHIR search params accepted | Unknown search params rejected with OperationOutcome | API gateway policy + contract tests | CI per build | int,ref,prod | crud-apis,dos-search | draft | Prevents ambiguity in search semantics |

### INT-010

Integration contract is version-controlled and published.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-010](#int-010) | version-controlled-contract | Version-controlled integration contract published | Contract published under version control; lint passes; updated \u22645 business days after change | Spec repo + Spectral lint + diff job | CI per build + weekly audit | int,ref,prod | crud-apis,dos-search | draft | Ensures consistent and timely documentation |

### INT-011

Machine-readable changelog is generated for each release.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-011](#int-011) | machine-readable-changelog | Machine-readable changelog generated | Changelog generated per release with breaking changes highlighted | Release pipeline + changelog generator | Per release | prod | crud-apis,dos-search | draft | Supports integrators with clear changes |

### INT-012

Terminology bindings are validated to ensure correct coding.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-012](#int-012) | terminology-binding-validation | Terminology bindings validated | 100% required bindings validated against value sets | Terminology server + validators | CI per build + monthly audit | int,ref,prod | crud-apis,dos-search | draft | Ensures correct coding practices |

### INT-013

Correlation IDs persist across internal and external calls for tracing.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-013](#int-013) | correlation-id-preserved | Correlation IDs preserved across calls | 100% requests preserve transaction_id/correlation_id in logs and headers | Middleware + log correlation tests | CI per build + monthly audit | int,ref,prod | crud-apis,dos-search | draft | Enables end-to-end tracing and diagnostics |

### INT-014

Null vs absent data semantics follow FHIR specification rules.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-014](#int-014) | null-vs-absent-semantics | Null vs absent data handled per FHIR | Responses follow FHIR rules; conformance tests pass | Contract tests + response validators | CI per build | int,ref,prod | crud-apis,dos-search | draft | Clarifies response semantics for consumers |

### INT-015

Test coverage spans ≥90% of defined interoperability scenarios.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-015](#int-015) | interoperability-scenario-coverage | \u226590% interoperability scenario coverage | \u226590% coverage across documented scenarios; exceptions recorded | Scenario test suite + coverage reports | CI per build + quarterly review | int,ref,prod | crud-apis,dos-search | draft | Ensures comprehensive interoperability validation |

### INT-016

Operations are stateless and do not rely on sequence order.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-016](#int-016) | stateless-sequence-independence | Stateless sequence-independent operations | 100% documented operations produce correct outcome independent of prior invocation order | Idempotence + shuffled sequence integration tests | CI per build + quarterly audit | int,ref,prod | crud-apis,dos-search | draft | Enables horizontal scaling and predictable consumer integration |

### INT-017

Input validation covers every field on every request to prevent malformed data.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-017](#int-017) | field-validation-complete | Complete field-level input validation every request | 100% of inputs validated; rich error responses on failure | Validation layer + contract tests | CI per build | int,ref,prod | crud-apis | draft | Protects system integrity via strict input validation |

### INT-018

Comprehensive OpenAPI documentation is published (overview, audience, related APIs, roadmap, SLA, tech stack, security/auth, test environment, onboarding, endpoints with examples) to support integrator adoption.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-018](#int-018) | api-documentation-completeness | Comprehensive published OpenAPI documentation | All required catalogue sections present; spec passes lint; updated ≤5 business days after prod change | Spectral lint + spec diff + manual checklist | CI per build + weekly audit | int,ref,prod | crud-apis,dos-search | draft | Reduces integration friction; ensures transparency for consumers |
