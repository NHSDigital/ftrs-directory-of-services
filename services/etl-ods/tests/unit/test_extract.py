import pytest
from ftrs_data_layer.domain.enums import OrganisationTypeCode
from pytest_mock import MockerFixture

from extractor.extract import (
    _build_ods_query_params,
    _extract_next_page_url,
    _extract_organizations_from_bundle,
    _get_page_limit,
    fetch_outdated_organisations,
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
        "extractor.extract.ods_client.make_request", return_value=mock_bundle
    )

    date = "2025-10-15"
    result = fetch_outdated_organisations(date)

    assert str(len(result)) == "2"
    assert result[0]["id"] == "ABC123"
    assert result[1]["id"] == "XYZ789"

    expected_params = [
        ("_lastUpdated", date),
        ("_count", "1000"),
        ("roleCode", OrganisationTypeCode.PRESCRIBING_COST_CENTRE_CODE.value),
        ("roleCode", OrganisationTypeCode.GP_PRACTICE_ROLE_CODE.value),
    ]
    make_request_mock.assert_called_once_with(
        "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization",
        params=expected_params,
    )


def test_fetch_outdated_organisations_empty_results(
    caplog: pytest.LogCaptureFixture, mocker: MockerFixture
) -> None:
    """Test fetching organizations when no results found."""
    mocker.patch(
        "extractor.extract.ods_client.make_request",
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


def test_fetch_outdated_organisations_with_pagination(mocker: MockerFixture) -> None:
    """Test fetching organizations with pagination support."""
    # First page response
    first_page = {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 3,
        "status_code": 200,
        "link": [
            {
                "relation": "next",
                "url": "https://int.api.service.nhs.uk/organisation-data-terminology-api/fhir/Organization?_offset=2",
            }
        ],
        "entry": [
            {"resource": {"resourceType": "Organization", "id": "ABC123"}},
            {"resource": {"resourceType": "Organization", "id": "DEF456"}},
        ],
    }

    # Second page response (no next link)
    second_page = {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 1,
        "status_code": 200,
        "entry": [
            {"resource": {"resourceType": "Organization", "id": "GHI789"}},
        ],
    }
    EXPECTED_ORGANISATION_COUNT = 3
    EXPECTED_CALL_COUNT = 2

    make_request_mock = mocker.patch(
        "extractor.extract.ods_client.make_request",
        side_effect=[first_page, second_page],
    )

    date = "2025-10-15"
    result = fetch_outdated_organisations(date)

    assert len(result) == EXPECTED_ORGANISATION_COUNT
    assert result[0]["id"] == "ABC123"
    assert result[1]["id"] == "DEF456"
    assert result[2]["id"] == "GHI789"
    assert make_request_mock.call_count == EXPECTED_CALL_COUNT


def test_build_ods_query_params_includes_gp_practice_role_codes() -> None:
    """Test that role codes RO177 and RO76 are included for GP Practice filtering."""
    date = "2025-10-15"
    params = _build_ods_query_params(date)

    assert isinstance(params, list)

    role_code_params = [p for p in params if p[0] == "roleCode"]

    assert str(len(role_code_params)) == "2"
    assert (
        "roleCode",
        OrganisationTypeCode.PRESCRIBING_COST_CENTRE_CODE.value,
    ) in params
    assert ("roleCode", OrganisationTypeCode.GP_PRACTICE_ROLE_CODE.value) in params
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


@pytest.mark.parametrize(
    "env_value,expected_result,should_log",
    [
        ("50", 50, False),  # Valid env var
        ("invalid", 1000, True),  # Invalid env var
        ("0", 1000, True),  # Zero value
        (None, 1000, True),  # No env var set
    ],
)
def test_get_page_limit(
    mocker: MockerFixture, env_value: str | None, expected_result: int, should_log: bool
) -> None:
    """Test _get_page_limit with various environment variable values."""
    if env_value is None:
        mocker.patch.dict("os.environ", {}, clear=True)
    else:
        mocker.patch.dict("os.environ", {"ODS_API_PAGE_LIMIT": env_value})

    mock_logger = mocker.patch("extractor.extract.ods_extractor_logger.log")

    result = _get_page_limit()

    assert result == expected_result

    if should_log:
        mock_logger.assert_called_once()
    else:
        mock_logger.assert_not_called()


def test_extract_next_page_url_success() -> None:
    """Test _extract_next_page_url extracts next page URL."""
    bundle = {
        "resourceType": "Bundle",
        "link": [
            {"relation": "self", "url": "http://example.com/current"},
            {"relation": "next", "url": "http://example.com/next"},
        ],
    }

    result = _extract_next_page_url(bundle)

    assert result == "http://example.com/next"


def test_extract_next_page_url_no_next_link() -> None:
    """Test _extract_next_page_url returns None when no next link."""
    bundle = {
        "resourceType": "Bundle",
        "link": [
            {"relation": "self", "url": "http://example.com/current"},
        ],
    }

    result = _extract_next_page_url(bundle)

    assert result is None


def test_extract_next_page_url_non_bundle() -> None:
    """Test _extract_next_page_url returns None for non-Bundle."""
    non_bundle = {"resourceType": "Organization", "id": "123"}

    result = _extract_next_page_url(non_bundle)

    assert result is None


def test_extract_next_page_url_no_links() -> None:
    """Test _extract_next_page_url returns None when no links."""
    bundle = {"resourceType": "Bundle"}

    result = _extract_next_page_url(bundle)

    assert result is None
