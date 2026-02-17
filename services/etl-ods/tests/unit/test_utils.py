"""Additional test utilities for ETL ODS unit tests."""

import json
from typing import Any, Dict, List
from unittest.mock import MagicMock

from pytest_mock import MockerFixture


def create_mock_sqs_record(
    message_id: str = "test-message-123",
    receive_count: str = "1",
    body_data: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Create a mock SQS record with standard structure.

    Args:
        message_id: The message ID for the record
        receive_count: The approximate receive count
        body_data: The data to include in the message body

    Returns:
        Dict representing an SQS record
    """
    if body_data is None:
        body_data = {
            "path": "test-path",
            "body": {"test": "data"},
            "correlation_id": "test-correlation-123",
            "request_id": "test-request-456",
        }

    return {
        "messageId": message_id,
        "attributes": {"ApproximateReceiveCount": receive_count},
        "body": json.dumps(body_data),
    }


def create_mock_lambda_event(records: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a mock Lambda event with SQS records.

    Args:
        records: List of SQS records to include

    Returns:
        Dict representing a Lambda event
    """
    if records is None:
        records = [create_mock_sqs_record()]

    return {"Records": records}


def create_mock_organisation(
    ods_code: str = "ABC123", name: str = "Test Organisation"
) -> Dict[str, Any]:
    """Create a mock organisation FHIR resource.

    Args:
        ods_code: The ODS code for the organisation
        name: The name of the organisation

    Returns:
        Dict representing a FHIR Organisation resource
    """
    return {
        "resourceType": "Organization",
        "id": ods_code,
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": ods_code,
            }
        ],
        "name": name,
    }


def setup_standard_mocks(mocker: MockerFixture) -> Dict[str, MagicMock]:
    """Setup standard mocks used across multiple test modules.

    Args:
        mocker: pytest-mock MockerFixture

    Returns:
        Dict of mock objects keyed by their purpose
    """
    mocks = {
        "logger": mocker.MagicMock(),
        "correlation_id": mocker.patch(
            "ftrs_common.request_context.get_correlation_id"
        ),
        "request_id": mocker.patch("ftrs_common.request_context.get_request_id"),
        "jwt_authenticator": mocker.patch("common.auth.get_jwt_authenticator"),
        "boto3_client": mocker.patch("boto3.client"),
    }

    # Configure common return values
    mocks["correlation_id"].return_value = "test-correlation-123"
    mocks["request_id"].return_value = "test-request-456"

    return mocks
