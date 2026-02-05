import pytest
from pydantic import ValidationError

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
            ("https://fhir.nhs.uk/Id/ods-organization-code|ABC12", "ABC12"),
            (
                "https://fhir.nhs.uk/Id/ods-organization-code|ABC123456789",
                "ABC123456789",
            ),
            ("https://fhir.nhs.uk/Id/ods-organization-code|ABC123", "ABC123"),
            ("https://fhir.nhs.uk/Id/ods-organization-code|ABCDEF", "ABCDEF"),
            ("https://fhir.nhs.uk/Id/ods-organization-code|123456", "123456"),
            (
                "https://fhir.nhs.uk/Id/ods-organization-code|abc123",
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
            identifier=identifier, _revinclude="Endpoint:organization"
        )

        # Assert
        assert params.identifier == identifier
        assert params.revinclude == "Endpoint:organization"
        assert params.ods_code == expected_ods_code

    @pytest.mark.parametrize(
        ("identifier", "expected_exception"),
        [
            (
                "https://fhir.nhs.uk/Id/ods-organization-code|",
                ODSCodeInvalidFormatError,
            ),
            (
                "https://fhir.nhs.uk/Id/ods-organization-code|ABC1",
                ODSCodeInvalidFormatError,
            ),
            (
                "https://fhir.nhs.uk/Id/ods-organization-code|ABCD123456789",
                ODSCodeInvalidFormatError,
            ),
            (
                "https://fhir.nhs.uk/Id/ods-organization-code|ABC-123",
                ODSCodeInvalidFormatError,
            ),
            (
                "https://fhir.nhs.uk/Id/ods-organization-code|ABC 123",
                ODSCodeInvalidFormatError,
            ),
            (
                "https://fhir.nhs.uk/Id/ods-organization-code|ABC@123",
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
                identifier="https://fhir.nhs.uk/Id/ods-organization-code|ABC123",
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
            identifier="https://fhir.nhs.uk/Id/ods-organization-code|abc123",
            _revinclude="Endpoint:organization",
        )

        # Assert
        assert params.ods_code == "ABC123"
