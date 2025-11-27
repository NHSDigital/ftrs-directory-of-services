---
story_id: STORY-SEC-004
jira_key:
title: Storage services show encryption enabled
role: Security Engineer
goal: Implement and validate encryption at rest for all storage services
value: Ensures data confidentiality and compliance through enforced encryption
nfr_refs: [SEC-004]
status: draft
---

## Description
Implement automated validation ensuring all platform storage services (databases, object stores, block volumes, search indices, queues) have encryption at rest enabled using approved KMS keys. Provide continuous compliance reporting and remediation pathways.

## Acceptance Criteria
1. Inventory lists every storage resource with encryption status and KMS key reference.
2. 100% storage resources show encryption enabled (no exceptions in prod).
3. AWS Config / policy as code rules detect and flag non-encrypted resources within 5 minutes.
4. CI policy check blocks merges introducing unencrypted storage definitions.
5. Drift remediation script can auto-enable encryption where supported (non-destructive).
6. Dashboard shows real-time compliance percentage and list of violations (empty in steady state).
7. Weekly compliance report archived with timestamp and tooling version.
8. Alerts raised if compliance <100% for >10 minutes in prod or <95% in any non-prod environment.
9. Metrics: `storage_encryption_enabled_compliance_ratio{env}` and `storage_encryption_enabled_violations_total{env}`.
10. Evidence pack export (CSV/JSON) available for audit containing resource id, env, encryption flag, key id.

## Non-Functional Acceptance
- Control ID: `storage-encryption-enabled`
- Threshold: 100% encrypted in prod; auto-remediation triggers <100%.
- Tooling: AWS Config, Terraform policy checks, compliance dashboard, remediation script.
- Cadence: Continuous monitoring + per-merge policy evaluation + weekly report.
- Environments: dev, int, ref, prod (all monitored; stricter alerting in prod).

## Test Strategy
| Test Type | Focus | Tooling |
|-----------|-------|---------|
| Policy Unit | Detect unencrypted definitions | Terraform compliance tests |
| Integration | AWS Config rule firing | Simulated unencrypted resource |
| Remediation | Auto-enable encryption | Script dry-run & apply tests |
| Reporting | Accuracy of weekly export | Snapshot comparison |
| Alerting | Threshold breach triggers | Metrics injection in staging |

## Monitoring & Metrics
- `storage_encryption_enabled_compliance_ratio{env}` gauge
- `storage_encryption_enabled_violations_total{env}` counter
- Alert: compliance_ratio <1.0 (prod) sustained >10m.

## Implementation Notes
- Use tagging or resource graph queries to build inventory.
- Map KMS key ARNs; verify rotation policy separately (other control).
- Provide CLI `scripts/nfr/storage_encryption_check.py` for local & CI use.

## Risks & Mitigation
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Unsupported legacy resource | Partial coverage | Document exceptions & plan migration |
| False positives | Noise | Rule tuning & allowlist with expiration |
| Auto-remediation failure | Non-compliance | Fallback manual runbook & alerting |

## Traceability
- NFR: SEC-004
- Expectations Registry: `security/expectations.yaml` (encryption-at-rest related control)

## Open Questions
| Topic | Question | Next Step |
|-------|----------|-----------|
| Key rotation linkage | Separate story or same? | Split to distinct rotation control story |
| Cross-account keys | Standardize approach? | Define pattern in platform security guide |
