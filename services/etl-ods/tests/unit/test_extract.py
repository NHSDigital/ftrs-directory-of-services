import pytest
from pytest_mock import MockerFixture
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
    assert mock_call.last_request.qs == {"lastchangedate": [date]} # qs returns in lowercase


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


def test_fetch_organisation_uuid(requests_mock: RequestsMock, monkeypatch) -> None:
    # Patch get_base_crud_api_url to return a test URL
    from pipeline import extract

    monkeypatch.setattr(
        extract, "get_base_crud_api_url", lambda: "http://test-crud-api"
    )

    mock_call = requests_mock.get(
        "http://test-crud-api/organisation/ods_code/ABC123",
        json={"id": "UUID123"},
    )

    result = fetch_organisation_uuid("ABC123")
    assert result == "UUID123"

    assert mock_call.called_once
    assert (
        mock_call.last_request.url
        == "http://test-crud-api/organisation/ods_code/ABC123"
    )


def test_fetch_organisation_uuid_logs_and_raises_on_not_found(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
):
    from pipeline import extract
    from requests.exceptions import HTTPError
    from http import HTTPStatus

    # Patch get_base_crud_api_url to return a test URL
    mocker.patch("pipeline.extract.get_base_crud_api_url", return_value="http://test-crud-api")

    class MockResponse:
        status_code = HTTPStatus.NOT_FOUND

    http_err = HTTPError()
    http_err.response = MockResponse()

    def raise_http_error(*args, **kwargs):
        raise http_err

    mocker.patch("pipeline.extract.make_request", side_effect=raise_http_error)
    logger = mocker.patch("pipeline.extract.ods_processor_logger.log")

    with pytest.raises(ValueError) as excinfo:
        fetch_organisation_uuid("ABC123")

    calls = logger.call_args_list
    assert calls[0][0][0] == extract.OdsETLPipelineLogBase.ETL_PROCESSOR_028
    assert calls[0][1]["ods_code"] == "ABC123"
    assert calls[1][0][0] == extract.OdsETLPipelineLogBase.ETL_PROCESSOR_007
    assert extract.OdsETLPipelineLogBase.ETL_PROCESSOR_007.value.message in str(excinfo.value)


def test_fetch_organisation_uuid_logs_and_raises_on_bad_request(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
):
    from pipeline import extract
    from requests.exceptions import HTTPError
    from http import HTTPStatus

    # Patch get_base_crud_api_url to return a test URL
    mocker.patch(
        "pipeline.extract.get_base_crud_api_url", return_value="http://test-crud-api"
    )

    class MockResponse:
        status_code = HTTPStatus.BAD_REQUEST

    http_err = HTTPError()
    http_err.response = MockResponse()

    def raise_http_error(*args, **kwargs):
        raise http_err

    mocker.patch("pipeline.extract.make_request", side_effect=raise_http_error)
    logger = mocker.patch("pipeline.extract.ods_processor_logger.log")

    with pytest.raises(HTTPError):
        fetch_organisation_uuid("ABC123")

    calls = logger.call_args_list
    assert calls[0][0][0] == extract.OdsETLPipelineLogBase.ETL_PROCESSOR_028


def test_extract_ods_code() -> None:
    link = "https:///organisations/ABC123"
    result = extract_ods_code(link)
    assert result == "ABC123"


def test_extract_ods_code_failure(caplog: pytest.LogCaptureFixture) -> None:
    link = None
    with pytest.raises(Exception):
        extract_ods_code(link)
    assert "e=" in caplog.text or "ODS code extraction failed" in caplog.text
