---
story_id: STORY-SEC-028
jira_key:
title: API responses contain no unencrypted PID fields
role: Security Engineer
goal: Implement and validate: API responses contain no unencrypted PID fields
value: Ensures sensitive data is never returned unencrypted
nfr_refs: [SEC-026]
status: draft
---

## Description
Implement automated validation for: API responses contain no unencrypted PID fields.

## Acceptance Criteria
1. 0 occurrences of unencrypted PID in responses
2. Tooling: Integration tests + response scanners operational
3. Cadence: CI per build + periodic production sampling validated
4. Environments: int, ref, prod covered
5. Monitoring configured and alerting tested

## Non-Functional Acceptance
- Control ID: `pid-no-plaintext-response`\n- Threshold: 0 occurrences of unencrypted PID in responses\n- Tooling: Integration tests + response scanners\n- Cadence: CI per build + periodic production sampling\n- Environments: int, ref, prod

## Test Strategy
| Test Type | Tooling | Focus |
|-----------|---------|-------|
| Compliance | Automated tooling | Policy enforcement |
| Integration | CI pipeline | Continuous validation |
| Audit | Manual review | Compliance assessment |

## Out of Scope
Implementation details to be refined during sprint planning

## Implementation Notes
- Ensures sensitive data is never returned unencrypted
- Cadence: CI per build + periodic production sampling
- Status: draft

## Monitoring & Metrics
- `pid_no_plaintext_response_compliance_status` gauge
- `pid_no_plaintext_response_violations_total` counter

## Risks & Mitigation
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Configuration drift | Non-compliance | Automated remediation |
| Tool failures | Missed violations | Redundant checks |

## Traceability
- NFR: SEC-026
- Registry: security/expectations.yaml v1.0

## Open Questions
None
