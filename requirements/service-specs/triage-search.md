---
title: Triage Code Search Service Specification
status: draft
version: 0.2.0
related_component: triage-search
last_updated: 2025-11-13
---

# Triage Code Search Service Specification

## 1. Overview
The Triage Code Search service provides a FHIR-based API for consumers to discover clinical or referral services matching one or more triage classification codes. Three code families are supported initially: SD, SG and DX. The service accepts a FHIR `Parameters` resource containing repeating code parameters and returns a FHIR `Bundle` (type `searchset`) of matching `HealthcareService` resources (optionally accompanied by `Organization` and `Location` resources when requested via include parameters). All errors are surfaced as FHIR `OperationOutcome`. Designed for low-latency query of multi-code combinations with rigorous validation and structured observability. This version (0.2.0) converts the prior custom JSON contract to a pure FHIR resource exchange to increase interoperability (INT-001, INT-004, INT-005, INT-017).

## 2. Scope
In-scope:
- Accept triage code criteria across SD / SG / DX families in a single FHIR `Parameters` resource.
- Validate code syntax, cardinality, emptiness, duplicates, and family presence at the Parameters layer.
- Perform search against indexed triage code relationships (data layer abstraction) to resolve matching service entities.
- Map internal service entities to FHIR `HealthcareService` resources with enrichment.
- Paginate results with a FHIR `Bundle` (`searchset`) including `total`, and maintain ordering by score.
- Optional inclusion of related `Organization` and `Location` resources either as separate entries (preferred) or as `contained` (future decision).
- Emit structured logs, correlation IDs, and performance metrics.
- Graceful error responses using FHIR `OperationOutcome`.

Out-of-scope (current version):
- Formal UKCore profile validation of `HealthcareService` (future INT-001 enhancement).
- Faceted filtering beyond triage codes (e.g. geography, availability windows).
- Partial text search / synonyms expansions.
- Write/update of service triage code mappings (managed by separate administration service).

## 3. Actors & Use Cases
Primary actor: External clinical triage / referral engine submitting triage codes to identify candidate services.
Secondary actors: Internal monitoring (synthetic probes), analytics pipeline for usage metrics.

Use cases:
1. Search services matching a set of SD codes only.
2. Search combining SD+SG+DX codes (intersection semantics default).
3. Construct fallback search with union semantics if intersection yields zero (optional parameter).
4. Receive validation feedback for malformed or unsupported codes.
5. Inspect pagination for large result sets.
6. Trace end-to-end correlation for a given triage request.

## 4. Interface Contract
### 4.1 Endpoint
FHIR Operation style (preferred): `POST /TriageService/$triage-search`

Alternative pragmatic REST path (still FHIR content): `POST /TriageService/search` (MUST send FHIR resources). The system SHOULD migrate to the operation name in production.

### 4.2 Request – FHIR `Parameters` Resource
Sample:
```json
{
    "resourceType": "Parameters",
    "parameter": [
        { "name": "SD", "valueCode": "SD123" },
        { "name": "SD", "valueCode": "SD456" },
        { "name": "SG", "valueCode": "SG789" },
        { "name": "DX", "valueCode": "DX321" },
        { "name": "mode", "valueCode": "intersection" },
        { "name": "page", "valueInteger": 1 },
        { "name": "page-size", "valueInteger": 25 },
        { "name": "include", "valueCode": "organization" },
        { "name": "include", "valueCode": "location" },
        { "name": "include", "valueCode": "triageCodes" },
        { "name": "correlation-id", "valueUuid": "6df0c32e-0dd1-4d33-9c2e-4cb7b8f9e111" }
    ]
}
```

Parameter names & semantics:
| Name | Cardinality | Type | Description |
|------|-------------|------|-------------|
| SD | 0..50 | code | SD family triage code (repeatable) |
| SG | 0..50 | code | SG family triage code (repeatable) |
| DX | 0..50 | code | DX family triage code (repeatable) |
| mode | 0..1 | code | `intersection` (default) or `union` |
| page | 0..1 | integer | Page number (>=1, default 1) |
| page-size | 0..1 | integer | Items per page (1..100, default 25) |
| include | 0..* | code | `organization`, `location`, `triageCodes` |
| correlation-id | 0..1 | uuid | External correlation identifier |

At least one triage code (any family) MUST be present.

### 4.3 Validation Rules (applied to Parameters)
| Aspect | Rule | Failure Mapping (OperationOutcome.issue) |
|--------|------|------------------------------------------|
| resourceType | MUST equal `Parameters` | severity=fatal, code=structure |
| Code presence | ≥1 SD/SG/DX parameter | severity=error, code=required |
| Family counts | Each family ≤50 codes | severity=error, code=value |
| Code format | Regex `^[A-Z]{2}[0-9]{3,6}$` (case-normalised uppercase) | severity=error, code=value, details.coding.code=`TRIAGE_CODE_INVALID` |
| Duplicates | Allowed; deduplicated internally; informational log only | severity=information (optional issue) |
| mode | `intersection` or `union` only | severity=error, code=value, details.coding.code=`TRIAGE_MODE_INVALID` |
| page | integer ≥1 | severity=error, code=value |
| page-size | 1..100 | severity=error, code=value |
| include | Must be one of allowed codes | severity=error, code=value |
| correlation-id | Must be valid UUID if present | severity=error, code=value |

### 4.4 Response – FHIR `Bundle` (Success 200)
Sample:
```json
{
    "resourceType": "Bundle",
    "type": "searchset",
    "total": 37,
    "link": [
        { "relation": "self", "url": "https://api.example.nhs.uk/TriageService/$triage-search" }
    ],
    "entry": [
        {
            "fullUrl": "https://api.example.nhs.uk/HealthcareService/svc-uuid",
            "resource": {
                "resourceType": "HealthcareService",
                "id": "svc-uuid",
                "name": "Service Name",
                "extension": [
                    {
                        "url": "http://example.nhs.uk/ftrs/extension/triage-codes",
                        "valueCodeableConcept": {
                            "coding": [
                                { "system": "http://example.nhs.uk/ftrs/triage/SD", "code": "SD123" },
                                { "system": "http://example.nhs.uk/ftrs/triage/SG", "code": "SG789" }
                            ]
                        }
                    },
                    { "url": "http://example.nhs.uk/ftrs/extension/search-score", "valueDecimal": 0.92 },
                    { "url": "http://example.nhs.uk/ftrs/extension/match-mode", "valueCode": "intersection" }
                ],
                "providedBy": { "reference": "Organization/org-uuid" },
                "location": [ { "reference": "Location/loc-uuid" } ]
            }
        },
        {
            "fullUrl": "https://api.example.nhs.uk/Organization/org-uuid",
            "resource": { "resourceType": "Organization", "id": "org-uuid", "name": "Org Name" }
        },
        {
            "fullUrl": "https://api.example.nhs.uk/Location/loc-uuid",
            "resource": { "resourceType": "Location", "id": "loc-uuid", "postalCode": "AB12 3CD" }
        }
    ]
}
```

Pagination: Subsequent pages MAY include `link` relations: `first`, `previous`, `next`, `last` with canonical URLs encoding page & page-size.

### 4.5 Error Responses – FHIR `OperationOutcome`
| Status | Condition | Notes |
|--------|-----------|-------|
| 400 | Any validation failure | Issues enumerated; MUST include correlation-id in diagnostics or extension |
| 404 | No services matched (optional alternative to 200 with empty `total`) | severity=information; code=`not-found` |
| 500 | Unhandled exception | severity=fatal; generic `internal-error` plus sanitized diagnostics |

### 4.6 Headers
`Content-Type: application/fhir+json`
`Accept: application/fhir+json`
`X-API-Key: <key>` (if protected by API Gateway)
`X-Correlation-ID: <uuid>` (propagated or generated) – if absent the service will inject and echo via an `extension` on `OperationOutcome` or propagate in logs.

### 4.7 OperationOutcome Issue Fields
| Field | Example |
|-------|---------|
| severity | error / fatal / informational |
| code | `value` / `required` / `code-invalid` / `structure` |
| details.coding[0].code | Domain-specific (e.g. `TRIAGE_CODE_INVALID`) |
| diagnostics | Human readable reason |

## 5. Search Semantics
- Intersection mode: Only services containing at least one code from each provided family are returned.
- Union mode: Services containing at least one code from any provided family included.
- Ranking: Default score = number of matched families + fractional weight per code matched (configurable). Future expansion: TF-IDF or usage-based prioritisation.
- Deduplication: A service appears once even if multiple matched codes across families.
- Bundle ordering MUST be descending by score; ties resolved by lexicographical `HealthcareService.id` for determinism (INT-004 consistency).

## 6. Data Flow
1. API Gateway receives POST operation request; correlation ID captured/created.
2. Lambda (Python) parses FHIR `Parameters`, normalises codes (uppercase) & validates.
3. Repository queries triage index fetching candidate service IDs per family.
4. Set operations combine ID lists according to `mode`.
5. Service details hydrated (batch get) + organization/location enrichment.
6. Scoring applied; results ordered & paginated.
7. FHIR `Bundle` constructed; structured logs & metrics emitted.
8. Errors diverted early into `OperationOutcome` before repository calls when possible.

## 7. Domain Models
| Model | Purpose |
|-------|---------|
| `FHIRParametersAdapter` | Converts incoming Parameters into internal request model |
| `TriageSearchRequest` | Internal validated representation (SD/SG/DX lists, mode, paging, include, correlation_id) |
| `ServiceEntity` | Internal service record (id, name, triageCodes, orgId, locationId) |
| `SearchResult` | Output DTO with enrichment & score |
| `BundleBuilder` | Assembles FHIR Bundle (entries & links) |

## 8. Architecture & Deployment
- Serverless: AWS Lambda (Python 3.12) via Poetry packaging.
- Data: DynamoDB triage code index tables (partition key: family, sort key: code; attribute listing service IDs). Secondary table with service details.
- Observability: Lambda Powertools (logging, metrics, tracing), X-Ray traces (validate correlation chain).
- Security: API Key / IAM authorizer; input validation rejects malformed codes; dependencies scanned (SEC-027/SEC-028). Potential future SNOMED CT terminology validation (INT-012).
- Reliability: Stateless, multi-AZ storage; graceful error fallback returning OperationOutcome.
- Scalability: Horizontal scaling via concurrent Lambdas; optimized index queries & batch hydration; pagination limits.
- Interoperability: FHIR-native contract eliminates custom JSON translation layer, reducing schema drift risk (INT-004).

## 9. Non-Functional Requirements Mapping
| Concern | NFR Codes | Rationale |
|---------|-----------|-----------|
| Latency & performance | PERF-001, PERF-003, PERF-005 | p50/p95 targets on Bundle response & pagination path; expectations versioned. |
| Telemetry overhead | PERF-007 | Structured logging/tracing within accepted overhead. |
| Reliability of search | REL-016 | Graceful error semantics via OperationOutcome. |
| Security (transport & scanning) | SEC-003, SEC-027, SEC-028 | TLS enforced, dependency & pipeline vuln scanning. |
| Observability (tracing & logs) | OBS-019, OBS-014, OBS-009 | Correlation chain, log schema, latency histograms. |
| Interoperability (FHIR resources & errors) | INT-001 (future), INT-004, INT-005, INT-006, INT-017 | FHIR-native exchange, semantic fidelity, error structure, normalization, comprehensive validation. |
| Terminology future-proofing | INT-012, INT-020 (future) | Potential SNOMED integration & search classification. |
| Cost efficiency | COST-001 | Mandatory tagging for resources. |
| Governance & assurance | GOV-001..GOV-016 | Pre-live approvals. |

## 10. Acceptance Quality Gates
- All validation failures return OperationOutcome with specific `details.coding.code` values (e.g. `TRIAGE_CODE_INVALID`, `TRIAGE_MODE_INVALID`).
- p95 latency for intersection search ≤ target threshold (define in performance expectations table).
- Pagination boundaries enforced (no >100 page-size returned).
- Structured log event includes: `correlation_id`, `search_mode`, `code_family_counts`, `result_total`, `duration_ms`.
- Empty intersection result returns Bundle with `total=0` (preferred) or optional 404 OperationOutcome (configurable).

## 11. Open Questions / Future Considerations
| Topic | Question | Next Step |
|-------|----------|-----------|
| Terminology standardisation | Are SD/SG/DX codes mapped to SNOMED CT? | Confirm with clinical taxonomy team. |
| Advanced ranking | Incorporate usage statistics or outcomes? | Evaluate data availability & privacy. |
| Faceted filtering | Geography, availability windows | Defer to future stories. |
| FHIR resource output | Provide `HealthcareService` Bundle? | Prototype after baseline stabilisation. |
| Caching strategy | Cache common code combinations? | Load test to determine benefit. |

## 12. Glossary
- SD / SG / DX Codes: Internal triage group families representing differing classification axes (exact semantics to be documented).
- Intersection Mode: Result must satisfy presence across all provided families.
- Union Mode: Result satisfies any provided family.
- OperationOutcome: FHIR resource for standardized error messaging.

## 13. Traceability
NFR codes referenced exist in registry `requirements/nfrs/cross-references/index.yaml`. User stories STORY-226..STORY-232 (triage search FHIR adoption) will update `nfr-matrix.md` accordingly.

## 14. Developer Implementation Guide
### 14.1 Input Contract (FHIR Parameters Adapter)
```python
CODE_REGEX = re.compile(r"^[A-Z]{2}[0-9]{3,6}$")

class TriageSearchRequest(BaseModel):
    SD: list[str] = Field(default_factory=list)
    SG: list[str] = Field(default_factory=list)
    DX: list[str] = Field(default_factory=list)
    mode: Literal["intersection", "union"] = "intersection"
    page: PositiveInt = 1
    page_size: conint(ge=1, le=100) = 25
    include: list[str] = Field(default_factory=list)
    correlation_id: Optional[str] = None

    @root_validator
    def validate_codes(cls, values):
        total = len(values['SD']) + len(values['SG']) + len(values['DX'])
        if total == 0:
            raise ValueError("At least one triage code required")
        for fam in ("SD", "SG", "DX"):
            arr = values[fam]
            if len(arr) > 50:
                raise ValueError(f"Family {fam} exceeds max 50 codes")
            for c in arr:
                uc = c.upper()
                if not CODE_REGEX.match(uc):
                    raise ValueError(f"Invalid code format: {c}")
        return values

def from_fhir_parameters(parameters: dict) -> TriageSearchRequest:
    """Convert a FHIR Parameters JSON dict to internal request model."""
    param_items = parameters.get("parameter", [])
    buckets: dict[str, list[str]] = {"SD": [], "SG": [], "DX": []}
    include: list[str] = []
    kwargs: dict[str, Any] = {}
    for p in param_items:
        name = p.get("name")
        if name in ("SD", "SG", "DX") and "valueCode" in p:
            buckets[name].append(p["valueCode"].upper())
        elif name == "mode" and "valueCode" in p:
            kwargs['mode'] = p['valueCode']
        elif name == "page" and 'valueInteger' in p:
            kwargs['page'] = p['valueInteger']
        elif name == "page-size" and 'valueInteger' in p:
            kwargs['page_size'] = p['valueInteger']
        elif name == "include" and 'valueCode' in p:
            include.append(p['valueCode'])
        elif name == "correlation-id" and 'valueUuid' in p:
            kwargs['correlation_id'] = p['valueUuid']
    return TriageSearchRequest(SD=buckets['SD'], SG=buckets['SG'], DX=buckets['DX'], include=include, **kwargs)
```

### 14.2 Repository Contract
```python
class TriageRepository(Protocol):
    def get_service_ids_by_codes(self, family: str, codes: list[str]) -> set[str]: ...
    def batch_get_services(self, ids: list[str]) -> list[ServiceEntity]: ...
```

### 14.3 Service Logic Skeleton
```python
def search(request: TriageSearchRequest, repo: TriageRepository) -> Bundle:
    correlation_id = fetch_or_set_correlation_id(request.correlation_id)
    logger.append_keys(correlation_id=correlation_id, mode=request.mode)
    family_results: dict[str, set[str]] = {}
    for fam, codes in (("SD", request.SD), ("SG", request.SG), ("DX", request.DX)):
        family_results[fam] = repo.get_service_ids_by_codes(fam, codes) if codes else set()
    if request.mode == 'intersection':
        non_empty_sets = [s for s in family_results.values() if s]
        combined = set.intersection(*non_empty_sets) if non_empty_sets else set()
    else:
        combined = set.union(*family_results.values())
    services = repo.batch_get_services(list(combined))
    scored = score_services(services, family_results)
    page_slice = paginate(scored, request.page, request.page_size)
    return build_fhir_bundle(page_slice, total=len(scored), request=request, correlation_id=correlation_id)
```

### 14.4 Scoring Example
```python
def score_services(services: list[ServiceEntity], family_results: dict[str, set[str]]) -> list[SearchResult]:
    scored = []
    for svc in services:
        families_matched = sum(1 for fam, ids in family_results.items() if svc.id in ids and ids)
        code_matches = 0
        for fam, ids in family_results.items():
            if svc.id in ids:
                code_matches += 1  # simplistic weight
        score = families_matched + code_matches * 0.1
        scored.append(SearchResult(service=svc, score=round(score, 3)))
    return sorted(scored, key=lambda r: r.score, reverse=True)
```

### 14.5 Test Layout
```
tests/unit/triage_search/
  test_validation.py
  test_intersection_mode.py
  test_union_mode.py
  test_scoring.py
  test_pagination.py
  test_operation_outcome_errors.py
  test_empty_results.py
```

### 14.6 Definition of Done Checklist
| Item | Criteria |
|------|----------|
| Validation | All listed rules enforced & negative tests pass |
| Performance | p95 latency within target for typical payload (≤ X ms) |
| Observability | Log includes correlation_id, duration_ms, result_total |
| Error Model | OperationOutcome conforms (severity/code/details/diagnostics) |
| Security | Dependency scans pass (SEC-027/028), TLS enforced |
| Docs | Spec updated & sample request/response confirmed |
| NFR Trace | Mapped codes verified by validator (future story) |

### 14.7 Future Enhancements
| Idea | Benefit | Candidate NFRs |
|------|---------|---------------|
| FHIR `Bundle` output | Interoperability with clinical systems | INT-001, INT-004 |
| SNOMED CT mapping | Standard terminology alignment | INT-012, INT-020 |
| Usage-based ranking | Relevance improvement | PERF-009, OBS-026 |
| Caching layer | Reduced latency for common queries | PERF-001, SCAL-001 |
| Parallel family lookups | Lower end-to-end latency | PERF-001, SCAL-005 |

---
End of triage-search specification.
