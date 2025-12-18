# FtRS NFR – Service: Ingress API – Domain: Performance

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Performance NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471098/Performance)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Performance | [PERF-001](#perf-001) | Each operation meets registry-defined percentile targets (p50/p95) logged & asserted (see performance/expectations.yaml) | Each API or batch operation meets agreed median and 95th percentile latency targets. | (none) |
| Performance | PERF-002 | Performance pillar checklist completed & actions closed | Performance pillar checklist is completed and any actions are closed. | (none) |
| Performance | PERF-003 | Performance expectations table versioned & referenced | The versioned performance expectations table is maintained and referenced by tests. | (none) |
| Performance | PERF-004 | Anonymised live-like dataset present & audited | A representative, anonymised dataset exists for realistic performance validation. | (none) |
| Performance | PERF-005 | Automated test suite matches defined actions & exclusions | Automated performance tests implement all defined actions and listed exclusions. | (none) |
| Performance | PERF-007 | Telemetry overhead within CPU & latency thresholds | Telemetry overhead (CPU, latency) remains within acceptable limits while capturing required data. | (none) |
| Performance | PERF-008 | 8h rolling window p95 variance ≤10% | Rolling window performance variance remains stable within target percentage bounds. | (none) |
| Performance | PERF-009 | Regression alert triggers on >10% p95 increase | Alerting triggers when p95 latency regresses beyond the defined threshold (e.g., >10%). | (none) |
| Performance | PERF-010 | Percentile methodology document & tool configuration aligned | Documented percentile methodology matches tool configuration (consistent measurement). | (none) |
| Performance | [PERF-013](#perf-013) | Request payload size per endpoint stays within the defined maximum (max_request_payload_bytes) | Endpoint request payloads remain under the maximum defined size to protect performance. | (none) |

## Operations

Operation: performance-specific expectation for an endpoint or job. Tied to a service and operation_id; sets p50/p95 latency, absolute max, burst/sustained TPS, payload limits, status, rationale, and stories.

| Operation ID | p50 ms | p95 ms | Max ms | Burst TPS | Sustained TPS | Max Payload (bytes) | Status | Stories | Rationale |
|--------------|--------|--------|--------|-----------|---------------|---------------------|--------|---------|-----------|
| Get HealthcareService (healthcare-service-get) | 50 | 120 | 350 |  |  |  | draft | (none) | Direct read + lightweight mapping |
| Get Organisation (org-get) | 40 | 100 | 300 |  |  |  | draft | (none) | Simple primary key lookup; cached storage path |
| Search by ODS (org-search-ods) | 60 | 140 | 400 |  |  |  | draft | (none) | ODS code normalization + single index scan |
| Update Organisation (org-update) | 70 | 150 | 400 |  |  |  | draft | (none) | Validation + persistence + OperationOutcome classification |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### PERF-001

Each operation meets registry-defined percentile targets (p50/p95) logged & asserted (see performance/expectations.yaml)

See explanation: [PERF-001](../../explanations.md#perf-001)

Sources: [Performance NFRs – Atomic Requirements](requirements/nfrs/areas/performance/overview.md#PERF-001)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Operation ID | p50 ms | p95 ms | Max ms | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|------------|------|------|------|---------|
| perf-org-get-latency | Assert p50/p95/max targets per operation | As per operations in PERF-001 (crud-apis endpoints) | continuous | prod | Ingress API | draft | (none) | Get Organisation (org-get) | 40 | 100 | 300 | Aligns with defined operation targets |
| perf-org-update-latency | Assert p50/p95/max targets per operation | As per operations in PERF-001 (crud-apis endpoints) | continuous | prod | Ingress API | draft | (none) | Update Organisation (org-update) | 70 | 150 | 400 | Aligns with defined operation targets |

### PERF-013

Request payload size per endpoint stays within the defined maximum (max_request_payload_bytes)

See explanation: [PERF-013](../../explanations.md#perf-013)

Sources: [Performance NFRs – Atomic Requirements](requirements/nfrs/areas/performance/overview.md#PERF-013)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Operation ID | Max Payload (bytes) | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|------------|-------------------|---------|
| perf-request-payload-limits | Maximum request payload size per endpoint 1MB | Max_request_payload_bytes enforced per endpoint per operations registry | CI per build + monthly audit | int,ref,prod | Ingress API | draft | (none) | Get HealthcareService (healthcare-service-get) |  | Prevents oversized payload degradation |
| perf-request-payload-limits | Maximum request payload size per endpoint 1MB | Max_request_payload_bytes enforced per endpoint per operations registry | CI per build + monthly audit | int,ref,prod | Ingress API | draft | (none) | Get Organisation (org-get) |  | Prevents oversized payload degradation |
| perf-request-payload-limits | Maximum request payload size per endpoint 1MB | Max_request_payload_bytes enforced per endpoint per operations registry | CI per build + monthly audit | int,ref,prod | Ingress API | draft | (none) | Search by ODS (org-search-ods) |  | Prevents oversized payload degradation |
| perf-request-payload-limits | Maximum request payload size per endpoint 1MB | Max_request_payload_bytes enforced per endpoint per operations registry | CI per build + monthly audit | int,ref,prod | Ingress API | draft | (none) | Update Organisation (org-update) |  | Prevents oversized payload degradation |
