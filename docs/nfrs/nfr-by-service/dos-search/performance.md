# FtRS NFR – Service: DoS Search – Domain: Performance

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Performance NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471098/Performance)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Performance | [PERF-001](../../explanations.md#Explanations-PERF-001) | Each operation meets registry-defined percentile targets (p50/p95) logged & asserted (see performance/expectations.yaml) | Each API or batch operation meets agreed median and 95th percentile latency targets. | [FTRS-1382](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1382), [FTRS-887](https://nhsd-jira.digital.nhs.uk/browse/FTRS-887) |
| Performance | [PERF-002](../../explanations.md#Explanations-PERF-002) | Performance pillar checklist completed & actions closed | Performance pillar checklist is completed and any actions are closed. | (none) |
| Performance | [PERF-003](../../explanations.md#Explanations-PERF-003) | Performance expectations table versioned & referenced | The versioned performance expectations table is maintained and referenced by tests. | (none) |
| Performance | [PERF-004](../../explanations.md#Explanations-PERF-004) | Anonymised live-like dataset present & audited | A representative, anonymised dataset exists for realistic performance validation. | (none) |
| Performance | [PERF-005](../../explanations.md#Explanations-PERF-005) | Automated test suite matches defined actions & exclusions | Automated performance tests implement all defined actions and listed exclusions. | (none) |
| Performance | [PERF-007](../../explanations.md#Explanations-PERF-007) | Telemetry overhead within CPU & latency thresholds | Telemetry overhead (CPU, latency) remains within acceptable limits while capturing required data. | (none) |
| Performance | [PERF-008](../../explanations.md#Explanations-PERF-008) | 8h rolling window p95 variance ≤10% | Rolling window performance variance remains stable within target percentage bounds. | (none) |
| Performance | [PERF-009](../../explanations.md#Explanations-PERF-009) | Regression alert triggers on >10% p95 increase | Alerting triggers when p95 latency regresses beyond the defined threshold (e.g., >10%). | (none) |
| Performance | [PERF-010](../../explanations.md#Explanations-PERF-010) | Percentile methodology document & tool configuration aligned | Documented percentile methodology matches tool configuration (consistent measurement). | (none) |
| Performance | [PERF-011](../../explanations.md#Explanations-PERF-011) | Endpoints sustain burst TPS at or above the defined target (burst_tps_target) | GP search endpoints handle short burst throughput at or above the target TPS. | [FTRS-1382](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1382), [FTRS-738](https://nhsd-jira.digital.nhs.uk/browse/FTRS-738), [FTRS-831](https://nhsd-jira.digital.nhs.uk/browse/FTRS-831) |
| Performance | [PERF-012](../../explanations.md#Explanations-PERF-012) | Endpoints sustain steady-state TPS at or above the defined target (sustained_tps_target) | GP search endpoints sustain steady-state throughput at or above the TPS target. | [FTRS-1382](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1382), [FTRS-1650](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1650), [FTRS-1690](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1690), [FTRS-738](https://nhsd-jira.digital.nhs.uk/browse/FTRS-738) |
| Performance | [PERF-013](../../explanations.md#Explanations-PERF-013) | Request payload size per endpoint stays within the defined maximum (max_request_payload_bytes) | Endpoint request payloads remain under the maximum defined size to protect performance. | (none) |

## Operations

Operation: performance-specific expectation for an endpoint or job. Tied to a service and operation_id; sets p50/p95 latency, absolute max, burst/sustained TPS, payload limits, status, rationale, and stories.

| Operation ID | p50 ms | p95 ms | Max ms | Burst TPS | Sustained TPS | Max Payload (bytes) | Status | Stories | Rationale |
|--------------|--------|--------|--------|-----------|---------------|---------------------|--------|---------|-----------|
| Search by ODS code (dos-lookup-ods) | 150 | 300 | 500 | 150 | 150 | 1048576 | draft | [FTRS-1382](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1382), [FTRS-831](https://nhsd-jira.digital.nhs.uk/browse/FTRS-831), [FTRS-887](https://nhsd-jira.digital.nhs.uk/browse/FTRS-887) | Direct ODS code lookup; largely cacheable |
| Nearby Services (dos-nearby) | 150 | 300 | 500 | 150 | 150 | 1048576 | draft | [FTRS-831](https://nhsd-jira.digital.nhs.uk/browse/FTRS-831) | Geo filtering + limited enrichment |
| Search (GP) (dos-search) | 150 | 300 | 500 | 150 | 150 | 1048576 | draft | [FTRS-1690](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1690), [FTRS-831](https://nhsd-jira.digital.nhs.uk/browse/FTRS-831) | Primary user-facing query; critical perceived responsiveness |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### PERF-001

Each operation meets registry-defined percentile targets (p50/p95) logged & asserted (see performance/expectations.yaml)

See explanation: [PERF-001](../../explanations.md#Explanations-PERF-001)

Sources: [Performance NFRs – Atomic Requirements](requirements/nfrs/areas/performance/overview.md#PERF-001)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Operation ID | p50 ms | p95 ms | Max ms | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|------------|------|------|------|---------|
| perf-dos-search-latency | Assert p50/p95/max targets per operation | As per operations in PERF-001 (dos-search endpoints) | continuous | prod | DoS Search | draft | [FTRS-1690](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1690), [FTRS-831](https://nhsd-jira.digital.nhs.uk/browse/FTRS-831) | Search (GP) (dos-search) | 150 | 300 | 500 | Aligns with defined operation targets |
| perf-lookup-ods-latency | Assert p50/p95/max targets per operation | As per operations in PERF-001 (dos-search endpoints) | continuous | prod | DoS Search | draft | [FTRS-1382](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1382), [FTRS-831](https://nhsd-jira.digital.nhs.uk/browse/FTRS-831), [FTRS-887](https://nhsd-jira.digital.nhs.uk/browse/FTRS-887) | Search by ODS code (dos-lookup-ods) | 150 | 300 | 500 | Aligns with defined operation targets |
| perf-nearby-latency | Assert p50/p95/max targets per operation | As per operations in PERF-001 (dos-search endpoints) | continuous | prod | DoS Search | draft | [FTRS-831](https://nhsd-jira.digital.nhs.uk/browse/FTRS-831) | Nearby Services (dos-nearby) | 150 | 300 | 500 | Aligns with defined operation targets |

### PERF-011

Endpoints sustain burst TPS at or above the defined target (burst_tps_target)

See explanation: [PERF-011](../../explanations.md#Explanations-PERF-011)

Sources: [Performance NFRs – Atomic Requirements](requirements/nfrs/areas/performance/overview.md#PERF-011)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Operation ID | Burst TPS | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|------------|---------|---------|
| perf-dos-search-burst-tps | dos-search endpoints sustain burst 150 TPS | Burst_tps_target met across key endpoints as per operations registry | Quarterly + CI smoke on change | int,ref,prod | DoS Search | draft | [FTRS-1382](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1382), [FTRS-738](https://nhsd-jira.digital.nhs.uk/browse/FTRS-738), [FTRS-831](https://nhsd-jira.digital.nhs.uk/browse/FTRS-831) | Search by ODS code (dos-lookup-ods) | 150 | Verifies burst throughput capacity |
| perf-dos-search-burst-tps | dos-search endpoints sustain burst 150 TPS | Burst_tps_target met across key endpoints as per operations registry | Quarterly + CI smoke on change | int,ref,prod | DoS Search | draft | [FTRS-1382](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1382), [FTRS-738](https://nhsd-jira.digital.nhs.uk/browse/FTRS-738), [FTRS-831](https://nhsd-jira.digital.nhs.uk/browse/FTRS-831) | Nearby Services (dos-nearby) | 150 | Verifies burst throughput capacity |
| perf-dos-search-burst-tps | dos-search endpoints sustain burst 150 TPS | Burst_tps_target met across key endpoints as per operations registry | Quarterly + CI smoke on change | int,ref,prod | DoS Search | draft | [FTRS-1382](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1382), [FTRS-738](https://nhsd-jira.digital.nhs.uk/browse/FTRS-738), [FTRS-831](https://nhsd-jira.digital.nhs.uk/browse/FTRS-831) | Search (GP) (dos-search) | 150 | Verifies burst throughput capacity |

### PERF-012

Endpoints sustain steady-state TPS at or above the defined target (sustained_tps_target)

See explanation: [PERF-012](../../explanations.md#Explanations-PERF-012)

Sources: [Performance NFRs – Atomic Requirements](requirements/nfrs/areas/performance/overview.md#PERF-012)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Operation ID | Sustained TPS | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|------------|-------------|---------|
| perf-dos-search-steady-tps | dos-search endpoints sustain steady 150 TPS | Sustained_tps_target met across key endpoints as per operations registry | Quarterly + CI smoke on change | int,ref,prod | DoS Search | draft | [FTRS-1382](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1382), [FTRS-1650](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1650), [FTRS-1690](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1690), [FTRS-738](https://nhsd-jira.digital.nhs.uk/browse/FTRS-738) | Search by ODS code (dos-lookup-ods) | 150 | Verifies steady-state throughput capacity |
| perf-dos-search-steady-tps | dos-search endpoints sustain steady 150 TPS | Sustained_tps_target met across key endpoints as per operations registry | Quarterly + CI smoke on change | int,ref,prod | DoS Search | draft | [FTRS-1382](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1382), [FTRS-1650](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1650), [FTRS-1690](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1690), [FTRS-738](https://nhsd-jira.digital.nhs.uk/browse/FTRS-738) | Nearby Services (dos-nearby) | 150 | Verifies steady-state throughput capacity |
| perf-dos-search-steady-tps | dos-search endpoints sustain steady 150 TPS | Sustained_tps_target met across key endpoints as per operations registry | Quarterly + CI smoke on change | int,ref,prod | DoS Search | draft | [FTRS-1382](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1382), [FTRS-1650](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1650), [FTRS-1690](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1690), [FTRS-738](https://nhsd-jira.digital.nhs.uk/browse/FTRS-738) | Search (GP) (dos-search) | 150 | Verifies steady-state throughput capacity |

### PERF-013

Request payload size per endpoint stays within the defined maximum (max_request_payload_bytes)

See explanation: [PERF-013](../../explanations.md#Explanations-PERF-013)

Sources: [Performance NFRs – Atomic Requirements](requirements/nfrs/areas/performance/overview.md#PERF-013)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Operation ID | Max Payload (bytes) | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|------------|-------------------|---------|
| perf-request-payload-limits | Maximum request payload size per endpoint 1MB | Max_request_payload_bytes enforced per endpoint per operations registry | CI per build + monthly audit | int,ref,prod | DoS Search | draft | (none) | Search by ODS code (dos-lookup-ods) | 1048576 | Prevents oversized payload degradation |
| perf-request-payload-limits | Maximum request payload size per endpoint 1MB | Max_request_payload_bytes enforced per endpoint per operations registry | CI per build + monthly audit | int,ref,prod | DoS Search | draft | (none) | Nearby Services (dos-nearby) | 1048576 | Prevents oversized payload degradation |
| perf-request-payload-limits | Maximum request payload size per endpoint 1MB | Max_request_payload_bytes enforced per endpoint per operations registry | CI per build + monthly audit | int,ref,prod | DoS Search | draft | (none) | Search (GP) (dos-search) | 1048576 | Prevents oversized payload degradation |
