---
id: STORY-099
title: Compute health checks & auto-replacement
nfr_refs:
  - REL-011
  - REL-012
type: reliability
status: draft
owner: platform-team
summary: Continuously probe compute nodes, marking unhealthy nodes offline and triggering automated replacement without performance degradation.
---

## Description
Configure health probes for all compute resource types (lambda, container, VM). Unhealthy results mark node as offline; replacement instance launched automatically; workload continues without SLA breach.

## Acceptance Criteria
- Health probe interval & thresholds documented.
- Unhealthy node simulation removes node from rotation.
- Auto-replacement instance launched & registered.
- Performance metrics stable before/after replacement.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| probe_threshold_config_presence | manual | Config committed |
| unhealthy_node_simulation | automated | Node quarantined |
| auto_replacement_event_check | automated | New instance active |
| perf_stability_comparison | automated | Metrics unchanged |

## Traceability
NFRs: REL-011, REL-012
