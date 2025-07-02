import json
from typing import NamedTuple

import pytest
from ftrs_data_layer.logbase import OdsETLPipelineLogBase
from pytest_mock import MockerFixture
from requests_mock import (
    Mocker as RequestsMock,
)
from requests_mock.adapter import _Matcher as Matcher

from pipeline.processor import processor, processor_lambda_handler


class MockResponses(NamedTuple):
    ods_sync: Matcher
    ods_abc123: Matcher
    crud_org_abc123: Matcher


@pytest.fixture
def mock_responses(
    requests_mock: RequestsMock,
) -> MockResponses:
    # Setup ODS Sync Data Mock
    ods_sync_data = {
        "Organisations": [
            {
                "OrgLink": "https://directory.spineservices.nhs.uk/STU3/Organization/ABC123"
            }
        ]
    }
    ods_sync_mock = requests_mock.get(
        "https://directory.spineservices.nhs.uk/ORD/2-0-0/sync",
        json=ods_sync_data,
    )

    # Setup ODS Organisation Data Mock for ABC123
    ods_data_abc123 = {
        "resourceType": "Organization",
        "id": "ABC123",
        "name": "Test Organisation ABC ODS",
        "active": True,
        "identifier": {
            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
            "value": "ABC123",
        },
        "extension": [
            {
                "url": "https://fhir.nhs.uk/STU3/StructureDefinition/Extension-ODSAPI-OrganizationRole-1",
                "extension": [
                    {
                        "url": "role",
                        "valueCoding": {
                            "system": "https://directory.spineservices.nhs.uk/STU3/CodeSystem/ODSAPI-OrganizationRole-1",
                            "code": "197",
                            "display": "GP Service",
                        },
                    },
                    {"url": "primaryRole", "valueBoolean": True},
                ],
            }
        ],
    }
    ods_abc123_mock = requests_mock.get(
        "https://directory.spineservices.nhs.uk/STU3/Organization/ABC123",
        json=ods_data_abc123,
    )

    # Setup CRUD API Mock for Organisation UUID (ABC123)
    crud_api_data_abc123 = {
        "resourceType": "Organization",
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
        crud_org_abc123=crud_org_abc123_mock,
    )


def test_processor_processing_organisations_successful(
    mocker: MockerFixture,
    requests_mock: RequestsMock,
    mock_responses: MockResponses,
) -> None:
    expected_call_count = 3

    date = "2023-01-01"

    load_data_mock = mocker.patch("pipeline.processor.load_data")
    assert processor(date) is None

    assert requests_mock.call_count == expected_call_count

    # Assert ODS Sync Call
    assert mock_responses.ods_sync.called_once
    assert mock_responses.ods_sync.last_request.path == "/ord/2-0-0/sync"
    assert mock_responses.ods_sync.last_request.qs == {"lastchangedate": [date]}
    assert requests_mock.request_history[0] == mock_responses.ods_sync.last_request

    # Assert ODS Organisation Call for ABC123
    assert mock_responses.ods_abc123.called_once
    assert mock_responses.ods_abc123.last_request.path == "/stu3/organization/abc123"
    assert requests_mock.request_history[1] == mock_responses.ods_abc123.last_request

    # Assert CRUD API Call for Organisation UUID
    assert mock_responses.crud_org_abc123.called_once
    assert (
        mock_responses.crud_org_abc123.last_request.path
        == "/organisation/ods_code/abc123"
    )
    assert (
        requests_mock.request_history[2] == mock_responses.crud_org_abc123.last_request
    )

    # Assert load_data call
    load_data_mock.assert_called_once()
    data_to_load = [json.loads(entry) for entry in load_data_mock.call_args[0][0]]

    # Check the data struct
    assert data_to_load == [
        {
            "path": "uuid_abc123",
            "body": {
                "resourceType": "Organization",
                "id": "ABC123",
                "active": True,
                "type": [{"coding": [{"system": "todo", "display": "GP Service"}]}],
                "name": "Test Organisation ABC ODS",
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
                    "OrgLink": "https://directory.spineservices.nhs.uk/STU3/Organization/ABC123"
                },
                {
                    "OrgLink": "https://directory.spineservices.nhs.uk/STU3/Organization/EFG456"
                },
            ]
        },
    )

    crud_api_abc123_mock = requests_mock.get(
        "http://test-crud-api/organisation/ods_code/ABC123",
        status_code=422,  # Simulate Unprocessable Entity error
    )

    ods_efg456_mock = requests_mock.get(
        "https://directory.spineservices.nhs.uk/STU3/Organization/EFG456",
        json={
            "resourceType": "Organization",
            "id": "EFG456",
            "name": "Test Organisation EFG ODS",
            "active": True,
        },
    )

    crud_efg456_mock = requests_mock.get(
        "http://test-crud-api/organisation/ods_code/EFG456",
        json={"id": "uuid_efg456", "name": "Test Organisation EFG"},
    )
    expected_call_count = 5

    date = "2023-01-01"

    load_data_mock = mocker.patch("pipeline.processor.load_data")
    assert processor(date) is None

    assert requests_mock.call_count == expected_call_count
    # Assert ODS Sync Call
    assert ods_sync_mock.called_once
    assert ods_sync_mock.last_request.path == "/ord/2-0-0/sync"
    assert ods_sync_mock.last_request.qs == {"lastchangedate": [date]}
    assert requests_mock.request_history[0] == ods_sync_mock.last_request

    # Assert ODS Organisation Call for ABC123
    assert mock_responses.ods_abc123.called_once
    assert mock_responses.ods_abc123.last_request.path == "/stu3/organization/abc123"
    assert requests_mock.request_history[1] == mock_responses.ods_abc123.last_request

    # Assert CRUD API Call for Organisation UUID (ABC123)
    assert crud_api_abc123_mock.called_once
    assert crud_api_abc123_mock.last_request.path == "/organisation/ods_code/abc123"
    assert requests_mock.request_history[2] == crud_api_abc123_mock.last_request

    # Failure for ABC123 should be logged
    expected_failed_log = OdsETLPipelineLogBase.ETL_PROCESSOR_027.value.message.format(
        ods_code="ABC123",
        error_message="422 Client Error: None for url: http://test-crud-api/organisation/ods_code/ABC123",
    )
    assert expected_failed_log in caplog.text

    # Assert ODS Organisation Call for EFG456
    assert ods_efg456_mock.called_once
    assert ods_efg456_mock.last_request.path == "/stu3/organization/efg456"
    assert requests_mock.request_history[3] == ods_efg456_mock.last_request

    # Assert CRUD API Call for Organisation UUID (EFG456)
    assert crud_efg456_mock.called_once
    assert crud_efg456_mock.last_request.path == "/organisation/ods_code/efg456"
    assert requests_mock.request_history[4] == crud_efg456_mock.last_request

    # Assert load_data call
    load_data_mock.assert_called_once()
    data_to_load = [json.loads(entry) for entry in load_data_mock.call_args[0][0]]
    print(data_to_load)
    assert data_to_load == [
        {
            "path": "uuid_efg456",
            "body": {
                "resourceType": "Organization",
                "active": True,
                "type": [{"coding": [{"system": "todo"}]}],
                "name": "Test Organisation EFG ODS",
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

    expected_log = OdsETLPipelineLogBase.ETL_PROCESSOR_020.value.message.format(
        date=date
    )
    assert expected_log in caplog.text


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

    expected_log = OdsETLPipelineLogBase.ETL_PROCESSOR_021.value.message.format()
    assert expected_log in caplog.text


def test_processor_no_organisations_logs_and_returns(
    mocker: MockerFixture, requests_mock: RequestsMock, caplog: pytest.LogCaptureFixture
) -> None:
    mocker.patch("pipeline.processor.fetch_sync_data", return_value=[])
    date = "2023-01-01"
    assert processor(date) is None
    expected_log = OdsETLPipelineLogBase.ETL_PROCESSOR_020.value.message.format(
        date=date
    )
    assert expected_log in caplog.text


def test_processor_skips_when_orglink_missing(
    mocker: MockerFixture, requests_mock: RequestsMock, caplog: pytest.LogCaptureFixture
) -> None:
    mocker.patch(
        "pipeline.processor.fetch_sync_data", return_value=[{"NotOrgLink": "missing"}]
    )
    date = "2023-01-01"
    assert processor(date) is None
    expected_log = OdsETLPipelineLogBase.ETL_PROCESSOR_021.value.message.format()
    assert expected_log in caplog.text


def test_process_organisation_exception_logs_and_returns_none(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    mocker.patch(
        "pipeline.processor.fetch_ods_organisation_data", side_effect=Exception("fail")
    )
    result = processor.__globals__["process_organisation"]("ANYCODE")
    assert result is None
    expected_log = OdsETLPipelineLogBase.ETL_PROCESSOR_027.value.message.format(
        ods_code="ANYCODE", error_message="fail"
    )
    assert expected_log in caplog.text


def test_processor_lambda_handler_success(mocker: MockerFixture) -> None:
    mock_processor = mocker.patch("pipeline.processor.processor")
    date = "2025-02-02"
    event = {"date": date}

    response = processor_lambda_handler(event, {})

    mock_processor.assert_called_once_with(date=date)
    assert response == {"statusCode": 200, "body": "Processing complete"}


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
    assert str(result["statusCode"]) == "500"
    assert "Unexpected error: Test error" in result["body"]
