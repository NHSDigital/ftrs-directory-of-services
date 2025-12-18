# FtRS NFR – Service: ODS ETL – Domain: Performance

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Performance NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471098/Performance)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Performance | [PERF-001](#ODSETL–PerformanceNFRs&Operations-PERF-001) | Each operation meets registry-defined percentile targets (p50/p95) logged & asserted (see performance/expectations.yaml) | Each API or batch operation meets agreed median and 95th percentile latency targets. | (none) |
| Performance | [PERF-006](#ODSETL–PerformanceNFRs&Operations-PERF-006) | Batch window p95 latency delta ≤5% | Batch window latency stays within a small variance (e.g., p95 delta ≤ defined %). | (none) |

## Operations

Operation: performance-specific expectation for an endpoint or job. Tied to a service and operation_id; sets p50/p95 latency, absolute max, burst/sustained TPS, payload limits, status, rationale, and stories.

| Operation ID | p50 ms | p95 ms | Max ms | Burst TPS | Sustained TPS | Max Payload (bytes) | Status | Stories | Rationale |
|--------------|--------|--------|--------|-----------|---------------|---------------------|--------|---------|-----------|
| ODS Batch Transform (ods-batch-transform) | 200 | 600 | 1200 |  |  |  | draft | (none) | Mapping + normalization + extension filtering |
| ODS Daily Sync (ods-daily-sync) | 500 | 1500 | 3000 |  |  |  | exception | (none) | External ORD call + list parsing; acceptable longer latency |
| ODS SQS Batch Send (ods-sqs-batch-send) | 30 | 80 | 200 |  |  |  | draft | (none) | Single AWS API batch request with lightweight payload |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.
