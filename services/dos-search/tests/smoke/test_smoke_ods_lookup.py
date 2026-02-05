"""
Smoke Tests: ODS Lookup

Tests core ODS organization lookup functionality in deployed environments.
These tests validate critical search paths and should run every 15 minutes.
"""

import json

import pytest
import requests
from fhir.resources.bundle import Bundle
from fhir.resources.operationoutcome import OperationOutcome
from pydantic import ValidationError
from requests.exceptions import ConnectionError, Timeout


class TestODSLookupSmoke:
    """Smoke tests for ODS organization lookup"""

    def test_valid_ods_lookup_returns_200(
        self, base_url, headers, valid_ods_code, timeout
    ):
        """
        CRITICAL: Valid ODS code lookup must return 200 OK

        This validates the core functionality of the search service.
        Should run every 15 minutes in production.
        """
        # Arrange
        search_url = f"{base_url}/Organization"
        params = {
            "identifier": f"odsOrganisationCode|{valid_ods_code}",
            "_revinclude": "Endpoint:organization",
        }

        # Act
        try:
            response = requests.get(
                search_url, params=params, headers=headers, timeout=timeout
            )
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"ODS lookup endpoint unreachable: {e}")

        # Assert
        assert (
            response.status_code == 200
        ), f"Valid ODS lookup failed with status {response.status_code}"

    def test_valid_ods_lookup_returns_fhir_bundle(
        self, base_url, headers, valid_ods_code, timeout
    ):
        """
        Valid ODS lookup should return a FHIR Bundle

        Validates the response structure matches FHIR specification.
        """
        # Arrange
        search_url = f"{base_url}/Organization"
        params = {
            "identifier": f"odsOrganisationCode|{valid_ods_code}",
            "_revinclude": "Endpoint:organization",
        }

        # Act
        try:
            response = requests.get(
                search_url, params=params, headers=headers, timeout=timeout
            )
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"ODS lookup endpoint unreachable: {e}")

        # Assert
        assert response.status_code == 200
        content_type = response.headers.get("Content-Type", "")
        assert "application/fhir+json" in content_type, (
            f"Expected FHIR JSON content type, got {content_type}"
        )

        data = response.json()
        assert data.get("resourceType") == "Bundle", "Response should be a FHIR Bundle"
        assert data.get("type") == "searchset", "Bundle type should be searchset"

    def test_valid_ods_lookup_bundle_has_entries(
        self, base_url, headers, valid_ods_code, timeout
    ):
        """
        Valid ODS lookup should return bundle with entries

        Validates that a known ODS code returns organization and endpoint data.
        """
        # Arrange
        search_url = f"{base_url}/Organization"
        params = {
            "identifier": f"odsOrganisationCode|{valid_ods_code}",
            "_revinclude": "Endpoint:organization",
        }

        # Act
        try:
            response = requests.get(
                search_url, params=params, headers=headers, timeout=timeout
            )
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"ODS lookup endpoint unreachable: {e}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        entries = data.get("entry", [])

        # Should have at least organization entry
        assert len(entries) > 0, "Bundle should contain at least the organization entry"

        # First entry should be Organization
        first_entry = entries[0]
        assert first_entry.get("resource", {}).get("resourceType") == "Organization"
        assert first_entry.get("search", {}).get("mode") == "match"

    def test_valid_ods_lookup_response_time(
        self, base_url, headers, valid_ods_code, timeout
    ):
        """
        ODS lookup should respond within acceptable time

        Validates that searches complete quickly (< 5 seconds).
        """
        # Arrange
        search_url = f"{base_url}/Organization"
        params = {
            "identifier": f"odsOrganisationCode|{valid_ods_code}",
            "_revinclude": "Endpoint:organization",
        }
        max_response_time = 5.0  # seconds

        # Act
        try:
            response = requests.get(
                search_url, params=params, headers=headers, timeout=timeout
            )
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"ODS lookup endpoint unreachable: {e}")

        # Assert
        assert response.status_code == 200
        assert response.elapsed.total_seconds() < max_response_time, (
            f"ODS lookup took {response.elapsed.total_seconds():.2f}s, "
            f"expected < {max_response_time}s"
        )


class TestInvalidODSCodeSmoke:
    """Smoke tests for invalid ODS code handling"""

    def test_invalid_ods_format_returns_400(
        self, base_url, headers, invalid_ods_code, timeout
    ):
        """
        CRITICAL: Invalid ODS code format should return 400 Bad Request

        Validates error handling for malformed ODS codes.
        Should run hourly in production.
        """
        # Arrange
        search_url = f"{base_url}/Organization"
        params = {
            "identifier": f"odsOrganisationCode|{invalid_ods_code}",
            "_revinclude": "Endpoint:organization",
        }

        # Act
        try:
            response = requests.get(
                search_url, params=params, headers=headers, timeout=timeout
            )
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"ODS lookup endpoint unreachable: {e}")

        # Assert
        assert (
            response.status_code == 400
        ), f"Invalid ODS code should return 400, got {response.status_code}"

    def test_invalid_ods_returns_operation_outcome(
        self, base_url, headers, invalid_ods_code, timeout
    ):
        """
        Invalid ODS code should return FHIR OperationOutcome

        Validates that error responses follow FHIR specification.
        """
        # Arrange
        search_url = f"{base_url}/Organization"
        params = {
            "identifier": f"odsOrganisationCode|{invalid_ods_code}",
            "_revinclude": "Endpoint:organization",
        }

        # Act
        try:
            response = requests.get(
                search_url, params=params, headers=headers, timeout=timeout
            )
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"ODS lookup endpoint unreachable: {e}")

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert (
            data.get("resourceType") == "OperationOutcome"
        ), "Error response should be an OperationOutcome"
        assert "issue" in data, "OperationOutcome should contain issues"
        assert len(data["issue"]) > 0, "OperationOutcome should have at least one issue"

    def test_too_short_ods_code_rejected(self, base_url, headers, timeout):
        """
        ODS code shorter than 5 characters should be rejected

        Validates length validation (minimum).
        """
        # Arrange
        search_url = f"{base_url}/Organization"
        short_ods = "ABC1"  # 4 characters - too short
        params = {
            "identifier": f"odsOrganisationCode|{short_ods}",
            "_revinclude": "Endpoint:organization",
        }

        # Act
        try:
            response = requests.get(
                search_url, params=params, headers=headers, timeout=timeout
            )
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"ODS lookup endpoint unreachable: {e}")

        # Assert
        assert (
            response.status_code == 400
        ), f"Short ODS code should return 400, got {response.status_code}"

    def test_too_long_ods_code_rejected(self, base_url, headers, timeout):
        """
        ODS code longer than 12 characters should be rejected

        Validates length validation (maximum).
        """
        # Arrange
        search_url = f"{base_url}/Organization"
        long_ods = "ABCD123456789"  # 13 characters - too long
        params = {
            "identifier": f"odsOrganisationCode|{long_ods}",
            "_revinclude": "Endpoint:organization",
        }

        # Act
        try:
            response = requests.get(
                search_url, params=params, headers=headers, timeout=timeout
            )
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"ODS lookup endpoint unreachable: {e}")

        # Assert
        assert (
            response.status_code == 400
        ), f"Long ODS code should return 400, got {response.status_code}"


class TestNonexistentODSCodeSmoke:
    """Smoke tests for nonexistent ODS code handling"""

    def test_nonexistent_ods_returns_empty_bundle(
        self, base_url, headers, nonexistent_ods_code, timeout
    ):
        """
        CRITICAL: Nonexistent ODS code should return empty bundle

        Validates that valid format codes with no matches return empty results.
        Should run hourly in production.
        """
        # Arrange
        search_url = f"{base_url}/Organization"
        params = {
            "identifier": f"odsOrganisationCode|{nonexistent_ods_code}",
            "_revinclude": "Endpoint:organization",
        }

        # Act
        try:
            response = requests.get(
                search_url, params=params, headers=headers, timeout=timeout
            )
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"ODS lookup endpoint unreachable: {e}")

        # Assert
        assert response.status_code == 200, "Should return 200 even for no results"
        data = response.json()
        assert data.get("resourceType") == "Bundle"
        assert data.get("type") == "searchset"
        entries = data.get("entry", [])
        assert len(entries) == 0, "Bundle should be empty for nonexistent ODS code"

    def test_nonexistent_ods_bundle_has_self_link(
        self, base_url, headers, nonexistent_ods_code, timeout
    ):
        """
        Empty bundle should still contain self link

        Validates bundle structure even when no results found.
        """
        # Arrange
        search_url = f"{base_url}/Organization"
        params = {
            "identifier": f"odsOrganisationCode|{nonexistent_ods_code}",
            "_revinclude": "Endpoint:organization",
        }

        # Act
        try:
            response = requests.get(
                search_url, params=params, headers=headers, timeout=timeout
            )
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"ODS lookup endpoint unreachable: {e}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        links = data.get("link", [])
        assert len(links) > 0, "Bundle should have at least a self link"
        self_link = next((link for link in links if link.get("relation") == "self"), None)
        assert self_link is not None, "Bundle should have a self link"
        assert nonexistent_ods_code in self_link.get("url", ""), "Self link should contain ODS code"


class TestQueryParameterValidationSmoke:
    """Smoke tests for query parameter validation"""

    def test_missing_identifier_parameter(self, base_url, headers, timeout):
        """
        Missing identifier parameter should return 400

        Validates required parameter validation.
        """
        # Arrange
        search_url = f"{base_url}/Organization"
        params = {
            "_revinclude": "Endpoint:organization",
            # Missing identifier parameter
        }

        # Act
        try:
            response = requests.get(
                search_url, params=params, headers=headers, timeout=timeout
            )
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"ODS lookup endpoint unreachable: {e}")

        # Assert
        assert (
            response.status_code == 400
        ), f"Missing identifier should return 400, got {response.status_code}"

    def test_missing_revinclude_parameter(
        self, base_url, headers, valid_ods_code, timeout
    ):
        """
        Missing _revinclude parameter should return 400

        Validates required parameter validation.
        """
        # Arrange
        search_url = f"{base_url}/Organization"
        params = {
            "identifier": f"odsOrganisationCode|{valid_ods_code}",
            # Missing _revinclude parameter
        }

        # Act
        try:
            response = requests.get(
                search_url, params=params, headers=headers, timeout=timeout
            )
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"ODS lookup endpoint unreachable: {e}")

        # Assert
        assert (
            response.status_code == 400
        ), f"Missing _revinclude should return 400, got {response.status_code}"

    def test_wrong_identifier_system(
        self, base_url, headers, valid_ods_code, timeout
    ):
        """
        Wrong identifier system should return 400

        Validates identifier system validation.
        """
        # Arrange
        search_url = f"{base_url}/Organization"
        params = {
            "identifier": f"wrongSystem|{valid_ods_code}",
            "_revinclude": "Endpoint:organization",
        }

        # Act
        try:
            response = requests.get(
                search_url, params=params, headers=headers, timeout=timeout
            )
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"ODS lookup endpoint unreachable: {e}")

        # Assert
        assert (
            response.status_code == 400
        ), f"Wrong identifier system should return 400, got {response.status_code}"

    def test_wrong_revinclude_value(
        self, base_url, headers, valid_ods_code, timeout
    ):
        """
        Wrong _revinclude value should return 400

        Validates _revinclude parameter value.
        """
        # Arrange
        search_url = f"{base_url}/Organization"
        params = {
            "identifier": f"odsOrganisationCode|{valid_ods_code}",
            "_revinclude": "WrongValue",
        }

        # Act
        try:
            response = requests.get(
                search_url, params=params, headers=headers, timeout=timeout
            )
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"ODS lookup endpoint unreachable: {e}")

        # Assert
        assert (
            response.status_code == 400
        ), f"Wrong _revinclude should return 400, got {response.status_code}"

    def test_extra_query_parameters_rejected(
        self, base_url, headers, valid_ods_code, timeout
    ):
        """
        Extra unexpected query parameters should be rejected

        Validates strict parameter checking.
        """
        # Arrange
        search_url = f"{base_url}/Organization"
        params = {
            "identifier": f"odsOrganisationCode|{valid_ods_code}",
            "_revinclude": "Endpoint:organization",
            "extra_param": "unexpected",
        }

        # Act
        try:
            response = requests.get(
                search_url, params=params, headers=headers, timeout=timeout
            )
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"ODS lookup endpoint unreachable: {e}")

        # Assert
        assert (
            response.status_code == 400
        ), f"Extra parameters should return 400, got {response.status_code}"


class TestHeaderValidationSmoke:
    """Smoke tests for header validation"""

    def test_invalid_custom_header_rejected(
        self, base_url, headers, valid_ods_code, timeout
    ):
        """
        Invalid custom headers should be rejected with 400

        Validates header validation in deployed environment.
        Should run daily in production.
        """
        # Arrange
        search_url = f"{base_url}/Organization"
        params = {
            "identifier": f"odsOrganisationCode|{valid_ods_code}",
            "_revinclude": "Endpoint:organization",
        }
        invalid_headers = headers.copy()
        invalid_headers["X-NHSD-INVALID"] = "should-fail"

        # Act
        try:
            response = requests.get(
                search_url, params=params, headers=invalid_headers, timeout=timeout
            )
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"ODS lookup endpoint unreachable: {e}")

        # Assert
        assert (
            response.status_code == 400
        ), f"Invalid header should return 400, got {response.status_code}"

    def test_valid_nhsd_headers_accepted(
        self, base_url, headers, valid_ods_code, timeout
    ):
        """
        Valid NHSD headers should be accepted

        Validates that standard NHSD headers work in production.
        """
        # Arrange
        search_url = f"{base_url}/Organization"
        params = {
            "identifier": f"odsOrganisationCode|{valid_ods_code}",
            "_revinclude": "Endpoint:organization",
        }
        valid_headers = headers.copy()
        valid_headers.update(
            {
                "NHSD-Correlation-ID": "smoke-test-correlation-id",
                "NHSD-Request-ID": "smoke-test-request-id",
            }
        )

        # Act
        try:
            response = requests.get(
                search_url, params=params, headers=valid_headers, timeout=timeout
            )
        except (ConnectionError, Timeout) as e:
            pytest.fail(f"ODS lookup endpoint unreachable: {e}")

        # Assert
        assert (
            response.status_code == 200
        ), f"Valid NHSD headers should be accepted, got {response.status_code}"
