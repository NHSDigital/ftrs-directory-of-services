---
title: DoS Search Service Specification
status: draft
version: 0.1.0
related_component: dos-search
last_updated: 2025-11-12
---


## 1. Overview

The DoS Search service (renamed from former "GP Search" on 2025-11-24) provides a FHIR R4 compliant read-only API for discovering an Organisation's electronic communication Endpoints by ODS (Organisation Data Service) code. It assembles a FHIR Bundle containing the `Organization` resource (if found) and its related `Endpoint` resources. It is optimised for low-latency clinical and integration use cases.

## 2. Scope

In-scope:

- Retrieval of Organisation and Endpoint records from the FtRS data layer via DynamoDB repository abstraction.
- Validation and transformation of request query parameters to internal model.
- Mapping domain models to FHIR R4 resources.
- Emission of structured logs and distributed traces.
- Graceful error responses using `OperationOutcome`.
- Performance profiling and regression detection for the primary search action.

Out-of-scope (initial version):

- Write/update operations.
- Bulk search or multi-criteria filtering beyond ODS code.
- Authentication/authorisation implementation details (delegated to API Gateway / platform layer).
- UI rendering (service is headless API).

## 3. Actors & Use Cases

Primary actor: External clinical system / integration adapter calling the API to locate Directory of Services (DoS) endpoints.
Secondary actor: Internal monitoring & synthetic probes validating availability/performance.

Key use cases:

1. Fetch endpoints for an Organisation by ODS code.
2. Receive validation guidance when parameters are malformed.
3. Observe latency, throughput and traces for operational diagnostics.
4. Detect and alert on performance regressions or abnormal variability.

## 4. Interface Contract

### 4.1 Endpoint

`GET /Organization`

### 4.2 Required Query Parameters

| Name          | Example                 | Description                                                   |
| ------------- | ----------------------- | ------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `identifier`  | `odsOrganisationCode    | A1234`                                                        | Encoded ODS code with system prefix. Must match regex `^[A-Za-z0-9]{5,12}$` after separator. |
| `_revinclude` | `Endpoint:organization` | Instructs inclusion of linked Endpoint resources (mandatory). |

### 4.3 Responses

| Status | Condition               | Payload                                                                        | Notes                                                            |
| ------ | ----------------------- | ------------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| 200    | Valid request processed | `Bundle` (type=`searchset`) containing 0..1 `Organization` and 0..N `Endpoint` | Empty Bundle if no organisation/endpoints found.                 |
| 400    | Validation failure      | `OperationOutcome`                                                             | Includes issue entries with UK Core error coding and diagnostics. |
| 500    | Unhandled exception     | `OperationOutcome`                                                             | Generic fatal structure issue for internal failure.              |

### 4.4 Headers

`Content-Type: application/fhir+json`
`Accept: application/fhir+json`

### 4.5 Error Model (OperationOutcome issue fields)

| Field                    | Description                                                                 |
| ------------------------ | --------------------------------------------------------------------------- | ----- |
| `severity`               | error                                                                       | fatal |
| `code`                   | `value` / `code-invalid` / `required` / `structure`                         |
| `details.coding[0].code` | UK Core SpineErrorOrWarningCode (e.g. `INVALID_SEARCH_DATA`)                 |
| `diagnostics`            | Human-readable explanation (e.g. invalid identifier system, missing param). |

## 5. Data Flow

1. API Gateway receives HTTP GET with query parameters.
2. Lambda handler validates parameters via `OrganizationQueryParams` (Pydantic).
3. Repository (`get_service_repository`) fetches Organisation record + endpoints from DynamoDB.
4. `BundleMapper` constructs FHIR resources & aggregates into a `Bundle`.
5. Response serialized with `body=fhir_resource.model_dump_json()` and returned.
6. Structured logs & traces emitted (Powertools Logger/Tracer).

## 6. Domain Models

### 6.1 Organization

Minimal fields required for mapping (id, identifiers, name, endpoints). Additional attributes may be passed through as supported by FHIR `Organization` resource profile.

### 6.2 Endpoint

Contains connection details (address, payloadType, status). Associated to Organisation via reference.

## 7. Architecture & Deployment

- Serverless compute: AWS Lambda (Python 3.12) packaged via Poetry.
- Data: DynamoDB (partitioned by entity type, keyed by ODS code or internal id).
- Observability: AWS Lambda Powertools (structured logging, tracing), X-Ray integration, metrics export (latency histograms, TPS).
- Security: TLS enforced via API Gateway; request validation ensures ODS codes conform; dependencies scanned in CI.
- Availability & Reliability: Multi-AZ DynamoDB; Lambda service inherently multi-AZ; blue/green deployment strategy for zero downtime.
- Scalability: Stateless Lambda scales horizontally; DynamoDB auto-scaling manages throughput.

## 8. Non-Functional Requirements Mapping

| Concern                                 | NFR Codes                                                              | Application Rationale                                                                                                                                            |
| --------------------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Latency baseline                        | PERF-001, PERF-003                                                     | Define and assert p50/p95 targets for GET /Organization.                                                                                                         |
| Performance governance                  | PERF-002, PERF-010                                                     | Pillar checklist & standard percentile methodology adoption.                                                                                                     |
| Dataset realism                         | PERF-004                                                               | Use anonymised live-like dataset for load tests.                                                                                                                 |
| Targeted performance tests              | PERF-005                                                               | Suite covers only critical action (search by ODS).                                                                                                               |
| Batch impact protection                 | PERF-006                                                               | Ensure background tasks don't materially raise p95.                                                                                                              |
| Telemetry overhead                      | PERF-007                                                               | Structured logging/tracing overhead within thresholds.                                                                                                           |
| Stability & regression alerts           | PERF-008, PERF-009                                                     | Rolling variance & alerting on >10% p95 increase.                                                                                                                |
| Security (transport, vuln mgmt)         | SEC-003, SEC-027, SEC-028, SEC-009                                     | TLS enforced; dependency scans; ASVS coverage & release gates.                                                                                                   |
| Reliability (graceful errors, multi-AZ) | REL-002, REL-016                                                       | Fault-tolerance & user-friendly error responses.                                                                                                                 |
| Availability                            | AVAIL-001, AVAIL-010                                                   | Multi-AZ SLA & zero-downtime deployments.                                                                                                                        |
| Scalability                             | SCAL-001, SCAL-005                                                     | Horizontal Lambda scale & autoscaling guardrails.                                                                                                                |
| Observability (logging/tracing/latency) | OBS-009, OBS-019, OBS-030, OBS-011, OBS-017, OBS-021, OBS-024, OBS-007 | Latency histograms, transaction correlation, distributed traces, failure classification, dynamic log levels, transaction ids, alert rules & telemetry freshness. |
| Governance & approvals                  | GOV-001..GOV-016                                                       | Full assurance chain required pre-live.                                                                                                                          |

## 9. Acceptance Quality Gates (Summary)

- p95 latency < defined target (see performance expectations table).
- Structured logs include transaction & organization identifiers when present.
- OperationOutcome produced for all validation failures with appropriate codes.
- No unencrypted PID exposure (if future fields added) – SEC-026 future consideration.

## 10. Open Questions / Future Considerations

| Topic          | Question                                                         | Next Step                                                  |
| -------------- | ---------------------------------------------------------------- | ---------------------------------------------------------- |
| Authentication | Will endpoint require user-level auth vs system integration key? | Confirm with security architecture (SEC-012 alignment).    |
| Caching        | Should frequent ODS lookups employ in-memory or CDN caching?     | Evaluate latency benefit vs consistency needs.             |
| PID Data       | Potential future inclusion of patient-facing endpoints?          | Re-assess SEC-025/SEC-026 implications.                    |
| FHIR Profiles  | Need to constrain to UK Core profiles?                            | Align with standards group & add validation layer.         |
| Rate Limiting  | Per-ODS request throttling for abuse prevention?                 | Integrate WAF / API Gateway usage plans (REL-004 synergy). |

## 11. Glossary

- ODS Code: Identifier assigned by Organisation Data Service.
- FHIR Bundle: Aggregated collection of FHIR resources.
- OperationOutcome: Standard FHIR resource for conveying errors.

## 12. Traceability

All mapped NFR codes present in canonical registry `requirements/nfrs/cross-references/index.yaml`. (Historical reference to STORY-176..STORY-185 deprecated; see current backlog stories under `requirements/user-stories/backlog/` for active traceability.)

---

End of specification.
