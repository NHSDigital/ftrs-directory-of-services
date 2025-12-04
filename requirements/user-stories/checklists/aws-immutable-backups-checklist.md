# AWS Immutable Backups Adoption Checklist

- Terraform modules: `NHSDigital/terraform-aws-backup@v1.1.0` referenced (no copied bespoke code)
- Dedicated recovery account: cross-account backup copy configured
- Vault Lock: AWS Backup Vault Lock enabled and status verified
- S3 Object Lock (if applicable): compliance mode enabled on backup buckets
- KMS CMKs: restrictive key policies (no arbitrary disable/delete); least‑privilege usage for backup/restore roles
- IAM: least‑privilege for backup/restore execution and cross-account copy
- Retention: daily immutable backups retained ≥30 days (or service-defined), lifecycle/retention report captured
- Scope: essential service data backed; non‑data restore artifacts (configuration, production build, secrets, certificates) included; ≥2 immutable copies across window
- Alerts: attempted delete/overwrite blocked and alert routed to on-call
- Restore drill: annual locked-archive restore executed; evidence stored
- Upstream contribution: any new alerting/integration added to blueprint repository
