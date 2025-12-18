# FtRS NFR – Service: Ingress API – Domain: Interoperability

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Interoperability NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471146/Interoperability)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Interoperability | [INT-001](#INT-001) | Resources validated against UK Core profiles | Resources conform to UK Core profiles ensuring national standard alignment. | [FTRS-978](https://nhsd-jira.digital.nhs.uk/browse/FTRS-978) |
| Interoperability | [INT-002](#INT-002) | Versioning & deprecation policy published | Versioning and deprecation policy is published for integrators. | (none) |
| Interoperability | [INT-003](#INT-003) | Minor releases backward compatible for 12 months | Minor releases remain backward compatible for the defined support window. | (none) |
| Interoperability | [INT-004](#INT-004) | Semantic mapping round-trip fidelity preserved | Semantic mappings preserve meaning when round-tripped between formats. | (none) |
| Interoperability | [INT-005](#INT-005) | Standard OperationOutcome error structure enforced | Error responses follow standard OperationOutcome structure. | (none) |
| Interoperability | [INT-006](#INT-006) | Identifier normalization applied (uppercase, trimmed) | Identifiers are normalised (case, trimming) for consistent matching. | (none) |
| Interoperability | [INT-007](#INT-007) | Strict content negotiation implemented | Strict content negotiation enforces supported media types only. | (none) |
| Interoperability | [INT-009](#INT-009) | Only documented FHIR search params accepted | Only documented FHIR search parameters are accepted; unknown ones rejected. | (none) |
| Interoperability | [INT-010](#INT-010) | Version-controlled integration contract published | Integration contract is version-controlled and published. | (none) |
| Interoperability | [INT-011](#INT-011) | Machine-readable changelog generated | Machine-readable changelog is generated for each release. | (none) |
| Interoperability | [INT-012](#INT-012) | Terminology bindings validated | Terminology bindings are validated to ensure correct coding. | (none) |
| Interoperability | [INT-013](#INT-013) | Correlation IDs preserved across calls | Correlation IDs persist across internal and external calls for tracing. | [FTRS-980](https://nhsd-jira.digital.nhs.uk/browse/FTRS-980) |
| Interoperability | [INT-014](#INT-014) | Null vs absent data handled per FHIR | Null vs absent data semantics follow FHIR specification rules. | (none) |
| Interoperability | [INT-015](#INT-015) | ≥90% interoperability scenario coverage | Test coverage spans ≥90% of defined interoperability scenarios. | (none) |
| Interoperability | [INT-016](#INT-016) | Stateless sequence-independent operations | Operations are stateless and do not rely on sequence order. | (none) |
| Interoperability | [INT-017](#INT-017) | Complete field-level input validation every request | Input validation covers every field on every request to prevent malformed data. | [FTRS-1488](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1488) |
| Interoperability | [INT-018](#INT-018) | Comprehensive published OpenAPI documentation (overview, audience, related APIs, roadmap, SLA, tech stack, network access, security/auth, test environment, onboarding, endpoints with examples) | Comprehensive OpenAPI documentation is published (overview, audience, related APIs, roadmap, SLA, tech stack, security/auth, test environment, onboarding, endpoints with examples) to support integrator adoption. | (none) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### INT-001

Resources validated against UK Core profiles

See explanation: [INT-001](../../explanations.md#Explanations-INT-001)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| uk-core-profile-validation | Resources validated against UK Core profiles | 100% resources pass UK Core validation in CI and pre-release audit | CI per build + quarterly audit | int,ref,prod | Ingress API | draft | [FTRS-978](https://nhsd-jira.digital.nhs.uk/browse/FTRS-978) | Ensures national standard alignment |

### INT-002

Versioning & deprecation policy published

See explanation: [INT-002](../../explanations.md#Explanations-INT-002)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| versioning-deprecation-policy | Versioning & deprecation policy published | Policy published; changes communicated; minimum 6 months deprecation window | Review quarterly; update on change | prod | Ingress API | draft | (none) | Reduces integration friction |

### INT-003

Minor releases backward compatible for 12 months

See explanation: [INT-003](../../explanations.md#Explanations-INT-003)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| backward-compatibility-window | Minor releases backward compatible for 12 months | No breaking changes; deprecation window \u226512 months; exceptions recorded | CI per build + release review | prod | Ingress API | draft | (none) | Protects consumer integrations |

### INT-004

Semantic mapping round-trip fidelity preserved

See explanation: [INT-004](../../explanations.md#Explanations-INT-004)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| semantic-roundtrip-fidelity | Semantic mapping round-trip fidelity preserved | Round-trip preserves fields and codes; divergence \u2264 1% | CI per build + monthly audit | int,ref | Ingress API | draft | (none) | Maintains semantic integrity |

### INT-005

Standard OperationOutcome error structure enforced

See explanation: [INT-005](../../explanations.md#Explanations-INT-005)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| operationoutcome-structure | Standard OperationOutcome error structure enforced | 100% error responses conform to OperationOutcome spec | CI per build + weekly contract audit | int,ref,prod | Ingress API | draft | (none) | Ensures consistent error semantics across integrations |

### INT-006

Identifier normalization applied (uppercase, trimmed)

See explanation: [INT-006](../../explanations.md#Explanations-INT-006)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| identifier-normalization-enforced | Identifier normalization applied (uppercase, trimmed) | 100% identifiers normalised; mismatches \u2264 0.1% | CI per build + monthly audit | int,ref,prod | Ingress API | draft | (none) | Ensures consistent identifier handling |

### INT-007

Strict content negotiation implemented

See explanation: [INT-007](../../explanations.md#Explanations-INT-007)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| strict-content-negotiation | Strict content negotiation implemented | Only documented media types accepted; correct response Content-Type | CI per build | int,ref,prod | Ingress API | draft | (none) | Prevents ambiguity in accepted formats |

### INT-009

Only documented FHIR search params accepted

See explanation: [INT-009](../../explanations.md#Explanations-INT-009)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| documented-search-params-only | Only documented FHIR search params accepted | Unknown search params rejected with OperationOutcome | CI per build | int,ref,prod | Ingress API | draft | (none) | Prevents ambiguity in search semantics |

### INT-010

Version-controlled integration contract published

See explanation: [INT-010](../../explanations.md#Explanations-INT-010)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| version-controlled-contract | Version-controlled integration contract published | Contract published under version control; lint passes; updated \u22645 business days after change | CI per build + weekly audit | int,ref,prod | Ingress API | draft | (none) | Ensures consistent and timely documentation |

### INT-011

Machine-readable changelog generated

See explanation: [INT-011](../../explanations.md#Explanations-INT-011)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| machine-readable-changelog | Machine-readable changelog generated | Changelog generated per release with breaking changes highlighted | Per release | prod | Ingress API | draft | (none) | Supports integrators with clear changes |

### INT-012

Terminology bindings validated

See explanation: [INT-012](../../explanations.md#Explanations-INT-012)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| terminology-binding-validation | Terminology bindings validated | 100% required bindings validated against value sets | CI per build + monthly audit | int,ref,prod | Ingress API | draft | (none) | Ensures correct coding practices |

### INT-013

Correlation IDs preserved across calls

See explanation: [INT-013](../../explanations.md#Explanations-INT-013)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| correlation-id-preserved | Correlation IDs preserved across calls | 100% requests preserve transaction_id/correlation_id in logs and headers | CI per build + monthly audit | int,ref,prod | Ingress API | draft | [FTRS-980](https://nhsd-jira.digital.nhs.uk/browse/FTRS-980) | Enables end-to-end tracing and diagnostics |

### INT-014

Null vs absent data handled per FHIR

See explanation: [INT-014](../../explanations.md#Explanations-INT-014)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| null-vs-absent-semantics | Null vs absent data handled per FHIR | Responses follow FHIR rules; conformance tests pass | CI per build | int,ref,prod | Ingress API | draft | (none) | Clarifies response semantics for consumers |

### INT-015

≥90% interoperability scenario coverage

See explanation: [INT-015](../../explanations.md#Explanations-INT-015)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| interoperability-scenario-coverage | \u226590% interoperability scenario coverage | \u226590% coverage across documented scenarios; exceptions recorded | CI per build + quarterly review | int,ref,prod | Ingress API | draft | (none) | Ensures comprehensive interoperability validation |

### INT-016

Stateless sequence-independent operations

See explanation: [INT-016](../../explanations.md#Explanations-INT-016)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| stateless-sequence-independence | Stateless sequence-independent operations | 100% documented operations produce correct outcome independent of prior invocation order | CI per build + quarterly audit | int,ref,prod | Ingress API | draft | (none) | Enables horizontal scaling and predictable consumer integration |

### INT-017

Complete field-level input validation every request

See explanation: [INT-017](../../explanations.md#Explanations-INT-017)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| field-validation-complete | Complete field-level input validation every request | 100% of inputs validated; rich error responses on failure | CI per build | int,ref,prod | Ingress API | draft | [FTRS-1488](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1488) | Protects system integrity via strict input validation |

### INT-018

Comprehensive published OpenAPI documentation (overview, audience, related APIs, roadmap, SLA, tech stack, network access, security/auth, test environment, onboarding, endpoints with examples)

See explanation: [INT-018](../../explanations.md#Explanations-INT-018)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| api-documentation-completeness | Comprehensive published OpenAPI documentation | All required catalogue sections present; spec passes lint; updated ≤5 business days after prod change | CI per build + weekly audit | int,ref,prod | Ingress API | draft | (none) | Reduces integration friction; ensures transparency for consumers |
