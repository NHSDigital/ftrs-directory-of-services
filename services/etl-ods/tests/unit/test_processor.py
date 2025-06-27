import json
import pytest
from ftrs_data_layer.logbase import OdsETLPipelineLogBase
from pytest_mock import MockerFixture
from requests_mock import Mocker as RequestsMock

from pipeline.processor import processor, processor_lambda_handler


@pytest.fixture
def mock_responses(requests_mock: RequestsMock):
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

    ods_data_abc123 = {
        "resourceType": "Organization",
        "id": "ABC123",
        "name": "Test Organisation",
        "active": True,
        "telecom": [{"system": "phone", "value": "00000000000"}],
        "type": [{"text": "NHS TRUST"}],
    }
    ods_abc123_mock = requests_mock.get(
        "https://directory.spineservices.nhs.uk/STU3/Organization/ABC123",
        json=ods_data_abc123,
    )

    crud_api_data_abc123 = {
        "id": "uuid_abc123",
        "name": "Test Organisation",
    }
    crud_org_abc123_mock = requests_mock.get(
        "http://test-crud-api/organisation/ods_code/ABC123",
        json=crud_api_data_abc123,
    )

    return {
        "ods_sync": ods_sync_mock,
        "ods_abc123": ods_abc123_mock,
        "crud_org_abc123": crud_org_abc123_mock,
    }


def test_processor_processing_organisations_successful(
    mocker: MockerFixture,
    requests_mock: RequestsMock,
    mock_responses,
) -> None:
    date = "2023-01-01"

    mocker.patch(
        "pipeline.processor.transform_to_payload",
        return_value={
            "active": True,
            "name": "Test Organisation",
            "telecom": "00000000000",
            "type": "NHS TRUST",
            "modified_by": "ODS_ETL_PIPELINE",
        },
    )
    # Patch fetch_organisation_uuid to use lowercase code
    mocker.patch(
        "pipeline.processor.fetch_organisation_uuid", return_value="uuid_abc123"
    )
    # Patch load_data to just record calls
    load_data_mock = mocker.patch("pipeline.processor.load_data")

    assert processor(date) is None

    # Assert ODS Sync Call
    assert mock_responses["ods_sync"].called_once
    assert mock_responses["ods_sync"].last_request.path == "/ord/2-0-0/sync"
    assert mock_responses["ods_sync"].last_request.qs == {"LastChangeDate": [date]}

    # Assert ODS Organisation Call for ABC123
    assert mock_responses["ods_abc123"].called_once
    assert mock_responses["ods_abc123"].last_request.path == "/stu3/organization/ABC123"

    # Assert CRUD API Call for Organisation UUID
    assert mock_responses["crud_org_abc123"].called_once
    assert (
        mock_responses["crud_org_abc123"].last_request.path
        == "/organisation/ods_code/ABC123"
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
    caplog: pytest.LogCaptureFixture,
) -> None:
    requests_mock.get(
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

    requests_mock.get(
        "https://directory.spineservices.nhs.uk/STU3/Organization/ABC123",
        json={
            "resourceType": "Organization",
            "id": "ABC123",
            "name": "Test Organisation",
            "active": True,
            "telecom": [{"system": "phone", "value": "00000000000"}],
            "type": [{"text": "NHS TRUST"}],
        },
    )
    requests_mock.get(
        "https://directory.spineservices.nhs.uk/STU3/Organization/EFG456",
        json={
            "resourceType": "Organization",
            "id": "EFG456",
            "name": "Test Organisation EFG ODS",
            "active": True,
            "telecom": [{"system": "phone", "value": "11111111111"}],
            "type": [{"text": "NHS TRUST"}],
        },
    )

    # CRUD API for ABC123 fails
    requests_mock.get(
        "http://test-crud-api/organisation/ods_code/ABC123",
        status_code=422,
        text="Unprocessable Entity",
    )
    # CRUD API for EFG456 succeeds
    requests_mock.get(
        "http://test-crud-api/organisation/ods_code/EFG456",
        json={"id": "uuid_efg456", "name": "Test Organisation EFG"},
    )

    # Patch transform_to_payload
    mocker.patch(
        "pipeline.processor.transform_to_payload",
        side_effect=[
            {
                "active": True,
                "name": "Test Organisation",
                "telecom": "00000000000",
                "type": "NHS TRUST",
                "modified_by": "ODS_ETL_PIPELINE",
            },
            {
                "active": True,
                "name": "Test Organisation EFG ODS",
                "telecom": "11111111111",
                "type": "NHS TRUST",
                "modified_by": "ODS_ETL_PIPELINE",
            },
        ],
    )

    # Patch fetch_organisation_uuid to raise for ABC123, succeed for EFG456
    def fetch_uuid_side_effect(ods_code):
        if ods_code == "ABC123":
            raise Exception(
                "422 Client Error: None for url: http://test-crud-api/organisation/ods_code/ABC123"
            )
        return "uuid_efg456"

    mocker.patch(
        "pipeline.processor.fetch_organisation_uuid", side_effect=fetch_uuid_side_effect
    )
    load_data_mock = mocker.patch("pipeline.processor.load_data")

    date = "2023-01-01"
    assert processor(date) is None

    assert "422 Client Error" in caplog.text

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
    assert str(result["statusCode"]) == "500"
    assert "Unexpected error: Test error" in result["body"]
