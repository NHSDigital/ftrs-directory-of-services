---
story_id: STORY-AVAIL-008
title: Replication lag ≤60s; fail-over data delta minimal
role: SRE
goal: Deliver: Replication lag ≤60s; fail-over data delta minimal
value: Data replication lag remains under target ensuring minimal failover delta.
nfr_refs: [AVAIL-007]
status: draft
---

## Description

Implement and validate NFR `AVAIL-007` for domain `availability`.

## Acceptance Criteria

- Replication lag \u2264 60s for primary datasets; failover delta \u2264 1% records
- Tooling and cadence established
- Monitoring and alerting in place

## Non-Functional Acceptance

- NFR Code: `AVAIL-007`
- Domain: availability
- Control ID: `replication-lag-threshold`
- Measure: Replication lag \u226460s; fail-over data delta minimal
- Threshold: Replication lag \u2264 60s for primary datasets; failover delta \u2264 1% records
- Tooling: Replication metrics + failover audit
- Cadence: Continuous + monthly report
- Environments: prod


## Traceability

- Domain registry: requirements/nfrs/availability/nfrs.yaml
