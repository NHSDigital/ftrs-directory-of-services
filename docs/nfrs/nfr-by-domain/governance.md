# FtRS NFR – Governance

This page is auto-generated; do not hand-edit.

## NFR Codes

| Code | Requirement | Explanation | Stories |
|------|-------------|-------------|---------|
| GOV-001 | Service Management pre-live acceptance signed | Service Management pre-live acceptance is signed off before go-live. | STORY-GOV-001 |
| GOV-002 | Well-Architected review completed & actions closed | Well-Architected review completed; remediation actions closed. | STORY-GOV-002 |
| GOV-003 | Solution Architecture Framework assessment approved | Solution Architecture Framework assessment is approved. | STORY-GOV-003 |
| GOV-004 | Engineering Red-lines compliance checklist signed | Engineering red-lines compliance checklist is signed. | STORY-GOV-004 |
| GOV-005 | GDPR compliance assessment signed by IG | GDPR compliance assessment signed by Information Governance. | STORY-GOV-005 |
| GOV-006 | Medical Device out-of-scope statement recorded | Statement confirming service is out of scope for Medical Device regulation. | STORY-GOV-006 |
| GOV-007 | FtRS Architects review & approval logged | Architecture review and approval logged by FtRS architects. | STORY-GOV-007 |
| GOV-008 | Cloud Expert deployment approval documented | Cloud expert deployment approval documented (infrastructure readiness). | STORY-GOV-008 |
| GOV-009 | Solution Assurance approval ticket closed | Solution Assurance approval ticket is closed. | STORY-GOV-003, STORY-GOV-009 |
| GOV-010 | Clinical Safety assurance approval recorded | Clinical Safety assurance approval recorded. | STORY-GOV-004, STORY-GOV-010 |
| GOV-011 | Information Governance approval recorded | Information Governance approval recorded. | STORY-GOV-011 |
| GOV-012 | TRG approval session outcome logged | Technical Review Group (TRG) approval outcome documented. | STORY-GOV-012 |
| GOV-013 | SIRO sign-off obtained | Senior Information Risk Owner (SIRO) sign-off obtained. | STORY-GOV-013 |
| GOV-014 | Caldicott Principles Guardian approval recorded | Caldicott Guardian approval recorded for data handling. | STORY-GOV-014 |
| GOV-015 | DUEC Assurance Board acceptance logged | DUEC Assurance Board acceptance logged. | STORY-GOV-015 |
| GOV-016 | Live Services Board go-live approval recorded | Live Services Board go-live approval recorded. | STORY-GOV-016 |

## Controls

### GOV-001

Service Management pre-live acceptance is signed off before go-live.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-001](#gov-001) | service-management-pre-live | Service Management pre-live acceptance signed | Acceptance signed; evidence stored | Governance tracker + document repository | Pre-live | prod | crud-apis,dos-search | draft | Ensures service readiness sign-off |

### GOV-002

Well-Architected review completed; remediation actions closed.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-002](#gov-002) | well-architected-review | Well-Architected review completed & actions closed | Review complete; actions closed or exceptioned | WAR tool + issue tracker | Pre-live + annual | prod | crud-apis,dos-search | draft | Maintains architectural quality |

### GOV-003

Solution Architecture Framework assessment is approved.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-003](#gov-003) | saf-assessment-approved | Solution Architecture Framework assessment approved | Approved assessment stored with evidence link; exceptions recorded | Governance tracker + document repository | Pre-live | prod | crud-apis,dos-search | draft | Ensures architectural governance sign-off |

### GOV-004

Engineering red-lines compliance checklist is signed.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-004](#gov-004) | nhs-github-enterprise-repos | All FtRS code repositories are hosted in NHS GitHub Enterprise and comply with securing-repositories policy; engineering dashboards show compliance | 100% repositories on NHS GitHub Enterprise; 100% securing-repositories checks passing; exceptions recorded with owner and review date | Enterprise repository policy audit + engineering compliance dashboards + CI checks | Continuous (CI on change) + quarterly governance review | dev,int,ref,prod | crud-apis,dos-ingestion-api,etl-ods,dos-search,read-only-viewer | draft | Enforces organisational SDLC-1 Red Line for using NHS GitHub Enterprise and securing repositories; provides traceable evidence and automated verification |

### GOV-005

GDPR compliance assessment signed by Information Governance.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-005](#gov-005) | gdpr-assessment-signed | GDPR compliance assessment signed by IG | Assessment signed; actions tracked | IG workflow + evidence repository | Pre-live + annual | prod | crud-apis,dos-search | draft | Ensures data protection compliance |

### GOV-006

Statement confirming service is out of scope for Medical Device regulation.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-006](#gov-006) | medical-device-out-of-scope | Medical Device out-of-scope statement recorded | Statement recorded and reviewed annually | Evidence repository | Annual review | prod | crud-apis,dos-search | draft | Confirms regulatory position |

### GOV-007

Architecture review and approval logged by FtRS architects.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-007](#gov-007) | ftrs-architects-approval | FtRS Architects review & approval logged | Review minutes and approval recorded; actions tracked | Review tracker + minutes repo | Pre-live + on major change | prod | crud-apis,dos-search | draft | Provides architectural oversight evidence |

### GOV-008

Cloud expert deployment approval documented (infrastructure readiness).

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-008](#gov-008) | cloud-expert-approval | Cloud Expert deployment approval documented | Approval recorded; infra readiness checklist passed | Infra checklist + evidence repo | Pre-live | prod | crud-apis,dos-search | draft | Confirms infrastructure deployment readiness |

### GOV-009

Solution Assurance approval ticket is closed.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-009](#gov-009) | solution-assurance-approval | Solution Assurance approval ticket closed | Approval obtained; ticket closed | Assurance workflow + evidence repository | Pre-live | prod | crud-apis,dos-search | draft | Meets governance approval requirements |

### GOV-010

Clinical Safety assurance approval recorded.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-010](#gov-010) | clinical-safety-approval | Clinical Safety assurance approval recorded | Approval recorded; evidence available | Clinical safety workflow + repository | Pre-live | prod | crud-apis,dos-search | draft | Complies with clinical safety governance |

### GOV-011

Information Governance approval recorded.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-011](#gov-011) | ig-approval-recorded | Information Governance approval recorded | Approval recorded; actions tracked | IG workflow + evidence repository | Pre-live | prod | crud-apis,dos-search | draft | Meets IG governance |

### GOV-012

Technical Review Group (TRG) approval outcome documented.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-012](#gov-012) | trg-approval-outcome | TRG approval session outcome logged | Outcome recorded; decisions minuted; actions tracked | TRG minutes + tracker | Pre-live | prod | crud-apis,dos-search | draft | Documents technical governance approval |

### GOV-013

Senior Information Risk Owner (SIRO) sign-off obtained.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-013](#gov-013) | siro-signoff | SIRO sign-off obtained | Sign-off recorded; evidence stored | Governance tracker | Pre-live | prod | crud-apis,dos-search | draft | Confirms senior risk acceptance |

### GOV-014

Caldicott Guardian approval recorded for data handling.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-014](#gov-014) | caldicott-guardian-approval | Caldicott Principles Guardian approval recorded | Approval recorded with data handling summary | Governance tracker + evidence repo | Pre-live | prod | crud-apis,dos-search | draft | Ensures data handling governance |

### GOV-015

DUEC Assurance Board acceptance logged.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-015](#gov-015) | duec-acceptance | DUEC Assurance Board acceptance logged | Acceptance recorded; actions tracked | Board minutes + tracker | Pre-live | prod | crud-apis,dos-search | draft | Documents assurance acceptance |

### GOV-016

Live Services Board go-live approval recorded.

| Requirement | Control ID | Measure | Threshold | Tooling | Cadence | Envs | Services | Status | Rationale |
|-------------|------------|---------|-----------|---------|---------|------|----------|--------|-----------|
| [GOV-016](#gov-016) | live-services-go-live | Live Services Board go-live approval recorded | Go-live approval recorded; evidence stored | Governance tracker + evidence repo | Pre-live | prod | crud-apis,dos-search | draft | Final governance approval before production |
