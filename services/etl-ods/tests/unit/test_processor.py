import logging
import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from pipeline.processor import lambda_handler, processor

STATUS_SUCCESSFUL = 200
STATUS_UNEXPECTED_ERROR = 500


@pytest.fixture
def mock_responses() -> MagicMock:
    first_response = MagicMock()
    first_response.text = (
        '{"Organisations": [{"OrgLink": "https://nhs.com/organisations/ABC123"}]}'
    )
    first_response.status_code = 200
    first_response.json.return_value = {
        "Organisations": [
            {"OrgLink": "https://nhs.com/organisations/ABC123"},
        ]
    }

    second_response = MagicMock()
    second_response.status_code = 200
    second_response.json.return_value = {
        "Organisation": {
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
    }

    thrid_response = MagicMock()
    second_response.status_code = 200
    thrid_response.json.return_value = {
        "Roles": [
            {
                "primaryRole": "true",
                "displayName": "NHS TRUST",
            }
        ]
    }

    forth_response = MagicMock()
    forth_response.json.return_value = {
        "id": "uuid",
    }
    return first_response, second_response, thrid_response, forth_response


@patch("pipeline.processor.requests.get")
@patch.dict(
    "os.environ",
    {
        "ORGANISATION_API_URL": "https://localhost:8001/",
        "ENVIRONMENT": os.environ["ENVIRONMENT"],
        "WORKSPACE": os.environ["WORKSPACE"],
    },
)
def test_processor_processing_organisations_continues_if_failure(
    mock_get: MagicMock, caplog: any
) -> None:
    """Test successful data extraction"""
    first_response = MagicMock()
    first_response.status_code = 200
    first_response.json.return_value = {
        "Organisations": [
            {"OrgLink": "https://example.com/organisations/ABC123"},
            {"OrgLink": "https://example.com/organisations/EFG456"},
        ]
    }

    second_response = MagicMock()
    second_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "404 Client Error: Not Found for url"
    )

    third_response = MagicMock()
    third_response.status_code = 200
    third_response.json.return_value = {
        "Organisation": {
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
    }

    fourth_response = MagicMock()
    fourth_response.status_code = 200
    fourth_response.json.return_value = {
        "Roles": [
            {
                "primaryRole": "true",
                "displayName": "NHS TRUST",
            }
        ]
    }

    fifth_response = MagicMock()
    fifth_response.status_code = 200
    fifth_response.json.return_value = {
        "id": "uuid",
    }

    mock_get.side_effect = [
        first_response,
        second_response,
        third_response,
        fourth_response,
        fifth_response,
    ]

    GET_COUNT = 5
    caplog.set_level(logging.INFO)
    processor(date="2023-01-01")

    first_call_args = mock_get.call_args_list[0]
    second_call_args = mock_get.call_args_list[1]
    third_call_args = mock_get.call_args_list[2]
    forth_call_args = mock_get.call_args_list[3]
    fifth_call_args = mock_get.call_args_list[4]

    assert mock_get.call_count == GET_COUNT

    assert (
        first_call_args[0][0]
        == "https://directory.spineservices.nhs.uk/ORD/2-0-0/sync?"
    )
    assert first_call_args[1]["params"] == {"LastChangeDate": "2023-01-01"}
    assert (
        second_call_args[0][0]
        == "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/ABC123"
    )
    assert (
        third_call_args[0][0]
        == "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/EFG456"
    )
    assert (
        forth_call_args[0][0]
        == "https://directory.spineservices.nhs.uk/ORD/2-0-0/roles/RO157"
    )
    assert fifth_call_args[0][0] == "https://localhost:8001/ods_code/EFG456"

    assert (
        "Error processing organisation with ods_code ABC123: 404 Client Error: Not Found for url"
        in caplog.text
    )
    assert (
        'Transformed request_body: {"path": "uuid", "body": {"active": true, "name": "Test Organisation", "telecom": "00000000000", "type": "NHS TRUST", "modified_by": "ODS_ETL_PIPELINE"}}'
        in caplog.text
    )


@patch("pipeline.processor.requests.get")
@patch.dict(
    "os.environ",
    {
        "ORGANISATION_API_URL": "https://localhost:8001/",
        "ENVIRONMENT": os.environ["ENVIRONMENT"],
        "WORKSPACE": os.environ["WORKSPACE"],
    },
)
def test_processor_processing_organisations_successful(
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
    caplog.set_level(logging.INFO)
    processor(date="2023-01-01")

    first_call_args = mock_get.call_args_list[0]
    second_call_args = mock_get.call_args_list[1]
    third_call_args = mock_get.call_args_list[2]
    forth_call_args = mock_get.call_args_list[3]

    assert mock_get.call_count == GET_COUNT

    assert (
        first_call_args[0][0]
        == "https://directory.spineservices.nhs.uk/ORD/2-0-0/sync?"
    )
    assert first_call_args[1]["params"] == {"LastChangeDate": "2023-01-01"}
    assert (
        second_call_args[0][0]
        == "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/ABC123"
    )
    assert (
        third_call_args[0][0]
        == "https://directory.spineservices.nhs.uk/ORD/2-0-0/roles/RO157"
    )
    assert forth_call_args[0][0] == "https://localhost:8001/ods_code/ABC123"

    assert (
        'Transformed request_body: {"path": "uuid", "body": {"active": true, "name": "Test Organisation", "telecom": "00000000000", "type": "NHS TRUST", "modified_by": "ODS_ETL_PIPELINE"}}'
        in caplog.text
    )


@patch("pipeline.processor.requests.get")
def test_processor_no_outdated_organisations(mock_get: MagicMock, caplog: any) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"Organisations": []}
    mock_get.return_value = mock_response

    caplog.set_level(logging.INFO)

    processor(date="2025-04-23")

    mock_get.assert_called_once()
    assert "No organisations found for the given date." in caplog.text


@patch("pipeline.processor.requests.get")
def test_processor_missing_org_link(mock_get: MagicMock, caplog: any) -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"Organisations": [{"NotOrgLink": "test"}]}
    mock_get.return_value = mock_response

    caplog.set_level(logging.INFO)

    processor(date="2025-04-23")

    mock_get.assert_called_once()
    assert "Organisation link is missing in the response." in caplog.text


@patch("pipeline.processor.requests.get")
def test_processor_request_exception(mock_get: MagicMock, caplog: any) -> None:
    mock_get.side_effect = requests.exceptions.RequestException("Connection error")

    caplog.set_level(logging.WARNING)

    with pytest.raises(requests.exceptions.RequestException, match="Connection error"):
        processor(date="2025-04-23")

    mock_get.assert_called_once()
    assert "Error fetching data" in caplog.text


@patch("pipeline.processor.requests.get")
def test_processor_exception(mock_get: MagicMock, caplog: any) -> None:
    mock_get.side_effect = Exception("Unknown error")

    caplog.set_level(logging.WARNING)

    with pytest.raises(Exception):
        processor(date="2025-04-23")

    mock_get.assert_called_once()
    assert "Unexpected error" in caplog.text


@patch("pipeline.processor.process_organisation")
@patch("pipeline.processor.requests.get")
def test_processor_calls_organisation_crud_api(
    mock_get: MagicMock, mock_process_organisation: MagicMock, mock_responses: MagicMock
) -> None:
    with patch.dict(
        "os.environ",
        {"ENVIRONMENT": "dev"},
    ):
        first_response, second_response, _, _ = mock_responses
        mock_get.side_effect = [first_response, second_response]
        mock_process_organisation.return_value = None

        processor(date="2023-01-01")

        mock_process_organisation.assert_called_once_with("ABC123")


@patch("pipeline.processor.processor")
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


@patch("pipeline.processor.processor")
def test_lambda_handler_exception(mock_processor: MagicMock) -> None:
    mock_processor.side_effect = Exception("Test error")
    event = {"date": "2025-02-02"}

    result = lambda_handler(event, {})

    mock_processor.assert_called_once_with(date="2025-02-02")
    # assert "Unexpected error" in mock_logging.call_args[0][0]
    assert str(result["statusCode"]) == "500"
    assert "Unexpected error: Test error" in result["body"]
