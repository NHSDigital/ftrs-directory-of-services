import logging
from unittest.mock import MagicMock, patch

import pytest
import requests

from pipeline import processor

STATUS_SUCCESSFUL = 200
STATUS_UNEXPECTED_ERROR = 500


@pytest.fixture
def mock_responses() -> MagicMock:
    """Fixture to create mock responses for both API calls"""
    first_response = MagicMock()
    first_response.text = '{"Organisations": [{"OrgLink": "https://nhs.com/organisations/ABC123", {"OrgLink": "https://nhs.com/organisations/EFG456"}}]}'
    first_response.status_code = 200
    first_response.json.return_value = {
        "Organisations": [
            {"OrgLink": "https://nhs.com/organisations/ABC123"},
            {"OrgLink": "https://nhs.com/organisations/EFG456"},
        ]
    }

    second_response = MagicMock()
    second_response = {
        "Name": "Test Organisation",
        "Status": "Active",
        "Contacts": {"Contact": [{"type": "tel", "value": "00000000000"}]},
        "Roles": {
            "Role": [
                {
                    "id": "RO157",
                    "primaryRole": True,
                },
                {
                    "id": "RO7",
                },
            ]
        },
    }

    thrid_response = MagicMock()
    thrid_response.text = {
        "Roles": [
            {
                "displayName": "NHS TRUST",
            }
        ]
    }

    forth_response = MagicMock()
    forth_response.text = {
        "id": "12345",
    }
    return first_response, second_response, thrid_response, forth_response


@patch("pipeline.processor.requests.get")
def test_processor_processing_multiple_organisations_successful(
    mock_get: MagicMock, mock_responses: MagicMock, caplog: any
) -> None:
    """Test successful data extraction"""
    first_response, second_response, third_response, fourth_response = mock_responses
    mock_get.side_effect = [
        first_response,
        second_response,
        third_response,
        fourth_response,
    ]
    GET_COUNT = 4

    processor(date="2023-01-01")

    assert mock_get.call_count == GET_COUNT
    first_call_args = mock_get.call_args_list[0]
    second_call_args = mock_get.call_args_list[1]
    third_call_args = mock_get.call_args_list[2]
    forth_call_args = mock_get.call_args_list[3]

    assert (
        first_call_args[0][0]
        == "https://directory.spineservices.nhs.uk/ORD/2-0-0/sync?"
    )
    assert first_call_args[1]["params"] == {"LastChangeDate": "2023-01-01"}
    assert (
        second_call_args[0][0]
        == "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/ABC123?"
    )
    assert (
        third_call_args[0][0]
        == "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/ABC123?"
    )
    assert (
        forth_call_args[0][0]
        == "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/ABC123?"
    )

    assert "https://directory.spineservices.nhs.uk/ORD/2-0-0/sync?" in caplog.text
    assert f"Extracted data: {second_response.text}" in caplog.text


@patch("pipeline.processor.requests.get")
def test_processor_request_exception(mock_get: MagicMock, caplog: any) -> None:
    mock_get.side_effect = requests.exceptions.RequestException("Connection error")

    caplog.set_level(logging.ERROR)

    with pytest.raises(requests.exceptions.RequestException):
        processor(date="2025-04-23")

    mock_get.assert_called_once()
    assert "Error fetching data" in caplog.text


@patch("pipeline.processor.requests.get")
def test_processor_exception(mock_get: MagicMock, caplog: any) -> None:
    mock_get.side_effect = Exception("Unknown error")

    caplog.set_level(logging.WARNING)

    with pytest.raises(requests.exceptions.RequestException):
        processor(date="2025-04-23")

    mock_get.assert_called_once()
    assert "Unexpected error" in caplog.text


@patch("pipeline.processor.process_organisation")
@patch("pipeline.processor.requests.get")
def test_processor_calls_organisation_crud_api(
    mock_get: MagicMock, mock_process_organisation: MagicMock, mock_responses: MagicMock
) -> None:
    first_response, second_response, _, _ = mock_responses
    mock_get.side_effect = [first_response, second_response]
    mock_process_organisation.return_value = None

    processor(date="2023-01-01")

    # Assert that process_organisation was called with the correct ODS code
    mock_process_organisation.assert_called_once_with("ABC123")


@patch("pipeline.processor.requests.get")
def test_process_organisation_success(
    mock_get: MagicMock, mock_responses: MagicMock
) -> None:
    """Test process_organisation with successful API calls."""
    _, second_response, third_response, fourth_response = mock_responses
    mock_get.side_effect = [second_response, third_response, fourth_response]

    result = processor.process_organisation("ABC123")

    # Assert that the organisation data was processed successfully
    assert result is not None
    assert str(mock_get.call_count) == "3"
