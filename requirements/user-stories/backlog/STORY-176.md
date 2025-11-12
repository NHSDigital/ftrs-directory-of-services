---
id: STORY-176
title: Return FHIR Bundle for GP endpoints by ODS code
status: draft
type: functional
owner: gp-search-team
nfr_refs:
  - PERF-001
  - PERF-003
  - OBS-009
  - OBS-019
  - OBS-030
  - SEC-003
  - REL-002
summary: As an integration client I want to retrieve endpoint details for an organisation using its ODS code so that I can communicate with the correct GP systems.
---

### Acceptance Criteria
1. Given a valid identifier & _revinclude when Organisation exists then response is 200 and Bundle contains Organization + ≥1 Endpoint.
2. Given a valid identifier & _revinclude when Organisation not found then response is 200 and Bundle with type searchset contains no entries.
3. Response headers include `Content-Type: application/fhir+json`.
4. Latency p50 < baseline target and p95 within defined performance expectation (PERF-001/003).
5. Logs contain transaction id, ods_code and organisation_id (if found) (OBS-019).
6. Distributed trace spans cover handler, repository access & mapping (OBS-030).
7. Transport is TLS1.2+ only (SEC-003).

### Test Notes
| Scenario | Tool | Data | Expected |
|----------|------|------|----------|
| Existing org | pytest + synthetic fixture | Valid ODS code | Bundle with org + endpoints; latency assertions |
| Missing org | pytest + synthetic fixture | Valid ODS code not present | Empty Bundle; latency assertions |
| Trace coverage | local invocation + X-Ray | Any valid code | Spans for handler, repository, mapper present |

### Traceability
NFR codes referenced align with registry entries for performance, observability, security & reliability.
