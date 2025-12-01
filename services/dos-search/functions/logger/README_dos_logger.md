# DOS Logger — dos-search service

## Summary

This document explains how the service-local DOS logging wrapper works and how the three files in this service interact to produce structured JSON logging suitable for CloudWatch (via aws_lambda_powertools). It's intended for developers working on the `dos-search` stack.

The logger is implemented as a singular instance instantiated during the `init` phase of a Lambda execution, and is shared between DOS Python module files during execution. Clearing down of appended keys is handled by the `clear_state=True` setting specified in the Lambda Handler as a decorator, which should be sufficient for current logging behavior to avoid log data accidentally persisting into a subsequent invocation. If more explicit control is required in the future, a `clear_state` method is implemented as a shallow wrapper over the underlying PowerTools `clear_state` method on the DOS Logger to support this. For more information about Lambda concurrency and how this setting avoids contamination, see [AWS Lambda Concurrency](https://docs.aws.amazon.com/lambda/latest/dg/lambda-concurrency.html).

## Files covered

- `services/dos-search/functions/dos_logger.py` — the DOS logging wrapper used by this service. It builds the structured `extra` payload (ftrs*\*, nhsd*\_, Opt\_\_ fields) and delegates top-level metadata (timestamp, location, `function_name`, `xray_trace_id`, etc.) to aws_lambda_powertools' `Logger`.
- `services/dos-search/functions/dos_search_ods_code_function.py` — the Lambda handler. It calls `dos_logger.info(...)` for request and response logging and demonstrates passing response metrics back to the logger.

## Goals and behavior

- Produce structured JSON logs for every endpoint (except `healthcheck`) using `aws_lambda_powertools.Logger`.
- Add DOS-specific fields to every log line via the powertools `extra` argument so they appear at the same JSON level in CloudWatch.
- Always include mandatory DOS fields (present in every log line).

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
