import json
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from utilities.common.context import Context
from utilities.common.resource_name import get_resource_name
from utilities.infra.sqs_util import (
    SQS_CLIENT,
    get_queue_attributes,
    get_queue_url,
    send_message_to_sqs,
    set_visibility_timeout,
)

# Queue suffix mapping for retry/DLQ tests
QUEUE_SUFFIX_MAP = {
    "transform": "transform-queue",
    "load": "load-queue",
}

DLQ_SUFFIX_MAP = {
    "transform": "transform-dlq",
    "load": "load-dlq",
}

LAMBDA_NAME_MAP = {
    "transform": "transformer-lambda",
    "load": "consumer-lambda",
}

# Test Configuration Constants
DEFAULT_QUEUE_VISIBILITY_TIMEOUT_SECONDS = 2


def setup_queue_config(context: Context, queue_type: str, _lambda_wrapper):
    """Set up queue configuration for queue type."""
    if not hasattr(context, "queue_configs"):
        context.queue_configs = {}

    queue_suffix = QUEUE_SUFFIX_MAP[queue_type]
    dlq_suffix = DLQ_SUFFIX_MAP[queue_type]

    queue_url = get_queue_url(
        context.project, context.workspace, context.env, "etl-ods", queue_suffix
    )
    dlq_url = get_queue_url(
        context.project, context.workspace, context.env, "etl-ods", dlq_suffix
    )

    # Store and set visibility timeout
    attrs = get_queue_attributes(queue_url)
    original_timeout = int(attrs["VisibilityTimeout"])
    set_visibility_timeout(queue_url, DEFAULT_QUEUE_VISIBILITY_TIMEOUT_SECONDS)

    lambda_name = get_resource_name(
        context.project,
        context.workspace,
        context.env,
        "etl-ods",
        LAMBDA_NAME_MAP[queue_type],
    )

    context.queue_configs[queue_type] = {
        "queue_url": queue_url,
        "dlq_url": dlq_url,
        "original_timeout": original_timeout,
        "lambda_name": lambda_name,
        "lambda_wrapper": _lambda_wrapper,
    }


def create_test_message(
    context: Context, queue_type: str, message_type: str, **kwargs
) -> None:
    """Unified function to create test messages for different scenarios."""
    context.current_queue_type = queue_type
    correlation_id = str(uuid.uuid4())
    context.message_correlation_id = correlation_id

    if hasattr(context, "test_correlation_id"):
        delattr(context, "test_correlation_id")

    request_id = kwargs.get("request_id", "test-request-id")

    # Malformed JSON - special case with raw string
    if message_type == "malformed_json":
        context.test_message_raw = (
            f'{{"correlation_id": "{correlation_id}", '
            f'"request_id": "{request_id}", '
            f'"organisation": {{"resourceType": "Organization", "malformed'
        )
        context.message_correlation_id = correlation_id
        return

    # Build messages based on queue type and message type
    if queue_type == "transform":
        context.test_message = _create_transform_message(
            correlation_id, request_id, message_type, kwargs
        )
    else:  # load queue
        context.test_message = _create_load_message(
            correlation_id, request_id, message_type, kwargs
        )


def _create_transform_message(
    correlation_id: str, request_id: str, message_type: str, kwargs: Dict[str, Any]
) -> Dict:
    """Create transform queue message based on message type."""
    base_message = {"correlation_id": correlation_id, "request_id": request_id}

    if message_type == "404":
        base_message["organisation"] = {
            "resourceType": "Organization",
            "identifier": [
                {
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": "NONEXIST",
                }
            ],
            "name": "Non-existent Organisation",
        }
    elif message_type == "400":
        base_message["organisation"] = {
            "OrgId": "ABC123",
            "invalid_field": "causes validation error",
        }
    elif message_type == "missing_fields":
        base_message["some_other_field"] = "value"
    elif message_type == "invalid_structure":
        base_message["organisation"] = {
            "resourceType": "Organization",
            "identifier": [
                {
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": "TEST123",
                }
            ],
            "name": None,
            "active": "not-a-boolean",
        }
    elif message_type == "invalid_ods_code":
        base_message["organisation"] = {
            "resourceType": "Organization",
            "identifier": [
                {
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": "INVALIDODSCODE",
                }
            ],
            "name": "Organisation with Invalid ODS Code",
        }
    elif message_type == "missing_identifier":
        base_message["organisation"] = {
            "resourceType": "Organization",
            "name": "Organisation Without Identifier",
        }
    else:  # valid
        base_message["organisation"] = kwargs.get(
            "message",
            {
                "resourceType": "Organization",
                "identifier": [
                    {
                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                        "value": "ABC123",
                    }
                ],
                "name": "Test Organisation",
            },
        ).get(
            "organisation",
            {
                "resourceType": "Organization",
                "identifier": [
                    {
                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                        "value": "ABC123",
                    }
                ],
                "name": "Test Organisation",
            },
        )

    return base_message


def _create_load_message(
    correlation_id: str, request_id: str, message_type: str, kwargs: Dict[str, Any]
) -> Dict:
    """Create load queue message based on message type."""
    base_message = {"correlation_id": correlation_id, "request_id": request_id}

    if message_type == "404":
        base_message.update(
            {
                "path": "00000000-0000-0000-0000-00000000000a",
                "body": {
                    "resourceType": "Organization",
                    "id": "00000000-0000-0000-0000-00000000000a",
                    "identifier": [{"value": "ABC123"}],
                },
            }
        )
    elif message_type == "422":
        base_message["organisation"] = {
            "resourceType": "Organization",
            "identifier": [
                {
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": "HTTP422",
                }
            ],
            "name": "HTTP Error Organisation",
        }
    elif message_type == "missing_fields":
        base_message["path"] = "00000000-0000-0000-0000-00000000000c"
    elif message_type == "invalid_structure":
        base_message.update(
            {
                "path": "00000000-0000-0000-0000-00000000000d",
                "body": {
                    "resourceType": "NotAnOrganization",
                    "invalid_structure": True,
                },
            }
        )
    else:  # valid
        path = kwargs.get("path", "00000000-0000-0000-0000-0000000000aa")
        base_message.update(
            {
                "path": path,
                "body": {
                    "resourceType": "Organization",
                    "id": path,
                    "identifier": [
                        {
                            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                            "value": "ABC123",
                        }
                    ],
                    "name": "Test Organisation",
                },
            }
        )

    return base_message


def process_message_in_queue(context: Context, queue_type: str):
    """Process a message in specified queue type."""
    context.current_queue_type = queue_type
    config = context.queue_configs[queue_type]

    if hasattr(context, "test_message_raw"):
        # Send malformed JSON directly
        response = SQS_CLIENT.send_message(
            QueueUrl=config["queue_url"], MessageBody=context.test_message_raw
        )
    else:
        response = send_message_to_sqs(config["queue_url"], context.test_message)

    context.message_id = response["MessageId"]
    time.sleep(30)  # MESSAGE_PROCESSING_DELAY


def invoke_lambda_generic(
    context: Context,
    project: str,
    workspace: str,
    env: str,
    aws_lambda_client,
    date_param: str = None,
) -> Context:
    """Generic lambda invocation for ETL ODS pipeline."""

    lambda_name = f"{project}-{workspace}-{env}-ods-extract-lambda"

    event = {}
    if date_param:
        event = {"extraction_date": date_param}

    response = aws_lambda_client.invoke_lambda(lambda_name, event)

    context.lambda_name = lambda_name

    # Parse response
    if isinstance(response.get("Payload"), str):
        response["Payload"] = json.loads(response["Payload"])

    context.lambda_response = response
    return context


def create_problem_message(
    context: Context,
    queue_type: str,
    problem_type: str = None,
    status_code: int = None,
    error_condition: str = None,
) -> None:
    """Create a message with specified problem type or error condition."""
    # Map consumer to load queue type
    actual_queue_type = "load" if queue_type == "consumer" else queue_type
    context.current_queue_type = actual_queue_type

    # Determine message type from various parameter formats
    message_type = None
    if status_code:
        message_type = str(status_code)
    elif problem_type:
        problem_map = {
            "malformed JSON": "malformed_json",
            "missing required fields": "missing_fields",
            "invalid structure": "invalid_structure",
            "invalid FHIR structure": "invalid_structure",
            "invalid ODS code format": "invalid_ods_code",
            "organisation missing identifier": "missing_identifier",
        }
        message_type = problem_map.get(problem_type, problem_type.replace(" ", "_"))
    elif error_condition:
        if "fail with" in error_condition:
            parts = error_condition.split()
            if len(parts) >= 3 and parts[-1].isdigit():
                message_type = parts[-1]
            else:
                message_type = error_condition.replace("fail with ", "").replace(
                    " ", "_"
                )
        else:
            message_type = error_condition.replace(" ", "_")

    if not message_type:
        raise ValueError("Could not determine message type from parameters")

    create_test_message(context, actual_queue_type, message_type)


def step_invoke_valid_date(
    context: Context,
    project: str,
    workspace: str,
    env: str,
    aws_lambda_client,
) -> Context:
    """Invoke lambda with valid extraction date and track correlation_id."""
    context.test_correlation_id = str(uuid.uuid4())

    context = invoke_lambda_generic(
        context,
        project,
        workspace,
        env,
        aws_lambda_client,
        date_param=context.extraction_date,
    )
    context.lambda_invocation_time = int(datetime.now(timezone.utc).timestamp())
    return context


def verify_message_in_queue_by_id(
    context: Context,
    queue_type: str,
    queue_or_dlq: str,
    have_or_not: str,
) -> None:
    """Check if test message is present/absent in queue by correlation_id."""
    assert hasattr(context, "message_correlation_id"), (
        "No message_correlation_id found in context. Message must be created before checking queue."
    )

    config = context.queue_configs[queue_type]
    queue_url = (
        config["dlq_url"]
        if queue_or_dlq.lower() in ["dlq", "dead-letter-queue"]
        else config["queue_url"]
    )
    queue_name = (
        f"{queue_type} DLQ"
        if queue_or_dlq.lower() in ["dlq", "dead-letter-queue"]
        else f"{queue_type} queue"
    )

    correlation_id = context.message_correlation_id
    should_be_present = "not" not in have_or_not.lower()

    # Poll queue multiple times to handle timing issues
    message_found = False
    max_attempts = 5

    for attempt in range(max_attempts):
        response = SQS_CLIENT.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=5,
            VisibilityTimeout=0,
        )
        messages = response.get("Messages", [])

        # Check if any message contains our correlation_id
        for msg in messages:
            try:
                body = json.loads(msg.get("Body", "{}"))
                if body.get("correlation_id") == correlation_id:
                    message_found = True
                    break
            except json.JSONDecodeError:
                # Check if correlation_id appears in raw message body
                if correlation_id in msg.get("Body", ""):
                    message_found = True
                    break

        if message_found:
            break

        if attempt < max_attempts - 1:  # Don't sleep on last attempt
            time.sleep(3)

    if should_be_present:
        assert message_found, (
            f"Expected message {correlation_id} in {queue_name}, but not found after {max_attempts} attempts"
        )
    else:
        assert not message_found, (
            f"Expected message {correlation_id} removed from {queue_name}, but still found"
        )
