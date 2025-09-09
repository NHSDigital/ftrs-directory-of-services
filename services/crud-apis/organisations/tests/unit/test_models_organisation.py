import pytest
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


# def test_field_too_long_name() -> None:
#     payload = {
#         "id": "123",
#         "resourceType": "Organization",
#         "meta": {
#             "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
#         },
#         "identifier": [
#             {
#                 "system": "https://fhir.nhs.uk/Id/ods-organization-code",
#                 "value": "ABC123",
#             }
#         ],
#         "name": "a" * 1000,  # Too long
#         "active": False,
#         "telecom": [{"system": "phone", "value": "0123456789"}],
#         "type": [{"coding": [{"system": "TO-DO", "code": "GP Service"}]}],
#         "address": [
#             {
#                 "line": ["Example Medical Practice", "Example Street"],
#                 "city": "Example City",
#                 "postalCode": "AB12 3CD",
#                 "country": "ENGLAND",
#             }
#         ],
#     }
#     with pytest.raises(ValidationError) as e:
#         OrganisationUpdatePayload(**payload)
#     assert "String should have at most" in str(e.value)


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
