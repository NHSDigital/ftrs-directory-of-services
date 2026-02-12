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
        params = HealthcareServiceQueryParams(identifier=identifier)

        # Assert
        assert params.identifier == identifier
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
            HealthcareServiceQueryParams(identifier=identifier)

        # Assert
        assert len(exc_info.value.errors()) == 1
        assert (
            exc_info.value.errors()[0]["ctx"]["error"].__class__ == expected_exception
        )

    def test_ods_code_computed_field(self) -> None:
        # Act
        params = HealthcareServiceQueryParams(
            identifier="odsOrganisationCode|abc123",
        )

        # Assert
        assert params.ods_code == "ABC123"

    def test_missing_identifier_raises_validation_error(self) -> None:
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            HealthcareServiceQueryParams()

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("identifier",) for error in errors)
