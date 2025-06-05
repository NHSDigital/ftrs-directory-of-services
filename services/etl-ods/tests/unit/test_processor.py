import json
from typing import NamedTuple

import pytest
from pytest_mock import MockerFixture
from requests_mock import (
    Mocker as RequestsMock,
)
from requests_mock.adapter import _Matcher as Matcher

from pipeline.processor import processor, processor_lambda_handler


class MockResponses(NamedTuple):
    ods_sync: Matcher
    ods_abc123: Matcher
    ods_role_ro157: Matcher

    crud_org_abc123: Matcher


@pytest.fixture
def mock_responses(
    requests_mock: RequestsMock,
) -> None:
    # Setup ODS Sync Data Mock
    ods_sync_data = {
        "Organisations": [
            {
                "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/ABC123"
            }
        ]
    }
    ods_sync_mock = requests_mock.get(
        "https://directory.spineservices.nhs.uk/ORD/2-0-0/sync",
        json=ods_sync_data,
    )

    # Setup ODS Organisation Data Mock for ABC123
    ods_data_abc123 = {
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
    ods_abc123_mock = requests_mock.get(
        "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/ABC123",
        json=ods_data_abc123,
    )

    # Setup ODS Role Data Mock for RO157
    ods_role_data = {
        "Roles": [
            {
                "primaryRole": "true",
                "displayName": "NHS TRUST",
            }
        ]
    }
    ods_role_ro157_mock = requests_mock.get(
        "https://directory.spineservices.nhs.uk/ORD/2-0-0/roles/RO157",
        json=ods_role_data,
    )

    # Setup CRUD API Mock for Organisation UUID (ABC123)
    crud_api_data_abc123 = {
        "id": "uuid_abc123",
        "name": "Test Organisation",
    }
    crud_org_abc123_mock = requests_mock.get(
        "http://test-crud-api/organisation/ods_code/ABC123",
        json=crud_api_data_abc123,
    )

    return MockResponses(
        ods_sync=ods_sync_mock,
        ods_abc123=ods_abc123_mock,
        ods_role_ro157=ods_role_ro157_mock,
        crud_org_abc123=crud_org_abc123_mock,
    )


def test_processor_processing_organisations_successful(
    mocker: MockerFixture,
    requests_mock: RequestsMock,
    mock_responses: MockResponses,
) -> None:
    expected_call_count = 4

    date = "2023-01-01"

    load_data_mock = mocker.patch("pipeline.processor.load_data")
    assert processor(date) is None

    assert requests_mock.call_count == expected_call_count

    # Assert ODS Sync Call
    assert mock_responses.ods_sync.called_once
    assert mock_responses.ods_sync.last_request.path == "/ord/2-0-0/sync"
    assert mock_responses.ods_sync.last_request.query == "lastchangedate=2023-01-01"
    assert requests_mock.request_history[0] == mock_responses.ods_sync.last_request

    # Assert ODS Organisation Call for ABC123
    assert mock_responses.ods_abc123.called_once
    assert (
        mock_responses.ods_abc123.last_request.path == "/ord/2-0-0/organisations/abc123"
    )
    assert requests_mock.request_history[1] == mock_responses.ods_abc123.last_request

    # Assert ODS Role Call for RO157
    assert mock_responses.ods_role_ro157.called_once
    assert mock_responses.ods_role_ro157.last_request.path == "/ord/2-0-0/roles/ro157"
    assert (
        requests_mock.request_history[2] == mock_responses.ods_role_ro157.last_request
    )

    # Assert CRUD API Call for Organisation UUID
    assert mock_responses.crud_org_abc123.called_once
    assert (
        mock_responses.crud_org_abc123.last_request.path
        == "/organisation/ods_code/abc123"
    )
    assert (
        requests_mock.request_history[3] == mock_responses.crud_org_abc123.last_request
    )

    # Assert load_data call
    load_data_mock.assert_called_once()
    data_to_load = [json.loads(entry) for entry in load_data_mock.call_args[0][0]]

    assert data_to_load == [
        {
            "path": "uuid_abc123",
            "body": {
                "active": True,
                "name": "Test Organisation",
                "telecom": "00000000000",
                "type": "NHS TRUST",
                "modified_by": "ODS_ETL_PIPELINE",
            },
        }
    ]


def test_processor_continue_on_validation_failure(
    mocker: MockerFixture,
    requests_mock: RequestsMock,
    mock_responses: MockResponses,
    caplog: pytest.LogCaptureFixture,
) -> None:
    ods_sync_mock = requests_mock.get(
        "https://directory.spineservices.nhs.uk/ORD/2-0-0/sync",
        json={
            "Organisations": [
                {
                    "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/ABC123"
                },
                {
                    "OrgLink": "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/EFG456"
                },
            ]
        },
    )

    crud_api_abc123_mock = requests_mock.get(
        "http://test-crud-api/organisation/ods_code/ABC123",
        status_code=422,  # Simulate Unprocessable Entity error
    )

    ods_efg456_mock = requests_mock.get(
        "https://directory.spineservices.nhs.uk/ORD/2-0-0/organisations/EFG456",
        json={
            "Organisation": {
                "Name": "Test Organisation EFG ODS",
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
        },
    )

    crud_efg456_mock = requests_mock.get(
        "http://test-crud-api/organisation/ods_code/EFG456",
        json={"id": "uuid_efg456", "name": "Test Organisation EFG"},
    )
    expected_call_count = 7

    date = "2023-01-01"

    load_data_mock = mocker.patch("pipeline.processor.load_data")
    assert processor(date) is None

    assert requests_mock.call_count == expected_call_count
    # Assert ODS Sync Call
    assert ods_sync_mock.called_once
    assert ods_sync_mock.last_request.path == "/ord/2-0-0/sync"
    assert ods_sync_mock.last_request.query == "lastchangedate=2023-01-01"
    assert requests_mock.request_history[0] == ods_sync_mock.last_request

    # Assert ODS Organisation Call for ABC123
    assert mock_responses.ods_abc123.called_once
    assert (
        mock_responses.ods_abc123.last_request.path == "/ord/2-0-0/organisations/abc123"
    )
    assert requests_mock.request_history[1] == mock_responses.ods_abc123.last_request

    # Assert Role Call for RO157
    assert mock_responses.ods_role_ro157.last_request.path == "/ord/2-0-0/roles/ro157"
    assert (
        requests_mock.request_history[2]
        == mock_responses.ods_role_ro157.request_history[0]
    )

    # Assert CRUD API Call for Organisation UUID (ABC123)
    assert crud_api_abc123_mock.called_once
    assert crud_api_abc123_mock.last_request.path == "/organisation/ods_code/abc123"
    assert requests_mock.request_history[3] == crud_api_abc123_mock.last_request

    # Failure for ABC123 should be logged
    assert "Error processing organisation with ods_code ABC123" in caplog.text

    # Assert ODS Organisation Call for EFG456
    assert ods_efg456_mock.called_once
    assert ods_efg456_mock.last_request.path == "/ord/2-0-0/organisations/efg456"
    assert requests_mock.request_history[4] == ods_efg456_mock.last_request

    # Assert Role Call for RO157 (again)
    assert mock_responses.ods_role_ro157.last_request.path == "/ord/2-0-0/roles/ro157"
    assert (
        requests_mock.request_history[5]
        == mock_responses.ods_role_ro157.request_history[1]
    )

    # Assert CRUD API Call for Organisation UUID (EFG456)
    assert crud_efg456_mock.called_once
    assert crud_efg456_mock.last_request.path == "/organisation/ods_code/efg456"
    assert requests_mock.request_history[6] == crud_efg456_mock.last_request

    # Assert load_data call
    load_data_mock.assert_called_once()
    data_to_load = [json.loads(entry) for entry in load_data_mock.call_args[0][0]]

    assert data_to_load == [
        {
            "path": "uuid_efg456",
            "body": {
                "active": True,
                "name": "Test Organisation EFG ODS",
                "telecom": "00000000000",
                "type": "NHS TRUST",
                "modified_by": "ODS_ETL_PIPELINE",
            },
        }
    ]


def test_processor_no_outdated_organisations(
    requests_mock: RequestsMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test when no outdated organisations are found."""
    requests_mock.get(
        "https://directory.spineservices.nhs.uk/ORD/2-0-0/sync",
        json={"Organisations": []},
    )

    date = "2023-01-01"
    assert processor(date) is None

    assert "No organisations found for the given date: 2023-01-01" in caplog.text


def test_processor_missing_org_link(
    requests_mock: RequestsMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test when OrgLink is missing in the response."""
    requests_mock.get(
        "https://directory.spineservices.nhs.uk/ORD/2-0-0/sync",
        json={"Organisations": [{"NotOrgLink": "test"}]},
    )

    date = "2025-04-23"
    assert processor(date) is None

    assert "Organisation link is missing in the response." in caplog.text


def test_processor_lambda_handler_success(mocker: MockerFixture) -> None:
    mock_processor = mocker.patch("pipeline.processor.processor")
    date = "2025-02-02"
    event = {"date": date}

    response = processor_lambda_handler(event, {})

    mock_processor.assert_called_once_with(date=date)
    assert response is None


def test_processor_lambda_handler_missing_date() -> None:
    response = processor_lambda_handler({}, {})

    assert response == {"statusCode": 400, "body": "Date parameter is required"}


def test_processor_lambda_handler_invalid_date_format() -> None:
    invalid_event = {"date": "14-05-2025"}

    response = processor_lambda_handler(invalid_event, {})

    assert response == {"statusCode": 400, "body": "Date must be in YYYY-MM-DD format"}


def test_processor_lambda_handler_exception(mocker: MockerFixture) -> None:
    mock_processor = mocker.patch("pipeline.processor.processor")
    mock_processor.side_effect = Exception("Test error")
    event = {"date": "2025-02-02"}

    result = processor_lambda_handler(event, {})

    mock_processor.assert_called_once_with(date="2025-02-02")
    # assert "Unexpected error" in mock_logging.call_args[0][0]
    assert str(result["statusCode"]) == "500"
    assert "Unexpected error: Test error" in result["body"]
