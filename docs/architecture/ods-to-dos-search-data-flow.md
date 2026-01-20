# ODS to DoS Search: End-to-End Data Flow

## Overview

This document describes how organisation data is synchronised from the external NHS ODS Terminology API into the Find the Right Service (FtRS) system and subsequently queried by healthcare consumers.

**Schedule:** Daily at 01:10 AM (London time)
**Trigger:** EventBridge Scheduler
**Data Format:** HL7 FHIR R4
**Architecture:** Extract-Transform-Load (ETL) pipeline with 3 Lambdas and 2 SQS queues

---

## Data Flow Diagram

```text
┌─────────────────────┐
│ ODS Terminology API │ (External NHS API)
└─────────┬───────────┘
          │ 1. Fetch modified organisations (FHIR Bundle)
          ▼
┌─────────────────────┐
│  ODS Extractor      │ (Lambda - VPC)
│  Lambda             │
└─────────┬───────────┘
          │ 2. Queue raw organisation data
          ▼
┌─────────────────────┐
│  Transform Queue    │ (KMS Encrypted)
│  (SQS)              │
└─────────┬───────────┘
          │ 3. SQS trigger (batch size: 10)
          ▼
┌─────────────────────┐
│  ODS Transformer    │ (Lambda - VPC)
│  Lambda             │
└─────────┬───────────┘
          │ 4-7. UUID lookup via APIM → CRUD APIs → DynamoDB
          │ 8. Queue transformed FHIR payloads
          ▼
┌─────────────────────┐
│  Load Queue         │ (KMS Encrypted)
│  (SQS)              │
└─────────┬───────────┘
          │ 9. SQS trigger (batch size: 10)
          ▼
┌─────────────────────┐
│  ODS Loader         │ (Lambda - VPC)
│  Lambda             │
└─────────┬───────────┘
          │ 10-13. PUT via APIM → CRUD APIs → DynamoDB
          ▼
┌─────────────────────┐
│  DynamoDB           │ (Organisation Table)
│  (Encrypted, PITR)  │
└─────────────────────┘
          ▲
          │ 14-19. Query via APIM → DoS Search → DynamoDB
┌─────────┴───────────┐
│ Healthcare Consumer │ (e.g. 111 Online, GP Systems)
└─────────────────────┘
```

---

## Data Flow Stages

### Stage 1: Data Extraction (Daily Scheduled)

| Step | Source               | Destination          | Protocol | Description                                                         |
| ---- | -------------------- | -------------------- | -------- | ------------------------------------------------------------------- |
| 1    | ODS Terminology API  | ODS Extractor Lambda | HTTPS    | Fetches organisations modified on a given date (FHIR Bundle format) |
| 2    | ODS Extractor Lambda | Transform Queue      | AWS SDK  | Sends raw organisation data for transformation                      |

### Stage 2: Data Transformation

| Step | Source                 | Destination            | Protocol     | Description                                     |
| ---- | ---------------------- | ---------------------- | ------------ | ----------------------------------------------- |
| 3    | Transform Queue        | ODS Transformer Lambda | SQS Event    | Event-driven trigger (batch size: 10)           |
| 4    | ODS Transformer Lambda | APIM Read Proxy        | HTTPS        | GET request to lookup internal UUID by ODS code |
| 5    | APIM Read Proxy        | API Gateway            | HTTPS (mTLS) | Authenticates and proxies request               |
| 6    | API Gateway            | CRUD APIs Lambda       | Internal     | Routes to organisation query endpoint           |
| 7    | CRUD APIs Lambda       | DynamoDB               | AWS SDK      | Queries by ODS code index (GSI)                 |
| 8    | ODS Transformer Lambda | Load Queue             | AWS SDK      | Sends transformed FHIR payloads                 |

### Stage 3: Data Loading (Write Path)

| Step | Source            | Destination       | Protocol     | Description                                      |
| ---- | ----------------- | ----------------- | ------------ | ------------------------------------------------ |
| 9    | Load Queue        | ODS Loader Lambda | SQS Event    | Event-driven trigger (batch size: 10)            |
| 10   | ODS Loader Lambda | APIM Write Proxy  | HTTPS        | PUT /Organization/{uuid} with JWT authentication |
| 11   | APIM Write Proxy  | API Gateway       | HTTPS (mTLS) | Validates JWT, proxies to internal API           |
| 12   | API Gateway       | CRUD APIs Lambda  | Internal     | Routes to update endpoint                        |
| 13   | CRUD APIs Lambda  | DynamoDB          | AWS SDK      | Persists organisation data                       |

### Stage 4: External Query (Read Path)

| Step | Source              | Destination       | Protocol     | Description                            |
| ---- | ------------------- | ----------------- | ------------ | -------------------------------------- |
| 14   | Healthcare Consumer | APIM Read Proxy   | HTTPS        | FHIR search request with API key       |
| 15   | APIM Read Proxy     | API Gateway       | HTTPS (mTLS) | Authenticates, proxies search          |
| 16   | API Gateway         | DoS Search Lambda | Internal     | Routes to search handler               |
| 17   | DoS Search Lambda   | FTRS Service      | Internal     | Invokes service layer                  |
| 18   | FTRS Service        | DynamoDB          | AWS SDK      | Queries organisation by ODS code       |
| 19   | FTRS Service        | Bundle Mapper     | Internal     | Maps to FHIR searchset Bundle response |

---

## Security Controls

| Control                         | Implementation                | Notes                                            |
| ------------------------------- | ----------------------------- | ------------------------------------------------ |
| **Authentication (Write Path)** | JWT tokens via NHS APIM       | Short-lived tokens, OAuth 2.0 client credentials |
| **Authentication (Read Path)**  | API key via NHS APIM          | Registered consumer applications                 |
| **Transport Security**          | mTLS on API Gateway           | Client certificate validation                    |
| **Encryption in Transit**       | TLS 1.2+                      | All connections                                  |
| **Encryption at Rest**          | KMS Customer Managed Keys     | SQS queues, DynamoDB, Secrets Manager            |
| **Network Isolation**           | Lambda in private VPC subnets | No public IP addresses                           |
| **Secrets Management**          | AWS Secrets Manager           | JWT credentials, ODS API key                     |
| **DDoS Protection**             | AWS Shield Advanced           | Protects Route 53 hosted zone                    |
| **Concurrency Control**         | Reserved concurrency          | Transformer: 2, Loader: 2                        |
| **Logging**                     | CloudWatch Logs               | All Lambda invocations                           |
| **Tracing**                     | AWS X-Ray                     | End-to-end request tracing                       |

---

## Trust Boundaries

| Boundary                | Description                           | Controls                                                   |
| ----------------------- | ------------------------------------- | ---------------------------------------------------------- |
| **External → NHS APIM** | Public internet to NHS API Management | API key/JWT authentication, rate limiting, IP allowlisting |
| **NHS APIM → AWS**      | GCP to AWS cross-cloud                | mTLS with client certificate validation                    |
| **Internet → VPC**      | Public to private network             | NAT Gateway egress only, no inbound                        |
| **VPC → AWS Services**  | Lambda to managed services            | VPC Endpoints (private connectivity)                       |

---

## Network Flow

```asciidoc
┌─────────────────────────────────────────────────────────────────────────┐
│                           INTERNET                                      │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐    ┌─────────────────────┐    ┌───────────────┐
│ ODS API       │    │ NHS APIM            │    │ Healthcare    │
│ (External)    │    │ - dosReadProxy      │    │ Consumers     │
└───────┬───────┘    │ - dosWriteProxy     │    └───────┬───────┘
        │            └─────────┬───────────┘            │
        │                      │ mTLS                   │
        │                      ▼                        │
        │            ┌─────────────────────┐            │
        │            │ Route 53 + Shield   │            │
        │            └─────────┬───────────┘            │
        │                      │                        │
        │                      ▼                        │
        │            ┌─────────────────────┐            │
        │            │ API Gateway (mTLS)  │◄───────────┘
        │            └─────────┬───────────┘
        │                      │
┌───────┴──────────────────────┴───────────────────────────────────┐
│                         AWS VPC                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │
│  │ ODS         │  │ ODS         │  │ ODS         │               │
│  │ Extractor   │  │ Transformer │  │ Loader      │               │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘               │
│         │                │                │                      │
│         ▼                ▼                ▼                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │
│  │ DoS Search  │  │ CRUD APIs   │  │             │               │
│  │ Lambda      │  │ Lambda      │  │             │               │
│  └──────┬──────┘  └──────┬──────┘  │             │               │
│         │                │         │             │               │
│         └────────────────┴─────────┘             │               │
│                          │ VPC Endpoints                         │
└──────────────────────────┼───────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ DynamoDB      │  │ SQS (x2)      │  │ Secrets Mgr   │
│ (KMS)         │  │ (KMS)         │  │ (KMS)         │
└───────────────┘  └───────────────┘  └───────────────┘
```

---

## Data Classification

| Data Element                         | Classification | Retention  |
| ------------------------------------ | -------------- | ---------- |
| Organisation identifiers (ODS codes) | Official       | Indefinite |
| Organisation names and addresses     | Official       | Indefinite |
| Service endpoints                    | Official       | Indefinite |
| API access logs                      | Official       | 90 days    |
| Lambda execution logs                | Official       | 30 days    |

---

## Failure Handling

| Scenario                        | Handling                                  | Alert                             |
| ------------------------------- | ----------------------------------------- | --------------------------------- |
| ODS API unavailable             | Retry with exponential backoff            | CloudWatch alarm after 3 failures |
| Transform Queue message failure | Dead Letter Queue (DLQ) after max retries | DLQ depth alarm                   |
| Load Queue message failure      | Dead Letter Queue (DLQ) after max retries | DLQ depth alarm                   |
| Rate limit exceeded (429)       | Message returned to queue for retry       | Logged, auto-retry                |
| DynamoDB write failure          | Lambda retry (2 attempts)                 | Error rate alarm                  |
| JWT token expiry                | Automatic refresh from Secrets Manager    | None (automatic)                  |

---

## Related Documentation

- Architecture diagrams: `architecture/data-flows.c4`
- Deployment configuration: `architecture/deployment.c4`
- ETL ODS service: `services/etl-ods/`
- DoS Search service: `services/dos-search/`
- CRUD APIs service: `services/crud-apis/`
