---
id: STORY-042
title: Encrypt data at rest for all persistence layers
nfr_refs:
  - SEC-004
type: security
status: draft
owner: platform-team
summary: Ensure all storage services (DynamoDB, S3, OpenSearch, RDS, EBS, backups) have encryption at rest enabled with managed keys.
---

## Description
All persistent storage locations must enforce encryption at rest using approved KMS keys. Backups must inherit encryption. Key policies restrict access.

## Acceptance Criteria
- KMS CMKs configured or AWS-managed keys documented per service.
- Storage encryption flags set (SSE for S3, encryption for DynamoDB tables, OpenSearch domains, RDS snapshots, EBS volumes).
- Backup artifacts show encrypted status.
- Unauthorized key usage attempt denied and logged.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| kms_key_policy_review | manual | Least privilege policy present |
| storage_encryption_scan | automated | 100% resources encrypted |
| backup_encryption_check | automated | 100% backups encrypted |
| unauthorized_key_use | automated | Access denied; audit log entry |

## Traceability
NFRs: SEC-004
