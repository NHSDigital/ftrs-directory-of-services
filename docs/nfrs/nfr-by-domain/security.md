# FtRS NFR – Security

This page is auto-generated; do not hand-edit.

## NFR Codes

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| SEC-001 | Crypto algorithms conform; weak ciphers rejected | Use only strong, approved cryptographic algorithms; weak or deprecated ciphers are blocked. | STORY-SEC-013 |
| SEC-002 | WAF security pillar checklist completed & gaps tracked | Complete the AWS/WAF security pillar checklist and track remediation actions for any gaps. | STORY-SEC-014, STORY-SEC-031 |
| SEC-003 | All endpoints TLS only; storage encryption enabled | All service endpoints enforce TLS and all stored data (databases, buckets) is encrypted at rest. | [FTRS-1563](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1563) |
| SEC-004 | Storage services show encryption enabled | Every storage service (S3, RDS, etc.) shows encryption enabled with managed or customer keys. | STORY-SEC-004, STORY-SEC-015, STORY-SEC-032 |
| SEC-005 | Cross-environment data access attempts denied | Strict environment isolation: data access from one environment to another is prevented. | STORY-SEC-011, STORY-SEC-033 |
| SEC-006 | No direct prod console queries detected in audit period | No direct production console queries by engineers outside approved, audited break-glass processes. | STORY-SEC-016, STORY-SEC-034 |
| SEC-007 | SG rules audited; attempt broad ingress denied | Network security groups allow only narrowly scoped inbound rules; broad ingress is denied. | STORY-SEC-017 |
| SEC-008 | Perimeter scan shows no broad whitelist & secure channels | Perimeter scans show secure transport, no open broad whitelists, and hardened edge configuration. | STORY-SEC-018, STORY-SEC-035 |
| SEC-009 | ASVS & CIS benchmark automation reports pass thresholds | Automated ASVS and CIS benchmark scans meet pass thresholds; failures trigger remediation. | STORY-SEC-004, STORY-SEC-036 |
| SEC-010 | Annual pen test executed; remediation tickets raised & closed | Annual penetration test completed; identified issues tracked and closed. | STORY-SEC-019, STORY-SEC-037 |
| SEC-011 | Security features enabled latency within SLA | Enabling security controls does not push latency beyond defined SLAs. | STORY-SEC-020, STORY-SEC-038 |
| SEC-012 | IAM policy review confirms least privilege for system roles | IAM roles and policies grant least privilege; periodic reviews confirm minimal access. | STORY-SEC-005, STORY-SEC-030, STORY-SEC-039 |
| SEC-013 | Key rotation events logged; unauthorized access denied | Cryptographic keys rotate on schedule and unauthorized access attempts are rejected and logged. | STORY-SEC-021, STORY-SEC-040 |
| SEC-014 | mTLS handshake succeeds between designated services | Mutual TLS (mTLS) succeeds between designated internal services to protect sensitive flows. | STORY-SEC-006 |
| SEC-015 | Expiry alert fired in advance; renewal executed seamlessly | Certificate expiry is detected in advance; renewal occurs without downtime. | STORY-SEC-022 |
| SEC-016 | MFA enforced for all privileged infra roles | Privileged infrastructure roles require multi-factor authentication (MFA). | STORY-SEC-023 |
| SEC-017 | Scan reports zero unmanaged long-lived credentials | No long-lived unmanaged credentials; periodic scans confirm only managed secrets exist. | STORY-SEC-010, STORY-SEC-041 |
| SEC-018 | Supplier audit attestation stored & verified | Third-party supplier security attestation is collected and stored for audit. | STORY-SEC-024, STORY-SEC-042 |
| SEC-019 | Segmentation test confirms tenant isolation | Tenant or data segmentation tests confirm isolation boundaries hold. | STORY-SEC-012, STORY-SEC-043 |
| SEC-020 | Remote connections present valid Authority certs | Remote connections present valid certificates from trusted authorities. | STORY-SEC-007, STORY-SEC-044 |
| SEC-021 | Port scan matches approved diagnostic list only | Port scans reveal only approved diagnostic and service ports—no unexpected exposures. | STORY-SEC-008, STORY-SEC-045 |
| SEC-022 | Utility program access restricted to approved roles | Access to powerful utility programs is restricted to approved roles. | STORY-SEC-025, STORY-SEC-046 |
| SEC-023 | Deployment provenance shows unique traceable accounts | Deployment provenance shows traceable unique accounts per automated pipeline stage. | STORY-SEC-026, STORY-SEC-047 |
| SEC-024 | Code/data transfer logs show integrity & secure channels | Transfer of code or data maintains integrity and uses secure channels; events are logged. | STORY-SEC-027, STORY-SEC-048 |
| SEC-025 | PID requests enforce mTLS; plain text blocked | Requests containing identifiable patient data enforce mTLS; plaintext attempts are blocked. | STORY-SEC-003 |
| SEC-026 | API responses contain no unencrypted PID fields | API responses never include unencrypted patient identifiable data (PID) fields. | STORY-SEC-028, STORY-SEC-049 |
| SEC-027 | Build fails on high CVE; report archived | Build pipeline blocks release when critical CVEs exceed threshold; reports archived. | STORY-SEC-002 |
| SEC-028 | Release pipeline blocks on critical unresolved findings | Releases are halted if critical unresolved security findings remain. | STORY-SEC-009, STORY-SEC-050 |
| SEC-029 | All API endpoints enforce CIS2 JWT authentication (signature, issuer, audience, assurance claims) | All API endpoints enforce CIS2 JWT authentication with signature, issuer, audience and required assurance claim validation; invalid or missing tokens are rejected with structured errors. | [FTRS-1593](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1593) |
| SEC-030 | Certificates and private keys stored only in approved encrypted secret stores; zero plain text exposure | Certificates and private keys are stored only in approved encrypted secret stores (e.g., Secrets Manager/KMS) with zero plaintext exposure across repositories, images, logs, or build artifacts; continuous scanning enforces compliance. | STORY-SEC-030 |

## Controls

### SEC-001

Use only strong, approved cryptographic algorithms; weak or deprecated ciphers are blocked.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-001](#sec-001) | crypto-cipher-policy | Crypto algorithms conform; weak ciphers rejected | TLS1.2+ only; no weak/legacy ciphers enabled | TLS scanner + configuration policy checks | CI per change + monthly scan | dev,int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Enforces modern TLS standards; automated scans detect drift |

### SEC-002

Complete the AWS/WAF security pillar checklist and track remediation actions for any gaps.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-002](#sec-002) | waf-pillar-checklist | WAF security pillar checklist completed & gaps tracked | Checklist complete; 100% actions tracked; 0 open critical gaps | WAF checklist repository + issue tracker gate | Quarterly + on change | dev,int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Formalizes WAF security governance; gaps tracked to closure |

### SEC-003

All service endpoints enforce TLS and all stored data (databases, buckets) is encrypted at rest.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-003](#sec-003) | tls-encryption-endpoints | All public/private API endpoints enforce TLS; storage services enable encryption at rest | 100% compliant across resources | AWS Config rules + Terraform policy checks | Continuous (real-time) with CI enforcement on change | dev,int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Aligns with NHS policy; Config provides continuous guardrails; CI blocks drift |

### SEC-004

Every storage service (S3, RDS, etc.) shows encryption enabled with managed or customer keys.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-004](#sec-004) | storage-encryption-enabled | Storage services show encryption enabled | 100% storage resources encrypted at rest | AWS Config rules + Terraform policy checks | Continuous + CI enforcement | dev,int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Guardrails ensure encryption at rest across services |

### SEC-005

Strict environment isolation: data access from one environment to another is prevented.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-005](#sec-005) | cross-env-access-denied | Cross-env data access attempts denied and logged | 100% denial; audit logs prove enforcement | IAM policies + SCP guardrails + audit log queries | CI policy checks + monthly audit review | dev,int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Prevents accidental or malicious cross-environment data access |

### SEC-006

No direct production console queries by engineers outside approved, audited break-glass processes.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-006](#sec-006) | prod-console-access-audit | No direct prod console queries detected in audit period | 0 non-approved console queries in audit period | CloudTrail + SIEM audit queries | Weekly audit + alerting | prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Detects improper direct access to production consoles |

### SEC-007

Network security groups allow only narrowly scoped inbound rules; broad ingress is denied.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-007](#sec-007) | sg-broad-ingress-denied | SG rules audited; attempt broad ingress denied | 0 broad (0.0.0.0/0) ingress on restricted ports | AWS Config + IaC linter | CI per change + monthly audit | dev,int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Prevents risky network exposure via security groups |

### SEC-008

Perimeter scans show secure transport, no open broad whitelists, and hardened edge configuration.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-008](#sec-008) | perimeter-scan | Perimeter scan shows no broad whitelist & secure channels | No broad whitelists; only secure channels reported | External perimeter scanner + config validation | Monthly + on change | int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Confirms perimeter hygiene and secure external exposure |

### SEC-009

Automated ASVS and CIS benchmark scans meet pass thresholds; failures trigger remediation.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-009](#sec-009) | cis-benchmark-compliance | CIS benchmark automation reports meet pass thresholds for targeted services | >= 95% controls passing; all high-severity findings remediated or exceptioned | CIS benchmark tooling integrated in CI and periodic audits | CI per change + monthly full audit | dev,int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Baseline hardening validated continuously; monthly cadence catches drift |

### SEC-010

Annual penetration test completed; identified issues tracked and closed.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-010](#sec-010) | annual-pentest | Annual pen test executed; remediation tickets raised & closed | Pen test executed; all critical findings remediated or exceptioned | Pen test reports + remediation tracking | Annual | prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Validates security posture with external testing and tracked remediation |

### SEC-011

Enabling security controls does not push latency beyond defined SLAs.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-011](#sec-011) | security-features-latency-sla | Security features enabled latency within SLA | Added latency within agreed SLA per endpoint | Performance tests with security features enabled | CI perf checks + monthly regression review | int,ref,prod | crud-apis,dos-search | draft | Ensures security does not breach performance SLAs |

### SEC-012

IAM roles and policies grant least privilege; periodic reviews confirm minimal access.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-012](#sec-012) | iam-least-privilege | IAM policy review confirms least privilege for system roles | >= 95% policies compliant; no wildcard resource; explicit actions only | IAM Access Analyzer + policy linters | CI per change + quarterly audit | dev,int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Continuous analysis prevents privilege creep; periodic review catches drift |

### SEC-013

Cryptographic keys rotate on schedule and unauthorized access attempts are rejected and logged.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-013](#sec-013) | key-rotation-logging | Key rotation events logged; unauthorized access denied | 100% rotation events logged; 0 unauthorized key access | KMS/AWS logs + SIEM correlation | Quarterly audit + CI checks on policy | dev,int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Audit trail confirms rotation compliance and denial of unauthorized access |

### SEC-014

Mutual TLS (mTLS) succeeds between designated internal services to protect sensitive flows.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-014](#sec-014) | mtls-service-handshake | mTLS handshake succeeds between designated services using ITOC-approved CA signed leaf + intermediate certs (chain to ITOC root); invalid/expired/revoked/untrusted-issuer/weak-cipher attempts rejected | 100% handshake success for valid ITOC chain; 0 successful handshakes with expired, revoked, weak cipher, or non-ITOC issuer certs; rotation introduces 0 downtime | Integration tests (valid/expired/revoked/wrong-CA/weak-cipher) + gateway cert management + OCSP/CRL polling | CI per build + cert rotation checks + revocation poll ≤5m | int,ref,prod | dos-search,crud-apis | draft | Enforces trusted ITOC certificate chain, strong ciphers, timely revocation, and zero-downtime rotation for secure service-to-service trust |

### SEC-015

Certificate expiry is detected in advance; renewal occurs without downtime.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-015](#sec-015) | cert-expiry-alert-renewal | Expiry alert fired in advance; renewal executed seamlessly | >= 30 days prior alert; 0 outage during renewal | Cert manager alerts + renewal runbooks | Continuous monitoring | int,ref,prod | crud-apis,dos-search | draft | Proactive renewal prevents downtime; alerts ensure timely action |

### SEC-016

Privileged infrastructure roles require multi-factor authentication (MFA).

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-016](#sec-016) | privileged-mfa-enforced | MFA enforced for all privileged infra roles | 100% privileged roles require MFA | IAM policy checks + directory audit | CI policy checks + quarterly audit | dev,int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Strong authentication for privileged accounts reduces risk |

### SEC-017

No long-lived unmanaged credentials; periodic scans confirm only managed secrets exist.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-017](#sec-017) | zero-long-lived-credentials | Scan reports zero unmanaged long-lived credentials | 0 unmanaged long-lived credentials | Secret scanners + IAM credential report audit | CI per build + weekly audit | dev,int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Reduces risk from forgotten credentials; continuous scanning plus scheduled audits |

### SEC-018

Third-party supplier security attestation is collected and stored for audit.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-018](#sec-018) | supplier-audit-attestation | Supplier audit attestation stored & verified | Attestations current; verification completed | Supplier management system + evidence repository | Annual + on contract change | prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Ensures supplier compliance and auditable records |

### SEC-019

Tenant or data segmentation tests confirm isolation boundaries hold.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-019](#sec-019) | segmentation-tenant-isolation | Segmentation test confirms tenant isolation | 100% isolation; no cross-tenant data access observed | Segmentation test suite + log verification | Quarterly | int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Ensures strict isolation between tenants per policy |

### SEC-020

Remote connections present valid certificates from trusted authorities.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-020](#sec-020) | authority-cert-validation | Remote connections present valid Authority certs; invalid certs rejected | 100% validation events pass; 0 successful connections with invalid certs | TLS config tests + runtime observation in logs | CI policy validation + runtime checks | int,ref,prod | etl-ods | draft | External data source interactions require strict certificate validation |

### SEC-021

Port scans reveal only approved diagnostic and service ports—no unexpected exposures.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-021](#sec-021) | port-scan-diagnostic-only | Port scan matches approved diagnostic list only | No unexpected open ports detected outside approved list | Automated port scan + baseline comparison | Monthly + CI smoke on infra changes | dev,int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Detects misconfigurations; verifies adherence to diagnostic port policy |

### SEC-022

Access to powerful utility programs is restricted to approved roles.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-022](#sec-022) | utility-access-restricted | Utility program access restricted to approved roles | Only approved roles can access utility programs | RBAC policy checks + audit logs | CI policy checks + monthly audit | dev,int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Prevents misuse of diagnostic utilities |

### SEC-023

Deployment provenance shows traceable unique accounts per automated pipeline stage.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-023](#sec-023) | deployment-provenance-traceable | Deployment provenance shows unique traceable accounts | All deployments traceable to unique accounts | CI/CD audit trails + commit signing | Continuous | dev,int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Ensures accountability and traceability for all deployments |

### SEC-024

Transfer of code or data maintains integrity and uses secure channels; events are logged.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-024](#sec-024) | transfer-integrity-secure | Code/data transfer logs show integrity & secure channels | 100% transfers logged; integrity and secure channel verified | Checksums/signatures + TLS enforcement + audit logs | CI per change + weekly reviews | dev,int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Validates integrity and secure transport for all transfers |

### SEC-025

Requests containing identifiable patient data enforce mTLS; plaintext attempts are blocked.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-025](#sec-025) | pid-mtls-enforcement | Requests carrying PID fields require mutual TLS; plaintext requests blocked | 100% enforcement on designated endpoints | API gateway/WAF policy + integration tests | CI policy validation + continuous enforcement | int,ref,prod | crud-apis,dos-search | draft | Ensures transport security for sensitive data; test coverage verifies enforcement |

### SEC-026

API responses never include unencrypted patient identifiable data (PID) fields.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-026](#sec-026) | pid-no-plaintext-response | API responses contain no unencrypted PID fields | 0 occurrences of unencrypted PID in responses | Integration tests + response scanners | CI per build + periodic production sampling | int,ref,prod | crud-apis,dos-search | draft | Ensures sensitive data is never returned unencrypted |

### SEC-027

Build pipeline blocks release when critical CVEs exceed threshold; reports archived.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-027](#sec-027) | high-cve-block | Build fails when high/critical CVEs detected in application or container dependencies | 0 unresolved High/Critical CVEs at release time | SCA scanner (e.g., OWASP Dependency-Check), container scanner, pipeline gate | CI per build + scheduled weekly scans | dev,int,ref | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Prevents introduction of known vulnerabilities; gate aligned to release quality |

### SEC-028

Releases are halted if critical unresolved security findings remain.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-028](#sec-028) | release-block-critical-findings | Release pipeline blocks on critical unresolved findings | 0 critical unresolved findings prior to release | Pipeline gate integrated with SCA, container, IaC scanners | Per release | dev,int,ref | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Enforces remediation before release; gate consolidates multiple scanner outputs |

### SEC-029

All API endpoints enforce CIS2 JWT authentication with signature, issuer, audience and required assurance claim validation; invalid or missing tokens are rejected with structured errors.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-029](#sec-029) | cis2-jwt-auth-enforced | All API endpoints enforce CIS2 JWT authentication (signature, issuer, audience, assurance claims) | 100% endpoints require valid CIS2 JWT; invalid/missing tokens rejected with structured 401 | OIDC integration tests + JWT validator + JWKS cache monitor | CI per build + continuous runtime enforcement | dev,int,ref,prod | crud-apis,dos-search,etl-ods,read-only-viewer | draft | Ensures uniform strong authentication; claim + signature validation prevents unauthorized access |

### SEC-030

Certificates and private keys are stored only in approved encrypted secret stores (e.g., Secrets Manager/KMS) with zero plaintext exposure across repositories, images, logs, or build artifacts; continuous scanning enforces compliance.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [SEC-030](#sec-030) | cert-secure-storage | Certificate and private key material stored only in approved encrypted secret stores (KMS/Secrets Manager); zero plaintext in repos, images, build logs, or artifacts | 0 plaintext occurrences; 100% issuance & rotation actions use managed secrets; 100% scan coverage of git history and container layers | Secret scanning (git history + container layers), CI policy checks, artifact scanner, repo pre-commit hooks | CI per build + weekly full history & image layer scan | dev,int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Prevents certificate/private key exposure by enforcing exclusive use of encrypted secret storage and continuous scanning |
