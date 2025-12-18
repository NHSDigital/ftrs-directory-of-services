# FtRS NFR – Service: Infrastructure – Domain: Security

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Security NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066470803/Security)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Security | [SEC-002](#Infrastructure–SecurityNFRs&Controls-SEC-002) | WAF security pillar checklist completed & gaps tracked | Complete the AWS/WAF security pillar checklist and track remediation actions for any gaps. | [FTRS-364](https://nhsd-jira.digital.nhs.uk/browse/FTRS-364) |
| Security | [SEC-003](#Infrastructure–SecurityNFRs&Controls-SEC-003) | All endpoints TLS only; storage encryption enabled | All service endpoints enforce TLS and all stored data (databases, buckets) is encrypted at rest. | [FTRS-1563](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1563) |
| Security | [SEC-004](#Infrastructure–SecurityNFRs&Controls-SEC-004) | Storage services show encryption enabled | Every storage service (S3, RDS, etc.) shows encryption enabled with managed or customer keys. | (none) |
| Security | [SEC-005](#Infrastructure–SecurityNFRs&Controls-SEC-005) | Cross-environment data access attempts denied | Strict environment isolation: data access from one environment to another is prevented. | [FTRS-1494](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1494) |
| Security | [SEC-006](#Infrastructure–SecurityNFRs&Controls-SEC-006) | No direct prod console queries detected in audit period | No direct production console queries by engineers outside approved, audited break-glass processes. | (none) |
| Security | [SEC-007](#Infrastructure–SecurityNFRs&Controls-SEC-007) | SG rules audited; attempt broad ingress denied | Network security groups allow only narrowly scoped inbound rules; broad ingress is denied. | (none) |
| Security | [SEC-008](#Infrastructure–SecurityNFRs&Controls-SEC-008) | Perimeter scan shows no broad whitelist & secure channels | Perimeter scans show secure transport, no open broad whitelists, and hardened edge configuration. | (none) |
| Security | [SEC-009](#Infrastructure–SecurityNFRs&Controls-SEC-009) | ASVS & CIS benchmark automation reports pass thresholds | Automated ASVS and CIS benchmark scans meet pass thresholds; failures trigger remediation. | (none) |
| Security | [SEC-010](#Infrastructure–SecurityNFRs&Controls-SEC-010) | Annual pen test executed; remediation tickets raised & closed | Annual penetration test completed; identified issues tracked and closed. | [FTRS-1440](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1440), [FTRS-1455](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1455), [FTRS-1462](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1462), [FTRS-2](https://nhsd-jira.digital.nhs.uk/browse/FTRS-2) |
| Security | [SEC-011](#Infrastructure–SecurityNFRs&Controls-SEC-011) | Security features enabled latency within SLA | Enabling security controls does not push latency beyond defined SLAs. | (none) |
| Security | [SEC-012](#Infrastructure–SecurityNFRs&Controls-SEC-012) | IAM policy review confirms least privilege for system roles | IAM roles and policies grant least privilege; periodic reviews confirm minimal access. | [FTRS-1274](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1274) |
| Security | [SEC-013](#Infrastructure–SecurityNFRs&Controls-SEC-013) | Key rotation events logged; unauthorized access denied | Cryptographic keys rotate on schedule and unauthorized access attempts are rejected and logged. | (none) |
| Security | [SEC-014](#Infrastructure–SecurityNFRs&Controls-SEC-014) | mTLS handshake succeeds between designated services | Mutual TLS (mTLS) succeeds between designated internal services to protect sensitive flows. | [FTRS-1600](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1600) |
| Security | [SEC-015](#Infrastructure–SecurityNFRs&Controls-SEC-015) | Expiry alert fired in advance; renewal executed seamlessly | Certificate expiry is detected in advance; renewal occurs without downtime. | [FTRS-1604](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1604) |
| Security | [SEC-016](#Infrastructure–SecurityNFRs&Controls-SEC-016) | MFA enforced for all privileged infra roles | Privileged infrastructure roles require multi-factor authentication (MFA). | (none) |
| Security | [SEC-017](#Infrastructure–SecurityNFRs&Controls-SEC-017) | Scan reports zero unmanaged long-lived credentials | No long-lived unmanaged credentials; periodic scans confirm only managed secrets exist. | (none) |
| Security | [SEC-018](#Infrastructure–SecurityNFRs&Controls-SEC-018) | Supplier audit attestation stored & verified | Third-party supplier security attestation is collected and stored for audit. | (none) |
| Security | [SEC-019](#Infrastructure–SecurityNFRs&Controls-SEC-019) | Segmentation test confirms tenant isolation | Tenant or data segmentation tests confirm isolation boundaries hold. | (none) |
| Security | [SEC-020](#Infrastructure–SecurityNFRs&Controls-SEC-020) | Remote connections present valid Authority certs | Remote connections present valid certificates from trusted authorities. | (none) |
| Security | [SEC-021](#Infrastructure–SecurityNFRs&Controls-SEC-021) | Port scan matches approved diagnostic list only | Port scans reveal only approved diagnostic and service ports—no unexpected exposures. | (none) |
| Security | [SEC-022](#Infrastructure–SecurityNFRs&Controls-SEC-022) | Utility program access restricted to approved roles | Access to powerful utility programs is restricted to approved roles. | (none) |
| Security | [SEC-023](#Infrastructure–SecurityNFRs&Controls-SEC-023) | Deployment provenance shows unique traceable accounts | Deployment provenance shows traceable unique accounts per automated pipeline stage. | (none) |
| Security | [SEC-024](#Infrastructure–SecurityNFRs&Controls-SEC-024) | Code/data transfer logs show integrity & secure channels | Transfer of code or data maintains integrity and uses secure channels; events are logged. | (none) |
| Security | [SEC-025](#Infrastructure–SecurityNFRs&Controls-SEC-025) | PID requests enforce mTLS; plain text blocked | Requests containing identifiable patient data enforce mTLS; plaintext attempts are blocked. | (none) |
| Security | [SEC-026](#Infrastructure–SecurityNFRs&Controls-SEC-026) | API responses contain no unencrypted PID fields | API responses never include unencrypted patient identifiable data (PID) fields. | (none) |
| Security | [SEC-027](#Infrastructure–SecurityNFRs&Controls-SEC-027) | Build fails on high CVE; report archived | Build pipeline blocks release when critical CVEs exceed threshold; reports archived. | (none) |
| Security | [SEC-028](#Infrastructure–SecurityNFRs&Controls-SEC-028) | Release pipeline blocks on critical unresolved findings | Releases are halted if critical unresolved security findings remain. | (none) |
| Security | [SEC-030](#Infrastructure–SecurityNFRs&Controls-SEC-030) | Certificates and private keys stored only in approved encrypted secret stores; zero plain text exposure | Certificates and private keys are stored only in approved encrypted secret stores (e.g., Secrets Manager/KMS) with zero plaintext exposure across repositories, images, logs, or build artifacts; continuous scanning enforces compliance. | [FTRS-1602](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1602) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### SEC-002

WAF security pillar checklist completed & gaps tracked

See explanation: [SEC-002](../../explanations.md#Explanations-SEC-002)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| waf-pillar-checklist | WAF security pillar checklist completed & gaps tracked | Checklist complete; 100% actions tracked; 0 open critical gaps | Quarterly + on change | dev,int,ref,prod | Infrastructure | draft | [FTRS-364](https://nhsd-jira.digital.nhs.uk/browse/FTRS-364) | Formalizes WAF security governance; gaps tracked to closure |

### SEC-003

All endpoints TLS only; storage encryption enabled

See explanation: [SEC-003](../../explanations.md#Explanations-SEC-003)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| tls-encryption-endpoints | All public/private API endpoints enforce TLS; storage services enable encryption at rest | 100% compliant across resources | Continuous (real-time) with CI enforcement on change | dev,int,ref,prod | Infrastructure | draft | [FTRS-1563](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1563) | Aligns with NHS policy; Config provides continuous guardrails; CI blocks drift |

### SEC-004

Storage services show encryption enabled

See explanation: [SEC-004](../../explanations.md#Explanations-SEC-004)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| storage-encryption-enabled | Storage services show encryption enabled | 100% storage resources encrypted at rest | Continuous + CI enforcement | dev,int,ref,prod | Infrastructure | draft | (none) | Guardrails ensure encryption at rest across services |

### SEC-005

Cross-environment data access attempts denied

See explanation: [SEC-005](../../explanations.md#Explanations-SEC-005)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| cross-env-access-denied | Cross-env data access attempts denied and logged | 100% denial; audit logs prove enforcement | CI policy checks + monthly audit review | dev,int,ref,prod | Infrastructure | draft | [FTRS-1494](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1494) | Prevents accidental or malicious cross-environment data access |

### SEC-006

No direct prod console queries detected in audit period

See explanation: [SEC-006](../../explanations.md#Explanations-SEC-006)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| prod-console-access-audit | No direct prod console queries detected in audit period | 0 non-approved console queries in audit period | Weekly audit + alerting | prod | Infrastructure | draft | (none) | Detects improper direct access to production consoles |

### SEC-007

SG rules audited; attempt broad ingress denied

See explanation: [SEC-007](../../explanations.md#Explanations-SEC-007)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| sg-broad-ingress-denied | SG rules audited; attempt broad ingress denied | 0 broad (0.0.0.0/0) ingress on restricted ports | CI per change + monthly audit | dev,int,ref,prod | Infrastructure | draft | (none) | Prevents risky network exposure via security groups |

### SEC-008

Perimeter scan shows no broad whitelist & secure channels

See explanation: [SEC-008](../../explanations.md#Explanations-SEC-008)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| perimeter-scan | Perimeter scan shows no broad whitelist & secure channels | No broad whitelists; only secure channels reported | Monthly + on change | int,ref,prod | Infrastructure | draft | (none) | Confirms perimeter hygiene and secure external exposure |

### SEC-009

ASVS & CIS benchmark automation reports pass thresholds

See explanation: [SEC-009](../../explanations.md#Explanations-SEC-009)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| cis-benchmark-compliance | CIS benchmark automation reports meet pass thresholds for targeted services | >= 95% controls passing; all high-severity findings remediated or exceptioned | CI per change + monthly full audit | dev,int,ref,prod | Infrastructure | draft | (none) | Baseline hardening validated continuously; monthly cadence catches drift |

### SEC-010

Annual pen test executed; remediation tickets raised & closed

See explanation: [SEC-010](../../explanations.md#Explanations-SEC-010)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| annual-pentest | Annual pen test executed; remediation tickets raised & closed | Pen test executed; all critical findings remediated or exceptioned | Annual | prod | Infrastructure | draft | [FTRS-1440](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1440), [FTRS-1455](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1455), [FTRS-1462](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1462), [FTRS-2](https://nhsd-jira.digital.nhs.uk/browse/FTRS-2) | Validates security posture with external testing and tracked remediation |

### SEC-011

Security features enabled latency within SLA

See explanation: [SEC-011](../../explanations.md#Explanations-SEC-011)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| security-features-latency-sla | Security features enabled latency within SLA | Added latency within agreed SLA per endpoint | CI perf checks + monthly regression review | int,ref,prod | Infrastructure | draft | (none) | Ensures security does not breach performance SLAs |

### SEC-012

IAM policy review confirms least privilege for system roles

See explanation: [SEC-012](../../explanations.md#Explanations-SEC-012)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| iam-least-privilege | IAM policy review confirms least privilege for system roles | >= 95% policies compliant; no wildcard resource; explicit actions only | CI per change + quarterly audit | dev,int,ref,prod | Infrastructure | draft | [FTRS-1274](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1274) | Continuous analysis prevents privilege creep; periodic review catches drift |

### SEC-013

Key rotation events logged; unauthorized access denied

See explanation: [SEC-013](../../explanations.md#Explanations-SEC-013)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| key-rotation-logging | Key rotation events logged; unauthorized access denied | 100% rotation events logged; 0 unauthorized key access | Quarterly audit + CI checks on policy | dev,int,ref,prod | Infrastructure | draft | (none) | Audit trail confirms rotation compliance and denial of unauthorized access |

### SEC-014

mTLS handshake succeeds between designated services

See explanation: [SEC-014](../../explanations.md#Explanations-SEC-014)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| mtls-service-handshake | mTLS handshake succeeds between designated services using ITOC-approved CA signed leaf + intermediate certs (chain to ITOC root); invalid/expired/revoked/untrusted-issuer/weak-cipher attempts rejected | 100% handshake success for valid ITOC chain; 0 successful handshakes with expired, revoked, weak cipher, or non-ITOC issuer certs; rotation introduces 0 downtime | CI per build + cert rotation checks + revocation poll ≤5m | int,ref,prod | Infrastructure | draft | [FTRS-1600](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1600) | Enforces trusted ITOC certificate chain, strong ciphers, timely revocation, and zero-downtime rotation for secure service-to-service trust |

### SEC-015

Expiry alert fired in advance; renewal executed seamlessly

See explanation: [SEC-015](../../explanations.md#Explanations-SEC-015)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| cert-expiry-alert-renewal | Expiry alert fired in advance; renewal executed seamlessly | >= 30 days prior alert; 0 outage during renewal | Continuous monitoring | int,ref,prod | Infrastructure | draft | [FTRS-1604](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1604) | Proactive renewal prevents downtime; alerts ensure timely action |

### SEC-016

MFA enforced for all privileged infra roles

See explanation: [SEC-016](../../explanations.md#Explanations-SEC-016)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| privileged-mfa-enforced | MFA enforced for all privileged infra roles | 100% privileged roles require MFA | CI policy checks + quarterly audit | dev,int,ref,prod | Infrastructure | draft | (none) | Strong authentication for privileged accounts reduces risk |

### SEC-017

Scan reports zero unmanaged long-lived credentials

See explanation: [SEC-017](../../explanations.md#Explanations-SEC-017)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| zero-long-lived-credentials | Scan reports zero unmanaged long-lived credentials | 0 unmanaged long-lived credentials | CI per build + weekly audit | dev,int,ref,prod | Infrastructure | draft | (none) | Reduces risk from forgotten credentials; continuous scanning plus scheduled audits |

### SEC-018

Supplier audit attestation stored & verified

See explanation: [SEC-018](../../explanations.md#Explanations-SEC-018)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| supplier-audit-attestation | Supplier audit attestation stored & verified | Attestations current; verification completed | Annual + on contract change | prod | Infrastructure | draft | (none) | Ensures supplier compliance and auditable records |

### SEC-019

Segmentation test confirms tenant isolation

See explanation: [SEC-019](../../explanations.md#Explanations-SEC-019)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| segmentation-tenant-isolation | Segmentation test confirms tenant isolation | 100% isolation; no cross-tenant data access observed | Quarterly | int,ref,prod | Infrastructure | draft | (none) | Ensures strict isolation between tenants per policy |

### SEC-020

Remote connections present valid Authority certs

See explanation: [SEC-020](../../explanations.md#Explanations-SEC-020)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| authority-cert-validation | Remote connections present valid Authority certs; invalid certs rejected | 100% validation events pass; 0 successful connections with invalid certs | CI policy validation + runtime checks | int,ref,prod | Infrastructure | draft | (none) | External data source interactions require strict certificate validation |

### SEC-021

Port scan matches approved diagnostic list only

See explanation: [SEC-021](../../explanations.md#Explanations-SEC-021)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| port-scan-diagnostic-only | Port scan matches approved diagnostic list only | No unexpected open ports detected outside approved list | Monthly + CI smoke on infra changes | dev,int,ref,prod | Infrastructure | draft | (none) | Detects misconfigurations; verifies adherence to diagnostic port policy |

### SEC-022

Utility program access restricted to approved roles

See explanation: [SEC-022](../../explanations.md#Explanations-SEC-022)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| utility-access-restricted | Utility program access restricted to approved roles | Only approved roles can access utility programs | CI policy checks + monthly audit | dev,int,ref,prod | Infrastructure | draft | (none) | Prevents misuse of diagnostic utilities |

### SEC-023

Deployment provenance shows unique traceable accounts

See explanation: [SEC-023](../../explanations.md#Explanations-SEC-023)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| deployment-provenance-traceable | Deployment provenance shows unique traceable accounts | All deployments traceable to unique accounts | Continuous | dev,int,ref,prod | Infrastructure | draft | (none) | Ensures accountability and traceability for all deployments |

### SEC-024

Code/data transfer logs show integrity & secure channels

See explanation: [SEC-024](../../explanations.md#Explanations-SEC-024)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| transfer-integrity-secure | Code/data transfer logs show integrity & secure channels | 100% transfers logged; integrity and secure channel verified | CI per change + weekly reviews | dev,int,ref,prod | Infrastructure | draft | (none) | Validates integrity and secure transport for all transfers |

### SEC-025

PID requests enforce mTLS; plain text blocked

See explanation: [SEC-025](../../explanations.md#Explanations-SEC-025)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| pid-mtls-enforcement | Requests carrying PID fields require mutual TLS; plaintext requests blocked | 100% enforcement on designated endpoints | CI policy validation + continuous enforcement | int,ref,prod | Infrastructure | draft | (none) | Ensures transport security for sensitive data; test coverage verifies enforcement |

### SEC-026

API responses contain no unencrypted PID fields

See explanation: [SEC-026](../../explanations.md#Explanations-SEC-026)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| pid-no-plaintext-response | API responses contain no unencrypted PID fields | 0 occurrences of unencrypted PID in responses | CI per build + periodic production sampling | int,ref,prod | Infrastructure | draft | (none) | Ensures sensitive data is never returned unencrypted |

### SEC-027

Build fails on high CVE; report archived

See explanation: [SEC-027](../../explanations.md#Explanations-SEC-027)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| high-cve-block | Build fails when high/critical CVEs detected in application or container dependencies | 0 unresolved High/Critical CVEs at release time | CI per build + scheduled weekly scans | dev,int,ref | Infrastructure | draft | (none) | Prevents introduction of known vulnerabilities; gate aligned to release quality |

### SEC-028

Release pipeline blocks on critical unresolved findings

See explanation: [SEC-028](../../explanations.md#Explanations-SEC-028)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| release-block-critical-findings | Release pipeline blocks on critical unresolved findings | 0 critical unresolved findings prior to release | Per release | dev,int,ref | Infrastructure | draft | (none) | Enforces remediation before release; gate consolidates multiple scanner outputs |

### SEC-030

Certificates and private keys stored only in approved encrypted secret stores; zero plain text exposure

See explanation: [SEC-030](../../explanations.md#Explanations-SEC-030)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| cert-secure-storage | Certificate and private key material stored only in approved encrypted secret stores (KMS/Secrets Manager); zero plaintext in repos, images, build logs, or artifacts | 0 plaintext occurrences; 100% issuance & rotation actions use managed secrets; 100% scan coverage of git history and container layers | CI per build + weekly full history & image layer scan | dev,int,ref,prod | Infrastructure | draft | [FTRS-1602](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1602) | Prevents certificate/private key exposure by enforcing exclusive use of encrypted secret storage and continuous scanning |
