from http import HTTPStatus

import pytest
from pytest_mock import MockerFixture
from requests import HTTPError
from requests_mock import Mocker as RequestsMock

from pipeline.extract import (
    extract_ods_code,
    fetch_ods_organisation_data,
    fetch_organisation_uuid,
    fetch_sync_data,
)


def test_fetch_sync_data(requests_mock: RequestsMock) -> None:
    mock_call = requests_mock.get(
        "https://directory.spineservices.nhs.uk/ORD/2-0-0/sync?",
        json={"Organisations": [{"OrgLink": "https:///organisations/ABC123"}]},
    )

    date = "2025-05-14"
    result = fetch_sync_data(date)

    assert result == [{"OrgLink": "https:///organisations/ABC123"}]
    assert mock_call.called_once
    assert mock_call.last_request.path == "/ord/2-0-0/sync"
    assert mock_call.last_request.qs == {
        "lastchangedate": [date]
    }  # qs returns in lowercase


def test_fetch_ods_organisation_data(requests_mock: RequestsMock) -> None:
    mock_call = requests_mock.get(
        "https://directory.spineservices.nhs.uk/STU3/Organization/ABC123",
        json={"resourceType": "Organization", "id": "ABC123"},
    )

    ods_code = "ABC123"
    result = fetch_ods_organisation_data(ods_code)
    assert result == {"resourceType": "Organization", "id": "ABC123"}

    assert mock_call.called_once
    assert (
        mock_call.last_request.url
        == "https://directory.spineservices.nhs.uk/STU3/Organization/ABC123"
    )


def test_fetch_ods_organisation_data_no_organisations(
    requests_mock: RequestsMock,
) -> None:
    requests_mock.get(
        "https://directory.spineservices.nhs.uk/STU3/Organization/ABC123",
        json={"Organisations": []},
    )

    ods_code = "ABC123"
    result = fetch_ods_organisation_data(ods_code)
    assert result == {"Organisations": []}


def test_fetch_organisation_uuid(
    requests_mock: RequestsMock, mocker: MockerFixture
) -> None:
    mocker.patch(
        "pipeline.extract.get_base_crud_api_url",
        return_value="http://test-crud-api",
    )

    mock_call = requests_mock.get(
        "http://test-crud-api/Organization/?identifier=odsOrganisationCode|XYZ999",
        json={
            "resourceType": "Bundle",
            "type": "searchset",
            "entry": [
                {"resource": {"resourceType": "Organization", "id": "BUNDLE_ORG_ID"}}
            ],
        },
    )
    result_bundle = fetch_organisation_uuid("XYZ999")
    assert result_bundle == "BUNDLE_ORG_ID"
    assert mock_call.called_once
    pipeUrlEncoding = "%7C"
    assert (
        mock_call.last_request.url
        == f"http://test-crud-api/Organization/?identifier=odsOrganisationCode{pipeUrlEncoding}XYZ999"
    )


def test_fetch_organisation_uuid_logs_and_raises_on_not_found(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    mocker.patch(
        "pipeline.extract.get_base_crud_api_url",
        return_value="http://test-crud-api",
    )

    class MockResponse:
        status_code = HTTPStatus.NOT_FOUND

    def raise_http_error_not_found(*args: object, **kwargs: object) -> None:
        http_err = HTTPError()
        http_err.response = MockResponse()
        raise http_err

    mocker.patch(
        "pipeline.extract.make_request", side_effect=raise_http_error_not_found
    )

    with caplog.at_level("WARNING"):
        with pytest.raises(ValueError) as excinfo:
            fetch_organisation_uuid("ABC123")
        assert str(excinfo.value) == "Organisation not found in database."

    assert "Organisation not found in database" in caplog.text


def test_fetch_organisation_uuid_logs_and_raises_on_bad_request(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    mocker.patch(
        "pipeline.extract.get_base_crud_api_url",
        return_value="http://test-crud-api",
    )

    class MockResponse:
        response = "Error"
        status_code = HTTPStatus.UNPROCESSABLE_ENTITY

    def raise_http_error_not_found(*args: object, **kwargs: object) -> Exception:
        http_err = HTTPError()
        http_err.response = MockResponse()
        raise http_err

    mocker.patch(
        "pipeline.extract.make_request", side_effect=raise_http_error_not_found
    )
    with caplog.at_level("ERROR"):
        with pytest.raises(HTTPError) as excinfo:
            fetch_organisation_uuid("ABC123")
        assert isinstance(excinfo.value, HTTPError)


def test_extract_ods_code() -> None:
    link = "https:///organisations/ABC123"
    result = extract_ods_code(link)
    assert result == "ABC123"


def test_extract_ods_code_failure(caplog: pytest.LogCaptureFixture) -> None:
    link = None
    with pytest.raises(Exception):
        extract_ods_code(link)
    assert "e=" in caplog.text or "ODS code extraction failed" in caplog.text
