---
id: STORY-180
title: Establish performance test baseline and expectations for search action
status: draft
type: functional
owner: gp-search-team
nfr_refs:
  - PERF-001
  - PERF-002
  - PERF-003
  - PERF-004
  - PERF-005
  - PERF-009
  - PERF-010
summary: As a performance engineer I need defined expectations and automated tests to track latency over time and detect regressions.
---

### Acceptance Criteria
1. Performance expectations table includes p50/p95 targets and is versioned in repo.
2. Anonymised dataset representative (record count, distribution) documented & audited.
3. Load test script covers only defined actions (search) excluding non-priority flows.
4. Baseline run produces median <300ms and p95 within target (PERF-001/003).
5. Regression alert triggers simulation on >10% p95 increase (PERF-009).
6. Percentile methodology doc matches tool configuration (PERF-010).
7. Pillar checklist completed with open actions tracked (PERF-002).

### Test Notes
| Scenario | Tool | Data | Expected |
|----------|------|------|----------|
| Baseline run | k6 | Representative dataset | Latency metrics within targets |
| Regression simulation | k6 + injected delay | Same dataset | Alert triggered |
| Methodology match | doc + config diff | N/A | No mismatch found |

### Traceability
Performance governance end-to-end.
