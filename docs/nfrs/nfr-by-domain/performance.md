# FtRS NFR – Performance

Source: requirements/nfrs/cross-references/nfr-matrix.md

This page is auto-generated; do not hand-edit.

## NFR Codes

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| PERF-001 | Each operation meets registry-defined percentile targets (p50/p95) logged & asserted (see performance/expectations.yaml) | Each API or batch operation meets agreed median and 95th percentile latency targets. | STORY-PERF-001, STORY-PERF-002, STORY-PERF-003, STORY-PERF-004, STORY-PERF-005, STORY-PERF-006, STORY-PERF-007, STORY-PERF-008, STORY-PERF-009, STORY-PERF-010, STORY-SCAL-001 |
| PERF-002 | Performance pillar checklist completed & actions closed | Performance pillar checklist is completed and any actions are closed. | STORY-PERF-011 |
| PERF-003 | Performance expectations table versioned & referenced | The versioned performance expectations table is maintained and referenced by tests. | STORY-PERF-012 |
| PERF-004 | Anonymised live-like dataset present & audited | A representative, anonymised dataset exists for realistic performance validation. | STORY-PERF-013 |
| PERF-005 | Automated test suite matches defined actions & exclusions | Automated performance tests implement all defined actions and listed exclusions. | STORY-PERF-014 |
| PERF-006 | Batch window p95 latency delta ≤5% | Batch window latency stays within a small variance (e.g., p95 delta ≤ defined %). | STORY-PERF-015 |
| PERF-007 | Telemetry overhead within CPU & latency thresholds | Telemetry overhead (CPU, latency) remains within acceptable limits while capturing required data. | STORY-PERF-016 |
| PERF-008 | 8h rolling window p95 variance ≤10% | Rolling window performance variance remains stable within target percentage bounds. | STORY-PERF-017 |
| PERF-009 | Regression alert triggers on >10% p95 increase | Alerting triggers when p95 latency regresses beyond the defined threshold (e.g., >10%). | STORY-PERF-018 |
| PERF-010 | Percentile methodology document & tool configuration aligned | Documented percentile methodology matches tool configuration (consistent measurement). | STORY-PERF-019 |
| PERF-011 | dos-search endpoints sustain burst ≥150 TPS (registry burst_tps_target) | GP search endpoints handle short burst throughput at or above the target TPS. | (placeholder) |
| PERF-012 | dos-search endpoints sustain steady ≥150 TPS (registry sustained_tps_target) | GP search endpoints sustain steady-state throughput at or above the TPS target. | (placeholder) |
| PERF-013 | Request payload size per endpoint ≤1MB (max_request_payload_bytes) | Endpoint request payloads remain under the maximum defined size to protect performance. | (placeholder) |

## Operations

| Service | Operation ID | p50 ms | p95 ms | Max ms | Burst TPS | Sustained TPS | Max Payload (bytes) | Status | Rationale |
|---------|--------------|--------|--------|--------|----------|--------------|---------------------|--------|-----------|
| dos-search | dos-search | 150 | 300 | 500 | 150 | 150 | 1048576 | draft | Primary user-facing query; critical perceived responsiveness |
| dos-search | dos-lookup-ods | 150 | 300 | 500 | 150 | 150 | 1048576 | draft | Direct ODS code lookup; largely cacheable |
| dos-search | dos-nearby | 150 | 300 | 500 | 150 | 150 | 1048576 | draft | Geo filtering + limited enrichment |
| crud-apis | org-get | 40 | 100 | 300 |  |  |  | draft | Simple primary key lookup; cached storage path |
| crud-apis | org-update | 70 | 150 | 400 |  |  |  | draft | Validation + persistence + OperationOutcome classification |
| crud-apis | healthcare-service-get | 50 | 120 | 350 |  |  |  | draft | Direct read + lightweight mapping |
| crud-apis | org-search-ods | 60 | 140 | 400 |  |  |  | draft | ODS code normalization + single index scan |
| etl-ods | ods-daily-sync | 500 | 1500 | 3000 |  |  |  | exception | External ORD call + list parsing; acceptable longer latency |
| etl-ods | ods-batch-transform | 200 | 600 | 1200 |  |  |  | draft | Mapping + normalization + extension filtering |
| etl-ods | ods-sqs-batch-send | 30 | 80 | 200 |  |  |  | draft | Single AWS API batch request with lightweight payload |
| data-migration | dm-record-transform | 120 | 250 | 800 |  |  |  | draft | Single legacy record validation + transform + upsert |
| data-migration | dm-full-sync | 1200000 | 1800000 | 2700000 |  |  |  | draft | End-to-end duration baseline including transform and upserts |

