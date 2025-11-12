---
id: STORY-177
title: Validate query parameters and return OperationOutcome on errors
status: draft
type: functional
owner: gp-search-team
nfr_refs:
  - REL-016
  - OBS-011
  - SEC-009
summary: As a client I want clear error responses when I submit invalid parameters so that I can correct mistakes quickly.
---

### Acceptance Criteria
1. Missing `_revinclude` returns 400 OperationOutcome with issue code `required` and UKCore INVALID_SEARCH_DATA coding.
2. Invalid identifier system returns 400 with `code-invalid` and diagnostics describing expected system.
3. Malformed ODS code regex violation returns 400 with `value` issue.
4. Unknown error paths return 500 OperationOutcome with fatal structure issue only (no internal details).
5. All validation failures logged with structured classification (OBS-011).
6. Security validation aligned to OWASP input handling guidance (SEC-009).
7. Server-side errors produce graceful message per REL-016 intent.

### Test Notes
| Scenario | Tool | Data | Expected |
|----------|------|------|----------|
| Missing param | pytest | Omit _revinclude | 400 OperationOutcome required issue |
| Wrong system | pytest | identifier=wrong|A1234 | 400 code-invalid issue |
| Bad format | pytest | identifier=odsOrganisationCode|A!@ | 400 value issue |
| Unexpected exception | pytest + monkeypatch | Force mapper raise | 500 OperationOutcome |

### Traceability
NFR refs ensure graceful, classified, secure error handling.
