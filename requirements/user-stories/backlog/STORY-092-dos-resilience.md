---
id: STORY-092
title: Volumetric DoS resilience
nfr_refs:
  - REL-004
  - SEC-008
type: reliability
status: draft
owner: security-team
summary: Ensure FtRS maintains acceptable performance under simulated volumetric denial of service conditions.
---

## Description
Simulate high-rate traffic floods using load testing + attack simulation tooling. Validate WAF/DDoS protections and rate limiting preserve core functionality and latency/error SLAs.

## Acceptance Criteria
- DoS simulation generates target peak RPS.
- Core endpoints remain responsive within latency SLA.
- Rate limiting activates; malicious traffic dropped.
- Monitoring dashboard annotates mitigation event.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| dos_simulation_run | automated | Target RPS achieved |
| endpoint_latency_during_attack | automated | Latency within SLA |
| rate_limit_activation_check | automated | Limits engaged |
| mitigation_event_annotation | manual | Annotation visible |

## Traceability
NFRs: REL-004, SEC-008
