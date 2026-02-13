import pytest
from pydantic import ValidationError

from functions.constants import ODS_ORG_CODE_IDENTIFIER_SYSTEM
from functions.healthcare_service_query_params import (
    HealthcareServiceQueryParams,
    InvalidIdentifierSystem,
    ODSCodeInvalidFormatError,
)


class TestHealthcareServiceQueryParams:
    @pytest.mark.parametrize(
        ("identifier", "expected_ods_code"),
        [
            (f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC12", "ABC12"),
            (f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC123456789", "ABC123456789"),
            (f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC123", "ABC123"),
            (f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABCDEF", "ABCDEF"),
            (f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|123456", "123456"),
            (f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|abc123", "ABC123"),
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
            (f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|", ODSCodeInvalidFormatError),
            (f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC1", ODSCodeInvalidFormatError),
            (
                f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABCD123456789",
                ODSCodeInvalidFormatError,
            ),
            (f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC-123", ODSCodeInvalidFormatError),
            (f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC 123", ODSCodeInvalidFormatError),
            (f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC@123", ODSCodeInvalidFormatError),
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
            identifier=f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|abc123",
        )

        # Assert
        assert params.ods_code == "ABC123"

    def test_missing_identifier_raises_validation_error(self) -> None:
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            HealthcareServiceQueryParams()

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("identifier",) for error in errors)

    def test_extra_fields_forbidden(self) -> None:
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            HealthcareServiceQueryParams(
                identifier=f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC123",
                extra_field="not allowed",
            )

        errors = exc_info.value.errors()
        assert any(error["type"] == "extra_forbidden" for error in errors)
