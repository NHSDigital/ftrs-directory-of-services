import pytest
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
    assert mock_call.last_request.qs == {"Lastchangedate": [date]}


def test_fetch_ods_organisation_data(requests_mock: RequestsMock) -> None:
    mock_call = requests_mock.get(
        "https://directory.spineservices.nhs.uk/STU3/Organization/ABC123",
        json={"resourceType": "Organization", "id": "ABC123"},
    )

    ods_code = "ABC123"
    result = fetch_ods_organisation_data(ods_code)
    assert result == {"resourceType": "Organization", "id": "ABC123"}

    assert mock_call.called_once
    assert mock_call.last_request.path == "/stu3/organization/ABC123"


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
    assert mock_call.last_request.path == "/organisation/ods_code/ABC123"


def test_fetch_organisation_uuid_not_found(requests_mock: RequestsMock, monkeypatch):
    from requests.exceptions import HTTPError
    from http import HTTPStatus
    from pipeline import extract

    monkeypatch.setattr(
        extract, "get_base_crud_api_url", lambda: "http://test-crud-api"
    )

    class MockResponse:
        status_code = HTTPStatus.NOT_FOUND

    def raise_http_error(*args, **kwargs):
        err = HTTPError()
        err.response = MockResponse()
        raise err

    monkeypatch.setattr(extract, "make_request", lambda *a, **kw: raise_http_error())

    with pytest.raises(ValueError):
        fetch_organisation_uuid("ABC123")


def test_extract_ods_code() -> None:
    link = "https:///organisations/ABC123"
    result = extract_ods_code(link)
    assert result == "ABC123"


def test_extract_ods_code_failure(caplog: pytest.LogCaptureFixture) -> None:
    link = None
    with pytest.raises(Exception):
        extract_ods_code(link)
    assert "e=" in caplog.text or "ODS code extraction failed" in caplog.text
