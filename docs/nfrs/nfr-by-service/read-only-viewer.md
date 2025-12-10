# FtRS NFR – Service: read-only-viewer

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Accessibility | ACC-001 | WCAG 2.2 AA scan & manual audit pass | Product passes WCAG 2.2 AA via automated and manual audits. | STORY-ACC-001 |
| Accessibility | ACC-002 | Automated scans run across critical pages & browsers | Automated scans run across critical pages and browser variants. | STORY-ACC-002 |
| Accessibility | ACC-003 | Manual accessibility test executed per release | Manual accessibility tests are executed for each release cycle. | STORY-ACC-003 |
| Accessibility | ACC-004 | Defects tracked with parity priority & SLA | Accessibility defects tracked with equal priority and defined SLAs. | STORY-ACC-004 |
| Accessibility | ACC-005 | Tooling operational in dev/int/reference envs | Accessibility tooling operates correctly in dev, int, and reference environments. | STORY-ACC-005 |
| Accessibility | ACC-006 | Assistive tech not blocked by headers/CSP | Assistive technologies are not blocked by headers or Content Security Policy (CSP). | STORY-ACC-006 |
| Accessibility | ACC-007 | Test dataset covers tables/forms/status messages | Test dataset covers common components: tables, forms, status messages. | STORY-ACC-007 |
| Accessibility | ACC-008 | CI accessibility stage completes <5min | CI accessibility scan stage completes quickly (under target time). | STORY-ACC-008 |
| Accessibility | ACC-009 | Keyboard tab order regression test passes | Keyboard-only navigation preserves logical tab order without traps. | STORY-ACC-003, STORY-ACC-009 |
| Accessibility | ACC-010 | Focus trap tests pass for modals/overlays | Focus handling works for modals and overlays without trapping user. | STORY-ACC-004, STORY-ACC-010 |
| Accessibility | ACC-011 | Screen reader ARIA role announcements verified | Screen reader announces ARIA roles and states correctly. | STORY-ACC-011 |
| Accessibility | ACC-012 | Accessibility results documented with feature tests | Accessibility results are documented alongside feature tests. | STORY-ACC-012 |
| Accessibility | ACC-013 | Central issue log maintained & current | Centralised accessibility issue log is maintained and current. | STORY-ACC-013 |
| Accessibility | ACC-014 | Accessibility champion/workgroup active | Active champion or workgroup drives accessibility practice. | STORY-ACC-014 |
| Accessibility | ACC-015 | Monthly accessibility report published | Monthly accessibility report is published for stakeholders. | STORY-ACC-005, STORY-ACC-015 |
| Accessibility | ACC-016 | Exception process documented & used | Exception process for accessibility deviations is documented. | STORY-ACC-016 |
| Accessibility | ACC-017 | Exception record contains required fields | Exception records include required fields (impact, mitigation, expiry). | STORY-ACC-017 |
| Accessibility | ACC-018 | Pre-commit checks complete <30s | Pre-commit accessibility checks finish within target duration. | STORY-ACC-018 |
| Accessibility | ACC-019 | CI accessibility stage completes <5min | CI accessibility stage completes within target time window. | STORY-ACC-019 |
| Accessibility | ACC-020 | Overnight full scan duration <2h | Overnight full scan finishes under defined maximum duration. | STORY-ACC-020 |
| Accessibility | ACC-021 | Accessibility regression triggers alert | Regression in accessibility triggers automated alert. | STORY-ACC-021 |
| Accessibility | ACC-022 | False positive ratio report shows improvement | False positive ratio is measured and trending toward improvement. | STORY-ACC-022 |
| Compatibility | COMP-001 | Published OS/browser list matches warranted spec | Supported OS/browser list matches published specification. | STORY-COMP-001, STORY-COMP-004 |
| Compatibility | COMP-002 | MFA (CIS2) succeeds across supported platforms | Multi-factor authentication (CIS2) works across supported platforms. | STORY-COMP-002, STORY-COMP-005 |
| Compatibility | COMP-003 | ≥90% critical journeys test pass per platform | Critical user journeys pass across all supported platforms at target success rate. | STORY-COMP-003, STORY-COMP-006 |
| Cost | COST-001 | Mandatory tagging set present on 100% resources | All resources have mandatory cost tags for allocation and reporting. | STORY-COST-001 |
| Cost | COST-002 | Monthly Cost Explorer review & anomaly log | Monthly cost review identifies anomalies and tracks actions. | STORY-COST-002 |
| Cost | COST-003 | CloudHealth access for each team infra engineer | Each team infra engineer has access to cost analysis tooling (e.g., CloudHealth). | STORY-COST-003 |
| Cost | COST-004 | CloudHealth optimisation & tag compliance reports | Optimisation and tag compliance reports are produced and reviewed. | STORY-COST-004 |
| Cost | COST-005 | Budgets & alert notifications configured & tested | Budgets and cost alert notifications are configured and tested. | STORY-COST-005 |
| Cost | COST-006 | #ftrs-cost-alerts channel created & receiving test alerts | Dedicated cost alerts channel receives test and live notifications. | STORY-COST-006 |
| Cost | COST-007 | Quarterly cost review minutes & tracked actions | Quarterly cost reviews record minutes and follow-up actions. | STORY-COST-007 |
| Governance | GOV-004 | Engineering Red-lines compliance checklist signed | Engineering red-lines compliance checklist is signed. | STORY-GOV-004 |
| Observability | OBS-001 | App & infra health panels show green | Application and infrastructure health panels display green status during normal operation. | STORY-OBS-001 |
| Observability | OBS-007 | Performance metrics latency ≤60s | Performance metrics latency (ingest to display) stays within defined limit (e.g., ≤60s). | STORY-OBS-002 |
| Observability | OBS-033 | Unauthorized API access attempts logged, classified, alerted | Unauthorized API access attempts (failed authentication, forbidden operations, rate limit breaches, anomalous spikes) are logged with required context and generate timely alerts for early detection of credential misuse or attack patterns. | [FTRS-1607](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1607) |
| Reliability | REL-007 | Brute force/auth anomalies rate limited & alerted (peak 500 TPS burst capacity; rate limits + alerts) | Brute force or auth anomaly attempts are rate limited and create alerts. | STORY-REL-005 |
| Reliability | REL-009 | Iframe embed blocked; headers verified | UI prevents iframe embedding (clickjacking) via secure headers. | STORY-REL-023 |
| Reliability | REL-016 | Server error shows logout/message per spec | Server error paths show expected logout or user messaging per specification. | STORY-REL-016 |
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
| Security | SEC-012 | IAM policy review confirms least privilege for system roles | IAM roles and policies grant least privilege; periodic reviews confirm minimal access. | STORY-SEC-005, STORY-SEC-030, STORY-SEC-039 |
| Security | SEC-013 | Key rotation events logged; unauthorized access denied | Cryptographic keys rotate on schedule and unauthorized access attempts are rejected and logged. | STORY-SEC-021, STORY-SEC-040 |
| Security | SEC-016 | MFA enforced for all privileged infra roles | Privileged infrastructure roles require multi-factor authentication (MFA). | STORY-SEC-023 |
| Security | SEC-017 | Scan reports zero unmanaged long-lived credentials | No long-lived unmanaged credentials; periodic scans confirm only managed secrets exist. | STORY-SEC-010, STORY-SEC-041 |
| Security | SEC-018 | Supplier audit attestation stored & verified | Third-party supplier security attestation is collected and stored for audit. | STORY-SEC-024, STORY-SEC-042 |
| Security | SEC-019 | Segmentation test confirms tenant isolation | Tenant or data segmentation tests confirm isolation boundaries hold. | STORY-SEC-012, STORY-SEC-043 |
| Security | SEC-021 | Port scan matches approved diagnostic list only | Port scans reveal only approved diagnostic and service ports—no unexpected exposures. | STORY-SEC-008, STORY-SEC-045 |
| Security | SEC-022 | Utility program access restricted to approved roles | Access to powerful utility programs is restricted to approved roles. | STORY-SEC-025, STORY-SEC-046 |
| Security | SEC-023 | Deployment provenance shows unique traceable accounts | Deployment provenance shows traceable unique accounts per automated pipeline stage. | STORY-SEC-026, STORY-SEC-047 |
| Security | SEC-024 | Code/data transfer logs show integrity & secure channels | Transfer of code or data maintains integrity and uses secure channels; events are logged. | STORY-SEC-027, STORY-SEC-048 |
| Security | SEC-027 | Build fails on high CVE; report archived | Build pipeline blocks release when critical CVEs exceed threshold; reports archived. | STORY-SEC-002 |
| Security | SEC-028 | Release pipeline blocks on critical unresolved findings | Releases are halted if critical unresolved security findings remain. | STORY-SEC-009, STORY-SEC-050 |
| Security | SEC-029 | All API endpoints enforce CIS2 JWT authentication (signature, issuer, audience, assurance claims) | All API endpoints enforce CIS2 JWT authentication with signature, issuer, audience and required assurance claim validation; invalid or missing tokens are rejected with structured errors. | [FTRS-1593](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1593) |
| Security | SEC-030 | Certificates and private keys stored only in approved encrypted secret stores; zero plain text exposure | Certificates and private keys are stored only in approved encrypted secret stores (e.g., Secrets Manager/KMS) with zero plaintext exposure across repositories, images, logs, or build artifacts; continuous scanning enforces compliance. | STORY-SEC-030 |

## Operations

No performance operations defined for this service.

## Controls

### ACC-001

WCAG 2.2 AA scan & manual audit pass

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| wcag-aa-pass | WCAG 2.2 AA scan & manual audit pass | Automated AA scan passes; manual audit issues triaged and resolved | Accessibility scanner + manual audit checklist | Quarterly + pre-release | int,ref | read-only-viewer | draft | Ensures accessibility conformance for UI surfaces |

### ACC-002

Automated scans run across critical pages & browsers

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| automated-scans-coverage | Automated scans run across critical pages & browsers | Critical pages covered across supported browsers | CI accessibility suite + cross-browser runners | CI per build | int,ref | read-only-viewer | draft | Automated checks catch regressions early |

### ACC-003

Manual accessibility test executed per release

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| manual-accessibility-test | Manual accessibility test executed per release | Release includes manual accessibility audit; issues triaged within 5 business days | Manual checklist + report | Per release | ref | read-only-viewer | draft | Ensures human validation beyond automation |

### ACC-004

Defects tracked with parity priority & SLA

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| accessibility-defect-sla | Defects tracked with parity priority & SLA | Accessibility defects use same priority/SLA scheme; monthly compliance report | Issue tracker + SLA report | Monthly | int,ref | read-only-viewer | draft | Enforces parity with functional defects |

### ACC-005

Tooling operational in dev/int/reference envs

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| accessibility-tooling-operational | Tooling operational in dev/int/reference envs | CI scanners and browser runners functional in dev/int/ref | CI accessibility suite | CI per build | dev,int,ref | read-only-viewer | draft | Guarantees tooling readiness across envs |

### ACC-006

Assistive tech not blocked by headers/CSP

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| assistive-tech-headers-csp | Assistive tech not blocked by headers/CSP | Headers/CSP allow screen readers; tests pass for supported AT | AT test harness + response header checks | Pre-release | ref | read-only-viewer | draft | Prevents accidental blocking via security headers |

### ACC-007

Test dataset covers tables/forms/status messages

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| accessibility-test-dataset-coverage | Test dataset covers tables/forms/status messages | Dataset includes representative components; annual review | Dataset repo + checklist | Annual | int | read-only-viewer | draft | Ensures coverage of common interactive components |

### ACC-008

CI accessibility stage completes <5min

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| ci-accessibility-duration | CI accessibility stage completes <5min | CI accessibility job completes < 5 minutes | CI job timer | CI per build | int | read-only-viewer | draft | Keeps pipeline fast while ensuring checks |

### ACC-009

Keyboard tab order regression test passes

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| keyboard-tab-order | Keyboard tab order regression test passes | Tab order matches expected flow; no focus loss | Automated tab order tests + manual verification | CI per build + pre-release | int,ref | read-only-viewer | draft | Supports keyboard-only navigation |

### ACC-010

Focus trap tests pass for modals/overlays

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| focus-trap-tests | Focus trap tests pass for modals/overlays | No escape from focus trap; correct focus restoration | Automated focus tests + manual checks | CI per build + pre-release | int,ref | read-only-viewer | draft | Ensures accessible modal behaviour |

### ACC-011

Screen reader ARIA role announcements verified

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| aria-role-announcements | Screen reader ARIA role announcements verified | ARIA roles/states announced correctly across key flows | Screen reader scripts + audit | Quarterly | ref | read-only-viewer | draft | Validates semantic accessibility |

### ACC-012

Accessibility results documented with feature tests

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| accessibility-results-documented | Accessibility results documented with feature tests | Docs stored with tests; updated on change | Test reports + docs repo | CI per build | int | read-only-viewer | draft | Maintains traceable evidence |

### ACC-013

Central issue log maintained & current

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| accessibility-issue-log-current | Central issue log maintained & current | Log updated within 5 business days of finding; monthly review | Issue tracker + report | Monthly | int | read-only-viewer | draft | Ensures visibility of accessibility work |

### ACC-014

Accessibility champion/workgroup active

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| accessibility-champion-active | Accessibility champion/workgroup active | Named champion/workgroup; quarterly minutes published | Meeting notes + tracker | Quarterly | int | read-only-viewer | draft | Sustains practice through leadership |

### ACC-015

Monthly accessibility report published

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| monthly-accessibility-report | Monthly accessibility report published | Report produced and published monthly with tracked actions | Reporting automation + issue tracker | Monthly | int,ref | read-only-viewer | draft | Maintains visibility and accountability |

### ACC-016

Exception process documented & used

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| accessibility-exception-process | Exception process documented & used | Exceptions recorded with impact, mitigation, expiry; reviewed monthly | Exception log | Monthly | int | read-only-viewer | draft | Manages deviations responsibly |

### ACC-017

Exception record contains required fields

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| accessibility-exception-record-fields | Exception record contains required fields | 100% exceptions include fields; expiry monitored | Exception log + report | Monthly | int | read-only-viewer | draft | Ensures actionable exception management |

### ACC-018

Pre-commit checks complete <30s

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| precommit-accessibility-duration | Pre-commit checks complete <30s | Pre-commit accessibility checks complete < 30s | Pre-commit runner | On commit | dev | read-only-viewer | draft | Keeps local workflow efficient |

### ACC-019

CI accessibility stage completes <5min

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| ci-accessibility-duration-policy | CI accessibility stage completes <5min | CI job < 5 minutes; breaches trigger optimisation ticket | CI timer + policy | CI per build | int | read-only-viewer | draft | Enforces pipeline performance policy |

### ACC-020

Overnight full scan duration <2h

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| overnight-scan-duration | Overnight full scan duration <2h | Full scan completes < 2 hours | Scan scheduler + timer | Nightly | int | read-only-viewer | draft | Keeps nightly checks practical |

### ACC-021

Accessibility regression triggers alert

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| accessibility-regression-alert | Accessibility regression triggers alert | Alert fires on score drop or new critical issue | Accessibility scanner + alerting | CI per build | int | read-only-viewer | draft | Fast feedback on regressions |

### ACC-022

False positive ratio report shows improvement

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| accessibility-false-positive-ratio | False positive ratio report shows improvement | False positive ratio decreasing quarter over quarter | Scanner report + trend analysis | Quarterly | int | read-only-viewer | draft | Improves signal quality of automated scans |

### COMP-001

Published OS/browser list matches warranted spec

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| published-supported-platforms | Published OS/browser list matches warranted spec | Supported platform list published and current | Documentation repo + review checklist | Quarterly | prod | read-only-viewer | draft | Sets clear compatibility expectations for users |

### COMP-002

MFA (CIS2) succeeds across supported platforms

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| mfa-platforms | MFA (CIS2) succeeds across supported platforms | MFA journeys pass across supported platforms | Cross-platform test suite + identity provider logs | Release cycle | int,ref,prod | read-only-viewer | draft | Ensures authentication compatibility |

### COMP-003

≥90% critical journeys test pass per platform

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| journeys-pass-rate | ≥90% critical journeys test pass per platform | >= 90% pass rate for critical journeys on each supported platform | Cross-platform automated E2E tests | CI per build + release candidate validation | int,ref | read-only-viewer | draft | Protects user experience across platforms |

### COST-001

Mandatory tagging set present on 100% resources

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| mandatory-tagging | Mandatory tagging set present on 100% resources | 100% resources carry mandatory tags | AWS Config rules + tag audit automation | Continuous + monthly report | dev,int,ref,prod | read-only-viewer | draft | Enables cost visibility and accountability |

### COST-002

Monthly Cost Explorer review & anomaly log

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| monthly-cost-review | Monthly Cost Explorer review & anomaly log | Review completed; anomalies logged with actions | Cost Explorer + anomaly detection | Monthly | prod | read-only-viewer | draft | Ensures proactive cost management |

### COST-003

CloudHealth access for each team infra engineer

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| cloudhealth-access | CloudHealth access for each team infra engineer | Access provisioned; onboarding verified | CloudHealth admin + access logs | Quarterly verification | prod | read-only-viewer | draft | Ensures teams can act on cost insights |

### COST-004

CloudHealth optimisation & tag compliance reports

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| optimisation-reports | CloudHealth optimisation & tag compliance reports | Reports generated; tracked actions created | CloudHealth reporting + tracker | Monthly | prod | read-only-viewer | draft | Drives optimisation and tag hygiene |

### COST-005

Budgets & alert notifications configured & tested

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| budgets-and-alerts | Budgets & alert notifications configured & tested | Budgets configured; alerts tested successfully | AWS Budgets + notifications | Quarterly + pre-fiscal review | prod | read-only-viewer | draft | Prevents cost overruns via alerting |

### GOV-004

Engineering Red-lines compliance checklist signed

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| nhs-github-enterprise-repos | All FtRS code repositories are hosted in NHS GitHub Enterprise and comply with securing-repositories policy; engineering dashboards show compliance | 100% repositories on NHS GitHub Enterprise; 100% securing-repositories checks passing; exceptions recorded with owner and review date | Enterprise repository policy audit + engineering compliance dashboards + CI checks | Continuous (CI on change) + quarterly governance review | dev,int,ref,prod | read-only-viewer | draft | Enforces organisational SDLC-1 Red Line for using NHS GitHub Enterprise and securing repositories; provides traceable evidence and automated verification |

### OBS-001

App & infra health panels show green

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| health-panels-green | App & infra health panels show green | All critical panels green; no stale data | Health checks + dashboard status API | Continuous + CI verification on change | int,ref,prod | read-only-viewer | draft | Ensures at-a-glance service health visibility |

### OBS-007

Performance metrics latency ≤60s

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| perf-metrics-latency | Performance metrics latency ≤60s | Metrics pipeline delivers data within 60s latency | Metrics agent + ingestion SLA alerting | Continuous monitoring | int,ref,prod | read-only-viewer | draft | Fresh metrics are required for accurate operational decisions |

### OBS-033

Unauthorized API access attempts logged, classified, alerted

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| unauth-access-monitoring | Unauthorized API access attempts logged & alerted with context | 100% auth failures & forbidden requests produce structured log entry with reason, correlation_id, source_ip, user_agent; alert triggers on >5 failed auth attempts per principal per 1m or anomaly spike (>3x baseline) | API gateway logs, auth middleware, metrics backend, alerting rules, anomaly detection job | Continuous collection + weekly anomaly review + monthly rule tuning | int,ref,prod | read-only-viewer | draft | Early detection of credential stuffing, token misuse, and privilege escalation attempts |

### REL-007

Brute force/auth anomalies rate limited & alerted (peak 500 TPS burst capacity; rate limits + alerts)

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| auth-brute-force-protection | Brute force/auth anomalies rate limited & alerted (peak 500 TPS legitimate burst supported) | Peak 500 TPS legitimate auth unaffected; anomalies blocked; alert ≤30s; ≤1% false positives | Auth gateway rate limiter + anomaly aggregator + performance harness + alerting | Continuous runtime enforcement + daily compliance script | dev,int,ref,prod | read-only-viewer | draft | Protects availability & integrity under authentication attack patterns |

### REL-016

Server error shows logout/message per spec

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| server-error-user-messaging | Server error shows logout/message per spec | Error paths conform to spec; correct logout/message; audit evidence across endpoints | Contract tests + UI behaviour checks + logs | CI per build + monthly audit | int,ref,prod | read-only-viewer | draft | Protects user experience during server errors |

### SEC-001

Crypto algorithms conform; weak ciphers rejected

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| crypto-cipher-policy | Crypto algorithms conform; weak ciphers rejected | TLS1.2+ only; no weak/legacy ciphers enabled | TLS scanner + configuration policy checks | CI per change + monthly scan | dev,int,ref,prod | read-only-viewer | draft | Enforces modern TLS standards; automated scans detect drift |

### SEC-002

WAF security pillar checklist completed & gaps tracked

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| waf-pillar-checklist | WAF security pillar checklist completed & gaps tracked | Checklist complete; 100% actions tracked; 0 open critical gaps | WAF checklist repository + issue tracker gate | Quarterly + on change | dev,int,ref,prod | read-only-viewer | draft | Formalizes WAF security governance; gaps tracked to closure |

### SEC-003

All endpoints TLS only; storage encryption enabled

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| tls-encryption-endpoints | All public/private API endpoints enforce TLS; storage services enable encryption at rest | 100% compliant across resources | AWS Config rules + Terraform policy checks | Continuous (real-time) with CI enforcement on change | dev,int,ref,prod | read-only-viewer | draft | Aligns with NHS policy; Config provides continuous guardrails; CI blocks drift |

### SEC-004

Storage services show encryption enabled

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| storage-encryption-enabled | Storage services show encryption enabled | 100% storage resources encrypted at rest | AWS Config rules + Terraform policy checks | Continuous + CI enforcement | dev,int,ref,prod | read-only-viewer | draft | Guardrails ensure encryption at rest across services |

### SEC-005

Cross-environment data access attempts denied

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| cross-env-access-denied | Cross-env data access attempts denied and logged | 100% denial; audit logs prove enforcement | IAM policies + SCP guardrails + audit log queries | CI policy checks + monthly audit review | dev,int,ref,prod | read-only-viewer | draft | Prevents accidental or malicious cross-environment data access |

### SEC-006

No direct prod console queries detected in audit period

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| prod-console-access-audit | No direct prod console queries detected in audit period | 0 non-approved console queries in audit period | CloudTrail + SIEM audit queries | Weekly audit + alerting | prod | read-only-viewer | draft | Detects improper direct access to production consoles |

### SEC-007

SG rules audited; attempt broad ingress denied

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| sg-broad-ingress-denied | SG rules audited; attempt broad ingress denied | 0 broad (0.0.0.0/0) ingress on restricted ports | AWS Config + IaC linter | CI per change + monthly audit | dev,int,ref,prod | read-only-viewer | draft | Prevents risky network exposure via security groups |

### SEC-008

Perimeter scan shows no broad whitelist & secure channels

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| perimeter-scan | Perimeter scan shows no broad whitelist & secure channels | No broad whitelists; only secure channels reported | External perimeter scanner + config validation | Monthly + on change | int,ref,prod | read-only-viewer | draft | Confirms perimeter hygiene and secure external exposure |

### SEC-009

ASVS & CIS benchmark automation reports pass thresholds

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| cis-benchmark-compliance | CIS benchmark automation reports meet pass thresholds for targeted services | >= 95% controls passing; all high-severity findings remediated or exceptioned | CIS benchmark tooling integrated in CI and periodic audits | CI per change + monthly full audit | dev,int,ref,prod | read-only-viewer | draft | Baseline hardening validated continuously; monthly cadence catches drift |

### SEC-010

Annual pen test executed; remediation tickets raised & closed

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| annual-pentest | Annual pen test executed; remediation tickets raised & closed | Pen test executed; all critical findings remediated or exceptioned | Pen test reports + remediation tracking | Annual | prod | read-only-viewer | draft | Validates security posture with external testing and tracked remediation |

### SEC-012

IAM policy review confirms least privilege for system roles

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| iam-least-privilege | IAM policy review confirms least privilege for system roles | >= 95% policies compliant; no wildcard resource; explicit actions only | IAM Access Analyzer + policy linters | CI per change + quarterly audit | dev,int,ref,prod | read-only-viewer | draft | Continuous analysis prevents privilege creep; periodic review catches drift |

### SEC-013

Key rotation events logged; unauthorized access denied

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| key-rotation-logging | Key rotation events logged; unauthorized access denied | 100% rotation events logged; 0 unauthorized key access | KMS/AWS logs + SIEM correlation | Quarterly audit + CI checks on policy | dev,int,ref,prod | read-only-viewer | draft | Audit trail confirms rotation compliance and denial of unauthorized access |

### SEC-016

MFA enforced for all privileged infra roles

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| privileged-mfa-enforced | MFA enforced for all privileged infra roles | 100% privileged roles require MFA | IAM policy checks + directory audit | CI policy checks + quarterly audit | dev,int,ref,prod | read-only-viewer | draft | Strong authentication for privileged accounts reduces risk |

### SEC-017

Scan reports zero unmanaged long-lived credentials

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| zero-long-lived-credentials | Scan reports zero unmanaged long-lived credentials | 0 unmanaged long-lived credentials | Secret scanners + IAM credential report audit | CI per build + weekly audit | dev,int,ref,prod | read-only-viewer | draft | Reduces risk from forgotten credentials; continuous scanning plus scheduled audits |

### SEC-018

Supplier audit attestation stored & verified

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| supplier-audit-attestation | Supplier audit attestation stored & verified | Attestations current; verification completed | Supplier management system + evidence repository | Annual + on contract change | prod | read-only-viewer | draft | Ensures supplier compliance and auditable records |

### SEC-019

Segmentation test confirms tenant isolation

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| segmentation-tenant-isolation | Segmentation test confirms tenant isolation | 100% isolation; no cross-tenant data access observed | Segmentation test suite + log verification | Quarterly | int,ref,prod | read-only-viewer | draft | Ensures strict isolation between tenants per policy |

### SEC-021

Port scan matches approved diagnostic list only

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| port-scan-diagnostic-only | Port scan matches approved diagnostic list only | No unexpected open ports detected outside approved list | Automated port scan + baseline comparison | Monthly + CI smoke on infra changes | dev,int,ref,prod | read-only-viewer | draft | Detects misconfigurations; verifies adherence to diagnostic port policy |

### SEC-022

Utility program access restricted to approved roles

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| utility-access-restricted | Utility program access restricted to approved roles | Only approved roles can access utility programs | RBAC policy checks + audit logs | CI policy checks + monthly audit | dev,int,ref,prod | read-only-viewer | draft | Prevents misuse of diagnostic utilities |

### SEC-023

Deployment provenance shows unique traceable accounts

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| deployment-provenance-traceable | Deployment provenance shows unique traceable accounts | All deployments traceable to unique accounts | CI/CD audit trails + commit signing | Continuous | dev,int,ref,prod | read-only-viewer | draft | Ensures accountability and traceability for all deployments |

### SEC-024

Code/data transfer logs show integrity & secure channels

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| transfer-integrity-secure | Code/data transfer logs show integrity & secure channels | 100% transfers logged; integrity and secure channel verified | Checksums/signatures + TLS enforcement + audit logs | CI per change + weekly reviews | dev,int,ref,prod | read-only-viewer | draft | Validates integrity and secure transport for all transfers |

### SEC-027

Build fails on high CVE; report archived

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| high-cve-block | Build fails when high/critical CVEs detected in application or container dependencies | 0 unresolved High/Critical CVEs at release time | SCA scanner (e.g., OWASP Dependency-Check), container scanner, pipeline gate | CI per build + scheduled weekly scans | dev,int,ref | read-only-viewer | draft | Prevents introduction of known vulnerabilities; gate aligned to release quality |

### SEC-028

Release pipeline blocks on critical unresolved findings

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| release-block-critical-findings | Release pipeline blocks on critical unresolved findings | 0 critical unresolved findings prior to release | Pipeline gate integrated with SCA, container, IaC scanners | Per release | dev,int,ref | read-only-viewer | draft | Enforces remediation before release; gate consolidates multiple scanner outputs |

### SEC-029

All API endpoints enforce CIS2 JWT authentication (signature, issuer, audience, assurance claims)

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| cis2-jwt-auth-enforced | All API endpoints enforce CIS2 JWT authentication (signature, issuer, audience, assurance claims) | 100% endpoints require valid CIS2 JWT; invalid/missing tokens rejected with structured 401 | OIDC integration tests + JWT validator + JWKS cache monitor | CI per build + continuous runtime enforcement | dev,int,ref,prod | read-only-viewer | draft | Ensures uniform strong authentication; claim + signature validation prevents unauthorized access |

### SEC-030

Certificates and private keys stored only in approved encrypted secret stores; zero plain text exposure

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| cert-secure-storage | Certificate and private key material stored only in approved encrypted secret stores (KMS/Secrets Manager); zero plaintext in repos, images, build logs, or artifacts | 0 plaintext occurrences; 100% issuance & rotation actions use managed secrets; 100% scan coverage of git history and container layers | Secret scanning (git history + container layers), CI policy checks, artifact scanner, repo pre-commit hooks | CI per build + weekly full history & image layer scan | dev,int,ref,prod | read-only-viewer | draft | Prevents certificate/private key exposure by enforcing exclusive use of encrypted secret storage and continuous scanning |
