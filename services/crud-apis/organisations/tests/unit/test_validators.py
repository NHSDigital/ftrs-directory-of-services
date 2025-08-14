import pytest
from pydantic_core import ValidationError

from organisations.app.services.validators import (
    NAME_EMPTY_ERROR,
    UpdatePayloadValidator,
)


def test_update_payload_validator_valid_details() -> None:
    payload = UpdatePayloadValidator(
        id="123",
        resourceType="Organization",
        meta={
            "profile": ["https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"]
        },
        identifier=[
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        name="NHS Digital",
        active=True,
        telecom=[{"system": "phone", "value": "123456789", "use": "work"}],
        type=[{"coding": [{"system": "TO-DO", "code": "GP Practice"}]}],
    )
    assert payload.name == "NHS Digital"
    assert payload.active is True
    assert payload.telecom[0].value == "123456789"
    assert payload.type[0].coding[0].code == "GP Practice"
    assert payload.identifier[0].value == "ABC123"


def test_update_payload_validator_empty_name() -> None:
    with pytest.raises(ValidationError, match=NAME_EMPTY_ERROR):
        UpdatePayloadValidator(
            id="123",
            resourceType="Organization",
            meta={
                "profile": [
                    "https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"
                ]
            },
            identifier=[
                {
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": "ABC123",
                }
            ],
            name="   ",
            active=True,
            telecom=[{"system": "phone", "value": "123456789"}],
            type=[{"coding": [{"system": "TO-DO", "code": "GP Practice"}]}],
        )


def test_update_payload_validator_missing_id() -> None:
    with pytest.raises(ValidationError, match="id\\n  Field required"):
        UpdatePayloadValidator(
            resourceType="Organization",
            meta={"versionId": "1"},
            name="NHS Digital",
            modified_by="test_user",
            type=[{"coding": [{"system": "TO-DO", "code": "GP Practice"}]}],
            active=True,
            telecom=[{"system": "phone", "value": "123456789"}],
            identifier=[
                {
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": "ABC123",
                }
            ],
        )


def test_update_payload_validator_missing_resource_type() -> None:
    with pytest.raises(ValidationError, match="resourceType\\n  Field required"):
        UpdatePayloadValidator(
            id="123",
            meta={
                "profile": [
                    "https://fhir.nhs.uk/StructureDefinition/UKCore-Organization"
                ]
            },
            identifier=[
                {
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": "ABC123",
                }
            ],
            name="NHS Digital",
            active=True,
            telecom=[{"system": "phone", "value": "123456789"}],
        )


def test_update_payload_validator_missing_meta() -> None:
    with pytest.raises(ValidationError, match="meta\\n  Field required"):
        UpdatePayloadValidator(
            id="123",
            resourceType="Organization",
            name="NHS Digital",
            modified_by="test_user",
            type="NHS",
            active=True,
            telecom="123456789",
            identifier={"value": "ABC123"},
        )


def test_update_payload_validator_missing_identifier() -> None:
    with pytest.raises(ValidationError, match="identifier\\n  Field required"):
        UpdatePayloadValidator(
            id="123",
            resourceType="Organization",
            meta={"versionId": "1"},
            name="NHS Digital",
            modified_by="test_user",
            type="NHS",
            active=True,
            telecom="123456789",
        )
