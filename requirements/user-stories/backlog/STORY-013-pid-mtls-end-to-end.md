---
id: STORY-013
title: End-to-end PID mutual TLS protection
nfr_refs:
  - SEC-025
type: security
status: draft
owner: platform-team
summary: Ensure complete pathway of PID data enforces mutual TLS including intermediaries and proxies.
---

## Description
Audit all hops for PID flows; configure and validate mutual TLS from client through proxies/load balancers to backend services.

## Acceptance Criteria
- Diagram enumerating PID data path hops.
- Each hop shows successful mTLS handshake in trace.
- Attempt to intercept with non-mTLS client fails.
- Logs correlate transaction ID across hops.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| pid_path_diagram_presence | manual | Diagram stored in repo |
| hop_handshake_trace | automated | All spans show mTLS success |
| non_mtls_intercept_attempt | automated | Connection refused & logged |
| cross_hop_trace_correlation | automated | Consistent transaction ID |

## Traceability
NFRs: SEC-025
