# Performance Expectations Model

## 1. Purpose

Centralise endpoint / operation latency targets outside individual user stories so they remain:

- Traceable (single registry drives tests, dashboards, alerts)
- Versioned (explicit history of threshold changes)
- Explicit (each operation lists concrete numeric targets without abstract classes)
- Enforceable (automation consumes a machine-readable file)

This README documents the pattern for refining baseline performance NFRs (e.g. `PERF-001`, `PERF-003`) using a versioned expectations registry rather than fragmenting numeric targets across many stories.

## 2. Layered NFR Model

| Layer | Artifact | Responsibility |
|-------|----------|----------------|
| Baseline NFR (e.g. PERF-001) | NFR Matrix | Mandates that each operation meets its documented percentile thresholds. |
| Expectations Registry | `expectations.yaml` | Stores per-operation quantitative targets, metadata, rationale, and validation status. |
| Refinement Stories | e.g. STORY-176 | Provide acceptance criteria referencing registry rows ("p95 latency ≤ 180ms, see expectations.yaml v1.3 row #dos-search"). |
| Automation | Test & CI scripts | Dynamically assert actual metrics against registry targets; fail on breach. |
| Governance | Changelog + exception stories | Control & audit changes to thresholds; justify slower endpoints. |

## 3. Registry File (`expectations.yaml`) Schema

```yaml
version: <string>            # Semantic increment on any target change
generated: <ISO date>        # Date of current version creation
operations:
  - service: <string>        # Service/component identifier
    operation_id: <string>   # Stable key used in metrics & tests
    path: <string>           # REST/FHIR path (+ optional operation name)
    method: <string>         # HTTP verb or 'OPERATION'
    p50_target_ms: <int>
    p95_target_ms: <int>
    absolute_max_ms: <int>   # Hard ceiling (optional)
    concurrency_profile: <string> # e.g. burst-50 steady-10
    rationale: <string>
    test_ref: <file or story id>
    exception_story: <story id>   # Only for SLOW endpoints
    review_cycle: <string>        # e.g. quarterly
    last_validated: <ISO date>
    status: pass|watch|exception  # Current health state
changelog:
  - <version entry list>
```

### 3.1 Status Field

| Status | Meaning | Action |
|--------|---------|--------|
| pass | All recent percentiles within target | None |
| watch | Approaching breach (e.g. > target +5%) | Investigate & optimise |
| exception | Approved slower behavior documented | Review per cycle |

## 4. Example Registry

See `expectations.yaml` for a live example.

## 5. Refinement Stories

Each story refining a performance target MUST:

1. Reference baseline NFR code(s) (`PERF-001`, `PERF-003`).
2. Include acceptance criterion linking to a specific row + version ("Registry v1.3 row operation_id=dos-search p95 ≤ 180ms").
3. Add or update rationale when thresholds change.
4. If slowing an endpoint: create/attach an exception story documenting justification + review cycle (explicitly justified on the operation itself; no class labels).

## 6. Automation Pattern

### 6.1 Metric Naming Conventions

Prometheus style (example):

```text
http_request_duration_ms_bucket{operation_id="dos-search",le="0.3"}
http_request_duration_ms_sum{operation_id="dos-search"}
http_request_duration_ms_count{operation_id="dos-search"}
```

OR custom metrics from AWS/Powertools aggregated into a distribution.

Derived percentiles are computed either by Prometheus or offline by the test harness.

### 6.2 Test Harness Pseudocode

```python
import yaml, statistics, time
from metrics_client import fetch_latency_samples

with open('requirements/nfrs/performance/expectations.yaml') as f:
    cfg = yaml.safe_load(f)
violations = []
for op in cfg['operations']:
    samples = fetch_latency_samples(op['operation_id'], window_minutes=30)
    if not samples:
        continue
    p50 = percentile(samples, 50)
    p95 = percentile(samples, 95)
    if p50 > op['p50_target_ms']:
        violations.append((op['operation_id'], 'p50', p50, op['p50_target_ms']))
    if p95 > op['p95_target_ms']:
        violations.append((op['operation_id'], 'p95', p95, op['p95_target_ms']))
    if 'absolute_max_ms' in op and max(samples) > op['absolute_max_ms']:
        violations.append((op['operation_id'], 'max', max(samples), op['absolute_max_ms']))
if violations:
    for v in violations:
        print(f"PERF VIOLATION {v}")
    exit(1)
else:
    print("Performance expectations satisfied")
```

Integrate into CI (e.g. `make performance-validate`) and tie failures to `PERF-009` regression alert processes.

### 6.3 Regression & Drift

A secondary script compares last 7-day rolling p95 against target triggers:

- GREEN ≤ target
- AMBER ≤ target +10%
- RED > target +10% → open ticket referencing refining story & PERF-001.

## 7. Governance & Change Control

1. Any target adjustment increments registry `version` and appends changelog entry.
2. Slower target change requires explicit exception story & sign-off referencing GOV codes if governance needed.
3. Registry modifications must pass code review and link to rationale (performance optimisation result, new feature cost).
4. Quarterly audit: enumerate all endpoints with exception stories, confirm still needed.

## 8. Exceptions Workflow

- Create story: e.g. `STORY-EXC-TRIAGE-ENRICH-SLOW` (or reuse enrichment story) capturing: previous target, new target, justification, mitigation plan.
- Update registry row with `exception_story` and `status: exception`.
- Schedule review (add `review_cycle`).

## 9. Dashboards & Observability

Annotate dashboards with target overlays by exposing a gauge metric:

```text
dos_search_target_latency_ms{quantile="p95"} 180
```

Automations render actual vs target; breaches highlighted automatically.

## 10. Failure Handling Strategy

- Test harness fails build on breach: developer inspects logs, runs profiling.
- Short-term acceptable variance (<5%) flagged as `watch` without failing to reduce noise.
- Major breach (>15%) triggers incident classification & root cause analysis story.

## 11. Rationale Field Guidance

Should answer: "Why is this endpoint's target different?" Acceptable categories:

- User-facing critical path
- Heavy enrichment or aggregation
- External dependency latency bound
- Security scanning overhead

## 12. Extensibility

Future fields optionally added:

- p99_target_ms
- error_rate_target_percent
- payload_size_avg_bytes
- cache_hit_rate_target_percent
- warm_vs_cold_latency_ms

- burst_tps_target
- sustained_tps_target
- max_request_payload_bytes

## 13. Relationship to Existing NFRs

| NFR | Role |
|-----|------|
| PERF-001 | Enforces presence + adherence to per-operation percentile targets |
| PERF-003 | Ensures performance expectations table is versioned & referenced |
| PERF-005 | Test suite covers actions including latency assertions |
| PERF-007 | Telemetry overhead to collect metrics stays within threshold |
| PERF-009 | Alerts/regression detection on >10% p95 increase |
| PERF-010 | Methodology for computing percentiles documented |
| PERF-011 | Verifies burst throughput capacity (≥ burst_tps_target) |
| PERF-012 | Verifies sustained throughput baseline (≥ sustained_tps_target) |
| PERF-013 | Enforces request payload size constraint (≤ max_request_payload_bytes) |

## 14. Acceptance for This Model

- Registry present & versioned.
- All dos-search, crud-apis and etl-ods operations listed.
- At least one refinement story references a registry row.
- CI harness uses registry for dynamic assertions.
- Changelog includes at least one non-trivial adjustment.

## 15. Open Questions

| Topic | Question | Next Step |
|-------|----------|-----------|
| Multi-region targets | Do we store per-region latency? | Consider region sub-field if divergence emerges |
| Warm vs cold starts | Separate targets? | Add optional warm/cold fields after measurement |
| Rolling window size | 30 vs 60 minute evaluation? | Experiment & tune for noise reduction |

---
End of README.
