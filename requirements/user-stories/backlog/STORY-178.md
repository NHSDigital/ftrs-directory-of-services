---
id: STORY-178
title: Map domain models to FHIR R4 resources in Bundle
status: draft
type: functional
owner: gp-search-team
nfr_refs:
  - PERF-003
  - OBS-009
summary: As a client I want FHIR-compliant resource representations so that downstream systems can interoperate reliably.
---

### Acceptance Criteria
1. Organization resource includes identifier with system odsOrganisationCode and value uppercase.
2. Endpoint resources include status, connection details and reference back to Organization.
3. Bundle type is `searchset` and total matches number of entries.
4. Latency metrics captured for mapping step (OBS-009 histogram contributes).
5. Mapping time within expectation threshold defined for action (PERF-003).

### Test Notes
| Scenario | Tool | Data | Expected |
|----------|------|------|----------|
| Mapping valid | pytest | Synthetic org + 2 endpoints | Bundle with Organization + 2 Endpoint entries |
| Empty endpoints | pytest | Org with zero endpoints | Bundle with Organization only; total=1 |
| No org | pytest | None | Empty Bundle; total=0 |

### Traceability
Performance expectation and latency observability applied to mapping.
