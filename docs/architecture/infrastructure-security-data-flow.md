# FtRS Infrastructure Security Overview (Private Beta)

## Overview

This document describes the infrastructure security architecture for the Find the Right Service (FtRS) system **Private Beta** release, covering:

1. **DoS Search API** - Consumer-facing search-by-ODS-code (read path)
2. **ETL ODS Pipeline** - Internal data ingestion from NHS ODS (write path)

For each service, this document details ingress/egress points, authentication mechanisms, and security controls.

> **Note:** This document reflects the Private Beta architecture. Additional services and access paths may be added in future releases.

---

## Network Architecture Summary

```text
                                    INTERNET
                                        │
                                        ▼
                             ┌─────────────────────┐
                             │ Healthcare Consumers│
                             │ (NHS Applications)  │
                             └──────────┬──────────┘
                                        │
                                        │ HTTPS + API Key
                                        ▼
                             ┌─────────────────────┐
                             │   NHS APIM (GCP)    │
                             │  - dosReadProxy     │
                             │  - API Key Validation│
                             │  - Rate Limiting    │
                             └──────────┬──────────┘
                                        │
                                        │ mTLS (Client Certificate)
                                        ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                          AWS Cloud (eu-west-2)                            │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    Public / Regional Services                       │  │
│  │                                                                     │  │
│  │  ┌─────────────┐    ┌──────────────┐    ┌─────────────────────────┐ │  │
│  │  │ Route 53    │───▶│ ACM Cert     │    │ Shield Advanced (DDoS)  │ │  │
│  │  │ DNS Zone    │    │ *.ftrs.nhs.uk│    │ protects Route 53       │ │  │
│  │  └──────┬──────┘    └──────────────┘    └─────────────────────────┘ │  │
│  │         │                                                           │  │
│  │         ▼                                                           │  │
│  │  ┌─────────────────────────────────────────────────────────────┐    │  │
│  │  │              API Gateway (Regional, REST)                   │    │  │
│  │  │  - Custom domain: dos-search.ftrs.nhs.uk                    │    │  │
│  │  │  - mTLS enabled (client cert validation)                    │    │  │
│  │  │  - Trust store in S3                                        │    │  │
│  │  └──────────────────────────┬──────────────────────────────────┘    │  │
│  └─────────────────────────────┼───────────────────────────────────────┘  │
│                                │                                          │
│                                ▼                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                         FtRS VPC (Private Subnets)                  │  │
│  │                                                                     │  │
│  │  ┌─────────────────────────────────────────────────────────────┐    │  │
│  │  │               DoS Search Lambda Function                    │    │  │
│  │  │  - Python 3.12, X-Ray enabled                               │    │  │
│  │  │  - No public IP address                                     │    │  │
│  │  │  - Runs in private subnet                                   │    │  │
│  │  └──────────────────────────┬──────────────────────────────────┘    │  │
│  │                             │                                       │  │
│  │                             │ VPC Endpoint (Gateway)                │  │
│  │                             ▼                                       │  │
│  │  ┌─────────────────────────────────────────────────────────────┐    │  │
│  │  │                  DynamoDB (Organisation Table)              │    │  │
│  │  │  - On-demand capacity                                       │    │  │
│  │  │  - PITR enabled                                             │    │  │
│  │  │  - KMS encryption                                           │    │  │
│  │  └─────────────────────────────────────────────────────────────┘    │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────┘

Key: Healthcare consumers can ONLY access AWS via NHS APIM proxy layer.
     There is NO direct path from consumers to AWS infrastructure.
```

---

## Internet-Facing Surface

### DoS Search API (Consumer-Facing)

| Attribute          | Value                          |
| ------------------ | ------------------------------ |
| **Endpoint**       | `dos-search.ftrs.nhs.uk`       |
| **Protocol**       | HTTPS (TLS 1.2+)               |
| **Ingress Type**   | API Gateway (Regional)         |
| **Authentication** | mTLS (Mutual TLS) via NHS APIM |
| **Authorisation**  | NHS APIM API key validation    |

**Traffic Flow:**

```text
Healthcare Consumer
    │
    ▼ (HTTPS + API Key)
NHS APIM (GCP)
    │
    ▼ (mTLS - Client Certificate)
Route 53 DNS
    │
    ▼
AWS API Gateway (Regional)
    │
    ▼ (Internal)
DoS Search Lambda (VPC)
    │
    ▼ (VPC Endpoint)
DynamoDB
```

**Authentication Layers:**

1. **NHS APIM**: Validates API key, applies rate limiting, logs access
2. **API Gateway mTLS**: Validates client certificate from trust store (S3-hosted)
3. **WAF Rules**: Geo-blocking (GB/JE/IM only), IP reputation, rate limiting

---

## Internal Services - ETL ODS Pipeline

The ETL ODS pipeline is an internal data ingestion service with **no internet-facing ingress**. It runs on a daily schedule using an Extract-Transform-Load (ETL) pattern with three Lambda functions and two SQS queues.

### Trigger

| Attribute    | Value                           |
| ------------ | ------------------------------- |
| **Type**     | EventBridge Scheduler           |
| **Schedule** | Daily at 01:10 AM (London time) |
| **Target**   | ODS Extractor Lambda            |

### Pipeline Stages

| Stage         | Lambda          | Purpose                                             |
| ------------- | --------------- | --------------------------------------------------- |
| **Extract**   | ODS Extractor   | Fetches organisations from ODS API, queues raw data |
| **Transform** | ODS Transformer | Transforms to FHIR, looks up UUID, queues payload   |
| **Load**      | ODS Loader      | Sends PUT requests to CRUD APIs via APIM            |

### Egress Point 1: ODS Terminology Server (Data Source)

| Attribute          | Value                                             |
| ------------------ | ------------------------------------------------- |
| **Destination**    | NHS ODS Terminology Server (external NHS service) |
| **Source**         | ODS Extractor Lambda (VPC)                        |
| **Protocol**       | HTTPS (TLS 1.2+)                                  |
| **Authentication** | API Key (stored in Secrets Manager)               |
| **Purpose**        | Fetch organisation data from NHS ODS              |

### Egress Point 2: NHS APIM (UUID Lookup - Read Path)

| Attribute          | Value                             |
| ------------------ | --------------------------------- |
| **Destination**    | NHS APIM dosReadProxy             |
| **Source**         | ODS Transformer Lambda (VPC)      |
| **Protocol**       | HTTPS (TLS 1.2+)                  |
| **Authentication** | API Key                           |
| **Purpose**        | Look up internal UUID by ODS code |

### Egress Point 3: NHS APIM (Write Path to CRUD APIs)

| Attribute          | Value                                    |
| ------------------ | ---------------------------------------- |
| **Destination**    | NHS APIM dosWriteProxy                   |
| **Source**         | ODS Loader Lambda (VPC)                  |
| **Protocol**       | HTTPS (TLS 1.2+)                         |
| **Authentication** | JWT (OAuth 2.0 Client Credentials)       |
| **Purpose**        | Write transformed FHIR data to CRUD APIs |

**ETL ODS Traffic Flow:**

```text
EventBridge Scheduler (01:10 AM daily)
    │
    ▼ (Invoke)
┌──────────────────────────────────────────────────────────────────────────────┐
│                         FtRS VPC (Private Subnets)                           │
│                                                                              │
│  ┌──────────────────────┐                                                    │
│  │ ODS Extractor Lambda │───────────────────────────────────────────────────────▶ ODS Terminology
│  │ - Fetch ODS data     │              HTTPS + API Key                          Server (NHS)
│  └──────────┬───────────┘                                                    │
│             │                                                                │
│             ▼ VPC Endpoint                                                   │
│  ┌──────────────────────┐                                                    │
│  │   Transform Queue    │                                                    │
│  │   (KMS encrypted)    │                                                    │
│  └──────────┬───────────┘                                                    │
│             │                                                                │
│             ▼ SQS Trigger (batch size 10)                                    │
│  ┌──────────────────────┐                                                    │
│  │ODS Transformer Lambda│───────────────────────────────────────────────────────▶ NHS APIM
│  │ - Transform to FHIR  │              HTTPS + API Key (UUID lookup)            dosReadProxy
│  │ - Lookup UUID        │                                                    │
│  └──────────┬───────────┘                                                    │
│             │                                                                │
│             ▼ VPC Endpoint                                                   │
│  ┌──────────────────────┐                                                    │
│  │     Load Queue       │                                                    │
│  │   (KMS encrypted)    │                                                    │
│  └──────────┬───────────┘                                                    │
│             │                                                                │
│             ▼ SQS Trigger (batch size 10)                                    │
│  ┌──────────────────────┐                                                    │
│  │  ODS Loader Lambda   │───────────────────────────────────────────────────────▶ NHS APIM
│  │ - PUT to CRUD APIs   │              HTTPS + JWT                              dosWriteProxy
│  └──────────────────────┘                                                    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                                                                                      │
                                                                                      ▼
                                                                           ┌─────────────────┐
                                                                           │ CRUD APIs Lambda│
                                                                           │ (writes to      │
                                                                           │  DynamoDB)      │
                                                                           └─────────────────┘
```

**Security Controls:**

- All Lambda functions have no public IP addresses
- Egress via NAT Gateway only
- JWT credentials stored in Secrets Manager (KMS encrypted)
- ODS API key stored in Secrets Manager (KMS encrypted)
- Both SQS queues encrypted with KMS CMK
- Each queue has a Dead Letter Queue (DLQ) for failed messages
- All outbound traffic is HTTPS only (port 443)
- Reserved concurrency limits on Transformer and Loader (2 each)

---

## WAF (Web Application Firewall) Rules

API Gateway is protected by AWS WAF with:

| Rule               | Priority | Action | Description                         |
| ------------------ | -------- | ------ | ----------------------------------- |
| Geo-blocking       | 11       | Block  | Allow only GB, JE, IM               |
| IP Reputation List | 21       | Block  | AWS managed bad IP list             |
| Anonymous IP List  | 31       | Block  | VPN, proxy, Tor detection           |
| Rate Limiting      | 41       | Block  | 100 requests per 120 seconds per IP |
| Common Rule Set    | 51       | Block  | OWASP Top 10 protections            |
| Known Bad Inputs   | 61       | Block  | Log4j, etc.                         |

---

## DDoS Protection

| Component            | Protection            |
| -------------------- | --------------------- |
| Route 53 Hosted Zone | AWS Shield Advanced   |
| API Gateway          | WAF + Shield Standard |

Shield Advanced provides:

- Proactive engagement enabled
- 24/7 DDoS Response Team (DRT) access
- Automatic application layer DDoS mitigation

---

## VPC Network Controls

### Private Subnet Architecture

All Lambda functions run in **private subnets** with:

- No public IP addresses
- Egress via NAT Gateway (for internet access)
- VPC Endpoints for AWS services (DynamoDB, SQS, Secrets Manager, S3)

### Network ACLs

| Direction | Port        | Protocol | CIDR        | Purpose                    |
| --------- | ----------- | -------- | ----------- | -------------------------- |
| Inbound   | 443         | TCP      | VPC CIDR    | HTTPS responses            |
| Inbound   | 32768-65535 | TCP      | 0.0.0.0/0   | Ephemeral (return traffic) |
| Outbound  | 443         | TCP      | 0.0.0.0/0   | HTTPS (API calls)          |
| Outbound  | 53          | UDP      | VPC DNS     | DNS resolution             |
| Outbound  | 123         | UDP      | NTP servers | Time synchronisation       |

---

## Administrative Access

### AWS Console Access

| Method      | Authentication                |
| ----------- | ----------------------------- |
| AWS Console | AWS IAM Identity Center (SSO) |
| AWS CLI     | Temporary credentials via SSO |

### GitHub Actions (CI/CD)

| Attribute          | Value                            |
| ------------------ | -------------------------------- |
| **Authentication** | OIDC Federation                  |
| **Trust Policy**   | GitHub Actions OIDC provider     |
| **Scope**          | Limited to specific repositories |

```json
{
  "Federated": "arn:aws:iam::{account}:oidc-provider/token.actions.githubusercontent.com"
}
```

---

## Encryption Summary

| Data Type                | At Rest | In Transit              |
| ------------------------ | ------- | ----------------------- |
| DynamoDB tables          | KMS CMK | TLS 1.2+ (VPC Endpoint) |
| SQS queues               | KMS CMK | TLS 1.2+ (VPC Endpoint) |
| Secrets Manager          | KMS CMK | TLS 1.2+                |
| S3 buckets (trust store) | SSE-S3  | TLS 1.2+                |
| API traffic              | N/A     | TLS 1.2+ / mTLS         |

---

## Logging and Monitoring

| Component              | Log Destination    | Retention    |
| ---------------------- | ------------------ | ------------ |
| API Gateway            | CloudWatch Logs    | 90 days      |
| DoS Search Lambda      | CloudWatch Logs    | 30 days      |
| ODS Extractor Lambda   | CloudWatch Logs    | 30 days      |
| ODS Transformer Lambda | CloudWatch Logs    | 30 days      |
| ODS Loader Lambda      | CloudWatch Logs    | 30 days      |
| WAF                    | CloudWatch Metrics | Configurable |
| Lambda X-Ray Traces    | X-Ray              | Configurable |

---

## Summary: Attack Surface

| Surface                       | Exposure                   | Protection                                                |
| ----------------------------- | -------------------------- | --------------------------------------------------------- |
| DoS Search API                | Internet (via APIM only)   | mTLS, WAF, Shield Advanced, Geo-blocking                  |
| DoS Search Lambda             | No direct ingress          | Private subnet, VPC endpoints                             |
| ETL ODS Lambdas (3)           | No ingress (scheduled/SQS) | Private subnet, egress-only via NAT, reserved concurrency |
| ODS Terminology Server        | Egress only                | API key auth, HTTPS, Secrets Manager                      |
| NHS APIM (read path)          | Egress only                | API key auth, HTTPS                                       |
| NHS APIM (write path)         | Egress only                | JWT auth, HTTPS, Secrets Manager                          |
| SQS Queues (Transform + Load) | No direct access           | VPC endpoint only, KMS encryption, DLQs                   |
| DynamoDB                      | No direct ingress          | VPC endpoint only, KMS encryption                         |
| AWS Console                   | Federated SSO              | IAM Identity Center                                       |
| CI/CD Pipeline                | GitHub OIDC                | OIDC Federation, scoped roles                             |

---

## Related Documentation

- Data flow diagrams: `architecture/data-flows.c4`
- Deployment topology: `architecture/deployment.c4`
- ODS ETL data flow: `docs/architecture/ods-to-dos-search-data-flow.md`
