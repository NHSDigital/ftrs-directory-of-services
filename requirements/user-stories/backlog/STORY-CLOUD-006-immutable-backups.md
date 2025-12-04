---
code: STORY-CLOUD-006
as_a: Platform_Engineer
i_want: enforce_immutable_backup_policy_and_retention
so_that: backups_cannot_be_tampered_and_support_point_in_time_recovery
business_value: Ensures recoverability and reduces ransomware impact
nfr_refs: [NFR-BACKUP-IMMUTABLE-01]
nfr_tags: [backup, security, dr]
acceptance_criteria:
  - GIVEN blueprint adoption WHEN provisioning THEN terraform references `NHSDigital/terraform-aws-backup@v1.1.0` modules (no copied bespoke code)
  - GIVEN backup vault WHEN created THEN AWS Backup Vault Lock enabled in dedicated recovery account with cross-account copy
  - GIVEN S3 backups WHEN applicable THEN S3 Object Lock in compliance mode enabled for backup buckets
  - GIVEN KMS configuration WHEN reviewed THEN CMK policies prevent disable/delete by non-approved roles; backup/restore IAM roles least-privileged
  - GIVEN retention policy WHEN configured THEN daily immutable backups retained ≥30 days (or product-defined) with lifecycle/retention reports
  - GIVEN non-data artifacts WHEN enumerated THEN configuration, production build, secrets, certificates backed immutably with ≥2 copies across window
  - GIVEN attempted modification WHEN immutability period active THEN delete/overwrite blocked and alert routed to on-call
  - GIVEN restore validation WHEN annual window THEN locked-archive restore drill executed and evidenced
out_of_scope:
  - Cross-cloud backup replication
notes: |
  Evidence: policy definitions, storage configuration screenshots, automated test of immutability block.
  Checklist: requirements/user-stories/checklists/aws-immutable-backups-checklist.md
  Blueprint: https://github.com/NHSDigital/terraform-aws-backup/tree/v1.1.0
  Position: requirements/red-lines/cloud-backups.md
---

# Summary

Immutable backups with enforced retention safeguards.

## Detail

Consume the NHS AWS cloud backups blueprint (v1.1) as Terraform modules to provision immutable backups with a locked archive in a dedicated recovery account. Use AWS Backup with Vault Lock (and S3 Object Lock where applicable), enforce least‑privilege IAM and robust KMS key policies. Retain daily backups for at least 30 days unless a product-specific retention is agreed. Back up essential service data required to restore service, plus non‑data artifacts (configuration, production build, secrets, certificates). Contribute any required enhancements (e.g., alerting options) upstream to the blueprint. Validate annually that a locked archive restores successfully.

## Deriving Acceptance Criteria from NFRs

- NFR-BACKUP-IMMUTABLE-01:
  - Module consumption proves blueprint alignment and upgradeability.
  - Vault/Object Lock enforce write-once; cross-account copy provides isolation.
  - Retention reports demonstrate ≥30 days immutable coverage.
  - KMS/IAM controls prevent tampering; alerts fire on blocked operations.
  - Annual restore drill evidences end-to-end recoverability of locked archives.

## INVEST Checklist

- Independent: Can proceed without DR restore scheduling.
- Negotiable: Specific storage class technology.
- Valuable: Protects backups from ransomware/tampering.
- Estimable: Policy configuration + test attempt + alert wiring.
- Small: Limited to backup policy and validation steps.
- Testable: Storage configuration, lifecycle report, alert log.
