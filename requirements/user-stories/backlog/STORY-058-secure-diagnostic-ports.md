---
id: STORY-058
title: Secure diagnostic ports and tools
nfr_refs:
  - SEC-021
type: security
status: draft
owner: platform-team
summary: Lock down diagnostic ports/tools under joint security policy with continuous monitoring.
---

## Description
Identify all diagnostic interfaces; restrict access via IAM/network rules; monitor port usage and alert on unauthorized access attempts.

## Acceptance Criteria
- Diagnostic port/tool list maintained.
- Port scan matches approved list only.
- Unauthorized access attempt triggers alert & log.
- Monthly review updates list.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| diagnostic_list_presence | manual | List committed |
| port_scan_verification | automated | Only approved ports open |
| unauthorized_diagnostic_attempt | automated | Denied & alert logged |
| monthly_review_entry | manual | Review log present |

## Traceability
NFRs: SEC-021
