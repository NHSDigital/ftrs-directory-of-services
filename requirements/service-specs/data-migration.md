# Data Migration Pipeline Specification

## 1. Overview

The Data Migration pipeline ingests legacy Directory of Services (DoS) relational data (PostgreSQL) and transforms selected service and triage code records into the FtRS target domain model (FHIR‑aligned `Organisation`, `Location`, `HealthcareService`, `TriageCode`). It supports two operational modes:

1. Full synchronisation – bulk transform of all supported legacy service types and triage code related domain tables.
2. Incremental (near real‑time) – processing of single change events emitted via DMS (Database Migration Service) and delivered through SQS.

Primary outcomes: accelerate transition to unified FtRS data layer, improve semantic fidelity (INT‑004), ensure identifier normalisation (INT‑006), maintain traceability (INT‑013, OBS‑019) and provide resilient, observable migration runs (REL‑016, OBS‑014).

## 2. Scope

In Scope:

- Transformation of legacy `Service` records (GP Practice, GP Enhanced Access) into Organisation / Location / HealthcareService entities.
- Transformation of SymptomGroup, Disposition, SymptomDiscriminator into `TriageCode` entities (including combination derivations).
- Validation, filtering, and enrichment (metadata cache) per transformer.
- SQS queue population utility for backfilling incremental events.
- Structured logging & metrics emission for migration progress.

Out of Scope:

- Non‑GP service categories (future onboarding).
- Complex multi‑record transactional reconciliation (handled by downstream APIs).
- FHIR round‑trip conformity tests (future enhancement).
- Automated anomaly detection on migration metrics.

## 3. Domain Context

Upstream: Legacy DoS PostgreSQL (read replica), AWS DMS change events, manual CLI invocations, SQS for queued single record changes.
Downstream: FtRS DynamoDB tables (`organisation`, `location`, `healthcare-service`, `triage-code`), internal CRUD APIs (indirect through repository abstraction). Supporting services: Secrets Manager (credentials), CloudWatch / log aggregation, SQS.
Events: Full sync trigger; DMS change (insert/update) event; queue population batch events; triage code combination derivation.

## 4. Functional Flows

Full Sync Flow:

1. CLI / Lambda invokes `handle_full_sync_event`.
2. Iterate all legacy Service records (batched select) -> transformer selection -> validation -> transform -> upsert entities.
3. Iterate triage domain tables (SymptomGroup / Disposition / SymptomDiscriminator) -> build single codes -> build combination codes.
4. Emit start, per‑record, per‑transform, and completion logs + metrics.

Incremental Service Change Flow:

1. DMS event consumed via SQS Lambda / CLI `migrate` single record mode.
2. Parse event → filter unsupported method/table → fetch legacy record.
3. Transformer selection → include decision → validation → transform → upsert.
4. Emit structured logs with elapsed time and entity counts.

Queue Population Flow:

1. CLI or Lambda `populate-queue` filters legacy services by type/status.
2. Generate batches of DMSEvent JSON bodies (size ≤10) and send to SQS.
3. Log batch success/failure; backpressure controlled by thread pool.

Triage Code Combination Flow:

1. Post individual triage code creation, iterate symptom groups.
2. Fetch discriminators; skip if none; create combination triage code aggregate.
3. Upsert and log transformation + metrics.

## 5. Data Model (Target)

Entities:

- Organisation: Derived for GP Practice (name normalisation, ODS code pattern). Not created for Enhanced Access hub services.
- Location: Single physical location for GP Practice (address sourced from legacy record; omitted for Enhanced Access).
- HealthcareService: Category & Type mapped (GP services; consultation vs PCN service). Validation issues annotated.
- TriageCode: Represents symptom group / disposition / discriminator mapping; combination codes aggregate multiple discriminators.

Validation Rules (illustrative):

- ODS code regex (GP Practice: `^[ABCDEFGHJKLMNPVWY][0-9]{5}$`; GP Enhanced Access: first 6 chars `^U\d{5}$`).
- Service active status required (statusid == 1).
- Excluded name patterns for Enhanced Access to filter non‑service operational entries.
- Validation issue severities (fatal/error halt; warning/information continue) via `ValidationResult` semantics.

## 6. Interfaces / Entry Points

CLI (Typer) Commands:
| Command | Purpose | Key Options |
|---------|---------|------------|
| `migrate` | Full or single service sync | `--db-uri`, `--service-id`, `--environment`, `--workspace`, `--output-dir` |
| `populate-queue` | Seed SQS with service DMSEvents | `--db-uri`, `--sqs-queue-url`, `--type-id[]`, `--status-id[]` |
| `export-to-s3` | Dump DynamoDB tables to S3 | `--environment`, `--workspace` |
| `restore-from-s3` | Restore DynamoDB tables from S3 | `--environment`, `--workspace` |

Lambda Handlers:

- `lambda_handler` (queue_populator): populates SQS based on filter event.
- `dms_db_lambda_handler` / trigger variants (not fully documented here) expected to receive DMS change payloads, forward to `DataMigrationApplication`.

Internal API Abstraction:

- Repository `upsert` operations to DynamoDB for each entity type (organisation/location/healthcare-service/triage-code).

Message Contract (DMSEvent JSON): `{ "type": "dms_event", "record_id": <int>, "table_name": "services", "method": "insert"|"update" }`.

## 7. Non-Functional Requirements Mapping

| NFR Code | Applicability                                                   |
| -------- | --------------------------------------------------------------- |
| INT-006  | ODS code pattern validation & normalisation                     |
| INT-004  | Semantic fidelity via transformers & mapping rules              |
| INT-017  | Validation framework (severity-based gating)                    |
| INT-013  | Correlation IDs appended to logs for traceability               |
| REL-016  | Graceful handling of partial failures; skip unsupported records |
| PERF-001 | Batching & per-record elapsed time metrics                      |
| OBS-014  | Structured log fields (event, elapsed_time, entity counts)      |
| OBS-019  | Operational log chain reconstructable by correlation ID         |
| SEC-027  | Dependency scanning & secret retrieval practices                |
| SEC-030  | Secrets Manager use; no plain text credentials in logs           |

## 8. Performance & Capacity

Baseline full sync volume: Number of legacy services (GP Practice + Enhanced Access) O(10^4) scaled by future onboarding. Batch iteration uses select yield-per 1000 to balance memory vs DB round trips. Target per‑record transform latency <250ms p95; full sync completion <30m baseline with parallel SQS population optional. ThreadPool in queue population limited to 10 workers to avoid overwhelming SQS.

## 9. Reliability & Resilience

Failure modes: unsupported transformer, validation halt, DynamoDB upsert error, SQS batch failure. Strategies: per-record try/except with metrics increments (`errors`), skip unsupported or inactive services, continue on partial SQS batch failures, idempotent upsert semantics. Combination triage code creation logs missing discriminators (DM_ETL_012) without failing overall run.

## 10. Security & Privacy

Credentials sourced via Secrets Manager (`replica-rds-credentials`). No secret values logged (password redaction). Access is read-only to source DB. Data classification: healthcare service metadata – no patient identifiers. DMS events validated to prevent injection (table whitelist). JWT / CIS2 not directly handled (performed downstream). Ensure IAM least privilege for SQS, DynamoDB, Secrets Manager (SEC-012 alignment indirectly).

## 11. Observability

Logging: Powertools Logger with structured events (DM*ETL*\* codes). Keys: `run_id`, `environment`, `workspace`, `record_id`, transformer name, elapsed_time, counts. Metrics: aggregated via final DM_ETL_999 log snapshot (`migrated_records`, `errors`). Tracing: correlation IDs appended; can extend to X-Ray/OTel spans later. Alert rules (future): error rate >1% or duration >threshold.

## 12. Scalability

Scaling via horizontal process replication (multiple Lambda shards or parallel CLI instances) reading distinct record segments (future partitioning strategy). Stateless transforms allow concurrency; caution around DynamoDB provisioned throughput. Potential partition key optimisation for high-volume triage codes.

## 13. Compliance & Governance

FHIR transformation aims for R4B alignment (Organisation / HealthcareService mapping). Version alignment documented in future FHIR spec references. Security scanning and dependency policies enforced via CI (link to docs). Audit logs retained per retention policy (OBS-015). Governance reviews track spec changes under Decision Log.

## 14. Deployment & Migration

Configuration via environment variables (.environment / Lambda). Rollout strategy: deploy Lambda functions & verify dry-run subset; full sync executed during controlled window. Backfill with `populate-queue` for incremental event seeding. Future migrations: new transformer classes added with gating tests.

## 15. Risks & Mitigations

| Risk                              | Impact                         | Mitigation                                        |
| --------------------------------- | ------------------------------ | ------------------------------------------------- |
| Transformer drift vs domain model | Incorrect mappings             | Contract tests & schema diff utilities            |
| Validation false negatives        | Data quality issues propagate  | Expand validator rules & severity logic           |
| Slow full sync under scale        | Delayed availability           | Parallelisation & yield_per tuning                |
| SQS batch failures high           | Event loss                     | Retry failed batch; DLQ configuration (future)    |
| Secret exposure in logs           | Security incident              | Strict logging filters & review                   |
| Unsupported service types backlog | Data gap                       | Incremental onboarding plan with new transformers |
| Triage code combination explosion | Performance & storage overhead | Pre-filter discriminators; monitor counts         |

## 16. Open Questions

| Question                                             | Owner         | Target Date |
| ---------------------------------------------------- | ------------- | ----------- |
| Partitioning strategy for large legacy service sets? | Data Eng      | 2025-12-15  |
| Introduce DynamoDB streams for downstream events?    | Platform      | 2026-01-10  |
| Dedicated anomaly metrics for migration variances?   | Observability | 2025-12-30  |
| Automated FHIR profile conformance check?            | Interop       | 2025-12-20  |

## 17. Decisions Log

| Decision                       | Context                | Option Chosen              | Rationale                              | Date       | Owner        |
| ------------------------------ | ---------------------- | -------------------------- | -------------------------------------- | ---------- | ------------ |
| Single-process full sync       | Initial implementation | Sequential batch iteration | Lower complexity & acceptable baseline | 2025-11-25 | Team         |
| Separate triage code processor | Data domain difference | Distinct class & flow      | Clear separation & metrics clarity     | 2025-11-25 | Team         |
| Secrets Manager for DB creds   | Source DB access       | Managed secret retrieval   | Rotation & audit compliance            | 2025-11-25 | Platform Sec |

## 18. Glossary

- DMS: AWS Database Migration Service (change data capture events).
- DMSEvent: Internal JSON structure representing single record change.
- Transformer: Class converting legacy record -> target entities.
- Upsert: Create or replace item in DynamoDB by key.
- ODS Code: NHS Organisation Data Service identifier.
- Triage Code: Encoded symptom/disposition combination for routing.

## 19. Traceability

User Stories (illustrative placeholders): STORY-DM-001 full sync, STORY-DM-002 single change event, STORY-DM-003 triage code combinations, STORY-DM-004 queue population, STORY-DM-005 validation severity gating.
NFR Mapping: See Section 7 table.
Test Suites: `services/data-migration/tests/unit/*` to be expanded per story.

## 20. Change History

| Version | Date       | Author              | Summary                                  |
| ------- | ---------- | ------------------- | ---------------------------------------- |
| 0.1.0   | 2025-11-25 | Automated (Copilot) | Initial reverse‑engineered specification |
