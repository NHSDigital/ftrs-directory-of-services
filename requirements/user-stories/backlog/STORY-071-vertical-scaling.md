---
id: STORY-071
title: Vertical scaling for stateful component
nfr_refs:
  - SCAL-002
  - SCAL-006
type: scalability
status: draft
owner: platform-team
summary: Resize a stateful data store instance (e.g., database or OpenSearch node) without downtime or data loss and maintain performance.
---

## Description
Perform a controlled vertical scale-up (increase instance class) and scale-down test on a stateful component verifying data integrity, continuity of operations, and performance stability.

## Acceptance Criteria
- Pre-scale data integrity checksum recorded.
- Scale-up completes with zero failed client requests.
- Post scale-up latency & throughput within SLA.
- Scale-down (to smaller class) performed during off-peak with no data loss.
- Checksums match pre/post scaling events.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| pre_scale_checksum | automated | Baseline checksums recorded |
| scale_up_procedure | manual/automated | Zero failed requests |
| post_scale_perf_test | automated | Metrics within SLA |
| scale_down_procedure | manual/automated | Integrity preserved |
| post_scale_down_checksum | automated | Matches baseline |

## Traceability
NFRs: SCAL-002, SCAL-006
