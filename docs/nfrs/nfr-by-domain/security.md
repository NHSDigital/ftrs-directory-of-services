# FtRS NFR – Security

Source: requirements/nfrs/cross-references/nfr-matrix.md

This page is auto-generated; do not hand-edit.

## NFR Codes

### Missing Metadata Checklist

- [Stories] SEC-002
- [Stories] SEC-004
- [Stories] SEC-005
- [Stories] SEC-006
- [Stories] SEC-008
- [Stories] SEC-009
- [Stories] SEC-010
- [Stories] SEC-011
- [Stories] SEC-012
- [Stories] SEC-013
- [Stories] SEC-017
- [Stories] SEC-018
- [Stories] SEC-019
- [Stories] SEC-020
- [Stories] SEC-021
- [Stories] SEC-022
- [Stories] SEC-023
- [Stories] SEC-024
- [Stories] SEC-026
- [Stories] SEC-028

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| SEC-001 | Crypto algorithms conform; weak ciphers rejected | Use only strong, approved cryptographic algorithms; weak or deprecated ciphers are blocked. | STORY-SEC-013 |
| SEC-002 | WAF security pillar checklist completed & gaps tracked | Complete the AWS/WAF security pillar checklist and track remediation actions for any gaps. | (none) |
| SEC-003 | All endpoints TLS only; storage encryption enabled | All service endpoints enforce TLS and all stored data (databases, buckets) is encrypted at rest. | FTRS-1563 |
| SEC-004 | Storage services show encryption enabled | Every storage service (S3, RDS, etc.) shows encryption enabled with managed or customer keys. | (none) |
| SEC-005 | Cross-environment data access attempts denied | Strict environment isolation: data access from one environment to another is prevented. | (none) |
| SEC-006 | No direct prod console queries detected in audit period | No direct production console queries by engineers outside approved, audited break-glass processes. | (none) |
| SEC-007 | SG rules audited; attempt broad ingress denied | Network security groups allow only narrowly scoped inbound rules; broad ingress is denied. | STORY-SEC-017 |
| SEC-008 | Perimeter scan shows no broad whitelist & secure channels | Perimeter scans show secure transport, no open broad whitelists, and hardened edge configuration. | (none) |
| SEC-009 | ASVS & CIS benchmark automation reports pass thresholds | Automated ASVS and CIS benchmark scans meet pass thresholds; failures trigger remediation. | (none) |
| SEC-010 | Annual pen test executed; remediation tickets raised & closed | Annual penetration test completed; identified issues tracked and closed. | (none) |
| SEC-011 | Security features enabled latency within SLA | Enabling security controls does not push latency beyond defined SLAs. | (none) |
| SEC-012 | IAM policy review confirms least privilege for system roles | IAM roles and policies grant least privilege; periodic reviews confirm minimal access. | (none) |
| SEC-013 | Key rotation events logged; unauthorized access denied | Cryptographic keys rotate on schedule and unauthorized access attempts are rejected and logged. | (none) |
| SEC-014 | mTLS handshake succeeds between designated services | Mutual TLS (mTLS) succeeds between designated internal services to protect sensitive flows. | FTRS-1600 |
| SEC-015 | Expiry alert fired in advance; renewal executed seamlessly | Certificate expiry is detected in advance; renewal occurs without downtime. | FTRS-1604 |
| SEC-016 | MFA enforced for all privileged infra roles | Privileged infrastructure roles require multi-factor authentication (MFA). | STORY-SEC-023 |
| SEC-017 | Scan reports zero unmanaged long-lived credentials | No long-lived unmanaged credentials; periodic scans confirm only managed secrets exist. | (none) |
| SEC-018 | Supplier audit attestation stored & verified | Third-party supplier security attestation is collected and stored for audit. | (none) |
| SEC-019 | Segmentation test confirms tenant isolation | Tenant or data segmentation tests confirm isolation boundaries hold. | (none) |
| SEC-020 | Remote connections present valid Authority certs | Remote connections present valid certificates from trusted authorities. | (none) |
| SEC-021 | Port scan matches approved diagnostic list only | Port scans reveal only approved diagnostic and service ports—no unexpected exposures. | (none) |
| SEC-022 | Utility program access restricted to approved roles | Access to powerful utility programs is restricted to approved roles. | (none) |
| SEC-023 | Deployment provenance shows unique traceable accounts | Deployment provenance shows traceable unique accounts per automated pipeline stage. | (none) |
| SEC-024 | Code/data transfer logs show integrity & secure channels | Transfer of code or data maintains integrity and uses secure channels; events are logged. | (none) |
| SEC-025 | PID requests enforce mTLS; plain text blocked | Requests containing identifiable patient data enforce mTLS; plaintext attempts are blocked. | STORY-SEC-003 |
| SEC-026 | API responses contain no unencrypted PID fields | API responses never include unencrypted patient identifiable data (PID) fields. | (none) |
| SEC-027 | Build fails on high CVE; report archived | Build pipeline blocks release when critical CVEs exceed threshold; reports archived. | STORY-SEC-002 |
| SEC-028 | Release pipeline blocks on critical unresolved findings | Releases are halted if critical unresolved security findings remain. | (none) |
| SEC-029 | All API endpoints enforce CIS2 JWT authentication (signature, issuer, audience, assurance claims) | All API endpoints enforce CIS2 JWT authentication with signature, issuer, audience and required assurance claim validation; invalid or missing tokens are rejected with structured errors. | FTRS-1593 |
| SEC-030 | Certificates and private keys stored only in approved encrypted secret stores; zero plain text exposure | Certificates and private keys are stored only in approved encrypted secret stores (e.g., Secrets Manager/KMS) with zero plaintext exposure across repositories, images, logs, or build artifacts; continuous scanning enforces compliance. | FTRS-1602 |
