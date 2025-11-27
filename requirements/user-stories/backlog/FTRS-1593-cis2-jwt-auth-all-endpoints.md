---
story_id: STORY-SEC-030
jira_key: FTRS-1593
title: CIS2 JWT authentication enforced for all API endpoints
role: Security Engineer
goal: Enforce CIS2 JWT authentication across all API endpoints
value: Uniform strong identity assurance prevents unauthorized access
nfr_refs: [SEC-029]
status: draft
---

## Description
Implement CIS2 (Care Identity Service 2) OpenID Connect / OAuth2 authentication for every FtRS API endpoint. All requests must present a valid CIS2-issued JWT (access or ID token) meeting signature, issuer, audience, expiration, and assurance level requirements before application logic executes. This baseline security control (SEC-029) guarantees consistent identity enforcement across services.

## Acceptance Criteria
1. Valid CIS2 JWT required on 100% API endpoints (no unauthenticated endpoints except explicitly documented health probes).
2. JWT signature verified against current CIS2 JWKS (RS256 only; unknown `kid` triggers immediate JWKS refresh).
3. Claims validated: `iss` matches environment-specific issuer, `aud` matches configured client/app id, `exp` not expired (≤60s clock skew), `nbf` respected.
4. Assurance/MFA claim (`acr` or CIS2-defined equivalent) meets required level for endpoint category (baseline level ≥2, privileged endpoints may require higher).
5. Scope / role claim authorises requested endpoint; missing or insufficient scope returns 403 with OperationOutcome structure (INT-005).
6. Invalid/missing/expired/malformed tokens return 401 (authentication) or 403 (authorisation) with standardized OperationOutcome (`issue.code` = `security`).
7. JWKS cache TTL configurable (default 15m); forced refresh occurs on key miss or signature validation failure.
8. Audit log entry recorded for every auth failure including reason code (no sensitive token contents) and correlation id.
9. Metrics emitted: `auth_token_validation_total{result="success|failure",reason}` and `auth_jwks_refresh_total`.
10. Negative test suite covers: expired token, wrong issuer, wrong audience, missing assurance claim, tampered signature, replay attempt (same jti within prohibited window).
11. Performance overhead: added p95 validation latency ≤20ms compared to unauthenticated baseline (align SEC-011).
12. Configuration externalised: issuer URL, audience/client id, JWKS refresh interval, required assurance level per endpoint class.
13. Documentation updated: developer guide lists required headers, auth flow, error examples, and test endpoint for token acquisition.

## Non-Functional Acceptance
- Algorithm allow-list: RS256 only (no HS* or none)
- Token lifetime policy documented; enforce max accepted lifetime (e.g. ≤1h access tokens)
- OperationOutcome error body includes: severity=error, code=security, diagnostics reason, correlation id
- Auditing ensures no logging of full token; only jti and sub recorded where needed
- JWKS unavailability causes fail-closed (requests rejected until keys load)

## Test Strategy
| Test Type | Tooling | Focus |
|-----------|---------|-------|
| Compliance | Automated auth policy tests | 100% endpoint coverage |
| Integration | OIDC flow + scope/role tests | End-to-end acquisition & enforcement |
| Security | Negative & tamper tests | Replay, signature, claims integrity |
| Performance | Latency measurement harness | Overhead within threshold |
| Audit | Log inspection | Proper redaction & reasoning |

## Out of Scope
- UI login flows (handled separately)
- Fine-grained authorisation rules (covered by role/scope design stories)
- Token refresh UX details

## Implementation Notes
- Use robust JWT library; enable critical claim checks and algorithm restrictions.
- Implement per-request middleware early in pipeline (before business logic).
- Provide structured debug logging for failure categories (issuer mismatch, expired, scope insufficient).
- Maintain small in-memory cache of JWKS; pre-warm on startup.
- Consider optional jti replay cache (in-memory + short TTL) for high-risk operations.

## Monitoring & Metrics
- `auth_token_validation_total` counter
- `auth_token_latency_ms` histogram
- `auth_jwks_refresh_total` counter
- `auth_failure_reason_total` (partition by reason)

## Risks & Mitigation
| Risk | Impact | Mitigation |
|------|--------|-----------|
| JWKS rotation not detected | Acceptance of revoked/old keys | Miss-trigger refresh + scheduled poll |
| Latency overhead too high | User impact | Cache parsed keys; optimise claim extraction |
| Scope misconfiguration | Over/under exposure | Startup config validation & CI tests |
| Replay attacks | Privilege misuse | Optional jti tracking & short token TTL |
| Logging sensitive data | Privacy breach | Strict redaction & whitelist logging |

## Traceability
- NFR: SEC-029
- Related NFRs: SEC-011 (latency overhead), INT-005 (error format), OBS-032 (endpoint metrics visibility)
- Registry: security/expectations.yaml v1.0 (control: cis2-jwt-auth-enforced)

## Open Questions
| Topic | Question | Next Step |
|-------|----------|-----------|
| Assurance Claim | Exact CIS2 claim name? `acr` vs custom? | Confirm via CIS2 docs |
| Replay Protection | Need jti store for all endpoints? | Threat model review |
| Token Classes | Use access vs ID tokens uniformly? | Decide & document |
| Roles vs Scopes | Naming convention (e.g. `dos-search.read`)? | Authorisation design story |
| Multi-tenancy | Additional tenant claim needed? | Evaluate future requirements |