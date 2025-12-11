# FtRS NFR – Service: data-migration

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Observability | OBS-025 | Alerts delivered to multi-channel with context | Alerts delivered with sufficient context to act (multi-channel). | STORY-OBS-025 |
| Performance | PERF-001 | Each operation meets registry-defined percentile targets (p50/p95) logged & asserted (see performance/expectations.yaml) | Each API or batch operation meets agreed median and 95th percentile latency targets. | STORY-PERF-001, STORY-PERF-002, STORY-PERF-003, STORY-PERF-004, STORY-PERF-005, STORY-PERF-006, STORY-PERF-007, STORY-PERF-008, STORY-PERF-009, STORY-PERF-010, STORY-SCAL-001 |
| Performance | PERF-006 | Batch window p95 latency delta ≤5% | Batch window latency stays within a small variance (e.g., p95 delta ≤ defined %). | STORY-PERF-015 |

## Operations

### PERF-001

| Requirement | Operation ID | p50 ms | p95 ms | Max ms | Burst TPS | Sustained TPS | Max Payload (bytes) | Status | Rationale |
|-------------|--------------|--------|--------|--------|-----------|---------------|---------------------|--------|-----------|
| [PERF-001](#perf-001) | dm-full-sync | 1200000 | 1800000 | 2700000 |  |  |  | draft | End-to-end duration baseline including transform and upserts |
| [PERF-001](#perf-001) | dm-record-transform | 120 | 250 | 800 |  |  |  | draft | Single legacy record validation + transform + upsert |

## Controls

### OBS-025

Alerts delivered to multi-channel with context

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-025](#obs-025) | migration-variance-alerts | Actionable alerts on data-migration error rate and duration variance | Alert when error_rate >1% over 5m window OR full-sync duration > baseline +20%; include playbook link, correlation_id, impacted counts | Metrics backend, alerting engine, synthetic event injector, dashboard | Continuous evaluation; monthly threshold tuning; weekly report | int,ref,prod | data-migration | draft | Early detection of pipeline health issues to reduce MTTR and prevent silent degradation |
