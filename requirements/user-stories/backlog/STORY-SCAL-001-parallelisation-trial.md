---
story_id: STORY-SCAL-001
title: Parallelised full-sync trial with safe concurrency limits
role: Scalability Engineer
goal: Demonstrate near-linear throughput scaling
value: Reduces migration duration under scale
nfr_refs: [SCAL-001, PERF-001]
status: draft
---

## Acceptance Criteria

1. Partition strategy trialed (ID ranges); measure throughput vs workers.
2. Document safe concurrency limits and DynamoDB capacity settings.
3. No data integrity issues detected.
