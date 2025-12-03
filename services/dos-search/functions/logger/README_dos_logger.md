# DOS Logger — dos-search service

## Overview

`DosLogger` is a service-local wrapper around AWS Lambda Powertools' `Logger` that adds structured DOS (Directory of Services) fields to all logs. It provides a consistent logging interface with mandatory APIM headers and optional request context fields.

The logger is implemented as a singular instance instantiated during the `init` phase of a Lambda execution, and is shared between DOS Python module files during execution. Clearing down of appended keys is handled by the `clear_state=True` setting specified in the Lambda Handler as a decorator, which should be sufficient for current logging behavior to avoid log data accidentally persisting into a subsequent invocation. If more explicit control is required in the future, a `clear_state` method is implemented as a shallow wrapper over the underlying PowerTools `clear_state` method on the DOS Logger to support this. For more information about Lambda concurrency and how this setting avoids contamination, see [AWS Lambda Concurrency](https://docs.aws.amazon.com/lambda/latest/dg/lambda-concurrency.html).

## Features

- **Structured logging** with DOS-specific fields
- **Simplified Initialisation method** - `init()` method handles extraction of relevant headers/data from APIM requests (correlation IDs, request IDs, message IDs) and automatically logs out key data, as well as appending other key fields to all future logs for the duration of execution.
- **Wrapper methods** that mirror AWS Lambda Powertools Logger interface, as well as providing access to the underlying Logger to facilitate access to that functionality as and when needed.
- **Configured Placeholders for any missing fields** to gracefully handle any issues with missing fields, while clearly drawing attention to such gaps when logs are checked.

## Getting started

Import `DosLogger` from `functions.logger.dos_logger`:

```python
from functions.logger.dos_logger import DosLogger
```

### Basic Usage

```python
# Initialize the logger (singleton pattern)
dos_logger = DosLogger.get(service="dos-search")
logger = dos_logger._logger  # Access to underlying powertools logger

# Log at the start of your Lambda handler
@logger.inject_lambda_context
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    dos_logger.init(event)  # Extract and log request context
    dos_logger.info("Processing request", ods_code="M00081046")
    return {"statusCode": 200}
```

Access to the underlying Powertools logger allows the use of Powertools-specific utilities, such as the `@logger.inject_lambda_context` decorator, while minimising complexity.
Referencing the logger from the DosLogger class instance via `dos_logger._logger` ensures any references to either the DosLogger or the Powertools remain consistent. While it is possible to achieve the same behaviour via referencing the PowerTools Logger as `Logger(service=`SERVICE`)`, reusing the reference via class attribute makes the relationship explicit and minimises risk of misconfiguration.

### Logging Methods

All logging methods accept a message and optional keyword arguments for structured fields:

```python
dos_logger.debug("Debug message", field1="value1")
dos_logger.info("Info message", field2="value2", field2_2="value2_2")
dos_logger.warning("Warning message", field3="value3")
dos_logger.error("Error message", field4="value4")
dos_logger.exception("Exception occurred", error_detail="details")
```

## Structured Fields

### Mandatory Fields (Extracted at Initialization)

These fields are extracted from API Gateway Event via the `extract` method and/or initialised as static/default fields, and appended to all subsequent logs for the duration of a Lambda execution when the `init` method is called:

| Field                     | Source                                   | Placeholder           |
| ------------------------- | ---------------------------------------- | --------------------- |
| `dos_nhsd_correlation_id` | `NHSD-Correlation-ID` header             | `DOS_LOG_PLACEHOLDER` |
| `dos_nhsd_request_id`     | `NHSD-Request-ID` header                 | `DOS_LOG_PLACEHOLDER` |
| `dos_message_id`          | `NHSD-Message-Id` header                 | `DOS_LOG_PLACEHOLDER` |
| `dos_message_category`    | Default: `"LOGGING"` (can be overridden) | N/A                   |
| `logger`                  | Identifier: `"dos_logger"`               | N/A                   |

### One-Time Fields (Logged Once at Initialization)

These optional fields are extracted from the API Gateway Event and/or Lambda Execution context via the `extract_one_time` method, and logged once when the `init` method is called:

| Field                      | Source                                  | Placeholder           |
| -------------------------- | --------------------------------------- | --------------------- |
| `opt_dos_api_version`      | `NHSD-Api-Version` header               | `DOS_LOG_PLACEHOLDER` |
| `opt_dos_end_user_role`    | `NHSD-End-User-Role` header             | `DOS_LOG_PLACEHOLDER` |
| `opt_dos_client_id`        | `NHSD-Client-Id` header                 | `DOS_LOG_PLACEHOLDER` |
| `opt_dos_application_name` | `NHSD-Connecting-Party-App-Name` header | `DOS_LOG_PLACEHOLDER` |
| `opt_dos_request_params`   | Query, path, and request context        | `{}`                  |
| `opt_dos_environment`      | `ENVIRONMENT` environment var                   | `DOS_LOG_PLACEHOLDER` |
| `opt_dos_lambda_version`   | `AWS_LAMBDA_FUNCTION_VERSION` environment var   | `DOS_LOG_PLACEHOLDER` |

### Custom Message Categories

Override the `dos_message_category` field to categorize logs:

```python
dos_logger.info(
    "Received request",
    ods_code="M00081046",
    dos_message_category="REQUEST",
)

dos_logger.info(
    "Response sent",
    status_code=200,
    dos_message_category="RESPONSE",
)

dos_logger.info(
    "Processing metrics",
    response_time="150ms",
    response_size=2048,
    dos_message_category="METRICS",
)
```

These categories are intended to provide syntactical references to the content of the log. Currently, the following categories have explicit intended uses (See [Logging at the Lambda Level](https://nhsd-confluence.digital.nhs.uk/spaces/DOSIS/pages/1199912451/Logging+at+the+Lambda+level) for more information):
| Category | Description |
|-------|--------|
| `LOGGING` | General Logs. Configured as the default when category is not specified |
| `REQUEST` | Logs relating to Request content |
| `RESPONSE` | Logs relating to Response content |
| `METRICS` | Logs relating to performance or reporting metrics |

## Usage Example

See dos_search_ods_code_function.py for a complete example:

```python
from functions.logger.dos_logger import DosLogger

service = "dos-search"
dos_logger = DosLogger.get(service=service)
logger = dos_logger._logger

@app.get("/Organization")
@tracer.capture_method
def get_organization() -> Response:
    start = time.time()
    dos_logger.init(app.current_event)
    try:
        dos_logger.info(
            "Received request for odsCode",
            ods_code=ods_code,
            dos_message_category="REQUEST",
        )
        """
        Lambda logic
        """
    except ValidationError as exception:
        dos_logger.warning(
            "Validation error occurred",
            validation_errors=exception.errors(),
        )
        """
        Error handling logic
        """
        return create_response(400, exception)
    except Exception:
        dos_logger.exception("Internal server error occurred")
        """
        Exception handling logic
        """
        return create_response(500, {})
    else:
        duration_ms = int((time.time() - start) * 1000)
        response_size = len(fhir_resource.model_dump_json().encode("utf-8"))
        dos_logger.info(
            "Successfully processed",
            opt_ftrs_response_time=f"{duration_ms}ms",
            opt_ftrs_response_size=response_size,
            dos_message_category="METRICS",
        )
        return create_response(200, fhir_resource)

@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
```

## API Reference

### Initialization

#### `DosLogger.get(service: str = "dos") -> DosLogger`

Returns a singleton instance of DosLogger for the given service name.

```python
dos_logger = DosLogger.get(service="dos-search")
```

#### `init(event: Dict[str, Any]) -> None`

Initializes the logger by extracting APIM headers and request context from the event. Should be called at the start of Lambda execution.

```python
dos_logger.init(app.current_event)
```

### Logging Methods

#### `debug(message: str, **detail: object) -> None`

Log a debug-level message with optional structured fields.

#### `info(message: str, **detail: object) -> None`

Log an info-level message with optional structured fields.

#### `warning(message: str, **detail: object) -> None`

Log a warning-level message with optional structured fields.

#### `error(message: str, **detail: object) -> None`

Log an error-level message with optional structured fields.

#### `exception(message: str, **detail: object) -> None`

Log an exception-level message with optional structured fields (includes trace of call stack).

### Powertools Wrapper Methods

#### `append_keys(extra: Dict[str, Any]) -> None`

Append additional structured fields to all subsequent logs. This is a thin wrapper over the [PowerTools Logger `append_keys` method](https://docs.aws.amazon.com/powertools/python/latest/core/logger/#appending-additional-keys).

```python
dos_logger.append_keys({"user_id": "12345", "request_id": "abc-123"})
```

#### `get_keys() -> Dict[str, Any]`

Retrieve all currently appended keys. This is a thin wrapper over the [PowerTools Logger `get_current_keys` method](https://docs.aws.amazon.com/powertools/python/latest/core/logger/#accessing-currently-configured-keys).

```python
current_keys = dos_logger.get_keys()
```

#### `set_level(level: Literal[10, 20, 30, 40, 50]) -> None`

Set the logging level (10=DEBUG, 20=INFO, 30=WARNING, 40=ERROR, 50=CRITICAL). This is a thin wrapper over the [PowerTools Logger `setLevel` method](https://docs.aws.amazon.com/powertools/python/latest/core/logger/#log-levelss).
The Python standard logging library provides an enumerated set for the numerical values of the log_levels, if that is preferred syntactically. These can be referenced via `logging.<LEVEL>` once the `logging` library is imported (e.g. `logging.DEBUG # Resolves to 10`)

```python
dos_logger.set_level(10)  # Set to DEBUG
```

#### `clear_state() -> None`

Clear all appended keys. Usually not needed as `clear_state=True` in the Lambda handler decorator handles this. This is a thin wrapper over the [PowerTools Logger `clear_state` method](https://docs.aws.amazon.com/powertools/python/latest/core/logger/#clear_state-method).

```python
dos_logger.clear_state()
```
