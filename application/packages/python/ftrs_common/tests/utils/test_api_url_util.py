from unittest.mock import MagicMock, patch

import pytest
from ftrs_common.utils.api_url_util import get_api_url, get_fhir_url


@pytest.mark.parametrize(
    ("workspace", "expected"),
    [
        (
            "default",
            "https://servicesearch.dev.ftrs.cloud.nhs.uk",
        ),
        (
            None,
            "https://servicesearch.dev.ftrs.cloud.nhs.uk",
        ),
        (
            "dosis-123",
            "https://servicesearch-dosis-123.dev.ftrs.cloud.nhs.uk",
        ),
    ],
)
@patch("ftrs_common.utils.api_url_util._settings")
def test_get_api_url(
    mock_settings: MagicMock,
    workspace: str | None,
    expected: str,
) -> None:
    # Arrange
    mock_settings.workspace = workspace
    mock_settings.env = "dev"
    api_name = "servicesearch"

    # Act
    result = get_api_url(api_name)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    ("resource_id", "workspace", "expected"),
    [
        (
            None,
            None,
            "https://servicesearch.dev.ftrs.cloud.nhs.uk/FHIR/R4/Organization",
        ),
        (
            "00000000-0000-0000-0000-000000000000",  # gitleaks:allow
            None,
            "https://servicesearch.dev.ftrs.cloud.nhs.uk/FHIR/R4/Organization/00000000-0000-0000-0000-000000000000",  # gitleaks:allow
        ),
        (
            None,
            "dosis-123",
            "https://servicesearch-dosis-123.dev.ftrs.cloud.nhs.uk/FHIR/R4/Organization",
        ),
        (
            "00000000-0000-0000-0000-000000000000",  # gitleaks:allow
            "dosis-123",
            "https://servicesearch-dosis-123.dev.ftrs.cloud.nhs.uk/FHIR/R4/Organization/00000000-0000-0000-0000-000000000000",  # gitleaks:allow
        ),
    ],
)
@patch("ftrs_common.utils.api_url_util._settings")
def test_get_fhir_url(
    mock_settings: MagicMock,
    resource_id: str | None,
    workspace: str | None,
    expected: str,
) -> None:
    # Arrange
    mock_settings.workspace = workspace
    mock_settings.env = "dev"
    api_name = "servicesearch"
    resource_type = "Organization"

    # Act
    result = get_fhir_url(api_name, resource_type, resource_id)

    # Assert
    assert result == expected
