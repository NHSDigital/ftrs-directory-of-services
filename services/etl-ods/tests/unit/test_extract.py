from http import HTTPStatus

import pytest
from pytest_mock import MockerFixture
from requests import HTTPError

from pipeline.extract import (
    _extract_organizations_from_bundle,
    fetch_organisation_uuid,
    fetch_outdated_organisations,
    validate_ods_code,
)


def test_fetch_outdated_organisations_success(mocker: MockerFixture) -> None:
    """Test successful fetching of outdated organizations."""
    mock_bundle = {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 2,
        "status_code": 200,
        "entry": [
            {
                "resource": {
                    "resourceType": "Organization",
                    "id": "ABC123",
                    "identifier": [
                        {
                            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                            "value": "ABC123",
                        }
                    ],
                }
            },
            {
                "resource": {
                    "resourceType": "Organization",
                    "id": "XYZ789",
                    "identifier": [
                        {
                            "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                            "value": "XYZ789",
                        }
                    ],
                }
            },
        ],
    }

    make_request_mock = mocker.patch(
        "pipeline.extract.make_request", return_value=mock_bundle
    )

    date = "2025-10-15"
    result = fetch_outdated_organisations(date)

    assert str(len(result)) == "2"
    assert result[0]["id"] == "ABC123"
    assert result[1]["id"] == "XYZ789"
    make_request_mock.assert_called_once_with(
        "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization",
        params={"_lastUpdated": date},
    )


def test_fetch_outdated_organisations_empty_results(
    caplog: pytest.LogCaptureFixture, mocker: MockerFixture
) -> None:
    """Test fetching organizations when no results found."""
    mocker.patch(
        "pipeline.extract.make_request",
        return_value={
            "resourceType": "Bundle",
            "type": "searchset",
            "total": 0,
            "status_code": 200,
            "link": [
                {
                    "relation": "self",
                    "url": "https://api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization?_lastUpdated=2025-10-15",
                }
            ],
        },
    )

    date = "2025-10-15"
    with caplog.at_level("INFO"):
        result = fetch_outdated_organisations(date)

    assert result == []
    assert "No organisations found for the given date" in caplog.text


def test_fetch_organisation_uuid(mocker: MockerFixture) -> None:
    """Test fetching organisation UUID from APIM."""
    mocker.patch(
        "pipeline.extract.get_base_apim_api_url",
        return_value="http://apim-proxy",
    )

    mock_response = {
        "resourceType": "Bundle",
        "type": "searchset",
        "status_code": 200,
        "entry": [
            {"resource": {"resourceType": "Organization", "id": "BUNDLE_ORG_ID"}}
        ],
    }
    make_request_mock = mocker.patch(
        "pipeline.extract.make_request", return_value=mock_response
    )

    result_bundle = fetch_organisation_uuid("XYZ999")

    assert result_bundle == "BUNDLE_ORG_ID"
    make_request_mock.assert_called_once_with(
        "http://apim-proxy/Organization?identifier=odsOrganisationCode|XYZ999",
        method="GET",
    )


def test_fetch_organisation_uuid_logs_and_raises_on_not_found(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    mocker.patch(
        "pipeline.extract.get_base_apim_api_url",
        return_value="http://apim-proxy",
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
        "pipeline.extract.get_base_apim_api_url",
        return_value="http://apim-proxy",
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


def test_fetch_organisation_uuid_invalid_resource_returned(
    mocker: MockerFixture, caplog: pytest.LogCaptureFixture
) -> None:
    """Test fetch_organisation_uuid handles invalid resource type."""
    mocker.patch(
        "pipeline.extract.get_base_apim_api_url",
        return_value="http://apim-proxy",
    )
    mocker.patch(
        "pipeline.extract.make_request",
        return_value={
            "resourceType": "Not Bundle",
            "status_code": 200,
        },
    )

    with caplog.at_level("WARNING"):
        with pytest.raises(ValueError) as excinfo:
            fetch_organisation_uuid("XYZ999")
        assert (
            "Fetching organisation uuid for ods code XYZ999 failed, resource type Not Bundle returned"
            in caplog.text
        )
        assert "Organisation not found in database" in str(excinfo.value)


def test_fetch_organisation_uuid_no_organisation_returned(
    mocker: MockerFixture,
) -> None:
    """Test fetch_organisation_uuid returns None when no Organization found in Bundle."""
    mocker.patch(
        "pipeline.extract.get_base_apim_api_url",
        return_value="http://apim-proxy",
    )
    mocker.patch(
        "pipeline.extract.make_request",
        return_value={
            "resourceType": "Bundle",
            "status_code": 200,
            "entry": [{"resource": {"resourceType": "ABC", "id": "BUNDLE_ORG_ID"}}],
        },
    )

    result = fetch_organisation_uuid("XYZ999")
    assert result is None


@pytest.mark.parametrize(
    "ods_code,should_pass",
    [
        ("ABC12", True),
        ("ABC123", True),
        ("ABC123456789", True),
        ("12345", True),
        ("ABC", False),  # Too short
        ("ABC1234567890", False),  # Too long
        ("ABC-123", False),  # Invalid characters
        (123456, False),  # Not a string
    ],
)
def test_validate_ods_code(ods_code: str, should_pass: bool) -> None:
    """Test ODS code validation with various inputs."""
    if should_pass:
        validate_ods_code(ods_code)  # Should not raise
    else:
        with pytest.raises(ValueError) as excinfo:
            validate_ods_code(ods_code)
        assert "must match" in str(excinfo.value)


def test__extract_organizations_from_bundle_with_missing_resource() -> None:
    """Test _extract_organizations_from_bundle handles entries without resource field."""
    bundle = {
        "resourceType": "Bundle",
        "entry": [
            {"resource": {"resourceType": "Organization", "id": "org1"}},
            {},  # Entry without resource field
            {"resource": None},  # Entry with None resource
            {
                "resource": {"resourceType": "Patient", "id": "patient1"}
            },  # Different resource type
            {"resource": {"resourceType": "Organization", "id": "org2"}},
        ],
    }

    organizations = _extract_organizations_from_bundle(bundle)

    assert str(len(organizations)) == "2"
    assert organizations[0]["id"] == "org1"
    assert organizations[1]["id"] == "org2"


def test__extract_organizations_from_bundle_non_bundle() -> None:
    """Test _extract_organizations_from_bundle returns empty list for non-Bundle."""
    non_bundle = {"resourceType": "Patient", "id": "123"}

    organizations = _extract_organizations_from_bundle(non_bundle)

    assert organizations == []
