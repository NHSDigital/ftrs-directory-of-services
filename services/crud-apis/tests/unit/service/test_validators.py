import pytest
from dos_ingest.service.org_validators import (
    NAME_EMPTY_ERROR,
    ODS_CODE_EMPTY_ERROR,
    CreatePayloadValidator,
    UpdatePayloadValidator,
)
from dos_ingest.service.validators import (
    NAME_EMPTY_ERROR as HS_NAME_EMPTY_ERROR,
)
from dos_ingest.service.validators import (
    HealthcareServiceCreatePayloadValidator,
)
from ftrs_data_layer.domain.enums import (
    HealthcareServiceCategory,
    HealthcareServiceType,
)
from pydantic import ValidationError


def test_update_payload_validator_accepts_valid_organisation_payload() -> None:
    payload = UpdatePayloadValidator(
        id="00000000-0000-0000-0000-00000000000a",
        resourceType="Organization",
        identifier=[
            {
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "ABC123",
            }
        ],
        name="NHS Digital",
        active=True,
        telecom=[{"system": "phone", "value": "0300 311 22 33", "use": "work"}],
    )

    assert payload.name == "NHS Digital"


def test_update_payload_validator_rejects_blank_name() -> None:
    with pytest.raises(ValidationError, match=NAME_EMPTY_ERROR):
        UpdatePayloadValidator(
            id="00000000-0000-0000-0000-00000000000a",
            resourceType="Organization",
            identifier=[
                {
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": "ABC123",
                }
            ],
            name="   ",
            active=True,
            telecom=[{"system": "phone", "value": "0300 311 22 33", "use": "work"}],
        )


def test_create_payload_validator_rejects_blank_ods_code() -> None:
    with pytest.raises(ValidationError, match=ODS_CODE_EMPTY_ERROR):
        CreatePayloadValidator(
            identifier_ODS_ODSCode=" ",
            active=True,
            name="Organisation",
            telecom=[{"type": "phone", "value": "0300 311 22 33", "isPublic": True}],
        )


def test_healthcare_create_validator_accepts_valid_payload() -> None:
    payload = HealthcareServiceCreatePayloadValidator(
        name="Healthcare Service",
        type=HealthcareServiceType.GP_CONSULTATION_SERVICE,
        category=HealthcareServiceCategory.GP_SERVICES,
        active=True,
        telecom={"phone_public": "0208 883 5555"},
        openingTime=[],
        symptomGroupSymptomDiscriminators=[],
        dispositions=[],
    )

    assert payload.name == "Healthcare Service"


def test_healthcare_create_validator_rejects_blank_name() -> None:
    with pytest.raises(ValidationError, match=HS_NAME_EMPTY_ERROR):
        HealthcareServiceCreatePayloadValidator(
            name=" ",
            type=HealthcareServiceType.GP_CONSULTATION_SERVICE,
            category=HealthcareServiceCategory.GP_SERVICES,
            active=True,
            telecom={"phone_public": "0208 883 5555"},
            openingTime=[],
            symptomGroupSymptomDiscriminators=[],
            dispositions=[],
        )


def test_healthcare_create_validator_rejects_invalid_type() -> None:
    with pytest.raises(ValidationError, match="Input should be"):
        HealthcareServiceCreatePayloadValidator(
            name="Healthcare Service",
            type="Bad Type",
            category=HealthcareServiceCategory.GP_SERVICES,
            active=True,
            telecom={"phone_public": "0208 883 5555"},
            openingTime=[],
            symptomGroupSymptomDiscriminators=[],
            dispositions=[],
        )


def test_healthcare_create_validator_rejects_invalid_category() -> None:
    with pytest.raises(ValidationError, match="Input should be"):
        HealthcareServiceCreatePayloadValidator(
            name="Healthcare Service",
            type=HealthcareServiceType.GP_CONSULTATION_SERVICE,
            category="Bad Category",
            active=True,
            telecom={"phone_public": "0208 883 5555"},
            openingTime=[],
            symptomGroupSymptomDiscriminators=[],
            dispositions=[],
        )
