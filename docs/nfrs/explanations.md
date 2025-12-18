# FtRS NFR – Explanations

This page is auto-generated; do not hand-edit.

## Index by Domain

- Accessibility: [ACC-001](#acc-001), [ACC-002](#acc-002), [ACC-003](#acc-003), [ACC-004](#acc-004), [ACC-005](#acc-005), [ACC-006](#acc-006), [ACC-007](#acc-007), [ACC-008](#acc-008), [ACC-009](#acc-009), [ACC-010](#acc-010), [ACC-011](#acc-011), [ACC-012](#acc-012), [ACC-013](#acc-013), [ACC-014](#acc-014), [ACC-015](#acc-015), [ACC-016](#acc-016), [ACC-017](#acc-017), [ACC-018](#acc-018), [ACC-019](#acc-019), [ACC-020](#acc-020), [ACC-021](#acc-021), [ACC-022](#acc-022)
- Availability: [AVAIL-001](#avail-001), [AVAIL-002](#avail-002), [AVAIL-003](#avail-003), [AVAIL-004](#avail-004), [AVAIL-005](#avail-005), [AVAIL-006](#avail-006), [AVAIL-007](#avail-007), [AVAIL-008](#avail-008), [AVAIL-009](#avail-009), [AVAIL-010](#avail-010)
- Compatibility: [COMP-001](#comp-001), [COMP-002](#comp-002), [COMP-003](#comp-003)
- Cost: [COST-001](#cost-001), [COST-002](#cost-002), [COST-003](#cost-003), [COST-004](#cost-004), [COST-005](#cost-005), [COST-006](#cost-006), [COST-007](#cost-007)
- Governance: [GOV-001](#gov-001), [GOV-002](#gov-002), [GOV-003](#gov-003), [GOV-004](#gov-004), [GOV-005](#gov-005), [GOV-006](#gov-006), [GOV-007](#gov-007), [GOV-008](#gov-008), [GOV-009](#gov-009), [GOV-010](#gov-010), [GOV-011](#gov-011), [GOV-012](#gov-012), [GOV-013](#gov-013), [GOV-014](#gov-014), [GOV-015](#gov-015), [GOV-016](#gov-016)
- Interoperability: [INT-001](#int-001), [INT-002](#int-002), [INT-003](#int-003), [INT-004](#int-004), [INT-005](#int-005), [INT-006](#int-006), [INT-007](#int-007), [INT-008](#int-008), [INT-009](#int-009), [INT-010](#int-010), [INT-011](#int-011), [INT-012](#int-012), [INT-013](#int-013), [INT-014](#int-014), [INT-015](#int-015), [INT-016](#int-016), [INT-017](#int-017), [INT-018](#int-018)
- Observability: [OBS-001](#obs-001), [OBS-002](#obs-002), [OBS-003](#obs-003), [OBS-004](#obs-004), [OBS-005](#obs-005), [OBS-006](#obs-006), [OBS-007](#obs-007), [OBS-008](#obs-008), [OBS-009](#obs-009), [OBS-010](#obs-010), [OBS-011](#obs-011), [OBS-012](#obs-012), [OBS-013](#obs-013), [OBS-014](#obs-014), [OBS-015](#obs-015), [OBS-016](#obs-016), [OBS-017](#obs-017), [OBS-018](#obs-018), [OBS-019](#obs-019), [OBS-020](#obs-020), [OBS-021](#obs-021), [OBS-022](#obs-022), [OBS-023](#obs-023), [OBS-024](#obs-024), [OBS-025](#obs-025), [OBS-026](#obs-026), [OBS-027](#obs-027), [OBS-028](#obs-028), [OBS-029](#obs-029), [OBS-030](#obs-030), [OBS-031](#obs-031), [OBS-032](#obs-032), [OBS-033](#obs-033)
- Performance: [PERF-001](#perf-001), [PERF-002](#perf-002), [PERF-003](#perf-003), [PERF-004](#perf-004), [PERF-005](#perf-005), [PERF-006](#perf-006), [PERF-007](#perf-007), [PERF-008](#perf-008), [PERF-009](#perf-009), [PERF-010](#perf-010), [PERF-011](#perf-011), [PERF-012](#perf-012), [PERF-013](#perf-013)
- Reliability: [REL-001](#rel-001), [REL-002](#rel-002), [REL-003](#rel-003), [REL-004](#rel-004), [REL-005](#rel-005), [REL-006](#rel-006), [REL-007](#rel-007), [REL-008](#rel-008), [REL-009](#rel-009), [REL-010](#rel-010), [REL-011](#rel-011), [REL-012](#rel-012), [REL-013](#rel-013), [REL-014](#rel-014), [REL-015](#rel-015), [REL-016](#rel-016), [REL-017](#rel-017)
- Scalability: [SCAL-001](#scal-001), [SCAL-002](#scal-002), [SCAL-003](#scal-003), [SCAL-004](#scal-004), [SCAL-005](#scal-005), [SCAL-006](#scal-006), [SCAL-007](#scal-007), [SCAL-008](#scal-008), [SCAL-009](#scal-009), [SCAL-010](#scal-010)
- Security: [SEC-001](#sec-001), [SEC-002](#sec-002), [SEC-003](#sec-003), [SEC-004](#sec-004), [SEC-005](#sec-005), [SEC-006](#sec-006), [SEC-007](#sec-007), [SEC-008](#sec-008), [SEC-009](#sec-009), [SEC-010](#sec-010), [SEC-011](#sec-011), [SEC-012](#sec-012), [SEC-013](#sec-013), [SEC-014](#sec-014), [SEC-015](#sec-015), [SEC-016](#sec-016), [SEC-017](#sec-017), [SEC-018](#sec-018), [SEC-019](#sec-019), [SEC-020](#sec-020), [SEC-021](#sec-021), [SEC-022](#sec-022), [SEC-023](#sec-023), [SEC-024](#sec-024), [SEC-025](#sec-025), [SEC-026](#sec-026), [SEC-027](#sec-027), [SEC-028](#sec-028), [SEC-029](#sec-029), [SEC-030](#sec-030)

## Accessibility

### ACC-001

Product passes WCAG 2.2 AA via automated and manual audits.

### ACC-002

Automated scans run across critical pages and browser variants.

### ACC-003

Manual accessibility tests are executed for each release cycle.

### ACC-004

Accessibility defects tracked with equal priority and defined SLAs.

### ACC-005

Accessibility tooling operates correctly in dev, int, and reference environments.

### ACC-006

Assistive technologies are not blocked by headers or Content Security Policy (CSP).

### ACC-007

Test dataset covers common components: tables, forms, status messages.

### ACC-008

CI accessibility scan stage completes quickly (under target time).

### ACC-009

Keyboard-only navigation preserves logical tab order without traps.

### ACC-010

Focus handling works for modals and overlays without trapping user.

### ACC-011

Screen reader announces ARIA roles and states correctly.

### ACC-012

Accessibility results are documented alongside feature tests.

### ACC-013

Centralised accessibility issue log is maintained and current.

### ACC-014

Active champion or workgroup drives accessibility practice.

### ACC-015

Monthly accessibility report is published for stakeholders.

### ACC-016

Exception process for accessibility deviations is documented.

### ACC-017

Exception records include required fields (impact, mitigation, expiry).

### ACC-018

Pre-commit accessibility checks finish within target duration.

### ACC-019

CI accessibility stage completes within target time window.

### ACC-020

Overnight full scan finishes under defined maximum duration.

### ACC-021

Regression in accessibility triggers automated alert.

### ACC-022

False positive ratio is measured and trending toward improvement.

## Availability

### AVAIL-001

Multi-AZ deployment achieves target uptime (e.g., ≥99.90%).

### AVAIL-002

Disaster recovery (DR) simulation meets documented objectives.

### AVAIL-003

Continuous uptime monitoring covers 24x7 operations.

### AVAIL-004

Maintenance windows stay within monthly and per-event minute limits.

### AVAIL-005

Scheduled maintenance executes successfully with passing smoke tests afterward.

### AVAIL-006

DR exercise restores service within target recovery time (< defined hours).

### AVAIL-007

Data replication lag remains under target ensuring minimal failover delta.

### AVAIL-008

API uptime aligns with overall service availability target.

### AVAIL-009

Access from non-approved geographic regions is blocked and logged.

### AVAIL-010

Blue/green deployments complete with zero failed user requests.

## Compatibility

### COMP-001

Supported OS/browser list matches published specification.

### COMP-002

Multi-factor authentication (CIS2) works across supported platforms.

### COMP-003

Critical user journeys pass across all supported platforms at target success rate.

## Cost

### COST-001

All resources have mandatory cost tags for allocation and reporting.

### COST-002

Monthly cost review identifies anomalies and tracks actions.

### COST-003

Each team infra engineer has access to cost analysis tooling (e.g., CloudHealth).

### COST-004

Optimisation and tag compliance reports are produced and reviewed.

### COST-005

Budgets and cost alert notifications are configured and tested.

### COST-006

Dedicated cost alerts channel receives test and live notifications.

### COST-007

Quarterly cost reviews record minutes and follow-up actions.

## Governance

### GOV-001

Service Management pre-live acceptance is signed off before go-live.

### GOV-002

Well-Architected review completed; remediation actions closed.

### GOV-003

Solution Architecture Framework assessment is approved.

### GOV-004

Engineering red-lines compliance checklist is signed.

### GOV-005

GDPR compliance assessment signed by Information Governance.

### GOV-006

Statement confirming service is out of scope for Medical Device regulation.

### GOV-007

Architecture review and approval logged by FtRS architects.

### GOV-008

Cloud expert deployment approval documented (infrastructure readiness).

### GOV-009

Solution Assurance approval ticket is closed.

### GOV-010

Clinical Safety assurance approval recorded.

### GOV-011

Information Governance approval recorded.

### GOV-012

Technical Review Group (TRG) approval outcome documented.

### GOV-013

Senior Information Risk Owner (SIRO) sign-off obtained.

### GOV-014

Caldicott Guardian approval recorded for data handling.

### GOV-015

DUEC Assurance Board acceptance logged.

### GOV-016

Live Services Board go-live approval recorded.

## Interoperability

### INT-001

Resources conform to UK Core profiles ensuring national standard alignment.

### INT-002

Versioning and deprecation policy is published for integrators.

### INT-003

Minor releases must remain backward compatible for consumers. Deprecations are announced
in a minor release and not removed within the same major. Removal happens at the next
major release and never earlier than 12 months after the first deprecation notice
(whichever is later).

Why this matters:
- Protects integrators from frequent breaking changes tied to team release cadence.
- Guarantees a clear minimum adaptation window that spans typical annual planning cycles.
- Keeps policy consumer-centric while still allowing evolution at major boundaries.

Acceptance (evidence we expect to see):
- Contract compatibility tests pass for supported minor versions in CI and at release review.
- A deprecation ledger records first-notice date, affected fields/endpoints, and planned removal version.
- Release notes include deprecations with migration guidance and timelines.
- A CI gate prevents breaking changes in minor releases unless an approved exception is recorded.

Exceptions:
- Rare, pre-approved, and documented with consumer sign-off; mitigations and timelines included.

### INT-004

Semantic mappings preserve meaning when round-tripped between formats.

### INT-005

Error responses follow standard OperationOutcome structure.

### INT-006

Identifiers are normalised (case, trimming) for consistent matching.

### INT-007

Strict content negotiation enforces supported media types only.

### INT-008

Reference data synchronises within defined latency (e.g., ≤24h).

### INT-009

Only documented FHIR search parameters are accepted; unknown ones rejected.

### INT-010

Integration contract is version-controlled and published.

### INT-011

Machine-readable changelog is generated for each release.

### INT-012

Terminology bindings are validated to ensure correct coding.

### INT-013

Correlation IDs persist across internal and external calls for tracing.

### INT-014

Null vs absent data semantics follow FHIR specification rules.

### INT-015

Test coverage spans ≥90% of defined interoperability scenarios.

### INT-016

Operations are stateless and do not rely on sequence order.

### INT-017

Input validation covers every field on every request to prevent malformed data.

### INT-018

Comprehensive OpenAPI documentation is published (overview, audience, related APIs, roadmap, SLA, tech stack, security/auth, test environment, onboarding, endpoints with examples) to support integrator adoption.

## Observability

### OBS-001

Application and infrastructure health panels display green status during normal operation.

### OBS-002

Authenticated remote health dashboard is accessible to support teams.

### OBS-003

Health events appear on dashboards shortly after failures (within target freshness).

### OBS-004

Automated maintenance tasks run successfully with no manual intervention required.

### OBS-005

Layered performance metrics (app, DB, cache) are visible.

### OBS-006

Remote performance dashboard mirrors local environment metrics accurately.

### OBS-007

Performance metrics latency (ingest to display) stays within defined limit (e.g., ≤60s).

### OBS-008

Per-endpoint transactions per second (TPS) are displayed with alert thresholds.

### OBS-009

Latency histograms show p50/p95/p99 for each endpoint.

### OBS-010

Aggregate latency panel roll-ups remain within acceptable accuracy margin (e.g., ≤2%).

### OBS-011

Failure types are logged and classified for reporting.

### OBS-012

Error rate metric and alert exist to highlight reliability issues.

### OBS-013

Infrastructure logs return expected structured fields for queries.

### OBS-014

Infrastructure log entries include required contextual fields (e.g., IDs, timestamps).

### OBS-015

Log retention policy is enforced and reported.

### OBS-016

Security/event forwarding to SIEM delivers test events within freshness target.

### OBS-017

All log levels are supported and can be changed dynamically.

### OBS-018

Log level changes propagate quickly (under defined minutes) with alert if breach.

### OBS-019

Operational logs allow full transaction chain reconstruction.

### OBS-020

Operations logs reconstruct workflow sequences accurately.

### OBS-021

Operational events include a transaction identifier for correlation.

### OBS-022

Audit trail can reconstruct a specific user action sequence.

### OBS-023

Audit events share transaction IDs and ordered timestamps for traceability.

### OBS-024

Alert rules trigger multi-channel notifications (e.g., chat + email).

### OBS-025

Alerts delivered with sufficient context to act (multi-channel).

### OBS-026

Analytics queries identify usage patterns from captured metrics.

### OBS-027

Analytics outages do not impact core transaction processing.

### OBS-028

Role-based access control (RBAC) restricts dashboard sections appropriately.

### OBS-029

Dashboard freshness age remains under target (e.g., ≤60s).

### OBS-030

Distributed tracing spans cover end-to-end request path.

### OBS-031

Anonymised behavioural metrics are collected without exposing personal identifiers.

### OBS-032

Per-endpoint 4xx and 5xx response metrics are captured with alert thresholds so error rate spikes are detected and acted upon quickly.

### OBS-033

Unauthorized API access attempts (failed authentication, forbidden operations, rate limit breaches, anomalous spikes) are logged with required context and generate timely alerts for early detection of credential misuse or attack patterns.

## Performance

### PERF-001

Each API or batch operation meets agreed median and 95th percentile latency targets.

### PERF-002

Performance pillar checklist is completed and any actions are closed.

### PERF-003

The versioned performance expectations table is maintained and referenced by tests.

### PERF-004

A representative, anonymised dataset exists for realistic performance validation.

### PERF-005

Automated performance tests implement all defined actions and listed exclusions.

### PERF-006

Batch window latency stays within a small variance (e.g., p95 delta ≤ defined %).

### PERF-007

Telemetry overhead (CPU, latency) remains within acceptable limits while capturing required data.

### PERF-008

Rolling window performance variance remains stable within target percentage bounds.

### PERF-009

Alerting triggers when p95 latency regresses beyond the defined threshold (e.g., >10%).

### PERF-010

Documented percentile methodology matches tool configuration (consistent measurement).

### PERF-011

GP search endpoints handle short burst throughput at or above the target TPS.

### PERF-012

GP search endpoints sustain steady-state throughput at or above the TPS target.

### PERF-013

Endpoint request payloads remain under the maximum defined size to protect performance.

## Reliability

### REL-001

Service remains healthy across multiple availability zones with verified health checks.

### REL-002

Simulated AZ failure does not interrupt service delivery.

### REL-003

Lifecycle reliability checklist is completed for the service components.

### REL-004

Denial-of-service (DoS) simulation shows successful mitigation and continued responsiveness.

### REL-005

Injection attacks are blocked, preventing arbitrary code execution attempts.

### REL-006

Resource placement scan shows no forbidden co-residency (e.g., sensitive + public workloads).

### REL-007

Brute force or auth anomaly attempts are rate limited and create alerts.

### REL-008

Man-in-the-middle (MITM) attempts fail due to secure certificate pinning.

### REL-009

UI prevents iframe embedding (clickjacking) via secure headers.

### REL-010

Pausing and resuming batch jobs does not corrupt or lose data.

### REL-011

Unhealthy nodes are automatically replaced with workload continuity.

### REL-012

Removing a single node yields no data loss and minimal performance impact.

### REL-013

Tier failure triggers graceful degradation and later clean recovery.

### REL-014

External dependency outage invokes fallback and clear user messaging.

### REL-015

Load balancer failure preserves sessions and maintains routing continuity.

### REL-016

Server error paths show expected logout or user messaging per specification.

### REL-017

Restore drills meet RPO/RTO targets and confirm ransomware defenses.

## Scalability

### SCAL-001

Horizontal scaling increases throughput nearly linearly without quality loss.

### SCAL-002

Vertical resizing (bigger instance) retains data and operation with no downtime.

### SCAL-003

All layers (app, DB, cache) meet defined scalability checklist items.

### SCAL-004

Scale-down only occurs after sustained low utilisation (not transient dips).

### SCAL-005

Autoscaling policy simulations trigger controlled scaling actions.

### SCAL-006

Scaling events do not cause SLA breaches in latency or error rate.

### SCAL-007

Capacity planning shows adequate headroom (e.g., ≥30%).

### SCAL-008

During the variance period no manual scaling tickets are needed.

### SCAL-009

Audit logs record who initiated scaling and why.

### SCAL-010

Predictive alerts fire before utilisation reaches critical thresholds.

## Security

### SEC-001

Use only strong, approved cryptographic algorithms; weak or deprecated ciphers are blocked.

### SEC-002

Complete the AWS/WAF security pillar checklist and track remediation actions for any gaps.

### SEC-003

All service endpoints enforce TLS and all stored data (databases, buckets) is encrypted at rest.

### SEC-004

Every storage service (S3, RDS, etc.) shows encryption enabled with managed or customer keys.

### SEC-005

Strict environment isolation: data access from one environment to another is prevented.

### SEC-006

No direct production console queries by engineers outside approved, audited break-glass processes.

### SEC-007

Network security groups allow only narrowly scoped inbound rules; broad ingress is denied.

### SEC-008

Perimeter scans show secure transport, no open broad whitelists, and hardened edge configuration.

### SEC-009

Automated ASVS and CIS benchmark scans meet pass thresholds; failures trigger remediation.

### SEC-010

Annual penetration test completed; identified issues tracked and closed.

### SEC-011

Enabling security controls does not push latency beyond defined SLAs.

### SEC-012

IAM roles and policies grant least privilege; periodic reviews confirm minimal access.

### SEC-013

Cryptographic keys rotate on schedule and unauthorized access attempts are rejected and logged.

### SEC-014

Mutual TLS (mTLS) succeeds between designated internal services to protect sensitive flows.

### SEC-015

Certificate expiry is detected in advance; renewal occurs without downtime.

### SEC-016

Privileged infrastructure roles require multi-factor authentication (MFA).

### SEC-017

No long-lived unmanaged credentials; periodic scans confirm only managed secrets exist.

### SEC-018

Third-party supplier security attestation is collected and stored for audit.

### SEC-019

Tenant or data segmentation tests confirm isolation boundaries hold.

### SEC-020

Remote connections present valid certificates from trusted authorities.

### SEC-021

Port scans reveal only approved diagnostic and service ports—no unexpected exposures.

### SEC-022

Access to powerful utility programs is restricted to approved roles.

### SEC-023

Deployment provenance shows traceable unique accounts per automated pipeline stage.

### SEC-024

Transfer of code or data maintains integrity and uses secure channels; events are logged.

### SEC-025

Requests containing identifiable patient data enforce mTLS; plaintext attempts are blocked.

### SEC-026

API responses never include unencrypted patient identifiable data (PID) fields.

### SEC-027

Build pipeline blocks release when critical CVEs exceed threshold; reports archived.

### SEC-028

Releases are halted if critical unresolved security findings remain.

### SEC-029

All API endpoints enforce CIS2 JWT authentication with signature, issuer, audience and required assurance claim validation; invalid or missing tokens are rejected with structured errors.

### SEC-030

Certificates and private keys are stored only in approved encrypted secret stores (e.g., Secrets Manager/KMS) with zero plaintext exposure across repositories, images, logs, or build artifacts; continuous scanning enforces compliance.
