# FtRS NFR – Service: data-migration

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Accessibility | ACC-003 | Manual accessibility test executed per release | Manual accessibility tests are executed for each release cycle. | STORY-ACC-003 |
| Accessibility | ACC-004 | Defects tracked with parity priority & SLA | Accessibility defects tracked with equal priority and defined SLAs. | STORY-ACC-004 |
| Accessibility | ACC-005 | Tooling operational in dev/int/reference envs | Accessibility tooling operates correctly in dev, int, and reference environments. | STORY-ACC-005 |
| Accessibility | ACC-006 | Assistive tech not blocked by headers/CSP | Assistive technologies are not blocked by headers or Content Security Policy (CSP). | (none) |
| Accessibility | ACC-007 | Test dataset covers tables/forms/status messages | Test dataset covers common components: tables, forms, status messages. | (none) |
| Accessibility | ACC-008 | CI accessibility stage completes <5min | CI accessibility scan stage completes quickly (under target time). | (none) |
| Accessibility | ACC-011 | Screen reader ARIA role announcements verified | Screen reader announces ARIA roles and states correctly. | (none) |
| Accessibility | ACC-012 | Accessibility results documented with feature tests | Accessibility results are documented alongside feature tests. | (none) |
| Accessibility | ACC-013 | Central issue log maintained & current | Centralised accessibility issue log is maintained and current. | (none) |
| Accessibility | ACC-014 | Accessibility champion/workgroup active | Active champion or workgroup drives accessibility practice. | (none) |
| Accessibility | ACC-016 | Exception process documented & used | Exception process for accessibility deviations is documented. | (none) |
| Accessibility | ACC-017 | Exception record contains required fields | Exception records include required fields (impact, mitigation, expiry). | (none) |
| Accessibility | ACC-018 | Pre-commit checks complete <30s | Pre-commit accessibility checks finish within target duration. | (none) |
| Accessibility | ACC-019 | CI accessibility stage completes <5min | CI accessibility stage completes within target time window. | (none) |
| Accessibility | ACC-020 | Overnight full scan duration <2h | Overnight full scan finishes under defined maximum duration. | (none) |
| Accessibility | ACC-021 | Accessibility regression triggers alert | Regression in accessibility triggers automated alert. | (none) |
| Accessibility | ACC-022 | False positive ratio report shows improvement | False positive ratio is measured and trending toward improvement. | (none) |
| Availability | AVAIL-005 | Tuesday window executed; smoke tests pass | Scheduled maintenance executes successfully with passing smoke tests afterward. | (none) |
| Availability | AVAIL-006 | DR exercise restores service <2h | DR exercise restores service within target recovery time (< defined hours). | (none) |
| Availability | AVAIL-007 | Replication lag ≤60s; fail-over data delta minimal | Data replication lag remains under target ensuring minimal failover delta. | (none) |
| Availability | AVAIL-008 | API uptime aligns with core service | API uptime aligns with overall service availability target. | (none) |
| Availability | AVAIL-009 | Non-UK access attempts blocked & logged | Access from non-approved geographic regions is blocked and logged. | (none) |
| Cost | COST-006 | #ftrs-cost-alerts channel created & receiving test alerts | Dedicated cost alerts channel receives test and live notifications. | (none) |
| Cost | COST-007 | Quarterly cost review minutes & tracked actions | Quarterly cost reviews record minutes and follow-up actions. | (none) |
| Governance | GOV-003 | Solution Architecture Framework assessment approved | Solution Architecture Framework assessment is approved. | STORY-GOV-003 |
| Governance | GOV-006 | Medical Device out-of-scope statement recorded | Statement confirming service is out of scope for Medical Device regulation. | (none) |
| Governance | GOV-007 | FtRS Architects review & approval logged | Architecture review and approval logged by FtRS architects. | (none) |
| Governance | GOV-008 | Cloud Expert deployment approval documented | Cloud expert deployment approval documented (infrastructure readiness). | (none) |
| Governance | GOV-011 | Information Governance approval recorded | Information Governance approval recorded. | (none) |
| Governance | GOV-012 | TRG approval session outcome logged | Technical Review Group (TRG) approval outcome documented. | (none) |
| Governance | GOV-013 | SIRO sign-off obtained | Senior Information Risk Owner (SIRO) sign-off obtained. | (none) |
| Governance | GOV-014 | Caldicott Principles Guardian approval recorded | Caldicott Guardian approval recorded for data handling. | (none) |
| Governance | GOV-015 | DUEC Assurance Board acceptance logged | DUEC Assurance Board acceptance logged. | (none) |
| Governance | GOV-016 | Live Services Board go-live approval recorded | Live Services Board go-live approval recorded. | (none) |
| Interoperability | INT-001 | Resources validated against UK Core profiles | Resources conform to UK Core profiles ensuring national standard alignment. | (none) |
| Interoperability | INT-002 | Versioning & deprecation policy published | Versioning and deprecation policy is published for integrators. | (none) |
| Interoperability | INT-003 | Minor releases backward compatible for 12 months | Minor releases remain backward compatible for the defined support window. | (none) |
| Interoperability | INT-004 | Semantic mapping round-trip fidelity preserved | Semantic mappings preserve meaning when round-tripped between formats. | STORY-INT-004 |
| Interoperability | INT-006 | Identifier normalization applied (uppercase, trimmed) | Identifiers are normalised (case, trimming) for consistent matching. | (none) |
| Interoperability | INT-009 | Only documented FHIR search params accepted | Only documented FHIR search parameters are accepted; unknown ones rejected. | (none) |
| Interoperability | INT-010 | Version-controlled integration contract published | Integration contract is version-controlled and published. | (none) |
| Interoperability | INT-011 | Machine-readable changelog generated | Machine-readable changelog is generated for each release. | (none) |
| Interoperability | INT-012 | Terminology bindings validated | Terminology bindings are validated to ensure correct coding. | (none) |
| Interoperability | INT-014 | Null vs absent data handled per FHIR | Null vs absent data semantics follow FHIR specification rules. | (none) |
| Interoperability | INT-015 | ≥90% interoperability scenario coverage | Test coverage spans ≥90% of defined interoperability scenarios. | (none) |
| Observability | OBS-002 | Authenticated remote health dashboard accessible | Authenticated remote health dashboard is accessible to support teams. | (none) |
| Observability | OBS-003 | Health event visible ≤60s after failure | Health events appear on dashboards shortly after failures (within target freshness). | (none) |
| Observability | OBS-004 | Automated maintenance tasks executed; zero manual interventions | Automated maintenance tasks run successfully with no manual intervention required. | (none) |
| Observability | OBS-005 | Performance metrics per layer present | Layered performance metrics (app, DB, cache) are visible. | (none) |
| Observability | OBS-006 | Remote performance dashboard matches local view | Remote performance dashboard mirrors local environment metrics accurately. | (none) |
| Observability | OBS-010 | Aggregate latency panel accurate within 2% roll-up | Aggregate latency panel roll-ups remain within acceptable accuracy margin (e.g., ≤2%). | (none) |
| Observability | OBS-011 | Failure types logged & classified in dashboard | Failure types are logged and classified for reporting. | (none) |
| Observability | OBS-012 | Error percentage metric & alert configured | Error rate metric and alert exist to highlight reliability issues. | (none) |
| Observability | OBS-013 | Infra log query returns expected fields | Infrastructure logs return expected structured fields for queries. | (none) |
| Observability | OBS-014 | Infra log entries include required fields | Infrastructure log entries include required contextual fields (e.g., IDs, timestamps). | STORY-OBS-014 |
| Observability | OBS-015 | Retention policy enforced & reported | Log retention policy is enforced and reported. | (none) |
| Observability | OBS-016 | SIEM forwarding delivers test event <60s | Security/event forwarding to SIEM delivers test events within freshness target. | (none) |
| Observability | OBS-017 | All log levels supported; dynamic change works | All log levels are supported and can be changed dynamically. | (none) |
| Observability | OBS-018 | Log level propagation <2min with alert on breach | Log level changes propagate quickly (under defined minutes) with alert if breach. | (none) |
| Observability | OBS-019 | Operational log shows full transaction chain | Operational logs allow full transaction chain reconstruction. | STORY-OBS-019 |
| Observability | OBS-020 | Operations logs reconstruct workflow | Operations logs reconstruct workflow sequences accurately. | (none) |
| Observability | OBS-021 | Operational events include transaction_id | Operational events include a transaction identifier for correlation. | (none) |
| Observability | OBS-022 | Audit trail reconstructs user action | Audit trail can reconstruct a specific user action sequence. | (none) |
| Observability | OBS-023 | Audit events share transaction_id & ordered timestamps | Audit events share transaction IDs and ordered timestamps for traceability. | (none) |
| Observability | OBS-024 | Alert rule triggers multi-channel notification | Alert rules trigger multi-channel notifications (e.g., chat + email). | (none) |
| Observability | OBS-025 | Alerts delivered to multi-channel with context | Alerts delivered with sufficient context to act (multi-channel). | STORY-OBS-025 |
| Observability | OBS-026 | Analytics query identifies usage pattern | Analytics queries identify usage patterns from captured metrics. | (none) |
| Observability | OBS-027 | Analytics outage non-impacting to transactions | Analytics outages do not impact core transaction processing. | (none) |
| Observability | OBS-028 | RBAC restricts dashboard sections | Role-based access control (RBAC) restricts dashboard sections appropriately. | (none) |
| Observability | OBS-029 | Dashboard freshness age ≤60s | Dashboard freshness age remains under target (e.g., ≤60s). | (none) |
| Observability | OBS-031 | Anonymised behaviour metrics collected without identifiers | Anonymised behavioural metrics are collected without exposing personal identifiers. | (none) |
| Observability | OBS-032 | Per-endpoint 4xx/5xx response metrics & alert thresholds configured | Per-endpoint 4xx and 5xx response metrics are captured with alert thresholds so error rate spikes are detected and acted upon quickly. | FTRS-1573 |
| Performance | PERF-001 | Each operation meets registry-defined percentile targets (p50/p95) logged & asserted (see performance/expectations.yaml) | Each API or batch operation meets agreed median and 95th percentile latency targets. | STORY-PERF-001, STORY-PERF-002, STORY-PERF-003, STORY-PERF-004, STORY-PERF-005, STORY-PERF-006, STORY-PERF-007, STORY-PERF-008, STORY-PERF-009, STORY-PERF-010 |
| Performance | PERF-002 | Performance pillar checklist completed & actions closed | Performance pillar checklist is completed and any actions are closed. | (none) |
| Performance | PERF-003 | Performance expectations table versioned & referenced | The versioned performance expectations table is maintained and referenced by tests. | (none) |
| Performance | PERF-004 | Anonymised live-like dataset present & audited | A representative, anonymised dataset exists for realistic performance validation. | (none) |
| Performance | PERF-005 | Automated test suite matches defined actions & exclusions | Automated performance tests implement all defined actions and listed exclusions. | (none) |
| Performance | PERF-006 | Batch window p95 latency delta ≤5% | Batch window latency stays within a small variance (e.g., p95 delta ≤ defined %). | (none) |
| Performance | PERF-007 | Telemetry overhead within CPU & latency thresholds | Telemetry overhead (CPU, latency) remains within acceptable limits while capturing required data. | (none) |
| Performance | PERF-008 | 8h rolling window p95 variance ≤10% | Rolling window performance variance remains stable within target percentage bounds. | (none) |
| Performance | PERF-009 | Regression alert triggers on >10% p95 increase | Alerting triggers when p95 latency regresses beyond the defined threshold (e.g., >10%). | (none) |
| Performance | PERF-010 | Percentile methodology document & tool configuration aligned | Documented percentile methodology matches tool configuration (consistent measurement). | (none) |
| Performance | PERF-011 | dos-search endpoints sustain burst ≥150 TPS (registry burst_tps_target) | GP search endpoints handle short burst throughput at or above the target TPS. | (placeholder) |
| Performance | PERF-012 | dos-search endpoints sustain steady ≥150 TPS (registry sustained_tps_target) | GP search endpoints sustain steady-state throughput at or above the TPS target. | (placeholder) |
| Performance | PERF-013 | Request payload size per endpoint ≤1MB (max_request_payload_bytes) | Endpoint request payloads remain under the maximum defined size to protect performance. | (placeholder) |
| Reliability | REL-001 | Health checks, multi-AZ deployment documented | Service remains healthy across multiple availability zones with verified health checks. | (none) |
| Reliability | REL-003 | Lifecycle reliability checklist completed | Lifecycle reliability checklist is completed for the service components. | (none) |
| Reliability | REL-004 | DoS simulation mitigated; service responsive | Denial-of-service (DoS) simulation shows successful mitigation and continued responsiveness. | (none) |
| Reliability | REL-005 | Injection attempt blocked; no code execution | Injection attacks are blocked, preventing arbitrary code execution attempts. | (none) |
| Reliability | REL-006 | Placement scan shows no forbidden co-residency | Resource placement scan shows no forbidden co-residency (e.g., sensitive + public workloads). | (none) |
| Reliability | REL-008 | MITM attempt fails; pinned cert validation passes | Man-in-the-middle (MITM) attempts fail due to secure certificate pinning. | (none) |
| Reliability | REL-009 | Iframe embed blocked; headers verified | UI prevents iframe embedding (clickjacking) via secure headers. | (none) |
| Reliability | REL-012 | Single node removal shows stable performance & zero data loss | Removing a single node yields no data loss and minimal performance impact. | (none) |
| Reliability | REL-014 | External outage shows fallback & user messaging | External dependency outage invokes fallback and clear user messaging. | (none) |
| Reliability | REL-015 | LB failure retains sessions & continues routing | Load balancer failure preserves sessions and maintains routing continuity. | (none) |
| Reliability | REL-016 | Server error shows logout/message per spec | Server error paths show expected logout or user messaging per specification. | STORY-REL-016 |
| Reliability | REL-017 | Restore drill meets RPO/RTO & ransomware defenses | Restore drills meet RPO/RTO targets and confirm ransomware defenses. | (none) |
| Scalability | SCAL-003 | All layers pass scalability checklist | All layers (app, DB, cache) meet defined scalability checklist items. | (none) |
| Scalability | SCAL-004 | Scale-down events occur after sustained low utilisation | Scale-down only occurs after sustained low utilisation (not transient dips). | (none) |
| Scalability | SCAL-008 | No manual scaling tickets for variance period | During the variance period no manual scaling tickets are needed. | (none) |
| Scalability | SCAL-009 | Audit logs capture actor/reason for scaling | Audit logs record who initiated scaling and why. | (none) |
| Scalability | SCAL-010 | Predictive alert fires at utilisation forecast threshold | Predictive alerts fire before utilisation reaches critical thresholds. | (none) |

## Operations

| Operation ID | p50 ms | p95 ms | Max ms | Burst TPS | Sustained TPS | Max Payload (bytes) | Status | Rationale |
|--------------|--------|--------|--------|-----------|---------------|---------------------|--------|-----------|
| dm-full-sync | 1200000 | 1800000 | 2700000 |  |  |  | draft | End-to-end duration baseline including transform and upserts |
| dm-record-transform | 120 | 250 | 800 |  |  |  | draft | Single legacy record validation + transform + upsert |

## Controls

### OBS-025

Alerts delivered to multi-channel with context

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| migration-variance-alerts | Actionable alerts on data-migration error rate and duration variance | Alert when error_rate >1% over 5m window OR full-sync duration > baseline +20%; include playbook link, correlation_id, impacted counts | Metrics backend, alerting engine, synthetic event injector, dashboard | Continuous evaluation; monthly threshold tuning; weekly report | int,ref,prod | data-migration | draft | Early detection of pipeline health issues to reduce MTTR and prevent silent degradation |
