from unittest.mock import MagicMock, patch

from pipeline.lambda_handler import lambda_handler


@patch("pipeline.lambda_handler.processor")
def test_lambda_handler_success(mock_processor: MagicMock) -> None:
    date = "2025-02-02"
    event = {"date": date}

    response = lambda_handler(event, {})

    mock_processor.assert_called_once_with(date=date)

    assert response is None


def test_lambda_handler_missing_date() -> None:
    response = lambda_handler({}, {})

    assert response == {"statusCode": 400, "body": "Date parameter is required"}


def test_lambda_handler_invalid_date_format() -> None:
    invalid_event = {"date": "14-05-2025"}

    response = lambda_handler(invalid_event, {})

    assert response == {"statusCode": 400, "body": "Date must be in YYYY-MM-DD format"}


@patch("pipeline.lambda_handler.processor")
def test_lambda_handler_exception(mock_processor: MagicMock) -> None:
    mock_processor.side_effect = Exception("Test error")
    event = {"date": "2025-02-02"}

    result = lambda_handler(event, {})

    mock_processor.assert_called_once_with(date="2025-02-02")
    # assert "Unexpected error" in mock_logging.call_args[0][0]
    assert str(result["statusCode"]) == "500"
    assert "Unexpected error: Test error" in result["body"]
