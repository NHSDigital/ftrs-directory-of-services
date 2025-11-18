# FTRS Logger — dos-search service

## Summary

This document explains how the service-local FTRS logging wrapper works and how the three files in this service interact to produce structured JSON logging suitable for CloudWatch (via aws_lambda_powertools). It's intended for developers working on the `dos-search` stack.

## Files covered

- `services/dos-search/functions/dos_logger.py` — the FTRS logging wrapper used by this service. It builds the structured `extra` payload (ftrs*\*, nhsd*\_, Opt\_\_ fields) and delegates top-level metadata (timestamp, location, `function_name`, `xray_trace_id`, etc.) to aws_lambda_powertools' `Logger`.
- `services/dos-search/functions/dos_search_ods_code_function.py` — the Lambda handler. It calls `dos_logger.info(...)` for request and response logging and demonstrates passing response metrics back to the logger.

## Goals and behavior

- Produce structured JSON logs for every endpoint (except `healthcheck`) using `aws_lambda_powertools.Logger`.
- Add FTRS-specific fields to every log line via the powertools `extra` argument so they appear at the same JSON level in CloudWatch.
- Always include mandatory FTRS fields (present in every log line).

## Key Concepts

### \_last_log_data

- To ensure the key fields are present in all logs without having to pass the bulky event object around, the DosLogger class persists the last specified `log_data` keyword argument via this attribute.
```python
  dos_logger = DosLogger

  log_data = DosLogger.extract(event)

  dos_logger.info("Message", log_data=log_data)
  dos_logger.warning("Message")
  # Outputs warning log with `log_data` due to earlier call to `info` method
```

- Due to this, it is important that all modules use the same instance of the logger rather than creating their own. The common logger used by all current modules is declared in `/functions/dos_logger.py`

- To explicitly avoid the accidental persisting of identifying information (such as ID values) and therefore contaminating our logs, all Lambda functions should call the provided helper cleanup method `clear_log_data` just before ending execution, such as immediately before the response is returned. See `/functions/dos_search_ods_code_function.py` for reference.
