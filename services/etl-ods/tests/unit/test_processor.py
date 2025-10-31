import json
from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Generator, NamedTuple

import pytest
import requests
from ftrs_common.utils.correlation_id import set_correlation_id
from ftrs_common.utils.request_id import set_request_id
from ftrs_data_layer.logbase import OdsETLPipelineLogBase
from pytest_mock import MockerFixture
from requests_mock import Mocker as RequestsMock
from requests_mock.adapter import _Matcher as Matcher

from pipeline.processor import (
    MAX_DAYS_PAST,
    processor,
    processor_lambda_handler,
)

TEST_CORRELATION_ID = "test-correlation"
TEST_REQUEST_ID = "test-request"


@pytest.fixture(autouse=True)
def fixed_ids() -> Generator[None, None, None]:
    set_correlation_id(TEST_CORRELATION_ID)
    set_request_id(TEST_REQUEST_ID)
    yield
    set_correlation_id(None)
    set_request_id(None)


class MockResponses(NamedTuple):
    ods_api: Matcher
    apim_org_abc123: Matcher


# Helper functions to reduce duplication
def _helper_create_organization_resource(ods_code: str) -> dict:
    return {
        "resourceType": "Organization",
        "id": ods_code,
        "name": f"Test Organisation {ods_code} ODS",
        "active": True,
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": ods_code,
            }
        ],
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


def create_ods_terminology_bundle(organizations: list[dict]) -> dict:
    """Create a FHIR Bundle response from ODS Terminology API."""
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(organizations),
        "status_code": 200,
        "entry": [{"resource": org} for org in organizations],
    }


def create_apim_uuid_bundle(uuid: str) -> dict:
    """Create a FHIR Bundle response for APIM UUID lookup."""
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "status_code": 200,
        "entry": [
            {
                "resource": {
                    "resourceType": "Organization",
                    "id": uuid,
                }
            }
        ],
    }


@pytest.fixture
def mock_responses(requests_mock: RequestsMock) -> MockResponses:
    """Setup standard mock responses for ODS Terminology API and APIM."""
    org_abc123 = _helper_create_organization_resource("ABC123")
    ods_terminology_bundle = create_ods_terminology_bundle([org_abc123])

    ods_api_mock = requests_mock.get(
        "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization",
        json=ods_terminology_bundle,
    )

    # Setup APIM API Mock for Organisation UUID
    apim_bundle = create_apim_uuid_bundle("00000000-0000-0000-0000-000000000abc")
    apim_org_abc123_mock = requests_mock.get(
        "http://test-apim-api/Organization?identifier=odsOrganisationCode|ABC123",
        json=apim_bundle,
    )

    return MockResponses(
        ods_api=ods_api_mock,
        apim_org_abc123=apim_org_abc123_mock,
    )


def test_processor_processing_organisations_successful(
    mocker: MockerFixture,
    requests_mock: RequestsMock,
    mock_responses: MockResponses,
) -> None:
    expected_call_count = 2  # ODS Terminology API + APIM UUID lookup
    date = datetime.now().strftime("%Y-%m-%d")
    load_data_mock = mocker.patch("pipeline.processor.load_data")
    assert processor(date) is None
    assert requests_mock.call_count == expected_call_count

    # Assert ODS Terminology API Call
    assert mock_responses.ods_api.called_once
    assert mock_responses.ods_api.last_request.qs == {"_lastupdated": [date]}
    assert requests_mock.request_history[0] == mock_responses.ods_api.last_request

    # Assert APIM API Call for Organisation UUID
    assert mock_responses.apim_org_abc123.called_once
    assert mock_responses.apim_org_abc123.last_request.path == "/organization"
    assert (
        mock_responses.apim_org_abc123.last_request.query
        == "identifier=odsorganisationcode%7cabc123"
    )
    assert (
        requests_mock.request_history[1] == mock_responses.apim_org_abc123.last_request
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
                "name": "Test Organisation ABC123 ODS",
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
            "request_id": TEST_REQUEST_ID,
        }
    ]


def test_processor_continue_on_validation_failure(
    mocker: MockerFixture,
    requests_mock: RequestsMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that processing continues when one organization fails validation."""
    org_abc123 = _helper_create_organization_resource("ABC123")
    org_efg456 = _helper_create_organization_resource("EFG456")
    ods_terminology_bundle = create_ods_terminology_bundle([org_abc123, org_efg456])

    ods_api_mock = requests_mock.get(
        "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization",
        json=ods_terminology_bundle,
    )

    # ABC123 fails UUID lookup
    apim_api_abc123_mock = requests_mock.get(
        "http://test-apim-api/Organization?identifier=odsOrganisationCode|ABC123",
        status_code=422,  # Simulate Unprocessable Entity error
    )

    # EFG456 succeeds
    apim_bundle_efg456 = create_apim_uuid_bundle("00000000-0000-0000-0000-000000000EFG")
    apim_efg456_mock = requests_mock.get(
        "http://test-apim-api/Organization?identifier=odsOrganisationCode|EFG456",
        json=apim_bundle_efg456,
    )
    expected_call_count = 3  # ODS Terminology + 2 UUID lookups

    date = datetime.now().strftime("%Y-%m-%d")

    load_data_mock = mocker.patch("pipeline.processor.load_data")
    assert processor(date) is None

    assert requests_mock.call_count == expected_call_count
    # Assert ODS Terminology API Call
    assert ods_api_mock.called_once
    assert ods_api_mock.last_request.qs == {"_lastupdated": [date]}
    assert requests_mock.request_history[0] == ods_api_mock.last_request

    # Assert APIM API Call for ABC123 UUID (fails)
    assert apim_api_abc123_mock.called_once
    assert (
        apim_api_abc123_mock.last_request.query
        == "identifier=odsorganisationcode%7cabc123"
    )

    assert requests_mock.request_history[1] == apim_api_abc123_mock.last_request

    # Failure for ABC123 should be logged
    assert "422 Client Error" in caplog.text or "ETL_PROCESSOR_027" in caplog.text

    # Assert APIM API Call for EFG456 UUID (succeeds)
    assert apim_efg456_mock.called_once
    assert apim_efg456_mock.last_request.path == "/organization"
    assert (
        apim_efg456_mock.last_request.query == "identifier=odsorganisationcode%7cefg456"
    )
    assert requests_mock.request_history[2] == apim_efg456_mock.last_request

    # Assert load_data call - only EFG456 should be loaded
    load_data_mock.assert_called_once()
    data_to_load = [json.loads(entry) for entry in load_data_mock.call_args[0][0]]

    assert len(data_to_load) == 1
    assert data_to_load[0]["path"] == "00000000-0000-0000-0000-000000000EFG"
    assert data_to_load[0]["body"]["identifier"][0]["value"] == "EFG456"


def test_processor_no_outdated_organisations(
    requests_mock: RequestsMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test when no outdated organisations are found."""
    requests_mock.get(
        "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization",
        json={
            "resourceType": "Bundle",
            "type": "searchset",
            "total": 0,
            "status_code": 200,
        },
    )

    date = datetime.now().strftime("%Y-%m-%d")
    assert processor(date) is None

    expected_log = OdsETLPipelineLogBase.ETL_PROCESSOR_020.value.message.format(
        date=date
    )
    assert expected_log in caplog.text


def test_processor_no_organisations_logs_and_returns(
    mocker: MockerFixture,
) -> None:
    mocker.patch("pipeline.processor.fetch_outdated_organisations", return_value=[])
    date = datetime.now().strftime("%Y-%m-%d")
    assert processor(date) is None


def test_process_organisation_exception_logs_and_returns_none(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    organisation_resource = _helper_create_organization_resource("ANYCODE")
    mocker.patch(
        "pipeline.processor.transform_to_payload",
        side_effect=Exception("transform failed"),
    )

    result = processor.__globals__["_process_organisation"](organisation_resource)
    assert result is None
    assert (
        "Error processing organisation with ods_code unknown: transform failed"
        in caplog.text
    )


def test_processor_lambda_handler_success(mocker: MockerFixture) -> None:
    mock_processor = mocker.patch("pipeline.processor.processor")
    date = datetime.now().strftime("%Y-%m-%d")
    event = {"date": date}

    response = processor_lambda_handler(event, {})

    mock_processor.assert_called_once_with(date=date)
    assert response == {"statusCode": 200, "body": "Processing complete"}


def test_processor_lambda_handler_success_is_scheduled(
    mocker: MockerFixture,
) -> None:
    mock_processor = mocker.patch("pipeline.processor.processor")

    event = {"is_scheduled": True}

    response = processor_lambda_handler(event, {})

    previous_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    mock_processor.assert_called_once_with(date=previous_date)
    assert response == {"statusCode": 200, "body": "Processing complete"}


def test_processor_lambda_handler_missing_date() -> None:
    response = processor_lambda_handler({}, {})
    assert response["statusCode"] == HTTPStatus.BAD_REQUEST
    assert json.loads(response["body"]) == {"error": "Date parameter is required"}


def test_processor_lambda_handler_invalid_date_format() -> None:
    invalid_event = {"date": "14-05-2025"}
    response = processor_lambda_handler(invalid_event, {})
    assert response["statusCode"] == HTTPStatus.BAD_REQUEST
    assert json.loads(response["body"]) == {
        "error": "Date must be in YYYY-MM-DD format"
    }


def test_processor_lambda_handler_date_too_old(mocker: MockerFixture) -> None:
    # Date more than 185 days in the past from 2025-08-14
    old_date = "2023-01-01"
    event = {"date": old_date}
    mock_processor = mocker.patch("pipeline.processor.processor")
    response = processor_lambda_handler(event, {})

    mock_processor.assert_not_called()
    assert response["statusCode"] == HTTPStatus.BAD_REQUEST
    assert json.loads(response["body"]) == {
        "error": f"Date must not be more than {MAX_DAYS_PAST} days in the past"
    }


def test_processor_lambda_handler_date_exactly_185_days(mocker: MockerFixture) -> None:
    # Calculate a date exactly 185 days ago from today
    date_185_days_ago = (datetime.now().date() - timedelta(days=185)).strftime(
        "%Y-%m-%d"
    )
    event = {"date": date_185_days_ago}
    mock_processor = mocker.patch("pipeline.processor.processor")
    response = processor_lambda_handler(event, {})
    mock_processor.assert_called_once_with(date=date_185_days_ago)
    assert response == {"statusCode": 200, "body": "Processing complete"}


def test_processor_lambda_handler_exception(mocker: MockerFixture) -> None:
    mock_processor = mocker.patch("pipeline.processor.processor")
    mock_processor.side_effect = Exception("Test error")
    date = datetime.now().strftime("%Y-%m-%d")
    event = {"date": date}

    result = processor_lambda_handler(event, {})

    mock_processor.assert_called_once_with(date=date)
    assert str(result["statusCode"]) == "500"
    error_body = json.loads(result["body"])
    assert "Unexpected error: Test error" in error_body["error"]


def test_processor_logs_and_raises_request_exception(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    mocker.patch(
        "pipeline.processor.fetch_outdated_organisations",
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
        "pipeline.processor.fetch_outdated_organisations",
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


def test_process_organisation_uuid_not_found(
    mocker: MockerFixture,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test _process_organisation when UUID lookup returns None (empty Bundle)."""
    org_abc123 = _helper_create_organization_resource("ABC123")

    # Mock fetch_organisation_uuid to return None (empty Bundle case)
    mocker.patch("pipeline.processor.fetch_organisation_uuid", return_value=None)

    result = processor.__globals__["_process_organisation"](org_abc123)

    assert result is None
    assert "Organisation UUID not found in internal system" in caplog.text
    assert "ABC123" in caplog.text
