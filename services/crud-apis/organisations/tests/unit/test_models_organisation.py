import pytest
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from pydantic import ValidationError

from organisations.app.models.organisation import OrganisationUpdatePayload

# Test constants
TEST_INSTANCE_ID = 12345


def _build_base_payload() -> dict:
    return {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": [
                "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Organization"
            ]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organisation",
        "active": False,
        "telecom": [{"system": "phone", "value": "0123456789", "use": "work"}],
    }


def _build_date_type_extension(
    date_type: str,
    include_value_coding: bool = True,
    date_type_system: str
    | None = "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
) -> dict:
    """Build a dateType sub-extension for TypedPeriod."""
    date_type_ext = {"url": "dateType"}
    if include_value_coding:
        date_type_ext["valueCoding"] = {"code": date_type}
        if date_type_system is not None:
            date_type_ext["valueCoding"]["system"] = date_type_system
    return date_type_ext


def _build_period_extension(
    start: str | None,
    end: str | None,
    include_value_period: bool = True,
) -> dict:
    """Build a period sub-extension for TypedPeriod."""
    period_ext = {"url": "period"}
    if include_value_period:
        period_ext["valuePeriod"] = {}
        if start is not None:
            period_ext["valuePeriod"]["start"] = start
        if end is not None:
            period_ext["valuePeriod"]["end"] = end
    return period_ext


def _build_typed_period_extension(
    date_type: str = "Legal",
    start: str | None = "2020-01-15",
    end: str | None = None,
    url: str
    | None = "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
) -> dict:
    """Helper to build a TypedPeriod extension.

    Args:
        date_type: "Legal" or "Operational"
        start: Start date in YYYY-MM-DD format or None
        end: End date in YYYY-MM-DD format or None
        url: URL for TypedPeriod extension (None to omit, "" for empty string)
    """
    extension = {}

    # Add URL if provided
    if url is not None:
        extension["url"] = url

    # Add extension array
    extension["extension"] = []

    # Add dateType sub-extension
    extension["extension"].append(_build_date_type_extension(date_type))

    # Add period sub-extension
    extension["extension"].append(_build_period_extension(start, end))

    return extension


def _build_role_code_extension(
    role_code: str = "RO76",
    include_value_codeable_concept: bool = True,
    include_coding_array: bool = True,
    role_code_value_codeable_concept: dict | None = None,
) -> dict:
    """Helper to build a roleCode extension.

    Args:
        role_code: Role code value (e.g., "RO76")
        include_value_codeable_concept: Whether to include valueCodeableConcept
        include_coding_array: Whether to include coding array in valueCodeableConcept
        role_code_value_codeable_concept: Custom roleCode valueCodeableConcept dict
    """
    if role_code_value_codeable_concept is not None:
        return {
            "url": "roleCode",
            "valueCodeableConcept": role_code_value_codeable_concept,
        }

    if not include_value_codeable_concept:
        return {"url": "roleCode"}

    role_code_ext = {"url": "roleCode"}
    if include_coding_array:
        role_code_ext["valueCodeableConcept"] = {
            "coding": [
                {
                    "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                    "code": role_code,
                    "display": "GP PRACTICE",
                }
            ]
        }
    else:
        role_code_ext["valueCodeableConcept"] = {"coding": []}

    return role_code_ext


def _build_organisation_role_extension(
    role_code: str = "RO182",
    typed_periods: list[dict] | None = None,
    url: str
    | None = "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
    primary_role: bool | None = None,
) -> dict:
    """Helper to build an OrganisationRole extension with TypedPeriod(s).

    Args:
        role_code: Role code value, defaults to RO182
        typed_periods: List of TypedPeriod extension dicts (None for default)
        url: URL for OrganisationRole extension (None to omit, "" for empty string)
    """
    extension = {}

    # Add URL if provided
    if url is not None:
        extension["url"] = url

    # Add extension array
    extension["extension"] = []

    # Add instanceID (always included)
    extension["extension"].append(
        {"url": "instanceID", "valueInteger": TEST_INSTANCE_ID}
    )

    # Add role code
    role_code_ext = _build_role_code_extension(role_code=role_code)
    extension["extension"].append(role_code_ext)

    # Add typed periods
    if typed_periods is None:
        # Default: add one Legal typed period with start date
        extension["extension"].append(_build_typed_period_extension())
    else:
        extension["extension"].extend(typed_periods)

    return extension


def test_valid_payload() -> None:
    payload = _build_base_payload()
    organisation = OrganisationUpdatePayload(**payload)
    assert organisation.name == "Test Organisation"
    assert organisation.active is False
    assert organisation.telecom[0].value == "0123456789"
    assert organisation.identifier[0].value == "ABC123"


def test_field_too_long_name() -> None:
    payload = _build_base_payload()
    payload["name"] = "a" * 1000
    with pytest.raises(ValidationError) as e:
        OrganisationUpdatePayload(**payload)
    assert "String should have at most" in str(e.value)


def test_missing_required_field() -> None:
    payload = _build_base_payload()
    # Remove identifier which is required
    del payload["identifier"]
    with pytest.raises(ValidationError) as e:
        OrganisationUpdatePayload(**payload)
    assert "Field required" in str(e.value)


def test_additional_field() -> None:
    payload = _build_base_payload()
    payload["extra"] = "value"
    with pytest.raises(ValidationError) as e:
        OrganisationUpdatePayload(**payload)
    assert "Extra inputs are not permitted" in str(e.value)


def test_active_field_null_fails() -> None:
    """Test that active field with null value fails validation."""
    payload = _build_base_payload()
    payload["active"] = None
    with pytest.raises(ValidationError) as e:
        OrganisationUpdatePayload(**payload)
    assert "Active field is required and cannot be null" in str(e.value)


# Tests for legal date extension validation


def test_valid_typed_period_extension_with_both_dates() -> None:
    """Test valid TypedPeriod extension with both start and end dates within OrganisationRole."""
    payload = _build_base_payload()

    primary_role = _build_organisation_role_extension(
        role_code="RO177",
        typed_periods=[
            _build_typed_period_extension(start="2020-01-15", end="2025-12-31")
        ],
    )
    non_primary_role = _build_organisation_role_extension(
        role_code="RO76",
        typed_periods=[_build_typed_period_extension(start="2014-04-15", end=None)],
    )
    payload["extension"] = [primary_role, non_primary_role]

    organisation = OrganisationUpdatePayload(**payload)
    assert organisation.extension is not None
    assert str(len(organisation.extension)) == "2"

    role_ext = organisation.extension[0]
    assert (
        role_ext.url
        == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole"
    )

    # Find the TypedPeriod extension within the role extension
    typed_period_ext = next(
        (
            ext
            for ext in role_ext.extension
            if ext.url
            == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod"
        ),
        None,
    )
    assert typed_period_ext is not None
    assert (
        typed_period_ext.url
        == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod"
    )
    # Check sub-extensions
    sub_exts = {e.url: e for e in typed_period_ext.extension}
    assert "dateType" in sub_exts
    assert "period" in sub_exts
    date_type_ext = sub_exts["dateType"]
    period_ext = sub_exts["period"]
    assert date_type_ext.valueCoding.code == "Legal"
    assert (
        date_type_ext.valueCoding.system
        == "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType"
    )
    assert period_ext.valuePeriod.start == "2020-01-15"
    assert period_ext.valuePeriod.end == "2025-12-31"


def test_valid_typed_period_extension_with_start_only() -> None:
    """Test valid TypedPeriod extension with only start date within OrganisationRole."""
    payload = _build_base_payload()

    primary_role = _build_organisation_role_extension(role_code="RO177")
    non_primary_role = _build_organisation_role_extension(role_code="RO76")
    payload["extension"] = [primary_role, non_primary_role]

    organisation = OrganisationUpdatePayload(**payload)
    role_ext = organisation.extension[0]

    # Find the TypedPeriod extension within the role extension
    typed_period_ext = next(
        (
            ext
            for ext in role_ext.extension
            if ext.url
            == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod"
        ),
        None,
    )
    assert typed_period_ext is not None

    sub_exts = {e.url: e for e in typed_period_ext.extension}
    period_ext = sub_exts["period"]
    assert period_ext.valuePeriod.start == "2020-01-15"
    assert period_ext.valuePeriod.end is None


def test_invalid_typed_period_extension_with_end_only() -> None:
    """Test that TypedPeriod extension with only end date within OrganisationRole fails validation for Legal periods but passes for Operational."""
    payload = _build_base_payload()
    typed_period = _build_typed_period_extension(
        date_type="Legal", start=None, end="2025-12-31"
    )
    payload["extension"] = [
        _build_organisation_role_extension(
            role_code="RO182", typed_periods=[typed_period]
        )
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert (
        "Legal period start date is required when TypedPeriod extension is present"
        in str(e.value)
    )


def test_invalid_typed_period_extension_with_no_dates() -> None:
    """Test that TypedPeriod extension with no dates fails validation."""
    payload = _build_base_payload()
    typed_period = _build_typed_period_extension(
        date_type="Legal", start=None, end=None
    )
    payload["extension"] = [
        _build_organisation_role_extension(
            role_code="RO182", typed_periods=[typed_period]
        )
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert (
        "Legal period start date is required when TypedPeriod extension is present"
        in str(e.value)
    )


def test_typed_period_equal_dates_legal() -> None:
    """Test that Legal periods with equal start/end dates fail."""
    payload = _build_base_payload()
    typed_period = _build_typed_period_extension(
        date_type="Legal", start="2022-01-01", end="2022-01-01"
    )
    payload["extension"] = [
        _build_organisation_role_extension(
            role_code="RO182", typed_periods=[typed_period]
        )
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "Legal period start and end dates must not be equal" in str(e.value)


def test_invalid_sub_extension() -> None:
    """Test validation fails when TypedPeriod extension in OrganisationRole has invalid sub extension."""
    payload = _build_base_payload()
    # Manually create TypedPeriod without extension array
    typed_period = {
        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod"
    }
    payload["extension"] = [
        _build_organisation_role_extension(
            role_code="RO182", typed_periods=[typed_period]
        )
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert (
        "TypedPeriod extension with URL 'https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod' must include a nested 'extension' array with 'dateType' and 'period' fields"
        in str(e.value)
    )


def test_invalid_extension_url() -> None:
    """Test validation fails with invalid top-level extension URL."""
    payload = _build_base_payload()
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/invalid-extension",
            "extension": [{"url": "instanceID", "valueInteger": 12345}],
        }
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "Invalid extension URL" in str(e.value)


def test_null_extension_is_valid() -> None:
    """Test that null/missing extension field is valid."""
    payload = _build_base_payload()
    organisation = OrganisationUpdatePayload(**payload)
    assert organisation.extension is None


@pytest.mark.parametrize(
    "invalid_date",
    [
        "2020-13-45",  # Invalid month and day
        "20-01-2020",  # Wrong format (YY-MM-YYYY)
        "2020/01/15",  # Wrong separator
        "2020-1-5",  # Missing zero padding
        "15-01-2020",  # DD-MM-YYYY instead of YYYY-MM-DD
        "invalid",  # Completely invalid
    ],
)
def test_invalid_date_format_in_legal_start_date(invalid_date: str) -> None:
    """Test validation fails when legal start date has invalid format in TypedPeriod within OrganisationRole."""
    payload = _build_base_payload()
    typed_period = _build_typed_period_extension(
        date_type="Legal", start=invalid_date, end="2025-12-31"
    )
    payload["extension"] = [
        _build_organisation_role_extension(
            role_code="RO182", typed_periods=[typed_period]
        )
    ]

    with pytest.raises(ValidationError) as exc_info:
        OrganisationUpdatePayload(**payload)

    assert (
        "datetime" in str(exc_info.value).lower()
        or "date" in str(exc_info.value).lower()
    ), f"Expected validation error for start date: {invalid_date}"


@pytest.mark.parametrize(
    "invalid_date",
    [
        "2025-13-45",  # Invalid month and day
        "25-12-2025",  # Wrong format (YY-MM-YYYY)
        "2025/12/31",  # Wrong separator
        "2025-12-1",  # Missing zero padding
        "31-12-2025",  # DD-MM-YYYY instead of YYYY-MM-DD
    ],
)
def test_invalid_date_format_in_legal_end_date(invalid_date: str) -> None:
    """Test validation fails when legal end date has invalid format in TypedPeriod within OrganisationRole."""
    payload = _build_base_payload()
    typed_period = _build_typed_period_extension(
        date_type="Legal", start="2020-01-15", end=invalid_date
    )
    payload["extension"] = [
        _build_organisation_role_extension(
            role_code="RO182", typed_periods=[typed_period]
        )
    ]

    with pytest.raises(ValidationError) as exc_info:
        OrganisationUpdatePayload(**payload)

    assert (
        "datetime" in str(exc_info.value).lower()
        or "date" in str(exc_info.value).lower()
    ), f"Expected validation error for end date: {invalid_date}"


@pytest.mark.parametrize(
    "start_date,end_date",
    [
        ("2020-01-01", "2025-12-31"),  # Standard dates
        ("2020-02-29", "2024-02-29"),  # Leap year dates
        ("2020-01-15", "2025-12-31"),  # Original test dates
    ],
)
def test_valid_date_formats_accepted(start_date: str, end_date: str) -> None:
    """Test that properly formatted YYYY-MM-DD dates are accepted in TypedPeriod within OrganisationRole."""
    payload = _build_base_payload()
    typed_period = _build_typed_period_extension(
        date_type="Legal", start=start_date, end=end_date
    )

    primary_role = _build_organisation_role_extension(
        role_code="RO177", typed_periods=[typed_period]
    )
    non_primary_role = _build_organisation_role_extension(role_code="RO76")
    payload["extension"] = [primary_role, non_primary_role]

    organisation = OrganisationUpdatePayload(**payload)
    assert organisation.extension is not None, (
        f"Valid dates {start_date} to {end_date} should be accepted"
    )


def test_valid_organisation_role_extension_with_typed_period() -> None:
    """Test valid OrganisationRole extension containing a TypedPeriod extension."""
    payload = _build_base_payload()
    typed_period = _build_typed_period_extension(
        date_type="Legal", start="2020-01-15", end="2025-12-31"
    )

    primary_role = _build_organisation_role_extension(
        role_code="RO177", typed_periods=[typed_period]
    )
    non_primary_role = _build_organisation_role_extension(role_code="RO76")
    payload["extension"] = [primary_role, non_primary_role]

    organisation = OrganisationUpdatePayload(**payload)
    assert str(len(organisation.extension)) == "2"

    role_ext = organisation.extension[0]
    assert (
        role_ext.url
        == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole"
    )

    # Find the TypedPeriod extension within the role extension
    typed_period_ext = next(
        (
            ext
            for ext in role_ext.extension
            if ext.url
            == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod"
        ),
        None,
    )
    assert typed_period_ext is not None

    sub_exts = {e.url: e for e in typed_period_ext.extension}
    assert "dateType" in sub_exts
    assert "period" in sub_exts
    assert sub_exts["dateType"].valueCoding.code == "Legal"
    assert sub_exts["period"].valuePeriod.start == "2020-01-15"
    assert sub_exts["period"].valuePeriod.end == "2025-12-31"


def test_valid_organisation_role_extension_with_multiple_typed_periods() -> None:
    """Test valid OrganisationRole extension containing multiple TypedPeriod extensions - validates Legal but accepts Operational."""
    payload = _build_base_payload()
    legal_period = _build_typed_period_extension(
        date_type="Legal", start="2020-01-15", end="2022-12-31"
    )
    operational_period = _build_typed_period_extension(
        date_type="Operational", start=None, end="2025-12-31"
    )

    primary_role = _build_organisation_role_extension(
        role_code="RO177", typed_periods=[legal_period, operational_period]
    )
    non_primary_role = _build_organisation_role_extension(role_code="RO76")
    payload["extension"] = [primary_role, non_primary_role]

    # Should pass because Legal period is valid and Operational period is not validated
    organisation = OrganisationUpdatePayload(**payload)
    role_ext = organisation.extension[0]

    # Find the first TypedPeriod extension within the role extension
    first_typed_period_ext = next(
        (
            ext
            for ext in role_ext.extension
            if ext.url
            == "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod"
        ),
        None,
    )
    assert first_typed_period_ext is not None

    # Validate the first TypedPeriod extension structure
    sub_exts = {e.url: e for e in first_typed_period_ext.extension}
    assert "dateType" in sub_exts
    assert "period" in sub_exts
    assert sub_exts["dateType"].valueCoding.code == "Legal"  # First one should be Legal
    assert sub_exts["period"].valuePeriod.start == "2020-01-15"


def test_invalid_organisation_role_extension_empty_extension_array() -> None:
    """Test OrganisationRole extension with empty extension array fails validation."""
    payload = _build_base_payload()
    # Manually create an extension with truly empty array (no instanceID, nothing)
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
            "extension": [],
        }
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "must include a nested 'extension' array" in str(e.value)


def test_invalid_organisation_role_extension_missing_extension_array() -> None:
    """Test OrganisationRole extension without extension array fails validation."""
    payload = _build_base_payload()
    # Manually create OrganisationRole without extension array
    payload["extension"] = [
        {
            "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole"
        }
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "OrganisationRole extension" in str(e.value)
    assert "must include a nested 'extension' array" in str(e.value)


def test_invalid_typed_period_in_organisation_role_missing_date_type() -> None:
    """Test TypedPeriod extension within OrganisationRole with missing dateType fails."""
    payload = _build_base_payload()
    # Manually create TypedPeriod without dateType
    typed_period = {
        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
        "extension": [
            {
                "url": "period",
                "valuePeriod": {"start": "2020-01-15"},
            }
        ],
    }
    payload["extension"] = [
        _build_organisation_role_extension(
            role_code="RO182", typed_periods=[typed_period]
        )
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "TypedPeriod extension must contain dateType and period" in str(e.value)


def test_date_type_missing_value_coding() -> None:
    """Test TypedPeriod with dateType missing valueCoding."""
    payload = _build_base_payload()
    # Manually create TypedPeriod with dateType missing valueCoding
    typed_period = {
        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
        "extension": [
            {"url": "dateType"},
            {
                "url": "period",
                "valuePeriod": {"start": "2020-01-15"},
            },
        ],
    }
    payload["extension"] = [
        _build_organisation_role_extension(
            role_code="RO182", typed_periods=[typed_period]
        )
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "dateType must have a valueCoding" in str(e.value)


def test_invalid_typed_period_in_organisation_role_invalid_system() -> None:
    """Test TypedPeriod extension within OrganisationRole with invalid system fails."""
    payload = _build_base_payload()
    # Manually create TypedPeriod with invalid system URL
    typed_period = {
        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
        "extension": [
            {
                "url": "dateType",
                "valueCoding": {
                    "system": "https://invalid.system.url",
                    "code": "Legal",
                },
            },
            {
                "url": "period",
                "valuePeriod": {"start": "2020-01-15"},
            },
        ],
    }
    payload["extension"] = [
        _build_organisation_role_extension(
            role_code="RO182", typed_periods=[typed_period]
        )
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert (
        "dateType system must be 'https://fhir.nhs.uk/England/CodeSystem/England-PeriodType'"
        in str(e.value)
    )


def test_no_role_extension() -> None:
    """Test unknown extension URL fails validation."""
    payload = _build_base_payload()
    # Manually create extension with invalid URL and no roleCode
    payload["extension"] = [
        {
            "url": "https://invalid.extension.url",
            "extension": [{"url": "instanceID", "valueInteger": TEST_INSTANCE_ID}],
        }
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "Invalid extension URL: https://invalid.extension.url" in str(e.value)


def test_organisation_role_with_no_typed_periods_fails_validation() -> None:
    """Test OrganisationRole extension without TypedPeriod extensions fails validation."""
    payload = _build_base_payload()
    payload["extension"] = [
        _build_organisation_role_extension(role_code="RO76", typed_periods=[])
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert (
        "OrganisationRole extension must contain at least one TypedPeriod extension"
        in str(e.value)
    )


def test_invalid_organisation_role_extension_url() -> None:
    """Test validation fails with an invalid OrganisationRole extension URL."""
    payload = _build_base_payload()
    payload["extension"] = [
        _build_organisation_role_extension(
            url="https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole-INVALID"
        )
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "Invalid extension URL" in str(e.value)
    assert "OrganisationRole-INVALID" in str(e.value)


def test_missing_organisation_role_extension_url() -> None:
    """Test validation fails when OrganisationRole extension is missing the URL field."""
    payload = _build_base_payload()
    # Manually create extension with invalid URL
    payload["extension"] = [
        {
            "url": "Invalid",
            "extension": [{"url": "instanceID", "valueInteger": TEST_INSTANCE_ID}],
        }
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "Invalid extension URL" in str(e.value)


def test_empty_organisation_role_extension_url() -> None:
    """Test validation fails when OrganisationRole extension has empty string URL field."""
    payload = _build_base_payload()
    payload["extension"] = [_build_organisation_role_extension(url="")]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "Extension URL must be present and cannot be empty or None" in str(e.value)


def test_invalid_typed_period_extension_url_in_organisation_role() -> None:
    """Test validation fails when TypedPeriod extension has invalid URL within OrganisationRole."""
    payload = _build_base_payload()
    typed_period = _build_typed_period_extension(
        url="https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod-Invalid",
        start="2020-01-15",
        end="2025-12-31",
    )
    payload["extension"] = [
        _build_organisation_role_extension(
            role_code="RO76", typed_periods=[typed_period]
        )
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "Invalid extension URL" in str(e.value)


def test_missing_typed_period_extension_url_in_organisation_role() -> None:
    """Test validation fails when TypedPeriod extension is missing URL within OrganisationRole."""
    payload = _build_base_payload()
    typed_period = _build_typed_period_extension(
        url=None, start="2020-01-15", end="2025-12-31"
    )
    payload["extension"] = [
        _build_organisation_role_extension(
            role_code="RO76", typed_periods=[typed_period]
        )
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert (
        "OrganisationRole extension must contain at least one TypedPeriod extension"
        in str(e.value)
    )


def test_empty_typed_period_extension_url_in_organisation_role() -> None:
    """Test validation fails when TypedPeriod extension has empty string URL within OrganisationRole."""
    payload = _build_base_payload()
    typed_period = _build_typed_period_extension(
        url="", start="2020-01-15", end="2025-12-31"
    )
    payload["extension"] = [
        _build_organisation_role_extension(
            role_code="RO76", typed_periods=[typed_period]
        )
    ]
    with pytest.raises(OperationOutcomeException) as exc_info:
        OrganisationUpdatePayload(**payload)
    assert (
        "OrganisationRole extension must contain at least one TypedPeriod extension"
        in str(exc_info.value)
    )


def test_organisation_role_missing_role_code_extension() -> None:
    """Test OrganisationRole extension without roleCode extension fails validation."""
    payload = _build_base_payload()
    payload["active"] = True

    # Manually create an extension with instanceID and TypedPeriod but NO roleCode
    typed_period = _build_typed_period_extension(
        date_type="Legal", start="2020-01-15", end=None
    )
    role_extension = {
        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
        "extension": [
            {"url": "instanceID", "valueInteger": TEST_INSTANCE_ID},
            typed_period,
        ],
    }
    payload["extension"] = [role_extension]

    with pytest.raises(OperationOutcomeException) as exc_info:
        OrganisationUpdatePayload(**payload)

    assert (
        "OrganisationRole extension must contain at least one roleCode extension"
        in str(exc_info.value)
    )


def test_role_code_missing_value_codeable_concept() -> None:
    """Test payload with roleCode extension missing valueCodeableConcept."""
    payload = _build_base_payload()
    payload["active"] = True

    # Manually create a roleCode extension without valueCodeableConcept
    typed_period = _build_typed_period_extension(
        date_type="Legal", start="2020-01-15", end=None
    )
    role_extension = {
        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
        "extension": [
            {"url": "instanceID", "valueInteger": TEST_INSTANCE_ID},
            {
                "url": "roleCode",
                # No valueCodeableConcept
            },
            typed_period,
        ],
    }
    payload["extension"] = [role_extension]

    with pytest.raises(OperationOutcomeException) as exc_info:
        OrganisationUpdatePayload(**payload)

    assert "roleCode must have a valueCodeableConcept" in str(exc_info.value)


def test_role_code_missing_coding_array() -> None:
    """Test payload with roleCode missing coding array."""
    payload = _build_base_payload()
    payload["active"] = True

    # Manually create a roleCode with valueCodeableConcept but empty coding array
    typed_period = _build_typed_period_extension(
        date_type="Legal", start="2020-01-15", end=None
    )
    role_extension = {
        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
        "extension": [
            {"url": "instanceID", "valueInteger": TEST_INSTANCE_ID},
            {
                "url": "roleCode",
                "valueCodeableConcept": {
                    "coding": []  # Empty coding array
                },
            },
            typed_period,
        ],
    }
    payload["extension"] = [role_extension]

    with pytest.raises(OperationOutcomeException) as exc_info:
        OrganisationUpdatePayload(**payload)

    assert "roleCode valueCodeableConcept must contain at least one coding" in str(
        exc_info.value
    )


def test_role_code_empty_code_value() -> None:
    """Test payload with roleCode having empty code value."""
    payload = _build_base_payload()

    typed_period = _build_typed_period_extension(
        date_type="Legal", start="2020-01-15", end=None
    )

    role_extension = {
        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-OrganisationRole",
        "extension": [
            {"url": "instanceID", "valueInteger": TEST_INSTANCE_ID},
            {
                "url": "roleCode",
                "valueCodeableConcept": {
                    "coding": [
                        {
                            "system": "https://digital.nhs.uk/services/organisation-data-service/CodeSystem/ODSOrganisationRole",
                            "code": None,  # None value to test line 278
                        }
                    ]
                },
            },
            typed_period,
        ],
    }
    payload["extension"] = [role_extension]

    with pytest.raises(OperationOutcomeException) as exc_info:
        OrganisationUpdatePayload(**payload)

    assert "roleCode coding must have a code value" in str(exc_info.value)


def test_valid_payload_with_primary_role_code() -> None:
    """Test payload with primary role code extension."""
    payload = _build_base_payload()

    typed_period = _build_typed_period_extension(
        date_type="Legal", start="2020-01-15", end=None
    )

    primary_role = _build_organisation_role_extension(
        role_code="RO177", typed_periods=[typed_period]
    )
    non_primary_role = _build_organisation_role_extension(role_code="RO76")
    payload["extension"] = [primary_role, non_primary_role]

    organisation = OrganisationUpdatePayload(**payload)
    assert organisation.name == "Test Organisation"
    assert organisation.extension is not None
    assert str(len(organisation.extension)) == "2"


def test_valid_payload_with_primary_and_non_primary_role_codes() -> None:
    """Test payload with both primary and non-primary role codes."""
    payload = _build_base_payload()

    primary_period = _build_typed_period_extension(
        date_type="Legal", start="2020-01-15", end=None
    )
    primary_role = _build_organisation_role_extension(
        role_code="RO177", typed_periods=[primary_period]
    )

    # Only RO76 is allowed as non-primary for RO177
    non_primary_period_1 = _build_typed_period_extension(
        date_type="Legal", start="2014-04-15", end=None
    )
    non_primary_role_1 = _build_organisation_role_extension(
        role_code="RO76", typed_periods=[non_primary_period_1]
    )

    payload["extension"] = [primary_role, non_primary_role_1]

    organisation = OrganisationUpdatePayload(**payload)
    assert organisation.name == "Test Organisation"
    assert organisation.extension is not None
    assert str(len(organisation.extension)) == "2"


def test_invalid_role_code_not_in_enum() -> None:
    """Test payload with role code that is not a valid OrganisationTypeCode enum value."""
    payload = _build_base_payload()

    typed_period = _build_typed_period_extension(
        date_type="Legal", start="2020-01-15", end=None
    )
    role_extension = _build_organisation_role_extension(
        role_code="INVALID_CODE", typed_periods=[typed_period], primary_role=True
    )
    payload["extension"] = [role_extension]

    with pytest.raises(OperationOutcomeException) as exc_info:
        OrganisationUpdatePayload(**payload)

    assert "Invalid role code: 'INVALID_CODE'" in str(exc_info.value)


def test_valid_payload_with_no_role_codes() -> None:
    """Test payload without any role code extensions."""
    payload = _build_base_payload()

    organisation = OrganisationUpdatePayload(**payload)
    assert organisation.name == "Test Organisation"
    assert organisation.extension is None


def test_role_with_only_operational_typed_period_fails() -> None:
    """Test that a role with only Operational TypedPeriod (no Legal) fails validation."""
    payload = _build_base_payload()
    operational_period = _build_typed_period_extension(
        date_type="Operational", start="2020-01-15", end=None
    )
    payload["extension"] = [
        _build_organisation_role_extension(
            role_code="RO76", typed_periods=[operational_period]
        )
    ]
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "At least one Typed Period extension should have dateType as Legal" in str(
        e.value
    )


def test_role_with_both_legal_and_operational_typed_periods_passes() -> None:
    """Test that a role with both Legal and Operational TypedPeriods passes validation."""
    payload = _build_base_payload()
    legal_period = _build_typed_period_extension(
        date_type="Legal", start="2020-01-15", end="2025-12-31"
    )
    operational_period = _build_typed_period_extension(
        date_type="Operational", start="2023-01-01", end=None
    )

    primary_role = _build_organisation_role_extension(
        role_code="RO177", typed_periods=[legal_period, operational_period]
    )
    non_primary_role = _build_organisation_role_extension(role_code="RO76")
    payload["extension"] = [primary_role, non_primary_role]

    organisation = OrganisationUpdatePayload(**payload)
    assert organisation.extension is not None
    assert str(len(organisation.extension)) == "2"


def test_typed_period_missing_value_period_fails() -> None:
    """Test that TypedPeriod with missing valuePeriod fails validation."""
    payload = _build_base_payload()

    # Manually create TypedPeriod with period extension but no valuePeriod
    typed_period = {
        "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
        "extension": [
            {
                "url": "dateType",
                "valueCoding": {
                    "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                    "code": "Legal",
                },
            },
            {
                "url": "period",
                # Missing valuePeriod
            },
        ],
    }
    role_extension = _build_organisation_role_extension(
        role_code="RO182", typed_periods=[typed_period]
    )
    payload["extension"] = [role_extension]

    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "TypedPeriod extension must have a valuePeriod" in str(e.value)


def test_invalid_pharmacy_with_non_primary_roles() -> None:
    """Test that pharmacy role (RO182) cannot be used as primary due to validation rules."""
    payload = _build_base_payload()

    primary_period = _build_typed_period_extension(
        date_type="Legal", start="2020-01-15", end=None
    )
    # RO182 is not in VALID_PRIMARY_TYPE_CODES, so this will fail
    primary_role = _build_organisation_role_extension(
        role_code="RO182", typed_periods=[primary_period]
    )

    payload["extension"] = [primary_role]

    with pytest.raises(OperationOutcomeException) as exc_info:
        OrganisationUpdatePayload(**payload)

    assert "Valid primary role code (RO177) must be provided" in str(exc_info.value)


def test_invalid_prescribing_cost_centre_with_duplicate_non_primary_roles() -> None:
    """Test that prescribing cost centre (RO177) with duplicate non-primary roles fails validation."""
    payload = _build_base_payload()

    primary_period = _build_typed_period_extension(
        date_type="Legal", start="2020-01-15", end=None
    )
    primary_role = _build_organisation_role_extension(
        role_code="RO177", typed_periods=[primary_period], primary_role=True
    )

    # First RO76
    non_primary_period_1 = _build_typed_period_extension(
        date_type="Legal", start="2014-04-15", end=None
    )
    non_primary_role_1 = _build_organisation_role_extension(
        role_code="RO76", typed_periods=[non_primary_period_1], primary_role=False
    )

    # Duplicate RO76
    non_primary_period_2 = _build_typed_period_extension(
        date_type="Legal", start="2015-05-20", end=None
    )
    non_primary_role_2 = _build_organisation_role_extension(
        role_code="RO76", typed_periods=[non_primary_period_2], primary_role=False
    )

    payload["extension"] = [primary_role, non_primary_role_1, non_primary_role_2]

    with pytest.raises(OperationOutcomeException) as exc_info:
        OrganisationUpdatePayload(**payload)

    assert "Duplicate non-primary roles are not allowed" in str(exc_info.value)


def test_invalid_prescribing_cost_centre_no_non_primary_roles() -> None:
    """Test that prescribing cost centre (RO177) without non-primary roles fails validation."""
    payload = _build_base_payload()

    primary_period = _build_typed_period_extension(
        date_type="Legal", start="2020-01-15", end=None
    )
    primary_role = _build_organisation_role_extension(
        role_code="RO177", typed_periods=[primary_period], primary_role=True
    )

    payload["extension"] = [primary_role]

    with pytest.raises(OperationOutcomeException) as exc_info:
        OrganisationUpdatePayload(**payload)

    assert "RO177 must have at least one non-primary role" in str(exc_info.value)


def test_invalid_multiple_primary_roles() -> None:
    """Test that validation fails when multiple primary roles are provided."""
    payload = _build_base_payload()

    # First primary role (RO177) - valid
    primary_period_1 = _build_typed_period_extension(
        date_type="Legal", start="2020-01-15", end=None
    )
    primary_role_1 = _build_organisation_role_extension(
        role_code="RO177", typed_periods=[primary_period_1]
    )

    # Second role (RO177) - duplicate primary
    primary_period_2 = _build_typed_period_extension(
        date_type="Legal", start="2020-01-15", end=None
    )
    primary_role_2 = _build_organisation_role_extension(
        role_code="RO177", typed_periods=[primary_period_2]
    )

    # Non-primary role
    non_primary_period = _build_typed_period_extension(
        date_type="Legal", start="2014-04-15", end=None
    )
    non_primary_role = _build_organisation_role_extension(
        role_code="RO76", typed_periods=[non_primary_period]
    )

    payload["extension"] = [primary_role_1, primary_role_2, non_primary_role]

    with pytest.raises(OperationOutcomeException) as exc_info:
        OrganisationUpdatePayload(**payload)

    assert "Only one primary role is allowed per organisation" in str(exc_info.value)


def test_valid_payload_with_primary_and_multiple_non_primary_role_codes() -> None:
    """Test payload with primary role and multiple valid non-primary role codes including GP Practice."""
    payload = _build_base_payload()

    primary_period = _build_typed_period_extension(
        date_type="Legal", start="2020-01-15", end=None
    )
    primary_role = _build_organisation_role_extension(
        role_code="RO177", typed_periods=[primary_period]
    )

    # RO76 (GP Practice) - required non-primary
    non_primary_period_1 = _build_typed_period_extension(
        date_type="Legal", start="2014-04-15", end=None
    )
    non_primary_role_1 = _build_organisation_role_extension(
        role_code="RO76", typed_periods=[non_primary_period_1]
    )

    # RO80 - additional non-primary
    non_primary_period_2 = _build_typed_period_extension(
        date_type="Legal", start="2015-05-20", end=None
    )
    non_primary_role_2 = _build_organisation_role_extension(
        role_code="RO80", typed_periods=[non_primary_period_2]
    )

    payload["extension"] = [primary_role, non_primary_role_1, non_primary_role_2]

    organisation = OrganisationUpdatePayload(**payload)
    assert organisation.name == "Test Organisation"
    assert organisation.extension is not None
    assert str(len(organisation.extension)) == "3"


def test_valid_payload_with_primary_and_three_non_primary_role_codes() -> None:
    """Test payload with primary role and three non-primary roles including required GP Practice."""
    payload = _build_base_payload()

    primary_period = _build_typed_period_extension(
        date_type="Legal", start="2020-01-15", end=None
    )
    primary_role = _build_organisation_role_extension(
        role_code="RO177", typed_periods=[primary_period]
    )

    # RO76 (GP Practice) - required
    gp_role = _build_organisation_role_extension(
        role_code="RO76", typed_periods=[_build_typed_period_extension()]
    )

    # RO80 - additional
    additional_role_1 = _build_organisation_role_extension(
        role_code="RO80", typed_periods=[_build_typed_period_extension()]
    )

    # RO87 - additional
    additional_role_2 = _build_organisation_role_extension(
        role_code="RO87", typed_periods=[_build_typed_period_extension()]
    )

    payload["extension"] = [primary_role, gp_role, additional_role_1, additional_role_2]

    organisation = OrganisationUpdatePayload(**payload)
    assert organisation.extension is not None
    assert str(len(organisation.extension)) == "4"


def test_invalid_prescribing_cost_centre_without_gp_practice() -> None:
    """Test that RO177 without RO76 (GP Practice) fails validation."""
    payload = _build_base_payload()

    primary_period = _build_typed_period_extension(
        date_type="Legal", start="2020-01-15", end=None
    )
    primary_role = _build_organisation_role_extension(
        role_code="RO177", typed_periods=[primary_period]
    )

    # Only RO80 without required RO76
    non_primary_role = _build_organisation_role_extension(
        role_code="RO80", typed_periods=[_build_typed_period_extension()]
    )

    payload["extension"] = [primary_role, non_primary_role]

    with pytest.raises(OperationOutcomeException) as exc_info:
        OrganisationUpdatePayload(**payload)

    assert "RO177 requires the following non-primary roles: RO76" in str(exc_info.value)


def test_invalid_prescribing_cost_centre_with_duplicate_additional_roles() -> None:
    """Test that RO177 with duplicate additional non-primary roles fails validation."""
    payload = _build_base_payload()

    primary_role = _build_organisation_role_extension(
        role_code="RO177", typed_periods=[_build_typed_period_extension()]
    )

    # Required GP Practice
    gp_role = _build_organisation_role_extension(
        role_code="RO76", typed_periods=[_build_typed_period_extension()]
    )

    # Duplicate RO80
    additional_role_1 = _build_organisation_role_extension(
        role_code="RO80", typed_periods=[_build_typed_period_extension()]
    )
    additional_role_2 = _build_organisation_role_extension(
        role_code="RO80", typed_periods=[_build_typed_period_extension()]
    )

    payload["extension"] = [primary_role, gp_role, additional_role_1, additional_role_2]

    with pytest.raises(OperationOutcomeException) as exc_info:
        OrganisationUpdatePayload(**payload)

    assert "Duplicate non-primary roles are not allowed" in str(exc_info.value)
