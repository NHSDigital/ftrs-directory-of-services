# FtRS NFR – Service: Data Migration – Domain: Performance

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Performance NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471098/Performance)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Performance | [PERF-001](../../explanations.md#Explanations-PERF-001) | Each operation meets registry-defined percentile targets (p50/p95) logged & asserted (see performance/expectations.yaml) | Each API or batch operation meets agreed median and 95th percentile latency targets. | (none) |
| Performance | [PERF-006](../../explanations.md#Explanations-PERF-006) | Batch window p95 latency delta ≤5% | Batch window latency stays within a small variance (e.g., p95 delta ≤ defined %). | (none) |

## Operations

Operation: performance-specific expectation for an endpoint or job. Tied to a service and operation_id; sets p50/p95 latency, absolute max, burst/sustained TPS, payload limits, status, rationale, and stories.

| Operation ID | p50 ms | p95 ms | Max ms | Burst TPS | Sustained TPS | Max Payload (bytes) | Status | Stories | Rationale |
|--------------|--------|--------|--------|-----------|---------------|---------------------|--------|---------|-----------|
| Full Sync (dm-full-sync) | 1200000 | 1800000 | 2700000 |  |  |  | draft | (none) | End-to-end duration baseline including transform and upserts |
| Record Transform (dm-record-transform) | 120 | 250 | 800 |  |  |  | draft | (none) | Single legacy record validation + transform + upsert |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.
