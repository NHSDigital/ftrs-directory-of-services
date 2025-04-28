import logging
from unittest.mock import MagicMock, patch

import pytest
import requests

from processor import extract, make_request_with_retry

STATUS_SUCCESSFUL = 200
STATUS_RATE_LIMIT = 429


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
        assert "Error fetching data: Connection error" in caplog.text


def test_successful_request_first_try() -> None:
    with patch("requests.get") as mock_get:
        with patch("time.sleep") as mock_sleep:
            mock_response = MagicMock()
            mock_response.status_code = STATUS_SUCCESSFUL
            mock_response.text = '{"data": "abc"}'
            mock_get.return_value = mock_response
            result = make_request_with_retry("https://example.com")

            mock_get.assert_called_once_with("https://example.com")
            mock_sleep.assert_not_called()
            assert result.status_code == STATUS_SUCCESSFUL
            assert result.text == '{"data": "abc"}'


def test_rate_limit_with_retry_then_success() -> None:
    GET_COUNT = 2
    with patch("requests.get") as mock_get:
        with patch("time.sleep") as mock_sleep:
            with patch("logging.warning") as mock_warning:
                rate_limit_response = MagicMock()
                rate_limit_response.status_code = STATUS_RATE_LIMIT
                success_response = MagicMock()
                success_response.status_code = STATUS_SUCCESSFUL
                success_response.text = '{"data": "success after retry"}'
                mock_get.side_effect = [rate_limit_response, success_response]
                result = make_request_with_retry("https://example.com")

                assert mock_get.call_count == GET_COUNT
                mock_sleep.assert_called_once_with(1)
                mock_warning.assert_called_once()
                assert result.status_code == STATUS_SUCCESSFUL
                assert result.text == '{"data": "success after retry"}'


def test_multiple_rate_limits_with_exponential_backoff_then_success() -> None:
    GET_COUNT = 4
    WARN_COUNT = 3
    with patch("requests.get") as mock_get:
        with patch("logging.warning") as mock_warning:
            rate_limit_response = MagicMock()
            rate_limit_response.status_code = STATUS_RATE_LIMIT
            success_response = MagicMock()
            success_response.status_code = STATUS_SUCCESSFUL
            success_response.text = '{"data": "finally succeeded"}'
            mock_get.side_effect = [
                rate_limit_response,
                rate_limit_response,
                rate_limit_response,
                success_response,
            ]
            result = make_request_with_retry("https://example.com")

            assert mock_get.call_count == GET_COUNT
            assert mock_warning.call_count == WARN_COUNT
            assert result.status_code == STATUS_SUCCESSFUL


def test_max_retries_exceeded() -> None:
    GET_COUNT = 3
    WARN_COUNT = 2
    with patch("requests.get") as mock_get:
        with patch("logging.warning") as mock_warning:
            with patch("logging.exception") as mock_exception:
                rate_limit_response = MagicMock()
                rate_limit_response.status_code = STATUS_RATE_LIMIT

                def side_effect_func() -> None:
                    raise ("Rate Limited")

                rate_limit_response.raise_for_status = MagicMock(
                    side_effect=side_effect_func
                )
                mock_get.return_value = rate_limit_response
                result = make_request_with_retry("https://example.com", max_retries=2)

                assert mock_get.call_count == GET_COUNT
                assert mock_warning.call_count == WARN_COUNT
                mock_exception.assert_called_once()
                assert result is None
