# ETL ODS Pipeline Specification

## 1. Overview

The ETL ODS pipeline ingests daily (or ad-hoc) changes to NHS ODS Organisation reference data, transforms each record to a FHIR R4B `Organization` representation aligned with FtRS expectations, and applies updates to existing Organisations through internal CRUD APIs. It is composed of two logical Lambda workflows:

1. Processor (date driven or scheduled) – extracts changed organisations since a supplied date, fetches full FHIR resources, transforms, batches, and loads messages to an SQS queue.
2. Consumer (SQS-triggered) – consumes messages and issues `PUT /Organization/{uuid}` FHIR update requests to the API Gateway endpoint, handling OperationOutcome semantics.

Core aims: accurate daily synchronisation (INT-008), semantic fidelity (INT-004), consistent identifier handling (INT-006), robust validation (INT-017), traceability (INT-013, OBS-019), and resilient batch delivery (REL-016).

## 2. Data Flow Stages

| Stage                   | File / Function                                               | Description                                                                   | Key Outputs                            |
| ----------------------- | ------------------------------------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------- | ------------ |
| Extract changed list    | `pipeline/extract.fetch_sync_data(date)`                      | Calls Spine ORD sync endpoint with LastChangeDate to gather changed org links | List of org link JSON records          |
| Parse ODS code          | `pipeline/extract.extract_ods_code(link)`                     | Derives ODS code from link URL path                                           | ODS code string                        |
| Fetch org FHIR resource | `pipeline/extract.fetch_ods_organisation_data(ods_code)`      | Retrieves STU3 Organisation and validates ODS code pattern                    | Raw ODS FHIR JSON                      |
| Fetch FtRS UUID         | `pipeline/extract.fetch_organisation_uuid(ods_code)`          | Queries internal `/Organization?identifier=odsOrganisationCode                | {code}` Bundle to locate existing UUID | UUID or None |
| Transform               | `pipeline/transform.transform_to_payload(ods_fhir, ods_code)` | Maps ODS FHIR to target R4B FHIR Organisation via `OrganizationMapper`        | FHIR Organization (Pydantic)           |
| Assemble payload        | `pipeline/processor.process_organisation(ods_code)`           | Combines path (uuid), body (FHIR JSON) & correlation id into JSON string      | JSON string for message body           |
| Batch & load            | `pipeline/load_data.load_data(transformed_batch)`             | Sends batch (size 10) to SQS queue named by environment & workspace                   | SQS send result (success/fail counts)  |
| Consume & update        | `pipeline/consumer.process_message_and_send_request(record)`  | Performs `PUT` to internal API, handling OperationOutcome                     | HTTP response code & logs              |

## 3. Scheduling & Invocation

| Mode                 | Trigger                                             | Date Resolution                 |
| -------------------- | --------------------------------------------------- | ------------------------------- |
| Manual CLI           | `python cli.py YYYY-MM-DD`                          | Exact provided date             |
| Lambda Event (API)   | POST event payload with `date`                      | Provided date validated         |
| EventBridge Schedule | `processor_lambda_handler` with `is_scheduled=True` | Current UTC - 1 day (yesterday) |

Date validation enforces format `YYYY-MM-DD` and maximum age (≤185 days) via `_validate_date`.

## 4. Message Contract (Producer → SQS → Consumer)

```json
{
  "path": "<uuid>",
  "body": {
    /* FHIR Organization JSON */
  },
  "correlation ID": "<uuid or similar>"
}
```

Batch entries are wrapped again as SQS message bodies (stringified). Consumer unpacks nested JSON and performs PUT with FHIR headers.

## 5. Error & Exception Model

| Stage                                | Detection                                    | Logging Codes                            | Propagation / Response                                  |
| ------------------------------------ | -------------------------------------------- | ---------------------------------------- | ------------------------------------------------------- |
| ODS code validation                  | Regex mismatch                               | `ETL_PROCESSOR_012`                      | Raises `ValueError` (skips organisation)                |
| Missing OrgLink                      | Null link field                              | `ETL_PROCESSOR_021`                      | Skip record                                             |
| Organisation UUID not found          | `fetch_organisation_uuid` returns None       | `ETL_PROCESSOR_027`                      | Skips update (idempotent no-op)                         |
| HTTP failures (external)             | `requests.HTTPError`                         | `ETL_PROCESSOR_022` or utilities codes   | Raise and surface 5xx error                             |
| FHIR OperationOutcome (consumer PUT) | Non-info severity via `handle_fhir_response` | `ETL_CONSUMER_009` etc                   | Raise `OperationOutcomeException` triggers failure item |
| SQS send failures                    | Partial batch responses                      | `ETL_PROCESSOR_015/016`                  | Logged + continue other messages                        |
| Unexpected exception                 | Catch-all                                    | `ETL_PROCESSOR_023` / `ETL_CONSUMER_005` | Logged, failure item recorded                           |

## 6. Non-Functional Mapping

| Concern                   | Implementation Notes                                                     | NFR Codes         |
| ------------------------- | ------------------------------------------------------------------------ | ----------------- |
| Reference data latency    | Daily schedule; last change date delta measured; alert if >24h           | INT-008, PERF-003 |
| Identifier normalisation  | Regex validation & consistent ODS usage                                  | INT-006           |
| Semantic fidelity         | Mapper retains required Organisation fields; round‑trip future test      | INT-004           |
| OperationOutcome handling | Distinguish info vs error severity on PUT                                | INT-005, REL-016  |
| Validation                | Date, ODS code pattern, payload FHIR semantics                           | INT-017           |
| Correlation & tracing     | Correlation ID generated, forwarded across components                    | INT-013, OBS-019  |
| Structured logging        | Log codes across each stage with contextual keys                         | OBS-014, OBS-019  |
| Reliability & resilience  | Batch size control, graceful skips, partial failure isolation            | REL-016           |
| Performance               | Batching (size=10), timeout=20s; measure per batch throughput            | PERF-001          |
| Security                  | Secret retrieval for API key via Secrets Manager, no key leakage in logs | SEC-027, SEC-028  |

## 7. Metrics & Observability (Initial Targets)

| Metric              | Definition                                              | Target               | Source                  |
| ------------------- | ------------------------------------------------------- | -------------------- | ----------------------- |
| Sync latency        | Time between ODS LastChangeDate and pipeline completion | ≤24h                 | Logs + dashboard        |
| Batch success rate  | Successful vs failed SQS entries (%)                    | ≥99%                 | `ETL_PROCESSOR_017/015` |
| PUT success rate    | 2xx vs all PUT attempts                                 | ≥98%                 | Consumer logs           |
| UUID miss ratio     | Orgs with no UUID found / total processed               | <5%                  | `ETL_PROCESSOR_027`     |
| Processing duration | Start → finish for daily run                            | Stable ±10% baseline | Schedule metrics        |

## 8. Security & Access

API key retrieved from Secrets Manager using environment + project prefix. Local development uses `LOCAL_API_KEY`. Ensure least privilege secret policy and avoid printing secret content (only error metadata). Vulnerability scanning integrated via existing CI (SEC-027/028). Correlation ID header preserved.

## 9. Developer Implementation Guide

### 9.1 Setup

```bash
cd services/etl-ods
poetry install
eval $(poetry environment activate)
export LOCAL_APIM_API_URL=http://localhost:8001
export LOCAL_API_KEY=changeme
```

### 9.2 Incremental Story Build Order

1. STORY-217 Scheduling & latency metric (baseline daily run & instrumentation)
2. STORY-218 ODS code validation hardening & tests
3. STORY-219 Correlation ID propagation across all steps
4. STORY-220 FHIR transform fidelity tests (round‑trip scaffolding)
5. STORY-221 Robust batch load failure handling & retry approach
6. STORY-222 Consumer PUT OperationOutcome handling & classification
7. STORY-223 Structured logging enhancement & metrics extraction
8. STORY-224 Error classification & alert integration
9. STORY-225 Latency dashboard & threshold alerting

### 9.3 Test Layout (Suggested)

```text
tests/unit/story_217/test_schedule_latency.py
tests/unit/story_218/test_ods_code_validation.py
tests/unit/story_219/test_correlation_id_propagation.py
tests/unit/story_220/test_fhir_transform_roundtrip.py
tests/unit/story_221/test_batch_load_failures.py
tests/unit/story_222/test_consumer_operation_outcome.py
tests/unit/story_223/test_structured_logging_fields.py
tests/unit/story_224/test_error_classification_alert.py
tests/unit/story_225/test_latency_dashboard_threshold.py
```

### 9.4 Skeleton Enhancements Examples

Correlation ID propagation example (Story-219):

```python
correlation ID = fetch_or_set_correlation_id(event.get("headers", {}).get("X-Correlation-ID"))
ods_processor_logger.append_keys(correlation ID=correlation ID)
```

Batch failure retry (Story-221) pseudo:

```python
failed_entries = response.get("Failed", [])
for fail in failed_entries:
    retry_queue.append(batch[int(fail["Id"]) - 1])  # simple requeue
```

Latency capture (Story-217/225):

```python
start = datetime.now(timezone.utc)
processor(date)
duration = (datetime.now(timezone.utc) - start).total_seconds()
ods_processor_logger.log(OdsETLPipelineLogBase.ETL_PROCESSOR_XXX, duration=duration)
```

### 9.5 Definition of Done per Story

| Item     | Criteria                                               |
| -------- | ------------------------------------------------------ |
| Tests    | New test module green & coverage maintained            |
| NFR refs | Validator exit code 0                                  |
| Logging  | New fields present & queryable                         |
| Metrics  | If applicable, visible in dashboard mock or log sample |
| Docs     | Spec + story acceptance reflect implementation         |

### 9.6 Future Enhancements

| Idea                                           | Benefit                                   | Candidate NFRs     |
| ---------------------------------------------- | ----------------------------------------- | ------------------ |
| Exponential backoff retries for failed PUTs    | Higher reliability under transient errors | REL-016, PERF-006  |
| Parallel extraction workers                    | Reduce total duration                     | PERF-001, SCAL-001 |
| Differential mapping validation service        | Early schema change detection             | INT-004, OBS-019   |
| Automated anomaly detection on UUID miss ratio | Proactive data quality alerts             | OBS-025, INT-008   |

## 10. Backlog Story Mapping

| Story     | Summary                                             | Key NFRs                     |
| --------- | --------------------------------------------------- | ---------------------------- |
| STORY-217 | Daily scheduling & latency instrumentation          | INT-008, PERF-003            |
| STORY-218 | ODS code validation hardening                       | INT-006, INT-017             |
| STORY-219 | Correlation ID propagation end-to-end               | INT-013, OBS-019             |
| STORY-220 | FHIR transform fidelity & UK Core alignment          | INT-004, INT-001 (follow-up) |
| STORY-221 | Batch load failure handling & retry                 | REL-016, OBS-014             |
| STORY-222 | Consumer OperationOutcome & validation semantics    | INT-005, INT-017, REL-016    |
| STORY-223 | Structured logging & metric field enrichment        | OBS-014, PERF-001            |
| STORY-224 | Error classification & alerting integration         | REL-016, OBS-025             |
| STORY-225 | Reference data latency dashboard & threshold alerts | INT-008, PERF-003            |

## 11. Open Questions

| Topic                      | Question                                                                | Next Step                 |
| -------------------------- | ----------------------------------------------------------------------- | ------------------------- |
| Batch size optimisation    | Is 10 optimal vs throughput & cost?                                     | Performance test & adjust |
| Parallelism                | Introduce concurrency without rate limiting issues?                     | Evaluate API limits       |
| Transform validation depth | Add round-trip verification now or after consumer reliability baseline? | Decide post Story-222     |
| Secrets rotation           | Automatic rotation impact on pipeline availability?                     | Security review           |

---

End of ETL ODS specification.
