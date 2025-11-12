---
id: STORY-094
title: Side-channel isolation
nfr_refs:
  - REL-006
  - SEC-019
type: reliability
status: draft
owner: security-team
summary: Prevent side-channel data leakage by isolating sensitive workloads from untrusted co-tenants.
---

## Description
Verify infrastructure placement policies ensure sensitive workloads are isolated (dedicated hosts, tenancy settings). Run co-residency scan and confirm no unauthorized adjacency. Document controls.

## Acceptance Criteria
- Placement policy documented (host/tenancy settings).
- Co-residency scan shows zero unauthorized adjacency.
- Attempt to schedule sensitive workload on shared host denied.
- Quarterly isolation review executed.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| placement_policy_presence | manual | Policy committed |
| co_residency_scan | automated | No unauthorized adjacency |
| shared_host_attempt | automated | Scheduling denied |
| quarterly_review_log | manual | Review entry present |

## Traceability
NFRs: REL-006, SEC-019
