---
id: STORY-074
title: Autoscaling policy simulation harness
nfr_refs:
  - SCAL-005
  - SCAL-009
type: scalability
status: draft
owner: platform-team
summary: Provide a simulation harness to test autoscaling triggers and audit log entries before deploying to production.
---

## Description
Implement a script/harness to inject synthetic metric data (CPU, latency, queue depth) to simulate scaling conditions. Verify resulting scale events and audit log entries before changes are applied to production policies.

## Acceptance Criteria
- Harness can inject metrics to trigger scale-out and scale-in.
- Simulated events produce audit log entries with timestamp, actor (system), reason.
- False-positive rate for scale triggers <5% in test run.
- Documentation guides usage and rollback.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| scale_out_simulation | automated | Scale-out event + audit entry |
| scale_in_simulation | automated | Scale-in event + audit entry |
| false_positive_analysis | automated | FP <5% threshold |
| harness_docs_presence | manual | Documentation committed |

## Traceability
NFRs: SCAL-005, SCAL-009
