---
id: STORY-070
title: Overall horizontal scalability for stateless services
nfr_refs:
  - SCAL-001
  - SCAL-006
  - SCAL-007
type: scalability
status: draft
owner: platform-team
summary: Demonstrate stateless service tier can scale out/in automatically without performance degradation and maintain capacity headroom.
---

## Description
Implement and validate autoscaling for a representative stateless API service. Show linear throughput improvement when adding replicas while keeping latency and error rates within SLA and sustaining ≥30% capacity headroom.

## Acceptance Criteria
- Baseline TPS & latency recorded at 2 replicas.
- Scale-out to 4 replicas increases TPS ~≥1.8x (allowing some overhead).
- Latency p50/p95 remain within performance SLA during scaling.
- Scale-in after sustained low utilisation reduces replicas with no failed requests.
- Capacity report indicates ≥30% headroom post-test.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| baseline_load_test | automated | Baseline metrics artifact stored |
| scale_out_load_test | automated | Throughput increase ≥1.8x; latency stable |
| scale_in_load_test | automated | No elevated error rate |
| capacity_headroom_report | automated | Utilisation <70% |

## Traceability
NFRs: SCAL-001, SCAL-006, SCAL-007
