# NFR Tagging Conventions

Use tags to enrich NFRs and support automated suggestion of acceptance criteria.

## Tag Categories

- impact: patient-safety | cost | legal | reputational
- verification: test | monitoring | audit | manual
- scope: api | data | infra | ui | service
- risk_level: low | medium | high

## Example

```yaml
code: PERF-001
tags:
  impact: patient-safety
  verification: test
  scope: api
  risk_level: medium
```

## Usage in Stories

Add `nfr_tags:` array for Copilot enrichment.

```yaml
nfr_tags: [performance, api, patient-safety]
```
