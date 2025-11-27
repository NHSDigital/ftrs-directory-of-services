---
story_id: STORY-OBS-019
title: Correlation ID present across migration stages and upserts
role: Platform Engineer
goal: Enable end-to-end reconstruction for migrated records
value: Faster incident diagnosis and audit traceability
nfr_refs: [OBS-019, INT-013]
status: draft
---

## Acceptance Criteria

1. `correlation_id` present in processor start, transform, save logs and final metrics.
2. Upsert repository calls include correlation_id in contextual logging.
3. Validation job samples 1% logs and reports zero missing IDs.
4. Query example reconstructs full chain for a record.

## Non-Functional Acceptance

- Control: OBS-019
- Cadence: Continuous; weekly audit
