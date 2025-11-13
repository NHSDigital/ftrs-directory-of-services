import pytest
from ftrs_common.fhir.operation_outcome import OperationOutcomeException
from pydantic import ValidationError

from organisations.app.models.organisation import OrganisationUpdatePayload


def test_valid_payload() -> None:
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
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
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
    }
    organisation = OrganisationUpdatePayload(**payload)
    assert organisation.name == "Test Organisation"
    assert organisation.active is False
    assert organisation.telecom[0].value == "0123456789"
    assert organisation.type[0].coding[0].code == "GP Service"
    assert organisation.identifier[0].value == "ABC123"


def test_field_too_long_name() -> None:
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "a" * 1000,  # Too long
        "active": False,
        "telecom": [{"system": "phone", "value": "0123456789"}],
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
        "address": [
            {
                "line": ["Example Medical Practice", "Example Street"],
                "city": "Example City",
                "postalCode": "AB12 3CD",
                "country": "ENGLAND",
            }
        ],
    }
    with pytest.raises(ValidationError) as e:
        OrganisationUpdatePayload(**payload)
    assert "String should have at most" in str(e.value)


def test_missing_required_field() -> None:
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        # missing identifier which is required
        "name": "Test Organisation",
        "active": False,
        "telecom": [{"system": "phone", "value": "0123456789"}],
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
        "address": [
            {
                "line": ["Example Medical Practice", "Example Street"],
                "city": "Example City",
                "postalCode": "AB12 3CD",
                "country": "ENGLAND",
            }
        ],
    }
    with pytest.raises(ValidationError) as e:
        OrganisationUpdatePayload(**payload)
    assert "Field required" in str(e.value)


def test_additional_field() -> None:
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organisation",
        "active": False,
        "telecom": [{"system": "phone", "value": "0123456789"}],
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
        "extra_field": "not allowed",
    }
    with pytest.raises(ValidationError) as e:
        OrganisationUpdatePayload(**payload)
    assert "Extra inputs are not permitted" in str(e.value)


# Tests for legal date extension validation


def test_valid_typed_period_extension_with_both_dates() -> None:
    """Test valid TypedPeriod extension with both start and end dates."""
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organisation",
        "active": True,
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
        "extension": [
            {
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
                        "valuePeriod": {
                            "start": "2020-01-15",
                            "end": "2025-12-31",
                        },
                    },
                ],
            }
        ],
    }
    organisation = OrganisationUpdatePayload(**payload)
    assert organisation.extension is not None
    assert len(organisation.extension) == 1


def test_valid_typed_period_extension_with_start_only() -> None:
    """Test valid TypedPeriod extension with only start date."""
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organisation",
        "active": True,
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
        "extension": [
            {
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
                        "valuePeriod": {"start": "2020-01-15"},
                    },
                ],
            }
        ],
    }
    organisation = OrganisationUpdatePayload(**payload)
    assert organisation.extension is not None


def test_valid_typed_period_extension_with_end_only() -> None:
    """Test valid TypedPeriod extension with only end date."""
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organisation",
        "active": True,
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
        "extension": [
            {
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
                        "valuePeriod": {"end": "2025-12-31"},
                    },
                ],
            }
        ],
    }
    organisation = OrganisationUpdatePayload(**payload)
    assert organisation.extension is not None


def test_invalid_extension_url() -> None:
    """Test validation fails with invalid extension URL."""
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organisation",
        "active": True,
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
        "extension": [
            {
                "url": "https://fhir.nhs.uk/invalid-extension",
                "extension": [
                    {
                        "url": "dateType",
                        "valueCoding": {"code": "Legal"},
                    },
                    {
                        "url": "period",
                        "valuePeriod": {"start": "2020-01-15"},
                    },
                ],
            }
        ],
    }
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "Invalid extension URL" in str(e.value)


def test_invalid_missing_date_type_sub_extension() -> None:
    """Test validation fails when dateType sub-extension is missing."""
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organisation",
        "active": True,
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
        "extension": [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                "extension": [
                    {
                        "url": "period",
                        "valuePeriod": {"start": "2020-01-15"},
                    },
                ],
            }
        ],
    }
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "must contain dateType and period" in str(e.value)


def test_invalid_missing_period_sub_extension() -> None:
    """Test validation fails when period sub-extension is missing."""
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organisation",
        "active": True,
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
        "extension": [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                "extension": [
                    {
                        "url": "dateType",
                        "valueCoding": {"code": "Legal"},
                    },
                ],
            }
        ],
    }
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "must contain dateType and period" in str(e.value)


def test_invalid_non_legal_date_type() -> None:
    """Test validation fails when dateType is not Legal."""
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organisation",
        "active": True,
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
        "extension": [
            {
                "url": "https://fhir.nhs.uk/England/StructureDefinition/Extension-England-TypedPeriod",
                "extension": [
                    {
                        "url": "dateType",
                        "valueCoding": {
                            "system": "https://fhir.nhs.uk/England/CodeSystem/England-PeriodType",
                            "code": "Operational",
                        },
                    },
                    {
                        "url": "period",
                        "valuePeriod": {"start": "2020-01-15"},
                    },
                ],
            }
        ],
    }
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "dateType must be Legal" in str(e.value)


def test_invalid_period_without_dates() -> None:
    """Test validation fails when period has neither start nor end date."""
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organisation",
        "active": True,
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
        "extension": [
            {
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
                        "valuePeriod": {},
                    },
                ],
            }
        ],
    }
    with pytest.raises(OperationOutcomeException) as e:
        OrganisationUpdatePayload(**payload)
    assert "must contain at least start or end date" in str(e.value)


def test_null_extension_is_valid() -> None:
    """Test that null/missing extension field is valid."""
    payload = {
        "id": "123",
        "resourceType": "Organization",
        "meta": {
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        "identifier": [
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        "name": "Test Organisation",
        "active": True,
        "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
    }
    organisation = OrganisationUpdatePayload(**payload)
    assert organisation.extension is None
