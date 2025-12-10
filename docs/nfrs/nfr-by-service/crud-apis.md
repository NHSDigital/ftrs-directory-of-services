# FtRS NFR – Service: crud-apis

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Availability | AVAIL-001 | Availability report shows ≥99.90% multi-AZ uptime | Multi-AZ deployment achieves target uptime (e.g., ≥99.90%). | STORY-AVAIL-001 |
| Availability | AVAIL-002 | Region DR simulation meets plan objectives | Disaster recovery (DR) simulation meets documented objectives. | STORY-AVAIL-002 |
| Availability | AVAIL-003 | Uptime monitoring confirms 24x7 coverage | Continuous uptime monitoring covers 24x7 operations. | STORY-AVAIL-003 |
| Availability | AVAIL-004 | Monthly maintenance minutes ≤150; single ≤60 | Maintenance windows stay within monthly and per-event minute limits. | STORY-AVAIL-004 |
| Availability | AVAIL-005 | Tuesday window executed; smoke tests pass | Scheduled maintenance executes successfully with passing smoke tests afterward. | (none) |
| Availability | AVAIL-006 | DR exercise restores service <2h | DR exercise restores service within target recovery time (< defined hours). | (none) |
| Availability | AVAIL-007 | Replication lag ≤60s; fail-over data delta minimal | Data replication lag remains under target ensuring minimal failover delta. | (none) |
| Availability | AVAIL-008 | API uptime aligns with core service | API uptime aligns with overall service availability target. | (none) |
| Availability | AVAIL-009 | Non-UK access attempts blocked & logged | Access from non-approved geographic regions is blocked and logged. | (none) |
| Availability | AVAIL-010 | Blue/green deployment produces 0 failed requests | Blue/green deployments complete with zero failed user requests. | (none) |
| Compatibility | COMP-002 | MFA (CIS2) succeeds across supported platforms | Multi-factor authentication (CIS2) works across supported platforms. | (none) |
| Cost | COST-001 | Mandatory tagging set present on 100% resources | All resources have mandatory cost tags for allocation and reporting. | STORY-COST-001 |
| Cost | COST-002 | Monthly Cost Explorer review & anomaly log | Monthly cost review identifies anomalies and tracks actions. | STORY-COST-002 |
| Cost | COST-003 | CloudHealth access for each team infra engineer | Each team infra engineer has access to cost analysis tooling (e.g., CloudHealth). | STORY-COST-003 |
| Cost | COST-004 | CloudHealth optimisation & tag compliance reports | Optimisation and tag compliance reports are produced and reviewed. | STORY-COST-004 |
| Cost | COST-005 | Budgets & alert notifications configured & tested | Budgets and cost alert notifications are configured and tested. | STORY-COST-005 |
| Cost | COST-006 | #ftrs-cost-alerts channel created & receiving test alerts | Dedicated cost alerts channel receives test and live notifications. | (none) |
| Cost | COST-007 | Quarterly cost review minutes & tracked actions | Quarterly cost reviews record minutes and follow-up actions. | (none) |
| Governance | GOV-001 | Service Management pre-live acceptance signed | Service Management pre-live acceptance is signed off before go-live. | STORY-GOV-001 |
| Governance | GOV-002 | Well-Architected review completed & actions closed | Well-Architected review completed; remediation actions closed. | STORY-GOV-002 |
| Governance | GOV-003 | Solution Architecture Framework assessment approved | Solution Architecture Framework assessment is approved. | STORY-GOV-003 |
| Governance | GOV-004 | Engineering Red-lines compliance checklist signed | Engineering red-lines compliance checklist is signed. | STORY-GOV-004 |
| Governance | GOV-005 | GDPR compliance assessment signed by IG | GDPR compliance assessment signed by Information Governance. | STORY-GOV-005 |
| Governance | GOV-006 | Medical Device out-of-scope statement recorded | Statement confirming service is out of scope for Medical Device regulation. | (none) |
| Governance | GOV-007 | FtRS Architects review & approval logged | Architecture review and approval logged by FtRS architects. | (none) |
| Governance | GOV-008 | Cloud Expert deployment approval documented | Cloud expert deployment approval documented (infrastructure readiness). | (none) |
| Governance | GOV-009 | Solution Assurance approval ticket closed | Solution Assurance approval ticket is closed. | (none) |
| Governance | GOV-010 | Clinical Safety assurance approval recorded | Clinical Safety assurance approval recorded. | (none) |
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
| Interoperability | INT-005 | Standard OperationOutcome error structure enforced | Error responses follow standard OperationOutcome structure. | STORY-INT-001 |
| Interoperability | INT-006 | Identifier normalization applied (uppercase, trimmed) | Identifiers are normalised (case, trimming) for consistent matching. | (none) |
| Interoperability | INT-007 | Strict content negotiation implemented | Strict content negotiation enforces supported media types only. | STORY-INT-002 |
| Interoperability | INT-009 | Only documented FHIR search params accepted | Only documented FHIR search parameters are accepted; unknown ones rejected. | (none) |
| Interoperability | INT-010 | Version-controlled integration contract published | Integration contract is version-controlled and published. | (none) |
| Interoperability | INT-011 | Machine-readable changelog generated | Machine-readable changelog is generated for each release. | (none) |
| Interoperability | INT-012 | Terminology bindings validated | Terminology bindings are validated to ensure correct coding. | (none) |
| Interoperability | INT-013 | Correlation IDs preserved across calls | Correlation IDs persist across internal and external calls for tracing. | STORY-INT-004 |
| Interoperability | INT-014 | Null vs absent data handled per FHIR | Null vs absent data semantics follow FHIR specification rules. | (none) |
| Interoperability | INT-015 | ≥90% interoperability scenario coverage | Test coverage spans ≥90% of defined interoperability scenarios. | (none) |
| Interoperability | INT-016 | Stateless sequence-independent operations | Operations are stateless and do not rely on sequence order. | (none) |
| Interoperability | INT-017 | Complete field-level input validation every request | Input validation covers every field on every request to prevent malformed data. | STORY-INT-005, STORY-INT-017 |
| Interoperability | INT-018 | Comprehensive published OpenAPI documentation (overview, audience, related APIs, roadmap, SLA, tech stack, network access, security/auth, test environment, onboarding, endpoints with examples) | Comprehensive OpenAPI documentation is published (overview, audience, related APIs, roadmap, SLA, tech stack, security/auth, test environment, onboarding, endpoints with examples) to support integrator adoption. | (none) |
| Observability | OBS-001 | App & infra health panels show green | Application and infrastructure health panels display green status during normal operation. | STORY-OBS-001 |
| Observability | OBS-002 | Authenticated remote health dashboard accessible | Authenticated remote health dashboard is accessible to support teams. | (none) |
| Observability | OBS-003 | Health event visible ≤60s after failure | Health events appear on dashboards shortly after failures (within target freshness). | (none) |
| Observability | OBS-004 | Automated maintenance tasks executed; zero manual interventions | Automated maintenance tasks run successfully with no manual intervention required. | (none) |
| Observability | OBS-005 | Performance metrics per layer present | Layered performance metrics (app, DB, cache) are visible. | (none) |
| Observability | OBS-006 | Remote performance dashboard matches local view | Remote performance dashboard mirrors local environment metrics accurately. | (none) |
| Observability | OBS-007 | Performance metrics latency ≤60s | Performance metrics latency (ingest to display) stays within defined limit (e.g., ≤60s). | STORY-OBS-002 |
| Observability | OBS-008 | TPS per endpoint displayed & threshold alert configured | Per-endpoint transactions per second (TPS) are displayed with alert thresholds. | STORY-OBS-003 |
| Observability | OBS-009 | Endpoint latency histograms with p50/p95/p99 | Latency histograms show p50/p95/p99 for each endpoint. | STORY-OBS-004 |
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
| Observability | OBS-026 | Analytics query identifies usage pattern | Analytics queries identify usage patterns from captured metrics. | (none) |
| Observability | OBS-027 | Analytics outage non-impacting to transactions | Analytics outages do not impact core transaction processing. | (none) |
| Observability | OBS-028 | RBAC restricts dashboard sections | Role-based access control (RBAC) restricts dashboard sections appropriately. | (none) |
| Observability | OBS-029 | Dashboard freshness age ≤60s | Dashboard freshness age remains under target (e.g., ≤60s). | (none) |
| Observability | OBS-030 | Distributed trace spans cover end-to-end request | Distributed tracing spans cover end-to-end request path. | STORY-OBS-005 |
| Observability | OBS-031 | Anonymised behaviour metrics collected without identifiers | Anonymised behavioural metrics are collected without exposing personal identifiers. | (none) |
| Observability | OBS-032 | Per-endpoint 4xx/5xx response metrics & alert thresholds configured | Per-endpoint 4xx and 5xx response metrics are captured with alert thresholds so error rate spikes are detected and acted upon quickly. | [FTRS-1573](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1573) |
| Observability | OBS-033 | Unauthorized API access attempts logged, classified, alerted | Unauthorized API access attempts (failed authentication, forbidden operations, rate limit breaches, anomalous spikes) are logged with required context and generate timely alerts for early detection of credential misuse or attack patterns. | [FTRS-1607](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1607) |
| Performance | PERF-001 | Each operation meets registry-defined percentile targets (p50/p95) logged & asserted (see performance/expectations.yaml) | Each API or batch operation meets agreed median and 95th percentile latency targets. | STORY-PERF-001, STORY-PERF-002, STORY-PERF-003, STORY-PERF-004, STORY-PERF-005, STORY-PERF-006, STORY-PERF-007, STORY-PERF-008, STORY-PERF-009, STORY-PERF-010 |
| Performance | PERF-002 | Performance pillar checklist completed & actions closed | Performance pillar checklist is completed and any actions are closed. | (none) |
| Performance | PERF-003 | Performance expectations table versioned & referenced | The versioned performance expectations table is maintained and referenced by tests. | (none) |
| Performance | PERF-004 | Anonymised live-like dataset present & audited | A representative, anonymised dataset exists for realistic performance validation. | (none) |
| Performance | PERF-005 | Automated test suite matches defined actions & exclusions | Automated performance tests implement all defined actions and listed exclusions. | (none) |
| Performance | PERF-007 | Telemetry overhead within CPU & latency thresholds | Telemetry overhead (CPU, latency) remains within acceptable limits while capturing required data. | (none) |
| Performance | PERF-008 | 8h rolling window p95 variance ≤10% | Rolling window performance variance remains stable within target percentage bounds. | (none) |
| Performance | PERF-009 | Regression alert triggers on >10% p95 increase | Alerting triggers when p95 latency regresses beyond the defined threshold (e.g., >10%). | (none) |
| Performance | PERF-010 | Percentile methodology document & tool configuration aligned | Documented percentile methodology matches tool configuration (consistent measurement). | (none) |
| Performance | PERF-013 | Request payload size per endpoint ≤1MB (max_request_payload_bytes) | Endpoint request payloads remain under the maximum defined size to protect performance. | (placeholder) |
| Reliability | REL-001 | Health checks, multi-AZ deployment documented | Service remains healthy across multiple availability zones with verified health checks. | (none) |
| Reliability | REL-002 | AZ failure simulation maintains service | Simulated AZ failure does not interrupt service delivery. | STORY-REL-001 |
| Reliability | REL-003 | Lifecycle reliability checklist completed | Lifecycle reliability checklist is completed for the service components. | (none) |
| Reliability | REL-004 | DoS simulation mitigated; service responsive | Denial-of-service (DoS) simulation shows successful mitigation and continued responsiveness. | (none) |
| Reliability | REL-005 | Injection attempt blocked; no code execution | Injection attacks are blocked, preventing arbitrary code execution attempts. | (none) |
| Reliability | REL-006 | Placement scan shows no forbidden co-residency | Resource placement scan shows no forbidden co-residency (e.g., sensitive + public workloads). | (none) |
| Reliability | REL-007 | Brute force/auth anomalies rate limited & alerted (peak 500 TPS burst capacity; rate limits + alerts) | Brute force or auth anomaly attempts are rate limited and create alerts. | [FTRS-1598](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1598) |
| Reliability | REL-008 | MITM attempt fails; pinned cert validation passes | Man-in-the-middle (MITM) attempts fail due to secure certificate pinning. | (none) |
| Reliability | REL-011 | Unhealthy node auto-replaced; workload continues | Unhealthy nodes are automatically replaced with workload continuity. | STORY-REL-003 |
| Reliability | REL-012 | Single node removal shows stable performance & zero data loss | Removing a single node yields no data loss and minimal performance impact. | (none) |
| Reliability | REL-013 | Tier failure graceful degradation & recovery evidenced | Tier failure triggers graceful degradation and later clean recovery. | STORY-REL-004 |
| Reliability | REL-014 | External outage shows fallback & user messaging | External dependency outage invokes fallback and clear user messaging. | (none) |
| Reliability | REL-015 | LB failure retains sessions & continues routing | Load balancer failure preserves sessions and maintains routing continuity. | (none) |
| Reliability | REL-017 | Restore drill meets RPO/RTO & ransomware defenses | Restore drills meet RPO/RTO targets and confirm ransomware defenses. | (none) |
| Scalability | SCAL-001 | Horizontal scale-out increases TPS linearly within tolerance | Horizontal scaling increases throughput nearly linearly without quality loss. | STORY-SCAL-001 |
| Scalability | SCAL-002 | Vertical resize retains data & function without downtime | Vertical resizing (bigger instance) retains data and operation with no downtime. | STORY-SCAL-002 |
| Scalability | SCAL-003 | All layers pass scalability checklist | All layers (app, DB, cache) meet defined scalability checklist items. | (none) |
| Scalability | SCAL-004 | Scale-down events occur after sustained low utilisation | Scale-down only occurs after sustained low utilisation (not transient dips). | (none) |
| Scalability | SCAL-005 | Autoscaling policy simulation triggers controlled scale | Autoscaling policy simulations trigger controlled scaling actions. | STORY-SCAL-003 |
| Scalability | SCAL-006 | Scale event shows no SLA breach in latency/error | Scaling events do not cause SLA breaches in latency or error rate. | STORY-SCAL-004 |
| Scalability | SCAL-007 | Capacity report shows ≥30% headroom | Capacity planning shows adequate headroom (e.g., ≥30%). | STORY-SCAL-005 |
| Scalability | SCAL-008 | No manual scaling tickets for variance period | During the variance period no manual scaling tickets are needed. | (none) |
| Scalability | SCAL-009 | Audit logs capture actor/reason for scaling | Audit logs record who initiated scaling and why. | (none) |
| Scalability | SCAL-010 | Predictive alert fires at utilisation forecast threshold | Predictive alerts fire before utilisation reaches critical thresholds. | (none) |
| Security | SEC-001 | Crypto algorithms conform; weak ciphers rejected | Use only strong, approved cryptographic algorithms; weak or deprecated ciphers are blocked. | STORY-SEC-013 |
| Security | SEC-002 | WAF security pillar checklist completed & gaps tracked | Complete the AWS/WAF security pillar checklist and track remediation actions for any gaps. | (none) |
| Security | SEC-003 | All endpoints TLS only; storage encryption enabled | All service endpoints enforce TLS and all stored data (databases, buckets) is encrypted at rest. | [FTRS-1563](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1563) |
| Security | SEC-004 | Storage services show encryption enabled | Every storage service (S3, RDS, etc.) shows encryption enabled with managed or customer keys. | (none) |
| Security | SEC-005 | Cross-environment data access attempts denied | Strict environment isolation: data access from one environment to another is prevented. | (none) |
| Security | SEC-006 | No direct prod console queries detected in audit period | No direct production console queries by engineers outside approved, audited break-glass processes. | (none) |
| Security | SEC-007 | SG rules audited; attempt broad ingress denied | Network security groups allow only narrowly scoped inbound rules; broad ingress is denied. | STORY-SEC-017 |
| Security | SEC-008 | Perimeter scan shows no broad whitelist & secure channels | Perimeter scans show secure transport, no open broad whitelists, and hardened edge configuration. | (none) |
| Security | SEC-009 | ASVS & CIS benchmark automation reports pass thresholds | Automated ASVS and CIS benchmark scans meet pass thresholds; failures trigger remediation. | (none) |
| Security | SEC-010 | Annual pen test executed; remediation tickets raised & closed | Annual penetration test completed; identified issues tracked and closed. | (none) |
| Security | SEC-011 | Security features enabled latency within SLA | Enabling security controls does not push latency beyond defined SLAs. | (none) |
| Security | SEC-012 | IAM policy review confirms least privilege for system roles | IAM roles and policies grant least privilege; periodic reviews confirm minimal access. | (none) |
| Security | SEC-013 | Key rotation events logged; unauthorized access denied | Cryptographic keys rotate on schedule and unauthorized access attempts are rejected and logged. | (none) |
| Security | SEC-014 | mTLS handshake succeeds between designated services | Mutual TLS (mTLS) succeeds between designated internal services to protect sensitive flows. | [FTRS-1600](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1600) |
| Security | SEC-015 | Expiry alert fired in advance; renewal executed seamlessly | Certificate expiry is detected in advance; renewal occurs without downtime. | [FTRS-1604](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1604) |
| Security | SEC-016 | MFA enforced for all privileged infra roles | Privileged infrastructure roles require multi-factor authentication (MFA). | STORY-SEC-023 |
| Security | SEC-017 | Scan reports zero unmanaged long-lived credentials | No long-lived unmanaged credentials; periodic scans confirm only managed secrets exist. | (none) |
| Security | SEC-018 | Supplier audit attestation stored & verified | Third-party supplier security attestation is collected and stored for audit. | (none) |
| Security | SEC-019 | Segmentation test confirms tenant isolation | Tenant or data segmentation tests confirm isolation boundaries hold. | (none) |
| Security | SEC-021 | Port scan matches approved diagnostic list only | Port scans reveal only approved diagnostic and service ports—no unexpected exposures. | (none) |
| Security | SEC-022 | Utility program access restricted to approved roles | Access to powerful utility programs is restricted to approved roles. | (none) |
| Security | SEC-023 | Deployment provenance shows unique traceable accounts | Deployment provenance shows traceable unique accounts per automated pipeline stage. | (none) |
| Security | SEC-024 | Code/data transfer logs show integrity & secure channels | Transfer of code or data maintains integrity and uses secure channels; events are logged. | (none) |
| Security | SEC-025 | PID requests enforce mTLS; plain text blocked | Requests containing identifiable patient data enforce mTLS; plaintext attempts are blocked. | STORY-SEC-003 |
| Security | SEC-026 | API responses contain no unencrypted PID fields | API responses never include unencrypted patient identifiable data (PID) fields. | (none) |
| Security | SEC-027 | Build fails on high CVE; report archived | Build pipeline blocks release when critical CVEs exceed threshold; reports archived. | STORY-SEC-002 |
| Security | SEC-028 | Release pipeline blocks on critical unresolved findings | Releases are halted if critical unresolved security findings remain. | (none) |
| Security | SEC-029 | All API endpoints enforce CIS2 JWT authentication (signature, issuer, audience, assurance claims) | All API endpoints enforce CIS2 JWT authentication with signature, issuer, audience and required assurance claim validation; invalid or missing tokens are rejected with structured errors. | [FTRS-1593](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1593) |
| Security | SEC-030 | Certificates and private keys stored only in approved encrypted secret stores; zero plain text exposure | Certificates and private keys are stored only in approved encrypted secret stores (e.g., Secrets Manager/KMS) with zero plaintext exposure across repositories, images, logs, or build artifacts; continuous scanning enforces compliance. | [FTRS-1602](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1602) |

## Operations

| Operation ID | p50 ms | p95 ms | Max ms | Burst TPS | Sustained TPS | Max Payload (bytes) | Status | Rationale |
|--------------|--------|--------|--------|-----------|---------------|---------------------|--------|-----------|
| healthcare-service-get | 50 | 120 | 350 |  |  |  | draft | Direct read + lightweight mapping |
| org-get | 40 | 100 | 300 |  |  |  | draft | Simple primary key lookup; cached storage path |
| org-search-ods | 60 | 140 | 400 |  |  |  | draft | ODS code normalization + single index scan |
| org-update | 70 | 150 | 400 |  |  |  | draft | Validation + persistence + OperationOutcome classification |

## Controls

### AVAIL-001

Availability report shows ≥99.90% multi-AZ uptime

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| multi-az-uptime-report | Availability report shows ≥99.90% multi-AZ uptime | >= 99.90% monthly uptime across multi-AZ deployment | Uptime monitoring + monthly report automation | Monthly | prod | crud-apis | draft | Tracks SLA against multi-AZ deployment goals |

### AVAIL-002

Region DR simulation meets plan objectives

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| region-dr-simulation | Region DR simulation meets plan objectives | DR exercise meets RTO/RPO targets and user impact objectives | DR runbooks + simulation exercises | Semi-annual | int,ref | crud-apis | draft | Validates disaster recovery readiness across regions |

### AVAIL-003

Uptime monitoring confirms 24x7 coverage

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| uptime-monitoring-coverage | Uptime monitoring confirms 24x7 coverage | 24x7 coverage; alerts configured for service degradation | Uptime monitors + alerting system | Continuous monitoring | prod | crud-apis | draft | Ensures continuous availability monitoring |

### AVAIL-004

Monthly maintenance minutes ≤150; single ≤60

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| maintenance-window-minutes | Monthly maintenance minutes ≤150; single ≤60 | Monthly total ≤150 minutes; single window ≤60 minutes | Maintenance logs + reporting | Monthly | prod | crud-apis | draft | Controls maintenance impact to meet availability objectives |

### AVAIL-005

Tuesday window executed; smoke tests pass

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| scheduled-maintenance-smoke-tests | Tuesday window executed; smoke tests pass | Maintenance completes; post-window smoke tests 100% pass; no Sev-1/2 incidents | Deployment controller + smoke test suite + incident log | Weekly maintenance window | prod | crud-apis | draft | Ensures safe scheduled maintenance without user impact |

### AVAIL-006

DR exercise restores service <2h

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| dr-exercise-rto | DR exercise restores service <2h | End-to-end restore < 120 minutes; data loss = 0 per RPO | DR runbook + timer + integrity checks | Semi-annual exercise | int,ref | crud-apis | draft | Validates recovery objectives and data integrity |

### AVAIL-007

Replication lag ≤60s; fail-over data delta minimal

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| replication-lag-threshold | Replication lag \u226460s; fail-over data delta minimal | Replication lag \u2264 60s for primary datasets; failover delta \u2264 1% records | Replication metrics + failover audit | Continuous + monthly report | prod | crud-apis | draft | Ensures rapid failover with minimal inconsistency |

### AVAIL-008

API uptime aligns with core service

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| api-uptime-sla | API uptime aligns with core service | API uptime \u2265 99.90% monthly; maintenance excluded per policy | Uptime monitors + SLA calculator | Monthly | prod | crud-apis | draft | Aligns API availability to overall SLA |

### AVAIL-009

Non-UK access attempts blocked & logged

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| geo-blocking-enforced | Non-UK access attempts blocked & logged | 100% non-UK requests blocked at edge; structured log with country + ip | WAF geo rules + edge logs | Continuous + weekly audit | prod | crud-apis | draft | Reduces risk from out-of-region access |

### AVAIL-010

Blue/green deployment produces 0 failed requests

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| blue-green-zero-failures | Blue/green deployment produces 0 failed requests | 0 failed requests during blue/green switch | Deployment controller + canary telemetry | Per deployment | int,ref,prod | crud-apis | draft | Ensures safe deployments without user impact |

### COMP-002

MFA (CIS2) succeeds across supported platforms

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| mfa-platforms | MFA (CIS2) succeeds across supported platforms | MFA journeys pass across supported platforms | Cross-platform test suite + identity provider logs | Release cycle | int,ref,prod | crud-apis | draft | Ensures authentication compatibility |

### COST-001

Mandatory tagging set present on 100% resources

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| mandatory-tagging | Mandatory tagging set present on 100% resources | 100% resources carry mandatory tags | AWS Config rules + tag audit automation | Continuous + monthly report | dev,int,ref,prod | crud-apis | draft | Enables cost visibility and accountability |

### COST-002

Monthly Cost Explorer review & anomaly log

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| monthly-cost-review | Monthly Cost Explorer review & anomaly log | Review completed; anomalies logged with actions | Cost Explorer + anomaly detection | Monthly | prod | crud-apis | draft | Ensures proactive cost management |

### COST-003

CloudHealth access for each team infra engineer

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| cloudhealth-access | CloudHealth access for each team infra engineer | Access provisioned; onboarding verified | CloudHealth admin + access logs | Quarterly verification | prod | crud-apis | draft | Ensures teams can act on cost insights |

### COST-004

CloudHealth optimisation & tag compliance reports

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| optimisation-reports | CloudHealth optimisation & tag compliance reports | Reports generated; tracked actions created | CloudHealth reporting + tracker | Monthly | prod | crud-apis | draft | Drives optimisation and tag hygiene |

### COST-005

Budgets & alert notifications configured & tested

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| budgets-and-alerts | Budgets & alert notifications configured & tested | Budgets configured; alerts tested successfully | AWS Budgets + notifications | Quarterly + pre-fiscal review | prod | crud-apis | draft | Prevents cost overruns via alerting |

### GOV-001

Service Management pre-live acceptance signed

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| service-management-pre-live | Service Management pre-live acceptance signed | Acceptance signed; evidence stored | Governance tracker + document repository | Pre-live | prod | crud-apis | draft | Ensures service readiness sign-off |

### GOV-002

Well-Architected review completed & actions closed

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| well-architected-review | Well-Architected review completed & actions closed | Review complete; actions closed or exceptioned | WAR tool + issue tracker | Pre-live + annual | prod | crud-apis | draft | Maintains architectural quality |

### GOV-003

Solution Architecture Framework assessment approved

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| saf-assessment-approved | Solution Architecture Framework assessment approved | Approved assessment stored with evidence link; exceptions recorded | Governance tracker + document repository | Pre-live | prod | crud-apis | draft | Ensures architectural governance sign-off |

### GOV-004

Engineering Red-lines compliance checklist signed

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| nhs-github-enterprise-repos | All FtRS code repositories are hosted in NHS GitHub Enterprise and comply with securing-repositories policy; engineering dashboards show compliance | 100% repositories on NHS GitHub Enterprise; 100% securing-repositories checks passing; exceptions recorded with owner and review date | Enterprise repository policy audit + engineering compliance dashboards + CI checks | Continuous (CI on change) + quarterly governance review | dev,int,ref,prod | crud-apis | draft | Enforces organisational SDLC-1 Red Line for using NHS GitHub Enterprise and securing repositories; provides traceable evidence and automated verification |

### GOV-005

GDPR compliance assessment signed by IG

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| gdpr-assessment-signed | GDPR compliance assessment signed by IG | Assessment signed; actions tracked | IG workflow + evidence repository | Pre-live + annual | prod | crud-apis | draft | Ensures data protection compliance |

### GOV-006

Medical Device out-of-scope statement recorded

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| medical-device-out-of-scope | Medical Device out-of-scope statement recorded | Statement recorded and reviewed annually | Evidence repository | Annual review | prod | crud-apis | draft | Confirms regulatory position |

### GOV-007

FtRS Architects review & approval logged

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| ftrs-architects-approval | FtRS Architects review & approval logged | Review minutes and approval recorded; actions tracked | Review tracker + minutes repo | Pre-live + on major change | prod | crud-apis | draft | Provides architectural oversight evidence |

### GOV-008

Cloud Expert deployment approval documented

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| cloud-expert-approval | Cloud Expert deployment approval documented | Approval recorded; infra readiness checklist passed | Infra checklist + evidence repo | Pre-live | prod | crud-apis | draft | Confirms infrastructure deployment readiness |

### GOV-009

Solution Assurance approval ticket closed

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| solution-assurance-approval | Solution Assurance approval ticket closed | Approval obtained; ticket closed | Assurance workflow + evidence repository | Pre-live | prod | crud-apis | draft | Meets governance approval requirements |

### GOV-010

Clinical Safety assurance approval recorded

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| clinical-safety-approval | Clinical Safety assurance approval recorded | Approval recorded; evidence available | Clinical safety workflow + repository | Pre-live | prod | crud-apis | draft | Complies with clinical safety governance |

### GOV-011

Information Governance approval recorded

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| ig-approval-recorded | Information Governance approval recorded | Approval recorded; actions tracked | IG workflow + evidence repository | Pre-live | prod | crud-apis | draft | Meets IG governance |

### GOV-012

TRG approval session outcome logged

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| trg-approval-outcome | TRG approval session outcome logged | Outcome recorded; decisions minuted; actions tracked | TRG minutes + tracker | Pre-live | prod | crud-apis | draft | Documents technical governance approval |

### GOV-013

SIRO sign-off obtained

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| siro-signoff | SIRO sign-off obtained | Sign-off recorded; evidence stored | Governance tracker | Pre-live | prod | crud-apis | draft | Confirms senior risk acceptance |

### GOV-014

Caldicott Principles Guardian approval recorded

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| caldicott-guardian-approval | Caldicott Principles Guardian approval recorded | Approval recorded with data handling summary | Governance tracker + evidence repo | Pre-live | prod | crud-apis | draft | Ensures data handling governance |

### GOV-015

DUEC Assurance Board acceptance logged

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| duec-acceptance | DUEC Assurance Board acceptance logged | Acceptance recorded; actions tracked | Board minutes + tracker | Pre-live | prod | crud-apis | draft | Documents assurance acceptance |

### GOV-016

Live Services Board go-live approval recorded

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| live-services-go-live | Live Services Board go-live approval recorded | Go-live approval recorded; evidence stored | Governance tracker + evidence repo | Pre-live | prod | crud-apis | draft | Final governance approval before production |

### INT-001

Resources validated against UK Core profiles

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| uk-core-profile-validation | Resources validated against UK Core profiles | 100% resources pass UK Core validation in CI and pre-release audit | FHIR validators + contract test suite | CI per build + quarterly audit | int,ref,prod | crud-apis | draft | Ensures national standard alignment |

### INT-002

Versioning & deprecation policy published

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| versioning-deprecation-policy | Versioning & deprecation policy published | Policy published; changes communicated; minimum 6 months deprecation window | Documentation repo + change comms channel | Review quarterly; update on change | prod | crud-apis | draft | Reduces integration friction |

### INT-003

Minor releases backward compatible for 12 months

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| backward-compatibility-window | Minor releases backward compatible for 12 months | No breaking changes; deprecation window \u226512 months; exceptions recorded | Contract tests + release notes | CI per build + release review | prod | crud-apis | draft | Protects consumer integrations |

### INT-004

Semantic mapping round-trip fidelity preserved

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| semantic-roundtrip-fidelity | Semantic mapping round-trip fidelity preserved | Round-trip preserves fields and codes; divergence \u2264 1% | Mapping tests + diff reports | CI per build + monthly audit | int,ref | crud-apis | draft | Maintains semantic integrity |

### INT-005

Standard OperationOutcome error structure enforced

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| operationoutcome-structure | Standard OperationOutcome error structure enforced | 100% error responses conform to OperationOutcome spec | Contract tests + schema validators | CI per build + weekly contract audit | int,ref,prod | crud-apis | draft | Ensures consistent error semantics across integrations |

### INT-006

Identifier normalization applied (uppercase, trimmed)

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| identifier-normalization-enforced | Identifier normalization applied (uppercase, trimmed) | 100% identifiers normalised; mismatches \u2264 0.1% | Normalization middleware + validation tests | CI per build + monthly audit | int,ref,prod | crud-apis | draft | Ensures consistent identifier handling |

### INT-007

Strict content negotiation implemented

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| strict-content-negotiation | Strict content negotiation implemented | Only documented media types accepted; correct response Content-Type | API contract tests + gateway policies | CI per build | int,ref,prod | crud-apis | draft | Prevents ambiguity in accepted formats |

### INT-009

Only documented FHIR search params accepted

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| documented-search-params-only | Only documented FHIR search params accepted | Unknown search params rejected with OperationOutcome | API gateway policy + contract tests | CI per build | int,ref,prod | crud-apis | draft | Prevents ambiguity in search semantics |

### INT-010

Version-controlled integration contract published

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| version-controlled-contract | Version-controlled integration contract published | Contract published under version control; lint passes; updated \u22645 business days after change | Spec repo + Spectral lint + diff job | CI per build + weekly audit | int,ref,prod | crud-apis | draft | Ensures consistent and timely documentation |

### INT-011

Machine-readable changelog generated

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| machine-readable-changelog | Machine-readable changelog generated | Changelog generated per release with breaking changes highlighted | Release pipeline + changelog generator | Per release | prod | crud-apis | draft | Supports integrators with clear changes |

### INT-012

Terminology bindings validated

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| terminology-binding-validation | Terminology bindings validated | 100% required bindings validated against value sets | Terminology server + validators | CI per build + monthly audit | int,ref,prod | crud-apis | draft | Ensures correct coding practices |

### INT-013

Correlation IDs preserved across calls

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| correlation-id-preserved | Correlation IDs preserved across calls | 100% requests preserve transaction_id/correlation_id in logs and headers | Middleware + log correlation tests | CI per build + monthly audit | int,ref,prod | crud-apis | draft | Enables end-to-end tracing and diagnostics |

### INT-014

Null vs absent data handled per FHIR

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| null-vs-absent-semantics | Null vs absent data handled per FHIR | Responses follow FHIR rules; conformance tests pass | Contract tests + response validators | CI per build | int,ref,prod | crud-apis | draft | Clarifies response semantics for consumers |

### INT-015

≥90% interoperability scenario coverage

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| interoperability-scenario-coverage | \u226590% interoperability scenario coverage | \u226590% coverage across documented scenarios; exceptions recorded | Scenario test suite + coverage reports | CI per build + quarterly review | int,ref,prod | crud-apis | draft | Ensures comprehensive interoperability validation |

### INT-016

Stateless sequence-independent operations

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| stateless-sequence-independence | Stateless sequence-independent operations | 100% documented operations produce correct outcome independent of prior invocation order | Idempotence + shuffled sequence integration tests | CI per build + quarterly audit | int,ref,prod | crud-apis | draft | Enables horizontal scaling and predictable consumer integration |

### INT-017

Complete field-level input validation every request

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| field-validation-complete | Complete field-level input validation every request | 100% of inputs validated; rich error responses on failure | Validation layer + contract tests | CI per build | int,ref,prod | crud-apis | draft | Protects system integrity via strict input validation |

### INT-018

Comprehensive published OpenAPI documentation (overview, audience, related APIs, roadmap, SLA, tech stack, network access, security/auth, test environment, onboarding, endpoints with examples)

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| api-documentation-completeness | Comprehensive published OpenAPI documentation | All required catalogue sections present; spec passes lint; updated ≤5 business days after prod change | Spectral lint + spec diff + manual checklist | CI per build + weekly audit | int,ref,prod | crud-apis | draft | Reduces integration friction; ensures transparency for consumers |

### OBS-001

App & infra health panels show green

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| health-panels-green | App & infra health panels show green | All critical panels green; no stale data | Health checks + dashboard status API | Continuous + CI verification on change | int,ref,prod | crud-apis | draft | Ensures at-a-glance service health visibility |

### OBS-007

Performance metrics latency ≤60s

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| perf-metrics-latency | Performance metrics latency ≤60s | Metrics pipeline delivers data within 60s latency | Metrics agent + ingestion SLA alerting | Continuous monitoring | int,ref,prod | crud-apis | draft | Fresh metrics are required for accurate operational decisions |

### OBS-008

TPS per endpoint displayed & threshold alert configured

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| tps-threshold-alert | TPS per endpoint displayed & threshold alert configured | TPS dashboard present; alert rule configured and tested | Metrics backend + alerting system | CI validation + monthly alert fire drill | int,ref,prod | crud-apis | draft | Detects throughput anomalies proactively |

### OBS-009

Endpoint latency histograms with p50/p95/p99

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| latency-histograms | Endpoint latency histograms with p50/p95/p99 | Histograms available per endpoint with p50/p95/p99 series | Metrics backend + dashboard | Continuous | int,ref,prod | crud-apis | draft | Percentile visibility supports performance governance |

### OBS-010

Aggregate latency panel accurate within 2% roll-up

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| aggregate-latency-accuracy | Aggregate latency panel accurate within 2% roll-up | Roll-up accuracy within \u22642% vs raw series | Dashboard query tests + calibration script | Monthly calibration | prod | crud-apis | draft | Ensures trustworthy aggregate metrics |

### OBS-011

Failure types logged & classified in dashboard

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| failure-type-classification | Failure types logged & classified in dashboard | 100% failures carry type; classification accuracy \u2265 95% | Structured logging + classifier + dashboard | Continuous + monthly accuracy audit | int,ref,prod | crud-apis | draft | Improves incident triage |

### OBS-012

Error percentage metric & alert configured

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| error-percentage-alert | Error percentage metric & alert configured | Alert triggers when error% > 1% over 5m; playbook linked | Metrics backend + alerting rules | Continuous + monthly tuning | prod | crud-apis | draft | Early detection of reliability regressions |

### OBS-013

Infra log query returns expected fields

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| infra-log-query-fields | Infra log query returns expected fields | Queries return required fields (timestamp, severity, host, correlation_id) | Log query tests + schema | CI per build + weekly audit | int,ref,prod | crud-apis | draft | Ensures log usability for ops |

### OBS-014

Infra log entries include required fields

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| infra-log-required-fields | Infra log entries include required fields | 100% entries include required fields; schema lint passes | Log schema validators + CI checks | CI per build + monthly audit | int,ref,prod | crud-apis | draft | Guarantees structured logging quality |

### OBS-030

Distributed trace spans cover end-to-end request

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| distributed-trace-coverage | Distributed trace spans cover end-to-end request | ≥95% of requests include spans across key tiers | Tracing SDKs + sampling config | Continuous + monthly sampling review | int,ref,prod | crud-apis | draft | Enables end-to-end diagnosis and correlation across layers |

### OBS-033

Unauthorized API access attempts logged, classified, alerted

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| unauth-access-monitoring | Unauthorized API access attempts logged & alerted with context | 100% auth failures & forbidden requests produce structured log entry with reason, correlation_id, source_ip, user_agent; alert triggers on >5 failed auth attempts per principal per 1m or anomaly spike (>3x baseline) | API gateway logs, auth middleware, metrics backend, alerting rules, anomaly detection job | Continuous collection + weekly anomaly review + monthly rule tuning | int,ref,prod | crud-apis | draft | Early detection of credential stuffing, token misuse, and privilege escalation attempts |

### PERF-001

Each operation meets registry-defined percentile targets (p50/p95) logged & asserted (see performance/expectations.yaml)

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| perf-dos-search-latency | Assert p50/p95/max targets per operation | As per operations in PERF-001 (dos-search endpoints) | synthetic probes + real-user monitoring | continuous | prod | crud-apis | draft | Aligns with defined operation targets |
| perf-lookup-ods-latency | Assert p50/p95/max targets per operation | As per operations in PERF-001 (dos-search endpoints) | synthetic probes + real-user monitoring | continuous | prod | crud-apis | draft | Aligns with defined operation targets |
| perf-nearby-latency | Assert p50/p95/max targets per operation | As per operations in PERF-001 (dos-search endpoints) | synthetic probes + real-user monitoring | continuous | prod | crud-apis | draft | Aligns with defined operation targets |
| perf-org-get-latency | Assert p50/p95/max targets per operation | As per operations in PERF-001 (crud-apis endpoints) | synthetic probes + real-user monitoring | continuous | prod | crud-apis | draft | Aligns with defined operation targets |
| perf-org-update-latency | Assert p50/p95/max targets per operation | As per operations in PERF-001 (crud-apis endpoints) | synthetic probes + real-user monitoring | continuous | prod | crud-apis | draft | Aligns with defined operation targets |

### PERF-013

Request payload size per endpoint ≤1MB (max_request_payload_bytes)

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| perf-request-payload-limits | Request payload size per endpoint \u22641MB | Max_request_payload_bytes enforced per endpoint per operations registry | Gateway payload limit + contract tests | CI per build + monthly audit | int,ref,prod | crud-apis | draft | Prevents oversized payload degradation |

### REL-002

AZ failure simulation maintains service

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| az-failure-simulation | AZ failure simulation maintains service | Successful failover with sustained service availability; no data loss | Chaos simulation + health checks | Quarterly exercise | int,ref | crud-apis | draft | Validates resilience to Availability Zone failures |

### REL-003

Lifecycle reliability checklist completed

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| reliability-checklist-complete | Lifecycle reliability checklist completed | 100% checklist items complete; exceptions recorded with expiry | Checklist tracker + evidence links | Pre-live + quarterly review | int,ref,prod | crud-apis | draft | Ensures reliability practices across lifecycle |

### REL-004

DoS simulation mitigated; service responsive

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| dos-simulation-mitigated | DoS simulation mitigated; service responsive | Sustained responsiveness; error rate \u2264 1%; p95 latency within SLA during attack | Attack simulator + WAF/rate-limiter + metrics | Quarterly exercise | int,ref | crud-apis | draft | Validates resilience under volumetric attacks |

### REL-007

Brute force/auth anomalies rate limited & alerted (peak 500 TPS burst capacity; rate limits + alerts)

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| auth-brute-force-protection | Brute force/auth anomalies rate limited & alerted (peak 500 TPS legitimate burst supported) | Peak 500 TPS legitimate auth unaffected; anomalies blocked; alert ≤30s; ≤1% false positives | Auth gateway rate limiter + anomaly aggregator + performance harness + alerting | Continuous runtime enforcement + daily compliance script | dev,int,ref,prod | crud-apis | draft | Protects availability & integrity under authentication attack patterns |

### REL-011

Unhealthy node auto-replaced; workload continues

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| unhealthy-node-auto-replace | Unhealthy node auto-replaced; workload continues | Auto-replacement within policy; no user-visible downtime | Autoscaling group events + workload health | Continuous monitoring + quarterly drill | int,ref,prod | crud-apis | draft | Maintains reliability during node failures |

### REL-012

Single node removal shows stable performance & zero data loss

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| single-node-removal-safety | Single node removal shows stable performance & zero data loss | 0 data loss; p95 latency delta \u2264 10% during removal | Autoscaling events + workload health + integrity checks | Quarterly drill | int,ref | crud-apis | draft | Ensures resilience to node loss without user impact |

### REL-013

Tier failure graceful degradation & recovery evidenced

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| tier-failure-graceful-degrade | Tier failure graceful degradation & recovery evidenced | Documented fallback; recovery time within SLA | Chaos experiments + observability evidence | Quarterly | int,ref | crud-apis | draft | Demonstrates graceful degradation patterns |

### REL-014

External outage shows fallback & user messaging

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| external-outage-fallback | External outage shows fallback & user messaging | Documented fallback engaged; user messaging displayed; error rate \u2264 2%; recovery within SLA | Chaos experiments on external deps + observability evidence | Quarterly | int,ref | crud-apis | draft | Demonstrates graceful handling of external dependency outages |

### REL-015

LB failure retains sessions & continues routing

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| lb-failure-session-retention | LB failure retains sessions & continues routing | Zero session loss; traffic re-routed within 30s; p95 latency delta \u2264 10% | LB failover drill + session continuity tests + metrics | Semi-annual drill | int,ref | crud-apis | draft | Ensures resilience of routing tier |

### SCAL-001

Horizontal scale-out increases TPS linearly within tolerance

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| horizontal-scale-linear | Horizontal scale-out increases TPS linearly within tolerance | TPS increases ~linearly per replica within agreed tolerance | Load tests + autoscaling reports | Quarterly simulation | int,ref | crud-apis | draft | Validates scale-out effectiveness |

### SCAL-002

Vertical resize retains data & function without downtime

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| vertical-resize-no-downtime | Vertical resize retains data & function without downtime | Resize completes with zero downtime and no data loss | Resize runbook + health checks | Semi-annual exercise | int,ref | crud-apis | draft | Ensures safe vertical scaling |

### SCAL-003

All layers pass scalability checklist

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| scalability-checklist-complete | All layers pass scalability checklist | 100% checklist items complete; exceptions recorded with expiry | Checklist tracker + evidence links | Quarterly | int,ref | crud-apis | draft | Ensures scale readiness across tiers |

### SCAL-004

Scale-down events occur after sustained low utilisation

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| scale-down-sustained-low-util | Scale-down events occur after sustained low utilisation | No scale-down unless utilisation < 40% sustained for 30m; no flapping | Autoscaling metrics + policy | Continuous + monthly policy audit | prod | crud-apis | draft | Prevents scale instability |

### SCAL-005

Autoscaling policy simulation triggers controlled scale

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| autoscaling-policy-simulation | Autoscaling policy simulation triggers controlled scale | Policy simulates expected scale events; no flapping | Policy simulator + metrics | Quarterly | int,ref | crud-apis | draft | Confirms autoscaling tuning |

### SCAL-006

Scale event shows no SLA breach in latency/error

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| scale-event-sla | Scale event shows no SLA breach in latency/error | No breach in latency/error SLAs during scale | Metrics/alerts during scale events | Continuous monitoring + quarterly drill | int,ref,prod | crud-apis | draft | Protects user experience during scaling |

### SCAL-007

Capacity report shows ≥30% headroom

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| capacity-headroom | Capacity report shows ≥30% headroom | >= 30% capacity headroom maintained | Capacity planning reports | Monthly | prod | crud-apis | draft | Ensures buffer for demand spikes |

### SCAL-008

No manual scaling tickets for variance period

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| manual-scaling-eliminated | No manual scaling tickets for variance period | 0 manual scaling tickets in rolling 90 days | Ticketing system + scaling audit | Monthly review | prod | crud-apis | draft | Confirms autoscaling effectiveness |

### SCAL-009

Audit logs capture actor/reason for scaling

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| scaling-audit-context | Audit logs capture actor/reason for scaling | 100% scale events have actor, reason, correlation_id | Audit log pipeline + policy | Continuous + quarterly audit | prod | crud-apis | draft | Provides traceability of scaling decisions |

### SCAL-010

Predictive alert fires at utilisation forecast threshold

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| predictive-utilisation-alert | Predictive alert fires at utilisation forecast threshold | Forecasted utilisation > 80% in 15m triggers alert; MTT Alert < 2m | Forecasting job + alerting rules | Continuous + monthly tuning | prod | crud-apis | draft | Prevents SLA breach via early action |

### SEC-001

Crypto algorithms conform; weak ciphers rejected

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| crypto-cipher-policy | Crypto algorithms conform; weak ciphers rejected | TLS1.2+ only; no weak/legacy ciphers enabled | TLS scanner + configuration policy checks | CI per change + monthly scan | dev,int,ref,prod | crud-apis | draft | Enforces modern TLS standards; automated scans detect drift |

### SEC-002

WAF security pillar checklist completed & gaps tracked

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| waf-pillar-checklist | WAF security pillar checklist completed & gaps tracked | Checklist complete; 100% actions tracked; 0 open critical gaps | WAF checklist repository + issue tracker gate | Quarterly + on change | dev,int,ref,prod | crud-apis | draft | Formalizes WAF security governance; gaps tracked to closure |

### SEC-003

All endpoints TLS only; storage encryption enabled

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| tls-encryption-endpoints | All public/private API endpoints enforce TLS; storage services enable encryption at rest | 100% compliant across resources | AWS Config rules + Terraform policy checks | Continuous (real-time) with CI enforcement on change | dev,int,ref,prod | crud-apis | draft | Aligns with NHS policy; Config provides continuous guardrails; CI blocks drift |

### SEC-004

Storage services show encryption enabled

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| storage-encryption-enabled | Storage services show encryption enabled | 100% storage resources encrypted at rest | AWS Config rules + Terraform policy checks | Continuous + CI enforcement | dev,int,ref,prod | crud-apis | draft | Guardrails ensure encryption at rest across services |

### SEC-005

Cross-environment data access attempts denied

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| cross-env-access-denied | Cross-env data access attempts denied and logged | 100% denial; audit logs prove enforcement | IAM policies + SCP guardrails + audit log queries | CI policy checks + monthly audit review | dev,int,ref,prod | crud-apis | draft | Prevents accidental or malicious cross-environment data access |

### SEC-006

No direct prod console queries detected in audit period

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| prod-console-access-audit | No direct prod console queries detected in audit period | 0 non-approved console queries in audit period | CloudTrail + SIEM audit queries | Weekly audit + alerting | prod | crud-apis | draft | Detects improper direct access to production consoles |

### SEC-007

SG rules audited; attempt broad ingress denied

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| sg-broad-ingress-denied | SG rules audited; attempt broad ingress denied | 0 broad (0.0.0.0/0) ingress on restricted ports | AWS Config + IaC linter | CI per change + monthly audit | dev,int,ref,prod | crud-apis | draft | Prevents risky network exposure via security groups |

### SEC-008

Perimeter scan shows no broad whitelist & secure channels

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| perimeter-scan | Perimeter scan shows no broad whitelist & secure channels | No broad whitelists; only secure channels reported | External perimeter scanner + config validation | Monthly + on change | int,ref,prod | crud-apis | draft | Confirms perimeter hygiene and secure external exposure |

### SEC-009

ASVS & CIS benchmark automation reports pass thresholds

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| cis-benchmark-compliance | CIS benchmark automation reports meet pass thresholds for targeted services | >= 95% controls passing; all high-severity findings remediated or exceptioned | CIS benchmark tooling integrated in CI and periodic audits | CI per change + monthly full audit | dev,int,ref,prod | crud-apis | draft | Baseline hardening validated continuously; monthly cadence catches drift |

### SEC-010

Annual pen test executed; remediation tickets raised & closed

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| annual-pentest | Annual pen test executed; remediation tickets raised & closed | Pen test executed; all critical findings remediated or exceptioned | Pen test reports + remediation tracking | Annual | prod | crud-apis | draft | Validates security posture with external testing and tracked remediation |

### SEC-011

Security features enabled latency within SLA

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| security-features-latency-sla | Security features enabled latency within SLA | Added latency within agreed SLA per endpoint | Performance tests with security features enabled | CI perf checks + monthly regression review | int,ref,prod | crud-apis | draft | Ensures security does not breach performance SLAs |

### SEC-012

IAM policy review confirms least privilege for system roles

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| iam-least-privilege | IAM policy review confirms least privilege for system roles | >= 95% policies compliant; no wildcard resource; explicit actions only | IAM Access Analyzer + policy linters | CI per change + quarterly audit | dev,int,ref,prod | crud-apis | draft | Continuous analysis prevents privilege creep; periodic review catches drift |

### SEC-013

Key rotation events logged; unauthorized access denied

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| key-rotation-logging | Key rotation events logged; unauthorized access denied | 100% rotation events logged; 0 unauthorized key access | KMS/AWS logs + SIEM correlation | Quarterly audit + CI checks on policy | dev,int,ref,prod | crud-apis | draft | Audit trail confirms rotation compliance and denial of unauthorized access |

### SEC-014

mTLS handshake succeeds between designated services

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| mtls-service-handshake | mTLS handshake succeeds between designated services using ITOC-approved CA signed leaf + intermediate certs (chain to ITOC root); invalid/expired/revoked/untrusted-issuer/weak-cipher attempts rejected | 100% handshake success for valid ITOC chain; 0 successful handshakes with expired, revoked, weak cipher, or non-ITOC issuer certs; rotation introduces 0 downtime | Integration tests (valid/expired/revoked/wrong-CA/weak-cipher) + gateway cert management + OCSP/CRL polling | CI per build + cert rotation checks + revocation poll ≤5m | int,ref,prod | crud-apis | draft | Enforces trusted ITOC certificate chain, strong ciphers, timely revocation, and zero-downtime rotation for secure service-to-service trust |

### SEC-015

Expiry alert fired in advance; renewal executed seamlessly

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| cert-expiry-alert-renewal | Expiry alert fired in advance; renewal executed seamlessly | >= 30 days prior alert; 0 outage during renewal | Cert manager alerts + renewal runbooks | Continuous monitoring | int,ref,prod | crud-apis | draft | Proactive renewal prevents downtime; alerts ensure timely action |

### SEC-016

MFA enforced for all privileged infra roles

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| privileged-mfa-enforced | MFA enforced for all privileged infra roles | 100% privileged roles require MFA | IAM policy checks + directory audit | CI policy checks + quarterly audit | dev,int,ref,prod | crud-apis | draft | Strong authentication for privileged accounts reduces risk |

### SEC-017

Scan reports zero unmanaged long-lived credentials

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| zero-long-lived-credentials | Scan reports zero unmanaged long-lived credentials | 0 unmanaged long-lived credentials | Secret scanners + IAM credential report audit | CI per build + weekly audit | dev,int,ref,prod | crud-apis | draft | Reduces risk from forgotten credentials; continuous scanning plus scheduled audits |

### SEC-018

Supplier audit attestation stored & verified

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| supplier-audit-attestation | Supplier audit attestation stored & verified | Attestations current; verification completed | Supplier management system + evidence repository | Annual + on contract change | prod | crud-apis | draft | Ensures supplier compliance and auditable records |

### SEC-019

Segmentation test confirms tenant isolation

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| segmentation-tenant-isolation | Segmentation test confirms tenant isolation | 100% isolation; no cross-tenant data access observed | Segmentation test suite + log verification | Quarterly | int,ref,prod | crud-apis | draft | Ensures strict isolation between tenants per policy |

### SEC-021

Port scan matches approved diagnostic list only

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| port-scan-diagnostic-only | Port scan matches approved diagnostic list only | No unexpected open ports detected outside approved list | Automated port scan + baseline comparison | Monthly + CI smoke on infra changes | dev,int,ref,prod | crud-apis | draft | Detects misconfigurations; verifies adherence to diagnostic port policy |

### SEC-022

Utility program access restricted to approved roles

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| utility-access-restricted | Utility program access restricted to approved roles | Only approved roles can access utility programs | RBAC policy checks + audit logs | CI policy checks + monthly audit | dev,int,ref,prod | crud-apis | draft | Prevents misuse of diagnostic utilities |

### SEC-023

Deployment provenance shows unique traceable accounts

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| deployment-provenance-traceable | Deployment provenance shows unique traceable accounts | All deployments traceable to unique accounts | CI/CD audit trails + commit signing | Continuous | dev,int,ref,prod | crud-apis | draft | Ensures accountability and traceability for all deployments |

### SEC-024

Code/data transfer logs show integrity & secure channels

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| transfer-integrity-secure | Code/data transfer logs show integrity & secure channels | 100% transfers logged; integrity and secure channel verified | Checksums/signatures + TLS enforcement + audit logs | CI per change + weekly reviews | dev,int,ref,prod | crud-apis | draft | Validates integrity and secure transport for all transfers |

### SEC-025

PID requests enforce mTLS; plain text blocked

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| pid-mtls-enforcement | Requests carrying PID fields require mutual TLS; plaintext requests blocked | 100% enforcement on designated endpoints | API gateway/WAF policy + integration tests | CI policy validation + continuous enforcement | int,ref,prod | crud-apis | draft | Ensures transport security for sensitive data; test coverage verifies enforcement |

### SEC-026

API responses contain no unencrypted PID fields

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| pid-no-plaintext-response | API responses contain no unencrypted PID fields | 0 occurrences of unencrypted PID in responses | Integration tests + response scanners | CI per build + periodic production sampling | int,ref,prod | crud-apis | draft | Ensures sensitive data is never returned unencrypted |

### SEC-027

Build fails on high CVE; report archived

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| high-cve-block | Build fails when high/critical CVEs detected in application or container dependencies | 0 unresolved High/Critical CVEs at release time | SCA scanner (e.g., OWASP Dependency-Check), container scanner, pipeline gate | CI per build + scheduled weekly scans | dev,int,ref | crud-apis | draft | Prevents introduction of known vulnerabilities; gate aligned to release quality |

### SEC-028

Release pipeline blocks on critical unresolved findings

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| release-block-critical-findings | Release pipeline blocks on critical unresolved findings | 0 critical unresolved findings prior to release | Pipeline gate integrated with SCA, container, IaC scanners | Per release | dev,int,ref | crud-apis | draft | Enforces remediation before release; gate consolidates multiple scanner outputs |

### SEC-029

All API endpoints enforce CIS2 JWT authentication (signature, issuer, audience, assurance claims)

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| cis2-jwt-auth-enforced | All API endpoints enforce CIS2 JWT authentication (signature, issuer, audience, assurance claims) | 100% endpoints require valid CIS2 JWT; invalid/missing tokens rejected with structured 401 | OIDC integration tests + JWT validator + JWKS cache monitor | CI per build + continuous runtime enforcement | dev,int,ref,prod | crud-apis | draft | Ensures uniform strong authentication; claim + signature validation prevents unauthorized access |

### SEC-030

Certificates and private keys stored only in approved encrypted secret stores; zero plain text exposure

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| cert-secure-storage | Certificate and private key material stored only in approved encrypted secret stores (KMS/Secrets Manager); zero plaintext in repos, images, build logs, or artifacts | 0 plaintext occurrences; 100% issuance & rotation actions use managed secrets; 100% scan coverage of git history and container layers | Secret scanning (git history + container layers), CI policy checks, artifact scanner, repo pre-commit hooks | CI per build + weekly full history & image layer scan | dev,int,ref,prod | crud-apis | draft | Prevents certificate/private key exposure by enforcing exclusive use of encrypted secret storage and continuous scanning |
