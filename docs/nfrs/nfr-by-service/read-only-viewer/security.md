# FtRS NFR – Service: Read-only Viewer – Domain: Security

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Security NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066470803/Security)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Security | [SEC-001](#sec-001) | Crypto algorithms conform; weak ciphers rejected | Use only strong, approved cryptographic algorithms; weak or deprecated ciphers are blocked. | (none) |
| Security | [SEC-002](#sec-002) | WAF security pillar checklist completed & gaps tracked | Complete the AWS/WAF security pillar checklist and track remediation actions for any gaps. | [FTRS-364 WAF Rate Limit enhancement](https://nhsd-jira.digital.nhs.uk/browse/FTRS-364) |
| Security | [SEC-003](#sec-003) | All endpoints TLS only; storage encryption enabled | All service endpoints enforce TLS and all stored data (databases, buckets) is encrypted at rest. | [FTRS-1563 TLS Encryption of Endpoints](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1563) |
| Security | [SEC-004](#sec-004) | Storage services show encryption enabled | Every storage service (S3, RDS, etc.) shows encryption enabled with managed or customer keys. | (none) |
| Security | [SEC-005](#sec-005) | Cross-environment data access attempts denied | Strict environment isolation: data access from one environment to another is prevented. | [FTRS-1494 Prepare test environment and data.](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1494) |
| Security | [SEC-006](#sec-006) | No direct prod console queries detected in audit period | No direct production console queries by engineers outside approved, audited break-glass processes. | (none) |
| Security | [SEC-007](#sec-007) | SG rules audited; attempt broad ingress denied | Network security groups allow only narrowly scoped inbound rules; broad ingress is denied. | (none) |
| Security | [SEC-008](#sec-008) | Perimeter scan shows no broad whitelist & secure channels | Perimeter scans show secure transport, no open broad whitelists, and hardened edge configuration. | (none) |
| Security | [SEC-009](#sec-009) | ASVS & CIS benchmark automation reports pass thresholds | Automated ASVS and CIS benchmark scans meet pass thresholds; failures trigger remediation. | (none) |
| Security | [SEC-010](#sec-010) | Annual pen test executed; remediation tickets raised & closed | Annual penetration test completed; identified issues tracked and closed. | [FTRS-1440 2025 - Execute Annual Pen-Tests to audit the Directory of Services (DoS) to identify vulnerabilities of the Live DoS system.](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1440), [FTRS-1455 Run DI Pen Test 2025](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1455), [FTRS-1462 Arrange Annual DI Pen Test 2025](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1462), [FTRS-2 Run the annual pen test audit for DoS Integration](https://nhsd-jira.digital.nhs.uk/browse/FTRS-2) |
| Security | [SEC-012](#sec-012) | IAM policy review confirms least privilege for system roles | IAM roles and policies grant least privilege; periodic reviews confirm minimal access. | [FTRS-1274 IAM roles cleanup for prod env](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1274) |
| Security | [SEC-013](#sec-013) | Key rotation events logged; unauthorized access denied | Cryptographic keys rotate on schedule and unauthorized access attempts are rejected and logged. | (none) |
| Security | [SEC-016](#sec-016) | MFA enforced for all privileged infra roles | Privileged infrastructure roles require multi-factor authentication (MFA). | (none) |
| Security | [SEC-017](#sec-017) | Scan reports zero unmanaged long-lived credentials | No long-lived unmanaged credentials; periodic scans confirm only managed secrets exist. | (none) |
| Security | [SEC-018](#sec-018) | Supplier audit attestation stored & verified | Third-party supplier security attestation is collected and stored for audit. | (none) |
| Security | [SEC-019](#sec-019) | Segmentation test confirms tenant isolation | Tenant or data segmentation tests confirm isolation boundaries hold. | (none) |
| Security | [SEC-021](#sec-021) | Port scan matches approved diagnostic list only | Port scans reveal only approved diagnostic and service ports—no unexpected exposures. | (none) |
| Security | [SEC-022](#sec-022) | Utility program access restricted to approved roles | Access to powerful utility programs is restricted to approved roles. | (none) |
| Security | [SEC-023](#sec-023) | Deployment provenance shows unique traceable accounts | Deployment provenance shows traceable unique accounts per automated pipeline stage. | (none) |
| Security | [SEC-024](#sec-024) | Code/data transfer logs show integrity & secure channels | Transfer of code or data maintains integrity and uses secure channels; events are logged. | (none) |
| Security | [SEC-027](#sec-027) | Build fails on high CVE; report archived | Build pipeline blocks release when critical CVEs exceed threshold; reports archived. | (none) |
| Security | [SEC-028](#sec-028) | Release pipeline blocks on critical unresolved findings | Releases are halted if critical unresolved security findings remain. | (none) |
| Security | [SEC-029](#sec-029) | All API endpoints enforce CIS2 JWT authentication (signature, issuer, audience, assurance claims) | All API endpoints enforce CIS2 JWT authentication with signature, issuer, audience and required assurance claim validation; invalid or missing tokens are rejected with structured errors. | [FTRS-1593 CIS2 JWT auth on all endpoints](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1593) |
| Security | [SEC-030](#sec-030) | Certificates and private keys stored only in approved encrypted secret stores; zero plain text exposure | Certificates and private keys are stored only in approved encrypted secret stores (e.g., Secrets Manager/KMS) with zero plaintext exposure across repositories, images, logs, or build artifacts; continuous scanning enforces compliance. | [FTRS-1602 Certificate secure storage](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1602) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### SEC-001

Crypto algorithms conform; weak ciphers rejected

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| crypto-cipher-policy | Crypto algorithms conform; weak ciphers rejected | TLS1.2+ only; no weak/legacy ciphers enabled | CI per change + monthly scan | dev,int,ref,prod | Read-only Viewer | draft | (none) | Enforces modern TLS standards; automated scans detect drift |

### SEC-002

WAF security pillar checklist completed & gaps tracked

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| waf-pillar-checklist | WAF security pillar checklist completed & gaps tracked | Checklist complete; 100% actions tracked; 0 open critical gaps | Quarterly + on change | dev,int,ref,prod | Read-only Viewer | draft | [FTRS-364 WAF Rate Limit enhancement](https://nhsd-jira.digital.nhs.uk/browse/FTRS-364) | Formalizes WAF security governance; gaps tracked to closure |

### SEC-003

All endpoints TLS only; storage encryption enabled

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| tls-encryption-endpoints | All public/private API endpoints enforce TLS; storage services enable encryption at rest | 100% compliant across resources | Continuous (real-time) with CI enforcement on change | dev,int,ref,prod | Read-only Viewer | draft | [FTRS-1563 TLS Encryption of Endpoints](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1563) | Aligns with NHS policy; Config provides continuous guardrails; CI blocks drift |

### SEC-004

Storage services show encryption enabled

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| storage-encryption-enabled | Storage services show encryption enabled | 100% storage resources encrypted at rest | Continuous + CI enforcement | dev,int,ref,prod | Read-only Viewer | draft | (none) | Guardrails ensure encryption at rest across services |

### SEC-005

Cross-environment data access attempts denied

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| cross-env-access-denied | Cross-env data access attempts denied and logged | 100% denial; audit logs prove enforcement | CI policy checks + monthly audit review | dev,int,ref,prod | Read-only Viewer | draft | [FTRS-1494 Prepare test environment and data.](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1494) | Prevents accidental or malicious cross-environment data access |

### SEC-006

No direct prod console queries detected in audit period

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| prod-console-access-audit | No direct prod console queries detected in audit period | 0 non-approved console queries in audit period | Weekly audit + alerting | prod | Read-only Viewer | draft | (none) | Detects improper direct access to production consoles |

### SEC-007

SG rules audited; attempt broad ingress denied

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| sg-broad-ingress-denied | SG rules audited; attempt broad ingress denied | 0 broad (0.0.0.0/0) ingress on restricted ports | CI per change + monthly audit | dev,int,ref,prod | Read-only Viewer | draft | (none) | Prevents risky network exposure via security groups |

### SEC-008

Perimeter scan shows no broad whitelist & secure channels

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| perimeter-scan | Perimeter scan shows no broad whitelist & secure channels | No broad whitelists; only secure channels reported | Monthly + on change | int,ref,prod | Read-only Viewer | draft | (none) | Confirms perimeter hygiene and secure external exposure |

### SEC-009

ASVS & CIS benchmark automation reports pass thresholds

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| cis-benchmark-compliance | CIS benchmark automation reports meet pass thresholds for targeted services | >= 95% controls passing; all high-severity findings remediated or exceptioned | CI per change + monthly full audit | dev,int,ref,prod | Read-only Viewer | draft | (none) | Baseline hardening validated continuously; monthly cadence catches drift |

### SEC-010

Annual pen test executed; remediation tickets raised & closed

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| annual-pentest | Annual pen test executed; remediation tickets raised & closed | Pen test executed; all critical findings remediated or exceptioned | Annual | prod | Read-only Viewer | draft | [FTRS-1440 2025 - Execute Annual Pen-Tests to audit the Directory of Services (DoS) to identify vulnerabilities of the Live DoS system.](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1440), [FTRS-1455 Run DI Pen Test 2025](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1455), [FTRS-1462 Arrange Annual DI Pen Test 2025](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1462), [FTRS-2 Run the annual pen test audit for DoS Integration](https://nhsd-jira.digital.nhs.uk/browse/FTRS-2) | Validates security posture with external testing and tracked remediation |

### SEC-012

IAM policy review confirms least privilege for system roles

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| iam-least-privilege | IAM policy review confirms least privilege for system roles | >= 95% policies compliant; no wildcard resource; explicit actions only | CI per change + quarterly audit | dev,int,ref,prod | Read-only Viewer | draft | [FTRS-1274 IAM roles cleanup for prod env](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1274) | Continuous analysis prevents privilege creep; periodic review catches drift |

### SEC-013

Key rotation events logged; unauthorized access denied

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| key-rotation-logging | Key rotation events logged; unauthorized access denied | 100% rotation events logged; 0 unauthorized key access | Quarterly audit + CI checks on policy | dev,int,ref,prod | Read-only Viewer | draft | (none) | Audit trail confirms rotation compliance and denial of unauthorized access |

### SEC-016

MFA enforced for all privileged infra roles

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| privileged-mfa-enforced | MFA enforced for all privileged infra roles | 100% privileged roles require MFA | CI policy checks + quarterly audit | dev,int,ref,prod | Read-only Viewer | draft | (none) | Strong authentication for privileged accounts reduces risk |

### SEC-017

Scan reports zero unmanaged long-lived credentials

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| zero-long-lived-credentials | Scan reports zero unmanaged long-lived credentials | 0 unmanaged long-lived credentials | CI per build + weekly audit | dev,int,ref,prod | Read-only Viewer | draft | (none) | Reduces risk from forgotten credentials; continuous scanning plus scheduled audits |

### SEC-018

Supplier audit attestation stored & verified

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| supplier-audit-attestation | Supplier audit attestation stored & verified | Attestations current; verification completed | Annual + on contract change | prod | Read-only Viewer | draft | (none) | Ensures supplier compliance and auditable records |

### SEC-019

Segmentation test confirms tenant isolation

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| segmentation-tenant-isolation | Segmentation test confirms tenant isolation | 100% isolation; no cross-tenant data access observed | Quarterly | int,ref,prod | Read-only Viewer | draft | (none) | Ensures strict isolation between tenants per policy |

### SEC-021

Port scan matches approved diagnostic list only

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| port-scan-diagnostic-only | Port scan matches approved diagnostic list only | No unexpected open ports detected outside approved list | Monthly + CI smoke on infra changes | dev,int,ref,prod | Read-only Viewer | draft | (none) | Detects misconfigurations; verifies adherence to diagnostic port policy |

### SEC-022

Utility program access restricted to approved roles

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| utility-access-restricted | Utility program access restricted to approved roles | Only approved roles can access utility programs | CI policy checks + monthly audit | dev,int,ref,prod | Read-only Viewer | draft | (none) | Prevents misuse of diagnostic utilities |

### SEC-023

Deployment provenance shows unique traceable accounts

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| deployment-provenance-traceable | Deployment provenance shows unique traceable accounts | All deployments traceable to unique accounts | Continuous | dev,int,ref,prod | Read-only Viewer | draft | (none) | Ensures accountability and traceability for all deployments |

### SEC-024

Code/data transfer logs show integrity & secure channels

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| transfer-integrity-secure | Code/data transfer logs show integrity & secure channels | 100% transfers logged; integrity and secure channel verified | CI per change + weekly reviews | dev,int,ref,prod | Read-only Viewer | draft | (none) | Validates integrity and secure transport for all transfers |

### SEC-027

Build fails on high CVE; report archived

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| high-cve-block | Build fails when high/critical CVEs detected in application or container dependencies | 0 unresolved High/Critical CVEs at release time | CI per build + scheduled weekly scans | dev,int,ref | Read-only Viewer | draft | (none) | Prevents introduction of known vulnerabilities; gate aligned to release quality |

### SEC-028

Release pipeline blocks on critical unresolved findings

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| release-block-critical-findings | Release pipeline blocks on critical unresolved findings | 0 critical unresolved findings prior to release | Per release | dev,int,ref | Read-only Viewer | draft | (none) | Enforces remediation before release; gate consolidates multiple scanner outputs |

### SEC-029

All API endpoints enforce CIS2 JWT authentication (signature, issuer, audience, assurance claims)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| cis2-jwt-auth-enforced | All API endpoints enforce CIS2 JWT authentication (signature, issuer, audience, assurance claims) | 100% endpoints require valid CIS2 JWT; invalid/missing tokens rejected with structured 401 | CI per build + continuous runtime enforcement | dev,int,ref,prod | Read-only Viewer | draft | [FTRS-1593 CIS2 JWT auth on all endpoints](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1593) | Ensures uniform strong authentication; claim + signature validation prevents unauthorized access |

### SEC-030

Certificates and private keys stored only in approved encrypted secret stores; zero plain text exposure

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| cert-secure-storage | Certificate and private key material stored only in approved encrypted secret stores (KMS/Secrets Manager); zero plaintext in repos, images, build logs, or artifacts | 0 plaintext occurrences; 100% issuance & rotation actions use managed secrets; 100% scan coverage of git history and container layers | CI per build + weekly full history & image layer scan | dev,int,ref,prod | Read-only Viewer | draft | [FTRS-1602 Certificate secure storage](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1602) | Prevents certificate/private key exposure by enforcing exclusive use of encrypted secret storage and continuous scanning |
