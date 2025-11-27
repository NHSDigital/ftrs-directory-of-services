# FtRS NFR – Governance

Source: requirements/nfrs/cross-references/nfr-matrix.md

This page is auto-generated; do not hand-edit.

## NFR Codes

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| GOV-001 | Service Management pre-live acceptance signed | Service Management pre-live acceptance is signed off before go-live. | STORY-GOV-001 |
| GOV-002 | Well-Architected review completed & actions closed | Well-Architected review completed; remediation actions closed. | STORY-GOV-002 |
| GOV-003 | Solution Architecture Framework assessment approved | Solution Architecture Framework assessment is approved. | STORY-GOV-003 |
| GOV-004 | Engineering Red-lines compliance checklist signed | Engineering red-lines compliance checklist is signed. | STORY-GOV-004 |
| GOV-005 | GDPR compliance assessment signed by IG | GDPR compliance assessment signed by Information Governance. | STORY-GOV-005 |
| GOV-006 | Medical Device out-of-scope statement recorded | Statement confirming service is out of scope for Medical Device regulation. | (none) |
| GOV-007 | FtRS Architects review & approval logged | Architecture review and approval logged by FtRS architects. | (none) |
| GOV-008 | Cloud Expert deployment approval documented | Cloud expert deployment approval documented (infrastructure readiness). | (none) |
| GOV-009 | Solution Assurance approval ticket closed | Solution Assurance approval ticket is closed. | (none) |
| GOV-010 | Clinical Safety assurance approval recorded | Clinical Safety assurance approval recorded. | (none) |
| GOV-011 | Information Governance approval recorded | Information Governance approval recorded. | (none) |
| GOV-012 | TRG approval session outcome logged | Technical Review Group (TRG) approval outcome documented. | (none) |
| GOV-013 | SIRO sign-off obtained | Senior Information Risk Owner (SIRO) sign-off obtained. | (none) |
| GOV-014 | Caldicott Principles Guardian approval recorded | Caldicott Principles Guardian approval recorded for data handling. | (none) |
| GOV-015 | DUEC Assurance Board acceptance logged | DUEC Assurance Board acceptance logged. | (none) |
| GOV-016 | Live Services Board go-live approval recorded | Live Services Board go-live approval recorded. | (none) |

## Controls

### GOV-001

Service Management pre-live acceptance is signed off before go-live.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| service-management-pre-live | Service Management pre-live acceptance signed | Acceptance signed; evidence stored | Governance tracker + document repository | Pre-live | prod | crud-apis,dos-search | draft | Ensures service readiness sign-off |

### GOV-002

Well-Architected review completed; remediation actions closed.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| well-architected-review | Well-Architected review completed & actions closed | Review complete; actions closed or exceptioned | WAR tool + issue tracker | Pre-live + annual | prod | crud-apis,dos-search | draft | Maintains architectural quality |

### GOV-005

GDPR compliance assessment signed by Information Governance.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| gdpr-assessment-signed | GDPR compliance assessment signed by IG | Assessment signed; actions tracked | IG workflow + evidence repository | Pre-live + annual | prod | crud-apis,dos-search | draft | Ensures data protection compliance |

### GOV-009

Solution Assurance approval ticket is closed.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| solution-assurance-approval | Solution Assurance approval ticket closed | Approval obtained; ticket closed | Assurance workflow + evidence repository | Pre-live | prod | crud-apis,dos-search | draft | Meets governance approval requirements |

### GOV-010

Clinical Safety assurance approval recorded.

| Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| clinical-safety-approval | Clinical Safety assurance approval recorded | Approval recorded; evidence available | Clinical safety workflow + repository | Pre-live | prod | crud-apis,dos-search | draft | Complies with clinical safety governance |
