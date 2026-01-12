from src.router.responses import (
    ERROR_INVALID_IDENTIFIER_SYSTEM,
    ERROR_INVALID_IDENTIFIER_VALUE,
    ERROR_MISSING_REVINCLUDE,
    SUCCESS_BUNDLE_ABC123,
)


class TestResponses:
    def test_success_bundle_abc123_structure(self):
        """Test that SUCCESS_BUNDLE_ABC123 has the correct structure"""
        # Assert
        assert SUCCESS_BUNDLE_ABC123["resourceType"] == "Bundle"
        assert SUCCESS_BUNDLE_ABC123["type"] == "searchset"
        assert "id" in SUCCESS_BUNDLE_ABC123
        assert "link" in SUCCESS_BUNDLE_ABC123
        assert "entry" in SUCCESS_BUNDLE_ABC123

    def test_success_bundle_abc123_has_link(self):
        """Test that SUCCESS_BUNDLE_ABC123 has a self link"""
        # Assert
        assert len(SUCCESS_BUNDLE_ABC123["link"]) == 1
        assert SUCCESS_BUNDLE_ABC123["link"][0]["relation"] == "self"
        assert (
            "Organization?identifier=odsOrganisationCode|ABC123"
            in SUCCESS_BUNDLE_ABC123["link"][0]["url"]
        )
        assert "_revinclude=Endpoint:organization" in SUCCESS_BUNDLE_ABC123["link"][0]["url"]

    def test_success_bundle_abc123_has_three_entries(self):
        """Test that SUCCESS_BUNDLE_ABC123 has exactly 3 entries (1 org + 2 endpoints)"""
        # Assert
        assert len(SUCCESS_BUNDLE_ABC123["entry"]) == 3

    def test_success_bundle_abc123_organization_entry(self):
        """Test that the first entry is an Organization"""
        # Arrange
        org_entry = SUCCESS_BUNDLE_ABC123["entry"][0]

        # Assert
        assert org_entry["resource"]["resourceType"] == "Organization"
        assert org_entry["resource"]["identifier"][0]["value"] == "ABC123"
        assert (
            org_entry["resource"]["identifier"][0]["system"]
            == "https://fhir.nhs.uk/Id/ods-organization-code"
        )
        assert org_entry["resource"]["active"] is True
        assert org_entry["resource"]["name"] == "Example Organization"
        assert org_entry["search"]["mode"] == "match"

    def test_success_bundle_abc123_endpoint_entries(self):
        """Test that the second and third entries are Endpoints"""
        # Arrange
        endpoint1 = SUCCESS_BUNDLE_ABC123["entry"][1]
        endpoint2 = SUCCESS_BUNDLE_ABC123["entry"][2]

        # Assert - First endpoint
        assert endpoint1["resource"]["resourceType"] == "Endpoint"
        assert endpoint1["resource"]["status"] == "active"
        assert endpoint1["resource"]["connectionType"]["code"] == "email"
        assert endpoint1["search"]["mode"] == "include"
        assert len(endpoint1["resource"]["extension"]) == 3

        # Assert - Second endpoint
        assert endpoint2["resource"]["resourceType"] == "Endpoint"
        assert endpoint2["resource"]["status"] == "active"
        assert endpoint2["resource"]["connectionType"]["code"] == "email"
        assert endpoint2["search"]["mode"] == "include"
        assert len(endpoint2["resource"]["extension"]) == 3

    def test_success_bundle_abc123_endpoint_business_scenarios(self):
        """Test that endpoints have correct business scenarios"""
        # Arrange
        endpoint1 = SUCCESS_BUNDLE_ABC123["entry"][1]["resource"]
        endpoint2 = SUCCESS_BUNDLE_ABC123["entry"][2]["resource"]

        # Find business scenario extensions
        endpoint1_scenario = next(
            ext
            for ext in endpoint1["extension"]
            if "EndpointBusinessScenario" in ext["url"]
        )
        endpoint2_scenario = next(
            ext
            for ext in endpoint2["extension"]
            if "EndpointBusinessScenario" in ext["url"]
        )

        # Assert
        assert endpoint1_scenario["valueCode"] == "primary-recipient"
        assert endpoint2_scenario["valueCode"] == "copy-recipient"

    def test_error_invalid_identifier_value_structure(self):
        """Test that ERROR_INVALID_IDENTIFIER_VALUE has the correct structure"""
        # Assert
        assert ERROR_INVALID_IDENTIFIER_VALUE["resourceType"] == "OperationOutcome"
        assert len(ERROR_INVALID_IDENTIFIER_VALUE["issue"]) == 1

    def test_error_invalid_identifier_value_issue(self):
        """Test that ERROR_INVALID_IDENTIFIER_VALUE has correct issue details"""
        # Arrange
        issue = ERROR_INVALID_IDENTIFIER_VALUE["issue"][0]

        # Assert
        assert issue["severity"] == "error"
        assert issue["code"] == "value"
        assert issue["details"]["coding"][0]["code"] == "INVALID_SEARCH_DATA"
        assert "Invalid identifier value" in issue["diagnostics"]
        assert "^[A-Za-z0-9]{5,12}$" in issue["diagnostics"]

    def test_error_missing_revinclude_structure(self):
        """Test that ERROR_MISSING_REVINCLUDE has the correct structure"""
        # Assert
        assert ERROR_MISSING_REVINCLUDE["resourceType"] == "OperationOutcome"
        assert len(ERROR_MISSING_REVINCLUDE["issue"]) == 1

    def test_error_missing_revinclude_issue(self):
        """Test that ERROR_MISSING_REVINCLUDE has correct issue details"""
        # Arrange
        issue = ERROR_MISSING_REVINCLUDE["issue"][0]

        # Assert
        assert issue["severity"] == "error"
        assert issue["code"] == "value"
        assert issue["details"]["coding"][0]["code"] == "INVALID_SEARCH_DATA"
        assert "_revinclude=Endpoint:organization" in issue["diagnostics"]

    def test_error_invalid_identifier_system_structure(self):
        """Test that ERROR_INVALID_IDENTIFIER_SYSTEM has the correct structure"""
        # Assert
        assert ERROR_INVALID_IDENTIFIER_SYSTEM["resourceType"] == "OperationOutcome"
        assert len(ERROR_INVALID_IDENTIFIER_SYSTEM["issue"]) == 1

    def test_error_invalid_identifier_system_issue(self):
        """Test that ERROR_INVALID_IDENTIFIER_SYSTEM has correct issue details"""
        # Arrange
        issue = ERROR_INVALID_IDENTIFIER_SYSTEM["issue"][0]

        # Assert
        assert issue["severity"] == "error"
        assert issue["code"] == "code-invalid"
        assert issue["details"]["coding"][0]["code"] == "INVALID_SEARCH_DATA"
        assert "Invalid identifier system" in issue["diagnostics"]
        assert "odsOrganisationCode" in issue["diagnostics"]

    def test_all_errors_use_spine_error_coding(self):
        """Test that all error responses use UKCore-SpineErrorOrWarningCode"""
        # Arrange
        errors = [
            ERROR_INVALID_IDENTIFIER_VALUE,
            ERROR_MISSING_REVINCLUDE,
            ERROR_INVALID_IDENTIFIER_SYSTEM,
        ]

        # Assert
        for error in errors:
            coding = error["issue"][0]["details"]["coding"][0]
            assert (
                coding["system"]
                == "https://fhir.hl7.org.uk/CodeSystem/UKCore-SpineErrorOrWarningCode"
            )
            assert coding["version"] == "1.0.0"

    def test_success_bundle_organization_has_contact_info(self):
        """Test that organization in SUCCESS_BUNDLE_ABC123 has telecom and address"""
        # Arrange
        org = SUCCESS_BUNDLE_ABC123["entry"][0]["resource"]

        # Assert
        assert len(org["telecom"]) == 2
        assert org["telecom"][0]["system"] == "phone"
        assert org["telecom"][1]["system"] == "email"
        assert len(org["address"]) == 1
        assert org["address"][0]["city"] == "Example City"
        assert org["address"][0]["postalCode"] == "AB12 3CD"

    def test_success_bundle_endpoints_have_payload_types(self):
        """Test that endpoints have payload type and mime type"""
        # Arrange
        endpoint1 = SUCCESS_BUNDLE_ABC123["entry"][1]["resource"]
        endpoint2 = SUCCESS_BUNDLE_ABC123["entry"][2]["resource"]

        # Assert
        assert len(endpoint1["payloadType"]) == 1
        assert len(endpoint1["payloadMimeType"]) == 1
        assert endpoint1["payloadMimeType"][0] == "application/pdf"

        assert len(endpoint2["payloadType"]) == 1
        assert len(endpoint2["payloadMimeType"]) == 1
        assert endpoint2["payloadMimeType"][0] == "application/pdf"
