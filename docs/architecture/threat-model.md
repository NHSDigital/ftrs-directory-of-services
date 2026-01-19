# FtRS Threat Model (Private Beta)

## Document Information

| Attribute | Value |
|-----------|-------|
| **Version** | 1.0 |
| **Date** | 19 January 2026 |
| **Scope** | ETL ODS, DoS Search, CRUD APIs |
| **Methodology** | STRIDE |
| **Classification** | Official |

---

## 1. System Overview

### 1.1 Components in Scope

| Component | Description | Data Classification |
|-----------|-------------|---------------------|
| **ETL ODS Pipeline** | Daily data ingestion from NHS ODS Terminology API | Official |
| **DoS Search API** | Consumer-facing FHIR search by ODS code | Official |
| **CRUD APIs** | Internal API for Organisation/HealthcareService/Location CRUD | Official |

### 1.2 Data Flow Summary

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  ODS Terminology│     │   NHS APIM      │     │   Healthcare    │
│  API (External) │     │   (GCP)         │     │   Consumers     │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         │ HTTPS + API Key       │ mTLS                  │ HTTPS + API Key
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         AWS Cloud (eu-west-2)                           │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐                │
│  │ ETL ODS       │  │ CRUD APIs     │  │ DoS Search    │                │
│  │ (3 Lambdas)   │──▶ (FastAPI)     │◀──│ (Lambda)      │                │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘                │
│          │                  │                  │                        │
│          └──────────────────┼──────────────────┘                        │
│                             ▼                                           │
│                   ┌───────────────────┐                                 │
│                   │     DynamoDB      │                                 │
│                   │  (KMS Encrypted)  │                                 │
│                   └───────────────────┘                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Trust Boundaries

| ID | Boundary | Description |
|----|----------|-------------|
| **TB-1** | Internet → NHS APIM | Public internet to NHS API Management |
| **TB-2** | NHS APIM → AWS | Cross-cloud boundary (GCP to AWS) |
| **TB-3** | API Gateway → VPC | AWS regional service to private VPC |
| **TB-4** | Lambda → AWS Services | VPC to DynamoDB/SQS via VPC Endpoints |
| **TB-5** | Lambda → External APIs | VPC egress to ODS API via NAT Gateway |

---

## 3. STRIDE Threat Analysis

### 3.1 DoS Search API

#### Entry Points
- NHS APIM dosReadProxy → API Gateway → Lambda → DynamoDB

#### Assets
- Organisation data (ODS codes, names, addresses, endpoints)
- API Gateway endpoints
- DynamoDB tables

| ID | Category | Threat | Likelihood | Impact | Risk | Mitigations | NFR/Jira Traceability |
|----|----------|--------|------------|--------|------|-------------|------------------------|
| **DS-S1** | Spoofing | Attacker impersonates legitimate healthcare consumer | Low | High | Medium | API key validation at APIM, mTLS at API Gateway, geo-blocking | SEC-014 (mTLS handshake), SEC-029 (JWT auth), AVAIL-009 (geo-blocking) |
| **DS-S2** | Spoofing | Attacker replays captured API requests | Low | Medium | Low | TLS 1.2+ (no replay possible), short-lived sessions | SEC-001 (TLS 1.2+), SEC-003 (TLS enforcement) |
| **DS-T1** | Tampering | Attacker modifies search request in transit | Very Low | Medium | Low | TLS 1.2+ encryption, mTLS certificate pinning | SEC-001, SEC-003, SEC-014, FTRS-1600 |
| **DS-T2** | Tampering | Attacker modifies response data in transit | Very Low | High | Low | TLS 1.2+ encryption end-to-end | SEC-003 (FTRS-1563), SEC-024 |
| **DS-R1** | Repudiation | Consumer denies making search request | Low | Low | Low | CloudWatch logging, X-Ray tracing, APIM access logs | OBS-030 (distributed tracing, FTRS-885), OBS-022, OBS-023 (FTRS-1018) |
| **DS-I1** | Info Disclosure | Attacker enumerates ODS codes | Medium | Low | Medium | Rate limiting (100 req/120s), no wildcard search | REL-007 (rate limiting, FTRS-1598) |
| **DS-I2** | Info Disclosure | Verbose error messages leak system info | Low | Low | Low | Standardised FHIR OperationOutcome errors, no stack traces | REL-016 (error messaging, FTRS-973) |
| **DS-I3** | Info Disclosure | CloudWatch logs exposed | Very Low | High | Low | IAM policies, KMS encryption, VPC Flow Logs | SEC-012 (IAM least privilege, FTRS-359), SEC-013 (key rotation) |
| **DS-D1** | Denial of Service | Volumetric DDoS attack | Medium | High | Medium | Shield Advanced, WAF rate limiting, APIM rate limiting | SEC-002 (WAF, FTRS-356), REL-004 (DoS simulation), AVAIL-001 |
| **DS-D2** | Denial of Service | Application-layer DoS (regex/query) | Low | Medium | Low | Input validation, timeout limits, Lambda concurrency | REL-004, SEC-011 (latency SLA) |
| **DS-D3** | Denial of Service | Resource exhaustion via large responses | Low | Medium | Low | Pagination limits, response size limits | REL-004 |
| **DS-E1** | Elevation | Attacker accesses unauthorised ODS codes | Very Low | Medium | Low | No authorisation boundaries per ODS code (by design - public data) | GOV-011 (IG approval) |

#### Residual Risks
- **DS-I1**: ODS codes are finite and could theoretically be enumerated. Mitigated by rate limiting but not eliminated. Data is also publicly available via ODS API.

---

### 3.2 ETL ODS Pipeline

#### Entry Points
- EventBridge Scheduler (internal trigger)
- SQS queues (internal)

#### Exit Points
- ODS Terminology API (egress)
- NHS APIM dosReadProxy (egress for UUID lookup)
- NHS APIM dosWriteProxy (egress for writes)

#### Assets
- ODS API key (Secrets Manager)
- JWT credentials (Secrets Manager)
- Organisation data in transit
- SQS queue messages

| ID | Category | Threat | Likelihood | Impact | Risk | Mitigations | NFR/Jira Traceability |
|----|----------|--------|------------|--------|------|-------------|------------------------|
| **ETL-S1** | Spoofing | Attacker triggers ETL Lambda directly | Very Low | Medium | Low | IAM policies, EventBridge is only trigger source | SEC-012 (IAM least privilege, FTRS-359) |
| **ETL-S2** | Spoofing | Attacker injects malicious SQS message | Very Low | High | Low | SQS policy restricts SendMessage, KMS encryption | SEC-004 (encryption, FTRS-1611/FTRS-1681), SEC-012 |
| **ETL-S3** | Spoofing | Compromised ODS API returns malicious data | Very Low | High | Low | Input validation, FHIR schema validation | SEC-020 (cert validation), GOV-007 (architecture review) |
| **ETL-T1** | Tampering | Attacker modifies SQS messages | Very Low | High | Very Low | KMS encryption, SQS access policies | SEC-004 (FTRS-1587), SEC-013 (key rotation) |
| **ETL-T2** | Tampering | Attacker modifies data in transit to/from ODS | Very Low | High | Very Low | TLS 1.2+ encryption | SEC-001, SEC-003, SEC-024 |
| **ETL-T3** | Tampering | Attacker modifies JWT credentials | Very Low | Critical | Low | Secrets Manager encryption, IAM policies, rotation | SEC-030 (cert/key storage, FTRS-1602), SEC-013, SEC-012 |
| **ETL-R1** | Repudiation | ETL process denies writing bad data | Low | Medium | Low | CloudWatch logging with correlation IDs, X-Ray | OBS-030 (FTRS-885), OBS-019, OBS-021 |
| **ETL-I1** | Info Disclosure | ODS API key leaked | Low | High | Medium | Secrets Manager, KMS encryption, no logging of secrets | SEC-030 (FTRS-1602), SEC-017 (zero long-lived creds) |
| **ETL-I2** | Info Disclosure | JWT credentials leaked | Low | Critical | Medium | Secrets Manager, KMS encryption, short-lived tokens | SEC-030 (FTRS-1602), SEC-029 (FTRS-1593), SEC-017 |
| **ETL-I3** | Info Disclosure | SQS messages exposed via misconfiguration | Very Low | Medium | Low | KMS encryption, VPC endpoints, IAM policies | SEC-004 (FTRS-1681), SEC-007 (SG audit, FTRS-386), SEC-012 |
| **ETL-D1** | Denial of Service | ODS API unavailable | Medium | Medium | Medium | Retry with backoff, DLQ for failed messages, alerting | REL-014 (external outage fallback), OBS-025 (alerting) |
| **ETL-D2** | Denial of Service | SQS queue poisoning (bad messages) | Low | Medium | Low | DLQ after max retries, message validation | REL-010 (batch integrity), OBS-012 (error alerts, FTRS-1017) |
| **ETL-D3** | Denial of Service | Lambda throttling due to rate limits | Low | Low | Low | Reserved concurrency (2), retry logic | AVAIL-001 (availability SLA) |
| **ETL-E1** | Elevation | Attacker with Lambda access writes to any org | Very Low | High | Low | Lambda IAM role scoped to specific resources | SEC-012 (IAM least privilege, FTRS-359) |
| **ETL-E2** | Elevation | Compromised Lambda pivots to other AWS services | Very Low | Critical | Low | Least privilege IAM, VPC isolation, no internet egress except NAT | SEC-012 (FTRS-359), SEC-007 (FTRS-386), SEC-005 (cross-env, FTRS-1494) |

#### Residual Risks
- **ETL-I1/I2**: Credential theft remains highest concern. Mitigated by encryption, rotation, and least privilege but not eliminated.

---

### 3.3 CRUD APIs

#### Entry Points
- API Gateway (via NHS APIM for writes)
- API Gateway (internal for DoS Search reads)

#### Assets
- Organisation, HealthcareService, Location data
- DynamoDB tables
- SSM Parameter Store configuration

| ID | Category | Threat | Likelihood | Impact | Risk | Mitigations | NFR/Jira Traceability |
|----|----------|--------|------------|--------|------|-------------|------------------------|
| **CRUD-S1** | Spoofing | Attacker bypasses APIM and calls API Gateway directly | Very Low | High | Low | mTLS requires valid client certificate | SEC-014 (mTLS, FTRS-1600), SEC-015 (cert expiry, FTRS-1604) |
| **CRUD-S2** | Spoofing | Attacker forges JWT token | Very Low | Critical | Low | JWT signature validation, short expiry, APIM validation | SEC-029 (JWT auth, FTRS-1593) |
| **CRUD-S3** | Spoofing | Attacker impersonates ETL pipeline | Very Low | High | Low | Unique JWT client credentials, audit logging | SEC-029 (FTRS-1593), OBS-033 (unauth access logging) |
| **CRUD-T1** | Tampering | Attacker modifies organisation data maliciously | Low | High | Medium | JWT auth required for writes, audit logging | SEC-029 (FTRS-1593), OBS-022 (audit trail) |
| **CRUD-T2** | Tampering | SQL/NoSQL injection in queries | Low | High | Low | Parameterised queries, input validation, FHIR schema | REL-005 (injection blocked), SEC-027 (CVE scanning) |
| **CRUD-T3** | Tampering | Mass deletion of data | Very Low | Critical | Low | JWT auth, no bulk delete endpoint, DynamoDB PITR | SEC-029, AVAIL-006 (DR RTO, FTRS-11/FTRS-751), REL-017 (FTRS-344) |
| **CRUD-R1** | Repudiation | Caller denies making write operation | Low | Medium | Low | CloudWatch logs, correlation IDs, APIM logs | OBS-022 (audit trail), OBS-023 (FTRS-1018), OBS-030 (FTRS-885) |
| **CRUD-I1** | Info Disclosure | Data leaked via error messages | Low | Medium | Low | Standardised error responses, no stack traces | REL-016 (error messaging, FTRS-973), SEC-026 (no PID in response) |
| **CRUD-I2** | Info Disclosure | Unauthorised access to DynamoDB | Very Low | High | Very Low | VPC endpoints, IAM policies, KMS encryption | SEC-012 (FTRS-359), SEC-004 (FTRS-1611), SEC-007 (FTRS-386) |
| **CRUD-I3** | Info Disclosure | SSM parameters exposed | Very Low | Medium | Low | IAM policies, SecureString for sensitive values | SEC-012 (FTRS-359), SEC-030 (FTRS-1602) |
| **CRUD-D1** | Denial of Service | API overwhelmed with write requests | Low | Medium | Low | JWT auth limits to ETL only, APIM rate limiting | SEC-029 (FTRS-1593), REL-007 (rate limiting, FTRS-1598) |
| **CRUD-D2** | Denial of Service | DynamoDB capacity exhaustion | Low | High | Low | On-demand capacity, auto-scaling, alerting | AVAIL-001 (availability), OBS-008 (TPS alerts, FTRS-1688) |
| **CRUD-D3** | Denial of Service | Large payload attacks | Low | Low | Low | API Gateway payload limits, Lambda memory limits | REL-004 (DoS simulation) |
| **CRUD-E1** | Elevation | Attacker escalates from read to write | Very Low | High | Low | Separate read/write proxies, JWT required for writes | SEC-029 (FTRS-1593), SEC-012 (FTRS-359) |
| **CRUD-E2** | Elevation | UUID manipulation to access other orgs | Low | Medium | Low | UUID is internal ID, not authorisation boundary | GOV-011 (IG approval), SEC-019 (tenant isolation) |

#### Residual Risks
- **CRUD-T1**: Malicious data writes by compromised ETL or stolen JWT credentials. Mitigated by credential management and logging but relies on detection rather than prevention.

---

## 4. Attack Trees

### 4.1 Compromise Organisation Data (Write)

```
Compromise Organisation Data
├── 1. Steal JWT Credentials
│   ├── 1.1 Compromise Secrets Manager
│   │   ├── 1.1.1 Steal AWS credentials with Secrets Manager access
│   │   └── 1.1.2 Exploit IAM misconfiguration
│   ├── 1.2 Extract from Lambda environment
│   │   └── 1.2.1 Exploit Lambda vulnerability (code injection)
│   └── 1.3 Intercept in transit
│       └── 1.3.1 MITM attack (blocked by TLS)
├── 2. Bypass Authentication
│   ├── 2.1 Forge JWT token
│   │   └── 2.1.1 Obtain signing key (very difficult)
│   ├── 2.2 Bypass APIM
│   │   └── 2.2.1 Call API Gateway directly (blocked by mTLS)
│   └── 2.3 Replay attack
│       └── 2.3.1 Capture and replay request (blocked by TLS)
└── 3. Poison Data Source
    └── 3.1 Compromise ODS API
        └── 3.1.1 Supply malicious FHIR data (external system)
```

### 4.2 Exfiltrate Organisation Data (Read)

```
Exfiltrate Organisation Data
├── 1. Abuse Legitimate Access
│   ├── 1.1 Enumerate all ODS codes
│   │   └── 1.1.1 Script API calls (limited by rate limiting)
│   └── 1.2 Compromised consumer application
│       └── 1.2.1 Steal API key from registered consumer
├── 2. Bypass Authentication
│   ├── 2.1 Bypass APIM
│   │   └── 2.1.1 Call API Gateway directly (blocked by mTLS)
│   └── 2.2 Steal API key
│       └── 2.2.1 Compromise consumer's systems (external)
└── 3. Access Data Store Directly
    ├── 3.1 Access DynamoDB
    │   └── 3.1.1 Steal AWS credentials (blocked by IAM, VPC)
    └── 3.2 Access CloudWatch logs
        └── 3.2.1 Steal AWS credentials with logs access
```

---

## 5. Security Controls Summary

### 5.1 Authentication & Authorisation

| Control | Component | Implementation | NFR/Jira Traceability |
|---------|-----------|----------------|------------------------|
| API Key | DoS Search (read) | NHS APIM validates API key | SEC-029 |
| JWT (OAuth 2.0) | CRUD APIs (write) | APIM validates JWT signature and claims | SEC-029 (FTRS-1593) |
| mTLS | API Gateway | Client certificate validation, trust store in S3 | SEC-014 (FTRS-1600), SEC-015 (FTRS-1604) |
| IAM Roles | All Lambdas | Least privilege policies per function | SEC-012 (FTRS-359) |

### 5.2 Encryption

| Control | Scope | Implementation | NFR/Jira Traceability |
|---------|-------|----------------|------------------------|
| TLS 1.2+ | All transit | Enforced on all connections | SEC-001, SEC-003 (FTRS-1563) |
| KMS CMK | DynamoDB | Customer managed keys, automatic rotation | SEC-004 (FTRS-1611), SEC-013 |
| KMS CMK | SQS | Customer managed keys | SEC-004 (FTRS-1681) |
| KMS CMK | Secrets Manager | Encryption for credentials | SEC-030 (FTRS-1602) |
| SSE-S3 | S3 Buckets | Server-side encryption | SEC-004 (FTRS-1587) |

### 5.3 Network Security

| Control | Scope | Implementation | NFR/Jira Traceability |
|---------|-------|----------------|------------------------|
| VPC | All Lambdas | Private subnets, no public IPs | SEC-007 (FTRS-386), SEC-005 (FTRS-1494) |
| VPC Endpoints | AWS Services | Gateway endpoints for DynamoDB, S3; Interface for SQS | SEC-007 |
| NAT Gateway | Egress | Controlled internet egress for external API calls | SEC-008 (perimeter scan) |
| WAF | API Gateway | Geo-blocking (GB/JE/IM), rate limiting, OWASP rules | SEC-002 (FTRS-356), AVAIL-009 |
| Shield Advanced | Route 53 | DDoS protection | REL-004, AVAIL-001 |

### 5.4 Monitoring & Detection

| Control | Scope | Implementation | NFR/Jira Traceability |
|---------|-------|----------------|------------------------|
| CloudWatch Logs | All Lambdas | 30-day retention | OBS-013 (FTRS-323), OBS-014, OBS-015 |
| X-Ray | DoS Search, ETL | Distributed tracing | OBS-030 (FTRS-885) |
| CloudWatch Alarms | All components | Error rates, DLQ depth, latency | OBS-012 (FTRS-1017), OBS-008 (FTRS-1688) |
| VPC Flow Logs | VPC | Network traffic logging | SEC-006 (FTRS-1771) |

---

## 6. Risk Register

| Risk ID | Description | Likelihood | Impact | Inherent Risk | Mitigations | Residual Risk | NFR/Jira Traceability | Owner |
|---------|-------------|------------|--------|---------------|-------------|---------------|------------------------|-------|
| R1 | JWT credential compromise | Low | Critical | High | Secrets Manager, KMS, rotation, least privilege | Medium | SEC-030 (FTRS-1602), SEC-029 (FTRS-1593), SEC-013 | Security |
| R2 | ODS code enumeration | Medium | Low | Medium | Rate limiting, no sensitive data exposed | Low | REL-007 (FTRS-1598), OBS-033 | Product |
| R3 | DDoS attack on DoS Search | Medium | High | High | Shield Advanced, WAF, APIM rate limiting | Medium | SEC-002 (FTRS-356), REL-004, AVAIL-001, AVAIL-009 | Platform |
| R4 | Malicious data injection from ODS | Very Low | High | Medium | Input validation, FHIR schema validation | Low | SEC-020, GOV-007, GOV-003 | Development |
| R5 | Insider threat (AWS access abuse) | Low | Critical | High | IAM least privilege, CloudTrail, MFA | Medium | SEC-012 (FTRS-359), SEC-016, SEC-006 (FTRS-1771) | Security |

---

## 7. Recommendations

### 7.1 High Priority

| ID | Recommendation | Risk Addressed | Effort | NFR/Jira Traceability |
|----|----------------|----------------|--------|------------------------|
| REC-1 | Implement JWT credential rotation policy (e.g., 90 days) | R1 | Medium | SEC-013, SEC-030 (FTRS-1602) |
| REC-2 | Add alerting for unusual API access patterns | R2, R5 | Medium | OBS-033, OBS-012 (FTRS-1017), SEC-006 (FTRS-1771) |
| REC-3 | Implement request signing for ETL → APIM calls | R1 | Medium | SEC-024, SEC-029 (FTRS-1593) |

### 7.2 Medium Priority

| ID | Recommendation | Risk Addressed | Effort | NFR/Jira Traceability |
|----|----------------|----------------|--------|------------------------|
| REC-4 | Add FHIR resource validation in CRUD APIs | R4 | Medium | GOV-003, GOV-007 |
| REC-5 | Implement anomaly detection for DynamoDB access | R5 | High | OBS-033, SEC-012 (FTRS-359) |
| REC-6 | Add WAF custom rules for common attack patterns | R3 | Low | SEC-002 (FTRS-356), REL-004 |

### 7.3 Low Priority

| ID | Recommendation | Risk Addressed | Effort | NFR/Jira Traceability |
|----|----------------|----------------|--------|------------------------|
| REC-7 | Document and test incident response procedures | All | Medium | AVAIL-002 (FTRS-11/FTRS-407), AVAIL-006 (FTRS-751) |
| REC-8 | Periodic penetration testing | All | High | SEC-010 (FTRS-1440/FTRS-1455/FTRS-1462) |
| REC-9 | Review and tighten IAM policies quarterly | R5 | Low | SEC-012 (FTRS-359) |

---

## 8. Appendix

### 8.1 NFR Traceability Matrix

This section provides a reverse mapping from NFRs to threat mitigations for audit purposes.

| NFR Code | NFR Requirement | Threat Mitigations | Jira Tickets |
|----------|-----------------|-------------------|--------------|
| **SEC-001** | Crypto algorithms conform; weak ciphers rejected | DS-S2, DS-T1, ETL-T2 | - |
| **SEC-002** | WAF security pillar checklist completed | DS-D1, R3 | FTRS-356 |
| **SEC-003** | All endpoints TLS only; storage encryption enabled | DS-S2, DS-T1, DS-T2, ETL-T2 | FTRS-1563 |
| **SEC-004** | Storage services show encryption enabled | ETL-S2, ETL-T1, ETL-I3, CRUD-I2 | FTRS-1611, FTRS-1681, FTRS-1587 |
| **SEC-005** | Cross-environment data access attempts denied | ETL-E2 | FTRS-1494 |
| **SEC-006** | No direct prod console queries detected | R5 | FTRS-1771 |
| **SEC-007** | SG rules audited; broad ingress denied | ETL-I3, ETL-E2, CRUD-I2 | FTRS-386 |
| **SEC-010** | Annual pen test executed | REC-8 | FTRS-1440, FTRS-1455, FTRS-1462, FTRS-2 |
| **SEC-012** | IAM policy review confirms least privilege | DS-I3, ETL-S1, ETL-E1, ETL-E2, CRUD-I2, CRUD-I3, CRUD-E1, R5, REC-5, REC-9 | FTRS-359 |
| **SEC-013** | Key rotation events logged | DS-I3, ETL-T1, ETL-T3, REC-1 | - |
| **SEC-014** | mTLS handshake succeeds | DS-S1, DS-T1, CRUD-S1 | FTRS-1600 |
| **SEC-015** | Cert expiry alert; renewal seamless | CRUD-S1 | FTRS-1604 |
| **SEC-017** | Zero unmanaged long-lived credentials | ETL-I1, ETL-I2 | - |
| **SEC-019** | Segmentation test confirms tenant isolation | CRUD-E2 | - |
| **SEC-020** | Remote connections present valid certs | ETL-S3 | - |
| **SEC-029** | All API endpoints enforce CIS2 JWT authentication | DS-S1, CRUD-S2, CRUD-S3, CRUD-T1, CRUD-D1, CRUD-E1, R1, REC-3 | FTRS-1593 |
| **SEC-030** | Certificates and private keys stored securely | ETL-T3, ETL-I1, ETL-I2, CRUD-I3, R1, REC-1 | FTRS-1602 |
| **REL-004** | DoS simulation mitigated; service responsive | DS-D1, DS-D2, DS-D3, CRUD-D3, R3, REC-6 | - |
| **REL-005** | Injection attempt blocked | CRUD-T2 | - |
| **REL-007** | Brute force/auth anomalies rate limited | DS-I1, CRUD-D1, R2 | FTRS-1598 |
| **REL-014** | External outage shows fallback | ETL-D1 | - |
| **REL-016** | Server error shows logout/message per spec | DS-I2, CRUD-I1 | FTRS-973 |
| **REL-017** | Restore drill meets RPO/RTO & ransomware defenses | CRUD-T3 | FTRS-11, FTRS-344 |
| **AVAIL-001** | Availability ≥99.90% | DS-D1, ETL-D3, CRUD-D2, R3 | - |
| **AVAIL-002** | Region DR simulation meets objectives | REC-7 | FTRS-11, FTRS-407 |
| **AVAIL-006** | DR exercise restores service <2h | CRUD-T3, REC-7 | FTRS-11, FTRS-751 |
| **AVAIL-009** | Non-UK access attempts blocked | DS-S1, R3 | - |
| **OBS-008** | TPS per endpoint & threshold alert | CRUD-D2 | FTRS-1688 |
| **OBS-012** | Error percentage metric & alert | ETL-D2, REC-2 | FTRS-1017 |
| **OBS-022** | Audit trail reconstructs user action | DS-R1, CRUD-T1, CRUD-R1 | - |
| **OBS-023** | Audit events share transaction_id | DS-R1, CRUD-R1 | FTRS-1018 |
| **OBS-030** | Distributed trace spans cover E2E | DS-R1, ETL-R1, CRUD-R1 | FTRS-885 |
| **OBS-033** | Unauthorized API access attempts logged | CRUD-S3, R2, REC-2, REC-5 | - |
| **GOV-003** | Solution Architecture Framework approved | R4, REC-4 | - |
| **GOV-007** | FtRS Architects review & approval | ETL-S3, R4, REC-4 | - |
| **GOV-011** | Information Governance approval | DS-E1, CRUD-E2 | - |

### 8.2 Data Classification

| Classification | Description | Examples |
|----------------|-------------|----------|
| **Official** | Routine business information | ODS codes, organisation names, addresses, endpoints |
| **Official-Sensitive** | Requires additional controls | JWT credentials, API keys |

### 8.3 Compliance Considerations

- **GDPR**: Organisation data is not personal data; no special requirements
- **NHS Data Security & Protection Toolkit**: Ensure logging and access controls
- **Cyber Essentials Plus**: Verify controls meet requirements

### 8.4 Related Documents

- [Infrastructure Security Data Flow](infrastructure-security-data-flow.md)
- [ODS to DoS Search Data Flow](ods-to-dos-search-data-flow.md)
- Architecture diagrams: `architecture/data-flows.c4`

---

## 9. Review & Approval

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Author | | | |
| Security Reviewer | | | |
| Technical Lead | | | |
| Product Owner | | | |

---

*This threat model should be reviewed and updated when significant architectural changes occur or at least annually.*
