import logging
from unittest.mock import MagicMock, patch

import pytest
import requests

from pipeline.processor import extract, lambda_handler

STATUS_SUCCESSFUL = 200
STATUS_UNEXPECTED_ERROR = 500


@pytest.fixture
def mock_responses() -> MagicMock:
    """Fixture to create mock responses for both API calls"""
    first_response = MagicMock()
    first_response.text = (
        '{"Organisations": [{"OrgLink": "https://example.com/organisations/ABC123"}]}'
    )
    first_response.status_code = 200
    first_response.json.return_value = {
        "Organisations": [{"OrgLink": "https://example.com/organisations/ABC123"}]
    }

    second_response = MagicMock()
    second_response.text = '{"name": "Test Organization", "id": "ABC123"}'

    return first_response, second_response


def test_extract_successful_request(mock_responses: MagicMock, caplog: any) -> None:
    """Test successful data extraction"""

    first_response, second_response = mock_responses
    GET_COUNT = 2

    with patch("requests.get") as mock_get:
        mock_get.side_effect = [first_response, second_response]

        caplog.set_level(logging.INFO)

        extract(date="2023-01-01")

        assert mock_get.call_count == GET_COUNT
        first_call_args = mock_get.call_args_list[0]
        assert (
            first_call_args[0][0]
            == "https://directory.spineservices.nhs.uk/ORD/2-0-0/sync?"
        )
        assert first_call_args[1]["params"] == {"LastChangeDate": "2023-01-01"}
        second_call_args = mock_get.call_args_list[1]
        assert (
            second_call_args[0][0]
            == "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/ABC123?"
        )
        assert "https://directory.spineservices.nhs.uk/ORD/2-0-0/sync?" in caplog.text
        assert f"Extracted data: {second_response.text}" in caplog.text


def test_extract_request_exception(caplog: any) -> None:
    """Test handling of request exception"""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        caplog.set_level(logging.ERROR)

        extract(date="2025-04-23")

        mock_get.assert_called_once()
        assert "Error fetching data" in caplog.text


def test_lambda_handler_success() -> None:
    """Test lambda_handler with valid date parameter"""
    with patch("pipeline.processor.extract") as mock_extract:
        event = {"date": "2025-02-02"}
        context = {}
        result = lambda_handler(event, context)

        mock_extract.assert_called_once_with(date="2025-02-02")
        assert result is None


def test_lambda_handler_exception() -> None:
    """Test lambda_handler when extract raises an exception"""
    with patch("pipeline.processor.extract") as mock_extract:
        with patch("logging.info") as mock_logging:
            mock_extract.side_effect = Exception("Test error")
            event = {"date": "2025-02-02"}
            context = {}
            result = lambda_handler(event, context)

            mock_extract.assert_called_once_with(date="2025-02-02")
            assert "Unexpected error" in mock_logging.call_args[0][0]
            assert result["statusCode"] == STATUS_UNEXPECTED_ERROR
            assert "Unexpected error: Test error" in result["body"]
