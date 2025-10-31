# FTRS Logger — dos-search service

## Summary

This document explains how the service-local FTRS logging wrapper works and how the three files in this service interact to produce structured JSON logging suitable for CloudWatch (via aws_lambda_powertools). It's intended for developers working on the `dos-search` stack.

## Files covered

- `services/dos-search/functions/ftrs_logger.py` — the FTRS logging wrapper used by this service. It builds the structured `extra` payload (ftrs*\*, nhsd*_, Opt\__ fields) and delegates top-level metadata (timestamp, location, `function_name`, `xray_trace_id`, etc.) to aws_lambda_powertools' `Logger`.
- `services/dos-search/functions/dos_search_ods_code_function.py` — the Lambda handler. It calls `ftrs_logger.info(...)` for request and response logging and demonstrates passing response metrics back to the logger.
- `services/dos-search/run_ftrs_logger_test.py` — a small local test harness that exercises the wrapper and writes example JSON outputs to disk for inspection.

## Goals and behavior

- Produce structured JSON logs for every endpoint (except `healthcheck`) using `aws_lambda_powertools.Logger`.
- Add FTRS-specific fields to every log line via the powertools `extra` argument so they appear at the same JSON level in CloudWatch.
- Always include mandatory FTRS fields (present in every log line), and include one-time fields prefixed with `Opt_` (these should be present but may contain a placeholder when not available).

## Key concepts

- powertools metadata: `aws_lambda_powertools.Logger` provides the top-level metadata (timestamp, location, service/function, correlation id, `xray_trace_id`). The wrapper passes an `extra` dict with FTRS fields; powertools merges both into the final JSON.
- `extra` payload: the wrapper builds an object with `ftrs_*`, `nhsd_*`, and `Opt_*` fields and passes it to powertools as `extra=`.
- Missing values: by default missing fields show the placeholder `TBC` (to meet acceptance criteria). This placeholder is configurable (see Environment section).

## ftrs_logger.py — how it works (high level)

Main public API:

- `FtrsLogger(service: str = "ftrs", debug: bool = False)` — constructor
- `.info(message, event=None, **detail)` — info-level log
- `.warning(...)`, `.error(...)`, `.exception(...)` — other levels
- `.info_payload(message, event=None, **detail)` — emit only the structured payload (no powertools metadata)
- `.get_powertools_metadata(context=None)` — best-effort view of powertools-like metadata for tests/debugging

Important internals:

- `_extract(event)`

  - Normalizes headers (case-insensitive) and extracts values for:
    - ftrs_nhsd_correlation_id, nhsd_correlation_id
    - ftrs_nhsd_request_id, nhsd_request_id
    - ftrs_message_id, nhsd_message_id
    - ftrs_message_category (defaults to "LOGGING")
    - ftrs_environment (ENVIRONMENT or WORKSPACE or service)
    - ftrs_api_version (from header or placeholder)
    - ftrs_lambda_version (from AWS_LAMBDA_FUNCTION_VERSION or placeholder)
    - ftrs_response_time, ftrs_response_size (placeholders by default)
    - Opt_ftrs_end_user_role, Opt_ftrs_client_id, Opt_ftrs_application_name
    - Opt_ftrs_request_parms (merged `queryStringParameters` + `pathParameters`)
  - Missing values use the configured placeholder (default `TBC`) or `null` if configured as such.

- `_append_powertools_context(extra)`

  - Best-effort: if the Powertools Logger exposes `append_keys`, we call `append_keys(correlation_id=<incoming-header>)` so the powertools top-level `correlation_id` matches the APIM-supplied value.
  - We also record the last appended correlation id locally for testing/debugging.

- `_log_with_level(level, message, event, **detail)`
  - Calls `_extract(event)` to build `extra`.
  - Moves certain override keys from `detail` to the top-level `extra` (these are: `ftrs_response_time`, `ftrs_response_size`, `ftrs_message_category`, `ftrs_response`).
  - Any remaining `detail` keyword args are nested under `extra['detail']` (this is where `ods_code` goes by default).
  - Calls powertools: `self._logger.info(message, extra=extra)` (or other level variants). Powertools then emits the final JSON.

## Placeholder configuration

- Environment variable: `FTRS_LOG_PLACEHOLDER`
  - Default: `TBC` (string) — matches acceptance criteria that missing fields should "state TBC".
  - If set to `NULL` (case-insensitive), the wrapper will use Python `None` for missing values, which becomes JSON `null`.

## Where `ods_code` ends up

- When you call `ftrs_logger.info("Received request for odsCode", event=event, ods_code=ods_code)`, the wrapper behavior is:
  - `ods_code` is not a recognised top-level override, so it is preserved and placed under `extra['detail']`.
  - The powertools JSON will therefore contain `"detail": { "ods_code": "A12345" }` unless you change the wrapper to promote `ods_code` to a top-level key.
  - Note: The request params are also available under `Opt_ftrs_request_parms` (merged query/path params), so if `odsCode` came as a query parameter it will appear there as well.

## How `dos_search_ods_code_function.py` uses the logger

- At request start: `ftrs_logger.info("Received request for odsCode", event=event, ods_code=ods_code)` — records request fields and adds `ods_code` to `detail`.
- On validation error: `ftrs_logger.warning("Validation error occurred", event=event, validation_errors=...)` — stores validation errors under `detail`.
- On success: the handler measures duration and response size and calls:

  ```py
  ftrs_logger.info(
      "Successfully processed",
      event=event,
      ftrs_response_time=f"{duration_ms}ms",
      ftrs_response_size=response_size,
  )
  ```

  where `ftrs_response_time` and `ftrs_response_size` are promoted to top-level keys in `extra` by the wrapper.

## Local test harness: run_ftrs_logger_test.py

Purpose: exercise the wrapper locally and produce files for inspection.

Where: `services/dos-search/run_ftrs_logger_test.py`

What it does:

- Instantiates `FtrsLogger(service='dos-search', debug=True)`
- Builds a sample `event` with headers and query params
- Prints the extracted `extra` object (`_extract(event)`), a best-effort powertools metadata snapshot (`get_powertools_metadata`), and a merged object for local inspection
- Emits an actual powertools log via `ftrs_logger.info(...)` (the common-case production path)
- Emits a payload-only JSON via `ftrs_logger.info_payload(...)`
- Writes results to `ftrs_logger_test_output.json` and `ftrs_logger_payload_output.json`

Run locally (Poetry)

```bash
cd services/dos-search
poetry run python -u run_ftrs_logger_test.py
```

Files created:

- `ftrs_logger_test_output.json` — contains three keys: `meta`, `extra`, `merged` (for inspection)
- `ftrs_logger_payload_output.json` — contains the payload-only JSON output

Example powertools log (single-line JSON — simplified):

```json
{
  "level": "INFO",
  "location": "info:238",
  "message": "Received request for odsCode",
  "timestamp": "2025-10-30 21:09:13,477+0000",
  "service": "dos-search",
  "correlation_id": "<EXAMPLE_CORRELATION_ID>",
  "ftrs_nhsd_correlation_id": "<EXAMPLE_CORRELATION_ID>",
  "ftrs_nhsd_request_id": "<EXAMPLE_REQUEST_ID>",
  "ftrs_message_id": "<EXAMPLE_APIM_MESSAGE_ID>",
  "ftrs_message_category": "LOGGING",
  "ftrs_environment": "Development",
  "Opt_ftrs_end_user_role": "clinician",
  "Opt_ftrs_client_id": "<EXAMPLE_CLIENT_ID>",
  "Opt_ftrs_request_parms": { "odsCode": "A12345" },
  "detail": { "ods_code": "A12345" }
}
```

## Searching logs in CloudWatch

Because powertools emits JSON and merges `extra` into the same object, you can search directly on fields:

- Example to filter by correlation id (CloudWatch filter syntax):

  ```json
  { $.correlation_id = "<EXAMPLE_CORRELATION_ID>" }
  ```

- Example to find logs for an ods_code (present under `detail`):

  ```json
  { $.detail.ods_code = "A12345" }
  ```

If you want ods_code searchable at top-level instead, I can update the wrapper to promote `ods_code` into the top-level `extra` (e.g. `extra['ods_code'] = value`). Let me know if you want that.

## Acceptance criteria mapping

- Mandatory fields present in every log line: implemented in `_extract` with placeholder defaults (configurable via `FTRS_LOG_PLACEHOLDER`) — DONE
- One-time fields prefixed with `Opt_`: implemented (`Opt_ftrs_end_user_role`, `Opt_ftrs_client_id`, `Opt_ftrs_application_name`, `Opt_ftrs_request_parms`) — DONE
- Fields visible even when missing (placeholder): default `TBC` used — DONE (configurable)

## Configuration and environment vars

- `FTRS_LOG_PLACEHOLDER` — default `TBC`. Set to `NULL` to emit JSON `null` for missing values.
- `ENVIRONMENT` / `WORKSPACE` — used to populate `ftrs_environment`.
- `AWS_LAMBDA_FUNCTION_VERSION` — used to populate `ftrs_lambda_version`.
