---
id: STORY-181
title: Deploy service multi-AZ with zero-downtime release capability
status: draft
type: functional
owner: gp-search-team
nfr_refs:
  - AVAIL-001
  - AVAIL-010
  - REL-002
  - SCAL-001
summary: As a platform engineer I need resilient, horizontally scalable deployment ensuring availability targets and seamless releases.
---

### Acceptance Criteria
1. Multi-AZ configuration evidenced for Lambda & DynamoDB.
2. Blue/green deployment strategy documented & automated; release produces zero failed requests.
3. AZ failure simulation shows continued successful search responses (REL-002).
4. Horizontal scaling under load increases throughput within SLA (SCAL-001).
5. Monthly availability report indicates ≥99.90% (AVAIL-001).

### Test Notes
| Scenario | Tool | Data | Expected |
|----------|------|------|----------|
| Release test | synthetic load | Deploy new version | Zero failed requests |
| AZ simulation | chaos tool | Valid searches | Success responses continue |
| Scale load | k6 | Ramp RPS | Latency stable, throughput rises |

### Traceability
Resilience & availability mapping confirmed.
