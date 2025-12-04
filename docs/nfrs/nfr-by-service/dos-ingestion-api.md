# FtRS NFR – Service: dos-ingestion-api

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
| Cost | COST-001 | Mandatory tagging set present on 100% resources | All resources have mandatory cost tags for allocation and reporting. | STORY-COST-001 |
| Cost | COST-002 | Monthly Cost Explorer review & anomaly log | Monthly cost review identifies anomalies and tracks actions. | STORY-COST-002 |
| Cost | COST-003 | CloudHealth access for each team infra engineer | Each team infra engineer has access to cost analysis tooling (e.g., CloudHealth). | STORY-COST-003 |
| Cost | COST-004 | CloudHealth optimisation & tag compliance reports | Optimisation and tag compliance reports are produced and reviewed. | STORY-COST-004 |
| Cost | COST-005 | Budgets & alert notifications configured & tested | Budgets and cost alert notifications are configured and tested. | STORY-COST-005 |
| Cost | COST-006 | #ftrs-cost-alerts channel created & receiving test alerts | Dedicated cost alerts channel receives test and live notifications. | (none) |
| Cost | COST-007 | Quarterly cost review minutes & tracked actions | Quarterly cost reviews record minutes and follow-up actions. | (none) |
| Governance | GOV-003 | Solution Architecture Framework assessment approved | Solution Architecture Framework assessment is approved. | STORY-GOV-003 |
| Governance | GOV-004 | Engineering Red-lines compliance checklist signed | Engineering red-lines compliance checklist is signed. | STORY-GOV-004 |
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
| Observability | OBS-001 | App & infra health panels show green | Application and infrastructure health panels display green status during normal operation. | STORY-OBS-001 |
| Observability | OBS-002 | Authenticated remote health dashboard accessible | Authenticated remote health dashboard is accessible to support teams. | (none) |
| Observability | OBS-003 | Health event visible ≤60s after failure | Health events appear on dashboards shortly after failures (within target freshness). | (none) |
| Observability | OBS-004 | Automated maintenance tasks executed; zero manual interventions | Automated maintenance tasks run successfully with no manual intervention required. | (none) |
| Observability | OBS-005 | Performance metrics per layer present | Layered performance metrics (app, DB, cache) are visible. | (none) |
| Observability | OBS-006 | Remote performance dashboard matches local view | Remote performance dashboard mirrors local environment metrics accurately. | (none) |
| Observability | OBS-007 | Performance metrics latency ≤60s | Performance metrics latency (ingest to display) stays within defined limit (e.g., ≤60s). | STORY-OBS-002 |
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
| Observability | OBS-031 | Anonymised behaviour metrics collected without identifiers | Anonymised behavioural metrics are collected without exposing personal identifiers. | (none) |
| Observability | OBS-032 | Per-endpoint 4xx/5xx response metrics & alert thresholds configured | Per-endpoint 4xx and 5xx response metrics are captured with alert thresholds so error rate spikes are detected and acted upon quickly. | FTRS-1573 |
| Observability | OBS-033 | Unauthorized API access attempts logged, classified, alerted | Unauthorized API access attempts (failed authentication, forbidden operations, rate limit breaches, anomalous spikes) are logged with required context and generate timely alerts for early detection of credential misuse or attack patterns. | FTRS-1607 |
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
| Reliability | REL-007 | Brute force/auth anomalies rate limited & alerted (peak 500 TPS burst capacity; rate limits + alerts) | Brute force or auth anomaly attempts are rate limited and create alerts. | FTRS-1598 |
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
| Security | SEC-001 | Crypto algorithms conform; weak ciphers rejected | Use only strong, approved cryptographic algorithms; weak or deprecated ciphers are blocked. | STORY-SEC-013 |
| Security | SEC-002 | WAF security pillar checklist completed & gaps tracked | Complete the AWS/WAF security pillar checklist and track remediation actions for any gaps. | (none) |
| Security | SEC-003 | All endpoints TLS only; storage encryption enabled | All service endpoints enforce TLS and all stored data (databases, buckets) is encrypted at rest. | FTRS-1563 |
| Security | SEC-004 | Storage services show encryption enabled | Every storage service (S3, RDS, etc.) shows encryption enabled with managed or customer keys. | (none) |
| Security | SEC-005 | Cross-environment data access attempts denied | Strict environment isolation: data access from one environment to another is prevented. | (none) |
| Security | SEC-006 | No direct prod console queries detected in audit period | No direct production console queries by engineers outside approved, audited break-glass processes. | (none) |
| Security | SEC-007 | SG rules audited; attempt broad ingress denied | Network security groups allow only narrowly scoped inbound rules; broad ingress is denied. | STORY-SEC-017 |
| Security | SEC-008 | Perimeter scan shows no broad whitelist & secure channels | Perimeter scans show secure transport, no open broad whitelists, and hardened edge configuration. | (none) |
| Security | SEC-009 | ASVS & CIS benchmark automation reports pass thresholds | Automated ASVS and CIS benchmark scans meet pass thresholds; failures trigger remediation. | (none) |
| Security | SEC-010 | Annual pen test executed; remediation tickets raised & closed | Annual penetration test completed; identified issues tracked and closed. | (none) |
| Security | SEC-012 | IAM policy review confirms least privilege for system roles | IAM roles and policies grant least privilege; periodic reviews confirm minimal access. | (none) |
| Security | SEC-013 | Key rotation events logged; unauthorized access denied | Cryptographic keys rotate on schedule and unauthorized access attempts are rejected and logged. | (none) |
| Security | SEC-016 | MFA enforced for all privileged infra roles | Privileged infrastructure roles require multi-factor authentication (MFA). | STORY-SEC-023 |
| Security | SEC-017 | Scan reports zero unmanaged long-lived credentials | No long-lived unmanaged credentials; periodic scans confirm only managed secrets exist. | (none) |
| Security | SEC-018 | Supplier audit attestation stored & verified | Third-party supplier security attestation is collected and stored for audit. | (none) |
| Security | SEC-019 | Segmentation test confirms tenant isolation | Tenant or data segmentation tests confirm isolation boundaries hold. | (none) |
| Security | SEC-021 | Port scan matches approved diagnostic list only | Port scans reveal only approved diagnostic and service ports—no unexpected exposures. | (none) |
| Security | SEC-022 | Utility program access restricted to approved roles | Access to powerful utility programs is restricted to approved roles. | (none) |
| Security | SEC-023 | Deployment provenance shows unique traceable accounts | Deployment provenance shows traceable unique accounts per automated pipeline stage. | (none) |
| Security | SEC-024 | Code/data transfer logs show integrity & secure channels | Transfer of code or data maintains integrity and uses secure channels; events are logged. | (none) |
| Security | SEC-027 | Build fails on high CVE; report archived | Build pipeline blocks release when critical CVEs exceed threshold; reports archived. | STORY-SEC-002 |
| Security | SEC-028 | Release pipeline blocks on critical unresolved findings | Releases are halted if critical unresolved security findings remain. | (none) |
| Security | SEC-030 | Certificates and private keys stored only in approved encrypted secret stores; zero plain text exposure | Certificates and private keys are stored only in approved encrypted secret stores (e.g., Secrets Manager/KMS) with zero plaintext exposure across repositories, images, logs, or build artifacts; continuous scanning enforces compliance. | FTRS-1602 |

## Operations

No performance operations defined for this service.

## Controls

### COST-001

Mandatory tagging set present on 100% resources

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| mandatory-tagging | Mandatory tagging set present on 100% resources | 100% resources carry mandatory tags | AWS Config rules + tag audit automation | Continuous + monthly report | dev,int,ref,prod | dos-ingestion-api | draft | Enables cost visibility and accountability |

### COST-002

Monthly Cost Explorer review & anomaly log

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| monthly-cost-review | Monthly Cost Explorer review & anomaly log | Review completed; anomalies logged with actions | Cost Explorer + anomaly detection | Monthly | prod | dos-ingestion-api | draft | Ensures proactive cost management |

### COST-003

CloudHealth access for each team infra engineer

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| cloudhealth-access | CloudHealth access for each team infra engineer | Access provisioned; onboarding verified | CloudHealth admin + access logs | Quarterly verification | prod | dos-ingestion-api | draft | Ensures teams can act on cost insights |

### COST-004

CloudHealth optimisation & tag compliance reports

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| optimisation-reports | CloudHealth optimisation & tag compliance reports | Reports generated; tracked actions created | CloudHealth reporting + tracker | Monthly | prod | dos-ingestion-api | draft | Drives optimisation and tag hygiene |

### COST-005

Budgets & alert notifications configured & tested

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| budgets-and-alerts | Budgets & alert notifications configured & tested | Budgets configured; alerts tested successfully | AWS Budgets + notifications | Quarterly + pre-fiscal review | prod | dos-ingestion-api | draft | Prevents cost overruns via alerting |

### GOV-004

Engineering Red-lines compliance checklist signed

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| nhs-github-enterprise-repos | All FtRS code repositories are hosted in NHS GitHub Enterprise and comply with securing-repositories policy; engineering dashboards show compliance | 100% repositories on NHS GitHub Enterprise; 100% securing-repositories checks passing; exceptions recorded with owner and review date | Enterprise repository policy audit + engineering compliance dashboards + CI checks | Continuous (CI on change) + quarterly governance review | dev,int,ref,prod | dos-ingestion-api | draft | Enforces organisational SDLC-1 Red Line for using NHS GitHub Enterprise and securing repositories; provides traceable evidence and automated verification |

### OBS-001

App & infra health panels show green

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| health-panels-green | App & infra health panels show green | All critical panels green; no stale data | Health checks + dashboard status API | Continuous + CI verification on change | int,ref,prod | dos-ingestion-api | draft | Ensures at-a-glance service health visibility |

### OBS-007

Performance metrics latency ≤60s

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| perf-metrics-latency | Performance metrics latency ≤60s | Metrics pipeline delivers data within 60s latency | Metrics agent + ingestion SLA alerting | Continuous monitoring | int,ref,prod | dos-ingestion-api | draft | Fresh metrics are required for accurate operational decisions |

### OBS-033

Unauthorized API access attempts logged, classified, alerted

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| unauth-access-monitoring | Unauthorized API access attempts logged & alerted with context | 100% auth failures & forbidden requests produce structured log entry with reason, correlation_id, source_ip, user_agent; alert triggers on >5 failed auth attempts per principal per 1m or anomaly spike (>3x baseline) | API gateway logs, auth middleware, metrics backend, alerting rules, anomaly detection job | Continuous collection + weekly anomaly review + monthly rule tuning | int,ref,prod | dos-ingestion-api | draft | Early detection of credential stuffing, token misuse, and privilege escalation attempts |

### REL-007

Brute force/auth anomalies rate limited & alerted (peak 500 TPS burst capacity; rate limits + alerts)

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| auth-brute-force-protection | Brute force/auth anomalies rate limited & alerted (peak 500 TPS legitimate burst supported) | Peak 500 TPS legitimate auth unaffected; anomalies blocked; alert ≤30s; ≤1% false positives | Auth gateway rate limiter + anomaly aggregator + performance harness + alerting | Continuous runtime enforcement + daily compliance script | dev,int,ref,prod | dos-ingestion-api | draft | Protects availability & integrity under authentication attack patterns |

### SEC-001

Crypto algorithms conform; weak ciphers rejected

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| crypto-cipher-policy | Crypto algorithms conform; weak ciphers rejected | TLS1.2+ only; no weak/legacy ciphers enabled | TLS scanner + configuration policy checks | CI per change + monthly scan | dev,int,ref,prod | dos-ingestion-api | draft | Enforces modern TLS standards; automated scans detect drift |

### SEC-002

WAF security pillar checklist completed & gaps tracked

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| waf-pillar-checklist | WAF security pillar checklist completed & gaps tracked | Checklist complete; 100% actions tracked; 0 open critical gaps | WAF checklist repository + issue tracker gate | Quarterly + on change | dev,int,ref,prod | dos-ingestion-api | draft | Formalizes WAF security governance; gaps tracked to closure |

### SEC-003

All endpoints TLS only; storage encryption enabled

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| tls-encryption-endpoints | All public/private API endpoints enforce TLS; storage services enable encryption at rest | 100% compliant across resources | AWS Config rules + Terraform policy checks | Continuous (real-time) with CI enforcement on change | dev,int,ref,prod | dos-ingestion-api | draft | Aligns with NHS policy; Config provides continuous guardrails; CI blocks drift |

### SEC-004

Storage services show encryption enabled

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| storage-encryption-enabled | Storage services show encryption enabled | 100% storage resources encrypted at rest | AWS Config rules + Terraform policy checks | Continuous + CI enforcement | dev,int,ref,prod | dos-ingestion-api | draft | Guardrails ensure encryption at rest across services |

### SEC-005

Cross-environment data access attempts denied

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| cross-env-access-denied | Cross-env data access attempts denied and logged | 100% denial; audit logs prove enforcement | IAM policies + SCP guardrails + audit log queries | CI policy checks + monthly audit review | dev,int,ref,prod | dos-ingestion-api | draft | Prevents accidental or malicious cross-environment data access |

### SEC-006

No direct prod console queries detected in audit period

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| prod-console-access-audit | No direct prod console queries detected in audit period | 0 non-approved console queries in audit period | CloudTrail + SIEM audit queries | Weekly audit + alerting | prod | dos-ingestion-api | draft | Detects improper direct access to production consoles |

### SEC-007

SG rules audited; attempt broad ingress denied

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| sg-broad-ingress-denied | SG rules audited; attempt broad ingress denied | 0 broad (0.0.0.0/0) ingress on restricted ports | AWS Config + IaC linter | CI per change + monthly audit | dev,int,ref,prod | dos-ingestion-api | draft | Prevents risky network exposure via security groups |

### SEC-008

Perimeter scan shows no broad whitelist & secure channels

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| perimeter-scan | Perimeter scan shows no broad whitelist & secure channels | No broad whitelists; only secure channels reported | External perimeter scanner + config validation | Monthly + on change | int,ref,prod | dos-ingestion-api | draft | Confirms perimeter hygiene and secure external exposure |

### SEC-009

ASVS & CIS benchmark automation reports pass thresholds

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| cis-benchmark-compliance | CIS benchmark automation reports meet pass thresholds for targeted services | >= 95% controls passing; all high-severity findings remediated or exceptioned | CIS benchmark tooling integrated in CI and periodic audits | CI per change + monthly full audit | dev,int,ref,prod | dos-ingestion-api | draft | Baseline hardening validated continuously; monthly cadence catches drift |

### SEC-010

Annual pen test executed; remediation tickets raised & closed

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| annual-pentest | Annual pen test executed; remediation tickets raised & closed | Pen test executed; all critical findings remediated or exceptioned | Pen test reports + remediation tracking | Annual | prod | dos-ingestion-api | draft | Validates security posture with external testing and tracked remediation |

### SEC-012

IAM policy review confirms least privilege for system roles

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| iam-least-privilege | IAM policy review confirms least privilege for system roles | >= 95% policies compliant; no wildcard resource; explicit actions only | IAM Access Analyzer + policy linters | CI per change + quarterly audit | dev,int,ref,prod | dos-ingestion-api | draft | Continuous analysis prevents privilege creep; periodic review catches drift |

### SEC-013

Key rotation events logged; unauthorized access denied

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| key-rotation-logging | Key rotation events logged; unauthorized access denied | 100% rotation events logged; 0 unauthorized key access | KMS/AWS logs + SIEM correlation | Quarterly audit + CI checks on policy | dev,int,ref,prod | dos-ingestion-api | draft | Audit trail confirms rotation compliance and denial of unauthorized access |

### SEC-016

MFA enforced for all privileged infra roles

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| privileged-mfa-enforced | MFA enforced for all privileged infra roles | 100% privileged roles require MFA | IAM policy checks + directory audit | CI policy checks + quarterly audit | dev,int,ref,prod | dos-ingestion-api | draft | Strong authentication for privileged accounts reduces risk |

### SEC-017

Scan reports zero unmanaged long-lived credentials

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| zero-long-lived-credentials | Scan reports zero unmanaged long-lived credentials | 0 unmanaged long-lived credentials | Secret scanners + IAM credential report audit | CI per build + weekly audit | dev,int,ref,prod | dos-ingestion-api | draft | Reduces risk from forgotten credentials; continuous scanning plus scheduled audits |

### SEC-018

Supplier audit attestation stored & verified

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| supplier-audit-attestation | Supplier audit attestation stored & verified | Attestations current; verification completed | Supplier management system + evidence repository | Annual + on contract change | prod | dos-ingestion-api | draft | Ensures supplier compliance and auditable records |

### SEC-019

Segmentation test confirms tenant isolation

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| segmentation-tenant-isolation | Segmentation test confirms tenant isolation | 100% isolation; no cross-tenant data access observed | Segmentation test suite + log verification | Quarterly | int,ref,prod | dos-ingestion-api | draft | Ensures strict isolation between tenants per policy |

### SEC-021

Port scan matches approved diagnostic list only

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| port-scan-diagnostic-only | Port scan matches approved diagnostic list only | No unexpected open ports detected outside approved list | Automated port scan + baseline comparison | Monthly + CI smoke on infra changes | dev,int,ref,prod | dos-ingestion-api | draft | Detects misconfigurations; verifies adherence to diagnostic port policy |

### SEC-022

Utility program access restricted to approved roles

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| utility-access-restricted | Utility program access restricted to approved roles | Only approved roles can access utility programs | RBAC policy checks + audit logs | CI policy checks + monthly audit | dev,int,ref,prod | dos-ingestion-api | draft | Prevents misuse of diagnostic utilities |

### SEC-023

Deployment provenance shows unique traceable accounts

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| deployment-provenance-traceable | Deployment provenance shows unique traceable accounts | All deployments traceable to unique accounts | CI/CD audit trails + commit signing | Continuous | dev,int,ref,prod | dos-ingestion-api | draft | Ensures accountability and traceability for all deployments |

### SEC-024

Code/data transfer logs show integrity & secure channels

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| transfer-integrity-secure | Code/data transfer logs show integrity & secure channels | 100% transfers logged; integrity and secure channel verified | Checksums/signatures + TLS enforcement + audit logs | CI per change + weekly reviews | dev,int,ref,prod | dos-ingestion-api | draft | Validates integrity and secure transport for all transfers |

### SEC-027

Build fails on high CVE; report archived

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| high-cve-block | Build fails when high/critical CVEs detected in application or container dependencies | 0 unresolved High/Critical CVEs at release time | SCA scanner (e.g., OWASP Dependency-Check), container scanner, pipeline gate | CI per build + scheduled weekly scans | dev,int,ref | dos-ingestion-api | draft | Prevents introduction of known vulnerabilities; gate aligned to release quality |

### SEC-028

Release pipeline blocks on critical unresolved findings

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| release-block-critical-findings | Release pipeline blocks on critical unresolved findings | 0 critical unresolved findings prior to release | Pipeline gate integrated with SCA, container, IaC scanners | Per release | dev,int,ref | dos-ingestion-api | draft | Enforces remediation before release; gate consolidates multiple scanner outputs |

### SEC-030

Certificates and private keys stored only in approved encrypted secret stores; zero plain text exposure

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| cert-secure-storage | Certificate and private key material stored only in approved encrypted secret stores (KMS/Secrets Manager); zero plaintext in repos, images, build logs, or artifacts | 0 plaintext occurrences; 100% issuance & rotation actions use managed secrets; 100% scan coverage of git history and container layers | Secret scanning (git history + container layers), CI policy checks, artifact scanner, repo pre-commit hooks | CI per build + weekly full history & image layer scan | dev,int,ref,prod | dos-ingestion-api | draft | Prevents certificate/private key exposure by enforcing exclusive use of encrypted secret storage and continuous scanning |
