import pytest
from pydantic import ValidationError

from functions.constants import (
    ODS_ORG_CODE_IDENTIFIER_SYSTEM,
    REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION,
)
from functions.organization_query_params import (
    InvalidIdentifierSystem,
    InvalidRevincludeError,
    ODSCodeInvalidFormatError,
    OrganizationQueryParams,
)


class TestOrganizationQueryParams:
    @pytest.mark.parametrize(
        ("identifier", "expected_ods_code"),
        [
            (f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC12", "ABC12"),
            (
                f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC123456789",
                "ABC123456789",
            ),
            (f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC123", "ABC123"),
            (f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABCDEF", "ABCDEF"),
            (f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|123456", "123456"),
            (
                f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|abc123",
                "ABC123",
            ),  # lowercase
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
    def test_valid_organization_query_params(self, identifier, expected_ods_code):
        # Act
        params = OrganizationQueryParams(
            identifier=identifier, _revinclude=REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION
        )

        # Assert
        assert params.identifier == identifier
        assert params.revinclude == REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION
        assert params.ods_code == expected_ods_code

    @pytest.mark.parametrize(
        ("identifier", "expected_exception"),
        [
            (
                f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|",
                ODSCodeInvalidFormatError,
            ),
            (
                f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC1",
                ODSCodeInvalidFormatError,
            ),
            (
                f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABCD123456789",
                ODSCodeInvalidFormatError,
            ),
            (
                f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC-123",
                ODSCodeInvalidFormatError,
            ),
            (
                f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC 123",
                ODSCodeInvalidFormatError,
            ),
            (
                f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC@123",
                ODSCodeInvalidFormatError,
            ),
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
    def test_invalid_identifier_validation(self, identifier, expected_exception):
        # Act
        with pytest.raises(ValidationError) as exc_info:
            OrganizationQueryParams(
                identifier=identifier,
                _revinclude=REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION,
            )

        # Assert
        assert len(exc_info.value.errors()) == 1
        assert (
            exc_info.value.errors()[0]["ctx"]["error"].__class__ == expected_exception
        )

    def test_invalid_revinclude_validation(self):
        # Act
        with pytest.raises(ValidationError) as exc_info:
            OrganizationQueryParams(
                identifier=f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|ABC123",
                _revinclude="Invalid:value",
            )

        # Assert
        assert len(exc_info.value.errors()) == 1
        assert (
            exc_info.value.errors()[0]["ctx"]["error"].__class__
            == InvalidRevincludeError
        )

    def test_ods_code_computed_field(self):
        # Act
        params = OrganizationQueryParams(
            identifier=f"{ODS_ORG_CODE_IDENTIFIER_SYSTEM}|abc123",
            _revinclude=REVINCLUDE_VALUE_ENDPOINT_ORGANIZATION,
        )

        # Assert
        assert params.ods_code == "ABC123"
