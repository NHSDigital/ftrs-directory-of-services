import pytest
from pydantic import ValidationError

from functions.healthcare_service_query_params import (
    HealthcareServiceQueryParams,
    InvalidIdentifierSystem,
    ODSCodeInvalidFormatError,
)


class TestHealthcareServiceQueryParams:
    @pytest.mark.parametrize(
        ("identifier", "expected_ods_code"),
        [
            ("odsOrganisationCode|ABC12", "ABC12"),
            ("odsOrganisationCode|ABC123456789", "ABC123456789"),
            ("odsOrganisationCode|ABC123", "ABC123"),
            ("odsOrganisationCode|ABCDEF", "ABCDEF"),
            ("odsOrganisationCode|123456", "123456"),
            ("odsOrganisationCode|abc123", "ABC123"),  # lowercase converted
        ],
        ids=[
            "minimum length",
            "maximum length",
            "alphanumeric mixed",
            "letters only",
            "numbers only",
            "lowercase converted",
        ],
    )
    def test_valid_healthcare_service_query_params(
        self, identifier: str, expected_ods_code: str
    ) -> None:
        # Act
        params = HealthcareServiceQueryParams(
            identifier=identifier, _include="HealthcareService:location"
        )

        # Assert
        assert params.identifier == identifier
        assert params.include == "HealthcareService:location"
        assert params.ods_code == expected_ods_code

    @pytest.mark.parametrize(
        ("identifier", "expected_exception"),
        [
            ("odsOrganisationCode|", ODSCodeInvalidFormatError),
            ("odsOrganisationCode|ABC1", ODSCodeInvalidFormatError),
            ("odsOrganisationCode|ABCD123456789", ODSCodeInvalidFormatError),
            ("odsOrganisationCode|ABC-123", ODSCodeInvalidFormatError),
            ("odsOrganisationCode|ABC 123", ODSCodeInvalidFormatError),
            ("odsOrganisationCode|ABC@123", ODSCodeInvalidFormatError),
            ("", InvalidIdentifierSystem),
            ("wrongPrefix|ABC123", InvalidIdentifierSystem),
            ("ABC123", InvalidIdentifierSystem),
        ],
        ids=[
            "odsCode empty after prefix",
            "odsCode too short",
            "odsCode too long",
            "odsCode non-alphanumeric hyphen",
            "odsCode non-alphanumeric space",
            "odsCode non-alphanumeric symbol",
            "identifier empty",
            "wrong prefix",
            "no prefix",
        ],
    )
    def test_invalid_identifier_validation(
        self, identifier: str, expected_exception: type
    ) -> None:
        # Act
        with pytest.raises(ValidationError) as exc_info:
            HealthcareServiceQueryParams(
                identifier=identifier, _include="HealthcareService:location"
            )

        # Assert
        assert len(exc_info.value.errors()) == 1
        assert (
            exc_info.value.errors()[0]["ctx"]["error"].__class__ == expected_exception
        )

    def test_ods_code_computed_field(self) -> None:
        # Act
        params = HealthcareServiceQueryParams(
            identifier="odsOrganisationCode|abc123",
            _include="HealthcareService:location",
        )

        # Assert
        assert params.ods_code == "ABC123"

    def test_missing_identifier_raises_validation_error(self) -> None:
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            HealthcareServiceQueryParams(_include="HealthcareService:location")

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("identifier",) for error in errors)

    def test_missing_include_raises_validation_error(self) -> None:
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            HealthcareServiceQueryParams(identifier="odsOrganisationCode|ABC123")

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("_include",) for error in errors)

    def test_extra_fields_forbidden(self) -> None:
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            HealthcareServiceQueryParams(
                identifier="odsOrganisationCode|ABC123",
                _include="HealthcareService:location",
                extra_field="not_allowed",
            )

        errors = exc_info.value.errors()
        assert any(error["type"] == "extra_forbidden" for error in errors)

    @pytest.mark.parametrize(
        "include_value",
        [
            "HealthcareService:location",
            "HealthcareService:endpoint",
            "HealthcareService:organization",
        ],
        ids=[
            "include location",
            "include endpoint",
            "include organization",
        ],
    )
    def test_various_include_values_accepted(self, include_value: str) -> None:
        # Act
        params = HealthcareServiceQueryParams(
            identifier="odsOrganisationCode|ABC123",
            _include=include_value,
        )

        # Assert
        assert params.include == include_value
