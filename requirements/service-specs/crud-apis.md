# CRUD APIs Service Specification

## 1. Overview

The CRUD APIs provide internal data mutation and retrieval capabilities for FtRS domain entities: Organisation, Location, and HealthcareService. They are exposed as a FastAPI application (aggregated in `handler_main.py`) deployed behind AWS Lambda + API Gateway (Mangum adapter) and interact with a DynamoDB-backed repository layer (`ftrs_data_layer`). Organisation endpoints additionally expose a FHIR-compatible surface (resource path `/Organization`) returning `application/fhir+json` Bundles and `OperationOutcome` payloads for update responses and error conditions.

## 2. Scope & Intended Consumers

Internal platform components (ingestion workflows, administrative tooling, migration scripts) requiring authoritative create/update/delete operations. Not intended for direct external consumer use; external search/read use cases are served by gp-search APIs.

## 3. Domain Entities & Data Contracts

| Entity            | Key Identifier(s)                                   | Storage Model                    | API Representations                                                     |
| ----------------- | --------------------------------------------------- | -------------------------------- | ----------------------------------------------------------------------- |
| Organisation      | UUID (primary), ODS Code (`identifier_ODS_ODSCode`) | `Organisation` domain model      | FHIR `Organization` resource & internal JSON on create/delete responses |
| Location          | UUID                                                | `Location` domain model          | Internal JSON (create/update/delete), raw model dump                    |
| HealthcareService | UUID                                                | `HealthcareService` domain model | Internal JSON (create/update/delete), raw model dump                    |

### 3.1 Organisation FHIR Mapping

`organisations/app/router/organisation.py` uses `OrganizationMapper` to convert domain model(s) to a FHIR Bundle when reading. Update operations accept a FHIR Organization payload (validated by Pydantic validators) and produce an `OperationOutcome` with diagnostic codes: `success`, `information` (no change), or `exception`.

### 3.2 Error Model

| Layer                       | Mechanism                                                                              | FHIR Alignment                          | Example                                      |
| --------------------------- | -------------------------------------------------------------------------------------- | --------------------------------------- | -------------------------------------------- |
| Validation (payload/params) | Pydantic validators raising `OperationOutcomeException` (Organisation) or HTTP 422     | Uses OperationOutcome for FHIR surfaces | Missing required element -> `code=structure` |
| Not Found                   | HTTP 404 (Location & HealthcareService) / OperationOutcome (Organisation bundle empty) | 404 preserved                           | `/Organization/{id}` absent -> HTTP 404      |
| Unexpected Exception        | Wrapped in `OperationOutcomeException` (Organisation) else HTTP 500 with log code      | Returns `code=exception`                | Repository outage during update              |

## 4. Endpoints Summary

### 4.1 Organisation (FHIR)

| Method | Path                            | Query                           | Purpose           | Response                                   |
| ------ | ------------------------------- | ------------------------------- | ----------------- | ------------------------------------------ | ------------------------------------- |
| GET    | /Organization                   | `identifier=https://fhir.nhs.uk/Id/ods-organization-code | {ODS}` (optional) | Read one (by ODS) or all                   | FHIR Bundle (`application/fhir+json`) |
| GET    | /Organization/{organisation_id} | —                               | Read by UUID      | Organisation JSON (domain model)           |
| POST   | /Organization                   | —                               | Create            | 201 + Organisation JSON + message          |
| PUT    | /Organization/{organisation_id} | —                               | Update            | 200 `OperationOutcome` success/information |
| DELETE | /Organization/{organisation_id} | —                               | Delete            | 204 No Content                             |

### 4.2 Location

| Method | Path                    | Purpose        | Response            |
| ------ | ----------------------- | -------------- | ------------------- |
| GET    | /location/              | List locations | Array JSON          |
| GET    | /location/{location_id} | Read           | Location JSON       |
| POST   | /location/              | Create         | 201 + Location JSON |
| PUT    | /location/{location_id} | Update         | 200 + Location JSON |
| DELETE | /location/{location_id} | Delete         | 204 No Content      |

### 4.3 HealthcareService

| Method | Path                             | Purpose                            | Response            |
| ------ | -------------------------------- | ---------------------------------- | ------------------- |
| GET    | /healthcare-service/             | List services                      | Array JSON          |
| GET    | /healthcare-service/{service_id} | Read                               | Service JSON or 404 |
| POST   | /healthcare-service/             | Create (UUID assigned server-side) | 201 + Service JSON  |
| PUT    | /healthcare-service/{service_id} | Update                             | 200 + Service JSON  |
| DELETE | /healthcare-service/{service_id} | Delete                             | 204 No Content      |

## 5. Non-Functional Characteristics

| Aspect              | Implementation Notes                                                                                                                    | Referenced NFR Codes                  |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------- | ---------------------------------------------------- |
| Standards & Interop | FHIR JSON media type & OperationOutcome for Organisation; identifier parsing (`identifier=https://fhir.nhs.uk/Id/ods-organization-code                           | {code}`)                              | INT-001, INT-004, INT-005, INT-006, INT-007, INT-017 |
| Validation          | Pydantic validators for create/update enforce field presence & structure                                                                | INT-017                               |
| Error Handling      | Unified translation to OperationOutcome (organisation) + structured HTTP status semantics                                               | INT-005, REL-016                      |
| Logging             | `CrudApisLogBase` codes emit structured events per operation; includes identifiers for chain reconstruction                             | OBS-014, OBS-019                      |
| Auditability        | Create/Update/Delete events logged (extend to audit trail pipeline)                                                                     | OBS-022, OBS-023 (future enhancement) |
| Reliability         | Idempotent update path returns informational outcome when no changes applied                                                            | REL-016                               |
| Security            | Assumes upstream TLS termination & standard pipeline scanning; dependency vulnerability gating to be aligned with existing SEC controls | SEC-027, SEC-028                      |
| Performance         | Lightweight FastAPI + Mangum; baseline latency instrumentation via existing logging (extend with metrics)                               | PERF-001 (future association)         |

## 6. Data Validation & Identifier Normalisation

Organisation query parameter `identifier` is normalised to extract ODS code. STORY-208 drives tests ensuring uppercase/trim and format `https://fhir.nhs.uk/Id/ods-organization-code|{code}`. Invalid patterns will raise `OperationOutcome` with `code=structure`.

## 7. OperationOutcome Codes Catalogue (Initial)

| Code        | Severity    | Usage                                 |
| ----------- | ----------- | ------------------------------------- |
| success     | information | Update applied successfully           |
| information | information | No-op update (no field changes)       |
| structure   | error       | Payload or parameter validation error |
| exception   | error       | Unexpected server-side failure        |

## 8. Observability Strategy

1. Structured log codes (CrudApisLogBase) -> central log aggregation (NFR OBS-014/019).
2. Correlate with transaction / request IDs once middleware added (future story referencing INT-013).
3. Extend with p95 latency metric extraction for CRUD endpoints (planned link PERF-001).

## 9. Security & Compliance

Inherited platform controls (TLS, authentication boundary) enforced upstream. Pipeline to integrate dependency & container scanning ensuring SEC-027 / SEC-028 gating (STORY-216). No direct secrets logged; validation ensures potentially harmful input is constrained (INT-017). Future enhancement: mTLS / auth context propagation for audit.

## 10. Risks & Mitigations

| Risk                                               | Impact                         | Mitigation                                                                   |
| -------------------------------------------------- | ------------------------------ | ---------------------------------------------------------------------------- |
| Inconsistent error model across non-FHIR endpoints | Consumer confusion             | STORY-214 extends OperationOutcome-style mapping or unified format decisions |
| Missing audit trail for delete operations          | Compliance gap                 | STORY-215 introduces audit event contract                                    |
| Identifier format drift                            | Lookup failures                | STORY-208 validation & tests                                                 |
| Silent semantic loss on FHIR mapping               | Downstream data quality issues | STORY-210 round-trip mapping tests                                           |

## 11. Backlog Mapping

| Story     | Summary                                         | Key NFRs         |
| --------- | ----------------------------------------------- | ---------------- |
| STORY-208 | ODS identifier normalisation & logging          | INT-006, OBS-019 |
| STORY-209 | Organisation update OperationOutcome semantics  | INT-005, REL-016 |
| STORY-210 | FHIR bundle mapping & UK Core validation         | INT-001, INT-004 |
| STORY-211 | FHIR content negotiation enforcement            | INT-007          |
| STORY-212 | Payload input validation (create/update)        | INT-017          |
| STORY-213 | Structured logging across CRUD operations       | OBS-014, OBS-019 |
| STORY-214 | Consistent 404/500 error translation & handling | INT-005, REL-016 |
| STORY-215 | Audit event generation for CRUD changes         | OBS-022, OBS-023 |
| STORY-216 | Security scanning & dependency gating           | SEC-027, SEC-028 |

## 12. Acceptance & Exit Criteria

1. All stories 208–216 accepted with passing automated & manual tests.
2. Validator confirms all NFR references resolve.
3. No critical / high unresolved vulnerabilities (SEC-027/028) at merge.
4. Tag for initial CRUD spec published & linked in architecture docs.

## 13. Open Questions

| Topic                 | Question                                                                    | Next Step                             |
| --------------------- | --------------------------------------------------------------------------- | ------------------------------------- |
| Error model alignment | Should Location & HealthcareService adopt OperationOutcome for consistency? | Evaluate after baseline usage metrics |
| Authentication        | Will internal auth/mTLS be enforced at this layer or upstream gateway only? | Security design review                |
| Metrics               | Adopt standard p95/p99 per endpoint (Perf domain) now or post baseline?     | Decide after initial load tests       |

---

End of specification.

## 14. Developer Implementation Guide (Practical Step-by-Step)

This section translates the higher-level spec into concrete build steps a developer can follow for each endpoint. Treat each story as a vertical slice that results in tests + code + logging.

### 14.1 Environment & Project Setup

1. From repository root: `cd services/crud-apis/organisations` (or `location`, `healthcare_service`).
2. Install deps: `poetry install`.
3. Activate environment: `eval $(poetry environment activate)`.
4. Run unit tests baseline: `pytest -q` (should pass existing tests).

### 14.2 Common Coding Conventions

| Concern           | Convention                                                                                                                                         |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Logging           | Use `Logger.get(service="crud_<entity>_logger")` and emit predefined `CrudApisLogBase` codes. Include minimal contextual fields (ids).             |
| Validation        | Define/extend Pydantic validator models in `app/services/validators.py` per entity. Fail fast; do not write partial objects.                       |
| Error Handling    | For Organisation FHIR endpoints raise / translate to `OperationOutcomeException`. For others use HTTPException (404/500) until Story-214 decision. |
| Media Type        | Organisation responses set `media_type=application/fhir+json`.                                                                                     |
| Repository Access | Use `get_service_repository(<DomainClass>, "<lower-name>")` for consistency.                                                                       |
| Idempotency       | Updates return informational outcome when no net change (Story-209).                                                                               |
| Tests             | One test module per story (allowing refactor later). Name pattern: `test_story_<id>.py`.                                                           |

### 14.3 Endpoint Build Skeletons

Below are distilled handler patterns; copy and adapt rather than rewriting from scratch.

#### Organisation: GET /Organization (Story-210 & 208)

```python
@router.get("/Organization", response_class=JSONResponse)
async def list_or_single_org(request: Request, qp: OrganizationQueryParams = Depends(_get_organization_query_params)):
    organisation_service.check_organisation_params(request.query_params)  # validation (Story-208)
    if qp and qp.identifier:
        ods_code = qp.ods_code  # already normalised
        orgs = [organisation_service.get_by_ods_code(ods_code)]
    else:
        orgs = organisation_service.get_all_organisations()
    bundle = organisation_mapper.to_fhir_bundle(orgs)
    return JSONResponse(content=bundle.model_dump(mode="json"), media_type=FHIR_MEDIA_TYPE)
```

Tests to add:
| Case | Input | Expected |
|------|-------|----------|
| Single by ODS | identifier param | Bundle size=1 |
| All | none | Bundle size>=1 |
| Bad identifier | malformed param | OperationOutcome structure |

#### Organisation: PUT /Organization/{id} (Story-209)

Key branches:

1. Validate request body (Pydantic).
2. Call `process_organisation_update`; if returns False -> no-op outcome.
3. Map exceptions to OperationOutcome with `code=exception`.

Add explicit unit tests for: change applied, no change, exception path.

#### Location: DELETE /location/{id} (Story-214, baseline)

```python
@router.delete("/{location_id}")
async def delete_location(location_id: UUID):
    location_service_logger.log(CrudApisLogBase.LOCATION_008, location_id=location_id)
    location = location_repository.get(location_id)
    if not location:
        location_service_logger.log(CrudApisLogBase.LOCATION_E001, location_id=location_id)
        raise HTTPException(status_code=404, detail="Location not found")
    location_repository.delete(location_id)
    location_service_logger.log(CrudApisLogBase.LOCATION_009, location_id=location_id)
    return Response(status_code=204)
```

Enhancement (optional): wrap 500 errors for consistency (decision in Story-214).

### 14.4 Logging & Error Mapping Cheat Sheet

| Action               | Log Code                      | Success Response        | Failure Response           |
| -------------------- | ----------------------------- | ----------------------- | -------------------------- |
| Org create           | ORGANISATION_011 / \_015      | 201 + org JSON          | OperationOutcome exception |
| Org update no-op     | ORGANISATION_007              | 200 information outcome | exception outcome          |
| Org update changed   | ORGANISATION_005 / \_015      | 200 success outcome     | exception outcome          |
| Location delete      | LOCATION_008 / \_009          | 204                     | 404 not found              |
| Healthcare GET by id | HEALTHCARESERVICE_006 / \_008 | 200 service JSON        | 404 or 500 (mapped)        |

### 14.5 Suggested Test File Layout

```text
tests/unit/
  story_208/test_identifier_normalisation.py
  story_209/test_operation_outcome_update.py
  story_210/test_fhir_bundle_mapping.py
  story_211/test_content_negotiation.py
  story_212/test_payload_validation.py
  story_213/test_structured_logging.py
  story_214/test_error_translation.py
  story_215/test_audit_events.py (placeholder until audit implementation exists)
  story_216/test_security_scan_integration.py (may live in CI pipeline rather than unit)
```

### 14.6 Build Order Recommendation (Onboarding Path)

1. Story-208 identifier normalisation (low risk, clarifies query handling).
2. Story-210 bundle mapping & validation (core read path).
3. Story-209 update semantics (write path correctness).
4. Story-211 content negotiation (compliance surface).
5. Story-212 payload validation across entities.
6. Story-213 structured logging completeness.
7. Story-214 error translation consistency.
8. Story-215 audit events.
9. Story-216 security scanning integration.

### 14.7 Sprint Definition of Done Additions

| DoD Item            | Check                                                   |
| ------------------- | ------------------------------------------------------- |
| Story tests passing | Pytest green & coverage threshold met                   |
| NFR refs validated  | NFR toolkit validation command exit 0                   |
| Logging observed    | Sample log entry contains expected code & fields        |
| Error behaviour     | Manual negative tests produce specified outcomes        |
| Docs updated        | Spec & story acceptance criteria reflect implementation |

### 14.8 Quick Start Commands (Optional)

```bash
# Run only new crud story tests as they are added
pytest -q tests/unit/story_208

# Execute all crud-api story tests
pytest -q tests/unit/story_20[8-9] tests/unit/story_21[0-6]

# Validate NFR refs after adding stories using the external NFR toolkit
```

### 14.9 Future Enhancements (Backlog Candidates)

| Enhancement                                     | Rationale                        | Potential NFR Codes |
| ----------------------------------------------- | -------------------------------- | ------------------- |
| Unified OperationOutcome for non-FHIR endpoints | Consistency & tooling reuse      | INT-005, REL-016    |
| Add correlation id middleware                   | Cross-system tracing             | INT-013, OBS-019    |
| Metrics (p95 latency) extraction                | Performance visibility           | PERF-001, PERF-003  |
| Bulk/streaming mutation endpoints               | Efficiency for ingestion batches | SCAL-001, PERF-006  |

---

Developer guide appended to aid actionable implementation.
