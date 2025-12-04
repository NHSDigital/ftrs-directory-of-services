---
story_id: STORY-SEC-031
jira_key: FTRS-1602
title: Certificates and private keys stored only in approved encrypted secret stores
role: Security Engineer
goal: Eliminate plain text certificate/private key exposure across repos, pipelines, container images, and runtime configuration
value: Prevents credential exfiltration, supports rapid rotation, and strengthens overall platform trust boundaries
nfr_refs: [SEC-030, SEC-001, SEC-015]
status: draft
---

## Description

Implement controls and automation ensuring that all TLS/mTLS certificates (leaf + intermediates where stored) and private key material are managed exclusively through approved encrypted secret storage services (e.g. AWS Secrets Manager / KMS). No certificate or private key data may appear in source repositories, build logs, container image layers, configuration files committed to VCS, or unsecured runtime paths. Continuous scanning must detect and block any inadvertent plain text introduction.

## Acceptance Criteria

1. Inventory of all certificate & private key usage (service, purpose, rotation cadence) documented and versioned.
2. 100% certificate issuance, renewal, and rotation workflows retrieve material from approved secret store APIs (never hard-coded or manually pasted).
3. Secret scanner (git history + diffs) configured to fail CI build on detection of private key patterns (e.g. `BEGIN ... KEY`) or certificate blocks outside approved encrypted storage manifests.
4. Container image layer scan confirms 0 occurrences of certificate/private key material (leaf or intermediate) outside designated ephemeral runtime mount points.
5. Build and deployment logs redact any certificate subjects or serial numbers except minimal metadata (fingerprint hash truncated, last 4 chars allowed for audit).
6. Weekly full git history scan reports 0 plain text private key/cert artifacts; results archived with timestamp and tool version.
7. Rotation run book updated to reference secret store path IDs; performing dry-run rotation produces 0 failed handshakes and no plain text artifacts.
8. Metrics emitted: `cert_secure_storage_scan_total{result="pass|fail",scope="git|image|runtime"}` and `cert_secure_storage_detected_total{pattern}` (should remain at 0 for production after remediation).
9. Alert triggers if any scan failure >0 or if weekly scan not executed within scheduled window (≥7d since last success).
10. Compliance script verifies every declared certificate/key in inventory maps to an existing secret ARN / ID and denies merge if discrepancy found.
11. Private key permissions: secret policy restricts read access to only necessary service principals; IAM Access Analyzer report shows 0 external access paths.
12. Pre-commit hook prevents committing files containing private key or full certificate blocks unless explicitly bypassed with documented override token (tracked, audited).
13. Documentation includes examples of valid secret references vs invalid plain text embedding.

## Non-Functional Acceptance

- Control ID: `cert-secure-storage`
- Threshold: 0 plain text occurrences across scans; 100% workflows secret-managed
- Tooling: Secret scanning (git history + diff), container layer scanner, compliance inventory validator, IAM Access Analyzer
- Cadence: CI per build + weekly full history & image scan + quarterly access review
- Environments: dev, int, ref, prod

## Test Strategy

| Test Type     | Tooling                     | Focus                            |
| ------------- | --------------------------- | -------------------------------- |
| Static scan   | Secret scanner (git + diff) | Prevent plain text commits        |
| Image scan    | Layer scanner               | Absence from built images        |
| Integration   | Rotation dry-run            | Zero downtime + secret retrieval |
| Compliance    | Inventory validator         | ARN/ID mapping completeness      |
| Access review | IAM Access Analyzer         | Least privilege on secret access |

## Out of Scope

- Certificate authority issuance policy (covered by mTLS chain story FTRS-1600)
- Runtime ephemeral filesystem encryption specifics (separate infra hardening)

## Implementation Notes

- Extend existing secret scanning configuration with explicit private key regex + entropy heuristics.
- Utilize build step to mount certificates from Secrets Manager at runtime-only path; unmount post-start or keep in memory.
- Introduce structured log field `cert_inventory_mismatch` for compliance script findings.
- Provide remediation guide for accidental key commit (history rewrite + revocation + rotation steps).

## Monitoring & Metrics

- `cert_secure_storage_scan_total`
- `cert_secure_storage_detected_total`
- `cert_secure_storage_last_success_timestamp` (gauge)
- Alert: Missing weekly scan or detected_total >0 (critical severity)

## Risks & Mitigation

| Risk                             | Impact               | Mitigation                             |
| -------------------------------- | -------------------- | -------------------------------------- |
| False positive scan blocks       | Developer friction   | Tuned regex + allowlist with audit     |
| Missed historical secret         | Potential exposure   | Periodic full history rescans          |
| Over-permissive secret access    | Privilege escalation | IAM Access Analyzer enforcement        |
| Rotation script misconfiguration | Downtime             | Staged dual-cert deployment & dry-run  |
| Logging omissions                | Limited auditability | Enforced structured log schema + tests |

## Traceability

- NFR: SEC-030 (cert secure storage), SEC-001 (cipher policy), SEC-015 (cert expiry alert)
- Expectations Registry: `security/expectations.yaml` control `cert-secure-storage`

## Open Questions

| Topic                    | Question                             | Next Step                                      |
| ------------------------ | ------------------------------------ | ---------------------------------------------- |
| Secret naming convention | Use hierarchical path (service/environment)? | Define naming standard in platform ops doc     |
| Entropy threshold tuning | What size triggers false positives?  | Experiment with sample commits                 |
| Inventory format         | YAML vs JSON for ARNs?               | Decide based on existing tooling compatibility |
