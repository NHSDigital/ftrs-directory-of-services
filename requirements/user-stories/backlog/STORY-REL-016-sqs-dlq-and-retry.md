---
story_id: STORY-REL-016
title: SQS DLQ and deterministic retry for queue population
role: Reliability Engineer
goal: Ensure no message loss during queue population
value: Increases resilience of incremental seeding
nfr_refs: [REL-016]
status: draft
---

## Acceptance Criteria
1. Failed batches routed to DLQ with payload and reason.
2. Retry policy drains DLQ; success rate ≥99% post-retry.
3. No message loss proven via reconciliation count.
4. Alert on DLQ backlog >100 or age >30m.
