# FtRS NFR – Service: dos-search

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Availability | AVAIL-001 | Availability report shows ≥99.90% multi-AZ uptime | Multi-AZ deployment achieves target uptime (e.g., ≥99.90%). | STORY-AVAIL-001 |
| Availability | AVAIL-002 | Region DR simulation meets plan objectives | Disaster recovery (DR) simulation meets documented objectives. | STORY-AVAIL-002 |
| Availability | AVAIL-003 | Uptime monitoring confirms 24x7 coverage | Continuous uptime monitoring covers 24x7 operations. | STORY-AVAIL-003 |
| Availability | AVAIL-004 | Monthly maintenance minutes ≤150; single ≤60 | Maintenance windows stay within monthly and per-event minute limits. | STORY-AVAIL-004 |
| Availability | AVAIL-005 | Tuesday window executed; smoke tests pass | Scheduled maintenance executes successfully with passing smoke tests afterward. | STORY-AVAIL-006 |
| Availability | AVAIL-006 | DR exercise restores service <2h | DR exercise restores service within target recovery time (< defined hours). | STORY-AVAIL-007 |
| Availability | AVAIL-007 | Replication lag ≤60s; fail-over data delta minimal | Data replication lag remains under target ensuring minimal failover delta. | STORY-AVAIL-008 |
| Availability | AVAIL-008 | API uptime aligns with core service | API uptime aligns with overall service availability target. | STORY-AVAIL-009 |
| Availability | AVAIL-009 | Non-UK access attempts blocked & logged | Access from non-approved geographic regions is blocked and logged. | STORY-AVAIL-010 |
| Availability | AVAIL-010 | Blue/green deployment produces 0 failed requests | Blue/green deployments complete with zero failed user requests. | STORY-AVAIL-005, STORY-AVAIL-011 |
| Cost | COST-001 | Mandatory tagging set present on 100% resources | All resources have mandatory cost tags for allocation and reporting. | STORY-COST-001 |
| Cost | COST-002 | Monthly Cost Explorer review & anomaly log | Monthly cost review identifies anomalies and tracks actions. | STORY-COST-002 |
| Cost | COST-003 | CloudHealth access for each team infra engineer | Each team infra engineer has access to cost analysis tooling (e.g., CloudHealth). | STORY-COST-003 |
| Cost | COST-004 | CloudHealth optimisation & tag compliance reports | Optimisation and tag compliance reports are produced and reviewed. | STORY-COST-004 |
| Cost | COST-005 | Budgets & alert notifications configured & tested | Budgets and cost alert notifications are configured and tested. | STORY-COST-005 |
| Cost | COST-006 | #ftrs-cost-alerts channel created & receiving test alerts | Dedicated cost alerts channel receives test and live notifications. | STORY-COST-006 |
| Cost | COST-007 | Quarterly cost review minutes & tracked actions | Quarterly cost reviews record minutes and follow-up actions. | STORY-COST-007 |
| Governance | GOV-001 | Service Management pre-live acceptance signed | Service Management pre-live acceptance is signed off before go-live. | STORY-GOV-001 |
| Governance | GOV-002 | Well-Architected review completed & actions closed | Well-Architected review completed; remediation actions closed. | STORY-GOV-002 |
| Governance | GOV-003 | Solution Architecture Framework assessment approved | Solution Architecture Framework assessment is approved. | STORY-GOV-003 |
| Governance | GOV-004 | Engineering Red-lines compliance checklist signed | Engineering red-lines compliance checklist is signed. | STORY-GOV-004 |
| Governance | GOV-005 | GDPR compliance assessment signed by IG | GDPR compliance assessment signed by Information Governance. | STORY-GOV-005 |
| Governance | GOV-006 | Medical Device out-of-scope statement recorded | Statement confirming service is out of scope for Medical Device regulation. | STORY-GOV-006 |
| Governance | GOV-007 | FtRS Architects review & approval logged | Architecture review and approval logged by FtRS architects. | STORY-GOV-007 |
| Governance | GOV-008 | Cloud Expert deployment approval documented | Cloud expert deployment approval documented (infrastructure readiness). | STORY-GOV-008 |
| Governance | GOV-009 | Solution Assurance approval ticket closed | Solution Assurance approval ticket is closed. | STORY-GOV-003, STORY-GOV-009 |
| Governance | GOV-010 | Clinical Safety assurance approval recorded | Clinical Safety assurance approval recorded. | STORY-GOV-004, STORY-GOV-010 |
| Governance | GOV-011 | Information Governance approval recorded | Information Governance approval recorded. | STORY-GOV-011 |
| Governance | GOV-012 | TRG approval session outcome logged | Technical Review Group (TRG) approval outcome documented. | STORY-GOV-012 |
| Governance | GOV-013 | SIRO sign-off obtained | Senior Information Risk Owner (SIRO) sign-off obtained. | STORY-GOV-013 |
| Governance | GOV-014 | Caldicott Principles Guardian approval recorded | Caldicott Guardian approval recorded for data handling. | STORY-GOV-014 |
| Governance | GOV-015 | DUEC Assurance Board acceptance logged | DUEC Assurance Board acceptance logged. | STORY-GOV-015 |
| Governance | GOV-016 | Live Services Board go-live approval recorded | Live Services Board go-live approval recorded. | STORY-GOV-016 |
| Interoperability | INT-001 | Resources validated against UK Core profiles | Resources conform to UK Core profiles ensuring national standard alignment. | STORY-INT-018 |
| Interoperability | INT-002 | Versioning & deprecation policy published | Versioning and deprecation policy is published for integrators. | STORY-INT-019 |
| Interoperability | INT-003 | Minor releases backward compatible for 12 months | Minor releases remain backward compatible for the defined support window. | STORY-INT-020 |
| Interoperability | INT-004 | Semantic mapping round-trip fidelity preserved | Semantic mappings preserve meaning when round-tripped between formats. | STORY-INT-004 |
| Interoperability | INT-005 | Standard OperationOutcome error structure enforced | Error responses follow standard OperationOutcome structure. | STORY-INT-001 |
| Interoperability | INT-006 | Identifier normalization applied (uppercase, trimmed) | Identifiers are normalised (case, trimming) for consistent matching. | STORY-INT-021 |
| Interoperability | INT-007 | Strict content negotiation implemented | Strict content negotiation enforces supported media types only. | STORY-INT-002 |
| Interoperability | INT-009 | Only documented FHIR search params accepted | Only documented FHIR search parameters are accepted; unknown ones rejected. | STORY-INT-022 |
| Interoperability | INT-010 | Version-controlled integration contract published | Integration contract is version-controlled and published. | STORY-INT-023 |
| Interoperability | INT-011 | Machine-readable changelog generated | Machine-readable changelog is generated for each release. | STORY-INT-024 |
| Interoperability | INT-012 | Terminology bindings validated | Terminology bindings are validated to ensure correct coding. | STORY-INT-005, STORY-INT-025 |
| Interoperability | INT-013 | Correlation IDs preserved across calls | Correlation IDs persist across internal and external calls for tracing. | STORY-INT-004, STORY-OBS-019 |
| Interoperability | INT-014 | Null vs absent data handled per FHIR | Null vs absent data semantics follow FHIR specification rules. | STORY-INT-026 |
| Interoperability | INT-015 | ≥90% interoperability scenario coverage | Test coverage spans ≥90% of defined interoperability scenarios. | STORY-INT-027 |
| Interoperability | INT-016 | Stateless sequence-independent operations | Operations are stateless and do not rely on sequence order. | STORY-INT-028 |
| Interoperability | INT-018 | Comprehensive published OpenAPI documentation (overview, audience, related APIs, roadmap, SLA, tech stack, network access, security/auth, test environment, onboarding, endpoints with examples) | Comprehensive OpenAPI documentation is published (overview, audience, related APIs, roadmap, SLA, tech stack, security/auth, test environment, onboarding, endpoints with examples) to support integrator adoption. | STORY-INT-006, STORY-INT-029 |
| Observability | OBS-001 | App & infra health panels show green | Application and infrastructure health panels display green status during normal operation. | STORY-OBS-001 |
| Observability | OBS-002 | Authenticated remote health dashboard accessible | Authenticated remote health dashboard is accessible to support teams. | STORY-OBS-026 |
| Observability | OBS-003 | Health event visible ≤60s after failure | Health events appear on dashboards shortly after failures (within target freshness). | STORY-OBS-027 |
| Observability | OBS-004 | Automated maintenance tasks executed; zero manual interventions | Automated maintenance tasks run successfully with no manual intervention required. | STORY-OBS-028 |
| Observability | OBS-005 | Performance metrics per layer present | Layered performance metrics (app, DB, cache) are visible. | STORY-OBS-029 |
| Observability | OBS-006 | Remote performance dashboard matches local view | Remote performance dashboard mirrors local environment metrics accurately. | STORY-OBS-030 |
| Observability | OBS-007 | Performance metrics latency ≤60s | Performance metrics latency (ingest to display) stays within defined limit (e.g., ≤60s). | STORY-OBS-002 |
| Observability | OBS-008 | TPS per endpoint displayed & threshold alert configured | Per-endpoint transactions per second (TPS) are displayed with alert thresholds. | STORY-OBS-003 |
| Observability | OBS-009 | Endpoint latency histograms with p50/p95/p99 | Latency histograms show p50/p95/p99 for each endpoint. | STORY-OBS-004 |
| Observability | OBS-010 | Aggregate latency panel accurate within 2% roll-up | Aggregate latency panel roll-ups remain within acceptable accuracy margin (e.g., ≤2%). | STORY-OBS-031 |
| Observability | OBS-011 | Failure types logged & classified in dashboard | Failure types are logged and classified for reporting. | STORY-OBS-032 |
| Observability | OBS-012 | Error percentage metric & alert configured | Error rate metric and alert exist to highlight reliability issues. | STORY-OBS-033 |
| Observability | OBS-013 | Infra log query returns expected fields | Infrastructure logs return expected structured fields for queries. | STORY-OBS-034 |
| Observability | OBS-014 | Infra log entries include required fields | Infrastructure log entries include required contextual fields (e.g., IDs, timestamps). | STORY-OBS-014 |
| Observability | OBS-015 | Retention policy enforced & reported | Log retention policy is enforced and reported. | STORY-OBS-035 |
| Observability | OBS-016 | SIEM forwarding delivers test event <60s | Security/event forwarding to SIEM delivers test events within freshness target. | STORY-OBS-036 |
| Observability | OBS-017 | All log levels supported; dynamic change works | All log levels are supported and can be changed dynamically. | STORY-OBS-037 |
| Observability | OBS-018 | Log level propagation <2min with alert on breach | Log level changes propagate quickly (under defined minutes) with alert if breach. | STORY-OBS-038 |
| Observability | OBS-019 | Operational log shows full transaction chain | Operational logs allow full transaction chain reconstruction. | STORY-OBS-014, STORY-OBS-019 |
| Observability | OBS-020 | Operations logs reconstruct workflow | Operations logs reconstruct workflow sequences accurately. | STORY-OBS-039 |
| Observability | OBS-021 | Operational events include transaction_id | Operational events include a transaction identifier for correlation. | STORY-OBS-040 |
| Observability | OBS-022 | Audit trail reconstructs user action | Audit trail can reconstruct a specific user action sequence. | STORY-OBS-041 |
| Observability | OBS-023 | Audit events share transaction_id & ordered timestamps | Audit events share transaction IDs and ordered timestamps for traceability. | STORY-OBS-042 |
| Observability | OBS-024 | Alert rule triggers multi-channel notification | Alert rules trigger multi-channel notifications (e.g., chat + email). | STORY-OBS-043 |
| Observability | OBS-026 | Analytics query identifies usage pattern | Analytics queries identify usage patterns from captured metrics. | STORY-OBS-044 |
| Observability | OBS-027 | Analytics outage non-impacting to transactions | Analytics outages do not impact core transaction processing. | STORY-OBS-045 |
| Observability | OBS-028 | RBAC restricts dashboard sections | Role-based access control (RBAC) restricts dashboard sections appropriately. | STORY-OBS-046 |
| Observability | OBS-029 | Dashboard freshness age ≤60s | Dashboard freshness age remains under target (e.g., ≤60s). | STORY-OBS-047 |
| Observability | OBS-030 | Distributed trace spans cover end-to-end request | Distributed tracing spans cover end-to-end request path. | STORY-OBS-005 |
| Observability | OBS-031 | Anonymised behaviour metrics collected without identifiers | Anonymised behavioural metrics are collected without exposing personal identifiers. | STORY-OBS-048 |
| Observability | OBS-032 | Per-endpoint 4xx/5xx response metrics & alert thresholds configured | Per-endpoint 4xx and 5xx response metrics are captured with alert thresholds so error rate spikes are detected and acted upon quickly. | [FTRS-1573](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1573) |
| Observability | OBS-033 | Unauthorized API access attempts logged, classified, alerted | Unauthorized API access attempts (failed authentication, forbidden operations, rate limit breaches, anomalous spikes) are logged with required context and generate timely alerts for early detection of credential misuse or attack patterns. | [FTRS-1607](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1607) |
| Performance | PERF-001 | Each operation meets registry-defined percentile targets (p50/p95) logged & asserted (see performance/expectations.yaml) | Each API or batch operation meets agreed median and 95th percentile latency targets. | STORY-PERF-001, STORY-PERF-002, STORY-PERF-003, STORY-PERF-004, STORY-PERF-005, STORY-PERF-006, STORY-PERF-007, STORY-PERF-008, STORY-PERF-009, STORY-PERF-010, STORY-SCAL-001 |
| Performance | PERF-002 | Performance pillar checklist completed & actions closed | Performance pillar checklist is completed and any actions are closed. | STORY-PERF-011 |
| Performance | PERF-003 | Performance expectations table versioned & referenced | The versioned performance expectations table is maintained and referenced by tests. | STORY-PERF-012 |
| Performance | PERF-004 | Anonymised live-like dataset present & audited | A representative, anonymised dataset exists for realistic performance validation. | STORY-PERF-013 |
| Performance | PERF-005 | Automated test suite matches defined actions & exclusions | Automated performance tests implement all defined actions and listed exclusions. | STORY-PERF-014 |
| Performance | PERF-007 | Telemetry overhead within CPU & latency thresholds | Telemetry overhead (CPU, latency) remains within acceptable limits while capturing required data. | STORY-PERF-016 |
| Performance | PERF-008 | 8h rolling window p95 variance ≤10% | Rolling window performance variance remains stable within target percentage bounds. | STORY-PERF-017 |
| Performance | PERF-009 | Regression alert triggers on >10% p95 increase | Alerting triggers when p95 latency regresses beyond the defined threshold (e.g., >10%). | STORY-PERF-018 |
| Performance | PERF-010 | Percentile methodology document & tool configuration aligned | Documented percentile methodology matches tool configuration (consistent measurement). | STORY-PERF-019 |
| Performance | PERF-011 | dos-search endpoints sustain burst ≥150 TPS (registry burst_tps_target) | GP search endpoints handle short burst throughput at or above the target TPS. | (placeholder) |
| Performance | PERF-012 | dos-search endpoints sustain steady ≥150 TPS (registry sustained_tps_target) | GP search endpoints sustain steady-state throughput at or above the TPS target. | (placeholder) |
| Performance | PERF-013 | Request payload size per endpoint ≤1MB (max_request_payload_bytes) | Endpoint request payloads remain under the maximum defined size to protect performance. | (placeholder) |
| Reliability | REL-001 | Health checks, multi-AZ deployment documented | Service remains healthy across multiple availability zones with verified health checks. | STORY-REL-017 |
| Reliability | REL-002 | AZ failure simulation maintains service | Simulated AZ failure does not interrupt service delivery. | STORY-REL-001 |
| Reliability | REL-003 | Lifecycle reliability checklist completed | Lifecycle reliability checklist is completed for the service components. | STORY-REL-018 |
| Reliability | REL-004 | DoS simulation mitigated; service responsive | Denial-of-service (DoS) simulation shows successful mitigation and continued responsiveness. | STORY-REL-019 |
| Reliability | REL-005 | Injection attempt blocked; no code execution | Injection attacks are blocked, preventing arbitrary code execution attempts. | STORY-REL-020 |
| Reliability | REL-006 | Placement scan shows no forbidden co-residency | Resource placement scan shows no forbidden co-residency (e.g., sensitive + public workloads). | STORY-REL-021 |
| Reliability | REL-007 | Brute force/auth anomalies rate limited & alerted (peak 500 TPS burst capacity; rate limits + alerts) | Brute force or auth anomaly attempts are rate limited and create alerts. | STORY-REL-005 |
| Reliability | REL-008 | MITM attempt fails; pinned cert validation passes | Man-in-the-middle (MITM) attempts fail due to secure certificate pinning. | STORY-REL-022 |
| Reliability | REL-011 | Unhealthy node auto-replaced; workload continues | Unhealthy nodes are automatically replaced with workload continuity. | STORY-REL-003 |
| Reliability | REL-012 | Single node removal shows stable performance & zero data loss | Removing a single node yields no data loss and minimal performance impact. | STORY-REL-024 |
| Reliability | REL-013 | Tier failure graceful degradation & recovery evidenced | Tier failure triggers graceful degradation and later clean recovery. | STORY-REL-004 |
| Reliability | REL-014 | External outage shows fallback & user messaging | External dependency outage invokes fallback and clear user messaging. | STORY-REL-025 |
| Reliability | REL-015 | LB failure retains sessions & continues routing | Load balancer failure preserves sessions and maintains routing continuity. | STORY-REL-026 |
| Reliability | REL-017 | Restore drill meets RPO/RTO & ransomware defenses | Restore drills meet RPO/RTO targets and confirm ransomware defenses. | STORY-REL-027 |
| Scalability | SCAL-001 | Horizontal scale-out increases TPS linearly within tolerance | Horizontal scaling increases throughput nearly linearly without quality loss. | STORY-SCAL-001 |
| Scalability | SCAL-002 | Vertical resize retains data & function without downtime | Vertical resizing (bigger instance) retains data and operation with no downtime. | STORY-SCAL-002 |
| Scalability | SCAL-003 | All layers pass scalability checklist | All layers (app, DB, cache) meet defined scalability checklist items. | STORY-SCAL-006 |
| Scalability | SCAL-004 | Scale-down events occur after sustained low utilisation | Scale-down only occurs after sustained low utilisation (not transient dips). | STORY-SCAL-007 |
| Scalability | SCAL-005 | Autoscaling policy simulation triggers controlled scale | Autoscaling policy simulations trigger controlled scaling actions. | STORY-SCAL-003 |
| Scalability | SCAL-006 | Scale event shows no SLA breach in latency/error | Scaling events do not cause SLA breaches in latency or error rate. | STORY-SCAL-004 |
| Scalability | SCAL-007 | Capacity report shows ≥30% headroom | Capacity planning shows adequate headroom (e.g., ≥30%). | STORY-SCAL-005 |
| Scalability | SCAL-008 | No manual scaling tickets for variance period | During the variance period no manual scaling tickets are needed. | STORY-SCAL-008 |
| Scalability | SCAL-009 | Audit logs capture actor/reason for scaling | Audit logs record who initiated scaling and why. | STORY-SCAL-009 |
| Scalability | SCAL-010 | Predictive alert fires at utilisation forecast threshold | Predictive alerts fire before utilisation reaches critical thresholds. | STORY-SCAL-010 |
| Security | SEC-001 | Crypto algorithms conform; weak ciphers rejected | Use only strong, approved cryptographic algorithms; weak or deprecated ciphers are blocked. | STORY-SEC-013 |
| Security | SEC-002 | WAF security pillar checklist completed & gaps tracked | Complete the AWS/WAF security pillar checklist and track remediation actions for any gaps. | STORY-SEC-014, STORY-SEC-031 |
| Security | SEC-003 | All endpoints TLS only; storage encryption enabled | All service endpoints enforce TLS and all stored data (databases, buckets) is encrypted at rest. | [FTRS-1563](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1563) |
| Security | SEC-004 | Storage services show encryption enabled | Every storage service (S3, RDS, etc.) shows encryption enabled with managed or customer keys. | STORY-SEC-004, STORY-SEC-015, STORY-SEC-032 |
| Security | SEC-005 | Cross-environment data access attempts denied | Strict environment isolation: data access from one environment to another is prevented. | STORY-SEC-011, STORY-SEC-033 |
| Security | SEC-006 | No direct prod console queries detected in audit period | No direct production console queries by engineers outside approved, audited break-glass processes. | STORY-SEC-016, STORY-SEC-034 |
| Security | SEC-007 | SG rules audited; attempt broad ingress denied | Network security groups allow only narrowly scoped inbound rules; broad ingress is denied. | STORY-SEC-017 |
| Security | SEC-008 | Perimeter scan shows no broad whitelist & secure channels | Perimeter scans show secure transport, no open broad whitelists, and hardened edge configuration. | STORY-SEC-018, STORY-SEC-035 |
| Security | SEC-009 | ASVS & CIS benchmark automation reports pass thresholds | Automated ASVS and CIS benchmark scans meet pass thresholds; failures trigger remediation. | STORY-SEC-004, STORY-SEC-036 |
| Security | SEC-010 | Annual pen test executed; remediation tickets raised & closed | Annual penetration test completed; identified issues tracked and closed. | STORY-SEC-019, STORY-SEC-037 |
| Security | SEC-011 | Security features enabled latency within SLA | Enabling security controls does not push latency beyond defined SLAs. | STORY-SEC-020, STORY-SEC-038 |
| Security | SEC-012 | IAM policy review confirms least privilege for system roles | IAM roles and policies grant least privilege; periodic reviews confirm minimal access. | STORY-SEC-005, STORY-SEC-030, STORY-SEC-039 |
| Security | SEC-013 | Key rotation events logged; unauthorized access denied | Cryptographic keys rotate on schedule and unauthorized access attempts are rejected and logged. | STORY-SEC-021, STORY-SEC-040 |
| Security | SEC-014 | mTLS handshake succeeds between designated services | Mutual TLS (mTLS) succeeds between designated internal services to protect sensitive flows. | STORY-SEC-006 |
| Security | SEC-015 | Expiry alert fired in advance; renewal executed seamlessly | Certificate expiry is detected in advance; renewal occurs without downtime. | STORY-SEC-022 |
| Security | SEC-016 | MFA enforced for all privileged infra roles | Privileged infrastructure roles require multi-factor authentication (MFA). | STORY-SEC-023 |
| Security | SEC-017 | Scan reports zero unmanaged long-lived credentials | No long-lived unmanaged credentials; periodic scans confirm only managed secrets exist. | STORY-SEC-010, STORY-SEC-041 |
| Security | SEC-018 | Supplier audit attestation stored & verified | Third-party supplier security attestation is collected and stored for audit. | STORY-SEC-024, STORY-SEC-042 |
| Security | SEC-019 | Segmentation test confirms tenant isolation | Tenant or data segmentation tests confirm isolation boundaries hold. | STORY-SEC-012, STORY-SEC-043 |
| Security | SEC-021 | Port scan matches approved diagnostic list only | Port scans reveal only approved diagnostic and service ports—no unexpected exposures. | STORY-SEC-008, STORY-SEC-045 |
| Security | SEC-022 | Utility program access restricted to approved roles | Access to powerful utility programs is restricted to approved roles. | STORY-SEC-025, STORY-SEC-046 |
| Security | SEC-023 | Deployment provenance shows unique traceable accounts | Deployment provenance shows traceable unique accounts per automated pipeline stage. | STORY-SEC-026, STORY-SEC-047 |
| Security | SEC-024 | Code/data transfer logs show integrity & secure channels | Transfer of code or data maintains integrity and uses secure channels; events are logged. | STORY-SEC-027, STORY-SEC-048 |
| Security | SEC-025 | PID requests enforce mTLS; plain text blocked | Requests containing identifiable patient data enforce mTLS; plaintext attempts are blocked. | STORY-SEC-003 |
| Security | SEC-026 | API responses contain no unencrypted PID fields | API responses never include unencrypted patient identifiable data (PID) fields. | STORY-SEC-028, STORY-SEC-049 |
| Security | SEC-027 | Build fails on high CVE; report archived | Build pipeline blocks release when critical CVEs exceed threshold; reports archived. | STORY-SEC-002 |
| Security | SEC-028 | Release pipeline blocks on critical unresolved findings | Releases are halted if critical unresolved security findings remain. | STORY-SEC-009, STORY-SEC-050 |
| Security | SEC-029 | All API endpoints enforce CIS2 JWT authentication (signature, issuer, audience, assurance claims) | All API endpoints enforce CIS2 JWT authentication with signature, issuer, audience and required assurance claim validation; invalid or missing tokens are rejected with structured errors. | [FTRS-1593](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1593) |
| Security | SEC-030 | Certificates and private keys stored only in approved encrypted secret stores; zero plain text exposure | Certificates and private keys are stored only in approved encrypted secret stores (e.g., Secrets Manager/KMS) with zero plaintext exposure across repositories, images, logs, or build artifacts; continuous scanning enforces compliance. | STORY-SEC-030 |

## Operations

### PERF-001

| Requirement | Operation ID | p50 ms | p95 ms | Max ms | Burst TPS | Sustained TPS | Max Payload (bytes) | Status | Rationale |
|-------------|--------------|--------|--------|--------|-----------|---------------|---------------------|--------|-----------|
| [PERF-001](#perf-001) | dos-lookup-ods | 150 | 300 | 500 | 150 | 150 | 1048576 | draft | Direct ODS code lookup; largely cacheable |
| [PERF-001](#perf-001) | dos-nearby | 150 | 300 | 500 | 150 | 150 | 1048576 | draft | Geo filtering + limited enrichment |
| [PERF-001](#perf-001) | dos-search | 150 | 300 | 500 | 150 | 150 | 1048576 | draft | Primary user-facing query; critical perceived responsiveness |

## Controls

### AVAIL-001

Availability report shows ≥99.90% multi-AZ uptime

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [AVAIL-001](#avail-001) | multi-az-uptime-report | Availability report shows ≥99.90% multi-AZ uptime | >= 99.90% monthly uptime across multi-AZ deployment | Uptime monitoring + monthly report automation | Monthly | prod | dos-search | draft | Tracks SLA against multi-AZ deployment goals |

### AVAIL-002

Region DR simulation meets plan objectives

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [AVAIL-002](#avail-002) | region-dr-simulation | Region DR simulation meets plan objectives | DR exercise meets RTO/RPO targets and user impact objectives | DR runbooks + simulation exercises | Semi-annual | int,ref | dos-search | draft | Validates disaster recovery readiness across regions |

### AVAIL-003

Uptime monitoring confirms 24x7 coverage

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [AVAIL-003](#avail-003) | uptime-monitoring-coverage | Uptime monitoring confirms 24x7 coverage | 24x7 coverage; alerts configured for service degradation | Uptime monitors + alerting system | Continuous monitoring | prod | dos-search | draft | Ensures continuous availability monitoring |

### AVAIL-004

Monthly maintenance minutes ≤150; single ≤60

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [AVAIL-004](#avail-004) | maintenance-window-minutes | Monthly maintenance minutes ≤150; single ≤60 | Monthly total ≤150 minutes; single window ≤60 minutes | Maintenance logs + reporting | Monthly | prod | dos-search | draft | Controls maintenance impact to meet availability objectives |

### AVAIL-005

Tuesday window executed; smoke tests pass

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [AVAIL-005](#avail-005) | scheduled-maintenance-smoke-tests | Tuesday window executed; smoke tests pass | Maintenance completes; post-window smoke tests 100% pass; no Sev-1/2 incidents | Deployment controller + smoke test suite + incident log | Weekly maintenance window | prod | dos-search | draft | Ensures safe scheduled maintenance without user impact |

### AVAIL-006

DR exercise restores service <2h

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [AVAIL-006](#avail-006) | dr-exercise-rto | DR exercise restores service <2h | End-to-end restore < 120 minutes; data loss = 0 per RPO | DR runbook + timer + integrity checks | Semi-annual exercise | int,ref | dos-search | draft | Validates recovery objectives and data integrity |

### AVAIL-007

Replication lag ≤60s; fail-over data delta minimal

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [AVAIL-007](#avail-007) | replication-lag-threshold | Replication lag \u226460s; fail-over data delta minimal | Replication lag \u2264 60s for primary datasets; failover delta \u2264 1% records | Replication metrics + failover audit | Continuous + monthly report | prod | dos-search | draft | Ensures rapid failover with minimal inconsistency |

### AVAIL-008

API uptime aligns with core service

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [AVAIL-008](#avail-008) | api-uptime-sla | API uptime aligns with core service | API uptime \u2265 99.90% monthly; maintenance excluded per policy | Uptime monitors + SLA calculator | Monthly | prod | dos-search | draft | Aligns API availability to overall SLA |

### AVAIL-009

Non-UK access attempts blocked & logged

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [AVAIL-009](#avail-009) | geo-blocking-enforced | Non-UK access attempts blocked & logged | 100% non-UK requests blocked at edge; structured log with country + ip | WAF geo rules + edge logs | Continuous + weekly audit | prod | dos-search | draft | Reduces risk from out-of-region access |

### AVAIL-010

Blue/green deployment produces 0 failed requests

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [AVAIL-010](#avail-010) | blue-green-zero-failures | Blue/green deployment produces 0 failed requests | 0 failed requests during blue/green switch | Deployment controller + canary telemetry | Per deployment | int,ref,prod | dos-search | draft | Ensures safe deployments without user impact |

### COST-001

Mandatory tagging set present on 100% resources

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [COST-001](#cost-001) | mandatory-tagging | Mandatory tagging set present on 100% resources | 100% resources carry mandatory tags | AWS Config rules + tag audit automation | Continuous + monthly report | dev,int,ref,prod | dos-search | draft | Enables cost visibility and accountability |

### COST-002

Monthly Cost Explorer review & anomaly log

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [COST-002](#cost-002) | monthly-cost-review | Monthly Cost Explorer review & anomaly log | Review completed; anomalies logged with actions | Cost Explorer + anomaly detection | Monthly | prod | dos-search | draft | Ensures proactive cost management |

### COST-003

CloudHealth access for each team infra engineer

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [COST-003](#cost-003) | cloudhealth-access | CloudHealth access for each team infra engineer | Access provisioned; onboarding verified | CloudHealth admin + access logs | Quarterly verification | prod | dos-search | draft | Ensures teams can act on cost insights |

### COST-004

CloudHealth optimisation & tag compliance reports

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [COST-004](#cost-004) | optimisation-reports | CloudHealth optimisation & tag compliance reports | Reports generated; tracked actions created | CloudHealth reporting + tracker | Monthly | prod | dos-search | draft | Drives optimisation and tag hygiene |

### COST-005

Budgets & alert notifications configured & tested

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [COST-005](#cost-005) | budgets-and-alerts | Budgets & alert notifications configured & tested | Budgets configured; alerts tested successfully | AWS Budgets + notifications | Quarterly + pre-fiscal review | prod | dos-search | draft | Prevents cost overruns via alerting |

### GOV-001

Service Management pre-live acceptance signed

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-001](#gov-001) | service-management-pre-live | Service Management pre-live acceptance signed | Acceptance signed; evidence stored | Governance tracker + document repository | Pre-live | prod | dos-search | draft | Ensures service readiness sign-off |

### GOV-002

Well-Architected review completed & actions closed

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-002](#gov-002) | well-architected-review | Well-Architected review completed & actions closed | Review complete; actions closed or exceptioned | WAR tool + issue tracker | Pre-live + annual | prod | dos-search | draft | Maintains architectural quality |

### GOV-003

Solution Architecture Framework assessment approved

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-003](#gov-003) | saf-assessment-approved | Solution Architecture Framework assessment approved | Approved assessment stored with evidence link; exceptions recorded | Governance tracker + document repository | Pre-live | prod | dos-search | draft | Ensures architectural governance sign-off |

### GOV-004

Engineering Red-lines compliance checklist signed

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-004](#gov-004) | nhs-github-enterprise-repos | All FtRS code repositories are hosted in NHS GitHub Enterprise and comply with securing-repositories policy; engineering dashboards show compliance | 100% repositories on NHS GitHub Enterprise; 100% securing-repositories checks passing; exceptions recorded with owner and review date | Enterprise repository policy audit + engineering compliance dashboards + CI checks | Continuous (CI on change) + quarterly governance review | dev,int,ref,prod | dos-search | draft | Enforces organisational SDLC-1 Red Line for using NHS GitHub Enterprise and securing repositories; provides traceable evidence and automated verification |

### GOV-005

GDPR compliance assessment signed by IG

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-005](#gov-005) | gdpr-assessment-signed | GDPR compliance assessment signed by IG | Assessment signed; actions tracked | IG workflow + evidence repository | Pre-live + annual | prod | dos-search | draft | Ensures data protection compliance |

### GOV-006

Medical Device out-of-scope statement recorded

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-006](#gov-006) | medical-device-out-of-scope | Medical Device out-of-scope statement recorded | Statement recorded and reviewed annually | Evidence repository | Annual review | prod | dos-search | draft | Confirms regulatory position |

### GOV-007

FtRS Architects review & approval logged

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-007](#gov-007) | ftrs-architects-approval | FtRS Architects review & approval logged | Review minutes and approval recorded; actions tracked | Review tracker + minutes repo | Pre-live + on major change | prod | dos-search | draft | Provides architectural oversight evidence |

### GOV-008

Cloud Expert deployment approval documented

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-008](#gov-008) | cloud-expert-approval | Cloud Expert deployment approval documented | Approval recorded; infra readiness checklist passed | Infra checklist + evidence repo | Pre-live | prod | dos-search | draft | Confirms infrastructure deployment readiness |

### GOV-009

Solution Assurance approval ticket closed

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-009](#gov-009) | solution-assurance-approval | Solution Assurance approval ticket closed | Approval obtained; ticket closed | Assurance workflow + evidence repository | Pre-live | prod | dos-search | draft | Meets governance approval requirements |

### GOV-010

Clinical Safety assurance approval recorded

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-010](#gov-010) | clinical-safety-approval | Clinical Safety assurance approval recorded | Approval recorded; evidence available | Clinical safety workflow + repository | Pre-live | prod | dos-search | draft | Complies with clinical safety governance |

### GOV-011

Information Governance approval recorded

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-011](#gov-011) | ig-approval-recorded | Information Governance approval recorded | Approval recorded; actions tracked | IG workflow + evidence repository | Pre-live | prod | dos-search | draft | Meets IG governance |

### GOV-012

TRG approval session outcome logged

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-012](#gov-012) | trg-approval-outcome | TRG approval session outcome logged | Outcome recorded; decisions minuted; actions tracked | TRG minutes + tracker | Pre-live | prod | dos-search | draft | Documents technical governance approval |

### GOV-013

SIRO sign-off obtained

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-013](#gov-013) | siro-signoff | SIRO sign-off obtained | Sign-off recorded; evidence stored | Governance tracker | Pre-live | prod | dos-search | draft | Confirms senior risk acceptance |

### GOV-014

Caldicott Principles Guardian approval recorded

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-014](#gov-014) | caldicott-guardian-approval | Caldicott Principles Guardian approval recorded | Approval recorded with data handling summary | Governance tracker + evidence repo | Pre-live | prod | dos-search | draft | Ensures data handling governance |

### GOV-015

DUEC Assurance Board acceptance logged

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-015](#gov-015) | duec-acceptance | DUEC Assurance Board acceptance logged | Acceptance recorded; actions tracked | Board minutes + tracker | Pre-live | prod | dos-search | draft | Documents assurance acceptance |

### GOV-016

Live Services Board go-live approval recorded

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-016](#gov-016) | live-services-go-live | Live Services Board go-live approval recorded | Go-live approval recorded; evidence stored | Governance tracker + evidence repo | Pre-live | prod | dos-search | draft | Final governance approval before production |

### INT-001

Resources validated against UK Core profiles

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-001](#int-001) | uk-core-profile-validation | Resources validated against UK Core profiles | 100% resources pass UK Core validation in CI and pre-release audit | FHIR validators + contract test suite | CI per build + quarterly audit | int,ref,prod | dos-search | draft | Ensures national standard alignment |

### INT-002

Versioning & deprecation policy published

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-002](#int-002) | versioning-deprecation-policy | Versioning & deprecation policy published | Policy published; changes communicated; minimum 6 months deprecation window | Documentation repo + change comms channel | Review quarterly; update on change | prod | dos-search | draft | Reduces integration friction |

### INT-003

Minor releases backward compatible for 12 months

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-003](#int-003) | backward-compatibility-window | Minor releases backward compatible for 12 months | No breaking changes; deprecation window \u226512 months; exceptions recorded | Contract tests + release notes | CI per build + release review | prod | dos-search | draft | Protects consumer integrations |

### INT-004

Semantic mapping round-trip fidelity preserved

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-004](#int-004) | semantic-roundtrip-fidelity | Semantic mapping round-trip fidelity preserved | Round-trip preserves fields and codes; divergence \u2264 1% | Mapping tests + diff reports | CI per build + monthly audit | int,ref | dos-search | draft | Maintains semantic integrity |

### INT-005

Standard OperationOutcome error structure enforced

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-005](#int-005) | operationoutcome-structure | Standard OperationOutcome error structure enforced | 100% error responses conform to OperationOutcome spec | Contract tests + schema validators | CI per build + weekly contract audit | int,ref,prod | dos-search | draft | Ensures consistent error semantics across integrations |

### INT-006

Identifier normalization applied (uppercase, trimmed)

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-006](#int-006) | identifier-normalization-enforced | Identifier normalization applied (uppercase, trimmed) | 100% identifiers normalised; mismatches \u2264 0.1% | Normalization middleware + validation tests | CI per build + monthly audit | int,ref,prod | dos-search | draft | Ensures consistent identifier handling |

### INT-007

Strict content negotiation implemented

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-007](#int-007) | strict-content-negotiation | Strict content negotiation implemented | Only documented media types accepted; correct response Content-Type | API contract tests + gateway policies | CI per build | int,ref,prod | dos-search | draft | Prevents ambiguity in accepted formats |

### INT-009

Only documented FHIR search params accepted

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-009](#int-009) | documented-search-params-only | Only documented FHIR search params accepted | Unknown search params rejected with OperationOutcome | API gateway policy + contract tests | CI per build | int,ref,prod | dos-search | draft | Prevents ambiguity in search semantics |

### INT-010

Version-controlled integration contract published

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-010](#int-010) | version-controlled-contract | Version-controlled integration contract published | Contract published under version control; lint passes; updated \u22645 business days after change | Spec repo + Spectral lint + diff job | CI per build + weekly audit | int,ref,prod | dos-search | draft | Ensures consistent and timely documentation |

### INT-011

Machine-readable changelog generated

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-011](#int-011) | machine-readable-changelog | Machine-readable changelog generated | Changelog generated per release with breaking changes highlighted | Release pipeline + changelog generator | Per release | prod | dos-search | draft | Supports integrators with clear changes |

### INT-012

Terminology bindings validated

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-012](#int-012) | terminology-binding-validation | Terminology bindings validated | 100% required bindings validated against value sets | Terminology server + validators | CI per build + monthly audit | int,ref,prod | dos-search | draft | Ensures correct coding practices |

### INT-013

Correlation IDs preserved across calls

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-013](#int-013) | correlation-id-preserved | Correlation IDs preserved across calls | 100% requests preserve transaction_id/correlation_id in logs and headers | Middleware + log correlation tests | CI per build + monthly audit | int,ref,prod | dos-search | draft | Enables end-to-end tracing and diagnostics |

### INT-014

Null vs absent data handled per FHIR

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-014](#int-014) | null-vs-absent-semantics | Null vs absent data handled per FHIR | Responses follow FHIR rules; conformance tests pass | Contract tests + response validators | CI per build | int,ref,prod | dos-search | draft | Clarifies response semantics for consumers |

### INT-015

≥90% interoperability scenario coverage

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-015](#int-015) | interoperability-scenario-coverage | \u226590% interoperability scenario coverage | \u226590% coverage across documented scenarios; exceptions recorded | Scenario test suite + coverage reports | CI per build + quarterly review | int,ref,prod | dos-search | draft | Ensures comprehensive interoperability validation |

### INT-016

Stateless sequence-independent operations

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-016](#int-016) | stateless-sequence-independence | Stateless sequence-independent operations | 100% documented operations produce correct outcome independent of prior invocation order | Idempotence + shuffled sequence integration tests | CI per build + quarterly audit | int,ref,prod | dos-search | draft | Enables horizontal scaling and predictable consumer integration |

### INT-018

Comprehensive published OpenAPI documentation (overview, audience, related APIs, roadmap, SLA, tech stack, network access, security/auth, test environment, onboarding, endpoints with examples)

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [INT-018](#int-018) | api-documentation-completeness | Comprehensive published OpenAPI documentation | All required catalogue sections present; spec passes lint; updated ≤5 business days after prod change | Spectral lint + spec diff + manual checklist | CI per build + weekly audit | int,ref,prod | dos-search | draft | Reduces integration friction; ensures transparency for consumers |

### OBS-001

App & infra health panels show green

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-001](#obs-001) | health-panels-green | App & infra health panels show green | All critical panels green; no stale data | Health checks + dashboard status API | Continuous + CI verification on change | int,ref,prod | dos-search | draft | Ensures at-a-glance service health visibility |

### OBS-007

Performance metrics latency ≤60s

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-007](#obs-007) | perf-metrics-latency | Performance metrics latency ≤60s | Metrics pipeline delivers data within 60s latency | Metrics agent + ingestion SLA alerting | Continuous monitoring | int,ref,prod | dos-search | draft | Fresh metrics are required for accurate operational decisions |

### OBS-008

TPS per endpoint displayed & threshold alert configured

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-008](#obs-008) | tps-threshold-alert | TPS per endpoint displayed & threshold alert configured | TPS dashboard present; alert rule configured and tested | Metrics backend + alerting system | CI validation + monthly alert fire drill | int,ref,prod | dos-search | draft | Detects throughput anomalies proactively |

### OBS-009

Endpoint latency histograms with p50/p95/p99

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-009](#obs-009) | latency-histograms | Endpoint latency histograms with p50/p95/p99 | Histograms available per endpoint with p50/p95/p99 series | Metrics backend + dashboard | Continuous | int,ref,prod | dos-search | draft | Percentile visibility supports performance governance |

### OBS-010

Aggregate latency panel accurate within 2% roll-up

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-010](#obs-010) | aggregate-latency-accuracy | Aggregate latency panel accurate within 2% roll-up | Roll-up accuracy within \u22642% vs raw series | Dashboard query tests + calibration script | Monthly calibration | prod | dos-search | draft | Ensures trustworthy aggregate metrics |

### OBS-011

Failure types logged & classified in dashboard

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-011](#obs-011) | failure-type-classification | Failure types logged & classified in dashboard | 100% failures carry type; classification accuracy \u2265 95% | Structured logging + classifier + dashboard | Continuous + monthly accuracy audit | int,ref,prod | dos-search | draft | Improves incident triage |

### OBS-012

Error percentage metric & alert configured

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-012](#obs-012) | error-percentage-alert | Error percentage metric & alert configured | Alert triggers when error% > 1% over 5m; playbook linked | Metrics backend + alerting rules | Continuous + monthly tuning | prod | dos-search | draft | Early detection of reliability regressions |

### OBS-013

Infra log query returns expected fields

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-013](#obs-013) | infra-log-query-fields | Infra log query returns expected fields | Queries return required fields (timestamp, severity, host, correlation_id) | Log query tests + schema | CI per build + weekly audit | int,ref,prod | dos-search | draft | Ensures log usability for ops |

### OBS-014

Infra log entries include required fields

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-014](#obs-014) | infra-log-required-fields | Infra log entries include required fields | 100% entries include required fields; schema lint passes | Log schema validators + CI checks | CI per build + monthly audit | int,ref,prod | dos-search | draft | Guarantees structured logging quality |

### OBS-030

Distributed trace spans cover end-to-end request

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-030](#obs-030) | distributed-trace-coverage | Distributed trace spans cover end-to-end request | ≥95% of requests include spans across key tiers | Tracing SDKs + sampling config | Continuous + monthly sampling review | int,ref,prod | dos-search | draft | Enables end-to-end diagnosis and correlation across layers |

### OBS-033

Unauthorized API access attempts logged, classified, alerted

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-033](#obs-033) | unauth-access-monitoring | Unauthorized API access attempts logged & alerted with context | 100% auth failures & forbidden requests produce structured log entry with reason, correlation_id, source_ip, user_agent; alert triggers on >5 failed auth attempts per principal per 1m or anomaly spike (>3x baseline) | API gateway logs, auth middleware, metrics backend, alerting rules, anomaly detection job | Continuous collection + weekly anomaly review + monthly rule tuning | int,ref,prod | dos-search | draft | Early detection of credential stuffing, token misuse, and privilege escalation attempts |

### PERF-001

Each operation meets registry-defined percentile targets (p50/p95) logged & asserted (see performance/expectations.yaml)

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [PERF-001](#perf-001) | perf-dos-search-latency | Assert p50/p95/max targets per operation | As per operations in PERF-001 (dos-search endpoints) | synthetic probes + real-user monitoring | continuous | prod | dos-search | draft | Aligns with defined operation targets |
| [PERF-001](#perf-001) | perf-lookup-ods-latency | Assert p50/p95/max targets per operation | As per operations in PERF-001 (dos-search endpoints) | synthetic probes + real-user monitoring | continuous | prod | dos-search | draft | Aligns with defined operation targets |
| [PERF-001](#perf-001) | perf-nearby-latency | Assert p50/p95/max targets per operation | As per operations in PERF-001 (dos-search endpoints) | synthetic probes + real-user monitoring | continuous | prod | dos-search | draft | Aligns with defined operation targets |
| [PERF-001](#perf-001) | perf-org-get-latency | Assert p50/p95/max targets per operation | As per operations in PERF-001 (crud-apis endpoints) | synthetic probes + real-user monitoring | continuous | prod | dos-search | draft | Aligns with defined operation targets |
| [PERF-001](#perf-001) | perf-org-update-latency | Assert p50/p95/max targets per operation | As per operations in PERF-001 (crud-apis endpoints) | synthetic probes + real-user monitoring | continuous | prod | dos-search | draft | Aligns with defined operation targets |

### PERF-011

dos-search endpoints sustain burst ≥150 TPS (registry burst_tps_target)

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [PERF-011](#perf-011) | perf-dos-search-burst-tps | dos-search endpoints sustain burst \u2265150 TPS | Burst_tps_target met across key endpoints as per operations registry | Performance harness + synthetic load + RUM | Quarterly + CI smoke on change | int,ref,prod | dos-search | draft | Verifies burst throughput capacity |

### PERF-012

dos-search endpoints sustain steady ≥150 TPS (registry sustained_tps_target)

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [PERF-012](#perf-012) | perf-dos-search-steady-tps | dos-search endpoints sustain steady \u2265150 TPS | Sustained_tps_target met across key endpoints as per operations registry | Performance harness + soak tests + RUM | Quarterly + CI smoke on change | int,ref,prod | dos-search | draft | Verifies steady-state throughput capacity |

### PERF-013

Request payload size per endpoint ≤1MB (max_request_payload_bytes)

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [PERF-013](#perf-013) | perf-request-payload-limits | Request payload size per endpoint \u22641MB | Max_request_payload_bytes enforced per endpoint per operations registry | Gateway payload limit + contract tests | CI per build + monthly audit | int,ref,prod | dos-search | draft | Prevents oversized payload degradation |

### REL-002

AZ failure simulation maintains service

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [REL-002](#rel-002) | az-failure-simulation | AZ failure simulation maintains service | Successful failover with sustained service availability; no data loss | Chaos simulation + health checks | Quarterly exercise | int,ref | dos-search | draft | Validates resilience to Availability Zone failures |

### REL-003

Lifecycle reliability checklist completed

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [REL-003](#rel-003) | reliability-checklist-complete | Lifecycle reliability checklist completed | 100% checklist items complete; exceptions recorded with expiry | Checklist tracker + evidence links | Pre-live + quarterly review | int,ref,prod | dos-search | draft | Ensures reliability practices across lifecycle |

### REL-004

DoS simulation mitigated; service responsive

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [REL-004](#rel-004) | dos-simulation-mitigated | DoS simulation mitigated; service responsive | Sustained responsiveness; error rate \u2264 1%; p95 latency within SLA during attack | Attack simulator + WAF/rate-limiter + metrics | Quarterly exercise | int,ref | dos-search | draft | Validates resilience under volumetric attacks |

### REL-007

Brute force/auth anomalies rate limited & alerted (peak 500 TPS burst capacity; rate limits + alerts)

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [REL-007](#rel-007) | auth-brute-force-protection | Brute force/auth anomalies rate limited & alerted (peak 500 TPS legitimate burst supported) | Peak 500 TPS legitimate auth unaffected; anomalies blocked; alert ≤30s; ≤1% false positives | Auth gateway rate limiter + anomaly aggregator + performance harness + alerting | Continuous runtime enforcement + daily compliance script | dev,int,ref,prod | dos-search | draft | Protects availability & integrity under authentication attack patterns |

### REL-011

Unhealthy node auto-replaced; workload continues

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [REL-011](#rel-011) | unhealthy-node-auto-replace | Unhealthy node auto-replaced; workload continues | Auto-replacement within policy; no user-visible downtime | Autoscaling group events + workload health | Continuous monitoring + quarterly drill | int,ref,prod | dos-search | draft | Maintains reliability during node failures |

### REL-012

Single node removal shows stable performance & zero data loss

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [REL-012](#rel-012) | single-node-removal-safety | Single node removal shows stable performance & zero data loss | 0 data loss; p95 latency delta \u2264 10% during removal | Autoscaling events + workload health + integrity checks | Quarterly drill | int,ref | dos-search | draft | Ensures resilience to node loss without user impact |

### REL-013

Tier failure graceful degradation & recovery evidenced

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [REL-013](#rel-013) | tier-failure-graceful-degrade | Tier failure graceful degradation & recovery evidenced | Documented fallback; recovery time within SLA | Chaos experiments + observability evidence | Quarterly | int,ref | dos-search | draft | Demonstrates graceful degradation patterns |

### REL-014

External outage shows fallback & user messaging

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [REL-014](#rel-014) | external-outage-fallback | External outage shows fallback & user messaging | Documented fallback engaged; user messaging displayed; error rate \u2264 2%; recovery within SLA | Chaos experiments on external deps + observability evidence | Quarterly | int,ref | dos-search | draft | Demonstrates graceful handling of external dependency outages |

### REL-015

LB failure retains sessions & continues routing

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [REL-015](#rel-015) | lb-failure-session-retention | LB failure retains sessions & continues routing | Zero session loss; traffic re-routed within 30s; p95 latency delta \u2264 10% | LB failover drill + session continuity tests + metrics | Semi-annual drill | int,ref | dos-search | draft | Ensures resilience of routing tier |

### SCAL-001

Horizontal scale-out increases TPS linearly within tolerance

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SCAL-001](#scal-001) | horizontal-scale-linear | Horizontal scale-out increases TPS linearly within tolerance | TPS increases ~linearly per replica within agreed tolerance | Load tests + autoscaling reports | Quarterly simulation | int,ref | dos-search | draft | Validates scale-out effectiveness |

### SCAL-002

Vertical resize retains data & function without downtime

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SCAL-002](#scal-002) | vertical-resize-no-downtime | Vertical resize retains data & function without downtime | Resize completes with zero downtime and no data loss | Resize runbook + health checks | Semi-annual exercise | int,ref | dos-search | draft | Ensures safe vertical scaling |

### SCAL-003

All layers pass scalability checklist

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SCAL-003](#scal-003) | scalability-checklist-complete | All layers pass scalability checklist | 100% checklist items complete; exceptions recorded with expiry | Checklist tracker + evidence links | Quarterly | int,ref | dos-search | draft | Ensures scale readiness across tiers |

### SCAL-004

Scale-down events occur after sustained low utilisation

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SCAL-004](#scal-004) | scale-down-sustained-low-util | Scale-down events occur after sustained low utilisation | No scale-down unless utilisation < 40% sustained for 30m; no flapping | Autoscaling metrics + policy | Continuous + monthly policy audit | prod | dos-search | draft | Prevents scale instability |

### SCAL-005

Autoscaling policy simulation triggers controlled scale

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SCAL-005](#scal-005) | autoscaling-policy-simulation | Autoscaling policy simulation triggers controlled scale | Policy simulates expected scale events; no flapping | Policy simulator + metrics | Quarterly | int,ref | dos-search | draft | Confirms autoscaling tuning |

### SCAL-006

Scale event shows no SLA breach in latency/error

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SCAL-006](#scal-006) | scale-event-sla | Scale event shows no SLA breach in latency/error | No breach in latency/error SLAs during scale | Metrics/alerts during scale events | Continuous monitoring + quarterly drill | int,ref,prod | dos-search | draft | Protects user experience during scaling |

### SCAL-007

Capacity report shows ≥30% headroom

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SCAL-007](#scal-007) | capacity-headroom | Capacity report shows ≥30% headroom | >= 30% capacity headroom maintained | Capacity planning reports | Monthly | prod | dos-search | draft | Ensures buffer for demand spikes |

### SCAL-008

No manual scaling tickets for variance period

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SCAL-008](#scal-008) | manual-scaling-eliminated | No manual scaling tickets for variance period | 0 manual scaling tickets in rolling 90 days | Ticketing system + scaling audit | Monthly review | prod | dos-search | draft | Confirms autoscaling effectiveness |

### SCAL-009

Audit logs capture actor/reason for scaling

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SCAL-009](#scal-009) | scaling-audit-context | Audit logs capture actor/reason for scaling | 100% scale events have actor, reason, correlation_id | Audit log pipeline + policy | Continuous + quarterly audit | prod | dos-search | draft | Provides traceability of scaling decisions |

### SCAL-010

Predictive alert fires at utilisation forecast threshold

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SCAL-010](#scal-010) | predictive-utilisation-alert | Predictive alert fires at utilisation forecast threshold | Forecasted utilisation > 80% in 15m triggers alert; MTT Alert < 2m | Forecasting job + alerting rules | Continuous + monthly tuning | prod | dos-search | draft | Prevents SLA breach via early action |

### SEC-001

Crypto algorithms conform; weak ciphers rejected

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-001](#sec-001) | crypto-cipher-policy | Crypto algorithms conform; weak ciphers rejected | TLS1.2+ only; no weak/legacy ciphers enabled | TLS scanner + configuration policy checks | CI per change + monthly scan | dev,int,ref,prod | dos-search | draft | Enforces modern TLS standards; automated scans detect drift |

### SEC-002

WAF security pillar checklist completed & gaps tracked

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-002](#sec-002) | waf-pillar-checklist | WAF security pillar checklist completed & gaps tracked | Checklist complete; 100% actions tracked; 0 open critical gaps | WAF checklist repository + issue tracker gate | Quarterly + on change | dev,int,ref,prod | dos-search | draft | Formalizes WAF security governance; gaps tracked to closure |

### SEC-003

All endpoints TLS only; storage encryption enabled

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-003](#sec-003) | tls-encryption-endpoints | All public/private API endpoints enforce TLS; storage services enable encryption at rest | 100% compliant across resources | AWS Config rules + Terraform policy checks | Continuous (real-time) with CI enforcement on change | dev,int,ref,prod | dos-search | draft | Aligns with NHS policy; Config provides continuous guardrails; CI blocks drift |

### SEC-004

Storage services show encryption enabled

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-004](#sec-004) | storage-encryption-enabled | Storage services show encryption enabled | 100% storage resources encrypted at rest | AWS Config rules + Terraform policy checks | Continuous + CI enforcement | dev,int,ref,prod | dos-search | draft | Guardrails ensure encryption at rest across services |

### SEC-005

Cross-environment data access attempts denied

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-005](#sec-005) | cross-env-access-denied | Cross-env data access attempts denied and logged | 100% denial; audit logs prove enforcement | IAM policies + SCP guardrails + audit log queries | CI policy checks + monthly audit review | dev,int,ref,prod | dos-search | draft | Prevents accidental or malicious cross-environment data access |

### SEC-006

No direct prod console queries detected in audit period

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-006](#sec-006) | prod-console-access-audit | No direct prod console queries detected in audit period | 0 non-approved console queries in audit period | CloudTrail + SIEM audit queries | Weekly audit + alerting | prod | dos-search | draft | Detects improper direct access to production consoles |

### SEC-007

SG rules audited; attempt broad ingress denied

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-007](#sec-007) | sg-broad-ingress-denied | SG rules audited; attempt broad ingress denied | 0 broad (0.0.0.0/0) ingress on restricted ports | AWS Config + IaC linter | CI per change + monthly audit | dev,int,ref,prod | dos-search | draft | Prevents risky network exposure via security groups |

### SEC-008

Perimeter scan shows no broad whitelist & secure channels

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-008](#sec-008) | perimeter-scan | Perimeter scan shows no broad whitelist & secure channels | No broad whitelists; only secure channels reported | External perimeter scanner + config validation | Monthly + on change | int,ref,prod | dos-search | draft | Confirms perimeter hygiene and secure external exposure |

### SEC-009

ASVS & CIS benchmark automation reports pass thresholds

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-009](#sec-009) | cis-benchmark-compliance | CIS benchmark automation reports meet pass thresholds for targeted services | >= 95% controls passing; all high-severity findings remediated or exceptioned | CIS benchmark tooling integrated in CI and periodic audits | CI per change + monthly full audit | dev,int,ref,prod | dos-search | draft | Baseline hardening validated continuously; monthly cadence catches drift |

### SEC-010

Annual pen test executed; remediation tickets raised & closed

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-010](#sec-010) | annual-pentest | Annual pen test executed; remediation tickets raised & closed | Pen test executed; all critical findings remediated or exceptioned | Pen test reports + remediation tracking | Annual | prod | dos-search | draft | Validates security posture with external testing and tracked remediation |

### SEC-011

Security features enabled latency within SLA

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-011](#sec-011) | security-features-latency-sla | Security features enabled latency within SLA | Added latency within agreed SLA per endpoint | Performance tests with security features enabled | CI perf checks + monthly regression review | int,ref,prod | dos-search | draft | Ensures security does not breach performance SLAs |

### SEC-012

IAM policy review confirms least privilege for system roles

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-012](#sec-012) | iam-least-privilege | IAM policy review confirms least privilege for system roles | >= 95% policies compliant; no wildcard resource; explicit actions only | IAM Access Analyzer + policy linters | CI per change + quarterly audit | dev,int,ref,prod | dos-search | draft | Continuous analysis prevents privilege creep; periodic review catches drift |

### SEC-013

Key rotation events logged; unauthorized access denied

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-013](#sec-013) | key-rotation-logging | Key rotation events logged; unauthorized access denied | 100% rotation events logged; 0 unauthorized key access | KMS/AWS logs + SIEM correlation | Quarterly audit + CI checks on policy | dev,int,ref,prod | dos-search | draft | Audit trail confirms rotation compliance and denial of unauthorized access |

### SEC-014

mTLS handshake succeeds between designated services

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-014](#sec-014) | mtls-service-handshake | mTLS handshake succeeds between designated services using ITOC-approved CA signed leaf + intermediate certs (chain to ITOC root); invalid/expired/revoked/untrusted-issuer/weak-cipher attempts rejected | 100% handshake success for valid ITOC chain; 0 successful handshakes with expired, revoked, weak cipher, or non-ITOC issuer certs; rotation introduces 0 downtime | Integration tests (valid/expired/revoked/wrong-CA/weak-cipher) + gateway cert management + OCSP/CRL polling | CI per build + cert rotation checks + revocation poll ≤5m | int,ref,prod | dos-search | draft | Enforces trusted ITOC certificate chain, strong ciphers, timely revocation, and zero-downtime rotation for secure service-to-service trust |

### SEC-015

Expiry alert fired in advance; renewal executed seamlessly

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-015](#sec-015) | cert-expiry-alert-renewal | Expiry alert fired in advance; renewal executed seamlessly | >= 30 days prior alert; 0 outage during renewal | Cert manager alerts + renewal runbooks | Continuous monitoring | int,ref,prod | dos-search | draft | Proactive renewal prevents downtime; alerts ensure timely action |

### SEC-016

MFA enforced for all privileged infra roles

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-016](#sec-016) | privileged-mfa-enforced | MFA enforced for all privileged infra roles | 100% privileged roles require MFA | IAM policy checks + directory audit | CI policy checks + quarterly audit | dev,int,ref,prod | dos-search | draft | Strong authentication for privileged accounts reduces risk |

### SEC-017

Scan reports zero unmanaged long-lived credentials

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-017](#sec-017) | zero-long-lived-credentials | Scan reports zero unmanaged long-lived credentials | 0 unmanaged long-lived credentials | Secret scanners + IAM credential report audit | CI per build + weekly audit | dev,int,ref,prod | dos-search | draft | Reduces risk from forgotten credentials; continuous scanning plus scheduled audits |

### SEC-018

Supplier audit attestation stored & verified

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-018](#sec-018) | supplier-audit-attestation | Supplier audit attestation stored & verified | Attestations current; verification completed | Supplier management system + evidence repository | Annual + on contract change | prod | dos-search | draft | Ensures supplier compliance and auditable records |

### SEC-019

Segmentation test confirms tenant isolation

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-019](#sec-019) | segmentation-tenant-isolation | Segmentation test confirms tenant isolation | 100% isolation; no cross-tenant data access observed | Segmentation test suite + log verification | Quarterly | int,ref,prod | dos-search | draft | Ensures strict isolation between tenants per policy |

### SEC-021

Port scan matches approved diagnostic list only

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-021](#sec-021) | port-scan-diagnostic-only | Port scan matches approved diagnostic list only | No unexpected open ports detected outside approved list | Automated port scan + baseline comparison | Monthly + CI smoke on infra changes | dev,int,ref,prod | dos-search | draft | Detects misconfigurations; verifies adherence to diagnostic port policy |

### SEC-022

Utility program access restricted to approved roles

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-022](#sec-022) | utility-access-restricted | Utility program access restricted to approved roles | Only approved roles can access utility programs | RBAC policy checks + audit logs | CI policy checks + monthly audit | dev,int,ref,prod | dos-search | draft | Prevents misuse of diagnostic utilities |

### SEC-023

Deployment provenance shows unique traceable accounts

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-023](#sec-023) | deployment-provenance-traceable | Deployment provenance shows unique traceable accounts | All deployments traceable to unique accounts | CI/CD audit trails + commit signing | Continuous | dev,int,ref,prod | dos-search | draft | Ensures accountability and traceability for all deployments |

### SEC-024

Code/data transfer logs show integrity & secure channels

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-024](#sec-024) | transfer-integrity-secure | Code/data transfer logs show integrity & secure channels | 100% transfers logged; integrity and secure channel verified | Checksums/signatures + TLS enforcement + audit logs | CI per change + weekly reviews | dev,int,ref,prod | dos-search | draft | Validates integrity and secure transport for all transfers |

### SEC-025

PID requests enforce mTLS; plain text blocked

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-025](#sec-025) | pid-mtls-enforcement | Requests carrying PID fields require mutual TLS; plaintext requests blocked | 100% enforcement on designated endpoints | API gateway/WAF policy + integration tests | CI policy validation + continuous enforcement | int,ref,prod | dos-search | draft | Ensures transport security for sensitive data; test coverage verifies enforcement |

### SEC-026

API responses contain no unencrypted PID fields

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-026](#sec-026) | pid-no-plaintext-response | API responses contain no unencrypted PID fields | 0 occurrences of unencrypted PID in responses | Integration tests + response scanners | CI per build + periodic production sampling | int,ref,prod | dos-search | draft | Ensures sensitive data is never returned unencrypted |

### SEC-027

Build fails on high CVE; report archived

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-027](#sec-027) | high-cve-block | Build fails when high/critical CVEs detected in application or container dependencies | 0 unresolved High/Critical CVEs at release time | SCA scanner (e.g., OWASP Dependency-Check), container scanner, pipeline gate | CI per build + scheduled weekly scans | dev,int,ref | dos-search | draft | Prevents introduction of known vulnerabilities; gate aligned to release quality |

### SEC-028

Release pipeline blocks on critical unresolved findings

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-028](#sec-028) | release-block-critical-findings | Release pipeline blocks on critical unresolved findings | 0 critical unresolved findings prior to release | Pipeline gate integrated with SCA, container, IaC scanners | Per release | dev,int,ref | dos-search | draft | Enforces remediation before release; gate consolidates multiple scanner outputs |

### SEC-029

All API endpoints enforce CIS2 JWT authentication (signature, issuer, audience, assurance claims)

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-029](#sec-029) | cis2-jwt-auth-enforced | All API endpoints enforce CIS2 JWT authentication (signature, issuer, audience, assurance claims) | 100% endpoints require valid CIS2 JWT; invalid/missing tokens rejected with structured 401 | OIDC integration tests + JWT validator + JWKS cache monitor | CI per build + continuous runtime enforcement | dev,int,ref,prod | dos-search | draft | Ensures uniform strong authentication; claim + signature validation prevents unauthorized access |

### SEC-030

Certificates and private keys stored only in approved encrypted secret stores; zero plain text exposure

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-030](#sec-030) | cert-secure-storage | Certificate and private key material stored only in approved encrypted secret stores (KMS/Secrets Manager); zero plaintext in repos, images, build logs, or artifacts | 0 plaintext occurrences; 100% issuance & rotation actions use managed secrets; 100% scan coverage of git history and container layers | Secret scanning (git history + container layers), CI policy checks, artifact scanner, repo pre-commit hooks | CI per build + weekly full history & image layer scan | dev,int,ref,prod | dos-search | draft | Prevents certificate/private key exposure by enforcing exclusive use of encrypted secret storage and continuous scanning |
