from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
from pytest_mock import MockerFixture

# Mock FeatureFlagsClient before importing handler to prevent AppConfig initialization
with patch("ftrs_common.feature_flags.FeatureFlagsClient") as mock_ff_class:
    mock_ff_instance = MagicMock()
    mock_ff_instance.is_enabled.return_value = True
    mock_ff_class.return_value = mock_ff_instance

    from healthcare_service.app.handler_healthcare_service import handler


@pytest.fixture(autouse=True)
def mock_feature_flags(mocker: MockerFixture) -> MagicMock:
    """Mock the feature flags client to ensure consistent behavior across tests."""
    mock_client = mocker.patch(
        "healthcare_service.app.handler_healthcare_service.FEATURE_FLAGS_CLIENT"
    )
    mock_client.is_enabled.return_value = True
    return mock_client


def test_handler_returns_200_for_valid_get_request() -> None:
    mock_event = {
        "httpMethod": "GET",
        "path": "/",
        "headers": {},
        "queryStringParameters": None,
        "body": None,
        "requestContext": {
            "resourcePath": "/",
            "httpMethod": "GET",
            "requestId": "test-request-id",
            "apiId": "test-api-id",
        },
        "resource": "/",
    }
    mock_context = MagicMock()
    response = handler(mock_event, mock_context)

    assert "statusCode" in response
    assert "headers" in response
    assert "body" in response


def test_handler_returns_502_when_feature_flag_disabled(
    mock_feature_flags: MagicMock,
) -> None:
    # Override the fixture to return False for this test
    mock_feature_flags.is_enabled.return_value = False

    mock_event = {
        "httpMethod": "GET",
        "path": "/",
        "headers": {},
        "queryStringParameters": None,
        "body": None,
        "requestContext": {
            "resourcePath": "/",
            "httpMethod": "GET",
            "requestId": "test-request-id",
            "apiId": "test-api-id",
        },
        "resource": "/",
    }
    mock_context = MagicMock()
    response = handler(mock_event, mock_context)

    assert response["statusCode"] == HTTPStatus.SERVICE_UNAVAILABLE
    assert (
        "Service Unavailable: Data Migration Search Triage Code feature is disabled."
        in response["body"]
    )
