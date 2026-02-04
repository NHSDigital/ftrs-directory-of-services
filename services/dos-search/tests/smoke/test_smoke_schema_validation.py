"""
Smoke Tests: FHIR Schema Validation

Tests that API responses comply with FHIR R4B schema in deployed environments.
These tests validate schema compliance and should run hourly.
"""

import pytest
import requests
from fhir.resources.bundle import Bundle
from fhir.resources.endpoint import Endpoint
from fhir.resources.operationoutcome import OperationOutcome
from fhir.resources.organization import Organization
from pydantic import ValidationError
from requests.exceptions import ConnectionError, Timeout


class TestFHIRSchemaComplianceSmoke:
    """Smoke tests for FHIR R4B schema compliance"""

    def test_bundle_response_validates_against_fhir_schema(
        self, base_url, headers, valid_ods_code, timeout
    ):
        """
        CRITICAL: API responses must validate against FHIR R4B schema

        This ensures all responses comply with FHIR specification.
        Should run hourly in production.
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

        # Validate against FHIR R4B Bundle schema
        try:
            bundle = Bundle(**data)
            assert bundle.resource_type == "Bundle"
            assert bundle.type == "searchset"
        except ValidationError as e:
            pytest.fail(f"Response does not validate against FHIR R4B Bundle schema: {e}")

    def test_organization_resource_validates_against_schema(
        self, base_url, headers, valid_ods_code, timeout
    ):
        """
        Organization resources must validate against FHIR R4B schema

        Validates the organization resource structure.
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
        bundle = Bundle(**data)

        # Find organization entry
        org_entry = next(
            (
                entry
                for entry in bundle.entry or []
                if entry.resource.get("resourceType") == "Organization"
            ),
            None,
        )

        if org_entry:
            try:
                org_resource = Organization(**org_entry.resource)
                assert org_resource.resource_type == "Organization"
            except ValidationError as e:
                pytest.fail(
                    f"Organization resource does not validate against FHIR R4B schema: {e}"
                )

    def test_endpoint_resources_validate_against_schema(
        self, base_url, headers, valid_ods_code, timeout
    ):
        """
        Endpoint resources must validate against FHIR R4B schema

        Validates endpoint resource structures.
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
        bundle = Bundle(**data)

        # Find endpoint entries
        endpoint_entries = [
            entry
            for entry in bundle.entry or []
            if entry.resource.get("resourceType") == "Endpoint"
        ]

        for endpoint_entry in endpoint_entries:
            try:
                endpoint_resource = Endpoint(**endpoint_entry.resource)
                assert endpoint_resource.resource_type == "Endpoint"
            except ValidationError as e:
                pytest.fail(
                    f"Endpoint resource does not validate against FHIR R4B schema: {e}"
                )

    def test_empty_bundle_validates_against_schema(
        self, base_url, headers, nonexistent_ods_code, timeout
    ):
        """
        Empty bundles must validate against FHIR R4B schema

        Validates schema compliance for no-results scenario.
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

        # Validate against FHIR R4B Bundle schema
        try:
            bundle = Bundle(**data)
            assert bundle.resource_type == "Bundle"
            assert len(bundle.entry or []) == 0
        except ValidationError as e:
            pytest.fail(f"Empty bundle does not validate against FHIR R4B schema: {e}")

    def test_operation_outcome_validates_against_schema(
        self, base_url, headers, invalid_ods_code, timeout
    ):
        """
        OperationOutcome responses must validate against FHIR R4B schema

        Validates schema compliance for error responses.
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

        # Validate against FHIR R4B OperationOutcome schema
        try:
            operation_outcome = OperationOutcome(**data)
            assert operation_outcome.resource_type == "OperationOutcome"
            assert len(operation_outcome.issue) > 0
        except ValidationError as e:
            pytest.fail(
                f"OperationOutcome does not validate against FHIR R4B schema: {e}"
            )


class TestBundleStructureCompliance:
    """Tests for FHIR Bundle structure compliance"""

    def test_bundle_has_required_type_field(
        self, base_url, headers, valid_ods_code, timeout
    ):
        """
        Bundle must have type field set to 'searchset'

        Validates required FHIR Bundle fields.
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
        assert data.get("type") == "searchset", "Bundle type must be 'searchset'"

    def test_bundle_has_self_link(
        self, base_url, headers, valid_ods_code, timeout
    ):
        """
        Bundle must contain self link

        Validates FHIR Bundle link structure.
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
        bundle = Bundle(**data)

        self_link = next(
            (link for link in bundle.link or [] if link.relation == "self"), None
        )
        assert self_link is not None, "Bundle must have a self link"
        assert valid_ods_code in self_link.url, "Self link must contain ODS code"

    def test_bundle_entries_have_search_mode(
        self, base_url, headers, valid_ods_code, timeout
    ):
        """
        Bundle entries must have search mode

        Validates entry.search.mode field presence and values.
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
        bundle = Bundle(**data)

        for entry in bundle.entry or []:
            assert entry.search is not None, "Each entry must have search field"
            assert entry.search.mode in [
                "match",
                "include",
            ], f"Search mode must be 'match' or 'include', got {entry.search.mode}"

    def test_organization_entry_has_match_mode(
        self, base_url, headers, valid_ods_code, timeout
    ):
        """
        Organization entry must have search mode 'match'

        Validates that primary result has correct search mode.
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
        bundle = Bundle(**data)

        org_entry = next(
            (
                entry
                for entry in bundle.entry or []
                if entry.resource.get("resourceType") == "Organization"
            ),
            None,
        )

        if org_entry:
            assert (
                org_entry.search.mode == "match"
            ), "Organization entry must have search mode 'match'"

    def test_endpoint_entries_have_include_mode(
        self, base_url, headers, valid_ods_code, timeout
    ):
        """
        Endpoint entries must have search mode 'include'

        Validates that included resources have correct search mode.
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
        bundle = Bundle(**data)

        endpoint_entries = [
            entry
            for entry in bundle.entry or []
            if entry.resource.get("resourceType") == "Endpoint"
        ]

        for endpoint_entry in endpoint_entries:
            assert (
                endpoint_entry.search.mode == "include"
            ), "Endpoint entries must have search mode 'include'"


class TestOrganizationResourceCompliance:
    """Tests for Organization resource FHIR compliance"""

    def test_organization_has_identifier(
        self, base_url, headers, valid_ods_code, timeout
    ):
        """
        Organization must have identifier with ODS code

        Validates organization identifier structure.
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
        bundle = Bundle(**data)

        org_entry = next(
            (
                entry
                for entry in bundle.entry or []
                if entry.resource.get("resourceType") == "Organization"
            ),
            None,
        )

        if org_entry:
            org_resource = Organization(**org_entry.resource)
            assert len(org_resource.identifier) > 0, "Organization must have identifier"
            ods_identifier = org_resource.identifier[0]
            assert (
                ods_identifier.system
                == "https://fhir.nhs.uk/Id/ods-organization-code"
            )
            assert ods_identifier.value == valid_ods_code

    def test_organization_has_active_field(
        self, base_url, headers, valid_ods_code, timeout
    ):
        """
        Organization must have active field

        Validates organization active status presence.
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
        bundle = Bundle(**data)

        org_entry = next(
            (
                entry
                for entry in bundle.entry or []
                if entry.resource.get("resourceType") == "Organization"
            ),
            None,
        )

        if org_entry:
            org_resource = Organization(**org_entry.resource)
            assert org_resource.active is not None, "Organization must have active field"
            assert isinstance(
                org_resource.active, bool
            ), "Organization active must be boolean"


class TestEndpointResourceCompliance:
    """Tests for Endpoint resource FHIR compliance"""

    def test_endpoint_has_required_fields(
        self, base_url, headers, valid_ods_code, timeout
    ):
        """
        Endpoint must have required fields: status, connectionType, address

        Validates endpoint required field presence.
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
        bundle = Bundle(**data)

        endpoint_entries = [
            entry
            for entry in bundle.entry or []
            if entry.resource.get("resourceType") == "Endpoint"
        ]

        for endpoint_entry in endpoint_entries:
            endpoint_resource = Endpoint(**endpoint_entry.resource)
            assert endpoint_resource.status is not None, "Endpoint must have status"
            assert (
                endpoint_resource.connectionType is not None
            ), "Endpoint must have connectionType"
            assert endpoint_resource.address is not None, "Endpoint must have address"

    def test_endpoint_connection_type_uses_valid_coding(
        self, base_url, headers, valid_ods_code, timeout
    ):
        """
        Endpoint connectionType must use valid FHIR coding system

        Validates endpoint connection type coding structure.
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
        bundle = Bundle(**data)

        endpoint_entries = [
            entry
            for entry in bundle.entry or []
            if entry.resource.get("resourceType") == "Endpoint"
        ]

        for endpoint_entry in endpoint_entries:
            endpoint_resource = Endpoint(**endpoint_entry.resource)
            conn_type = endpoint_resource.connectionType
            assert (
                conn_type.system
                == "http://terminology.hl7.org/CodeSystem/endpoint-connection-type"
            ), "Connection type must use standard FHIR coding system"
