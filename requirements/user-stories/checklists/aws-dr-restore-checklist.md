# AWS DR Full Restore Drill Checklist

- Schedule: Restore drill executed at least once every 24 months
- Environment: Isolated, dedicated account with no production dependencies
- Source backups: Use locked immutable archives (Vault Lock / Object Lock); note retest required if archive lock added after initial test
- Scope: Restore essential runtime data and non-data artifacts (configuration, production build, secrets, certificates)
- Runbook: Step-by-step restore runbook version-controlled and followed
- KMS/IAM: Validate CMK availability and least‑privilege permissions for restore
- Evidence: Report includes RPO/RTO metrics and data integrity verification summary
- Failures: Remediation tickets created; tracked to closure
- Clean-up: Deprovision test resources post drill; document residuals
- Upstream: Feed improvements (e.g., automation gaps) into blueprint repo
