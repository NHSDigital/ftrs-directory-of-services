# NFR User Stories Summary

Generated: 21 November 2025

## Overview

Complete set of user stories generated from Non-Functional Requirements (NFR) expectations registries.

**Total Stories: 80** (no duplicates)

All stories generated via automated script: `scripts/nfr/generate_stories.py`

## Stories by Domain

### Performance (PERF) - 10 stories

Focus: Latency, throughput, and payload expectations for API operations

Generated from performance/expectations.yaml operations:

- dos-search, dos-lookup-ods, dos-nearby (dos-search service; renamed from gp-search v1.5)
- org-get, org-update, healthcare-service-get, org-search-ods (crud-apis service)
- ods-daily-sync, ods-batch-transform, ods-sqs-batch-send (etl-ods service)

### Security (SEC) - 28 stories

Focus: Encryption, authentication, vulnerability management, access control

Generated from security/expectations.yaml controls covering:

- TLS encryption and storage encryption
- CVE and vulnerability management
- Mutual TLS (mTLS) enforcement
- CIS benchmark compliance
- IAM least privilege
- Certificate validation
- Port and network restrictions
- Release pipeline security gates
- Credential lifecycle management
- Cross-environment isolation
- Tenant segmentation
- Cryptographic cipher standards
- WAF security governance
- Console access auditing
- Security group policies

### Reliability (REL) - 4 stories

Focus: Resilience, fail-over, and graceful degradation

Generated from reliability/expectations.yaml controls:

- Availability Zone failure resilience
- Batch job suspend/resume integrity
- Automatic unhealthy node replacement
- Graceful tier failure degradation

### Observability (OBS) - 5 stories

Focus: Monitoring, metrics, tracing, and visibility

Generated from observability/expectations.yaml controls:

- Service health dashboards
- Performance metrics pipeline latency (≤60s)
- TPS threshold alerting
- Endpoint latency histograms (p50/p95/p99)
- Distributed tracing coverage (≥95%)

### Scalability (SCAL) - 5 stories

Focus: Horizontal/vertical scaling, autoscaling, capacity

Generated from scalability/expectations.yaml controls:

- Linear horizontal scaling validation
- Zero-downtime vertical scaling
- Autoscaling policy simulation
- Scaling event SLA protection
- Capacity headroom monitoring (≥30%)

### Accessibility (ACC) - 5 stories

Focus: WCAG compliance, keyboard navigation, assistive technology

Generated from accessibility/expectations.yaml controls:

- WCAG 2.2 AA compliance (automated + manual audits)
- Automated cross-browser accessibility scans
- Keyboard tab order regression tests
- Focus trap tests for modals/overlays
- Monthly accessibility reporting

### Governance (GOV) - 5 stories

Focus: Pre-live approvals, reviews, compliance assessments

Generated from governance/expectations.yaml controls:

- Service Management pre-live acceptance
- Well-Architected Framework review
- Solution Assurance approval
- Clinical Safety assurance approval
- GDPR compliance assessment

### Interoperability (INT) - 5 stories

Focus: FHIR compliance, content negotiation, validation, correlation

Generated from interoperability/expectations.yaml controls:

- Standard OperationOutcome error structure
- Strict content negotiation
- Reference data sync latency (≤24h)
- Correlation ID preservation across calls
- Complete field-level input validation

### Cost (COST) - 5 stories

Focus: Tagging, cost monitoring, budget alerts, optimization

Generated from cost/expectations.yaml controls:

- Mandatory resource tagging (100% coverage)
- Monthly Cost Explorer review and anomaly detection
- CloudHealth access provisioning
- CloudHealth optimization and tag compliance reports
- Budget and alert notification configuration

### Availability (AVAIL) - 5 stories

Focus: Uptime, disaster recovery, maintenance windows, deployments

Generated from availability/expectations.yaml controls:

- Multi-AZ uptime reporting (≥99.90%)
- Region disaster recovery simulation
- 24x7 uptime monitoring coverage
- Maintenance window limits (≤150min/month, ≤60min/window)
- Blue/green deployment with zero failed requests

### Compatibility (COMP) - 3 stories

Focus: Platform support, browser compatibility, MFA journeys

Generated from compatibility/expectations.yaml controls:

- Published supported OS/browser list
- MFA (CIS2) platform compatibility
- Cross-platform critical journey tests (≥90% pass rate)

## Story Template Structure

Each story follows the standard template:

- **Front matter**: story_id, title, role, goal, value, nfr_refs, status
- **Description**: Clear narrative of the requirement
- **Acceptance Criteria**: Numbered, testable criteria (≥5)
- **Non-Functional Acceptance**: Control details from registry
- **Test Strategy**: Table of test types, tooling, and focus areas
- **Out of Scope**: Explicit exclusions
- **Implementation Notes**: Technical guidance
- **Monitoring & Metrics**: Key metrics to emit
- **Risks & Mitigation**: Table of risks and mitigations
- **Traceability**: Links to NFR codes and registry
- **Open Questions**: Unresolved items

## Registry Mapping

All stories are generated from versioned expectations registries:

- `requirements/nfrs/performance/expectations.yaml` v1.4
- `requirements/nfrs/security/expectations.yaml` v1.0
- `requirements/nfrs/reliability/expectations.yaml` v1.0
- `requirements/nfrs/observability/expectations.yaml` v1.0
- `requirements/nfrs/scalability/expectations.yaml` v1.0
- `requirements/nfrs/accessibility/expectations.yaml` v1.0
- `requirements/nfrs/governance/expectations.yaml` v1.0
- `requirements/nfrs/interoperability/expectations.yaml` v1.0
- `requirements/nfrs/cost/expectations.yaml` v1.0
- `requirements/nfrs/availability/expectations.yaml` v1.0
- `requirements/nfrs/compatibility/expectations.yaml` v1.0

## Usage

These stories can be:

1. **Imported to Jira** using `scripts/jira/export_for_jira.py`
2. **Validated** using `scripts/jira/validate_artifacts.py`
3. **Referenced in specs** via NFR mapping sections
4. **Tracked in matrix** via `docs/developer-guides/nfr-matrix.md`

## Generation

All 80 stories generated automatically using `scripts/nfr/generate_stories.py`:

- Reads from versioned NFR expectations registries
- Generates consistent story structure for all domains
- Maps operations (performance) and controls (other domains) to user stories
- No manual story creation - fully reproducible from registries

To regenerate all stories:

```bash
cd /Users/peter/dev/src/github/NHSDigital/ftrs-directory-of-services
python3 scripts/nfr/generate_stories.py
```

## Next Steps

1. Review and refine generated stories
2. Link stories in NFR matrix
3. Map stories to service specifications
4. Plan sprint backlog from NFR stories
5. Establish validation pipeline for NFR compliance
