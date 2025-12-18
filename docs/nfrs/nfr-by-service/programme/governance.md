# FtRS NFR – Service: Programme – Domain: Governance

Source: docs/nfrs/nfr-by-domain/* (derived)

This page is auto-generated; do not hand-edit.

## Domain Sources

- [Governance NFRs – Original Confluence Page](https://nhsd-confluence.digital.nhs.uk/spaces/FRS/pages/1066471139/Compliance+and+Governance)

## Summary

| Domain | Code | Requirement | Explanation | Stories |
|--------|------|-------------|-------------|---------|
| Governance | [GOV-001](#GOV-001) | Service Management pre-live acceptance signed | Service Management pre-live acceptance is signed off before go-live. | (none) |
| Governance | [GOV-002](#GOV-002) | Well-Architected review completed & actions closed | Well-Architected review completed; remediation actions closed. | (none) |
| Governance | [GOV-003](#GOV-003) | Solution Architecture Framework assessment approved | Solution Architecture Framework assessment is approved. | (none) |
| Governance | [GOV-004](#GOV-004) | Engineering Red-lines compliance checklist signed | Engineering red-lines compliance checklist is signed. | (none) |
| Governance | [GOV-005](#GOV-005) | GDPR compliance assessment signed by IG | GDPR compliance assessment signed by Information Governance. | (none) |
| Governance | [GOV-006](#GOV-006) | Medical Device out-of-scope statement recorded | Statement confirming service is out of scope for Medical Device regulation. | (none) |
| Governance | [GOV-007](#GOV-007) | FtRS Architects review & approval logged | Architecture review and approval logged by FtRS architects. | (none) |
| Governance | [GOV-008](#GOV-008) | Cloud Expert deployment approval documented | Cloud expert deployment approval documented (infrastructure readiness). | (none) |
| Governance | [GOV-009](#GOV-009) | Solution Assurance approval ticket closed | Solution Assurance approval ticket is closed. | (none) |
| Governance | [GOV-010](#GOV-010) | Clinical Safety assurance approval recorded | Clinical Safety assurance approval recorded. | [FTRS-1640](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1640), [FTRS-824](https://nhsd-jira.digital.nhs.uk/browse/FTRS-824) |
| Governance | [GOV-011](#GOV-011) | Information Governance approval recorded | Information Governance approval recorded. | (none) |
| Governance | [GOV-012](#GOV-012) | TRG approval session outcome logged | Technical Review Group (TRG) approval outcome documented. | (none) |
| Governance | [GOV-013](#GOV-013) | SIRO sign-off obtained | Senior Information Risk Owner (SIRO) sign-off obtained. | (none) |
| Governance | [GOV-014](#GOV-014) | Caldicott Principles Guardian approval recorded | Caldicott Guardian approval recorded for data handling. | (none) |
| Governance | [GOV-015](#GOV-015) | DUEC Assurance Board acceptance logged | DUEC Assurance Board acceptance logged. | (none) |
| Governance | [GOV-016](#GOV-016) | Live Services Board go-live approval recorded | Live Services Board go-live approval recorded. | (none) |

## Controls

Control: governance/verification check that enforces an NFR. Defines measure, threshold, cadence, environments/services scope, status, rationale, and stories for traceability.

### GOV-001

Service Management pre-live acceptance signed

See explanation: [GOV-001](../../explanations.md#Explanations-GOV-001)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| service-management-pre-live | Service Management pre-live acceptance signed | Acceptance signed; evidence stored | Pre-live | prod | Programme | draft | (none) | Ensures service readiness sign-off |

### GOV-002

Well-Architected review completed & actions closed

See explanation: [GOV-002](../../explanations.md#Explanations-GOV-002)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| well-architected-review | Well-Architected review completed & actions closed | Review complete; actions closed or exceptioned | Pre-live + annual | prod | Programme | draft | (none) | Maintains architectural quality |

### GOV-003

Solution Architecture Framework assessment approved

See explanation: [GOV-003](../../explanations.md#Explanations-GOV-003)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| saf-assessment-approved | Solution Architecture Framework assessment approved | Approved assessment stored with evidence link; exceptions recorded | Pre-live | prod | Programme | draft | (none) | Ensures architectural governance sign-off |

### GOV-004

Engineering Red-lines compliance checklist signed

See explanation: [GOV-004](../../explanations.md#Explanations-GOV-004)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| nhs-github-enterprise-repos | All FtRS code repositories are hosted in NHS GitHub Enterprise and comply with securing-repositories policy; engineering dashboards show compliance | 100% repositories on NHS GitHub Enterprise; 100% securing-repositories checks passing; exceptions recorded with owner and review date | Continuous (CI on change) + quarterly governance review | dev,int,ref,prod | Programme | draft | (none) | Enforces organisational SDLC-1 Red Line for using NHS GitHub Enterprise and securing repositories; provides traceable evidence and automated verification |

### GOV-005

GDPR compliance assessment signed by IG

See explanation: [GOV-005](../../explanations.md#Explanations-GOV-005)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| gdpr-assessment-signed | GDPR compliance assessment signed by IG | Assessment signed; actions tracked | Pre-live + annual | prod | Programme | draft | (none) | Ensures data protection compliance |

### GOV-006

Medical Device out-of-scope statement recorded

See explanation: [GOV-006](../../explanations.md#Explanations-GOV-006)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| medical-device-out-of-scope | Medical Device out-of-scope statement recorded | Statement recorded and reviewed annually | Annual review | prod | Programme | draft | (none) | Confirms regulatory position |

### GOV-007

FtRS Architects review & approval logged

See explanation: [GOV-007](../../explanations.md#Explanations-GOV-007)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| ftrs-architects-approval | FtRS Architects review & approval logged | Review minutes and approval recorded; actions tracked | Pre-live + on major change | prod | Programme | draft | (none) | Provides architectural oversight evidence |

### GOV-008

Cloud Expert deployment approval documented

See explanation: [GOV-008](../../explanations.md#Explanations-GOV-008)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| cloud-expert-approval | Cloud Expert deployment approval documented | Approval recorded; infra readiness checklist passed | Pre-live | prod | Programme | draft | (none) | Confirms infrastructure deployment readiness |

### GOV-009

Solution Assurance approval ticket closed

See explanation: [GOV-009](../../explanations.md#Explanations-GOV-009)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| solution-assurance-approval | Solution Assurance approval ticket closed | Approval obtained; ticket closed | Pre-live | prod | Programme | draft | (none) | Meets governance approval requirements |

### GOV-010

Clinical Safety assurance approval recorded

See explanation: [GOV-010](../../explanations.md#Explanations-GOV-010)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| clinical-safety-approval | Clinical Safety assurance approval recorded | Approval recorded; evidence available | Pre-live | prod | Programme | draft | [FTRS-1640](https://nhsd-jira.digital.nhs.uk/browse/FTRS-1640), [FTRS-824](https://nhsd-jira.digital.nhs.uk/browse/FTRS-824) | Complies with clinical safety governance |

### GOV-011

Information Governance approval recorded

See explanation: [GOV-011](../../explanations.md#Explanations-GOV-011)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| ig-approval-recorded | Information Governance approval recorded | Approval recorded; actions tracked | Pre-live | prod | Programme | draft | (none) | Meets IG governance |

### GOV-012

TRG approval session outcome logged

See explanation: [GOV-012](../../explanations.md#Explanations-GOV-012)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| trg-approval-outcome | TRG approval session outcome logged | Outcome recorded; decisions minuted; actions tracked | Pre-live | prod | Programme | draft | (none) | Documents technical governance approval |

### GOV-013

SIRO sign-off obtained

See explanation: [GOV-013](../../explanations.md#Explanations-GOV-013)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| siro-signoff | SIRO sign-off obtained | Sign-off recorded; evidence stored | Pre-live | prod | Programme | draft | (none) | Confirms senior risk acceptance |

### GOV-014

Caldicott Principles Guardian approval recorded

See explanation: [GOV-014](../../explanations.md#Explanations-GOV-014)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| caldicott-guardian-approval | Caldicott Principles Guardian approval recorded | Approval recorded with data handling summary | Pre-live | prod | Programme | draft | (none) | Ensures data handling governance |

### GOV-015

DUEC Assurance Board acceptance logged

See explanation: [GOV-015](../../explanations.md#Explanations-GOV-015)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| duec-acceptance | DUEC Assurance Board acceptance logged | Acceptance recorded; actions tracked | Pre-live | prod | Programme | draft | (none) | Documents assurance acceptance |

### GOV-016

Live Services Board go-live approval recorded

See explanation: [GOV-016](../../explanations.md#Explanations-GOV-016)

| Control ID | Measure | Threshold | Cadence | Envs | Services | Status | Stories | Rationale |
|----------|-------|---------|-------|----|--------|------|-------|---------|
| live-services-go-live | Live Services Board go-live approval recorded | Go-live approval recorded; evidence stored | Pre-live | prod | Programme | draft | (none) | Final governance approval before production |
