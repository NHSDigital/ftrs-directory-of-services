# Scalability & Elasticity NFRs

Background:
Scalability is the ability of FtRS to adapt to sustained growth in demand, while elasticity addresses short-term variability (peaks/valleys). Production must scale horizontally (out/in) and vertically (up/down) across layers without major re-engineering or performance degradation.

Scope & Assumptions:

- Applies to Production environment operation of FtRS application & migrated services.
- Scaling actions should not breach latency/error SLAs (see performance & reliability domains).
- Elastic (automatic) responses handle sudden short spikes; scalable architecture handles sustained growth.

Legend:
Code | Requirement | Rationale | Verification | Tags

## NFR Table

| Code     | Requirement                                                                               | Rationale                                   | Verification                                                 | Tags                                  |
| -------- | ----------------------------------------------------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------ | ------------------------------------- |
| SCAL-001 | Support horizontal scaling (out/in) for stateless service tiers                           | Increase throughput by adding instances     | Load test shows linear-ish TPS gain with added replicas      | scalability, horizontal               |
| SCAL-002 | Support vertical scaling (up/down) for stateful components without re-engineering         | Handle growth in storage/compute needs      | Instance size change test retains data & functionality       | scalability, vertical                 |
| SCAL-003 | All solution layers (compute, storage, data pipeline, cache) scale without major redesign | Avoid costly migrations under growth        | Architecture review checklist passes for each layer          | scalability, architecture             |
| SCAL-004 | Bidirectional scaling (up/down, out/in) handles increases AND decreases in demand         | Optimise cost during valleys                | Autoscaling event log shows scale-down after low utilisation | scalability, cost, elasticity         |
| SCAL-005 | Automated scaling policies with defined triggers & guardrails (min/max, cooldown)         | Prevent oscillation & ensure predictability | Policy configuration lint + event simulation                        | scalability, automation, elasticity   |
| SCAL-006 | Scaling events do not degrade user performance (no SLA breach)                            | Preserve user experience                    | Load test during scale event: latency/error within SLA       | scalability, performance, reliability |
| SCAL-007 | Maintain capacity headroom (≥30% free) for sustained growth periods                       | Avoid emergency scaling crisis              | Capacity report shows utilisation <70% avg                   | scalability, capacity                 |
| SCAL-008 | Typical demand variance absorbed with no manual intervention                              | Reduce operational toil                     | Month ops log shows zero manual scaling tickets              | scalability, operations, elasticity   |
| SCAL-009 | Scaling actions auditable (timestamp, actor, reason, targets)                             | Traceability & governance                   | Audit log entry schema validation                            | scalability, audit                    |
| SCAL-010 | Pre-scale predictive alert issued when projected utilisation >80% sustained 15min         | Proactive planning                          | Forecast engine triggers alert in test                       | scalability, forecasting              |

## Verification Strategy

- Synthetic & load tests (baseline vs scaled replicas)
- Autoscaling policy simulation (e.g. metric injection)
- Architecture reviews for layer scalability characteristics
- Capacity forecasting & utilisation dashboards
- Audit log schema validation for scaling events

## Follow-Up Items

- Define quantitative latency/error SLAs cross-referenced to SCAL-006.
- Implement forecast model (e.g. Holt-Winters) for SCAL-010.
- Add cost optimisation metrics linking scale-down events to savings.
