# Cost (FinOps) NFRs Overview

## Purpose

Embed continuous cost visibility, accountability and optimisation practices so FtRS can scale sustainably while meeting NHS fiscal stewardship expectations.

## Goals

- Complete & consistent tagging across all AWS resources (Environment, Team, Application, CostCentre, Owner, Service).
- Proactive monitoring using AWS Cost Explorer & anomaly detection.
- Augmented insight via CloudHealth (utilisation, rightsizing, tag compliance).
- Budget thresholds with timely, multi-channel alerts.
- Centralised cost signal routing (#ftrs-cost-alerts) for rapid triage.
- Formal quarterly cost reviews driving measurable optimisation actions.

## Scope

Applies to all AWS accounts & environments (dev, int, ref, sandpit, test, prod). Integrates with governance, observability and performance domains (e.g. metrics & tagging feed dashboards / reports).

## NFR Codes

Refer to `index.yaml` for detailed definitions COST-001..COST-007.

| Code     | Theme        | Summary                                        |
| -------- | ------------ | ---------------------------------------------- |
| COST-001 | Tagging      | Standard mandatory tag set 100% coverage       |
| COST-002 | Monitoring   | Monthly Cost Explorer & anomaly review         |
| COST-003 | Access       | CloudHealth access for infra engineer per team |
| COST-004 | Optimisation | CloudHealth reports for tagging & utilisation  |
| COST-005 | Budgets      | AWS Budgets + multi-channel alerts configured  |
| COST-006 | Alerting     | #ftrs-cost-alerts channel operational          |
| COST-007 | Governance   | Quarterly cost review with actions logged      |

## Verification Approach

- Automated tag compliance scan (e.g. via AWS Configuration / custom Lambda) exporting coverage metric (COST-001).
- Scheduled monthly Cost Explorer report generation & anomaly diff stored (COST-002).
- Access roster exported & compared to team registry (COST-003).
- CloudHealth scheduled reports archived (tag compliance, rightsizing) with action tracking (COST-004).
- Terraform / IaC definitions for AWS Budgets + SNS topics & Slack integration test message (COST-005, COST-006).
- Quarterly review minutes & action register with status aging metrics (COST-007).

## Maturity & Roadmap

All COST codes begin `draft`. Transition to `approved` requires:

1. ≥3 consecutive monthly reviews executed (COST-002).
2. Tag coverage sustained ≥98% for 2 quarters (COST-001).
3. ≥80% of CloudHealth optimisation high-impact actions executed within SLA (COST-004).
4. At least 2 quarterly reviews completed with closed-loop action tracking (COST-007).

## Metrics

| Metric                        | Target                        | Related Codes      |
| ----------------------------- | ----------------------------- | ------------------ |
| Tag coverage                  | ≥98%                          | COST-001           |
| Anomaly MTTR                  | <5 working days               | COST-002, COST-006 |
| Rightsizing action completion | ≥80% within 30 days           | COST-004           |
| Budget alert timeliness       | Notification before 80% spend | COST-005           |

## Traceability

COST codes map to stories STORY-201..STORY-207. Matrix provides bidirectional audit.

## Open Questions

| Topic                  | Question                                        | Action                        |
| ---------------------- | ----------------------------------------------- | ----------------------------- |
| Tag taxonomy evolution | Need additional tags (e.g. DataClassification)? | Review next governance cycle  |
| Anomaly tooling        | Adopt AWS Cost Anomaly Detection vs custom?     | Evaluate pilot Q1             |
| Rightsizing automation | Safe automation for non-prod scale-down?        | PoC after baseline visibility |

## Success Indicators

- Reduction in monthly run-rate vs baseline after two optimisation cycles.
- No untagged cost >1% of total monthly spend.
- Zero missed budget threshold alerts.

---

End of overview.
