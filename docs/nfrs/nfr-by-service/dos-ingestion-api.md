# FtRS NFR – Service: dos-ingestion-api

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
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
| Security | SEC-030 | Certificates and private keys stored only in approved encrypted secret stores; zero plain text exposure | Certificates and private keys are stored only in approved encrypted secret stores (e.g., Secrets Manager/KMS) with zero plaintext exposure across repositories, images, logs, or build artifacts; continuous scanning enforces compliance. | STORY-SEC-030 |

## Operations

No performance operations defined for this service.

## Controls

### COST-001

Mandatory tagging set present on 100% resources

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [COST-001](#cost-001) | mandatory-tagging | Mandatory tagging set present on 100% resources | 100% resources carry mandatory tags | AWS Config rules + tag audit automation | Continuous + monthly report | dev,int,ref,prod | dos-ingestion-api | draft | Enables cost visibility and accountability |

### COST-002

Monthly Cost Explorer review & anomaly log

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [COST-002](#cost-002) | monthly-cost-review | Monthly Cost Explorer review & anomaly log | Review completed; anomalies logged with actions | Cost Explorer + anomaly detection | Monthly | prod | dos-ingestion-api | draft | Ensures proactive cost management |

### COST-003

CloudHealth access for each team infra engineer

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [COST-003](#cost-003) | cloudhealth-access | CloudHealth access for each team infra engineer | Access provisioned; onboarding verified | CloudHealth admin + access logs | Quarterly verification | prod | dos-ingestion-api | draft | Ensures teams can act on cost insights |

### COST-004

CloudHealth optimisation & tag compliance reports

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [COST-004](#cost-004) | optimisation-reports | CloudHealth optimisation & tag compliance reports | Reports generated; tracked actions created | CloudHealth reporting + tracker | Monthly | prod | dos-ingestion-api | draft | Drives optimisation and tag hygiene |

### COST-005

Budgets & alert notifications configured & tested

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [COST-005](#cost-005) | budgets-and-alerts | Budgets & alert notifications configured & tested | Budgets configured; alerts tested successfully | AWS Budgets + notifications | Quarterly + pre-fiscal review | prod | dos-ingestion-api | draft | Prevents cost overruns via alerting |

### GOV-004

Engineering Red-lines compliance checklist signed

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-004](#gov-004) | nhs-github-enterprise-repos | All FtRS code repositories are hosted in NHS GitHub Enterprise and comply with securing-repositories policy; engineering dashboards show compliance | 100% repositories on NHS GitHub Enterprise; 100% securing-repositories checks passing; exceptions recorded with owner and review date | Enterprise repository policy audit + engineering compliance dashboards + CI checks | Continuous (CI on change) + quarterly governance review | dev,int,ref,prod | dos-ingestion-api | draft | Enforces organisational SDLC-1 Red Line for using NHS GitHub Enterprise and securing repositories; provides traceable evidence and automated verification |

### OBS-001

App & infra health panels show green

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-001](#obs-001) | health-panels-green | App & infra health panels show green | All critical panels green; no stale data | Health checks + dashboard status API | Continuous + CI verification on change | int,ref,prod | dos-ingestion-api | draft | Ensures at-a-glance service health visibility |

### OBS-007

Performance metrics latency ≤60s

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-007](#obs-007) | perf-metrics-latency | Performance metrics latency ≤60s | Metrics pipeline delivers data within 60s latency | Metrics agent + ingestion SLA alerting | Continuous monitoring | int,ref,prod | dos-ingestion-api | draft | Fresh metrics are required for accurate operational decisions |

### OBS-033

Unauthorized API access attempts logged, classified, alerted

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [OBS-033](#obs-033) | unauth-access-monitoring | Unauthorized API access attempts logged & alerted with context | 100% auth failures & forbidden requests produce structured log entry with reason, correlation_id, source_ip, user_agent; alert triggers on >5 failed auth attempts per principal per 1m or anomaly spike (>3x baseline) | API gateway logs, auth middleware, metrics backend, alerting rules, anomaly detection job | Continuous collection + weekly anomaly review + monthly rule tuning | int,ref,prod | dos-ingestion-api | draft | Early detection of credential stuffing, token misuse, and privilege escalation attempts |

### REL-007

Brute force/auth anomalies rate limited & alerted (peak 500 TPS burst capacity; rate limits + alerts)

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [REL-007](#rel-007) | auth-brute-force-protection | Brute force/auth anomalies rate limited & alerted (peak 500 TPS legitimate burst supported) | Peak 500 TPS legitimate auth unaffected; anomalies blocked; alert ≤30s; ≤1% false positives | Auth gateway rate limiter + anomaly aggregator + performance harness + alerting | Continuous runtime enforcement + daily compliance script | dev,int,ref,prod | dos-ingestion-api | draft | Protects availability & integrity under authentication attack patterns |

### SEC-001

Crypto algorithms conform; weak ciphers rejected

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-001](#sec-001) | crypto-cipher-policy | Crypto algorithms conform; weak ciphers rejected | TLS1.2+ only; no weak/legacy ciphers enabled | TLS scanner + configuration policy checks | CI per change + monthly scan | dev,int,ref,prod | dos-ingestion-api | draft | Enforces modern TLS standards; automated scans detect drift |

### SEC-002

WAF security pillar checklist completed & gaps tracked

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-002](#sec-002) | waf-pillar-checklist | WAF security pillar checklist completed & gaps tracked | Checklist complete; 100% actions tracked; 0 open critical gaps | WAF checklist repository + issue tracker gate | Quarterly + on change | dev,int,ref,prod | dos-ingestion-api | draft | Formalizes WAF security governance; gaps tracked to closure |

### SEC-003

All endpoints TLS only; storage encryption enabled

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-003](#sec-003) | tls-encryption-endpoints | All public/private API endpoints enforce TLS; storage services enable encryption at rest | 100% compliant across resources | AWS Config rules + Terraform policy checks | Continuous (real-time) with CI enforcement on change | dev,int,ref,prod | dos-ingestion-api | draft | Aligns with NHS policy; Config provides continuous guardrails; CI blocks drift |

### SEC-004

Storage services show encryption enabled

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-004](#sec-004) | storage-encryption-enabled | Storage services show encryption enabled | 100% storage resources encrypted at rest | AWS Config rules + Terraform policy checks | Continuous + CI enforcement | dev,int,ref,prod | dos-ingestion-api | draft | Guardrails ensure encryption at rest across services |

### SEC-005

Cross-environment data access attempts denied

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-005](#sec-005) | cross-env-access-denied | Cross-env data access attempts denied and logged | 100% denial; audit logs prove enforcement | IAM policies + SCP guardrails + audit log queries | CI policy checks + monthly audit review | dev,int,ref,prod | dos-ingestion-api | draft | Prevents accidental or malicious cross-environment data access |

### SEC-006

No direct prod console queries detected in audit period

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-006](#sec-006) | prod-console-access-audit | No direct prod console queries detected in audit period | 0 non-approved console queries in audit period | CloudTrail + SIEM audit queries | Weekly audit + alerting | prod | dos-ingestion-api | draft | Detects improper direct access to production consoles |

### SEC-007

SG rules audited; attempt broad ingress denied

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-007](#sec-007) | sg-broad-ingress-denied | SG rules audited; attempt broad ingress denied | 0 broad (0.0.0.0/0) ingress on restricted ports | AWS Config + IaC linter | CI per change + monthly audit | dev,int,ref,prod | dos-ingestion-api | draft | Prevents risky network exposure via security groups |

### SEC-008

Perimeter scan shows no broad whitelist & secure channels

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-008](#sec-008) | perimeter-scan | Perimeter scan shows no broad whitelist & secure channels | No broad whitelists; only secure channels reported | External perimeter scanner + config validation | Monthly + on change | int,ref,prod | dos-ingestion-api | draft | Confirms perimeter hygiene and secure external exposure |

### SEC-009

ASVS & CIS benchmark automation reports pass thresholds

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-009](#sec-009) | cis-benchmark-compliance | CIS benchmark automation reports meet pass thresholds for targeted services | >= 95% controls passing; all high-severity findings remediated or exceptioned | CIS benchmark tooling integrated in CI and periodic audits | CI per change + monthly full audit | dev,int,ref,prod | dos-ingestion-api | draft | Baseline hardening validated continuously; monthly cadence catches drift |

### SEC-010

Annual pen test executed; remediation tickets raised & closed

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-010](#sec-010) | annual-pentest | Annual pen test executed; remediation tickets raised & closed | Pen test executed; all critical findings remediated or exceptioned | Pen test reports + remediation tracking | Annual | prod | dos-ingestion-api | draft | Validates security posture with external testing and tracked remediation |

### SEC-012

IAM policy review confirms least privilege for system roles

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-012](#sec-012) | iam-least-privilege | IAM policy review confirms least privilege for system roles | >= 95% policies compliant; no wildcard resource; explicit actions only | IAM Access Analyzer + policy linters | CI per change + quarterly audit | dev,int,ref,prod | dos-ingestion-api | draft | Continuous analysis prevents privilege creep; periodic review catches drift |

### SEC-013

Key rotation events logged; unauthorized access denied

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-013](#sec-013) | key-rotation-logging | Key rotation events logged; unauthorized access denied | 100% rotation events logged; 0 unauthorized key access | KMS/AWS logs + SIEM correlation | Quarterly audit + CI checks on policy | dev,int,ref,prod | dos-ingestion-api | draft | Audit trail confirms rotation compliance and denial of unauthorized access |

### SEC-016

MFA enforced for all privileged infra roles

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-016](#sec-016) | privileged-mfa-enforced | MFA enforced for all privileged infra roles | 100% privileged roles require MFA | IAM policy checks + directory audit | CI policy checks + quarterly audit | dev,int,ref,prod | dos-ingestion-api | draft | Strong authentication for privileged accounts reduces risk |

### SEC-017

Scan reports zero unmanaged long-lived credentials

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-017](#sec-017) | zero-long-lived-credentials | Scan reports zero unmanaged long-lived credentials | 0 unmanaged long-lived credentials | Secret scanners + IAM credential report audit | CI per build + weekly audit | dev,int,ref,prod | dos-ingestion-api | draft | Reduces risk from forgotten credentials; continuous scanning plus scheduled audits |

### SEC-018

Supplier audit attestation stored & verified

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-018](#sec-018) | supplier-audit-attestation | Supplier audit attestation stored & verified | Attestations current; verification completed | Supplier management system + evidence repository | Annual + on contract change | prod | dos-ingestion-api | draft | Ensures supplier compliance and auditable records |

### SEC-019

Segmentation test confirms tenant isolation

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-019](#sec-019) | segmentation-tenant-isolation | Segmentation test confirms tenant isolation | 100% isolation; no cross-tenant data access observed | Segmentation test suite + log verification | Quarterly | int,ref,prod | dos-ingestion-api | draft | Ensures strict isolation between tenants per policy |

### SEC-021

Port scan matches approved diagnostic list only

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-021](#sec-021) | port-scan-diagnostic-only | Port scan matches approved diagnostic list only | No unexpected open ports detected outside approved list | Automated port scan + baseline comparison | Monthly + CI smoke on infra changes | dev,int,ref,prod | dos-ingestion-api | draft | Detects misconfigurations; verifies adherence to diagnostic port policy |

### SEC-022

Utility program access restricted to approved roles

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-022](#sec-022) | utility-access-restricted | Utility program access restricted to approved roles | Only approved roles can access utility programs | RBAC policy checks + audit logs | CI policy checks + monthly audit | dev,int,ref,prod | dos-ingestion-api | draft | Prevents misuse of diagnostic utilities |

### SEC-023

Deployment provenance shows unique traceable accounts

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-023](#sec-023) | deployment-provenance-traceable | Deployment provenance shows unique traceable accounts | All deployments traceable to unique accounts | CI/CD audit trails + commit signing | Continuous | dev,int,ref,prod | dos-ingestion-api | draft | Ensures accountability and traceability for all deployments |

### SEC-024

Code/data transfer logs show integrity & secure channels

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-024](#sec-024) | transfer-integrity-secure | Code/data transfer logs show integrity & secure channels | 100% transfers logged; integrity and secure channel verified | Checksums/signatures + TLS enforcement + audit logs | CI per change + weekly reviews | dev,int,ref,prod | dos-ingestion-api | draft | Validates integrity and secure transport for all transfers |

### SEC-027

Build fails on high CVE; report archived

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-027](#sec-027) | high-cve-block | Build fails when high/critical CVEs detected in application or container dependencies | 0 unresolved High/Critical CVEs at release time | SCA scanner (e.g., OWASP Dependency-Check), container scanner, pipeline gate | CI per build + scheduled weekly scans | dev,int,ref | dos-ingestion-api | draft | Prevents introduction of known vulnerabilities; gate aligned to release quality |

### SEC-028

Release pipeline blocks on critical unresolved findings

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-028](#sec-028) | release-block-critical-findings | Release pipeline blocks on critical unresolved findings | 0 critical unresolved findings prior to release | Pipeline gate integrated with SCA, container, IaC scanners | Per release | dev,int,ref | dos-ingestion-api | draft | Enforces remediation before release; gate consolidates multiple scanner outputs |

### SEC-030

Certificates and private keys stored only in approved encrypted secret stores; zero plain text exposure

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-030](#sec-030) | cert-secure-storage | Certificate and private key material stored only in approved encrypted secret stores (KMS/Secrets Manager); zero plaintext in repos, images, build logs, or artifacts | 0 plaintext occurrences; 100% issuance & rotation actions use managed secrets; 100% scan coverage of git history and container layers | Secret scanning (git history + container layers), CI policy checks, artifact scanner, repo pre-commit hooks | CI per build + weekly full history & image layer scan | dev,int,ref,prod | dos-ingestion-api | draft | Prevents certificate/private key exposure by enforcing exclusive use of encrypted secret storage and continuous scanning |
