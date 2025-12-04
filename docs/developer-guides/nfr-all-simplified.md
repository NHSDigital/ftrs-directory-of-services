# FtRS Non-Functional Requirements – Simplified

Source: requirements/nfrs/cross-references/nfr-matrix.md

This page is auto-generated; do not hand-edit. Run `python3 scripts/nfr/refresh_simplified_nfr_page.py` to refresh.

## Domain Index

| Domain | NFR Codes | Expectations Items | Page |
|--------|-----------|--------------------|------|
| Accessibility | 22 | 5 | [Accessibility](nfr-domains/accessibility.md) |
| Availability | 10 | 5 | [Availability](nfr-domains/availability.md) |
| Compatibility | 3 | 3 | [Compatibility](nfr-domains/compatibility.md) |
| Cost | 7 | 5 | [Cost](nfr-domains/cost.md) |
| Governance | 16 | 5 | [Governance](nfr-domains/governance.md) |
| Interoperability | 18 | 7 | [Interoperability](nfr-domains/interoperability.md) |
| Observability | 33 | 7 | [Observability](nfr-domains/observability.md) |
| Performance | 13 | 12 | [Performance](nfr-domains/performance.md) |
| Reliability | 17 | 5 | [Reliability](nfr-domains/reliability.md) |
| Scalability | 10 | 5 | [Scalability](nfr-domains/scalability.md) |
| Security | 30 | 30 | [Security](nfr-domains/security.md) |

### Notes

Per-domain pages now contain detailed operations or controls grouped by NFR code. This index intentionally omits those large tables for comprehension.

---

## How to Read a Performance Operation Row (Plain English)

Example row:

| Service | Operation ID | Class | p50 ms | p95 ms | Max ms | Burst TPS | Sustained TPS | Max Payload (bytes) | Status | Rationale |
|---------|--------------|-------|--------|--------|--------|----------|--------------|---------------------|--------|-----------|
| crud-apis | org-search-ods |  | 60 | 140 | 400 |  |  |  | draft | ODS code normalization + single index scan |

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

Example control row:

| Control ID | NFR Code | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|----------|---------|-----------|---------|---------|------|----------|--------|-----------|
| crypto-cipher-policy | SEC-001 | cryptography algorithms conform; weak ciphers rejected | TLS1.2+ only; no weak/legacy ciphers enabled | TLS scanner + configuration policy checks | CI per change + monthly scan | dev,int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Enforces modern TLS standards; automated scans detect drift |

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
