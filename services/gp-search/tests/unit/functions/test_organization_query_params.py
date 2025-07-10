import pytest
from pydantic import ValidationError

from functions.organization_query_params import (
    InvalidIdentifierPrefixError,
    InvalidRevincludeError,
    ODSCodeInvalidFormatError,
    ODSCodeTooLongError,
    ODSCodeTooShortError,
    OrganizationQueryParams,
)


class TestOrganizationQueryParams:
    @pytest.mark.parametrize(
        ("identifier", "expected_ods_code"),
        [
            ("odsOrganisationCode|ABC12", "ABC12"),
            ("odsOrganisationCode|ABC123456789", "ABC123456789"),
            ("odsOrganisationCode|ABC123", "ABC123"),
            ("odsOrganisationCode|ABCDEF", "ABCDEF"),
            ("odsOrganisationCode|123456", "123456"),
            ("odsOrganisationCode|abc123", "ABC123"),  # lowercase
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
            identifier=identifier, _revinclude="Endpoint:organization"
        )

        # Assert
        assert params.identifier == identifier
        assert params.revinclude == "Endpoint:organization"
        assert params.ods_code == expected_ods_code

    @pytest.mark.parametrize(
        ("identifier", "expected_exception"),
        [
            ("odsOrganisationCode|", ODSCodeTooShortError),
            ("odsOrganisationCode|ABC1", ODSCodeTooShortError),
            ("odsOrganisationCode|ABCD123456789", ODSCodeTooLongError),
            ("odsOrganisationCode|ABC-123", ODSCodeInvalidFormatError),
            ("odsOrganisationCode|ABC 123", ODSCodeInvalidFormatError),
            ("odsOrganisationCode|ABC@123", ODSCodeInvalidFormatError),
            ("", InvalidIdentifierPrefixError),
            ("wrongPrefix|ABC123", InvalidIdentifierPrefixError),
            ("ABC123", InvalidIdentifierPrefixError),
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
                identifier=identifier, _revinclude="Endpoint:organization"
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
                identifier="odsOrganisationCode|ABC123", _revinclude="Invalid:value"
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
            identifier="odsOrganisationCode|abc123", _revinclude="Endpoint:organization"
        )

        # Assert
        assert params.ods_code == "ABC123"
