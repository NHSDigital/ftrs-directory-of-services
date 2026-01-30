---
domain: security
version: 1.1.0
last_updated: 2025-11-25
source: performance/initial.md (relocated security draft)
status: draft
summary: >-
  Consolidated security non-functional requirements for FtRS covering encryption,
  data protection, network & application security, key & certificate management,
  IAM, supplier obligations, PID handling, continuous penetration / dependency
  vulnerability testing, universal API authentication (CIS2 JWT) and secure
  certificate/private key storage.
---

# Security NFRs (FtRS)

## 0. Background

FtRS is a Priority Application and Mission Critical Infrastructure. Security controls must
preserve confidentiality, integrity, availability and traceability while minimising friction for
legitimate clinical and operational workflows.

## 1. Overall Security

| Code    | Requirement                                                                                                         | Rationale                                                       | Verification                                              | Tags                     |
| ------- | ------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- | --------------------------------------------------------- | ------------------------ |
| SEC-001 | Use NHSE approved cryptographic algorithms (GPG v4.0) for all encryption features (application + cloud provider).   | Align with organisational policy; prevent weak cipher adoption. | Configuration inspection; automated crypto policy audit.         | encryption, policy       |
| SEC-002 | Align solution design with cloud Well-Architected Framework security pillar guidance (design→delivery→maintenance). | Embed best practice early, reduce rework/security debt.         | Architecture review checklist; periodic WAF gap analysis. | architecture, governance |

## 2. Data Security

| Code    | Requirement                                                                                    | Rationale                                    | Verification                                                     | Tags                   |
| ------- | ---------------------------------------------------------------------------------------------- | -------------------------------------------- | ---------------------------------------------------------------- | ---------------------- |
| SEC-003 | Encrypt data in transit (TLS1.2+, prefer TLS1.3) between all components (internal & external). | Prevent interception / tampering.            | Automated endpoint scan; failed HTTP downgrade tests.            | encryption, transit    |
| SEC-004 | Encrypt data at rest for all persistence layers.                                               | Mitigate data exposure on media loss.        | Cloud KMS configuration + storage service encryption flags.             | encryption, at-rest    |
| SEC-005 | Enforce strict environment data isolation (each environment accesses only its own data).               | Contain impact radius; support safe testing. | IAM policy diff; attempted cross-environment access negative tests.      | isolation, environment |
| SEC-006 | Disallow direct human access to production data stores (no raw console queries).               | Reduce insider & accidental risk.            | Audit of break-glass approvals; absence of interactive sessions. | least-privilege, ops   |

## 3. Network Security

| Code    | Requirement                                                                                                                       | Rationale                            | Verification                                    | Tags                     |
| ------- | --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ | ----------------------------------------------- | ------------------------ |
| SEC-007 | Apply least-privilege firewall/security group rules per compute resource; deny by default.                                        | Minimise lateral movement.           | IaC policy lint; security group diff scanning.  | network, least-privilege |
| SEC-008 | Secure all inbound/outbound connectivity (VPN, public internet) with authentication & encryption; forbid broad subnet whitelists. | Prevent unauthorised ingress/egress. | Pen test; configuration scan for 0.0.0.0/0 exceptions. | perimeter, vpn           |

## 4. Application Security

| Code    | Requirement                                                                                            | Rationale                                           | Verification                                                      | Tags               |
| ------- | ------------------------------------------------------------------------------------------------------ | --------------------------------------------------- | ----------------------------------------------------------------- | ------------------ |
| SEC-009 | Implement OWASP ASVS L1+L2 controls where applicable; monitor CIS AWS benchmarks.                      | Standardised hardening; reduce common flaw classes. | Automated ASVS checklist mapping; CIS benchmark scan reports.     | appsec, standards  |
| SEC-010 | Perform independent external penetration test annually & on significant perimeter change.              | Detect unknown vulnerabilities early.               | Test reports archived; remediation tracking.                      | pen-test, cadence  |
| SEC-011 | Security controls must not materially degrade legitimate user experience within agreed SLAs.           | Maintain usability/adoption.                        | UX + performance regression tests with security features enabled. | usability, balance |
| SEC-012 | Access to application resources via defined IAM policies for human & system identities (roles/groups). | Unified access control; auditability.               | IAM policy review; access attempt tests.                          | iam, access        |

## 5. Key Management

| Code    | Requirement                                                                                                             | Rationale                                         | Verification                                                          | Tags           |
| ------- | ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------- | --------------------------------------------------------------------- | -------------- |
| SEC-013 | Restrict cryptographic key access (RBAC + least privilege); support secure generation, rotation, archival and deletion. | Prevent key compromise; ensure lifecycle hygiene. | KMS key rotation configuration; access audit logs; rotation success metrics. | kms, lifecycle |

## 6. Certificate Management

| Code    | Requirement                                                                 | Rationale                         | Verification                                             | Tags                     |
| ------- | --------------------------------------------------------------------------- | --------------------------------- | -------------------------------------------------------- | ------------------------ |
| SEC-014 | Use certificates for mutual authentication between relevant FtRS resources. | Assure endpoint identity.         | mTLS handshake tests; cert validation logs.              | certificates, mTLS       |
| SEC-015 | Provide proactive certificate expiry alerting and seamless renewal process. | Avoid outage due to expired cert. | Monitoring alert test; renewal run book execution record. | certificates, operations |

## 7. Infrastructure Access Management

| Code    | Requirement                                                                                                      | Rationale                   | Verification                                         | Tags             |
| ------- | ---------------------------------------------------------------------------------------------------------------- | --------------------------- | ---------------------------------------------------- | ---------------- |
| SEC-016 | Grant infra resource access only via approved human & system identities; enforce MFA for privileged human roles. | Reduce breach blast radius. | IAM analytics; MFA enforcement report.               | iam, infra       |
| SEC-017 | Authentication uses centrally governed identities; no long-lived unmanaged credentials.                          | Limit secret sprawl.        | Credential inventory scan; secret TTL policy checks. | secrets, hygiene |

## 8. Supplier Security

| Code    | Requirement                                                                                                       | Rationale                                 | Verification                                                  | Tags                       |
| ------- | ----------------------------------------------------------------------------------------------------------------- | ----------------------------------------- | ------------------------------------------------------------- | -------------------------- |
| SEC-018 | Supplier-controlled networks/services protected from external access; only Authority-approved entities permitted. | Maintain contractual security boundaries. | Supplier audit attestation; network ACL review.               | supplier, network          |
| SEC-019 | Enforce logical separation between Authority workloads and other supplier customers.                              | Prevent cross-tenant leakage.             | Segmentation test results; VLAN/VPC isolation evidence.       | multi-tenant, isolation    |
| SEC-020 | Authenticate remote server/app connections using Authority-issued digital certificates.                           | Ensure trust chain integrity.             | Cert fingerprint matching audit.                              | certificates, supplier     |
| SEC-021 | Secure diagnostic ports/tools under joint Security Policies.                                                      | Prevent exploitation via mgmt interfaces. | Port scan diff vs approved list.                              | hardening, ports           |
| SEC-022 | Restrict access to system utility programmes to approved entities only.                                           | Avoid privilege escalation.               | Access logs; role permission diff.                            | least-privilege, utilities |
| SEC-023 | Distribute & execute applications under unique traceable user accounts; block unapproved code execution.          | Strengthen non-repudiation & integrity.   | CI/CD provenance attestations; runtime allowlist enforcement. | provenance, integrity      |
| SEC-024 | Maintain secure code & data handling during transfer across supplier systems.                                     | Prevent tampering/exfiltration.           | Secure transport scan; checksum verification pipeline.        | integrity, transit         |

## 9. Patient Identifiable Data (PID)

| Code    | Requirement                                                                 | Rationale                         | Verification                                     | Tags            |
| ------- | --------------------------------------------------------------------------- | --------------------------------- | ------------------------------------------------ | --------------- |
| SEC-025 | Encrypt PID in transit with mutual authentication unless formally excepted. | Safeguard sensitive patient data. | TLS/mTLS test; attempt plain-text rejection.     | pid, encryption |
| SEC-026 | External APIs must not expose unencrypted PID fields.                       | Prevent accidental leakage.       | API contract scan; response sampling inspection. | pid, api        |

## 10. Penetration & Vulnerability Testing

| Code    | Requirement                                                                                                       | Rationale                               | Verification                                       | Tags                    |
| ------- | ----------------------------------------------------------------------------------------------------------------- | --------------------------------------- | -------------------------------------------------- | ----------------------- |
| SEC-027 | Automate dependency vulnerability scanning (focus OWASP A06:2021) per build.                                      | Early detection of outdated components. | CI scan reports; failing build on high severity.   | dependencies, vuln-scan |
| SEC-028 | Include pen test & vulnerability results in environment reporting; block release on unresolved critical findings. | Enforce remediation discipline.         | Release gate logs; tracked ticket closure metrics. | governance, release     |

## 11. Authentication & Secure Certificate Storage

| Code    | Requirement                                                                                                                                                                 | Rationale                                                                                      | Verification                                                                                                                            | Tags                           |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| SEC-029 | Enforce CIS2 JWT authentication (signature, issuer, audience, assurance claim) on 100% API endpoints; reject invalid/missing tokens with structured errors.                 | Universal strong auth prevents unauthorized access & supports consistent audit.                | JWT validator integration tests (positive/negative); structured 401/403 OperationOutcome responses; runtime metrics for token failures. | authentication, jwt, cis2      |
| SEC-030 | Store all certificates and private keys only in approved encrypted secret stores (e.g. AWS Secrets Manager/KMS); zero plain text exposure in repos, images, logs, artifacts. | Eliminates risk of credential/key exfiltration; ensures controlled lifecycle & rapid rotation. | Secret scanning (git history + diffs); container layer scan; artifact/log redaction checks; inventory vs secret ARN compliance script.  | certificates, secrets, storage |

## Glossary (Selected)

Cryptographic Key: Parameter determining output of cryptographic algorithm.
PID: Patient Identifiable Data – any data combination enabling patient identification.

## Traceability & Next Actions

- Ensure all codes (SEC-001..SEC-030) present in `index.yaml` & cross-reference matrix.
- Derive / refine acceptance criteria & stories for SEC-029 (CIS2 JWT) and SEC-030 (secure storage) where not already implemented.
- Implement linter to validate `nfr_refs` and detect missing overview entries (e.g. future SEC-\* additions).
