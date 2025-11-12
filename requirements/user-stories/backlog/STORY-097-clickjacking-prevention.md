---
id: STORY-097
title: Clickjacking prevention
nfr_refs:
  - REL-009
  - SEC-021
type: reliability
status: draft
owner: security-team
summary: Prevent FtRS UI from being embedded in unauthorized frames to protect user interactions.
---

## Description
Configure security headers (X-Frame-Options DENY or CSP frame-ancestors) and test unauthorized iframe embedding attempts ensuring block and user safety.

## Acceptance Criteria
- Response headers include X-Frame-Options or CSP frame-ancestors directive.
- Unauthorized embedding in test page fails to render interactive UI.
- Legitimate internal embeddings (if any) documented & allowed explicitly.
- Header presence monitored; alert on removal.

## Test Notes
| Test | Method | Expected |
|------|--------|----------|
| header_presence_scan | automated | Required headers present |
| unauthorized_iframe_test | automated | Embedding blocked |
| allowed_embedding_documentation | manual | Docs committed |
| header_removal_alert_test | automated | Alert on simulated removal |

## Traceability
NFRs: REL-009, SEC-021
