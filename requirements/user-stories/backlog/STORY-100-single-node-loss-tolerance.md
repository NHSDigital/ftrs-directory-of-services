---
id: STORY-100
title: Single node loss tolerance
nfr_refs:
  - REL-012
  - REL-002
type: reliability
status: draft
owner: platform-team
summary: Demonstrate that loss of any single node does not degrade performance or cause data loss until replaced.
---

## Description
Use chaos engineering to randomly terminate a single node in each functional group; measure performance and data integrity; confirm auto-replacement initiates.

## Acceptance Criteria
- Chaos test terminates one node per group.
- Performance metrics (latency, throughput) remain within SLA.
- Data integrity checks show no loss/corruption.
- Replacement node provisioned & healthy within threshold time.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| chaos_single_node_termination | automated | Node terminated |
| latency_throughput_post_termination | automated | Stable metrics |
| data_integrity_post_termination | automated | No corruption |
| replacement_node_health_check | automated | New node healthy |

## Traceability
NFRs: REL-012, REL-002
