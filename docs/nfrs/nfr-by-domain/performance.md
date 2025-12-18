# FtRS NFR – Performance

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Performance NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471098/Performance)

## NFR Codes

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| [PERF-001](../explanations.md#Explanations-PERF-001) | Each operation meets registry-defined percentile targets (p50/p95) logged & asserted (see performance/expectations.yaml) | Each API or batch operation meets agreed median and 95th percentile latency targets. | [FTRS-1382](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1382), [FTRS-887](https://nhsd-jira.digital.nhs.uk/browse/FTRS-887) |
| [PERF-002](../explanations.md#Explanations-PERF-002) | Performance pillar checklist completed & actions closed | Performance pillar checklist is completed and any actions are closed. | (none) |
| [PERF-003](../explanations.md#Explanations-PERF-003) | Performance expectations table versioned & referenced | The versioned performance expectations table is maintained and referenced by tests. | (none) |
| [PERF-004](../explanations.md#Explanations-PERF-004) | Anonymised live-like dataset present & audited | A representative, anonymised dataset exists for realistic performance validation. | (none) |
| [PERF-005](../explanations.md#Explanations-PERF-005) | Automated test suite matches defined actions & exclusions | Automated performance tests implement all defined actions and listed exclusions. | (none) |
| [PERF-006](../explanations.md#Explanations-PERF-006) | Batch window p95 latency delta ≤5% | Batch window latency stays within a small variance (e.g., p95 delta ≤ defined %). | (none) |
| [PERF-007](../explanations.md#Explanations-PERF-007) | Telemetry overhead within CPU & latency thresholds | Telemetry overhead (CPU, latency) remains within acceptable limits while capturing required data. | (none) |
| [PERF-008](../explanations.md#Explanations-PERF-008) | 8h rolling window p95 variance ≤10% | Rolling window performance variance remains stable within target percentage bounds. | (none) |
| [PERF-009](../explanations.md#Explanations-PERF-009) | Regression alert triggers on >10% p95 increase | Alerting triggers when p95 latency regresses beyond the defined threshold (e.g., >10%). | (none) |
| [PERF-010](../explanations.md#Explanations-PERF-010) | Percentile methodology document & tool configuration aligned | Documented percentile methodology matches tool configuration (consistent measurement). | (none) |
| [PERF-011](../explanations.md#Explanations-PERF-011) | Endpoints sustain burst TPS at or above the defined target (burst_tps_target) | GP search endpoints handle short burst throughput at or above the target TPS. | [FTRS-1382](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1382), [FTRS-738](https://nhsd-jira.digital.nhs.uk/browse/FTRS-738), [FTRS-831](https://nhsd-jira.digital.nhs.uk/browse/FTRS-831) |
| [PERF-012](../explanations.md#Explanations-PERF-012) | Endpoints sustain steady-state TPS at or above the defined target (sustained_tps_target) | GP search endpoints sustain steady-state throughput at or above the TPS target. | [FTRS-1382](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1382), [FTRS-1650](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1650), [FTRS-1690](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1690), [FTRS-738](https://nhsd-jira.digital.nhs.uk/browse/FTRS-738) |
| [PERF-013](../explanations.md#Explanations-PERF-013) | Request payload size per endpoint stays within the defined maximum (max_request_payload_bytes) | Endpoint request payloads remain under the maximum defined size to protect performance. | [(placeholder)](https://nhsd-jira.digital.nhs.uk/browse/(placeholder)) |

## Operations

| Service | Operation | p50 ms | p95 ms | Max ms | Burst TPS | Sustained TPS | Max Payload (bytes) | Status | Stories | Rationale |
|---------|--------------|--------|--------|--------|----------|--------------|---------------------|--------|---------|-----------|
| DoS Search | Search (GP) (dos-search) | 150 | 300 | 500 | 150 | 150 | 1048576 | draft | [FTRS-1690](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1690), [FTRS-831](https://nhsd-jira.digital.nhs.uk/browse/FTRS-831) | Primary user-facing query; critical perceived responsiveness |
| DoS Search | Search by ODS code (dos-lookup-ods) | 150 | 300 | 500 | 150 | 150 | 1048576 | draft | [FTRS-1382](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1382), [FTRS-831](https://nhsd-jira.digital.nhs.uk/browse/FTRS-831), [FTRS-887](https://nhsd-jira.digital.nhs.uk/browse/FTRS-887) | Direct ODS code lookup; largely cacheable |
| DoS Search | Nearby Services (dos-nearby) | 150 | 300 | 500 | 150 | 150 | 1048576 | draft | [FTRS-831](https://nhsd-jira.digital.nhs.uk/browse/FTRS-831) | Geo filtering + limited enrichment |
| Ingress API | Get Organisation (org-get) | 40 | 100 | 300 |  |  |  | draft | (none) | Simple primary key lookup; cached storage path |
| Ingress API | Update Organisation (org-update) | 70 | 150 | 400 |  |  |  | draft | (none) | Validation + persistence + OperationOutcome classification |
| Ingress API | Get HealthcareService (healthcare-service-get) | 50 | 120 | 350 |  |  |  | draft | (none) | Direct read + lightweight mapping |
| Ingress API | Search by ODS (org-search-ods) | 60 | 140 | 400 |  |  |  | draft | (none) | ODS code normalization + single index scan |
| ODS ETL | ODS Daily Sync (ods-daily-sync) | 500 | 1500 | 3000 |  |  |  | exception | (none) | External ORD call + list parsing; acceptable longer latency |
| ODS ETL | ODS Batch Transform (ods-batch-transform) | 200 | 600 | 1200 |  |  |  | draft | (none) | Mapping + normalization + extension filtering |
| ODS ETL | ODS SQS Batch Send (ods-sqs-batch-send) | 30 | 80 | 200 |  |  |  | draft | (none) | Single AWS API batch request with lightweight payload |
| Data Migration | Record Transform (dm-record-transform) | 120 | 250 | 800 |  |  |  | draft | (none) | Single legacy record validation + transform + upsert |
| Data Migration | Full Sync (dm-full-sync) | 1200000 | 1800000 | 2700000 |  |  |  | draft | (none) | End-to-end duration baseline including transform and upserts |
