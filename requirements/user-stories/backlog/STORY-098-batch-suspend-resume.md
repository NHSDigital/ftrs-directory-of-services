---
id: STORY-098
title: Batch process suspend/resume integrity
nfr_refs:
  - REL-010
type: reliability
status: draft
owner: platform-team
summary: Support suspension and resumption of batch housekeeping tasks without data corruption.
---

## Description
Implement checkpointing for batch processes (postcode updates, organisation updates, dispositions, certificate renewals). Simulate suspend and resume verifying data integrity and idempotent continuation.

## Acceptance Criteria
- Checkpoint metadata recorded at suspend.
- Resume continues from last checkpoint without duplication.
- Data integrity checksum matches pre/post execution.
- Corruption attempt (partial file write) detected & recovered.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| suspend_checkpoint_test | automated | Metadata recorded |
| resume_continuation_test | automated | Process resumes correctly |
| data_checksum_validation | automated | Checksums match |
| corruption_simulation_test | automated | Detected & recovered |

## Traceability
NFRs: REL-010
