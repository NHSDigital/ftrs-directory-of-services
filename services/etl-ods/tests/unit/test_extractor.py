from datetime import datetime, timedelta
from http import HTTPStatus
from unittest.mock import MagicMock

from pytest_mock import MockerFixture

from pipeline.extractor import (
    _send_organisations_to_queue,
    _validate_date,
    extractor_lambda_handler,
    processor,
)


def test_processor_success(mocker: MockerFixture) -> None:
    """Test successful extraction and queuing of organizations."""
    mock_organisations = [
        {
            "id": "org1",
            "identifier": [
                {
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": "ABC123",
                }
            ],
        },
        {
            "id": "org2",
            "identifier": [
                {
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": "DEF456",
                }
            ],
        },
    ]

    mock_fetch = mocker.patch(
        "pipeline.extractor.fetch_outdated_organisations",
        return_value=mock_organisations,
    )
    mock_send = mocker.patch("pipeline.extractor._send_organisations_to_queue")

    date = "2025-01-15"
    processor(date)

    mock_fetch.assert_called_once_with(date)
    mock_send.assert_called_once_with(mock_organisations)


def test_processor_no_organisations(mocker: MockerFixture) -> None:
    """Test processor with no organizations returned."""
    mock_fetch = mocker.patch(
        "pipeline.extractor.fetch_outdated_organisations", return_value=[]
    )
    mock_send = mocker.patch("pipeline.extractor._send_organisations_to_queue")

    date = "2025-01-15"
    processor(date)

    mock_fetch.assert_called_once_with(date)
    mock_send.assert_not_called()


def test_send_organisations_to_queue(mocker: MockerFixture) -> None:
    """Test sending organizations to transform queue."""
    mock_organisations = [
        {"id": "org1", "name": "Test Org 1"},
        {"id": "org2", "name": "Test Org 2"},
    ]

    mocker.patch("pipeline.extractor.get_correlation_id", return_value="corr-123")
    mocker.patch("pipeline.extractor.get_request_id", return_value="req-456")
    mock_send_messages = mocker.patch("pipeline.extractor.send_messages_to_queue")

    _send_organisations_to_queue(mock_organisations)

    expected_messages = [
        {
            "organisation": {"id": "org1", "name": "Test Org 1"},
            "correlation_id": "corr-123",
            "request_id": "req-456",
        },
        {
            "organisation": {"id": "org2", "name": "Test Org 2"},
            "correlation_id": "corr-123",
            "request_id": "req-456",
        },
    ]

    mock_send_messages.assert_called_once_with(
        expected_messages, queue_suffix="transform-queue"
    )


def test_extractor_lambda_handler_success(mocker: MockerFixture) -> None:
    """Test successful lambda handler execution."""
    # Use a recent date to avoid validation failure
    recent_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    mock_processor = mocker.patch("pipeline.extractor.processor")

    event = {"date": recent_date}
    context = MagicMock()
    context.aws_request_id = "test-request-id"

    result = extractor_lambda_handler(event, context)

    assert result["statusCode"] == HTTPStatus.OK
    assert (
        f"Successfully processed organizations for {recent_date}" in result["message"]
    )
    mock_processor.assert_called_once_with(date=recent_date)


def test_extractor_lambda_handler_missing_date() -> None:
    """Test lambda handler fails with missing date parameter."""
    event = {}
    context = MagicMock()

    result = extractor_lambda_handler(event, context)

    assert result["statusCode"] == HTTPStatus.BAD_REQUEST
    error_body = result["body"]
    assert "Date parameter is required" in error_body


def test_extractor_lambda_handler_invalid_date_format() -> None:
    """Test lambda handler fails with invalid date format."""
    event = {"date": "15-01-2025"}
    context = MagicMock()

    result = extractor_lambda_handler(event, context)

    assert result["statusCode"] == HTTPStatus.BAD_REQUEST
    error_body = result["body"]
    assert "Date must be in YYYY-MM-DD format" in error_body


def test_extractor_lambda_handler_date_too_old() -> None:
    """Test lambda handler fails with date older than 185 days."""
    old_date = (datetime.now() - timedelta(days=186)).strftime("%Y-%m-%d")
    event = {"date": old_date}
    context = MagicMock()

    result = extractor_lambda_handler(event, context)

    assert result["statusCode"] == HTTPStatus.BAD_REQUEST
    error_body = result["body"]
    assert "Date must not be more than 185 days in the past" in error_body


def test_extractor_lambda_handler_exception(mocker: MockerFixture) -> None:
    """Test lambda handler handles processor exceptions."""
    # Use a recent date to avoid validation failure
    recent_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    mocker.patch("pipeline.extractor.processor", side_effect=Exception("Test error"))

    event = {"date": recent_date}
    context = MagicMock()

    result = extractor_lambda_handler(event, context)

    assert result["statusCode"] == HTTPStatus.INTERNAL_SERVER_ERROR
    error_body = result["body"]
    assert "Unexpected error: Test error" in error_body


def test_validate_date_valid() -> None:
    """Test date validation with valid date."""
    today = datetime.now().strftime("%Y-%m-%d")
    is_valid, error = _validate_date(today)

    assert is_valid is True
    assert error is None


def test_validate_date_invalid_format() -> None:
    """Test date validation with invalid format."""
    is_valid, error = _validate_date("15-01-2025")

    assert is_valid is False
    assert "Date must be in YYYY-MM-DD format" in error


def test_validate_date_too_old() -> None:
    """Test date validation with date too old."""
    old_date = (datetime.now() - timedelta(days=186)).strftime("%Y-%m-%d")
    is_valid, error = _validate_date(old_date)

    assert is_valid is False
    assert "Date must not be more than 185 days in the past" in error


def test_validate_date_exactly_185_days() -> None:
    """Test date validation with date exactly 185 days old (should be valid)."""
    edge_date = (datetime.now() - timedelta(days=185)).strftime("%Y-%m-%d")
    is_valid, error = _validate_date(edge_date)

    assert is_valid is True
    assert error is None
