import json
from datetime import datetime

# , timedelta
# from http import HTTPStatus
from typing import NamedTuple

import pytest
import requests

# from unittest.mock import MagicMock, patch
from ftrs_common.utils.correlation_id import set_correlation_id
from ftrs_data_layer.logbase import OdsETLPipelineLogBase
from pytest_mock import MockerFixture
from requests_mock import Mocker as RequestsMock
from requests_mock.adapter import _Matcher as Matcher

from pipeline.processor import processor

# , processor_lambda_handler
TEST_CORRELATION_ID = "test-correlation"


@pytest.fixture(autouse=True)
def fixed_correlation_id() -> None:
    set_correlation_id(TEST_CORRELATION_ID)
    yield
    set_correlation_id(None)


class MockResponses(NamedTuple):
    ods_sync: Matcher
    ods_abc123: Matcher
    apim_org_abc123: Matcher


# @pytest.fixture(autouse=True)
# def mock_tracer() -> Generator[MagicMock, None, None]:
#     with patch("pipeline.consumer.tracer") as mock_tracer:
#         mock_tracer.capture_lambda_handler.return_value = lambda f: f
#         yield mock_tracer


@pytest.fixture
def mock_responses(requests_mock: RequestsMock) -> MockResponses:
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

    # Setup APIM API Mock for Organisation UUID (returns a FHIR Bundle with Organization resource)
    apim_api_data_abc123 = {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": [
            {
                "resource": {
                    "resourceType": "Organization",
                    "id": "00000000-0000-0000-0000-000000000abc",
                }
            }
        ],
    }
    apim_org_abc123_mock = requests_mock.get(
        "http://test-apim-api/Organization?identifier=odsOrganisationCode|ABC123",
        json=apim_api_data_abc123,
    )

    return MockResponses(
        ods_sync=ods_sync_mock,
        ods_abc123=ods_abc123_mock,
        apim_org_abc123=apim_org_abc123_mock,
    )


def test_processor_processing_organisations_successful(
    mocker: MockerFixture,
    requests_mock: RequestsMock,
    mock_responses: MockResponses,
) -> None:
    expected_call_count = 3
    date = datetime.now().strftime("%Y-%m-%d")
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
    # Assert APIM API Call for Organisation UUID
    assert mock_responses.apim_org_abc123.called_once
    assert mock_responses.apim_org_abc123.last_request.path == "/organization"
    assert (
        mock_responses.apim_org_abc123.last_request.query
        == "identifier=odsorganisationcode%7cabc123"
    )
    assert (
        requests_mock.request_history[2] == mock_responses.apim_org_abc123.last_request
    )
    # Assert load_data call
    load_data_mock.assert_called_once()
    data_to_load = [json.loads(entry) for entry in load_data_mock.call_args[0][0]]
    # Check the data struct
    assert data_to_load == [
        {
            "path": "00000000-0000-0000-0000-000000000abc",
            "body": {
                "resourceType": "Organization",
                "id": "00000000-0000-0000-0000-000000000abc",
                "meta": {
                    "profile": [
                        "https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"
                    ]
                },
                "active": True,
                "type": [
                    {
                        "coding": [
                            {
                                "system": "TO-DO",
                                "code": "GP Service",
                                "display": "GP Service",
                            }
                        ],
                        "text": "GP Service",
                    }
                ],
                "name": "Test Organisation ABC ODS",
                "identifier": [
                    {
                        "use": "official",
                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                        "value": "ABC123",
                    }
                ],
                "telecom": [],
            },
            "correlation_id": TEST_CORRELATION_ID,
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

    apim_api_abc123_mock = requests_mock.get(
        "http://test-apim-api/Organization?identifier=odsOrganisationCode|ABC123",
        status_code=422,  # Simulate Unprocessable Entity error
    )

    ods_efg456_mock = requests_mock.get(
        "https://directory.spineservices.nhs.uk/STU3/Organization/EFG456",
        json={
            "resourceType": "Organization",
            "meta": {
                "profile": [
                    "https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"
                ]
            },
            "id": "EFG456",
            "name": "Test Organisation EFG ODS",
            "active": True,
            "identifier": {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "EFG456",
            },
            "telecom": [],
        },
    )

    apim_api_data_efg456 = {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": [
            {
                "resource": {
                    "resourceType": "Organization",
                    "id": "00000000-0000-0000-0000-000000000EFG",
                }
            }
        ],
    }
    apim_efg456_mock = requests_mock.get(
        "http://test-apim-api/Organization?identifier=odsOrganisationCode|EFG456",
        json=apim_api_data_efg456,
    )
    expected_call_count = 5

    date = datetime.now().strftime("%Y-%m-%d")

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

    # Assert APIM API Call for Organisation UUID (00000000-0000-0000-0000-000000000abc)
    assert apim_api_abc123_mock.called_once
    assert (
        apim_api_abc123_mock.last_request.query
        == "identifier=odsorganisationcode%7cabc123"
    )

    assert requests_mock.request_history[2] == apim_api_abc123_mock.last_request

    # Failure for ABC123 should be logged
    expected_failed_log = OdsETLPipelineLogBase.ETL_PROCESSOR_027.value.message.format(
        ods_code="ABC123",
        error_message="422 Client Error: None for url: http://test-apim-api/Organization?identifier=odsOrganisationCode%7CABC123",
    )
    assert expected_failed_log in caplog.text

    # Assert ODS Organisation Call for EFG456
    assert ods_efg456_mock.called_once
    assert ods_efg456_mock.last_request.path == "/stu3/organization/efg456"
    assert requests_mock.request_history[3] == ods_efg456_mock.last_request

    # Assert APIM API Call for Organisation UUID (00000000-0000-0000-0000-000000000EFG)
    assert apim_efg456_mock.called_once
    assert apim_efg456_mock.last_request.path == "/organization"
    assert (
        apim_efg456_mock.last_request.query == "identifier=odsorganisationcode%7cefg456"
    )
    assert requests_mock.request_history[4] == apim_efg456_mock.last_request

    # Assert load_data call
    load_data_mock.assert_called_once()
    data_to_load = [json.loads(entry) for entry in load_data_mock.call_args[0][0]]
    assert data_to_load == [
        {
            "path": "00000000-0000-0000-0000-000000000EFG",
            "body": {
                "resourceType": "Organization",
                "meta": {
                    "profile": [
                        "https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"
                    ]
                },
                "active": True,
                "type": [
                    {
                        "coding": [
                            {
                                "system": "TO-DO",
                                "code": "GP Practice",
                                "display": "GP Practice",
                            }
                        ],
                        "text": "GP Practice",
                    }
                ],
                "name": "Test Organisation EFG ODS",
                "id": "00000000-0000-0000-0000-000000000EFG",
                "identifier": [
                    {
                        "use": "official",
                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                        "value": "EFG456",
                    }
                ],
                "telecom": [],
            },
            "correlation_id": TEST_CORRELATION_ID,
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

    date = datetime.now().strftime("%Y-%m-%d")
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
    date = datetime.now().strftime("%Y-%m-%d")
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
    date = datetime.now().strftime("%Y-%m-%d")
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


# def test_processor_lambda_handler_success(mocker: MockerFixture) -> None:
#     mock_processor = mocker.patch("pipeline.processor.processor")
#     date = datetime.now().strftime("%Y-%m-%d")
#     event = {"date": date}

#     response = processor_lambda_handler(event, {})

#     mock_processor.assert_called_once_with(date=date)
#     assert response == {"statusCode": 200, "body": "Processing complete"}


# def test_processor_lambda_handler_missing_date() -> None:
#     response = processor_lambda_handler({}, {})
#     assert response["statusCode"] == HTTPStatus.BAD_REQUEST
#     assert json.loads(response["body"]) == {"error": "Date parameter is required"}


# def test_processor_lambda_handler_invalid_date_format() -> None:
#     invalid_event = {"date": "14-05-2025"}
#     response = processor_lambda_handler(invalid_event, {})
#     assert response["statusCode"] == HTTPStatus.BAD_REQUEST
#     assert json.loads(response["body"]) == {
#         "error": "Date must be in YYYY-MM-DD format"
#     }


# def test_processor_lambda_handler_date_too_old(mocker: MockerFixture) -> None:
#     # Date more than 185 days in the past from 2025-08-14
#     old_date = "2023-01-01"
#     event = {"date": old_date}
#     mock_processor = mocker.patch("pipeline.processor.processor")
#     response = processor_lambda_handler(event, {})

#     mock_processor.assert_not_called()
#     assert response["statusCode"] == HTTPStatus.BAD_REQUEST
#     assert json.loads(response["body"]) == {
#         "error": f"Date must not be more than {MAX_DAYS_PAST} days in the past"
#     }


# def test_processor_lambda_handler_date_exactly_185_days(mocker: MockerFixture) -> None:
#     # Calculate a date exactly 185 days ago from today
#     date_185_days_ago = (datetime.now().date() - timedelta(days=185)).strftime(
#         "%Y-%m-%d"
#     )
#     event = {"date": date_185_days_ago}
#     mock_processor = mocker.patch("pipeline.processor.processor")
#     response = processor_lambda_handler(event, {})
#     mock_processor.assert_called_once_with(date=date_185_days_ago)
#     assert response == {"statusCode": 200, "body": "Processing complete"}


# def test_processor_lambda_handler_exception(mocker: MockerFixture) -> None:
#     mock_processor = mocker.patch("pipeline.processor.processor")
#     mock_processor.side_effect = Exception("Test error")
#     date = datetime.now().strftime("%Y-%m-%d")
#     event = {"date": date}

#     result = processor_lambda_handler(event, {})

#     mock_processor.assert_called_once_with(date=date)
#     assert str(result["statusCode"]) == "500"
#     error_body = json.loads(result["body"])
#     assert "Unexpected error: Test error" in error_body["error"]


def test_processor_logs_and_raises_request_exception(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    mocker.patch(
        "pipeline.processor.fetch_sync_data",
        side_effect=requests.exceptions.RequestException("network fail"),
    )
    date = datetime.now().strftime("%Y-%m-%d")
    with caplog.at_level("INFO"):
        with pytest.raises(requests.exceptions.RequestException, match="network fail"):
            processor(date)
        expected_log = OdsETLPipelineLogBase.ETL_PROCESSOR_022.value.message.format(
            error_message="network fail"
        )
        assert expected_log in caplog.text


def test_processor_logs_and_raises_generic_exception(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    mocker.patch(
        "pipeline.processor.fetch_sync_data",
        side_effect=Exception("unexpected error"),
    )
    date = datetime.now().strftime("%Y-%m-%d")
    with caplog.at_level("INFO"):
        with pytest.raises(Exception, match="unexpected error"):
            processor(date)
        expected_log = OdsETLPipelineLogBase.ETL_PROCESSOR_023.value.message.format(
            error_message="unexpected error"
        )
        assert expected_log in caplog.text
