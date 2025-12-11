# FtRS NFR – By Domain

This page is auto-generated; do not hand-edit.

## Domain Index

| Domain | NFR Codes | Expectations Items | Page |
|--------|-----------|--------------------|------|
| Compatibility | 3 | 0 | [Compatibility](nfr-by-domain/compatibility.md) |
| Security | 30 | 0 | [Security](nfr-by-domain/security.md) |
| Cost | 7 | 0 | [Cost](nfr-by-domain/cost.md) |
| Interoperability | 18 | 0 | [Interoperability](nfr-by-domain/interoperability.md) |
| Observability | 33 | 0 | [Observability](nfr-by-domain/observability.md) |
| Scalability | 10 | 0 | [Scalability](nfr-by-domain/scalability.md) |
| Reliability | 17 | 0 | [Reliability](nfr-by-domain/reliability.md) |
| Governance | 16 | 0 | [Governance](nfr-by-domain/governance.md) |
| Availability | 10 | 0 | [Availability](nfr-by-domain/availability.md) |
| Performance | 13 | 0 | [Performance](nfr-by-domain/performance.md) |
| Accessibility | 22 | 0 | [Accessibility](nfr-by-domain/accessibility.md) |

### Notes

Per-domain pages now contain detailed operations or controls grouped by NFR code. This index intentionally omits those large tables for comprehension.

---

## How to Read a Performance Operation Row (Plain English)

Meaning of columns:

- Service: Subsystem owning the endpoint or job
- Operation ID: Stable short name used in tests & dashboards
- Class: Speed category (FAST snappy, STANDARD typical, SLOW heavy/background)
- p50 ms: Typical median latency target
- p95 ms: Near worst-case target for 95% of requests
- Max ms: Hard cap; any single request over triggers alert/exception
- Burst TPS: Short spike capacity target (blank = not defined yet)
- Sustained TPS: Comfortable continuous throughput target (blank = not defined yet)
- Max Payload (bytes): Largest allowed request size (blank = not constrained yet)
- Status: draft (proposed), accepted (agreed/enforced), exception (temporarily unmet)
- Rationale: Reasoning / assumptions behind targets

Multiple tests per operation typically: latency monitor (p50/p95), max latency alert, throughput tests (burst & sustained), payload boundary test.

---

## How to Read a Control Row (Plain English)

Meaning of columns:

- Control ID: Stable name of the automated check
- NFR Code: Which atomic NFR this control supports
- Measure: What is examined (setting, scan result, metric)
- Threshold: Quantified pass condition
- Tooling: Automation or scanner enforcing the measure
- Cadence: How often it runs (CI build, daily, per release)
- Envs: Environments covered
- Services: Scope (blank means all)
- Status: draft / accepted / exception governance state
- Rationale: Why the threshold/tool was chosen

Typical validation: tool execution success, threshold met, alert on failure, exception tracked with mitigation & review date.
