import pytest
from ftrs_data_layer.domain.enums import OrganisationTypeCode
from pydantic_core import ValidationError

from organisations.app.services.validators import (
    NAME_EMPTY_ERROR,
    UpdatePayloadValidator,
    validate_type_combination,
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
    )
    assert payload.name == "NHS Digital"
    assert payload.active is True
    assert payload.telecom[0].value == "123456789"
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
        )


def test_update_payload_validator_missing_id() -> None:
    with pytest.raises(ValidationError, match="id\\n  Field required"):
        UpdatePayloadValidator(
            resourceType="Organization",
            meta={"versionId": "1"},
            name="NHS Digital",
            modified_by="test_user",
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


def test_validate_type_combination_valid_pharmacy_standalone() -> None:
    """Test valid pharmacy with no non-primary roles."""
    is_valid, error = validate_type_combination(
        OrganisationTypeCode.PHARMACY_ROLE_CODE, []
    )
    assert is_valid is True
    assert error is None


def test_validate_type_combination_valid_prescribing_cost_centre_single_role() -> None:
    """Test valid prescribing cost centre with one non-primary role."""
    is_valid, error = validate_type_combination(
        OrganisationTypeCode.PRESCRIBING_COST_CENTRE_CODE,
        [OrganisationTypeCode.GP_PRACTICE_ROLE_CODE],
    )
    assert is_valid is True
    assert error is None


def test_validate_type_combination_valid_prescribing_cost_centre_multiple_roles() -> (
    None
):
    """Test valid prescribing cost centre with multiple non-primary roles."""
    is_valid, error = validate_type_combination(
        OrganisationTypeCode.PRESCRIBING_COST_CENTRE_CODE,
        [
            OrganisationTypeCode.GP_PRACTICE_ROLE_CODE,
            OrganisationTypeCode.OUT_OF_HOURS_ROLE_CODE,
            OrganisationTypeCode.WALK_IN_CENTRE_ROLE_CODE,
        ],
    )
    assert is_valid is True
    assert error is None


def test_validate_type_combination_invalid_pharmacy_with_non_primary() -> None:
    """Test invalid pharmacy with non-primary roles."""
    is_valid, error = validate_type_combination(
        OrganisationTypeCode.PHARMACY_ROLE_CODE,
        [OrganisationTypeCode.GP_PRACTICE_ROLE_CODE],
    )
    assert is_valid is False
    assert error == "RO182 cannot have non-primary roles. "


def test_validate_type_combination_invalid_prescribing_cost_centre_no_roles() -> None:
    """Test invalid prescribing cost centre with no non-primary roles."""
    is_valid, error = validate_type_combination(
        OrganisationTypeCode.PRESCRIBING_COST_CENTRE_CODE, []
    )
    assert is_valid is False
    assert error == "RO177 must have at least one non-primary role"


def test_validate_type_combination_invalid_duplicate_non_primary_roles() -> None:
    """Test invalid duplicate non-primary roles."""
    is_valid, error = validate_type_combination(
        OrganisationTypeCode.PRESCRIBING_COST_CENTRE_CODE,
        [
            OrganisationTypeCode.GP_PRACTICE_ROLE_CODE,
            OrganisationTypeCode.GP_PRACTICE_ROLE_CODE,
        ],
    )
    assert is_valid is False
    assert error == "Duplicate non-primary roles are not allowed."


def test_validate_type_combination_invalid_non_permitted_role() -> None:
    """Test invalid non-primary role not permitted for prescribing cost centre."""
    is_valid, error = validate_type_combination(
        OrganisationTypeCode.PRESCRIBING_COST_CENTRE_CODE,
        [OrganisationTypeCode.PHARMACY_ROLE_CODE],
    )
    assert is_valid is False
    assert (
        error == "Non-primary role 'RO182' is not permitted for primary type 'RO177'."
    )


def test_validate_type_combination_invalid_no_primary_role() -> None:
    """Test invalid when no primary role code is provided."""
    is_valid, error = validate_type_combination(
        None, [OrganisationTypeCode.GP_PRACTICE_ROLE_CODE]
    )
    assert is_valid is False
    assert error == "Primary role code must be provided."


def test_validate_type_combination_invalid_primary_role_code() -> None:
    """Test invalid when primary role code is not in valid primary types."""
    is_valid, error = validate_type_combination(
        OrganisationTypeCode.GP_PRACTICE_ROLE_CODE, []
    )
    assert is_valid is False
    assert error == "Invalid primary role code: 'RO76'. "
