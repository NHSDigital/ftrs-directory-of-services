---
story_id: STORY-PERF-001
title: Full sync throughput and latency baseline with regression alerts
role: Performance Engineer
goal: Establish p50/p95 per-record latency and full-run SLO
value: Prevents silent performance regressions
nfr_refs: [PERF-001]
status: draft
---

## Acceptance Criteria

1. Metrics: `dm_record_transform_latency_seconds` (histogram), `dm_full_sync_duration_seconds`.
2. Baseline: p95 < 0.25s per record; full run < 30m.
3. Alert on >20% regression vs baseline.
4. Weekly report stored with tool version.
